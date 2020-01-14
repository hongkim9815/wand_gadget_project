#!/usr/bin/python3
#-*- coding: utf8 -*-
"""
Title   gif_tk.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    11-Jan-2020
Comment This program is test for GUI performance of Raspberry Pi. It will test whether gif is play-
        ed well on tkinter well or not.
        Test process:
            - Just execute this program.
"""

import tkinter as tk
import time

root = tk.Tk()
root.wm_attributes('-alpha', 0.7)
root.geometry('1024x768')
root['bg'] = 'white'

def gcd(a, b):
    while b is not 0:
        if a > b:
            a, b = b, a % b
        else:
            a, b = a, b % a
    return a

class AnimatedGif:
    def __init__(self, root, delay=0.04):
        self.root = root
        self.gifs = []
        self.gifs_label = []
        self.gifs_frame = []
        self.max_frame = 1
        self.delay = delay
        self.execute = True
        self._it = 0

    def add(self, giflist, frame=1):
        self.max_frame = int(self.max_frame * len(giflist) / gcd(self.max_frame, len(giflist)))
        self.gifs.append(giflist)
        self.gifs_label.append(tk.Label(self.root))
        self.gifs_frame.append(frame)

    def _labelplace(self):
        for i in range(len(self.gifs)):
            self.gifs_label[i]['bg'] = 'black'
            self.gifs_label[i].place(x = i * 200, y = i * 200)

    def start(self):
        self._labelplace()
        self._animate()

    def stop(self):
        self.execute = False

    def _configureLabel(self):
        for i in range(len(self.gifs)):
            self.gifs_label[i].configure(image=self.gifs[i][self._it % len(self.gifs[i])])

    def _animate(self):
        self._configureLabel()
        self._it = (self._it + 1) % self.max_frame
        if self.execute:
            self.root.after(int(self.delay*1000), self._animate)

def gif2list(filename, given_list, maxf=9999):
    it = 0
    while maxf != it:
        try:
            given_list.append(tk.PhotoImage(file=filename, format='gif -index {}'.format(it)))
            it += 1
            print(it)
        except tk.TclError:
            break

gif1_list = []
gif2_list = []
gif3_list = []
gif2list('sources/gif1.gif', gif1_list, 11)
gif2list('sources/gif2.gif', gif2_list, 15)
gif2list('sources/gif3.gif', gif3_list, 19)

anigif = AnimatedGif(root)
anigif.add(gif1_list)
anigif.add(gif2_list)
anigif.add(gif3_list)
anigif.start()
root.mainloop()

