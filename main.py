#!/usr/bin/python3
"""
Title   main.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    21-Jan-2020 (cloned from test/interact_tk_wand.py)
Comment This program is a main file of the project.
        Required electric circuit is connecting on pin11 for LED, pin8 for TXD, and pin10 for RXD
        of NDmesh module (RF connection module), pin16 for button, pin11 for TRIG, pin12 for ECHO
        of HC-SR04 module (ultrasonic distance sensor module).
Usage   Execute this program in GUI environment with 1024x768 resolution.
"""

import tkinter
from tkinter.font import Font
from PIL import Image, ImageTk
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list, gif2list_v2
import RPi.GPIO as GPIO
from multiprocessing import Process, Queue
from time import sleep, time
from glob import glob
from gtts import gTTS
from os import system
from random import random


# ================================================================================
# INITIALIZE CONSTANTS AND VARIABLES
# ================================================================================

if __name__ == "__main__":

# CONSTANTS: Constants to define options and stable constants
    FADEIN_PHASE = -1
    INITIAL_PHASE = 0
    DELAYED_PHASE = 99
    MAIN_FRAME = 24
    MAIN_VIEW_EXECUTE_TIME = 10
    DRAW_VIEW_EXECUTE_TIME = 10
    BADGE_VIEW_EXECUTE_TIME = 5
    DRAW_VIEW_SMOOTH = 7

    ULTRASONIC_DETECT_COUNT = 2
    ULTRASONIC_DETECT_DISTANCE = 120

    VERBOSE = False
    if VERBOSE:
        print("INITIALIZING CONSTANTS AND VARIABLES...")


# PATH: Sources' path of the file directory.
    MAIN_PATH = ""
    SOURCES_PATH = MAIN_PATH + "sources/"
    TMP_PATH = MAIN_PATH + "tmp/"
    BADGE_PATH = SOURCES_PATH + "badge/"
    COURSE_PATH = SOURCES_PATH + "course/"


# TKROOT: Tkinter Class Tk()
#         Root Class of Tkinter main window.
    TKROOT = tkinter.Tk()
    TKROOT.geometry('1024x768')
    TKROOT['bg'] = 'white'
    TKROOT.attributes('-fullscreen', True)


    IMAGES = dict()
    GIFS = dict()


    if VERBOSE:
        print("DONE.")

# ================================================================================
# Utils
# ================================================================================

# png2list(): Make animated gif with a png file.
def png2list(filename, frame, frame_duplicate=1, resize=None, effect=None):
    retlist = []                    # List(PhotoImage())
    img = Image.open(filename)      # Image()

    if resize is not None:
        img = img.resize(resize, Image.ANTIALIAS)
    x, y = img.size
    img_copied = img.copy()

    # remove path and extension of filename
    filename = filename[:-4]
    while '/' in filename:
        filename = filename[filename.index('/') + 1:]

    # set 'frame_range' depending on effect
    if effect is None:
        frame_range = list(range(1 + frame + 1))
    else:
        if 'reverse' in effect:
            frame_range = list(range(frame, 0, -1))
        elif 'gliter' in effect:
            frame_range = list(range(1, frame + 1)) + list(range(frame - 1, 0, -1))
        else:
            frame_range = list(range(1 + frame + 1))

        if 'round' in effect:
            img = roundImage(img)

    for k in frame_range:
        # if a temporary file is exist
        if len(glob(TMP_PATH + filename + "-%02d-%02d-%03d-%03d.png" % (frame, k, x, y))) is 1:
            img_copied = Image.open(TMP_PATH + filename
                                    + "-%02d-%02d-%03d-%03d.png" % (frame, k, x, y))
        else:
            # Change alpha channel of the image
            for i in range(x):
                for j in range(y):
                    pix = img.getpixel((i, j))
                    img_copied.putpixel((i, j), (pix[0], pix[1], pix[2], int(pix[3] * k / frame)))
            img_copied.save(TMP_PATH + filename + "-%02d-%02d-%03d-%03d.png" % (frame, k, x, y))

        # duplicate same frame for 'frame_duplicate'
        tmp = ImageTk.PhotoImage(img_copied)
        for i in range(frame_duplicate):
            retlist.append(tmp)

    return retlist

# roundImage(): Make a rounded image.
def roundImage(filepath, radius=15, exp=3, resize=None):
    img = Image.open(filepath)

    if resize is not None:
        x, y = resize
    else:
        x, y = img.size

    # remove path and extension of filename
    filename = filepath[:-4]
    while '/' in filename:
        filename = filename[filename.index('/') + 1:]
    filepath_tmp = TMP_PATH + filename + "-exp-%02d-%02d-%03d-%03d.png" % (radius, exp, x, y)

    if len(glob(filepath_tmp)) is 1:
        img = Image.open(filepath_tmp)

    else:
        if resize is not None:
            img = img.resize(resize, Image.ANTIALIAS)

        # cut the picture with the line of graph (x ^ exp + y ^ exp = r ^ exp)
        for i in range(radius):
            for j in range(radius):
                if abs(i - radius) ** exp + abs(j - radius) ** exp > radius ** exp + 1:
                    pix = img.getpixel((i, j))
                    img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))

        for i in range(x-radius, x):
            for j in range(radius):
                if abs(i - x + radius) ** exp + abs(j - radius) ** exp > radius ** exp + 1:
                    pix = img.getpixel((i, j))
                    img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))

        for i in range(radius):
            for j in range(y-radius,y):
                if abs(i - radius) ** exp + abs(j - y + radius) ** exp > radius ** exp + 1:
                    pix = img.getpixel((i, j))
                    img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))

        for i in range(x-radius,x):
            for j in range(y-radius,y):
                if abs(i - x + radius) ** exp + abs(j - y + radius) ** exp > radius ** exp + 1:
                    pix = img.getpixel((i, j))
                    img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))

        img.save(filepath_tmp)

    return img


def drawPoints(canvas, dots, index, args):
    # back to drawView
    if len(dots) - 2 < index:
        TKROOT.after(0, drawView, 1, args[0], time(), args[1], args[2])

        if not args[0].empty():
            args[0].get()
        return

    x, y = dots[index]

                                                                    #    <Dot shape>
    canvas.create_line(x + 2, y + 0, x + 5, y + 0, fill='black')    #       ======
    canvas.create_line(x + 1, y + 1, x + 6, y + 1, fill='black')    #     ==========
    canvas.create_line(x + 0, y + 2, x + 7, y + 2, fill='black')    #   ==============
    canvas.create_line(x + 0, y + 3, x + 7, y + 3, fill='black')    #   ==============
    canvas.create_line(x + 0, y + 4, x + 7, y + 4, fill='black')    #   ==============
    canvas.create_line(x + 1, y + 5, x + 6, y + 5, fill='black')    #     ==========
    canvas.create_line(x + 2, y + 6, x + 5, y + 6, fill='black')    #       ======

    # taking a dot per 0.001 sec
    TKROOT.after(1, drawPoints, canvas, dots, index + 1, args)


def findMinMax(points):
    xMin, xMax, yMin, yMax = 999, -999, 999, -999

    for x, y in points:
        if xMin > x:
            xMin = x
        if xMax < x:
            xMax = x
        if yMin > y:
            yMin = y
        if yMax < y:
            yMax = y

    return xMin, xMax, yMin, yMax

# ================================================================================
# Data functions
# - These functions are intended to operate in accordance with the API.
# ================================================================================

def getCourseFilename(data):
    return data['user_course_info']['course_thumbnail'][30:-4]


def getCourseTitle(data):
    return data['user_course_info']['course_title']


def getTodayMission(data):
    return data['today_mission']['mission_order'], data['today_mission']['mission_title']


def getBadgeName(data):
    return data['user_info']['user_badge_url'][27:-4]


def getUserLevel(data):
    return data['user_info']['user_level']


def getUserName(data):
    return data['user_info']['user_name']


# ================================================================================
# Main-view
# ================================================================================

# initView(): The initial view.
def initView(phase, queue=None, objs=None):
    # objs:    [None, 0]
    # objs[0]: ANIGIF.add() index | GIFS['default_char']
    # objs[1]: int | a value for checking how much the user stimulate ultrasonic sensor.
    if objs is None:
        objs = [None] * 2
        objs[1] = 0

    if phase is INITIAL_PHASE:
        if queue is None:
            queue = Queue()
            p1 = Process(target=wandProcess, args=(queue, ))
            p2 = Process(target=buttonProcess, args=(queue, ))
            p3 = Process(target=ultrasonicProcess, args=(queue, ))
            p1.start()
            p2.start()
            p3.start()
        objs[0] = ANIGIF.add(GIFS['default_char'], (89, 89))

        TKROOT.after(1000, initView, 1, queue, objs)

    elif phase is 1:
        if not queue.empty():
            datatype, data = queue.get()

            if datatype == 'w' or datatype == 'b':
                if datatype == 'w':
                    wand_uid = data['wand_uid']
                else:
                    wand_uid = 1

                user_data_get = {'wand_uid': wand_uid,
                                 'process': None,
                                 'user_data': None}
                # goto main view
                TKROOT.after(0, main, FADEIN_PHASE, queue, None, time(), user_data_get, None)

                # turn off 'GIFS['defualt_char']' after going to main view.
                TKROOT.after(200, initView, DELAYED_PHASE, queue, objs)

            elif datatype == 'u':
                objs[1] += 1
                TKROOT.after(0, helloView, INITIAL_PHASE, None, objs[1] > 5)
                TKROOT.after(4000, initView, 1, queue, objs)

            else:
                TKROOT.after(250, initView, 1, queue, objs)

        else:
            TKROOT.after(250, initView, 1, queue, objs)

    elif phase is DELAYED_PHASE:
        ANIGIF.remove(objs[0])



def main(phase, queue=None, objs=None, execute_time=-1, user_data_get=None, ttsproc=None):

    # object remover for changing view to other view
    def object_remover(flag=True):
        data = user_data_get['user_data']
        # ANIGIF.add(GIFS['fadeout_blackboard'], (370, 215), cycle=1)
        # if data is not None:
        #     ANIGIF.add(GIFS['fadeout_' + getCourseFilename(data)], (450, 375), cycle=1)
        if flag:
            ANIGIF.remove(objs[0])
        ANIGIF.add(GIFS['close_papirus'], (450, 160), cycle=1)
        ANIGIF.removeImage(objs[1])
        ANIGIF.removeImage_ig(objs[2])
        ANIGIF.removeText_ig(objs[3])
        ANIGIF.removeText_ig(objs[4])
        ANIGIF.removeText_ig(objs[5])
        ANIGIF.removeText_ig(objs[6])
        ANIGIF.removeText_ig(objs[7])

    # view constructor for course information.
    def course_view_constructor(objs, data):
        font = Font(family='NanumBarunpen', size=12, weight='bold')
        font_title = Font(family='NanumBarunpen', size=14, weight='bold')
        mission_order, mission_title = getTodayMission(data)
        title = 'Lv.' + str(getUserLevel(data)) + " " + getUserName(data) + ' 법사님의 오늘 할 일'

        objs[2] = ANIGIF.addImage(IMAGES[getCourseFilename(data)], (600, 325))
        objs[3] = ANIGIF.addText(title, (675, 300), font=font)

        # construct text into the view according to the length of mission_title
        if len(mission_title) > 70:
            objs[4] = ANIGIF.addText(mission_order, (675, 425), font=font)
            objs[5] = ANIGIF.addText(mission_title[:30], (675, 450), font=font)
            objs[6] = ANIGIF.addText(mission_title[30:60], (675, 475), font=font)
            objs[7] = ANIGIF.addText(mission_title[60:], (675, 500), font=font)
        if len(mission_title) > 40:
            objs[4] = ANIGIF.addText(mission_order, (675, 450), font=font)
            objs[5] = ANIGIF.addText(mission_title[:30], (675, 475), font=font)
            objs[6] = ANIGIF.addText(mission_title[30:], (675, 500), font=font)
        else:
            objs[4] = ANIGIF.addText(mission_order, (675, 475), font=font)
            objs[5] = ANIGIF.addText(mission_title, (675, 500), font=font)


    # objs:    [None] * 8
    # objs[0]: ANIGIF.add() index | GIFS['specific_page']
    # objs[1]: ANIGIF.addImage() index | IMAGES['papirus']
    # objs[2]: ANIGIF.addImage() index | image of course
    # objs[3]: ANIGIF.addText() index | title of user information papirus
    # objs[4]: ANIGIF.addText() index | order of user mission
    # objs[5]: ANIGIF.addText() index | title of user mission
    # objs[6]: ANIGIF.addText() index | title of user mission (cont.)
    # objs[7]: ANIGIF.addText() index | title of user mission (cont.)
    if objs is None:
        objs = [None] * 8

    wand_uid = user_data_get['wand_uid']

    # if tts process is exit (finished executing), it should be joined (for less memory usage)
    if ttsproc is not None:
        if not ttsproc.is_alive():
            ttsproc.join()
            ttsproc = None

    # if staying time is more than 'MAIN_VIEW_EXECUTE_TIME', exit main view and go to initial view
    if time() - execute_time > MAIN_VIEW_EXECUTE_TIME:
        object_remover(False)
        TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                     initView, INITIAL_PHASE, queue, None)
        TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                     main, DELAYED_PHASE, queue, objs, time(), user_data_get)
        return


    if phase is FADEIN_PHASE:
        objs[0] = ANIGIF.add(GIFS['specific_page'], (89, 89))
        ANIGIF.add(GIFS['open_papirus'], (450, 160), cycle=1)
        TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['open_papirus']) + 100),
                     main, INITIAL_PHASE, queue, objs, time(), user_data_get)

    elif phase is INITIAL_PHASE:
        # if objects are not in current view
        if objs[1] is None:
            objs[1] = ANIGIF.addImage(IMAGES['papirus'], (450, 160))

        # if "userinfoProcess" is not active
        if user_data_get['process'] is None:
            user_data_get['process'] = Process(target=userinfoProcess, args=(queue, wand_uid))
            user_data_get['process'].start()
            TKROOT.after(100, main, INITIAL_PHASE, queue, objs, time(), user_data_get)

        # else if "user_data" is not vaild
        # it means that "userinfoProcess" did not give any information after initView->main
        elif user_data_get['user_data'] is None:
            empty_flag = True

            # checking queue; if "user_data" is given by "userinfoProcess", then goto next phase
            while not queue.empty():
                datatype, data = queue.get()
                if datatype == 'r':
                    empty_flag = False
                    user_data_get['process'].join()

                    if data['result_state'] is 1:
                        username = getUserName(data['result'])
                        # tts process start
                        ttsproc = Process(target=ttsProcess,
                                          args=("안녕하세요, " + username + "법사님!", username))
                        ttsproc.start()
                        course_view_constructor(objs, data['result'])
                        user_data_get['user_data'] = data['result']
                        TKROOT.after(100, main, 1, queue, objs, time(), user_data_get, ttsproc)

                    # if the "user_data" which is given by the process is not valid
                    else:
                        if VERBOSE:
                            print("SERVER CONNECTION HAS A PROBLEM... RE-POOL THE PROCESS.")

                        user_data_get['process'] = Process(target=userinfoProcess,
                                                           args=(queue, wand_uid))
                        user_data_get['process'].start()
                        TKROOT.after(100, main, INITIAL_PHASE, queue, objs, time(), user_data_get)

            # If "datatype == 'r'" was not matched in while loop,
            # then TKROOT.after() should be given.
            if empty_flag:
                TKROOT.after(100, main, INITIAL_PHASE, queue, objs, time(), user_data_get)

        # "user_data" is already valid.
        else:
            while not queue.empty():
                queue.get()

            course_view_constructor(objs, user_data_get['user_data'])
            TKROOT.after(1000, main, 1, queue, objs, time(), user_data_get, ttsproc)

    elif phase is 1:
        if not queue.empty():
            user_data = user_data_get['user_data']

            try:
                datatype, data = queue.get()
            except ValueError:
                print("UNEXPECTED DATA IS DETECTED")

            # WAND PROCESS
            if datatype == 'w':
                # if the gesture is 'star', go to badge view
                if data['gesture'] == 'star':
                    object_remover(False)
                    TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                                 badgeView, FADEIN_PHASE, user_data, time())
                    TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                                 main, DELAYED_PHASE, queue, objs, time(), user_data_get)
                    TKROOT.after(5000 + int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                                 main, FADEIN_PHASE, queue, None, time(), user_data_get, ttsproc)

                # else, go to draw view.
                else:
                    object_remover(False)
                    TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                                 drawView, INITIAL_PHASE, queue, time(),
                                 [user_data_get, ttsproc], None)
                    TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                                 main, DELAYED_PHASE, queue, objs, time(), user_data_get)

            # BUTTON PROCESS
            # button is just for the test
            elif datatype is 'b':
                object_remover(False)
                TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                             drawView, INITIAL_PHASE, queue, time(),
                             [user_data_get, ttsproc], None)
                TKROOT.after(int(1000 / MAIN_FRAME * len(GIFS['close_papirus']) + 100),
                             main, DELAYED_PHASE, queue, objs, time(), user_data_get)

            # ULTRASONIC PROCESS
            elif datatype is 'u':
                TKROOT.after(200, main, 1, queue, objs, execute_time, user_data_get, ttsproc)

            else:
                print("UNEXPECTED DATA IS DETECTED:", datatype, data)
                raise NotImplementedError

        else:
            TKROOT.after(200, main, 1, queue, objs, execute_time, user_data_get, ttsproc)

    elif phase is DELAYED_PHASE:
        ANIGIF.remove(objs[0])

    else:
        print("UNEXPECTED PHASE IS DETECTED:", phase)
        raise NotImplementedError


# ================================================================================
# Sub-views
# ================================================================================

def drawView(phase, queue, execute_time, mainargs, objs=None):

    # objs:    [None] * 2
    # objs[0]: Canvas for the drawing
    # objs[1]: ANIGIF.addImage() index | IMAGES['static_papirus']
    if objs is None:
        objs = [None] * 2

    if time() - execute_time > DRAW_VIEW_EXECUTE_TIME:
        objs[0].destroy()
        ANIGIF.removeImage(objs[1])
        TKROOT.after(0, main, FADEIN_PHASE, queue, None, time(), mainargs[0], mainargs[1])
        return

    canvas_size = (600, 450)
    draw_size = (560, 350)
    draw_margin = ((canvas_size[0] - draw_size[0]) // 2, canvas_size[1] - draw_size[1] - 70)
    draw_center = (canvas_size[0] // 2, canvas_size[1] // 2)
    point_gap = 3
    font = Font(family='NanumBarunpen', size=15, weight='bold')


    if phase is INITIAL_PHASE:
        objs[0] = tkinter.Canvas(TKROOT, bg="white",
                                 width=canvas_size[0], height=canvas_size[1],
                                 highlightthickness=0)
        objs[0].pack()
        objs[0].place(x=210, y=150)
        objs[1] = ANIGIF.addImage(IMAGES['static_papirus'], (89, 89), priority=False)
        objs[0].create_image(89 + 850 // 2 - 210, 89 + 592 // 2 - 150,
                             image=IMAGES['static_papirus'])

        if not queue.empty():
            queue.get()

        TKROOT.after(1000, drawView, 1, queue, time(), mainargs, objs)

    else:
        if not queue.empty():
            try:
                datatype, data = queue.get()
            except ValueError:
                print("UNEXPECTED DATA IS DETECTED")

            # drawing
            if datatype == 'w':
                points = data['points']

                if len(points) < 10:
                    TKROOT.after(100, drawView, 1, queue, time(), mainargs, objs)
                    return

                # wand points are not continuous sometimes (limitation of wand)
                # so, below code makes gathered data from point data
                points_gathered = []
                xtmp, ytmp = points[0]
                xmul, ymul = 0, 0
                for x, y in points:
                    if xtmp - x > 80:
                        xmul += 1
                    elif x - xtmp > 80:
                        xmul -= 1
                    if ytmp - y > 80:
                        ymul += 1
                    elif y - ytmp > 80:
                        ymul -= 1
                    points_gathered.append((x + xmul * 100, y + ymul * 100))
                    xtmp, ytmp = x, y

                # find minimum and maximum for scaling
                # and decide scale ratio of drawing
                xMin, xMax, yMin, yMax = findMinMax(points_gathered)

                if xMax - xMin < 15 or yMax - yMin < 15:
                    TKROOT.after(100, drawView, 1, queue, time(), mainargs, objs)
                    return

                try:
                    if (yMax - yMin) * draw_size[0] > (xMax - xMin) * draw_size[1]:
                        ratio = (draw_size[1]) / (yMax - yMin)
                    else:
                        ratio = (draw_size[0]) / (xMax - xMin)

                except ZeroDivisionError:
                    TKROOT.after(100, drawView, 1, queue, time(), mainargs, objs)
                    return

                # points scaling and connect all dots continuously
                points_gathered.reverse()
                xcenter, ycenter = (xMax + xMin) // 2, (yMax + yMin) // 2
                dots = []

                # previous point setting
                x, y = points_gathered[0]
                xprev = int(draw_center[0] + (x - xcenter) * ratio - 1)
                yprev = int(draw_center[1] + (ycenter - y) * ratio - 1)

                smooth_cnt = 0
                for x, y in points_gathered:
                    xdot = int(draw_center[0] + (x - xcenter) * ratio)
                    ydot = int(draw_center[1] + (ycenter - y) * ratio)

                    # add dot only if it is different with previous dot
                    if xdot != xprev or ydot != yprev:

                        # 'smooth_cnt': this value is for smoothing the draw.
                        #               if xdot is same xprev or ydot is same yprev,
                        #                  then do not point it.
                        #               if smooth_cnt is more than 'DRAW_VIEW_SMOOTH',
                        #                  then connect it.
                        if xdot == xprev:
                            smooth_cnt += 1
                        elif ydot == yprev:
                            smooth_cnt += 1
                        else:
                            smooth_cnt = 0

                        if smooth_cnt > DRAW_VIEW_SMOOTH or smooth_cnt == 0:
                            smooth_cnt = 0

                            if xdot != xprev:
                                slope = (ydot - yprev) / (xdot - xprev)
                            else:
                                slope = 9999 if ydot - yprev > 0 else -9999

                            if abs(slope) < 1:
                                if xdot > xprev:
                                    for i in range(1, xdot - xprev + 1, point_gap):
                                        dots.append((xprev + i + draw_margin[0],
                                                     yprev + int(i * slope) + draw_margin[1]))
                                else:
                                    for i in range(0, xprev - xdot, point_gap):
                                        dots.append((xdot + i + draw_margin[0],
                                                     ydot + int(i * slope) + draw_margin[1]))
                            else:
                                if ydot > yprev:
                                    for i in range(1, ydot - yprev + 1, point_gap):
                                        dots.append((xprev + int(i / slope) + draw_margin[0],
                                                     yprev + i + draw_margin[1]))
                                else:
                                    for i in range(0, yprev - ydot, point_gap):
                                        dots.append((xdot + int(i / slope) + draw_margin[0],
                                                     ydot + i + draw_margin[1]))

                            xprev, yprev = xdot, ydot

                # clean view
                objs[0].delete("all")
                objs[0].create_image(89 + 850 // 2 - 210, 89 + 592 // 2 - 150,
                                     image=IMAGES['static_papirus'])

                # represent gesture
                gesture = data['gesture']
                if gesture is None:
                    objs[0].create_text(draw_center[0], 30,
                                        font=font, text="This Gesture: None", fill='#000000')
                else:
                    objs[0].create_text(draw_center[0], 30,
                                        font=font, text="This Gesture: " + gesture, fill='#000000')

                TKROOT.after(0, drawPoints, objs[0], dots, 0, [queue, mainargs, objs])

            else:
                TKROOT.after(100, drawView, 1, queue, execute_time, mainargs, objs)

        else:
            TKROOT.after(100, drawView, 1, queue, execute_time, mainargs, objs)


def helloView(phase, musicproc=None, angry=False):
    if phase is INITIAL_PHASE:
        if angry:
            filename = 'seonggasyeo.m4a'
        else:
            files = ['annyeong.m4a', 'eogeurae.m4a', 'eoi.m4a', 'mwoya.m4a', 'sogimsu.m4a']
            filename = files[int(random() * 5)]
        musicproc = Process(target=musicProcess, args=(SOURCES_PATH + "sound/" + filename, ))
        musicproc.start()
        TKROOT.after(1500, helloView, 1, musicproc)

    elif phase is 1:
        ANIGIF.add(GIFS['active_char'], (89, 89), cycle=1)
        TKROOT.after(1000, helloView, DELAYED_PHASE, musicproc)

    elif phase is DELAYED_PHASE:
        if musicproc.is_alive():
            TKROOT.after(1000, helloView, DELAYED_PHASE, musicproc)
        else:
            musicproc.join()


def badgeView(phase, user_info, execute_time, objs=None):

    def object_remover():
        badge_pos = [(600, 140), (700, 260), (700, 410), (600, 530)]
        ANIGIF.add(GIFS['fadeout_' + getBadgeName(user_info)], (300, 250), cycle=1)
        for i in range(len(user_info['badge_info'])):
            badge_path = user_info['badge_info'][i]['badge_url'][29:-4]
            ANIGIF.add(GIFS['fadeout_' + badge_path], badge_pos[i], cycle=1)
        for i in range(4 - len(user_info['badge_info'])):
            ANIGIF.add(GIFS['fadeout_badge_frame'], badge_pos[3 - i], cycle=1)
        ANIGIF.removeImage(objs[0])
        ANIGIF.removeImage(objs[1])
        ANIGIF.removeImage(objs[2])
        ANIGIF.removeImage(objs[3])
        ANIGIF.removeImage(objs[4])
        ANIGIF.remove_ig(objs[5])
        ANIGIF.remove_ig(objs[6])
        ANIGIF.remove_ig(objs[7])


    # objs:    [None] * 8
    # objs[0]: ANIGIF.addImage() index | image of main badge
    # objs[1]: ANIGIF.addImage() index | image of small badge 1
    # objs[2]: ANIGIF.addImage() index | image of small badge 2
    # objs[3]: ANIGIF.addImage() index | image of small badge 3
    # objs[4]: ANIGIF.addImage() index | image of small badge 4
    # objs[5]: ANIGIF.add() index | gliter 1
    # objs[6]: ANIGIF.add() index | gliter 2
    # objs[7]: ANIGIF.add() index | gliter 3
    if objs is None:
        objs = [None] * 8

    badge_pos = [(600, 140), (700, 260), (700, 410), (600, 530)]

    if phase is FADEIN_PHASE:
        ANIGIF.add(GIFS['fadein_' + getBadgeName(user_info)], (300, 250), cycle=1)

        for i in range(len(user_info['badge_info'])):
            badge_path = user_info['badge_info'][i]['badge_url'][29:-4]
            ANIGIF.add(GIFS['fadein_' + badge_path], badge_pos[i], cycle=1)

        # if there are empty badge slots, then just add frame only
        for i in range(4 - len(user_info['badge_info'])):
            ANIGIF.add(GIFS['fadein_badge_frame'], badge_pos[3 - i], cycle=1)

        TKROOT.after(int(8 * 1000 / MAIN_FRAME + 100), badgeView,
                     INITIAL_PHASE, user_info, execute_time, objs)


    elif phase is INITIAL_PHASE:
        objs[0] = ANIGIF.addImage(IMAGES[getBadgeName(user_info)], (300, 250))

        for i in range(len(user_info['badge_info'])):
            badge_path = user_info['badge_info'][i]['badge_url'][29:-4]
            objs[i+1] = ANIGIF.addImage(IMAGES[badge_path], badge_pos[i])

        for i in range(4 - len(user_info['badge_info'])):
            objs[4-i] = ANIGIF.addImage(IMAGES['badge_frame'], badge_pos[3 - i])

        TKROOT.after(0, badgeView, 1, user_info, execute_time, objs)

    # glitering effect
    elif phase in [1, 2, 3]:
        objs[(phase + 2) % 3 + 5] = ANIGIF.add(GIFS['gliter' + str(phase % 3 + 1)],
                                               (260, 210), cycle=1)
        if time() - execute_time < BADGE_VIEW_EXECUTE_TIME:
            TKROOT.after(1001, badgeView, (phase) % 3 + 1 , user_info, execute_time, objs)
        else:
            TKROOT.after(0, badgeView, 4, user_info, execute_time, objs)

    else:
        object_remover()


# ================================================================================
# Child-Process
# ================================================================================

def wandProcess(queue):
    if VERBOSE:
        print("WAND PROCESS START")

    points=[]
    wand = WandController(verbose=False)

    while(True):
        data = wand.readSerial()

        if len(str(data)) > 4:
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))
        else:
            continue

        if data[0] is 0x02:                             # data[0] = 0x02: End
                                                        #         = 0x01: Start
            gesture = wand.getGesture(points)

            if VERBOSE:
                print("WAND DETECTED")

            queue.put(('w', {'gesture': gesture,
                             'points': points,
                             'wand_uid': data_enc['wand_uid']}))
            points = []


# CHILD PROCESS
def buttonProcess(queue):
    if VERBOSE:
        print("BUTTON PROCESS START")

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while True:
        if GPIO.input(16) == GPIO.HIGH:
            queue.put(('b', None))
            if VERBOSE:
                print("BUTTON DETECTED")
            sleep(1)
        sleep(0.1)


# CHILD PROCESS
def ultrasonicProcess(queue):
    if VERBOSE:
        print("ULTRASONIC PROCESS START")

    hc_trig = 11
    hc_echo = 12

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(hc_trig, GPIO.OUT)
    GPIO.setup(hc_echo, GPIO.IN)

    flag = 0

    while True:
        if flag is ULTRASONIC_DETECT_COUNT:
            queue.put(('u', None))
            if VERBOSE:
                print("ULTRASONIC DETECTED")
            sleep(3)
            flag = 0

        else:
            GPIO.output(hc_trig, True)
            sleep(0.00001)
            GPIO.output(hc_trig, False)

            echo = GPIO.input(hc_echo)

            if echo == 1:
                sleep(0.2)
                print("ERROR")
                continue

            while echo == 0:
                StartTime = time()
                echo = GPIO.input(hc_echo)

            while echo == 1:
                StopTime = time()
                echo = GPIO.input(hc_echo)

            TimeElapsed = StopTime - StartTime
            distance = (TimeElapsed * 34300) / 2

            if distance < ULTRASONIC_DETECT_DISTANCE:
                flag += 1

        sleep(0.2)


# CHILD PROCESS
def userinfoProcess(queue, wand_uid):
    if VERBOSE:
        print("USERINFO PROCESS START")

    try:
        import requests
        import json
        result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                              + "/api/Gateway/Wands/%02d/User" % (wand_uid))
    except requests.exceptions.ConnectionError:
        print("userinfoProcess: requests.get() got an exception...")
        queue.put(('r', {"result_state": 0}))
        exit(0)

    try:
        result = json.loads(result.text)
    except json.decoder.JSONDecodeError:
        print("userinfoProcess: Could not decode user information...")
        queue.put(('r', {"result_state": 0}))
        exit(0)

    if result['result_state'] is not 1:
        print("userinfoProcess: result_state is not True...")
        queue.put(('r', {"result_state": 0}))
        exit(0)

    queue.put(('r', result))

    if VERBOSE:
        print("USERINFO PROCESS COMPLETED")

    exit(0)


# CHILD PROCESS
def ttsProcess(text, filename):
    if VERBOSE:
        print("TTS PROCESS START")

    # if TTS-filename is not exist, then make tts file first.
    if len(glob(TMP_PATH + "TTS-" + filename + "*")) is not 1:
        tts = gTTS(text=text, lang='ko')
        tts.save(TMP_PATH + "TTS-" + filename + ".mp3")

    # play tts file with mplayer
    system("sudo mplayer -quiet -speed 1.05 "
           + TMP_PATH + "TTS-" + filename + ".mp3 > /dev/null 2> /dev/null")

    if VERBOSE:
        print("TTS PROCESS COMPLETED")

    exit(0)


# CHILD PROCESS
def musicProcess(filename):
    if VERBOSE:
        print("MUSIC PROCESS START")

    system("sudo mplayer -quiet -speed 0.95 " + filename + " > /dev/null 2> /dev/null")

    if VERBOSE:
        print("MUSIC PROCESS COMPLETED")

    exit(0)


# ================================================================================
# LOAD AND PLAY MAINLOOP
# ================================================================================

if __name__ == "__main__":

    if VERBOSE:
        print("LOADING FOR CLASSES...")

# IMAGES: Dictionary(PhotoImage())
#         A dictionary of PhotoImage classes.
    IMAGES['background'] = tkinter.PhotoImage(file=SOURCES_PATH + 'background_frame.png')
    IMAGES['papirus'] = ImageTk.PhotoImage(Image.open(SOURCES_PATH + 'papirus.png'))
    IMAGES['static_papirus'] = ImageTk.PhotoImage(Image.open(SOURCES_PATH + 'static_papirus.png'))

    for f in glob(BADGE_PATH + '*'):
        imgtmp = Image.open(f)
        if "level" in f:
            imgtmp = imgtmp.resize((250, 250), Image.ANTIALIAS)
        elif "gliter" not in f:
            imgtmp = imgtmp.resize((100, 100), Image.ANTIALIAS)
        IMAGES[f[len(BADGE_PATH):-4]] = ImageTk.PhotoImage(imgtmp)

    for f in glob(COURSE_PATH + '*'):
        imgtmp = roundImage(f, exp=3, radius = 15, resize=(320 // 2, 220 // 2))
        IMAGES[f[len(COURSE_PATH):-4]] = ImageTk.PhotoImage(imgtmp)


# GIFS: Dict(List(PhotoImage()))
#       A dictionary consists of lists of PhotoImage classes configured by function gif2list().
    GIFS['default_char'] = gif2list_v2(SOURCES_PATH + 'default_char.gif', effect='gliter',
                                       frame_skip=2, frame_duplicate=2)
    GIFS['active_char'] = gif2list_v2(SOURCES_PATH + 'active_char.gif', effect='gliter')
    GIFS['specific_page'] = gif2list_v2(SOURCES_PATH + 'specific_page.gif', effect='gliter',
                                        frame_skip=2, frame_duplicate=2)
    GIFS['open_papirus'] = gif2list_v2(SOURCES_PATH + 'open_papirus.gif')
    GIFS['close_papirus'] = gif2list_v2(SOURCES_PATH + 'close_papirus.gif')

    GIFS['gliter1'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter1.png', 16,
                               frame_duplicate=1, resize=(330, 330), effect='gliter')
    GIFS['gliter2'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter2.png', 16,
                               frame_duplicate=1, resize=(330, 330), effect='gliter')
    GIFS['gliter3'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter3.png', 16,
                               frame_duplicate=1, resize=(330, 330), effect='gliter')

    for f in glob(BADGE_PATH + '*'):
        filename = f[len(BADGE_PATH):-4]
        if "level" in f:
            GIFS['fadein_' + filename] = png2list(f, 8, resize=(250, 250))
            GIFS['fadeout_' + filename] = png2list(f, 8, effect='reverse', resize=(250, 250))
        elif "gliter" not in f:
            GIFS['fadein_' + filename] = png2list(f, 8, resize=(100, 100))
            GIFS['fadeout_' + filename] = png2list(f, 8, effect='reverse', resize=(100, 100))


# ANIGIF: Class AnimatedGifs()
#         A class for animating GIF file well.
    ANIGIF = AnimatedGifs(TKROOT, frame=MAIN_FRAME, background=IMAGES['background'])
    ANIGIF.start()

    if VERBOSE:
        print("DONE.")

    TKROOT.after(0, initView, INITIAL_PHASE)
    TKROOT.mainloop()

