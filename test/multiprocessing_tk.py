#!/usr/bin/python3
"""
Title   multiprocessing_tk.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    21-Jan-2020
Comment This program is using python multiprocessing tool for my own study.
        If it works well, I expect that it is of great role to our project.
"""

import tkinter
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list
from multiprocessing import Process, Queue
from time import sleep


# ================================================================================
# Main-process
# ================================================================================
def main(first, queue=None):
    if first:
        queue = Queue()
        p = Process(target=process1, args=(queue, ))
        p.start()
    if queue.empty():
        # print("MAIN:   JOINED YET")
        root.after(200, main, False, queue)
    else:
        print("MAIN:   NEW ELEMENTS DETECTED...")
        print("MAIN:   DATA: ", queue.get())
        root.after(200, main, False, queue)


# ================================================================================
# Sub-process
# ================================================================================
def process1(queue):
    print("SUB:    START")
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
            else:
                queue.put(None)
            points = []
        elif(len(str(data)) > 4):
            data_enc = wand.print_data_enc(data)
            points.extend(data2point(data_enc['data_rest']))


# ================================================================================
# MAIN
# ================================================================================
if __name__ == "__main__":
    print("LOADING...")
    root = tkinter.Tk()
    root.geometry('1024x768')
    root['bg'] = 'white'

    sources_path = "../sources/"

    gif1 = []
    gif2 = []

    gif1 = gif2list(sources_path + 'gif2.gif')
    gif2 = gif2list(sources_path + 'maingif1.gif')

    anigif = AnimatedGifs(root, frame=60)
    anigif.add(gif1, (200, 200))
    anigif.add(gif2, (400, 400))
    anigif.start()
    root.after(200, main, True)
    print("DONE")
    root.mainloop()

