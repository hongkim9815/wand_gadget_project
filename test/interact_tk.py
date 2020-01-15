#!/usr/bin/python3
"""
Title   interact_tk_wand.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    15-Jan-2020
Comment This program is test for interaction of Raspberry Pi when tk.Tk().mainloop() is active.
        Besides, This program test for interaction between tk and wand.
        Required electric circuit is connecting on pin11 for LED, pin8 for TXD, and pin10 for RXD
        of NDmesh module (RF connection module).
        Also, you need a wand for the test.
        Test process:
            1) Just execute this program.
            2) Swing wand and gather RF-data.
            3) Check LED and Tkinter window. If LED works and Tkinter shows some behaviour.
"""

import RPi.GPIO as GPIO
import tkinter as tk
import time
import wand

GPIO.setwarning(False)                      # Ignore any warning
GPIO.setmode(GPIO.BOARD)                    # Use physical pin numbering system (40pin) on the board
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)

raise NotImplementedError

"""
TODO    Implement this file to test following list...
        wand / wand connection / Tkinter / animated gif / led / ...
"""

