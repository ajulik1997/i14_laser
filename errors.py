###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summmer 2018                                                  ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

def errno(num):
	'''
	RETURNS ERROR FROM ERROR NUMBER
	Note:   Errors marked with {+++} are likely to return a more descriptive
				error message instead instead of the generic messages below.
			Errors marked with {&&&} may be stacked together.
			Warnings (errors marked 0X) signal success (00) with a warning.
			More than one error can occur at any one time, but only the first
				error will be returned.
	'''
	
	errors = {
		##### 00 : SUCCESS ########################################################
		"00" : b'00 : Completed without errors\r\n',                        # {+++} 
		##### 0X : SUCCESS WITH WARNINGS ##########################################
		"01" : b'01 : Command has no effect\r\n',                           # {&&&}
		"09" : b'09 : Safety interlock override is on\r\n',                 # {&&&}
		##### 1X : MESSAGE ERRORS #################################################
		"10" : b'10 : Received message is too short or contains no data\r\n',
		"11" : b'11 : Received message is too long and cannot be parsed\r\n',
		"12" : b'12 : Received message is not terminated correctly\r\n',
		"13" : b'13 : Received message contains no commands\r\n',
		"14" : b'14 : Received message contains too many arguments\r\n',
		##### 2X : PARSING ERRORS #################################################
		"20" : b'20 : Command not recognized\r\n',
		"21" : b'21 : Not enough arguments provided for this command\r\n',
		"22" : b'22 : Too may arguments provided for this command\r\n',
		"23" : b'23 : One or more provided argument(s) not recognized\r\n',
		"24" : b'24 : One or more provided argument(s) are not of expected type\r\n',
		"25" : b'25 : One or more provided argument(s) are not in range\r\n',
		##### 3X : COM PORT ERRORS ################################################
		"30" : b'30 : Unexpected COM port error\r\n',                       # {+++}
		"31" : b'31 : Unable to connect to specified COM port\r\n',         # {+++}
		"32" : b'32 : A timeout occurred when reading from COM port\r\n',
		"33" : b'33 : Laser returned an error while executing command\r\n', # {+++} 
		##### 4X : I2C ERRORS #####################################################
		"40" : b'40 : Unable to connect to I2C device\r\n',                 # {+++}
		##### 9X : SAFETY ERRORS ##################################################
		"90" : b'90 : Safety interlock is open\r\n'
		###########################################################################
	}
	
	return errors.get(num, b'?? : An unknown error code was returned\r\n')