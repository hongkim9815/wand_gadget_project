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
from tkinter import *


querylist = ['', '오늘오전', '오늘오후날씨', '내일오전', '내일오후']

db = []
for i in range(len(querylist)):
    html = requests.get('https://search.naver.com/search.naver?query=전국'
                        + querylist[i] + '날씨')
    html.encoding = 'utf-8'
    html = html.text
    daejeon_class_name = 'ct006005'
    daejeon_index = html.index('w_box '+ daejeon_class_name)
    state_index = html.index('>', daejeon_index + len(daejeon_class_name) + 8)
    state_index += 1
    daejeon_state = html[state_index : html.index('</', state_index)]
    daejeon_temperature = html[html.index('dsc', state_index) + 5
                               : html.index('</a>', state_index) - 8]
    db.append((daejeon_state, daejeon_temperature))

tkmain = Tk()
tkmain.geometry('480x720')
for i in range(len(querylist)):
    lbl = Label(tkmain, text=db[i][0] + ' / ' + db[i][1])
    lbl.grid(column=0, row=i)
lbl = Label(tkmain, text='asdf')
lbl.grid(column = 10, row=100)
tkmain.mainloop()
