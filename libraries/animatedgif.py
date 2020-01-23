#!/usr/bin/python3
"""
Title   animatedgif.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    21-Jan-2020
Comment This python library file is for controlling animated GIF files.
"""

import tkinter
import time

# ================================================================================
# Utils
# ================================================================================

def _gcd(a, b):
    while b is not 0:
        a, b = (b, a % b) if a > b else (a, b % a)
    return a


def gif2list(filename, minf=0, maxf=9999):
    it, itmax = minf, maxf
    retlist = []

    while itmax != it:
        try:
            retlist.append(tkinter.PhotoImage(file=filename,
                                            format='gif -index {}'.format(it)))
            it += 1
        except tkinter.TclError:
            break

    if len(retlist) is 0:
        raise Exception("File: " + filename + "is not exist")

    return retlist

# ================================================================================
# AnimatedGifs Class: cloned by main.py
# ================================================================================

class AnimatedGifs:
    def __init__(self, root, frame=24):
        self.root = root
        self.root.update()
        self.canvas = tkinter.Canvas(self.root, bg="white",
                                     width=self.root.winfo_width(),
                                     height=self.root.winfo_height())
        self.canvas.pack()
        self.canvas.place(x=0, y=0)
        self.gifs = []
        self.gifs_position = []
        self.gifs_cycle = []

        self.gifs_frame = []
        self.cis = []
        self.delay = 1/frame
        self.size = 0
        self.execute = True

    def add(self, giflist, position, cycle=-1):
        self.size += 1
        self.gifs.append(giflist)
        self.gifs_position.append(position)
        self.gifs_cycle.append(cycle + 1)
        self.gifs_frame.append(0)
        self.cis.append(None)
        return self.size - 1

    def delete(self, index):
        if self.gifs[index] is None or index is -1:
            raise IndexError
        self.gifs[index] = None
        self.gifs_position[index] = None
        self.gifs_cycle[index] = None
        self.gifs_frame[index] = None

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
        for i in range(self.size):
            if self.gifs[i] is not None:
                self.canvas.delete(self.cis[i])
                self.cis[i] = self.canvas.create_image(self.gifs_position[i][0],
                                                       self.gifs_position[i][1],
                                                       image=self.gifs[i][self.gifs_frame[i]])
            else:
                self.canvas.delete(self.cis[i])

    def _animate(self):
        if self.execute:
            for i in range(len(self.gifs)):
                if self.gifs[i] is not None and self.gifs_frame[i] is 0:
                    self.gifs_cycle[i] -= 1
                    if self.gifs_cycle[i] is 0:
                        self.delete(i)
            self._configure()
            for i in range(self.size):
                if self.gifs[i] is not None:
                    self.gifs_frame[i] = (self.gifs_frame[i] + 1) % len(self.gifs[i])
            self.root.after(int(self.delay * 1000), self._animate)


if __name__ == "__main__":
    root = tkinter.Tk()
    root.geometry('1024x768')
    root['bg'] = 'white'

    sources_path = "sources/"

    gif1 = []
    gif2 = []

    gif1 = gif2list(sources_path + 'gif2.gif', 0, 20)
    gif2 = gif2list(sources_path + 'maingif2.gif', 0, 20)
    points = []
    anigif = AnimatedGifs(root, frame=24)
    anigif.add(gif1, (200, 200))
    anigif.add(gif2, (400, 400))
    anigif.start()
    root.mainloop()


