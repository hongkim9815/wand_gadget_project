#!/usr/bin/python3
"""
Title   alpha.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    05-Feb-2020
Comment This program is test for alpha channel of png file.
        The biggest purpose is making list of png images which have different alpha channel value,
        so that are able to be utilized in animatedGifs() class.
        Test process:
            - Just execute this program in main directory.
"""

import tkinter
from PIL import Image, ImageTk
from glob import glob
from libraries.animatedgif import AnimatedGifs

def gif2list_png(img, frame, frame_duplicate=1):
    retlist = []
    x, y = img.size
    it = list(range(frame)) + [frame] + list(range(frame, 0, -1))

    for k in it:
        print(k)
        tmpimg = img.copy()
        for i in range(x):
            for j in range(y):
                pix = tmpimg.getpixel((i, j))
                tmpimg.putpixel((i, j), (pix[0], pix[1], pix[2], int(pix[3] * 1 / frame * k)))
        for i in range(frame_duplicate):
            retlist.append(ImageTk.PhotoImage(tmpimg))

    return retlist


def roundCourse(img, radius=20, resize=None):
    x, y = img.size

    for i in range(radius):
        for j in range(radius):
            if (i - radius) ** 2 + (j - radius) ** 2 > radius ** 2:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    for i in range(x-radius, x):
        for j in range(radius):
            if (i - x + radius) ** 2 + (j - radius) ** 2 > radius ** 2:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    for i in range(radius):
        for j in range(y-radius,y):
            if (i - radius) ** 2 + (j - y + radius) ** 2 > radius ** 2:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    for i in range(x-radius,x):
        for j in range(y-radius,y):
            if (i - x + radius) ** 2 + (j - y + radius) ** 2 > radius ** 2:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    return ImageTk.PhotoImage(img)


def getBadgeFrame(img):
    x, y = img.size

    for i in range(x):
        for j in range(y):
            pix = img.getpixel((i, j))
            statement = (i - x / 2) ** 2 + (j - y / 2) ** 2
            for k in range(10):
                if statement < (71 - 0.1 * k) ** 2:
                    img.putpixel((i, j), (pix[0], pix[1], pix[2], int(0.1 * (9 - k) * 255)))
    img.save(SOURCES_PATH + "badge/badgeframe.png")


if __name__ == "__main__":
    TKROOT = tkinter.Tk()
    TKROOT.geometry('1024x768')
    TKROOT['bg'] = 'black'

    MAIN_PATH = "../"
    SOURCES_PATH = MAIN_PATH + "sources/"
    TMP_PATH = MAIN_PATH + "tmp/"

    IMAGES = dict()
    GIFS = dict()
    IMAGES['background'] = tkinter.PhotoImage(file=SOURCES_PATH + 'background_frame.png')

    ANIGIF = AnimatedGifs(TKROOT, frame=24, background=IMAGES['background'])

    """
    for f in glob(SOURCES_PATH + "badge/" + "user_badge_*"):
        imgtmp = Image.open(f)
        tmp = gif2list_png(imgtmp, 6, 2)
        print(tmp)
        ANIGIF.add(tmp, (200, 200), overlap=False)

    ANIGIF.start()
    """

    """
    for f in glob(SOURCES_PATH + "course/" + "course_*"):
        tmp = roundCourse(Image.open(f))
        ANIGIF.addImage(tmp, (100, 100))
    TKROOT.mainloop()
    """

    getBadgeFrame(Image.open(SOURCES_PATH + "badge/badge_mythical_owl.png"))

