###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summmer 2018                                                  ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

## DEPRECIATED: REPLACED BY arduino.py

import smbus

# Register values:
WRITEDAC         = 0x40
WRITEDACEEPROM   = 0x60

# Default I2C address:
DEFAULT_ADDRESS  = 0x62

def intensity(percentage, persistence=False):
    try:    ## Now standard for I2C device to be #1
        bus = smbus.SMBus(1)
    except: return '40'
    value = round(4095*(float(percentage)/100))
    data = [(value >> 4) & 0xFF, (value << 4) & 0xFF]
    if persistence:
        bus.write_i2c_block_data(DEFAULT_ADDRESS, WRITEDACEEPROM, data)
    else:
        bus.write_i2c_block_data(DEFAULT_ADDRESS, WRITEDAC, data)
    return '00'