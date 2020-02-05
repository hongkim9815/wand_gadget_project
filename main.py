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
from PIL import Image, ImageTk
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list
from libraries.weather import weatherCanvas
import RPi.GPIO as GPIO
from multiprocessing import Process, Queue
from time import sleep, time
from glob import glob


# ================================================================================
# INITIALIZE CONSTANTS AND VARIABLES
# ================================================================================

if __name__ == "__main__":
    print("INITIALIZING CONSTANTS AND VARIABLES...")


# CONSTANTS: Constants to define options and stable constants
    INITIAL_PHASE = 0


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


    print("DONE.")

# ================================================================================
# Utils
# ================================================================================

def png2list(filename, frame, frame_duplicate=1, resize=None):
    img = Image.open(filename)

    if resize is not None:
        img = img.resize(resize)

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


# ================================================================================
# Main-view
# ================================================================================

def main(init, queue=None, objs=None):
    if objs is None:
        objs = []
    else:
        maingif = objs[0]
        textbox_left = objs[1]

    if init:
        if len(objs) is 0:
            objs.append(ANIGIF.add(GIFS['maingif1'], (0, 250), overlap=False))
            objs.append(ANIGIF.addImage(IMAGES['textbox_left'], (340, 120)))

        if queue is None:
            queue = Queue()
            p1 = Process(target=wandProcess, args=(queue, ))
            p2 = Process(target=buttonProcess, args=(queue, ))
            p3 = Process(target=ultrasonicProcess, args=(queue, ))
            p1.start()
            p2.start()
            p3.start()
        TKROOT.after(200, main, False, queue, objs)

    elif not queue.empty():
        try:
            datatype, data = queue.get()
        except ValueError:
            print("UNEXPECTED DATA IS DETECTED")

        if datatype == 'w':                                         # WAND MOTION
            if data is not None:
                if data[0]['color'] == 'yellow':
                    ANIGIF.remove(maingif)
                    ANIGIF.removeImage(textbox_left)
                    TKROOT.after(3000, main, True, queue, None)
                    badgeView(INITIAL_PHASE, 1)
                elif data[0]['color'] == 'red':
                    ANIGIF.remove(maingif)
                    ANIGIF.removeImage(textbox_left)
                    TKROOT.after(2000, main, True, queue, None)
                    # weatherView(True)
                    badgeView(INITIAL_PHASE, 1)
            else:
                print("There is no works assigned for that motion.")
                TKROOT.after(200, main, False, queue, objs)

        elif datatype is 'b':                                       # BUTTON
            ANIGIF.remove(maingif)
            ANIGIF.removeImage(textbox_left)
            # TKROOT.after(2000, main, True, queue, None)
            # userinfoView(INITIAL_PHASE)
            badgeView(INITIAL_PHASE, 1, (True, queue, None))

        elif datatype is 'u':                                       # ULTRASONIC DISTANCE SENSOR
            ANIGIF.remove(maingif)
            ANIGIF.removeImage(textbox_left)
            TKROOT.after(2000, main, True, queue, None)
            helloView(INITIAL_PHASE)

        else:
            print("UNEXPECTED DATA IS DETECTED")
            raise NotImplementedError

    else:
        TKROOT.after(200, main, False, queue, objs)


# ================================================================================
# Sub-views
# ================================================================================

def weatherView(phase, canvas=None, objs=None):
    if objs is None:
        objs = []

    if phase is INITIAL_PHASE:
        canvas, objs = weatherCanvas(TKROOT, (200, 200))
        objs.append(ANIGIF.add(GIFS['maingif1'], (0, 0), overlap = True))
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
        objs = []

    if phase is INITIAL_PHASE:
        objs.append(ANIGIF.add(GIFS['working'], (300, 300), overlap = True))
        TKROOT.after(2000, helloView, False, objs)

    else:
        ANIGIF.remove(objs[0])


def badgeView(phase, wand_uid, mainarg, pq=None, objs=None):
    if objs is None:
        objs = []

    if phase is 0:
        q = Queue()
        p = Process(target=userinfoProcess, args=(q, wand_uid))
        p.start()
        pq = (p, q)
        objs.append(ANIGIF.add(GIFS['loading'], (1024 // 2 - 40, 768 // 2 - 40), overlap = False))
        TKROOT.after(300, badgeView, 1, wand_uid, mainarg, pq, objs)

    elif phase is 1:
        if not pq[0].is_alive():
            ANIGIF.remove(objs[0])
            result = pq[1].get()['result']
            badge_info = []
            badge_pos = [(600, 140), (700, 260), (700, 410), (600, 530)]

            objs.append(ANIGIF.addImage(IMAGES[result['user_info']['user_badge_url'][27:-4]],
                                        (300, 250)))

            for i in range(3):
                objs.append(-1)

            for i in range(len(result['badge_info'])):
                rt = result['badge_info'][i]
                badge_path = rt['badge_url'][29:-4]
                objs.append(ANIGIF.addImage(IMAGES[badge_path], badge_pos[i]))

            TKROOT.after(0, badgeView, 2, wand_uid, mainarg, pq, objs)
            pq[0].join()

        else:
            TKROOT.after(300, badgeView, 1, wand_uid, mainarg, pq, objs)

    elif phase < 15:
        if objs[phase % 3 + 2] is not -1 and False:
            ANIGIF.removeImage(objs[phase % 3 + 2])
        objs[(phase + 1) % 3 + 2] = ANIGIF.add(GIFS['gliter' + str((phase + 1) % 3 + 1)],
                                               (300, 250), cycle=1)
        TKROOT.after(900, badgeView, phase + 1 , wand_uid, mainarg, pq, objs)

    else:
        ANIGIF.removeImage(objs[1])
        for i in objs[2:5]:
            if ANIGIF.isActive(i):
                ANIGIF.remove(i)
        for i in objs[5:]:
            ANIGIF.removeImage(i)
        TKROOT.after(0, main, mainarg[0], mainarg[1], mainarg[2])


# ================================================================================
# Child-Process
# ================================================================================

def wandProcess(queue):
    points=[]
    wand = WandController(verbose=False)

    while(True):
        data = wand.readSerial()

        if (len(str(data)) > 4 and data[0] is 0x02):    # data[0] = 0x02: End to send
                                                        #         = 0x01: Start to send
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))
            action = wand.getAction(data_enc['wand_uid'], points)
            if action is not None:
                queue.put(('w', action['marble']))
            points = []
        elif(len(str(data)) > 4):
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))


# CHILD PROCESS
def buttonProcess(queue):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while True:
        if GPIO.input(16) == GPIO.HIGH:
            queue.put(('b', None))
            sleep(1)
        sleep(0.1)


# CHILD PROCESS
def ultrasonicProcess(queue):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    hc_trig = 11
    hc_echo = 12
    GPIO.setup(hc_trig, GPIO.OUT)
    GPIO.setup(hc_echo, GPIO.IN)

    flag = 0

    while True:
        if flag is 3:
            queue.put(('u', None))
            sleep(10)
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


def userinfoProcess(queue, wand_uid):
    try:
        import requests
        import json
        result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                              + "/api/Gateway/Wands/%02d/User" % (wand_uid))
    except requests.exceptions.ConnectionError:
        print("requests: requests.get() got an exception...")
        queue.put({result_state: 0})
        return

    result = json.loads(result.text)

    if result['result_state'] is not 1:
        print("requests: requests.get() got an exception...")
        queue.put({result_state: 0})
        return

    queue.put(result)
    return


# ================================================================================
# LOAD AND PLAY MAINLOOP
# ================================================================================

if __name__ == "__main__":

    print("LOADING FOR CLASSES...")

# IMAGES: Dictionary(PhotoImage())
#         A dictionary of PhotoImage classes.
    IMAGES['background'] = tkinter.PhotoImage(file=SOURCES_PATH + 'background_frame.png')
    IMAGES['textbox_left'] = tkinter.PhotoImage(file=SOURCES_PATH + 'textbox-left.png')
    IMAGES['blackboard'] = tkinter.PhotoImage(file=SOURCES_PATH + 'blackboard.png')

    for f in glob(SOURCES_PATH + "badge/*"):
        imgtmp = Image.open(f)
        if "level" in f:
            imgtmp = imgtmp.resize((250, 250), Image.ANTIALIAS)
        elif "gliter" not in f:
            imgtmp = imgtmp.resize((100, 100), Image.ANTIALIAS)
        IMAGES[f[len(SOURCES_PATH + "badge/"):-4]] = ImageTk.PhotoImage(imgtmp)


# GIFS: Dict(List(PhotoImage()))
#       A dictionary consists of lists of PhotoImage classes configured by function gif2list().
    # GIFS['cat'] = gif2list(SOURCES_PATH + 'cat.gif', 0, 20)
    GIFS['main'] = gif2list(SOURCES_PATH + 'main.gif', 0, 20)
    GIFS['loading'] = gif2list(SOURCES_PATH + 'loading.gif')
    GIFS['maingif1'] = gif2list(SOURCES_PATH + 'maingif1.gif')
    GIFS['maingif2'] = gif2list(SOURCES_PATH + 'maingif2.gif')
    GIFS['working'] = gif2list(SOURCES_PATH + 'working.gif')
    GIFS['gliter1'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter1.png', 16,
                               frame_duplicate=1, resize=(250, 250))
    GIFS['gliter2'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter2.png', 16,
                               frame_duplicate=1, resize=(250, 250))
    GIFS['gliter3'] = png2list(SOURCES_PATH + 'badge/user_badge_gliter3.png', 16,
                               frame_duplicate=1, resize=(250, 250))


# ANIGIF: Class AnimatedGifs()
#         A class for animating GIF file well.
    ANIGIF = AnimatedGifs(TKROOT, frame=24, background=IMAGES['background'])
    ANIGIF.start()


    print("DONE.")

    TKROOT.after(0, main, True)
    TKROOT.mainloop()

