###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summer 2018                                                   ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

import RPi.GPIO as GPIO
import serial
import time

## SET UP GPIOs ###############################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.OUT)                 ## Arduino reset pin
GPIO.setup([18, 27, 22], GPIO.OUT)      ## Modulation mode switch signals
GPIO.setup([23, 24], GPIO.OUT)          ## Operation mode switch signals

## RESET ARDUINO ##############################################################

GPIO.output(7, GPIO.HIGH)
time.sleep(0.1)
GPIO.output(7, GPIO.LOW)

GPIO.output([18, 27, 22], GPIO.LOW)
GPIO.output([23, 24], GPIO.LOW)

## FUNCTIONS ##################################################################

def isReady():
    '''
    Functions that handshakes with the Arduino to test if it is ready to
        receive commands.
    
    Arguments:
        none
    
    Returns:
        Error codes (see local file errors.txt)
    '''

    try:
        with serial.Serial(port = '/dev/ttyACM0',
                           baudrate = 9600,
                           timeout = 1) as ser:
            ser.write(b'READY\r\n')
            response = ser.readline().decode(encoding='ascii').rstrip()
            if response == 'OK': return('00')
            else: return('34')
    except serial.SerialException as e:
        return(['31', str(e)])
    except serial.SerialTimeoutException as e:
        return(['32', str(e)])
    except Exception as e:
        return(['30', str(e)])


def setLaserPower(pwr):
    '''
    Sets power of laser via TTY port
    
    Arguments:
        pwr <float> - laser power as a percentage
    
    Returns:
        Error codes (see local file errors.txt)
    '''

    try:
        with serial.Serial(port = '/dev/ttyACM0',
                           baudrate = 9600,
                           timeout = 1) as ser:
            ser.write((pwr + '\r\n').encode(encoding='ascii'))
            return('00')
    except serial.SerialException as e:
        return(['31', str(e)])
    except serial.SerialTimeoutException as e:
        return(['32', str(e)])
    except Exception as e:
        return(['30', str(e)])
        

def setOperationMode(mode):
    '''
    Sets the operation mode of laser via GPIO
    
    Arguments:
        mode <str> - string describing operation mode of laser
            gated:  laser is triggered via camera GPIO
            master: camera is triggered via laser GPIO
            indep:  laser and camera operate independently
        
    Returns:
        none
    '''

    if mode == 'gated':  GPIO.output([23, 24], (GPIO.HIGH, GPIO.LOW))
    if mode == 'master': GPIO.output([23, 24], (GPIO.LOW,  GPIO.HIGH))
    if mode == 'indep':  GPIO.output([23, 24], (GPIO.HIGH, GPIO.HIGH))


def setModulationMode(mode, freq, duty):
    '''
    Sets modulation mode of laser via GPIO and TTY
    
    Arguments:
        mode <str> - string describing modulation mode of laser
            none: laser is modulated to produce no output
            sine: laser is modulated to produce a sine wave of given frequency and duty
            square: laser is modulated to produce a square wave of given frequency and duty
            triangle: laser is modulated to produce a triangle wave of given frequency and duty
            sawtooth: laser is modulated to produce a sawtooth wave of given frequency and duty
            full: laser is modulated to produce constant output at set power
        freq <int> - target frequency of selected modulation mode
        duty <int> - percentage of frequency cycle that wave spends at nonzero power
    
    Returns:
        Error codes (see local file errors.txt)
    '''
    
    if mode == 'none':     GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.LOW,  GPIO.LOW))
    if mode == 'sine':     GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.LOW,  GPIO.HIGH))
    if mode == 'square':   GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.HIGH, GPIO.LOW))
    if mode == 'triangle': GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.HIGH, GPIO.HIGH))
    if mode == 'sawtooth': GPIO.output([18, 27, 22], (GPIO.HIGH, GPIO.LOW,  GPIO.LOW))
    if mode == 'full':     GPIO.output([18, 27, 22], (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
    
    try:
        with serial.Serial(port = '/dev/ttyACM0',
                           baudrate = 9600,
                           timeout = 1) as ser:
            ser.write((freq + ' ' + duty + '\r\n').encode(encoding='ascii'))
            return('00')
    except serial.SerialException as e:
        return(['31', str(e)])
    except serial.SerialTimeoutException as e:
        return(['32', str(e)])
    except Exception as e:
        return(['30', str(e)])