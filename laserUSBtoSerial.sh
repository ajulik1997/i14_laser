#!/bin/bash
modprobe ftdi_sio
echo 0d4d 003d > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
udevadm control --reload && udevadm trigger