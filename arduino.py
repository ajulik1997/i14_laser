###############################################################################
###                                                                         ###
###     Written by Alexander Liptak (GitHub: @ajulik1997)                   ###
###     Date: Summer 2018                                                   ###
###     E-Mail: Alexander.Liptak.2015@live.rhul.ac.uk                       ###
###     Phone: +44 7901 595107                                              ###
###                                                                         ###
###############################################################################

import RPi.GPIO as GPIO
import subprocess
import serial
import time

## SET UP GPIOs ###############################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.OUT)                 ## Arduino reset pin
GPIO.setup([18, 27, 22], GPIO.OUT)      ## Modulation mode switch signals
GPIO.setup([23, 24], GPIO.OUT)          ## Operation mode switch signals

## RESET ARDUINO ##############################################################

def reset():
    '''RESETS ARDUINO TO KNOWN STATE AND PREPARES FOR COMMUNICATION'''
    
    try:
        subprocess.run("stty -F /dev/ttyACM0 -hupcl", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return (['35', str(e)])

    GPIO.output(7, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(7, GPIO.LOW)

    GPIO.output([18, 27, 22], GPIO.LOW)
    GPIO.output([23, 24], GPIO.LOW)

## PRIVATE FUNCTIONS ##########################################################

def sendSerial(string, path='/dev/ttyACM0'):
    try:
        with serial.Serial(port = path,
                           baudrate = 9600,
                           timeout = 5,
                           dsrdtr = False) as ser:
            ser.write((string + ' \r\n').encode(encoding='ascii'))
            time.sleep(0.1)
            #response = ser.readline()
            while(True): print(ser.readline())
            #if response == b'OK\r\n':
            #    return('00')
            #elif response == b'':
            #    return('32')
            #else: return(['34', str(response)])
    except serial.SerialException as e:
        return(['31', str(e)])
    except Exception as e:
        return(['30', str(e)])

## PUBLIC FUNCTIONS ###########################################################

def setLaserPower(pwr):
    '''
    Sets power of laser via Serial port
    
    Arguments:
        pwr <float> [0.0 - 100.0] - laser power as a percentage
    
    Returns:
        Error codes (see local file errors.txt)
    '''
    
    return(sendSerial("A" + str(pwr)))


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

    
def setTriggerThreshold(pwr):
    '''
    Sets the percentage of power above which laser can trigger camera in "master" mode

    Arguments:
        pwr <float> [0.0 - 100.0] - laser power as a percentage

    Returns:
        Error codes (see local file errors.txt)
    '''
    
    return(sendSerial("T" + str(pwr)))


def setModulationMode(mode, period, delay):
    '''
    Sets modulation mode of laser via GPIO and Serial port
    
    Arguments:
        mode <str> - string describing modulation mode of laser
            none: laser is modulated to produce a constant output
            sine: laser is modulated to produce a sine wave of given period
            square: laser is modulated to produce a square wave of given period
            triangle: laser is modulated to produce a triangle wave of given period
            sawtooth: laser is modulated to produce a sawtooth wave of given period
            pulse: laser repeatedly pulses for specified time (period) then waits (delay)
        period <float> [0.0 - 3,600,000.0] - milliseconds of period of one cycle
        delay <float> [0.0 - 3,600,000.0] - milliseconds of delay between cycles
    
    Returns:
        Error codes (see local file errors.txt)
    '''
    
    if mode == 'none':     GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.LOW,  GPIO.LOW))
    if mode == 'sine':     GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.LOW,  GPIO.HIGH))
    if mode == 'square':   GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.HIGH, GPIO.LOW))
    if mode == 'triangle': GPIO.output([18, 27, 22], (GPIO.LOW,  GPIO.HIGH, GPIO.HIGH))
    if mode == 'sawtooth': GPIO.output([18, 27, 22], (GPIO.HIGH, GPIO.LOW,  GPIO.LOW))
    if mode == 'pulse':    GPIO.output([18, 27, 22], (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
    
    return(sendSerial("P" + str(period) + ' ' + "D" + str(delay)))
