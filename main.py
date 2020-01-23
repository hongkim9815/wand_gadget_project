#!/usr/bin/python3
"""
Title   main.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    21-Jan-2020 (cloned from test/interact_tk_wand.py)
Comment This program is a main file of the project.
        Required electric circuit is connecting on pin11 for LED, pin8 for TXD, and pin10 for RXD
        of NDmesh module (RF connection module).
Usage   NOT IMPLEMENTED
"""

import tkinter
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list
from libraries.weather import weatherCanvas
from multiprocessing import Process, Queue
from time import sleep


SOURCES_PATH = "sources/"
print("LOADING...")
TKROOT = tkinter.Tk()
TKROOT.geometry('1024x768')
TKROOT['bg'] = 'white'

GIFS = dict()

GIFS['gif'] = gif2list(SOURCES_PATH + 'gif2.gif')
GIFS['character1'] = gif2list(SOURCES_PATH + 'maingif1.gif')

ANIGIF = AnimatedGifs(TKROOT, frame=24)

print("DONE.")


# ================================================================================
# Utils
# ================================================================================

# ================================================================================
# Main-process
# ================================================================================

def main(first, queue=None, maingif=None):
    if first:
        maingif = ANIGIF.add(GIFS['character1'], (100, 100))
        if queue is None:
            queue = Queue()
            p = Process(target=mainView, args=(queue, ))
            p.start()
        TKROOT.after(200, main, False, queue, maingif)
    elif not queue.empty():
        data = queue.get()
        print(data)
        if data is not None:
            if data['color'] == 'yellow':
                ANIGIF.delete(maingif)
                weatherView(True, queue)
                TKROOT.after(3000, main, True, queue, maingif)
            elif data['color'] == 'red':
                ANIGIF.delete(maingif)
                weatherView(True, queue)
                TKROOT.after(2000, main, True, queue, maingif)
        else:
            TKROOT.after(200, main, False, queue, maingif)
    else:
        TKROOT.after(200, main, False, queue, maingif)


# CHILD PROCESS
def mainView(queue):
    points=[]
    while(True):
        wand = WandController(verbose=False)
        data = wand.read_serial()

        if (len(str(data)) > 4 and data[0] is 0x02):    # data[0] = 0x02: End to send
                                                        #         = 0x01: Start to send
            data_enc = wand.print_data_enc(data)
            points.extend(data2point(data_enc['data_rest']))
            action = wand.getAction(data_enc['wand_uid'], points)
            if action is not None:
                queue.put(action['marble'])
            points = []
        elif(len(str(data)) > 4):
            data_enc = wand.print_data_enc(data)
            points.extend(data2point(data_enc['data_rest']))


# ================================================================================
# Sub-views
# ================================================================================

def weatherView(first, canvas=None, objs=[]):
    if first:
        canvas, objs = weatherCanvas(TKROOT, (100, 100))
        TKROOT.after(3000, weatherView, False, canvas, objs)
    else:
        canvas.destroy()


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    TKROOT.after(0, main, True)
    ANIGIF.start()
    TKROOT.mainloop()

