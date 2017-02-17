#!/usr/bin/env python

# bridgeTests.py
import registers
from ngFECSendCommand import send_commands
import regtest
import time

port = regtest.port
host = regtest.host
reset = regtest.resetRBX

def orbitTest(rbx, dt):
    cmds  = ["put HE%i-%i-%i-B_orbit_histo_run 0"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    cmds += ["put HE%i-%i-%i-B_orbit_histo_clear 1"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    cmds += ["put HE%i-%i-%i-B_orbit_histo_run 1"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults = "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    time.sleep(dt)
    cmds  = ["get HE%i-%i-%i-B_orbit_histo_bin%i"%(rbx,rm,card,bin) for rm in xrange(1,5) for card in xrange(1,5) for bin in xrange(1,8)]
    cmds += ["put HE%i-%i-%i-B_orbit_histo_run 0"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    time.sleep(dt)
    cmds  = ["get HE%i-%i-%i-B_orbit_histo_bin%i"%(rbx,rm,card,bin) for rm in xrange(1,5) for card in xrange(1,5) for bin in xrange(1,8)]
    cmds += ["put HE%i-%i-%i-B_orbit_histo_clear 1"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    return formattedResults

def vddTest(rbx):
    # B_IglooVDD_Enable (1 is on, 0 is off) for card=1 controls power for all 4 Igloos in RM 
    delay = 0.2
    # Turn on IglooVDD 
    cmds = ["put HE%i-%i-%i-B_Igloo_VDD_Enable 1"%(rbx,rm,1) for rm in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults = "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    time.sleep(delay)
    cmds = ["get HE%i-%i-%i-i_scratch"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    # Turn off IglooVDD 
    cmds = ["put HE%i-%i-%i-B_Igloo_VDD_Enable 0"%(rbx,rm,1) for rm in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    time.sleep(delay)
    cmds = ["get HE%i-%i-%i-i_scratch"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    # Turn on IglooVDD
    cmds = ["put HE%i-%i-%i-B_Igloo_VDD_Enable 1"%(rbx,rm,1) for rm in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    time.sleep(delay)
    cmds = ["get HE%i-%i-%i-i_scratch"%(rbx,rm,card) for rm in xrange(1,5) for card in xrange(1,5)]
    results = send_commands(port, host, cmds, script=True, raw=False, time_out=20)
    formattedResults += "\n" + "\n".join(["%-40s : %s"%(x["cmd"], x["result"]) for x in results])
    
    return formattedResults

if __name__ == "__main__":
    #rbxList = [i for i in xrange(2,19)]
    rbxList = [5]
    NIterations = 1
    for rbx in rbxList:
        reset(rbx)
        #print orbitTest(rbx, 1.0)
        print vddTest(rbx)
        
