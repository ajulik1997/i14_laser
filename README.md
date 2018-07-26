# I14 Remote Laser Controller

Software developed for the remote control and monitoring of a laser at the [Diamond Light Source I14 instrument](https://www.diamond.ac.uk/Instruments/Imaging-and-Microscopy/I14.html).

The modular design of the code as well as the following documentation is designed as a guide to simply the processes of installing the software, using it for its intended purpose, extending its functionality, or applying it to other components or instruments.

## Table of Contents

- [Introduction](#introduction)
- [The Hardware](#the-hardware)
  - [Raspberry Pi](#raspberry-pi)
    - [Operating System](#operating-system)
    - [Pin Assignment](#pin-assignment)
    - [Python](#python)
  - [Laser](#laser)
  - [Digital to Analog Converter](#digital-to-analog-converter)
- [The Software](#the-software)
  - [Server](#server)
    - [Client](#client)
  - [Parser](#parser)
    - [Table of Recognised Commands](#table-of-recognised-commands)
  - [Error Handler](#error-handler)
    - [Table of Errors and Warnings](#table-of-errors-and-warnings)
- [Licensing](#licensing)
- [Author](#author)
- [Acknowledgements](#acknowledgements)
  
## Introduction

At the core of this "system" lies a [Raspberry Pi](https://www.raspberrypi.org/), used as a smart networked microcontroller running a python script which enables it to process text-based commands. A laser (or in theory, any other device that needs to be controlled) is connected to the Raspberry Pi via a USB-to-Serial interface. Other interfaces, such as I<sup>2</sup>C As the GPIO pins on the Pi are exclusively digital, a Digital-to-Analog converter tied to the Pi I<sup>2</sup>C-over-GPIO interface is also used to provide any necessary <CONTINUE FROM HERE>

## The Hardware

### Raspberry Pi

#### Operating System

#### Pin Assignment

#### Python

### Laser

### Digital to Analog Converter

## The Software

### Server

#### Client

### Parser

#### Table of Recognised Commands

### Error handler

#### Table of Errors and Warnings

## Licensing

## Author

## Acknowledgements
