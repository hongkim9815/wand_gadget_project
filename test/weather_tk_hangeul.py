#!/usr/bin/python3
#-*- coding: utf8 -*-
"""
Title   weather_tk_hangeul.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    27-Dec-2019
Comment This program is test for the internet, python Tkinter, and Hangeul on Raspberry Pi. For
        these purpose, it is going to do web-crawling. Thus, it might require the internet
        connection.
        Test process:
            Just execute this program.
"""
import requests
import glob
from tkinter import *
from tkinter.font import Font

sources_path = "../sources/weather/"
saved_path = "saved_200118"
time_list = ['', '오늘오전', '오늘오후날씨', '내일오전', '내일오후']
locate_code_dict = {'Seoul': '001013',
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

locate_xy_dict = {'Seoul': (160, 160),
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

weather_dict = {'맑음': 'sun',
                '구름조금': 'lightcloud',
                '구름많음': 'partlycloud',
                '흐림': 'cloud',
                '비': 'rain',
                '눈': 'snow',
                '엷은 안개': 'fog',
                '흐리고 비/눈': 'rain',
                '흐리고 가끔 비/눈': 'lightrain',
                '흐리고 가끔 눈': 'snow',
                '구름많고 한때 비/눈': 'rain'
                }


def get_all_requests():
    htmls = dict()
    for time_code in time_list:
        files = glob.glob(saved_path + time_code + ".html")
        if len(files) is 0:
            print("get_all_requests(): Reload new data...")
            temp = requests.get('https://search.naver.com/search.naver?query=전국'
                                + time_code + '날씨')
            temp.encoding = 'utf-8'
            temptext = temp.text
            htmls[time_code] = temptext
            f = open("saved_200118" + time_code + ".html", 'w')
            f.write(temptext)
            f.close()
        else:
            f = open(saved_path + time_code + ".html", 'r')
            htmls[time_code] = f.read()
            f.close()
    return htmls


def get_weather(htmls, time_code, locate_code):
    htmltext = htmls[time_code]
    class_name = 'ct' + locate_code
    wbox_index = htmltext.index('w_box '+ class_name)
    state_index = htmltext.index('>', wbox_index + len(class_name) + 8)
    state_index += 1
    state = htmltext[state_index : htmltext.index('</', state_index)]
    temperature = htmltext[htmltext.index('dsc', state_index) + 5
                           : htmltext.index('</a>', state_index) - 8]
    return state, temperature


if __name__ == "__main__":
    tkmain = Tk()
    tkmain.geometry('480x720')
    tkmain['bg'] = 'Gray'
    canvas = Canvas(tkmain, bg='white', width=480, height=650)
    canvas.pack()
    canvas.place(x=0, y=60)

    label = Label(tkmain, text="WEATHER OF " + time_list[1], font=("Helvetica", 30))
    label.pack()
    label.place(x=0, y=0)

    south_korea = PhotoImage(file=sources_path + "south_korea.png")
    canvas.create_image(220, 330, image=south_korea)

    boldfont = Font(family='Helvetica', size=12, weight='bold')

    htmls = get_all_requests()

    weather_icons = []
    weather_tems = []
    for loc, loccode in locate_code_dict.items():
        sta, tem = get_weather(htmls, time_list[1], loccode)
        try:
            tmp = PhotoImage(file=sources_path + weather_dict[sta] + '.png',)
        except KeyError:
            tmp = PhotoImage(file=sources_path + 'nodata.png')
            print(sta)
        weather_icons.append(tmp)
        canvas.create_image(locate_xy_dict[loc][0], locate_xy_dict[loc][1], image=weather_icons[-1])
        canvas.create_text(locate_xy_dict[loc][0]-1, locate_xy_dict[loc][1]+35,
                           text = tem + ' °C', font=boldfont)

    tkmain.mainloop()
