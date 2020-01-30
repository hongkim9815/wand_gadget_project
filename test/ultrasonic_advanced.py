#!/usr/bin/python3
"""
Title   ultrasonic_advanced.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    30-Jan-2020
Comment This test is for knowing how accurate and how compatible the distance sensor HC-SR04 detect
        the distance of object.
        Required electric circuit is almost similar in below link:
            https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04
            - However, for compatibility with other module, TRIG should be connected on pin11. and
             ECHO should be connected on pin12./
Result
        Range:          5 cm ~ 140 cm (Validated within 5% error)
        Accuracy:       Less than 2% (1.27% for 15cm, 1.38 for 30cm, 1.45% for 50cm (100 < # data))
        Compatibility:  Compatible when NDmesh(pin8, pin10), button(pin16), LED(pin15) are in use.
        Printed :       <NOTHING>
"""

import RPi.GPIO as GPIO
from time import sleep, time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

hc_trig = 11
hc_echo = 12
GPIO.setup(hc_trig, GPIO.OUT)
GPIO.setup(hc_echo, GPIO.IN)

while True:
    GPIO.output(hc_trig, True)
    sleep(0.00001)
    GPIO.output(hc_trig, False)

    echo = GPIO.input(hc_echo)

    if echo == 1:
        sleep(0.2)
        print("ERROR")
        continue

    while echo == 0:
        StartTime = time()
        echo = GPIO.input(hc_echo)

    while echo == 1:
        StopTime = time()
        echo = GPIO.input(hc_echo)

    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    print(distance)
    sleep(0.2)
