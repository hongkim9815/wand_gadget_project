#!/usr/bin/python3
#-*- coding: utf8 -*-
"""
Title   tts.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    07-Feb-2020
Comment This program is test for Google TTS and audio specification of Raspberry Pi.
        Known problem:
            In the case of the first part of a mp3 file, the volume is too low.
"""

from gtts import gTTS
import time
import os


MAIN_PATH = "../"
SOURCES_PATH = MAIN_PATH + "sources/"

student_name = "선생님"
text = "S" + student_name + "안녕! 코딩마법학교에 온걸 환영해!"

print(0, time.time())
tts = gTTS(text=text, lang='ko')
print(1, time.time())
tts.save(SOURCES_PATH + "asdf.mp3")
print(2, time.time())
os.system("mplayer -speed 1.05 " + SOURCES_PATH + "asdf.mp3")
print(3, time.time())
