#!/usr/bin/python3
"""
Title   animatedgif.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    21-Jan-2020
Comment This python library file is for controlling animated GIF files.
"""

import tkinter
from tkinter.font import Font
import time

# ================================================================================
# Utils
# ================================================================================

def gif2list(filename, minf=0, maxf=9999, speed=1):
    it, itmax = minf, maxf
    retlist = []

    while itmax > it * speed:
        try:
            retlist.append(tkinter.PhotoImage(file=filename,
                                              format='gif -index {}'.format(it * speed)))
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
    def __init__(self, root, frame=24, background=None, grid=None):
        self.MAXSIZE = 64

        self.root = root
        self.root.update()
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()

        self.canvas = tkinter.Canvas(self.root, bg="white", width=self.width, height=self.height)
        self.canvas.pack()
        self.canvas.place(x=0, y=0)
        if background is not None:
            self.canvas.create_image(0 + background.width() // 2, 0 + background.height() // 2,
                                     image=background)

        if grid is not None:
            for i in range(grid, self.width, grid):
                self.canvas.create_line(i, 0, i, self.height, fill='gray')
            for i in range(grid, self.height, grid):
                self.canvas.create_line(0, i, self.width, i, fill='gray')

        self.gifs = [None] * self.MAXSIZE
        self.gifs_position = [None] * self.MAXSIZE
        self.gifs_cycle = [None] * self.MAXSIZE
        self.gifs_frame = [None] * self.MAXSIZE
        self.gifs_overlap = [None] * self.MAXSIZE
        self.gifs_active = []

        self.objects = [None] * self.MAXSIZE
        self.objects_remove = []
        self.cis = [None] * self.MAXSIZE

        self.delay = 1/frame
        self.index = -1
        self.index_obj = -1
        self.execute = True

    def add(self, giflist, position, cycle=-1, overlap=False):
        self.index = (self.index + 1) % self.MAXSIZE

        rep = 0
        while self.gifs[self.index] is not None:
            self.index = (self.index + 1) % self.MAXSIZE
            rep += 1
            if rep > self.MAXSIZE:
                raise Exception("The number of active GIFs is over than maximum. "
                                + "Why don't you adjust \"AnimatedGifs().MAXSIZE\"?")

        self.gifs[self.index] = giflist
        self.gifs_position[self.index] = (position[0] + giflist[0].width() // 2,
                                          position[1] + giflist[0].height() // 2)
        self.gifs_cycle[self.index] = cycle + 1
        self.gifs_frame[self.index] = 0
        self.gifs_overlap[self.index] = overlap
        self.gifs_active.append(self.index)

        if overlap:
            self.cis[self.index] = []
        else:
            self.cis[self.index] = None

        return self.index

    # [v.03] Changed delete() to remove() for better understandability.
    def remove(self, index):
        if self.gifs[index] is None or index is -1:
            raise IndexError
        self.gifs[index] = None
        self.gifs_position[index] = None
        self.gifs_cycle[index] = None
        self.gifs_frame[index] = None
        self.gifs_active.remove(index)

        if self.gifs_overlap[index]:
            for ci in self.cis[index]:
                self.canvas.delete(ci)
        else:
            self.canvas.delete(self.cis[index])

        self.cis[index] = None

    def remove_ig(self, index):
        if self.isActive(index):
            self.remove(index)

    def addImage(self, image, position):
        self.index_obj = (self.index_obj + 1) % self.MAXSIZE

        rep = 0
        while self.objects[self.index_obj] is not None:
            self.index_obj = (self.index_obj + 1) % self.MAXSIZE
            rep += 1
            if rep > self.MAXSIZE:
                raise Exception("The number of active GIFs is over than maximum.")

        self.objects[self.index_obj] = self.canvas.create_image(position[0] + image.width() // 2,
                                                                position[1] + image.height() // 2,
                                                                image=image)
        return self.index_obj

    def removeImage(self, index):
        if self.objects[index] == None:
            raise IndexError

        self.objects_remove.append(index)

    def removeImage_ig(self, index):
        if self.isActiveImage(index):
            self.removeImage(index)

    def addText(self, text, position, font=None):
        self.index_obj = (self.index_obj + 1) % self.MAXSIZE

        rep = 0
        while self.objects[self.index_obj] is not None:
            self.index_obj = (self.index_obj + 1) % self.MAXSIZE
            rep += 1
            if rep > self.MAXSIZE:
                raise Exception("The number of active GIFs is over than maximum.")

        if font is None:
            font = Font(family='Helvetica', size=12, weight='bold')

        self.objects[self.index_obj] = self.canvas.create_text(position[0], position[1],
                                                               font=font, text=text, fill='#eeeeee')
        return self.index_obj

    def removeText(self, index):
        if self.objects[index] == None:
            raise IndexError

        self.objects_remove.append(index)

    def removeText_ig(self, index):
        if self.isActiveText(index):
            self.removeText(index)

    def start(self):
        self._animate()

    def stop(self):
        self.execute = False

    def isActive(self, index):
        if index is -1 or index is None:
            return False
        return self.gifs[index] is not None

    def isActiveImage(self, index):
        if index is -1 or index is None:
            return False
        return self.objects[index] is not None

    def isActiveText(self, index):
        if index is -1 or index is None:
            return False
        return self.objects[index] is not None

    def setPosition(self, index, position):
        self.gifs_position[index] = (position[0] + self.gifs[index][0].width() // 2,
                                     position[1] + self.gifs[index][0].height() // 2)

    def _configure(self):
        for i in self.gifs_active:
            if self.gifs[i] is not None:
                if self.gifs_overlap[i]:
                    if len(self.cis[i]) == len(self.gifs[i]):
                        for ci in self.cis[i]:
                            self.canvas.delete(ci)
                        self.cis[i] = []
                    tmp = self.canvas.create_image(self.gifs_position[i][0],
                                                   self.gifs_position[i][1],
                                                   image=self.gifs[i][self.gifs_frame[i]])
                    self.cis[i].append(tmp)
                else:
                    self.canvas.delete(self.cis[i])
                    self.cis[i] = self.canvas.create_image(self.gifs_position[i][0],
                                                           self.gifs_position[i][1],
                                                           image=self.gifs[i][self.gifs_frame[i]])
            else:
                self.canvas.delete(self.cis[i])
        for i in self.objects_remove:
            self.canvas.delete(self.objects[i])
            self.objects[i] = None
        self.objects_remove = []

    def _animate(self):
        if self.execute:
            for i in tuple(self.gifs_active):
                if self.gifs_frame[i] is 0 and self.gifs_cycle[i] is not -1:
                    self.gifs_cycle[i] -= 1
                    if self.gifs_cycle[i] is 0:
                        self.remove(i)
            self._configure()
            for i in self.gifs_active:
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


