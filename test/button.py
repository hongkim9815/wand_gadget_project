#!/usr/bin/python3
"""
Title   button.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    28-Jan-2020
Comment This program is for testing button on Raspberry Pi.
        Required electric circuit is connecting pin16 on one of the button's leg, 3.3V GCC on other
        part of its leg.
"""

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    if GPIO.input(16) == GPIO.HIGH:
        print("Button was pushed!")
    else:
        print("Button was unpushed...")
    time.sleep(0.1)
