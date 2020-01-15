#!/usr/bin/python3
"""
Title   autostart_led_blink.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    28-Dec-2019
Comment This program is test for autostart on Raspberry Pi. Required electric circuit is just
        connecting LED on pin11, pin13, pin15, and pin19.
        Test process:
            1) Just execute this program.
            2) If it works well, then execute this program by using autostart scheme.
             (You need to decide a method you want: rc.local, systemd)
        Known failed process:
            - If the board turns on pin13, pin15, then pin11 is turned off the current
             automatically. After then, when both of pin13 and pin15 are turned off, pin11 is
             automatically turned on if the board did not give any signal.
"""

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

pin_number = [11, 13, 15, 19]

for i in pin_number:
    GPIO.setup(i, GPIO.OUT, initial=GPIO.LOW)
    time.sleep(1)

for i in range(20):
    for j in pin_number:
        GPIO.output(i, GPIO.HIGH)
    time.sleep(2)
    for j in pin_number:
        GPIO.output(i, GPIO.LOW)
    time.sleep(2)
