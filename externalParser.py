###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summer 2018                                                   ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

##### IMPORTS #################################################################

import RPi.GPIO as GPIO                 ## for GPIO control
from BioRay import laser                ## EXTERNAL BIORAY SERIAL CONTROLLER
from errors import return_code          ## EXTERNAL RETURN CODE DICTIONARY
import arduino                          ## Arduino laser controller

##### GLOBAL VARS #############################################################

LASER_POWER = 0                 ## reset laser power to zero
LASER_MODE = 'indep'            ## reset laser mode to independent operation
LASER_MODULATION = 'none'       ## reset modulation to none (no modulation)
LASER_MODULATION_PERIOD = 0     ## reset modulation period to default
LASER_MODULATION_DELAY = 0      ## reset modulation LASER_MODULATION_DELAY to default
LASER_TRIGGER_THRESHOLD = 0     ## reset camera trigger threshold to default

STRICT_MODE = True

##### STARTUP INIT ############################################################

## set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([16,26], GPIO.IN) ## 16: INTERLOCK; 26: INTERLOCK_OVERRIDE

arduino.reset()

##### SAFETY CHECKS ###########################################################

def interlock_check():
    '''Returns interlock and override status'''

    if GPIO.input(16) == 1: return '00'    ## interlock closed
    if GPIO.input(26) == 1: return '04'    ## interlock open, override on
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
            if not STRICT_MODE:                    ## is it in range?
                if float(test_args[i]) < known_args[i][0]:
                    test_args[i] = known_args[i][0]
                    return '02'
                if float(test_args[i]) > known_args[i][1]:
                    test_args[i] = known_args[i][1]
                    return '02'
            else:
                if (float(test_args[i]) < known_args[i][0]
                or  float(test_args[i]) > known_args[i][1]):
                    return '25'
    return '00'

##### QUERY HANDLER ###########################################################

def query(list):
    '''HANDLES ALL LASER QUERY RESPONSES'''

    if list[0] != '00': return return_code(list[0])
    return (list[1]+'\r\n').encode(encoding='ascii')

##### COMMAND HANDLER #########################################################

def command(test_args, known_args):                                                        ############### FINISH ME
    a_check = argument_check(test_args, known_args)
    i_check = interlock_check()
    warn_list = []

    if a_check != '00': return a_check          ## arguments are not good
    if i_check == '90': return i_check          ## ilock open, override off
    if i_check == '04': warn_list.append('04')  ## append override warning if on

##### RULEBOOK FUNCTIONS - LASER ##############################################

def laser_mains_CMD(args):
    '''Switches laser ON or OFF'''

    a_check = argument_check(args, [['ON', 'OFF']])
    i_check = interlock_check()
    warn_list = []

    if a_check != '00': return return_code(a_check)   ## arguments are not good
    if i_check == '90': return return_code(i_check)   ## ilock open, override off
    if i_check == '04': warn_list.append('04')  ## append override warning if on

    ## add warning and do nothing if laser is already on/off
    if args[0].upper() == laser("SOUR:AM:STAT?")[-1]: warn_list.append('01')
    else:   ## time to switch on/off laser, and see if it worked
        result = laser("SOUR:AM:STAT "+args[0].upper())
        if result[0] != '00': return warn_parse(result) ## laser returned error

    return warn_parse(warn_list)  ## return all the warnings formatted nicely

#######################################

def laser_mains_QUERY():
    '''Queries whether laser is ON or OFF'''

    return query(laser("SOUR:AM:STAT?"))

#######################################

def laser_power_CMD(args):                                                                ### WILL BE DONE OVER ARDUINO NOW
    '''Sets amplitude of laser beam'''

    a_check = argument_check(args, [[0,100]])
    i_check = interlock_check()
    warn_list = []

    if a_check != '00' or a_check != '02': return return_code(a_check)   ## arguments are not good
    if a_check == '02': return
    if i_check == '90': return return_code(i_check)   ## ilock open, override off
    if i_check == '04': warn_list.append('04')  ## append override warning if on

    ## add warning and do nothing if laser power already set to wanted value
    if args[0] == LASER_POWER: warn_list.append('01')
    else: ## set laser power
        result = intensity(args[0])
        if result != '00': return return_code(result)

    return warn_parse(warn_list)

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

def laser_trigger_threshold_CMD():
    return ''

def laser_trigger_threshold_QUERY():
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

##### RULEBOOK FUNCTIONS - STRICT MODE ########################################

def strict_mode_CMD(args):
    pass

def strict_mode_QUERY():
    pass

##### MAIN ####################################################################

def parse(args):
    rulebook = {
        'LASER_MAINS'              : laser_mains_CMD(args[1:]),
        '?LASER_MAINS'             : laser_mains_QUERY(),
        'LASER_POWER'              : laser_power_CMD(args[1:]),
        '?LASER_POWER'             : laser_power_QUERY(),
        '?LASER_STATUS'            : laser_status_QUERY(),
        '?LASER_FAULT'             : laser_fault_QUERY(),
        'LASER_MODE'               : laser_mode_CMD(args[1:]),
        '?LASER_MODE'              : laser_mode_QUERY(),
        'LASER_MOD_POLARITY'       : laser_mod_polarity_CMD(args[1:]),
        '?LASER_MOD_POLARITY'      : laser_mod_polarity_QUERY(),
        'LASER_MODULATION'         : laser_modulation_CMD(args[1:]),
        '?LASER_MODULATION'        : laser_modulation_QUERY(),
        #######################
        'LASER_TRIGGER_THRESHOLD'  : laser_trigger_threshold_CMD(args[1:]),
        '?LASER_TRIGGER_THRESHOLD' : laser_trigger_threshold_QUERY(),
        #######################
        '?POWER_NOW'               : power_now_QUERY(),
        '?POWER_MAX'               : power_max_QUERY(),
        '?POWER_NOM'               : power_nom_QUERY(),
        '?AMPS_NOW'                : amps_now_QUERY(),
        '?TEMP_INTERNAL_NOW'       : temp_internal_now_QUERY(),
        '?TEMP_DIODE_NOW'          : temp_diode_now_QUERY(),
        '?TEMP_DIODE_MAX'          : temp_diode_max_QUERY(),
        '?TEMP_DIODE_MIN'          : temp_diode_min_QUERY(),
        #######################
        '?INFO_LASER'              : info_laser_QUERY(),
        '?INFO_SERVER'             : info_server_QUERY(),
        #######################
        '?INTERLOCK_STATUS'        : interlock_status_QUERY(args[1:]),
        '?INTERLOCK_OVERRIDE'      : interlock_override_QUERY(),
        #######################
        'STRICT_MODE'               : strict_mode_CMD(),
        '?STRICT_MODE'              : strict_mode_QUERY()
    }
    return rulebook.get(args[0], return_code('20'))
