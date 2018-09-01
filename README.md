# I14 Remote Laser Controller

Software developed for the remote control and monitoring of a laser at the [Diamond Light Source I14 instrument](https://www.diamond.ac.uk/Instruments/Imaging-and-Microscopy/I14.html).

The following documentation is designed as a guide to simplify the processes of preparing the hardware and installing this software, as well as extending its functionality and applying it to other components or instruments.


## Table of Contents

- [Introduction](#introduction)
  - [Key Features](#key-features)
- [The Hardware](#the-hardware)
  - [Raspberry Pi](#raspberry-pi)
    - [Operating System](#operating-system)
    - [Drivers and Packages](#drivers-and-packages)
    - [Python](#python)
    - [Pin Assignment](#pin-assignment)
  - [Laser](#laser)
  - [Arduino](#arduino)
    - [Pin Assignment](#pin-assignment)
  - [LED Signalling](#led-signalling)
  - [Digital to Analog Converter](#digital-to-analog-converter)
    - [Laser modulation](#laser-modulation)
  - [Camera](#camera)
- [The Software](#the-software)
  - [Server](#server)
    - [Client](#client)
  - [Parser](#parser)
    - [Table of Recognized Commands](#table-of-recognized-commands)
  - [Error Handler](#error-handler)
    - [Table of Errors and Warnings](#table-of-errors-and-warnings)
  - [Laser Serial Communication Script](#laser-serial-communication-script)
  - [Arduino Controller Script (Python)](#arduino-controller-script-python)
    - [Arduino Controller Script (C for AVR)](#arduino-controller-script-c-for-avr)
- [Licensing](#licensing)
- [Author](#author)
- [Acknowledgements](#acknowledgements)


## Introduction

At the core of this "system" lies a [Raspberry Pi](https://www.raspberrypi.org/), used as a server running a python script which allows it to process text-based commands that it receives over network. A [Coherent Laser](https://www.coherent.com/) is connected to the Raspberry Pi via a USB-to-Serial interface, enabling the Pi to send commands to the laser and monitor its status. An [Arduino board](https://www.arduino.cc/) is also connected to the Raspberry Pi via a USB-to-Serial as well as a GPIO interface, and is mainly responsible for real-time generation of waveforms that are used to modulate the laser via a Digital-to-Analog converter (DAC). Additionally, a camera can also be connected to the Arduino, which can synchronize the camera's shutter with the modulation of the laser.

A diagram that illustrates this setup can be seen below. It was created using [draw.io](https://www.draw.io/), and the source can be downloaded [here](./resources/flowcharts/project_map.xml).

![Project Map](./resources/flowcharts/project_map.png)


### Key Features

The most noteworthy and desirable features of this project can be summarized as follows:

  - Remote control of laser over LAN
  - Remote monitoring of laser and safety interlock status over LAN
  - High-precision control of laser output intensity
  - Modulation of laser beam with pre-set waveforms of customizable period length and inter-cycle delay:
    - Sine wave, triangle wave, sawtooth wave: cycle period between 1 millisecond and 1 second
    - Square wave, pulse wave: cycle period between 1 millisecond and 1 hour
  - Synchronization of laser with connected camera:
    - "gated mode": laser is turned on only when camera is exposing
    - "master mode": camera exposure triggered when laser intensity reaches a customizable threshold
  - Robust and extensible error handling
  - Modular, well-documented code for easy customization


## The Hardware

The following section documents the steps required to correctly set up the hardware. It describes the setup of the operating system on the Raspberry Pi, as well as the required wiring between the Raspberry Pi, Arduino, DAC, laser and camera.

### Raspberry Pi

The Raspberry Pi used in this project is the [Raspberry Pi 3 B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) (upgraded from the Raspberry Pi B Rev 2.0 on which development took place), chosen due to the following features:
  - 1.4GHz processor (upgraded from 700Mhz)
  - 1GB SDRAM (upgraded from 512MB)
  - 40 GPIO pins (upgraded from 26)
  - Gigabit Ethernet
  - MicroSD port
  - PoE support

According to our specification, the Raspberry Pi needs to be set up so that it can do the following:
  - run a headless Linux OS
  - securely connect to a LAN
  - communicate with other devices on the LAN via SSH
  - communicate with laser via Serial-over-USB
  - communicate with Arduino via Serial-over-USB and GPIO
  - start Python server at boot and ensure it restarts on exit


#### Operating System

The operating system chosen for this project was [Raspbian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), an OS based on Debian Stretch with no desktop interface, chosen for its minimal footprint and high compatibility with Raspberry Pi. The required image was downloaded from the [official mirror](https://downloads.raspberrypi.org/raspbian_lite_latest), and written to a 16GB microSD card according to the [installation instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).

As the Pi is being used a server, it needs to be set up to run headless. This process is described in detail [here](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md), but the most important step (activating SSH), can be accomplished by mounting the SD card on any Windows or 

MORE GOES ON MONDAY

#### Drivers and Packages

This section highlights the packages and drivers that need to be installed or set up, either as dependencies by the server, or optional add-ons for easier developement and set-up.

##### Flashing '.hex' files to Arduino

As of Arduino 1.6, it is possible to develop Arduino applications directly on the Raspberry Pi, although this is not recommended, as the newly released Arduino CLI has too many dependencies (up to 1GB, including a desktop environment, which is not necessary on a headless Raspberry Pi) for a system with limited storage and memory. 

<TALK ABOUT DRIVER> <avrdude> <USB TO SERIAL HACK FOR LASER?>

--
http://www.ladyada.net/learn/avr/avrdude.html

sudo avrdude -p atmega328p -P /dev/ttyACM0 -c arduino -U flash:w:arduino.hex:i
--

create a shell script 'laserUSBtoSerial.sh' (alternatively, download it from [here](./laserUSBtoSerial.sh)

'''shell
#!/bin/bash
modprobe ftdi_sio
echo 0d4d 003d > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
udevadm control --reload && udevadm trigger
'''

say what it does

needs to be run using 'su' as follows:

'''ShellSession
sudo su
./laserUSBtoSerial.sh
exit
'''

alternatively, (preffered) set it as a startup script

/lib/systemd/system/laserUSBtoSerial.service

description here (complete it): https://www.freedesktop.org/software/systemd/man/systemd.service.html

add as a file

'''
[Unit]
Description=Enable Coherent Laser USB-to-Serial

[Service]
Type=forking
ExecStart=/home/pi/laserUSBtoSerial.sh

[Install]
WantedBy=multi-user.target
'''

sudo chmod 744 laserUSBtoSerial.sh

then start it using

'''ShellSession
sudo systemctl enable laserUSBtoSerial.service
'''

reboot

#### Python


#### Pin Assignment

<VERSION, PACKAGES>


### Laser

https://edge.coherent.com/assets/pdf/Coherent-BioRay-Operator-s-Manual.pdf

<MODEL, DOCUMENTATION, CONTROLLER, USB-TO-SERIAL, ARDUINO???> <USB TO SERIAL HACK FOR LASER?>


### Arduino

https://www.circuito.io/blog/arduino-uno-pinout/

<MODEL, STORAGE, MEMORY>

<MODES OF OPERATION, MODES OF MODULATION>

https://www.sparkfun.com/datasheets/Components/BC546.pdf


#### Pin Assignment


#### LED Signalling

<LIST OF ASSIGNED PINS> <WIRING DIAGRAM>


### Digital to Analog Converter

https://www.adafruit.com/product/935

https://learn.adafruit.com/mcp4725-12-bit-dac-tutorial

https://www.sparkfun.com/datasheets/BreakoutBoards/MCP4725.pdf

https://cdn-shop.adafruit.com/datasheets/mcp4725.pdf

<SPECIFICATION> <DATA SHEET> <I2C>


#### Laser Modulation

<Oscilloscope>

Talk about physical and software maximums / minimums and why you should not cross them (show borderline cases)

(add safety section here!)

http://www.ti.com/lit/ds/symlink/cd54hc32.pdf


### Camera

https://www.alliedvision.com/fileadmin/content/documents/products/cameras/Manta/techman/Manta_TechMan.pdf


## The Software


### Server


CRATE A FILE FROM THIS AND HOST IT, AND CLEAN IT UP, LIKE ABOVE


'''
[Unit]
Description=Python3 server
After=multi-user.target
Wants = network-online.target
After = network.target network-online.target

[Service]
Type=idle
Restart=always
ExecStart=/usr/bin/python3 /home/pi/server.py

[Install]
WantedBy=multi-user.target
'''

/lib/systemd/system/server.service

#### Client


### Parser


#### Table of Recognized Commands


### Error handler


#### Table of Errors and Warnings


### Laser Serial Communication Script


### Arduino Controller Script (Python)

nohup

https://raspberrypi.stackexchange.com/questions/9695/disable-dtr-on-ttyusb0/31298#31298

https://linux.die.net/man/1/stty


#### Arduino Controller Script (C for AVR)

talk about why I had to replace the Wire library

http://dsscircuits.com/articles/arduino-i2c-master-library

changed compilation parameter to -O2 (talk about it) File --> Preferences --> Follow link at the bottom of page (using arduino 1.8.5)
"%USERPROFILE%\AppData\Local" on Windows, C:\Users\lyv26778\AppData\Local\Arduino15\preferences.txt, change all occurences (3) of -Os to -O2, restart Arduino IDE

## Licensing


## Author


## Acknowledgements
