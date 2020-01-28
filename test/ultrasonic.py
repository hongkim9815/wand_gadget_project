#!/usr/bin/python3
"""
Title   ultrasonic.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    28-Jan-2020
Comment This program is for testing ultrasonic distance sensor HC-SR04 on Raspberry Pi.
        Required electric circuit is represented in below link:
            https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04
        Test process:
            1) Just execute this program.

        - INCOMPLETELY IMPLEMENTED
"""

import RPi.GPIO as GPIO
from time import sleep, time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 18
GPIO_ECHO = 24

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    GPIO.output(GPIO_TRIGGER, True)

    sleep(0.0001)
    GPIO.output(GPIO_TRIGGER, False)

    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time()

    TimeElapsed = StopTime - StartTime

    return TimeElapsed * 34300 / 2

if __name__ == "__main__":
    while True:
        dist = distance()
        print ("Measured Distance = %.1f cm" % dist)
        sleep(1)
