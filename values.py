# 'correct' values for registers

bridge = {
"FIRMVERSION_MAJOR"     : "2",
"FIRMVERSION_MINOR"     : "3",
"FIRMVERSION_SVN"       : "0",
"ZEROES"                : "0",
"ONES"                  : "0xffffffff",
"ONESZEROES"            : "0xaaaaaaaa",
"ID1"                   : "0x4845524d", # HERM
"ID2"                   : "0x42726467", # Brdg
"BkPln_GEO"             : ['1','2','3','4'],
"SHT_temp_f"            : 30.0,
"SHT_rh_f"              : 22.5,
}

igloo = {
"scratch" : "0xffffffff",
}

nack = "ERROR!!  I2C: NACK"

# Backplane GEO : 1, 2, 3, 4

def getBridgeValue(register):
    return bridge[register]


def getIglooValue(register):
    return igloo[register]
