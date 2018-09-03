###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summer 2018                                                   ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

### CREATE UNIVERSAL ERROR HANDLER, DEPENDING ON TYPE, PRINTS APPROPRIATE ERROR

def return_code(list):
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
        "00" : b'00 : Completed without errors',                        # {+++}
        ##### 0X : SUCCESS WITH WARNINGS ##########################################
        "01" : b'01 : Command has no effect',                           # {&&&}
        "02" : b'02 : One or more of the arguments were out of range',  # {&&&}
        "09" : b'09 : Safety interlock override is on',                 # {&&&}
        ##### 1X : MESSAGE ERRORS #################################################
        "10" : b'10 : Received message is too short or contains no data',
        "11" : b'11 : Received message is too long and cannot be parsed',
        "12" : b'12 : Received message is not terminated correctly',
        "13" : b'13 : Received message contains no commands',
        "14" : b'14 : Received message contains too many arguments',
        ##### 2X : PARSING ERRORS #################################################
        "20" : b'20 : Command not recognized',
        "21" : b'21 : Not enough arguments provided for this command',
        "22" : b'22 : Too may arguments provided for this command',
        "23" : b'23 : One or more provided argument(s) not recognized',
        "24" : b'24 : One or more provided argument(s) are not of expected type',
        "25" : b'25 : One or more provided argument(s) are not in range',
        ##### 3X : TTY PORT ERRORS ################################################
        "30" : b'30 : Unexpected TTY port error',                       # {+++}
        "31" : b'31 : Unable to connect to specified TTY port',         # {+++}
        "32" : b'32 : A timeout occurred when reading from TTY port',
        "33" : b'33 : Laser returned an error while executing command', # {+++}
		"34" : b'34 : Arduino returned an unexpected response',
        ##### 4X : I2C ERRORS #####################################################
        "40" : b'40 : Unable to connect to I2C device',                 # {+++}
        ##### 9X : SAFETY ERRORS ##################################################
        "90" : b'90 : Safety interlock is open'
        ###########################################################################
    }

    return return_codes.get(list[0], b'?? : An unknown error code was returned')
           + ' : ' + str(list[2]) + '\r\n'

def warn_parse(list):																	## REVISIT
    '''HANDLES RETURNS WHERE IT IS POSSIBLE FOR MANY WARNINGS TO OCCUR'''

    if len(list) == 0: return errno('00')
    if len(list) == 1: return errno(list[0])
    return (' '.join(list)+'\r\n').encode(encoding='ascii')

def descriptive_err(errno, description):
	'''HANDLES ERRORS THAT PROVIDE A ADDITIONAL INFORMATION'''

	return (errno+' : '+str(description)+'\r\n').encode(encoding='ascii')
