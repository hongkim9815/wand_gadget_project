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
                main(True, queue=queue, last_execute_time=time(), user_data_get=user_data_get)

            elif datatype == 'u':
                ANIGIF.remove(objs[0])
                helloView(INITIAL_PHASE)
                TKROOT.after(2000, initView, True, queue, objs)

        else:
            TKROOT.after(500, initView, False, queue, objs)


def main(init, queue=None, objs=None, last_execute_time=-1, user_data_get=None):
    def object_remover():
        ANIGIF.remove(objs[0])
        ANIGIF.removeImage(objs[1])
        ANIGIF.removeImage(objs[2])
        ANIGIF.remove_ig(objs[3])
        ANIGIF.remove_ig(objs[4])

    if objs is None:
        objs = [None] * 8

    if user_data_get is None:
        raise Exception
    else:
        wand_uid = user_data_get['wand_uid']

    if time() - last_execute_time > 10:
        TKROOT.after(0, initView, True, queue)
        object_remover()
        return

    # INITIATE PART
    # Get user data from "userinfoProcess" with "wand_uid"
    if init:

        # If objects are not in current view...
        if objs[0] is None and objs[1] is None and objs[2] is None:
            objs[0] = ANIGIF.add(GIFS['maingif1'], (0, 250), overlap=False)
            objs[1] = ANIGIF.addImage(IMAGES['textbox_left'], (340, 120))
            objs[2] = ANIGIF.addImage(IMAGES['blackboard'], (390, 300))

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
                        user_data_get['user_data'] = data['result']
                        ANIGIF.remove(objs[3])
                        objs[4] = ANIGIF.add(GIFS['maingif2'], (400, 200))
                        TKROOT.after(100, main, False, queue, objs, time(), user_data_get)

                    # If the "user_data" which is given by the process is not valid...
                    else:
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

            TKROOT.after(100, main, False, queue, objs, time(), user_data_get)


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
                TKROOT.after(5000, main, True, queue, None, time(), user_data_get)

            elif data['gesture'] == 'triangle':
                object_remover()
                weatherView(INITIAL_PHASE)
                TKROOT.after(2000, main, True, queue, None, time(), user_data_get)

            # Else, goto practice board.
            else:
                print("PRACTICE BOARD HAD NOT BEEN IMPLEMENTED YET...")
                TKROOT.after(200, main, False, queue, objs, time(), user_data_get)

        # BUTTON PROCESS
        elif datatype is 'b':
            object_remover()
            badgeView(INITIAL_PHASE, user_data, time())
            TKROOT.after(5000, main, True, queue, None, time(), user_data_get)

        # ULTRASONIC PROCESS
        elif datatype is 'u':
            pass

        else:
            print("UNEXPECTED DATA IS DETECTED")
            raise NotImplementedError

    else:
        TKROOT.after(200, main, False, queue, objs, last_execute_time, user_data_get)


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
    if objs is None:
        objs = [None] * 8

    if phase is 0:
        badge_info = []
        badge_pos = [(600, 140), (700, 260), (700, 410), (600, 530)]

        objs[0] = ANIGIF.addImage(IMAGES[user_info['user_info']['user_badge_url'][27:-4]],
                                  (300, 250))

        for i in range(len(user_info['badge_info'])):
            rt = user_info['badge_info'][i]
            badge_path = rt['badge_url'][29:-4]
            objs[i+1] = ANIGIF.addImage(IMAGES[badge_path], badge_pos[i])

        TKROOT.after(0, badgeView, 1, user_info, execute_time, objs)

    elif phase in [1, 2, 3]:
        if objs[(phase + 1) % 3 + 5] is not -1 and False:
            ANIGIF.removeImage(objs[(phase + 1) % 3 + 5])
        objs[(phase + 2) % 3 + 5] = ANIGIF.add(GIFS['gliter' + str(phase % 3 + 1)],
                                               (300, 250), cycle=1)
        if time() - execute_time < 5:
            TKROOT.after(1001, badgeView, (phase) % 3 + 1 , user_info, execute_time, objs)
        else:
            TKROOT.after(0, badgeView, 4, user_info, execute_time, objs)
    else:
        for i in objs[:4]:
            if ANIGIF.isActiveImage(i):
                ANIGIF.removeImage(i)
        for i in objs[5:]:
            if ANIGIF.isActive(i):
                ANIGIF.remove(i)


# ================================================================================
# Child-Process
# ================================================================================

def wandProcess(queue):
    points=[]
    wand = WandController(verbose=False)
    print("WAND PROCESS START")

    while(True):
        data = wand.readSerial()

        if (len(str(data)) > 4 and data[0] is 0x02):    # data[0] = 0x02: End to send
                                                        #         = 0x01: Start to send
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))
            gesture = wand.getGesture(points)
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
    print("BUTTON PROCESS START")

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while True:
        if GPIO.input(16) == GPIO.HIGH:
            queue.put(('b', None))
            print("BUTTON DETECTED")
            sleep(1)
        sleep(0.1)


# CHILD PROCESS
def ultrasonicProcess(queue):
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
    try:
        import requests
        import json
        result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                              + "/api/Gateway/Wands/%02d/User" % (wand_uid))
    except requests.exceptions.ConnectionError:
        print("requests: requests.get() got an exception...")
        queue.put(('r', {result_state: 0}))
        exit(0)

    result = json.loads(result.text)

    if result['result_state'] is not 1:
        print("requests: requests.get() got an exception...")
        queue.put(('r', {result_state: 0}))
        exit(0)

    queue.put(('r', result))
    print("YES")
    exit(0)


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
    GIFS['gif2'] = gif2list(SOURCES_PATH + 'gif2.gif')
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

    TKROOT.after(0, initView, True)
    TKROOT.mainloop()

