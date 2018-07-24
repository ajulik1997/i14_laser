###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summmer 2018                                                  ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

##### IMPORTS #################################################################

import RPi.GPIO as GPIO                 ## for GPIO control
from BioRay import laser                ## serial control of laser
from errors import errno, warn_parse    ## EXTERNAL ERROR DICTIONARY

##### GLOBAL VARS #############################################################

LASER_POWER = 0                 ## reset laser power to zero
LASER_MODE = 'indep'            ## reset laser mode to independent operation
LASER_MODULATION = 'full'       ## reset modulation to full (no modulation)
LASER_MODULATION_FREQ = 1       ## reset modulation frequency to default
LASER_MODULATION_DUTY = 50      ## reset modulation duty to default 

##### STARTUP INIT ############################################################

## set up GPIO modes 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([4,17], GPIO.IN) ## 4: INTERLOCK; 17: INTERLOCK_OVERRIDE
GPIO.setup([18], GPIO.OUT)

## set up interrupt to switch off laser on interlock open or override off                   ##CHANGE THIS TO MODULATION
GPIO.add_event_detect(4, GPIO.FALLING,
                      callback=lambda x: laser("SOUR:AM:STAT OFF"))
GPIO.add_event_detect(17, GPIO.FALLING,
                      callback=lambda x: laser("SOUR:AM:STAT OFF"))

## initial interlock status check:
if GPIO.input(4) == 0 and GPIO.input(17) == 0: laser("SOUR:AM:STAT OFF")

#### set laser power to 0                                                               ##TODO

#### reset laser mode to independent mode                                               ##TODO

#### set laser modulation to full                                                       ##TODO

##### SAFETY CHECKS ###########################################################

def interlock_check():
    '''Returns interlock and override status'''
    
    if GPIO.input(4) == 1: return 'L00'     ## interlock closed
    if GPIO.input(17) == 1: return 'L09'    ## interlock open, override on
    return '90'                            ## interlock open, override off

##### ARGUMENT CHECKS #########################################################

def argument_check(test_args, known_args):
    '''Tests the validity of passed arguments against expected arguments'''
    
    if len(test_args) < len(known_args):    ## is there too little arguments?
        return '21'
    if len(test_args) > len(known_args):    ## is there too many arguments?
        return '22'
    for i in range(len(test_args)):         ## go through every passed argument
        if all(isinstance(x, str) for x in known_args[i]):  ## expecting string
            if test_args[i].upper() not in known_args[i]:   ## is it recognized?
                return '23'
        else:                                               ## expecting number
            if not test_args[i].isnumeric():    ## is the passed arg numeric?
                return '24'
            if (float(test_args[i]) < known_args[i][0] 
            or  float(test_args[i]) > known_args[i][1]):    ## is it in range?
                return '25'
    return '00'

##### RULEBOOK FUNCTIONS - LASER ##############################################

def laser_mains_CMD(args):
    '''Switches laser ON or OFF'''
    
    a_check = argument_check(args, [['ON', 'OFF']])
    i_check = interlock_check()
    warn_list = []

    if a_check != '00': return errno(a_check)   ## arguments are not good
    if i_check == '90': return errno(i_check)   ## ilock open, override off
    if i_check == '09': warn_list.append('09')      ## append override warning if on
    
    ## add warning and do nothing if laser is already on/off
    if args[0].upper() == laser("SOUR:AM:STAT?")[-1]: warn_list.append('01')
    else:   ## time to switch on/off laser, and see if it worked
        result = laser("SOUR:AM:STAT "+args[0].upper())
        if result[0] != '00': return (' '.join(result)+'/r/n')   ## laser did not switch on OK
    
    if len(warn_list) == 0: return errno('00')  ## no warnings, return OK
    if len(warn_list) == 1: return errno(warn_list[0])  ## return a warning
    return ' '.join(warn_list)  ## return all the warnings formatted nicely

#######################################
    
def laser_mains_QUERY():
    '''Queries whether laser is ON or OFF'''
    
    return laser("SOUR:AM:STAT?")[-1]

#######################################

def laser_power_CMD(args):
    a_check = argument_check(args, [[0,100]])
    return a_check

def laser_power_QUERY():
    return str(LASER_POWER)

def laser_status_QUERY():
    ## STAT
    return ''

def laser_fault_QUERY():
    ## FAUL
    return ''

def laser_mode_CMD(args):
    a_check = argument_check(args, [['gated', 'master', 'indep']])
    return a_check
    
def laser_mode_QUERY():
    return ''

def laser_mod_polarity_CMD(args):
    a_check = argument_check(args, [['pass', 'invert']])
    return a_check

def laser_mod_polarity_QUERY():
    return ''

def laser_modulation_CMD(args):
    a_check = argument_check(args, [['sine', 'square', 'triangle', 'sawtooth', 'full'],
                               [0, 10000],
                               [0, 100]])
    return a_check

def laser_modulation_QUERY():
    return ''

##### RULEBOOK FUNCTIONS - POWER, AMPS, TEMP ##################################

def power_now_QUERY():
    return ''
    
def power_max_QUERY():
    return ''

def power_nom_QUERY():
    return ''

def amps_now_QUERY():
    return ''

def temp_internal_now_QUERY():
    return ''

def temp_diode_now_QUERY():
    return ''

def temp_diode_max_QUERY():
    return ''

def temp_diode_min_QUERY():
    return ''

##### RULEBOOK FUNCTIONS - INFO ###############################################

def info_laser_QUERY():
    return ''
    
def info_server_QUERY():
    return 'I14 Laser Controller | Written in: Python 3.5 | Running on: RPi B Rev 2'

##### RULEBOOK FUNCTIONS - INTERLOCK ##########################################

def interlock_status_QUERY():
    if GPIO.input(4) == 0:
        return 'open'
    if GPIO.input(4) == 1:
        return 'closed'

def interlock_override_QUERY():
    if GPIO.input(17) == 0:
        return 'off'
    if GPIO.input(17) == 1:
        return 'on'

##### MAIN ####################################################################

def parse(args):
    rulebook = {
        'LASER_MAINS'         : laser_mains_CMD(args[1:]),
        '?LASER_MAINS'        : laser_mains_QUERY(),
        'LASER_POWER'         : laser_power_CMD(args[1:]),
        '?LASER_POWER'        : laser_power_QUERY(),
        '?LASER_STATUS'       : laser_status_QUERY(),
        '?LASER_FAULT'        : laser_fault_QUERY(),
        'LASER_MODE'          : laser_mode_CMD(args[1:]),
        '?LASER_MODE'         : laser_mode_QUERY(),
        'LASER_MOD_POLARITY'  : laser_mod_polarity_CMD(args[1:]),
        '?LASER_MOD_POLARITY' : laser_mod_polarity_QUERY(),
        'LASER_MODULATION'    : laser_modulation_CMD(args[1:]),
        '?LASER_MODULATION'   : laser_modulation_QUERY(),
        #######################
        '?POWER_NOW'          : power_now_QUERY(),
        '?POWER_MAX'          : power_max_QUERY(),
        '?POWER_NOM'          : power_nom_QUERY(),
        '?AMPS_NOW'           : amps_now_QUERY(),
        '?TEMP_INTERNAL_NOW'  : temp_internal_now_QUERY(),
        '?TEMP_DIODE_NOW'     : temp_diode_now_QUERY(),
        '?TEMP_DIODE_MAX'     : temp_diode_max_QUERY(),
        '?TEMP_DIODE_MIN'     : temp_diode_min_QUERY(),
        #######################
        '?INFO_LASER'         : info_laser_QUERY(),
        '?INFO_SERVER'        : info_server_QUERY(),
        #######################
        '?INTERLOCK_STATUS'   : interlock_status_QUERY(),
        '?INTERLOCK_OVERRIDE' : interlock_override_QUERY()
    }
    return rulebook.get(args[0], errno('20'))