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
        Result:
            - It works well. However, there is very big issue with utilizing Tkinter and serial
             connection. When Serial reads or request is waiting for receive any json data, gif in
             Tkinter display is stopped. This is because there is only one thread, so getting json
             should be waited. Thus, the next implementation should be "Threading based serial
             connection" or "multiprocessing based serial connection".
"""

import RPi.GPIO as GPIO
import tkinter as tk
import time
from libraries.wandlib import read_serial, print_data_enc, data2point, setVerbose, getAction
from multiprocessing import Pool, Queue

VERBOSE = True

GPIO.setwarnings(False)                      # Ignore any warning
GPIO.setmode(GPIO.BOARD)                    # Use physical pin numbering system (40pin) on the board
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)

root = tk.Tk()
root.geometry('1024x768')
root['bg'] = 'white'

sources_path = "../sources/"

setVerbose(True)



# ================================================================================
# Utils
# ================================================================================

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


# ================================================================================
# AnimatedGifs Class
# ================================================================================

class AnimatedGifs:
    def __init__(self, root, delay=0.04):
        self.root = root
        self.canvas = tk.Canvas(self.root, bg="white", width=1024, height=768)
        self.canvas.pack()
        self.canvas.place(x=0, y=0)
        self.gifs = []
        self.gifs_position = []
        self.cis = []
        self.max_frame = 1
        self.delay = delay
        self.execute = True
        self._it = 0

    def add(self, giflist, position, frame=1):
        self.max_frame = int(len(giflist) * self.max_frame / gcd(len(giflist), self.max_frame))
        self.gifs.append(giflist)
        self.gifs_position.append(position)
        self.cis.append(None)
        return len(self.gifs) - 1

    def delete(self, index, frame=1):
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
                self.cis[i] = self.canvas.create_image(self.gifs_position[i][0],
                                                       self.gifs_position[i][1],
                                                       image=self.gifs[i][frame4gif])
            else:
                self.canvas.delete(self.cis[i])

    def _animate(self):
        self._configureLabel()
        self._it = (self._it + 1) % self.max_frame
        if self.execute:
            self.root.after(int(self.delay * 1000), self._animate)

cnt = 0
gif1code = -1
gif2code = -1
gif1 = gif2list(sources_path + 'gif1.gif', 0, 20)
gif2 = gif2list(sources_path + 'gif2.gif', 0, 20)

def wand_data_process(root, ser, points):
    ser, data = read_serial(ser)
    global gif1code
    global gif2code
    global cnt
    # print(points)
    if len(str(data)) > 4 and data[0] is 0x02:
        data_enc = print_data_enc(data)
        points.extend(data2point(data_enc['data_rest']))
        action = getAction(data_enc['wand_uid'], points)
        print("ACTION : ", action)
        points = []
    elif len(str(data)) > 4:
        data_enc = print_data_enc(data)
        points.extend(data2point(data_enc['data_rest']))
    else:
        print("Serial does not detect any signal.")


    if cnt > 10:
        print("CNT DOUBLE ON")
        if cnt is 11:
            print("ON!")
            gif1code = anigif.add(gif1, (800, 200))
            anigif.delete(gif2code)
    elif cnt > 5:
        print("CNT ON!: " + str(cnt))
        if cnt is 6:
            print("ON!")
            anigif.delete(gif1code)
            gif2code = anigif.add(gif2, (500, 200))
    else:
        print("wait!: " + str(cnt))
    cnt+= 1
    root.after(1000, wand_data_process, root, ser, points)


if __name__ == "__main__":
    ser = None
    points = []
    root.after(10, wand_data_process, root, ser, points)

    anigif = AnimatedGifs(root, delay=0.01)
    gif1code = anigif.add(gif1, (200, 200))
    anigif.start()

    root.mainloop()
