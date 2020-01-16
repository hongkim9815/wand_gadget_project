#!/usr/bin/python3
"""
Title   gif_tk.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    11-Jan-2020
Comment This program is test for GUI performance of Raspberry Pi. It will test whether gif is
        played well on tkinter well or not.
        Test process:
            - Just execute this program.
"""

import tkinter as tk
import time

root = tk.Tk()
root.geometry('1024x768')
root['bg'] = 'white'

sources_path = "../sources/"


def gcd(a, b):
    while b is not 0:
        a, b = (b, a % b) if a > b else (a, b % a)
    return a


def gif2list(filename, minf=0, maxf=9999):
    it, itmax = minf, maxf
    retlist = []

    while itmax != it:
        try:
            retlist.append(tk.PhotoImage(file=filename,
                                         format='gif -index {}'.format(it)))
            it += 1
            print(it)
        except tk.TclError:
            break

    if len(retlist) is 0:
        raise Exception("File: " + filename + "is not exist")

    return retlist


class AnimatedGif:
    def __init__(self, root, delay=0.04):
        self.root = root
        self.canvas = tk.Canvas(self.root, bg="white", width=1024, height=768)
        self.canvas.pack()
        self.canvas.place(x=0, y=0)
        self.gifs = []
        self.cis = []
        self.max_frame = 1
        self.delay = delay
        self.execute = True
        self._it = 0

    def add(self, giflist, frame=1):
        self.max_frame = int(len(giflist) * self.max_frame
                             / gcd(len(giflist), self.max_frame))
        self.gifs.append(giflist)
        self.cis.append(None)
        return len(self.gifs) - 1

    def remove(self, index):
        # self.max_frame = ??     # Convension?
        self.gifs[index] = None
        # self.cis[index] = None  # Done by self._configureLabel()

    def start(self):
        self._animate()

    def stop(self):
        self.execute = False

    def _configureLabel(self):
        for i in range(len(self.gifs)):
            if self.gifs[i] is not None:
                frame4gif = self._it % len(self.gifs[i])
                self.canvas.delete(self.cis[i])
                self.cis[i] = self.canvas.create_image((i+2) * 100, (i+2) * 100,
                                                       image=self.gifs[i][frame4gif])
            else:
                self.canvas.delete(self.cis[i])
    def _animate(self):
        self._configureLabel()
        self._it = (self._it + 1) % self.max_frame
        if self._it > 110:
            self.root.after(int(self.delay * 1000), self.remove(3))
        if self.execute:
            self.root.after(int(self.delay * 1000), self._animate)


gif1_list = gif2list(sources_path + 'gif1.gif', 0, 30)
gif2_list = gif2list(sources_path + 'gif2.gif')
gif3_list = gif2list(sources_path + 'gif1.gif', 30, 40)
gif4_list = gif2_list[:]
gif5_list = gif2list(sources_path + 'gif1.gif', 40, 55)

anigif = AnimatedGif(root,delay=0.01)
gif1code = anigif.add(gif1_list)
gif2code = anigif.add(gif2_list)
gif3code = anigif.add(gif3_list)
gif4code = anigif.add(gif4_list)
gif5code = anigif.add(gif5_list)
anigif.start()
root.mainloop()

