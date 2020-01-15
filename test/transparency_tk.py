#!/usr/bin/python3
#-*- coding: utf8 -*-
"""
Title   transparency_tk.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    15-Jan-2020
Comment This program is test for GUI transparency of Raspberry Pi. It will test whether Tkinter
        module support transparent png and gif pixel.
        Test process:
            - Just execute this program.
        Result:
            - When PhotoImage() objects are in same canvas, then each transpa-
             rency of them works well on the window.
"""

import tkinter as tk
import time

root = tk.Tk()
root.geometry('1024x768')
root.title("Transparency")
root['bg'] = 'white'

sources_path = "../sources/"

# frame = tk.Frame(root)
# frame.pack()

canvas = tk.Canvas(root, bg="white", width=500, height=500)
canvas.pack()

photoimage = tk.PhotoImage(file=sources_path + "png1.png")
photoimage2 = tk.PhotoImage(file=sources_path + "png2.png")
canvas.create_image(150, 150, image=photoimage)
canvas.create_image(300, 300, image=photoimage2)

root.mainloop()



