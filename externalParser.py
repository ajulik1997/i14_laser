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

##### RULEBOOK ################################################################

rulebook = {
    'LASER_MAINS'              : laser_mains_CMD,
    '?LASER_MAINS'             : laser_mains_QUERY,
    'LASER_POWER'              : laser_power_CMD,
    '?LASER_POWER'             : laser_power_QUERY,
    '?LASER_STATUS'            : laser_status_QUERY,
    '?LASER_FAULT'             : laser_fault_QUERY,
    'LASER_MODE'               : laser_mode_CMD,
    '?LASER_MODE'              : laser_mode_QUERY,
    'LASER_MOD_POLARITY'       : laser_mod_polarity_CMD,
    '?LASER_MOD_POLARITY'      : laser_mod_polarity_QUERY,
    'LASER_MODULATION'         : laser_modulation_CMD,
    '?LASER_MODULATION'        : laser_modulation_QUERY,
    #######################
    'LASER_TRIGGER_THRESHOLD'  : laser_trigger_threshold_CMD,
    '?LASER_TRIGGER_THRESHOLD' : laser_trigger_threshold_QUERY,
    #######################
    '?POWER_NOW'               : power_now_QUERY,
    '?POWER_MAX'               : power_max_QUERY,
    '?POWER_NOM'               : power_nom_QUERY,
    '?AMPS_NOW'                : amps_now_QUERY,
    '?TEMP_INTERNAL_NOW'       : temp_internal_now_QUERY,
    '?TEMP_DIODE_NOW'          : temp_diode_now_QUERY,
    '?TEMP_DIODE_MAX'          : temp_diode_max_QUERY,
    '?TEMP_DIODE_MIN'          : temp_diode_min_QUERY,
    #######################
    '?INFO_LASER'              : info_laser_QUERY,
    '?INFO_SERVER'             : info_server_QUERY,
    #######################
    '?INTERLOCK_STATUS'        : interlock_status_QUERY,
    '?INTERLOCK_OVERRIDE'      : interlock_override_QUERY,
    #######################
    'STRICT_MODE'              : strict_mode_CMD,
    '?STRICT_MODE'             : strict_mode_QUERY
}

##### GLOBAL VARS #############################################################

LASER_POWER = 0                 ## reset laser power to zero
LASER_MODE = 'indep'            ## reset laser mode to independent operation
LASER_MODULATION = 'none'       ## reset modulation to none (no modulation)
LASER_MODULATION_PERIOD = 0     ## reset modulation period to default
LASER_MODULATION_DELAY = 0      ## reset modulation to default
LASER_TRIGGER_THRESHOLD = 0     ## reset camera trigger threshold to default

STRICT_MODE = True

##### STARTUP INIT ############################################################

## set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([23,24], GPIO.IN) ## 16: INTERLOCK; 26: INTERLOCK_OVERRIDE

arduino.reset()

##### SAFETY CHECKS ###########################################################

def interlock_check():
    '''Returns interlock and override status'''

    if GPIO.input(23) == 1: return '00'    ## interlock closed
    if GPIO.input(24) == 1: return '04'    ## interlock open, override on
    LASER_POWER = 0
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
            else:              ## if strict mode, throw error instead of warning
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

def command(test_args, known_args, on_success, variable_update, *additional_checks):
    '''GENERIC COMMAND PROCESSOR'''

    ## check arguments and interlock
    a_check = argument_check(test_args, known_args)
    i_check = interlock_check()
    warnings = '00'
    print("STAGE1")
    ## analyse results, compile warnings
    if a_check[0] != '0': return a_check        ## arguments are not good
    if i_check[0] != '0': return i_check        ## ilock open, override off
    warnings = "{0:0=2d}".format(int(warnings) + int(a_check) + int(i_check))
    print("STAGE2")
    ## run aditional checks as requested
    for check in additional_checks:
        status = eval(check)
        if status[0] != '0': return status
        warnings = "{0:0=2d}".format(int(warnings) + int(status))
    print("STAGE3")
    ## if action does not need carrying out, skip it
    if int(warnings)%2 == 0:
        result_of_eval = eval(on_success)
        if type(result_of_eval) is list:
            if result_of_eval[0] != '00': return result_of_eval
        else:
            if result_of_eval != '00': return result_of_eval
    print("STAGE4")
    ## if you got here, only warnings or success
    if variable_update != None: exec(variable_update)
    return warnings

##### RULEBOOK FUNCTIONS - LASER ##############################################

def laser_mains_CMD(args):
    '''Switches laser ON or OFF'''

    check = "'01' if test_args[0].upper() == laser('SOUR:AM:STAT?')[1] else '00'"
    final = "laser('SOUR:AM:STAT '+test_args[0].upper())"
    result = command(args, [['ON', 'OFF']], final, None, check)

    return return_code(result)

#######################################

def laser_mains_QUERY():
    '''Queries whether laser is ON or OFF'''

    return query(laser("SOUR:AM:STAT?"))

#######################################

def laser_power_CMD(args):
    '''Sets amplitude of laser beam'''
    print("SOMEHOW I ENDED UP HERE")
    check = "'01' if float(test_args[0]) == LASER_POWER else '00'"
    final = "arduino.setLaserPower(float(test_args[0]))"
    update = "LASER_POWER = float(test_args[0])"
    result = command(args, [[0, 100]], final, update, check)

    return return_code(result)

def laser_power_QUERY():
    '''Gets amplitude of laser beam'''

    return (str(LASER_POWER)+'\r\n').encode(encoding='ascii')
#######################!!!!!!
def laser_status_QUERY():
    '''Gets laser status code'''

    return query(laser("SYST:STAT?"))

def laser_fault_QUERY():
    '''Gets laser fault code'''

    return query(laser("SYST:FAUL?"))

def laser_mode_CMD(args):
    '''Sets laser operation mode'''

    check_1 = "'26' if (args[0].lower() == 'gated' and (LASER_MODULATION not in ['square', 'pulse'])) else '00'"
    check_2 = "'01' args[0].lower() == LASER_MODE else '00')"
    final = "LASER_MODE = args[0].lower(); arduino.setOperationMode(LASER_MODE)"
    result = command(args, [['GATED', 'MASTER', 'INDEP']], final, check_1, check_2)

    return return_code(result)

def laser_mode_QUERY():
    '''Gets laser operation mode'''

    return (str(LASER_MODE)+'\r\n').encode(encoding='ascii')

def laser_mod_polarity_CMD(args):
    '''Sets laser modulation polarity'''

    check = "'01' if args[0].upper() == laser('SOUR:AM:MPOL?') else '00')"
    final = "laser('SOUR:AM:MPOL '+args[0].upper())"
    result = command(args, [['PASS', 'INVERT']], final, check)

    return return_code(result)

def laser_mod_polarity_QUERY():
    '''Gets laser modulation polarity'''

    return query(laser("SYST:AM:MPOL?"))

def laser_modulation_CMD(args):
    '''Sets modulation mode, period and delay of laser'''

    #check_1 = "'26' if (LASER_MODE == 'gated' and (args[0].lower() not in ['square', 'pulse']) else '00'"
    #check_2 = "'25' if (args[0].lower in ['sine', 'triangle', 'sawtooth'] and (args[1] > 1000 or args[2] > 1000)) else '00'"
    #check_3 = "'01' if (args[0].lower() == LASER_MODULATION and args[1] == LASER_MODULATION_PERIOD and args[2] == LASER_MODULATION_DELAY) else '00'"
    #final =
    #result = command(args, [['none', 'sine', 'square', 'triangle', 'sawtooth', 'pulse'],[0, 3600000],[0, 3600000]])
    return ''
    #return return_code(result)

def laser_modulation_QUERY():
    '''Gets modulation mode and paramters of laser'''

    return (str(LASER_MODULATION)+'\r\n').encode(encoding='ascii')

def laser_trigger_threshold_CMD(args):
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
    # some compound function
    return ''

def info_server_QUERY():
    return 'I14 Laser Controller | Written in: Python 3.5 | Running on: RPi 3 B+'

##### RULEBOOK FUNCTIONS - INTERLOCK ##########################################

def interlock_status_QUERY():
    if GPIO.input(23) == 0:
        return 'OPEN'
    else:
        return 'CLOSED'

def interlock_override_QUERY():
    if GPIO.input(24) == 0:
        return 'OFF'
    else:
        return 'ON'

##### RULEBOOK FUNCTIONS - STRICT MODE ########################################

def strict_mode_CMD(args):
    pass

def strict_mode_QUERY():
    pass

##### MAIN ####################################################################

def parse(args):
    if args[0] not in rulebook.keys(): return return_code('20')
    if args[0][0] == '?':
        return rulebook[args[0]]()
    else:
        return rulebook[args[0]](args[1:])
