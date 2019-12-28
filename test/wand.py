#!/usr/bin/python3
"""
Title       wand.py
Author      Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made        28-Dec-2019
Comment     This program is a testfile for checking the connection between wand and Raspberry Pi.
            Required electric circuit is just connecting LED with pin6 (GND) and pin8 (GPIO14, TXD).
            Also, you need a wand for the test.
            Test process:
                1) Just execute this program.
                2) Swing wand and gather RF-Data.
                3) Check the read data whether the data is aligned well or not.
"""

import serial
import RPi.GPIO as GPIO
import time

while(True):
    print("====================")
    s = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
    s.inter_byte_timeout = 0.01
    data = s.read(10000)
    # data = b"Kihong Working Now"
    print("DATA:    " + data.hex())
    print("Length:  " + str(len(str(data))))
    print("type:    " + data[0:1].hex() + "(" + str(data[0]) +")")
    print("cds:     " + data[1:2].hex() + "(" + str(data[1]) +")")
    print("id:      " + data[2:3].hex() + data[3:4].hex() +
          "(" + str(int.from_bytes(data[2:4], byteorder='little')) +")")
    print("rest:    " + data[4:].hex())

