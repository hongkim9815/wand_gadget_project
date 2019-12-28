#!/usr/bin/python3
"""
Title       autostart_led_blink.py
Author      Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made        28-Dec-2019
Comment     This program is test for autostart on Raspberry Pi.
            Required electric circuit is just connecting LED with pin6 (GND) and pin8 (GPIO14, TXD)
            Test process:
                1) Just execute this program.
                2) If it works well, then execute this program by using autostart scheme.
                   (Need to determine rc.local, systemd)
"""

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)                     # Ignore any warning
GPIO.setmode(GPIO.BOARD)                    # Use physical pin numbering system (40pin) on the board
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

for i in range(20):
    GPIO.output(8, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(8, GPIO.LOW)
    time.sleep(1)