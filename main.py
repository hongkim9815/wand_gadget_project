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
from time import sleep


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


# GIFS: List(PhotoImage())
#       A list of PhotoImage classes. It is configured by function gif2list().
    GIFS = dict()
    GIFS['gif'] = gif2list(SOURCES_PATH + 'gif2.gif')
    GIFS['gif2'] = gif2list(SOURCES_PATH + 'maingif2.gif')
    GIFS['character1'] = gif2list(SOURCES_PATH + 'maingif1.gif')


# ANIGIF: Class AnimatedGifs()
#         A class for animating GIF file well.
    ANIGIF = AnimatedGifs(TKROOT, frame=24)

    print("DONE.")


# ================================================================================
# Utils
# ================================================================================


# ================================================================================
# Main-view
# ================================================================================

def main(first, queue=None, maingif=None):
    if first:
        if maingif is None:
            maingif = ANIGIF.add(GIFS['character1'], (100, 100))
        if queue is None:
            queue = Queue()
            p1 = Process(target=wandProcess, args=(queue, ))
            p1.start()
            p2 = Process(target=buttonProcess, args=(queue, ))
            p2.start()
        TKROOT.after(200, main, False, queue, maingif)

    elif not queue.empty():
        try:
            datatype, data = queue.get()
        except ValueError:
            print("UNEXPECTED DATA IS DETECTED")

        if datatype == 'w':
            if data is not None:
                if data['color'] == 'yellow':
                    ANIGIF.remove(maingif)
                    TKROOT.after(3000, main, True, queue, None)
                    weatherView(True)
                elif data['color'] == 'red':
                    ANIGIF.remove(maingif)
                    TKROOT.after(2000, main, True, queue, None)
                    weatherView(True)
            else:
                print("There is no works assigned for that motion.")
                TKROOT.after(200, main, False, queue, maingif)

        elif datatype is 'd':
            ANIGIF.remove(maingif)
            TKROOT.after(2000, main, True, queue, None)
            helloView(True)

        else:
            print("UNEXPECTED DATA IS DETECTED")

    else:
        TKROOT.after(200, main, False, queue, maingif)


# CHILD PROCESS
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
            queue.put(('d', None))
            sleep(3)
        sleep(0.1)



# ================================================================================
# Sub-views
# ================================================================================

def weatherView(first, canvas=None, objs=[]):
    if first:
        canvas, objs = weatherCanvas(TKROOT, (100, 100))
        TKROOT.after(3000, weatherView, False, canvas, objs)

    else:
        canvas.destroy()

def helloView(first, objs=None):
    if first:
        objs = ANIGIF.add(GIFS['gif2'], (200, 200))
        TKROOT.after(2000, helloView, False, objs)

    else:
        ANIGIF.remove(objs)

# ================================================================================
# MAINLOOP
# ================================================================================

if __name__ == "__main__":
    TKROOT.after(0, main, True)
    ANIGIF.start()
    TKROOT.mainloop()

