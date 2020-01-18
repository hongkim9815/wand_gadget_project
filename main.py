#!/usr/bin/python3
"""
Title   main.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    17-Jan-2020 (cloned from test/interact_tk_wand.py)
Comment This program is a main file of the project.
        Required electric circuit is connecting on pin11 for LED, pin8 for TXD, and pin10 for RXD
        of NDmesh module (RF connection module).
Usage   NOT IMPLEMENTED
"""

import RPi.GPIO as GPIO
import tkinter as tk
import time
from libraries.wandlib import read_serial, print_data_enc, data2point, setVerbose, getAction
from multiprocessing import Pool, Queue

VERBOSE = True

GPIO.setwarnings(False)                     # Ignore any warning
GPIO.setmode(GPIO.BOARD)                    # Use physical pin numbering system (40pin) on the board
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)

root = tk.Tk()
root.geometry('1024x768')
root['bg'] = 'white'

sources_path = "sources/"

setVerbose(True)

ser = None
gif1 = []
gif2 = []

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
        self.gifs_cycle = []
        self.cis = []
        self.max_frame = 1
        self.delay = delay
        self.execute = True
        self._it = 0

    def add(self, giflist, position, cycle=-1):
        self.max_frame = int(len(giflist) * self.max_frame / gcd(len(giflist), self.max_frame))
        self.gifs.append(giflist)
        self.gifs_position.append(position)
        self.gifs_cycle.append(cycle)
        self.cis.append(None)
        return len(self.gifs) - 1

    def delete(self, index):
        # self.max_frame = ??     # Convension?
        if self.gifs[index] is None or index is -1:
            raise IndexError
        self.gifs[index] = None
        self.gifs_position[index] = None
        self.gifs_cycle[index] = None
        # self.cis[index] = None  # Done by self._configure()

    def start(self):
        self._animate()

    def stop(self):
        self.execute = False

    def isPlay(self, index):
        if index is -1:
            raise IndexError
        return self.gifs[index] is not None

    def setPosition(self, index, position):
        self.gifs_position[index] = position

    """
    setSize(,,):    Issue: This function is not tested thoroughly... (it might be very very slow)
                    It should be fixed if there is better method to resize PhotoImage.
    """
    def setSize(self, index, size_mul):
        obj_list = self.gifs[index]
        for i in range(len(obj_list)):
            tmp = obj_list[i].subsample(int(1 / size_mul * 10))
            tmp = obj_list[i].zoom(10)
        self.gifs[index] = obj_list

    def _configure(self):
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
        self._configure()
        self._it = (self._it + 1) % self.max_frame
        if self.execute:
            for i in range(len(self.gifs)):
                if self.gifs[i] is not None and (self._it is 0 or self._it is len(self.gifs[i])):
                    self.gifs_cycle[i] -= 1
                if self.gifs_cycle[i] is 0:
                    self.delete(i)
            self.root.after(int(self.delay * 1000), self._animate)


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

    if cnt > 6:
        print("CNT DOUBLE ON")
        if cnt is 7:
            print("ON!")
            gif1code = anigif.add(gif1, (800, 200), cycle=2)
            anigif.delete(gif2code)
    elif cnt > 3:
        print("CNT ON!: " + str(cnt))
        if cnt is 4:
            print("ON!")
            anigif.delete(gif1code)
            gif2code = anigif.add(gif2, (500, 200))
    else:
        print("wait!: " + str(cnt))
    cnt+= 1
    root.after(1000, wand_data_process, root, ser, points)


def controlMainView(ag, rec, rec_index=-1):
    global ser

    if not rec:
        rec_index = ag.add(gif1, (100, 100), cycle=3)

    ser, data = read_serial(ser)
    if len(str(data)) > 4:
        if ag.isPlay(rec_index):
            ag.delete(rec_index)
        controlSubview1(ag, False)
    else:
        ag.root.after(200, controlMainView, ag, True, rec_index)


def controlSubview1(ag, rec, rec_index=-1, rec_time=-1):
    if not rec:
        rec_index = ag.add(gif2, (200, 200))
        rec_time = time.time()

    if rec_time + 5 < time.time():
        ag.delete(rec_index)
        controlMainView(ag, False)
    else:
        ag.root.after(200, controlSubview1, ag, True, rec_index, rec_time)


if __name__ == "__main__":
    gif1 = gif2list(sources_path + 'gif2.gif', 0, 20)
    gif2 = gif2list(sources_path + 'maingif2.gif', 0, 20)

    points = []
    # root.after(10, wand_data_process, root, ser, points)

    anigif = AnimatedGifs(root, delay=0.04)
    anigif.start()
    controlMainView(anigif, False)

    root.mainloop()

# TODO: - Add more views
#       - Merge weather view to this code
#       - Serial Data test
#       - Threading

