#!/usr/bin/python3
"""
Title   main.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    21-Jan-2020 (cloned from test/interact_tk_wand.py)
Comment This program is a main file of the project.
        Required electric circuit is connecting on pin11 for LED, pin8 for TXD, and pin10 for RXD
        of NDmesh module (RF connection module), and pin16 for button.
Usage   INCOMPLETELY IMPLEMENTED
"""

import tkinter
from tkinter.font import Font
from PIL import Image, ImageTk
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list
from libraries.weather import weatherCanvas
import RPi.GPIO as GPIO
from multiprocessing import Process, Queue
from time import sleep, time
from glob import glob
from gtts import gTTS
from os import system


# ================================================================================
# INITIALIZE CONSTANTS AND VARIABLES
# ================================================================================

if __name__ == "__main__":

# CONSTANTS: Constants to define options and stable constants
    INITIAL_PHASE = 0
    VERBOSE = False


    if VERBOSE:
        print("INITIALIZING CONSTANTS AND VARIABLES...")


# PATH: Sources' path of the file directory.
    MAIN_PATH = ""
    SOURCES_PATH = MAIN_PATH + "sources/"
    TMP_PATH = MAIN_PATH + "tmp/"


# TKROOT: Tkinter Class Tk()
#         Root Class of Tkinter main window.
    TKROOT = tkinter.Tk()
    TKROOT.geometry('1024x768')
    TKROOT['bg'] = 'white'


    IMAGES = dict()
    GIFS = dict()


    if VERBOSE:
        print("DONE.")

# ================================================================================
# Utils
# ================================================================================

def png2list(filename, frame, frame_duplicate=1, resize=None):
    img = Image.open(filename)

    if resize is not None:
        img = img.resize(resize, Image.ANTIALIAS)

    retlist = []
    x, y = img.size
    img_copied = img.copy()

    for k in list(range(frame)) + list(range(frame, 0, -1)):
        if len(glob(TMP_PATH + filename[len(SOURCES_PATH + "badge/"):-4]
                    + "-%02d-%02d-%03d-%03d.png" % (frame, k, x, y))) is 1:
            img_copied = Image.open(TMP_PATH + filename[len(SOURCES_PATH + "badge/"):-4]
                                    + "-%02d-%02d-%03d-%03d.png" % (frame, k, x, y))

        else:
            for i in range(x):
                for j in range(y):
                    pix = img.getpixel((i, j))
                    img_copied.putpixel((i, j),
                                        (pix[0], pix[1], pix[2], int(pix[3] * k / frame)))
            img_copied.save(TMP_PATH + filename[len(SOURCES_PATH + "badge/"):-4]
                            + "-%02d-%02d-%03d-%03d.png" % (frame, k, x, y))

        for i in range(frame_duplicate):
            retlist.append(ImageTk.PhotoImage(img_copied))

    return retlist


def roundImage(img, radius=20, rounding=2, resize=None):
    r = rounding

    if resize is not None:
        img = img.resize(resize, Image.ANTIALIAS)
        x, y = resize
    else:
        x, y = img.size

    for i in range(radius):
        for j in range(radius):
            if abs(i - radius) ** r + abs(j - radius) ** r > radius ** r + 1:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    for i in range(x-radius, x):
        for j in range(radius):
            if abs(i - x + radius) ** r + abs(j - radius) ** r > radius ** r + 1:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    for i in range(radius):
        for j in range(y-radius,y):
            if abs(i - radius) ** r + abs(j - y + radius) ** r > radius ** r + 1:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))
    for i in range(x-radius,x):
        for j in range(y-radius,y):
            if abs(i - x + radius) ** r + abs(j - y + radius) ** r > radius ** r + 1:
                pix = img.getpixel((i, j))
                img.putpixel((i, j), (pix[0], pix[1], pix[2], 0))

    return ImageTk.PhotoImage(img)


def getCourseFilename(data):
    return data['user_course_info']['course_thumbnail'][30:-4]


def getCourseTitle(data):
    return data['user_course_info']['course_title']


def getTodayMission(data):
    return data['today_mission']['mission_order'], data['today_mission']['mission_title']


def getBadgeName(data):
    return data['user_info']['user_badge_url'][27:-4]


# ================================================================================
# Main-view
# ================================================================================

def initView(init, queue=None, objs=None):
    if objs is None:
        objs = [None]

    if init:
        if queue is None:
            queue = Queue()
            p1 = Process(target=wandProcess, args=(queue, ))
            p2 = Process(target=buttonProcess, args=(queue, ))
            p3 = Process(target=ultrasonicProcess, args=(queue, ))
            p1.start()
            p2.start()
            p3.start()
        objs[0] = ANIGIF.add(GIFS['working'], (120, 162), overlap=True)

        TKROOT.after(1000, initView, False, queue, objs)

    else:
        if not queue.empty():
            datatype, data = queue.get()
            if datatype == 'w':
                user_data_get = {'wand_uid': data['wand_uid'],
                                 'process': None,
                                 'user_data': None}
                ANIGIF.remove(objs[0])
                main(True, queue=queue, execute_time=time(), user_data_get=user_data_get)

            elif datatype == 'u':
                ANIGIF.remove(objs[0])
                helloView(INITIAL_PHASE)
                TKROOT.after(2000, initView, True, queue, objs)

            elif datatype == 'b':
                user_data_get = {'wand_uid': 1,
                                 'process': None,
                                 'user_data': None}
                ANIGIF.remove(objs[0])
                main(True, queue=queue, execute_time=time(), user_data_get=user_data_get)

            else:
                TKROOT.after(250, initView, False, queue, objs)

        else:
            TKROOT.after(250, initView, False, queue, objs)


def main(init, queue=None, objs=None, execute_time=-1, user_data_get=None, ttsproc=None):

    def object_remover():
        ANIGIF.remove(objs[0])
        ANIGIF.removeImage_ig(objs[1])
        ANIGIF.removeImage(objs[2])
        ANIGIF.remove_ig(objs[3])
        ANIGIF.removeImage_ig(objs[4])
        ANIGIF.removeText_ig(objs[5])
        ANIGIF.removeText_ig(objs[6])
        ANIGIF.removeText_ig(objs[7])
        ANIGIF.removeText_ig(objs[8])
        ANIGIF.removeText_ig(objs[9])


    def course_view_constructor(objs, data):
        objs[4] = ANIGIF.addImage(IMAGES[getCourseFilename(data)], (450, 375))
        objs[5] = ANIGIF.addText(getCourseTitle(data), (500, 350))
        mission_order, mission_title = getTodayMission(data)
        font = Font(family='NanumBarunpen', size=12, weight='bold')
        # UnPilgiBold
        objs[6] = ANIGIF.addText(mission_order, (775, 400), font=font)
        if len(mission_title) > 45:
            objs[7] = ANIGIF.addText(mission_title[:20], (775, 430), font=font)
            objs[8] = ANIGIF.addText(mission_title[20:40], (775, 460), font=font)
            objs[8] = ANIGIF.addText(mission_title[40:], (775, 490), font=font)
        if len(mission_title) > 25:
            objs[7] = ANIGIF.addText(mission_title[:20], (775, 430), font=font)
            objs[8] = ANIGIF.addText(mission_title[20:], (775, 460), font=font)
        else:
            objs[7] = ANIGIF.addText(mission_title, (775, 430), font=font)


    if objs is None:
        objs = [None] * 10

    if user_data_get is None:
        raise Exception
    else:
        wand_uid = user_data_get['wand_uid']

    if time() - execute_time > 10:
        TKROOT.after(0, initView, True, queue)
        object_remover()
        return

    if ttsproc is not None:
        if not ttsproc.is_alive():
            ttsproc.join()
            ttsproc = None


    # INITIATE PART
    # Get user data from "userinfoProcess" with "wand_uid"
    if init:

        # If objects are not in current view...
        if objs[0] is None and objs[1] is None and objs[2] is None:
            objs[0] = ANIGIF.add(GIFS['maingif1'], (0, 250), overlap=False)
            # objs[1] = ANIGIF.addImage(IMAGES['textbox_left'], (340, 120))
            objs[2] = ANIGIF.addImage(IMAGES['blackboard'], (370, 215))

        # If "userinfoProcess" is not active...
        if user_data_get['process'] is None:
            objs[3] = ANIGIF.add(GIFS['loading'], (600, 400))
            user_data_get['process'] = Process(target=userinfoProcess, args=(queue, wand_uid))
            user_data_get['process'].start()
            TKROOT.after(100, main, True, queue, objs, time(), user_data_get)

        # Else if "user_data" is not vaild...
        # It means that "userinfoProcess" did not give any information after initView->main.
        elif user_data_get['user_data'] is None:
            empty_flag = True

            # Checking queue, if "user_data" is given by "userinfoProcess", then goto next phase.
            while not queue.empty():
                datatype, data = queue.get()
                if datatype == 'r':
                    empty_flag = False
                    user_data_get['process'].join()

                    if data['result_state'] is 1:
                        ANIGIF.remove(objs[3])
                        course_view_constructor(objs, data['result'])

                        username = data['result']['user_info']['user_name']
                        ttsproc = Process(target=ttsProcess,
                                          args=("안녕, " + username
                                                + "! 코딩마법학교에 온걸 환영해!", ))
                        ttsproc.start()

                        user_data_get['user_data'] = data['result']
                        TKROOT.after(100, main, False, queue, objs, time(), user_data_get, ttsproc)
                    # If the "user_data" which is given by the process is not valid...
                    else:
                        if VERBOSE:
                            print("SERVER CONNECTION HAS A PROBLEM... RE-POOL THE PROCESS.")

                        user_data_get['process'] = Process(target=userinfoProcess,
                                                           args=(queue, wand_uid))
                        user_data_get['process'].start()
                        TKROOT.after(100, main, True, queue, objs, time(), user_data_get)

            # If "datatype == 'r'" was not matched in while loop,
            # then tkafter action should be given.
            if empty_flag:
                TKROOT.after(100, main, True, queue, objs, time(), user_data_get)

        # "user_data" is already valid.
        else:
            while not queue.empty():
                queue.get()

            course_view_constructor(objs, user_data_get['user_data'])
            TKROOT.after(100, main, False, queue, objs, time(), user_data_get, ttsproc)


    elif not queue.empty():
        user_data = user_data_get['user_data']

        try:
            datatype, data = queue.get()
        except ValueError:
            print("UNEXPECTED DATA IS DETECTED")

        # WAND PROCESS
        if datatype == 'w':
            if data['gesture'] == 'star':
                object_remover()
                badgeView(INITIAL_PHASE, user_data, time())
                TKROOT.after(5000, main, True, queue, None, time(), user_data_get, ttsproc)

            elif data['gesture'] == 'triangle':
                object_remover()
                weatherView(INITIAL_PHASE)
                TKROOT.after(2000, main, True, queue, None, time(), user_data_get, ttsproc)

            # Else, goto practice board.
            else:
                print("PRACTICE BOARD HAD NOT BEEN IMPLEMENTED YET...")
                TKROOT.after(200, main, False, queue, objs, time(), user_data_get, ttsproc)

        # BUTTON PROCESS
        elif datatype is 'b':
            object_remover()
            badgeView(INITIAL_PHASE, user_data, time())
            TKROOT.after(5000, main, True, queue, None, time(), user_data_get, ttsproc)

        # ULTRASONIC PROCESS
        elif datatype is 'u':
            TKROOT.after(200, main, False, queue, objs, execute_time, user_data_get, ttsproc)

        else:
            print("UNEXPECTED DATA IS DETECTED")
            raise NotImplementedError

    else:
        TKROOT.after(200, main, False, queue, objs, execute_time, user_data_get, ttsproc)


# ================================================================================
# Sub-views
# ================================================================================

def weatherView(phase, canvas=None, objs=None):
    if objs is None:
        objs = []

    if phase is INITIAL_PHASE:
        canvas, objs = weatherCanvas(TKROOT, (200, 200))
        TKROOT.after(3000, weatherView, False, canvas, objs)

    else:
        canvas.destroy()


def userinfoView(phase, objs=None):
    if objs is None:
        objs = []

    if phase is INITIAL_PHASE:
        objs.append(ANIGIF.add(GIFS['maingif2'], (0, 200), overlap = False))
        objs.append(ANIGIF.addImage(IMAGES['blackboard'], (400, 250)))
        TKROOT.after(2000, userinfoView, False, objs)

    else:
        ANIGIF.remove(objs[0])
        ANIGIF.removeImage(objs[1])


def helloView(phase, objs=None):
    if objs is None:
        objs = [None]

    if phase is INITIAL_PHASE:
        objs[0] = ANIGIF.add(GIFS['gif2'], (300, 300), overlap = False)
        TKROOT.after(2000, helloView, False, objs)

    else:
        ANIGIF.remove(objs[0])


def badgeView(phase, user_info, execute_time, objs=None):

    def object_remover():
        ANIGIF.removeImage(objs[0])
        ANIGIF.removeImage(objs[1])
        ANIGIF.removeImage(objs[2])
        ANIGIF.removeImage(objs[3])
        ANIGIF.removeImage(objs[4])
        ANIGIF.remove_ig(objs[5])
        ANIGIF.remove_ig(objs[6])
        ANIGIF.remove_ig(objs[7])


    if objs is None:
        objs = [None] * 8

    if phase is 0:
        badge_info = []
        badge_pos = [(600, 140), (700, 260), (700, 410), (600, 530)]

        objs[0] = ANIGIF.addImage(IMAGES[getBadgeName(user_info)], (300, 250))

        for i in range(len(user_info['badge_info'])):
            badge_path = user_info['badge_info'][i]['badge_url'][29:-4]
            objs[i+1] = ANIGIF.addImage(IMAGES[badge_path], badge_pos[i])

        for i in range(4 - len(user_info['badge_info'])):
            objs[4-i] = ANIGIF.addImage(IMAGES['badge_frame'], badge_pos[3 - i])

        TKROOT.after(0, badgeView, 1, user_info, execute_time, objs)

    elif phase in [1, 2, 3]:
        if objs[(phase + 1) % 3 + 5] is not -1 and False:
            ANIGIF.removeImage(objs[(phase + 1) % 3 + 5])
        objs[(phase + 2) % 3 + 5] = ANIGIF.add(GIFS['gliter' + str(phase % 3 + 1)],
                                               (260, 210), cycle=1)
        if time() - execute_time < 5:
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

        if (len(str(data)) > 4 and data[0] is 0x02):    # data[0] = 0x02: End to send
                                                        #         = 0x01: Start to send
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))
            gesture = wand.getGesture(points)
            if VERBOSE:
                print("WAND DETECTED")
            queue.put(('w', {'gesture': gesture,
                             'points': points,
                             'wand_uid': data_enc['wand_uid']}))
            points = []

        elif(len(str(data)) > 4):
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))


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
        if flag is 3:
            queue.put(('u', None))
            if VERBOSE:
                print("ULTRASONIC DETECTED")
            sleep(5)
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

            if distance < 10:
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
        print("requests: requests.get() got an exception...")
        queue.put(('r', {"result_state": 0}))
        exit(0)

    result = json.loads(result.text)

    if result['result_state'] is not 1:
        print("requests: requests.get() got an exception...")
        queue.put(('r', {result_state: 0}))
        exit(0)

    queue.put(('r', result))

    if VERBOSE:
        print("USERINFO PROCESS COMPLETED")

    exit(0)


# CHILD PROCESS
def ttsProcess(text):
    if VERBOSE:
        print("TTS PROCESS START")

    # The reason of adding "S" is that the initial volume of mplayer is too low...
    if len(glob(TMP_PATH + "TTS-" + text[:3] + "*")) is not 1:
        tts = gTTS(text="S" + text, lang='ko')
        tts.save(TMP_PATH + "TTS-" + text[:3] + ".mp3")
    system("mplayer -quiet -speed 1.05 "
           + TMP_PATH + "TTS-" + text[:3] + ".mp3 > /dev/null 2> /dev/null")

    if VERBOSE:
        print("TTS PROCESS COMPLETED")

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
    IMAGES['textbox_left'] = tkinter.PhotoImage(file=SOURCES_PATH + 'textbox-left.png')
    tmp = Image.open(SOURCES_PATH + 'blackboard.png').resize((int(480 * 7 / 6), int(343 * 7 / 6)),
                                                             Image.ANTIALIAS)
    IMAGES['blackboard'] = ImageTk.PhotoImage(tmp)

    for f in glob(SOURCES_PATH + "badge/*"):
        imgtmp = Image.open(f)
        if "level" in f:
            imgtmp = imgtmp.resize((250, 250), Image.ANTIALIAS)
        elif "gliter" not in f:
            imgtmp = imgtmp.resize((100, 100), Image.ANTIALIAS)
        IMAGES[f[len(SOURCES_PATH + "badge/"):-4]] = ImageTk.PhotoImage(imgtmp)

    for f in glob(SOURCES_PATH + "course/*"):
        imgtmp = Image.open(f)
        IMAGES[f[len(SOURCES_PATH + "course/"):-4]] = roundImage(imgtmp, rounding=3, radius = 15,
                                                                 resize=(320 * 4 // 6,
                                                                         220 * 4 // 6))

# GIFS: Dict(List(PhotoImage()))
#       A dictionary consists of lists of PhotoImage classes configured by function gif2list().
    # GIFS['cat'] = gif2list(SOURCES_PATH + 'cat.gif', 0, 20)
    # GIFS['main'] = gif2list(SOURCES_PATH + 'main.gif', 0, 20)
    GIFS['loading'] = gif2list(SOURCES_PATH + 'loading.gif')
    GIFS['maingif1'] = gif2list(SOURCES_PATH + 'maingif1.gif')
    GIFS['maingif2'] = gif2list(SOURCES_PATH + 'maingif2.gif')
    GIFS['gif2'] = gif2list(SOURCES_PATH + 'gif2.gif')
    GIFS['working'] = gif2list(SOURCES_PATH + 'working.gif')
    GIFS['gliter1'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter1.png', 16,
                               frame_duplicate=1, resize=(330, 330))
    GIFS['gliter2'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter2.png', 16,
                               frame_duplicate=1, resize=(330, 330))
    GIFS['gliter3'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter3.png', 16,
                               frame_duplicate=1, resize=(330, 330))


# ANIGIF: Class AnimatedGifs()
#         A class for animating GIF file well.
    ANIGIF = AnimatedGifs(TKROOT, frame=29.98, background=IMAGES['background'], grid=50)
    ANIGIF.start()


    if VERBOSE:
        print("DONE.")

    TKROOT.after(0, initView, True)
    TKROOT.mainloop()

