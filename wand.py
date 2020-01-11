#!/usr/bin/python3
"""
Title       wand.py
Author      Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made        28-Dec-2019
Comment     This program is a testfile for checking the connection between wand and Raspberry Pi.
            Required electric circuit is just connecting LED with pin6 (GND) and pin8 (GPIO14, TXD).
            Also, you need a wand for the test.
            Test process:
                1) Just execute this program.
                2) Swing wand and gather RF-Data.
                3) Check the read data whether the data is aligned well or not.
"""

import serial
import RPi.GPIO as GPIO
import time
import requests
import json
import time
from lib.dollar import Dollar

def uint2int(x):
    return x if x < 128 else x - 256

def recognizerMotion(magicid, x, y, points):
    recognizer = Dollar()
    points.reverse()
    if(len(points)<100):
        return

    text = recognizer.get_gesture(points)
    print(text)
    print(magicid)
    result = requests.get("http://ec2-15-165-111-76.ap-northeast-2.compute.amazonaws.com:80/api/Gateway/JSON/"+magicid)
    print(result)
    spell = json.loads(result.txt)['result']
    data = json.loads(spell)
    print(data)

    if data.get(text):
        action = data[text]
        print(action)
        for i in action['marble']:
            print(i['color'])

def data_encrypt(data):
    data_enc = {}
    data_enc['data_type'] = data[0]
    data_enc['UNKNOWN_1'] = data[1]
    data_enc['wand_uid'] = int.from_bytes(data[2:4], byteorder='big')
    return data_enc

def printData(data):
    print("====================")
    print("DATA:    " + data.hex())
    print("Length:  " + str(len(str(data))))
    print("Start:   " + data[0:1].hex() + "(" + str(data[0]) +")")
    print("???:     " + data[1:2].hex() + "(" + str(data[1]) +")")
    print("Wand-id: " + data[2:3].hex() + data[3:4].hex() +
          "(" + str(int.from_bytes(data[2:4], byteorder='big')) +")")
    print("rest:    " + data[4:].hex())


s = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
s.inter_byte_timeout = 0.05

x = []
y = []
points = []

while(True):
    data = s.read(10000)
    # data = b"Kihong Working Now"
    if (len(str(data)) > 0 and data[0] == 0x02):  # data[0] = 0x02: End to send
        printData(data)
        magicid = int.from_bytes(data[2:4], byteorder='big')
        for i in range(4, len(data) - 1, 2):
            x.append(uint2int(data[i]) + 300)
            y.append(-uint2int(data[i+1]) + 300)
            point = (uint2int(data[i]) + 300, -uint2int(data[i+1]) + 300)
            points.append(point)
        recognizerMotion(magicid, x, y, points)
        x = []
        y = []
        points = []
    elif(len(str(data)) > 4):                         # data[0] = 0x01: Start to send
        printData(data)

        magicid = int.from_bytes(data[2:4], byteorder='big')
        for i in range(4, len(data) - 1, 2):
            x.append(uint2int(data[i]) + 300)
            y.append(-uint2int(data[i+1]) + 300)
            point = (uint2int(data[i]) + 300, -uint2int(data[i+1]) + 300)
            points.append(point)

