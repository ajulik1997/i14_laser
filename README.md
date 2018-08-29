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
    - [Pin Assignment](#pin-assignment)
    - [Python](#python)
  - [Laser](#laser)
  - [Arduino](#arduino)
    - [Pin Assignment](#pin-assignment)
  - [Digital to Analog Converter](#digital-to-analog-converter)
    - [Laser modulation](#laser-modulation)
- [The Software](#the-software)
  - [Server](#server)
    - [Client](#client)
  - [Parser](#parser)
    - [Table of Recognised Commands](#table-of-recognised-commands)
  - [Error Handler](#error-handler)
    - [Table of Errors and Warnings](#table-of-errors-and-warnings)
  - [Laser Serial Communication Script](#laser-serial-communication-script)
  - [Arduino Controller Script (Python)](#arduino-controller-script-python)
    - [Arduino Controller Script (C for AVR)](#arduino-controller-script-c-for-avr)
- [Licensing](#licensing)
- [Author](#author)
- [Acknowledgements](#acknowledgements)
  
## Introduction

At the core of this "system" lies a [Raspberry Pi](https://www.raspberrypi.org/), used as a server running a python script which allows it to process text-based commands that it receives over network. A [Coherent Laser](https://www.coherent.com/) is connected to the Raspberry Pi via a USB-to-Serial interface, enabling the Pi to send commands to the laser and monitor its status. An [Arduino board](https://www.arduino.cc/) is also connected to the Raspberry Pi via a USB-to-Serial as well as a GPIO interface, and is mainly responsible for realtime generation of waveforms that are used to modulate the laser via a Digital-to-Analog converter. Additionally, a camera can also be connected to the Arduino, which is able to synchronise the camera's shutter with the modulation of the laser.

### Key Features

## The Hardware

The following section decuments the steps required to correctly set up the hardware. It describes the setup of the operating system on the Raspberry Pi, as well as the required wiring between the Raspberry Pi, Arduino, DAC, laser and camera.

### Raspberry Pi

The Raspberry Pi used in this project is the [Raspberry Pi 3 B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) (upgraded from the Raspberry Pi B Rev 2.0 on which developement took place), chosen due to the following features:
  - 1.4GHz processor (upgraded from 700Mhz)
  - 1GB SDRAM (upgraded from 512MB)
  - 40 GPIO pins (upgraded from 26)
  - Gigabit Ethernet
  - MicroSD port
  - PoE support
  
According to our specification, the Raspberry Pi needs to be set up so that it can do the following:
  - run a headless Linux OS
  - communicate over SSH
  - run code written in Python
  - <INSERT MORE ITEMS HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!>

#### Operating System

The operating system chosen for this project was [Raspbian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/), an OS based on Debian Stretch with no desktop interface, chosen for its minimal footprint and high compatibility with Raspberry Pi. The required image was downloaded from the [official mirror](https://downloads.raspberrypi.org/raspbian_lite_latest), and written to a 16GB microSD card according to the [installation instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).

As the Pi is being used a server, it needs to be set up to run headless. This process is described in detail [here](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md), but the most important step (activating SSH), can be acomplished by mounting the SD card on any Windows or 

#### Drivers and Packages

<TALK ABOUT DRIVER> <avrdude>

#### Pin Assignment

#### Python

<VERSION, PACKAGES>

### Laser

<MODEL, DOCUMENTATION, CONTROLLER, USB-TO-SERIAL, ARDUINO???>

### Arduino

<MODEL, STORAGE, MEMORY>

<MODES OF OPERATION, MODES OF MODULATION>

#### Pin Assignment

<LIST OF ASSIGNED PINS> <WIRING DIAGRAM>

### Digital to Analog Converter

<SPECIFICATION> <DATA SHEET> <I2C>
  
#### Laser Modulation

<Oscilloscope>

## The Software

### Server

#### Client

### Parser

#### Table of Recognised Commands

### Error handler

#### Table of Errors and Warnings

### Laser Serial Communication Script

### Arduino Controller Script (Python)

#### Arduino Controller Script (C for AVR)

## Licensing

## Author

## Acknowledgements
