#!/usr/bin/python3
#-*- coding: utf8 -*-
"""
Title   gif_tk.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    11-Jan-2020
Comment This program is test for GUI performance of Raspberry Pi. It will test
        whether gif is played well on tkinter well or not.
        Test process:
            1) Move this file to the main folder (wand_tool_project/)
            2) Just execute this program.
"""
import requests
from tkinter import *
import libraries.AnimatedGif as agif
import time

tkmain = Tk()
tkmain.geometry('720x480')
gif = agif.AnimatedGif(tkmain, "sources/simple-gif.gif", delay=0.005)
gif.pack()
gif.start()
tkmain.mainloop()
