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
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list
from libraries.weather import weatherCanvas
import RPi.GPIO as GPIO
from multiprocessing import Process, Queue
from time import sleep, time


# ================================================================================
# INITIALIZE
# ================================================================================

if __name__ == "__main__":
    print("LOADING...")


# SOURCES_PATH: Sources' path of the file directory.
#               It should represent what directory should we execute this.
    MAIN_PATH = ""
    SOURCES_PATH = MAIN_PATH + "sources/"


# TKROOT: Tkinter Class Tk()
#         Root Class of Tkinter main window.
    TKROOT = tkinter.Tk()
    TKROOT.geometry('1024x768')
    TKROOT['bg'] = 'white'


# GIFS: Dict(List(PhotoImage()))
#       A dictionary consists of lists of PhotoImage classes configured by function gif2list().
    GIFS = dict()
    GIFS['cat'] = gif2list(SOURCES_PATH + 'cat.gif', 0, 20)
    GIFS['main'] = gif2list(SOURCES_PATH + 'main.gif', 0, 20)
    GIFS['maingif1'] = gif2list(SOURCES_PATH + 'maingif1.gif')
    GIFS['maingif2'] = gif2list(SOURCES_PATH + 'maingif2.gif')
    GIFS['working'] = gif2list(SOURCES_PATH + 'working.gif')


# IMAGES: Dictionary(PhotoImage())
#         A dictionary of PhotoImage classes.
    IMAGES = dict()
    IMAGES['background'] = tkinter.PhotoImage(file=SOURCES_PATH + 'background_frame.png')
    IMAGES['textbox_left'] = tkinter.PhotoImage(file=SOURCES_PATH + 'textbox-left.png')
    IMAGES['blackboard'] = tkinter.PhotoImage(file=SOURCES_PATH + 'blackboard.png')


# ANIGIF: Class AnimatedGifs()
#         A class for animating GIF file well.
    ANIGIF = AnimatedGifs(TKROOT, frame=24, background=IMAGES['background'])

    print("DONE.")


# ================================================================================
# Utils
# ================================================================================

# EMPTY


# ================================================================================
# Main-view
# ================================================================================

def main(first, queue=None, maingif=None):
    if first:
        if maingif is None:
            maingif = ANIGIF.add(GIFS['maingif1'], (0, 250), overlap=False)
            textbox_left = ANIGIF.addImage(IMAGES['textbox_left'], (340, 120))
        if queue is None:
            queue = Queue()
            p1 = Process(target=wandProcess, args=(queue, ))
            p2 = Process(target=buttonProcess, args=(queue, ))
            p3 = Process(target=ultrasonicProcess, args=(queue, ))
            p1.start()
            p2.start()
            p3.start()
        TKROOT.after(200, main, False, queue, maingif)

    elif not queue.empty():
        try:
            datatype, data = queue.get()
        except ValueError:
            print("UNEXPECTED DATA IS DETECTED")

        if datatype == 'w':
            if data is not None:
                if data[0]['color'] == 'yellow':
                    ANIGIF.remove(maingif)
                    TKROOT.after(3000, main, True, queue, None)
                    weatherView(True)
                elif data[0]['color'] == 'red':
                    ANIGIF.remove(maingif)
                    TKROOT.after(2000, main, True, queue, None)
                    weatherView(True)
            else:
                print("There is no works assigned for that motion.")
                TKROOT.after(200, main, False, queue, maingif)

        elif datatype is 'b':
            ANIGIF.remove(maingif)
            TKROOT.after(2000, main, True, queue, None)
            userinfoView(True)

        elif datatype is 'u':
            ANIGIF.remove(maingif)
            TKROOT.after(2000, main, True, queue, None)
            helloView(True)

        else:
            print("UNEXPECTED DATA IS DETECTED")
            raise NotImplementedError

    else:
        TKROOT.after(200, main, False, queue, maingif)


# ================================================================================
# Sub-views
# ================================================================================

def weatherView(first, canvas=None, objs=None):
    if objs is None:
        objs = []
    if first:
        canvas, objs = weatherCanvas(TKROOT, (200, 200))
        objs.append(ANIGIF.add(GIFS['maingif1'], (0, 0), overlap = True))
        TKROOT.after(3000, weatherView, False, canvas, objs)
    else:
        canvas.destroy()


def userinfoView(first, objs=None):
    if objs is None:
        objs = []
    if first:
        objs.append(ANIGIF.add(GIFS['maingif2'], (0, 200), overlap = False))
        objs.append(ANIGIF.addImage(IMAGES['blackboard'], (400, 250)))
        TKROOT.after(2000, userinfoView, False, objs)

    else:
        ANIGIF.remove(objs[0])
        ANIGIF.removeImage(objs[1])


def helloView(first, objs=None):
    if first:
        objs = ANIGIF.add(GIFS['working'], (300, 300), overlap = True)
        TKROOT.after(2000, helloView, False, objs)

    else:
        ANIGIF.remove(objs)


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


# ================================================================================
# MAINLOOP
# ================================================================================

if __name__ == "__main__":
    TKROOT.after(0, main, True)
    ANIGIF.start()
    TKROOT.mainloop()

