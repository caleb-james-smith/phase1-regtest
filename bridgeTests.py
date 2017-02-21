#!/usr/bin/env python

# bridgeTests.py
import registers
from ngFECSendCommand import send_commands
import regtest
import values
import time
import numpy as np
import operator

port  = regtest.port
host  = regtest.host
reset = regtest.resetRBXs

#################
# helpers       #
#################

def status(result):
    if result:  return "PASS"
    else:       return 4*" " + "FAIL"

def count(result):
    a, b = 1, 0 # attempts, fails
    if not result:
        b = 1   # increase number of fails by 1
    return (a,b)

def prettify(results, useStatus=False, extraN=False):
    if extraN:  a = "\n"
    else:       a = ""
    if useStatus:   return a + "\n".join(["%-40s : %-20s : %s"  %(x["cmd"], x["result"], x["status"]) for x in results])
    else:           return a + "\n".join(["%-40s : %-20s"       %(x["cmd"], x["result"]) for x in results]) 

def prettyTest(test):
    return "\n\nAttempts: %i , Passes: %i, Fails: %i\n" % (test[0], test[0] - test[1], test[1])

#################
# tests         #
#################

# Test Orbit Histograms: 7 bins on bridge
def orbitTest(rbxList, dt):
    test = (0,0)    # attempts, fails
    # Read FW version 
    cmds  = ["get HE%i-[1-4]-[1-4]-B_FIRMVERSION_[MAJOR,MINOR,SVN]"%(rbx) for rbx in rbxList]
    # stop run, clear histograms and then start run
    # the value of wait is in making these commands happen sequentially! 
    cmds += ["put HE%i-[1-4]-[1-4]-B_orbit_histo_run 16*0"%(rbx) for rbx in rbxList]
    cmds += ["wait"]
    cmds += ["put HE%i-[1-4]-[1-4]-B_orbit_histo_clear 16*1"%(rbx) for rbx in rbxList]
    cmds += ["wait"]
    cmds += ["put HE%i-[1-4]-[1-4]-B_orbit_histo_clear 16*0"%(rbx) for rbx in rbxList]
    cmds += ["wait"]
    cmds += ["put HE%i-[1-4]-[1-4]-B_orbit_histo_run 16*1"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults = prettify(results)
    # Wait for time dt and then stop run 
    time.sleep(dt)
    cmds  = ["put HE%i-[1-4]-[1-4]-B_orbit_histo_run 16*0"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += prettify(results, False, True)
    # Read from orbit histograms
    cmds  = ["get HE%i-%i-%i-B_orbit_histo_bin[1-7]"%(rbx,rm,card) for rbx in rbxList for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    for x in results:
        fails = 0
        histo = x["result"].split(" ")
        if len(histo) == 7:
            for i in xrange(7):
                if len(histo[i]) > 1:       val = int(histo[i][2:],16)
                else:                       val = int(histo[i])
                if i == 2 and val == 0:     fails += 1
                elif i != 2 and val != 0:   fails += 1
            passed = not bool(fails)    # False for fails > 0
        else:
            passed = False              # did not receive 7 histo bins
        x["status"] = status(passed)
        test = tuple(map(operator.add, test, count(passed)))
    formattedResults += prettify(results, True, True) 
    # Clear histograms 
    cmds  = ["put HE%i-[1-4]-[1-4]-B_orbit_histo_clear 16*1"%(rbx) for rbx in rbxList]
    cmds += ["wait"]
    cmds += ["put HE%i-[1-4]-[1-4]-B_orbit_histo_clear 16*0"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += prettify(results, False, True) 
    formattedResults += prettyTest(test)
    return formattedResults

# Test Ilgoo VDD voltage (1.2V) controled by bridge
def vddTest(rbxList):
    # B_IglooVDD_Enable (1 is on, 0 is off) for card=1 controls power for all 4 Igloos in RM 
    # the delay gives the Igloo time to power off and on
    delay = 0.2
    test = (0,0)    # attempts, fails
    # Read FW version
    cmds = ["get HE%i-[1-4]-[1-4]-B_FIRMVERSION_[MAJOR,MINOR,SVN]"%(rbx) for rbx in rbxList]
    # Turn on IglooVDD and read from Igloo scratch
    cmds += ["put HE%i-[1-4]-1-B_Igloo_VDD_Enable 4*1"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults = prettify(results) 
    time.sleep(delay)
    cmds = ["get HE%i-%i-%i-i_scratch"%(rbx,rm,card) for rbx in rbxList for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    for x in results:
        passed = x["result"] == values.getIglooValue("scratch")
        x["status"] = status(passed)
        test = tuple(map(operator.add, test, count(passed)))
    formattedResults += prettify(results, True, True) 
    # Turn off IglooVDD and read from Igloo scratch
    cmds = ["put HE%i-[1-4]-1-B_Igloo_VDD_Enable 4*0"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += prettify(results, False, True) 
    time.sleep(delay)
    cmds = ["get HE%i-%i-%i-i_scratch"%(rbx,rm,card) for rbx in rbxList for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    for x in results:
        passed = x["result"] == values.nack
        x["status"] = status(passed)
        test = tuple(map(operator.add, test, count(passed)))
    formattedResults += prettify(results, True, True) 
    # Turn on IglooVDD and read from Igloo scratch
    cmds = ["put HE%i-[1-4]-1-B_Igloo_VDD_Enable 4*1"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += prettify(results, False, True)
    time.sleep(delay)
    cmds = ["get HE%i-%i-%i-i_scratch"%(rbx,rm,card) for rbx in rbxList for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    for x in results:
        passed = x["result"] == values.getIglooValue("scratch")
        x["status"] = status(passed)
        test = tuple(map(operator.add, test, count(passed)))
    formattedResults += prettify(results, True, True) 
    formattedResults += prettyTest(test)
    return formattedResults

# write rbx, rm, card values to scratch register and then read back
def scratchTest(rbxList):
    test = (0,0)    # attempts, fails
    # Read FW version
    cmds = ["get HE%i-%i-[1-4]-B_FIRMVERSION_[MAJOR,MINOR,SVN]"%(rbx,rm) for rbx in rbxList for rm in xrange(1,5)]
    # Read scratch register
    cmds += ["get HE%i-%i-[1-4]-B_SCRATCH"%(rbx,rm) for rbx in rbxList for rm in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults = prettify(results) 
    # Write rbx, rm, card to scratch 
    cmds = []
    ids = np.zeros((20,4,4))
    for rbx in rbxList:
        for rm in xrange(1,5):
            for card in xrange(1,5):
                z = 0
                z |= rbx << 8
                z |= rm << 4
                z |= card
                cmds += ["put HE%i-%i-%i-B_SCRATCH %i" % (rbx, rm, card, z)]
                ids[rbx-1,rm-1,card-1] = z

    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += prettify(results, False, True) 
    # Read scratch register
    cmds = ["get HE%i-%i-%i-B_SCRATCH"%(rbx,rm,card) for rbx in rbxList for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    for x in results:
        parsed = x["cmd"].split("get HE")[1]
        parsed = parsed.split("-B_SCRATCH")[0]
        parsed = parsed.split("-")
        passed = x["result"] == hex(int(ids[int(parsed[0])-1,int(parsed[1])-1,int(parsed[2])-1]))
        x["status"] = status(passed)
        test = tuple(map(operator.add, test, count(passed)))
    formattedResults += prettify(results, True, True) 
    formattedResults += prettyTest(test)
    return formattedResults

# read and verify values of simple registers
def simpleReadTest(rbxList):
    test = (0,0)    # attempts, fails
    # Read FW version
    cmds = ["get HE%i-[1-4]-[1-4]-B_FIRMVERSION_[MAJOR,MINOR,SVN]"%(rbx) for rbx in rbxList]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults = prettify(results) 
    print formattedResults
    # Iterate through registers 
    cmds = ["get HE%i-%i-%i-B_%s" % (rbx, rm, card, reg) for reg in values.bridge for rbx in rbxList for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    for x in results:
        reg = x["cmd"].split("B_")[-1]
        # BkPln_GEO register holds the value of card slot (1, 2, 3, 4)
        if reg == "BkPln_GEO":
            val = x["cmd"].split("-B_BkPln_GEO")[0][-1] # get card number 1, 2, 3, 4
            passed = x["result"] == val
        elif reg == "SHT_temp_f":
            try:
                val = float(x["result"])
                passed = 25.0 < val < 40.0
            except:
                passed = False
        elif reg == "SHT_rh_f":
            try:
                val = float(x["result"])
                passed = 15.0 < val < 30.0
            except:
                passed = False
        else:
            val = values.getBridgeValue(reg)
            passed = x["result"] == val
        x["status"] = status(passed)
        test = tuple(map(operator.add, test, count(passed)))
    
    formattedResults = prettify(results, True, True) 
    formattedResults += prettyTest(test)
    return formattedResults

#################
# main          #
#################

if __name__ == "__main__":
    #rbxList = [11,12]
    rbxList = [i for i in xrange(2,16)]
    NIterations = 10
    for i in xrange(NIterations):
        reset(rbxList)
        print "\nReset RBXs : {0}\n".format(rbxList)
        #print vddTest(rbxList)
        print orbitTest(rbxList, 2.0)
        #print scratchTest(rbxList)
        #print simpleReadTest(rbxList)
     
