###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summer 2018                                                   ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

### CREATE UNIVERSAL ERROR HANDLER, DEPENDING ON TYPE, PRINTS APPROPRIATE ERROR

def return_code(obj):
    '''
    RETURNS MESSAGE FROM RETURN CODE
    Note:   Messages marked with {+++} are likely to return a more descriptive
                error message instead instead of the generic messages below.
            Warnings marked with {&&&} may be stacked together.
            More than one error can occur at any one time, but only the first
                error will be returned.
    '''

    return_codes = {
        ##### 00 : SUCCESS ########################################################
        "00" : '00 : Completed without errors',                             # {+++}
        ##### 0X : SUCCESS WITH WARNINGS ##########################################
        "01" : '01 : Command has no effect',                                # {&&&}
        "02" : '02 : One or more of the arguments were out of range',       # {&&&}
        "04" : '04 : Safety interlock override is on',                      # {&&&}
        ##### 1X : MESSAGE ERRORS #################################################
        "10" : '10 : Received message is too short or contains no data',
        "11" : '11 : Received message is too long and cannot be parsed',
        "12" : '12 : Received message is not terminated correctly',
        "13" : '13 : Received message contains no commands',
        "14" : '14 : Received message contains too many arguments',
        ##### 2X : PARSING ERRORS #################################################
        "20" : '20 : Command not recognized',
        "21" : '21 : Not enough arguments provided for this command',
        "22" : '22 : Too may arguments provided for this command',
        "23" : '23 : One or more provided argument(s) not recognized',
        "24" : '24 : One or more provided argument(s) are not of expected type',
        "25" : '25 : One or more provided argument(s) are not in range',
        "26" : '26 : Operation mode is not compatible with current modulation mode',
        ##### 3X : TTY PORT ERRORS ################################################
        "30" : '30 : Unexpected TTY port error',                            # {+++}
        "31" : '31 : Unable to connect to specified TTY port',              # {+++}
        "32" : '32 : A timeout occurred when reading from TTY port',
        "33" : '33 : Laser returned an error while executing command',      # {+++}
        "34" : '34 : Arduino returned an unexpected response',              # {+++}
        "35" : '35 : Unable to edit TTY settings for Arduino compatibility',# {+++}
        ##### 4X : I2C ERRORS #####################################################
        "40" : '40 : Unable to connect to I2C device',                      # {+++}
        ##### 9X : SAFETY ERRORS ##################################################
        "90" : '90 : Safety interlock is open'
        ###########################################################################
    }

    if type(obj) is str:
        if 0 < int(obj) < 10:
            message = obj + ' : More than one warning has occured'
        else:
            message = return_codes.get(obj, '?? : An unknown error code was returned')

    if type(obj) is list:
        message = return_codes.get(obj[0], '?? : An unknown error code was returned')
        message += ' : ' + str(obj[1])

    return (message+'\r\n').encode(encoding='ascii')
