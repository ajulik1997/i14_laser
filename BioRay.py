###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summmer 2018                                                  ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

import serial       ## for serial communication with laser

def laser(msg):
    '''
    A function for serial communication with a Coherent BioRay laser
    
        - a serial port that the laser is connected to is opened
        - message is written to laser (with a 100ms timeout)
        - two lines are read from laser (message, handshake)
        - if handshake shows OK, response is returned
        - if handshake shows ERR or another error occurs, returns error code
    
    Arguments:
        msg <str> - message to send to laser over serial
    
    Returns:
        Response from laser
        Error codes (see local file errors.txt)
    '''
    try:
        with serial.Serial(port='/dev/ttyUSB0',
                           baudrate=115200,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           bytesize=serial.EIGHTBITS,
                           timeout=0.1) as ser:
            ser.write((msg + '\r\n').encode(encoding='ascii'))
            response = [line.decode(encoding='ascii').rstrip() for line in ser.readlines()]
            
            if response[-1] == 'OK': return(['00', response[0]])
            else: return(['33', response[-1]])

    except serial.SerialException as e:
        return(['31', str(e)])
    except serial.SerialTimeoutException as e:
        return(['32', str(e)])
    except Exception as e:
        return(['30', str(e)])
