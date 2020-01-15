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

class AnimatedGif:
    def __init__(self, root, delay=0.04):
        self.root = root
        self.canvas = tk.Canvas(self.root, bg="white", width=500, height=500)
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

    def remove(self, index, frame=1):
        # self.max_frame = ??     # Convension?
        self.gifs = self.gifs[:index] + self.gifs[index+1:]
        self.cis.append

    def start(self):
        self._animate()

    def stop(self):
        self.execute = False

    def _configureLabel(self):
        for i in range(len(self.gifs)):
            frame4gif = self._it % len(self.gifs[i])
            self.canvas.delete(self.cis[i])
            self.cis[i] = self.canvas.create_image(i * 200, i * 200, image=self.gifs[i][frame4gif])

    def _animate(self):
        self._configureLabel()
        self._it = (self._it + 1) % self.max_frame
        if self.execute:
            self.root.after(int(self.delay * 10000), self._animate)

def gif2list(filename, given_list, maxf=9999):
    it = 0
    while maxf != it:
        try:
            given_list.append(tk.PhotoImage(file=filename,
                                            format='gif -index {}'.format(it)))
            it += 1
            print(it)
        except tk.TclError:
            break

    if len(given_list) is 0:
        raise Exception("File: " + filename + "is not exist")

gif1_list = []
gif2_list = []
gif3_list = []
gif2list(sources_path + 'gif1.gif', gif1_list, 10)
gif2list(sources_path + 'gif2.gif', gif2_list)
gif2list(sources_path + 'gif3.gif', gif3_list, 10)

anigif = AnimatedGif(root,delay=0.03)
gif1code = anigif.add(gif1_list)
gif2code = anigif.add(gif2_list)
gif3code = anigif.add(gif3_list)
anigif.start()
root.mainloop()
time.sleep(5)
anigif.stop()

