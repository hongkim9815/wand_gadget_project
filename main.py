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
import glob
import requests
from tkinter.font import Font
from libraries.wand import WandController, data2point
from libraries.animatedgif import AnimatedGifs, gif2list
from multiprocessing import Process, Queue
from time import sleep
from datetime import datetime


SOURCES_PATH = "sources/"
TODAY_DATE = datetime.today().strftime("%y%m%d")

time_list = ['', '오늘오전', '오늘오후날씨', '내일오전', '내일오후']
LOCATE_CODE_DICT = {'Seoul': '001013',
                    'Bakryeong': '002001',
                    'Chuncheon': '003007',
                    'Cheongju': '005010',
                    'Gangneung': '004001',
                    'Daejeon': '006005',
                    'Gwangju': '011005',
                    'Busan': '008008',
                    'Jeonju': '010011',
                    'Ulleung': '009002',
                    'Jeju': '012005',
                    'Daegu': '007007'}

LOCATE_XY_DICT = {'Seoul': (160, 160),
                  'Bakryeong': (80, 220),
                  'Chuncheon': (220, 140),
                  'Cheongju': (220, 240),
                  'Gangneung': (300, 160),
                  'Daejeon': (150, 260),
                  'Gwangju': (160, 380),
                  'Busan': (350, 400),
                  'Jeonju': (220, 350),
                  'Ulleung': (450, 180),
                  'Jeju': (110, 580),
                  'Daegu': (310, 260)}

WEATHER_FILE_DICT = {'맑음': 'sun',
                     '구름조금': 'lightcloud',
                     '구름많음': 'partlycloud',
                     '흐림': 'cloud',
                     '비': 'rain',
                     '눈': 'snow',
                     '엷은 안개': 'fog',
                     '흐리고 비/눈': 'rain',
                     '흐리고 가끔 비/눈': 'lightrain',
                     '흐리고 가끔 눈': 'snow',
                     '구름많고 한때 비/눈': 'rain'}

#DEFINE IN IF-MAIN
HTMLs = None

# ================================================================================
# Utils
# ================================================================================

def getAllRequests():
    htmls = dict()
    for time_code in time_list:
        files = glob.glob("saved_" + TODAY_DATE + time_code + ".html")
        if len(files) is 0:
            temp = requests.get('https://search.naver.com/search.naver?query=전국'
                                + time_code + '날씨')
            temp.encoding = 'utf-8'
            temptext = temp.text
            htmls[time_code] = temptext
            f = open("saved_" + TODAY_DATE + time_code + ".html", 'w')
            f.write(temptext)
            f.close()
        else:
            f = open("saved_" + TODAY_DATE + time_code + ".html", 'r')
            htmls[time_code] = f.read()
            f.close()
    return htmls


def getWeather(htmls, time_code, locate_code):
    htmltext = htmls[time_code]
    class_name = 'ct' + locate_code
    wbox_index = htmltext.index('w_box '+ class_name)
    state_index = htmltext.index('>', wbox_index + len(class_name) + 8)
    state_index += 1
    state = htmltext[state_index : htmltext.index('</', state_index)]
    temperature = htmltext[htmltext.index('dsc', state_index) + 5
                           : htmltext.index('</a>', state_index) - 8]
    return state, temperature


# ================================================================================
# Main-process
# ================================================================================

def main(root, first, queue=None):
    if first:
        queue = Queue()
        p = Process(target=mainView, args=(queue, ))
        p.start()
        root.after(200, main, root, False, queue)
    elif not queue.empty():
        data = queue.get()
        print(data)
        if data is not None:
            weatherView(root, True)
        else:
            root.after(200, main, root, False, queue)
    else:
        root.after(200, main, root, False, queue)



# ================================================================================
# Sub-views
# ================================================================================

# CHILD PROCESS
def mainView(queue):
    print("SUB:    START")
    points=[]
    while(True):
        wand = WandController(verbose=True)
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


def weatherView(root, first, canvas=None):
    print("WEATHERVIEW")
    if first:
        canvas = tkinter.Canvas(root, bg='white', width=800, height=768)
        canvas.pack()
        canvas.place(x=0, y=0)

        south_korea = tkinter.PhotoImage(file=SOURCES_PATH + "weather/" + "south_korea.png")
        canvas.create_image(220, 330, image=south_korea)
        weather_icons = []
        weather_tems = []
        for loc, loccode in LOCATE_CODE_DICT.items():
            sta, tem = getWeather(HTMLs, time_list[1], loccode)
            try:
                tmp = tkinter.PhotoImage(file=SOURCES_PATH + "weather/" + WEATHER_FILE_DICT[sta] + '.png')
            except KeyError:
                tmp = tkinter.PhotoImage(file=SOURCES_PATH + "weather/" + 'nodata.png')
                print(sta)
            weather_icons.append(tmp)
            canvas.create_image(LOCATE_XY_DICT[loc][0], LOCATE_XY_DICT[loc][1],
                                image=weather_icons[-1])
            canvas.create_text(LOCATE_XY_DICT[loc][0]-1, LOCATE_XY_DICT[loc][1]+35,
                               text = tem + ' °C', font=boldfont)
        root.after(5000, weatherView, root, False, canvas)
    else:
        canvas.pack_forget()
        main(root, False, queue=None)


# ================================================================================
# MAIN
# ================================================================================

if __name__ == "__main__":
    print("LOADING...")
    HTMLs = getAllRequests()

    root = tkinter.Tk()
    root.geometry('1024x768')
    root['bg'] = 'white'

    gif1 = []
    gif2 = []

    gif1 = gif2list(SOURCES_PATH + 'gif2.gif')
    gif2 = gif2list(SOURCES_PATH + 'maingif1.gif')

    anigif = AnimatedGifs(root, frame=24)
    anigif.add(gif1, (200, 200))
    anigif.add(gif2, (400, 400))
    anigif.start()
    root.after(200, main, root, HTMLs, True)
    print("DONE")
    root.mainloop()

