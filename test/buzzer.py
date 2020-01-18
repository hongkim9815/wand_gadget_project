#!/usr/bin/python3
"""
Title   buzzer.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    17-Jan-2020
Comment This program is for testing buzzer autostart on Raspberry Pi.
        Required electric circuit is connecting buzzer on pin13.
        Test process:
            1) Just execute this program.
"""

from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(27)                 # This is because pin13 is GP27.

buzzer.on()
sleep(1)
buzzer.off()
