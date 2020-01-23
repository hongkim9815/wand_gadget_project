#!/usr/bin/python3
"""
Title   weather.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    23-Jan-2020
Comment This python library file is for crawling weather information from Naver search engine.
"""

import tkinter
import glob
import requests
from datetime import datetime
from tkinter.font import Font


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
                     '흐리고 가끔 비': 'lightrain',
                     '구름많고 한때 비/눈': 'rain'}


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


def weatherCanvas(root, place):
    objs = []
    HTMLs = getAllRequests()
    canvas = tkinter.Canvas(root, bg='white',
                            width=root.winfo_width() - place[0],
                            height=root.winfo_height() - place[1])
    canvas.pack()

    canvas.place(x=place[0], y=place[1])

    south_korea = tkinter.PhotoImage(file=SOURCES_PATH + "weather/" + "south_korea.png")
    canvas.create_image(220, 330, image=south_korea)
    boldfont = Font(family='Helvetica', size=12, weight='bold')
    objs.append(south_korea)

    for loc, loccode in LOCATE_CODE_DICT.items():
        sta, tem = getWeather(HTMLs, time_list[1], loccode)
        try:
            tmp = tkinter.PhotoImage(file=SOURCES_PATH + "weather/" + WEATHER_FILE_DICT[sta] + '.png')
        except KeyError:
            tmp = tkinter.PhotoImage(file=SOURCES_PATH + "weather/" + 'nodata.png')
            print(sta)
        canvas.create_image(LOCATE_XY_DICT[loc][0], LOCATE_XY_DICT[loc][1],
                            image=tmp)
        canvas.create_text(LOCATE_XY_DICT[loc][0]-1, LOCATE_XY_DICT[loc][1]+35,
                           text = tem + ' °C', font=boldfont)
        objs.append(tmp)

    return canvas, objs

