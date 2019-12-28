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

x = []
y = []
points = []

def uint2int(x):
    return x if x < 128 else x - 256

def recognizerMotion(magicid, recognizer):
    global points,x,y
    recognizer = Dollar()
    points.reverse()
    if(len(points)<100):
        return

    text = recognizer.get_gesture(points)
    print(text)
    print(magicid)
    points = []
    x = []
    y = []

def printData(data):
    print("====================")
    print("DATA:    " + data.hex())
    print("Length:  " + str(len(str(data))))
    print("Start:   " + data[0:1].hex() + "(" + str(data[0]) +")")
    print("???:     " + data[1:2].hex() + "(" + str(data[1]) +")")
    print("Wand-id: " + data[2:3].hex() + data[3:4].hex() +
          "(" + str(int.from_bytes(data[2:4], byteorder='big')) +")")
    print("rest:    " + data[4:].hex())


while(True):
    s = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
    s.inter_byte_timeout = 0.05
    data = s.read(10000)
    # data = b"Kihong Working Now"
    if(len(str(data)) > 4 and data[0] == 0x01):         # data[0] = 0x01: Start to send
        printData(data)
    elif (len(str(data)) > 4 and data[0] == 0x02):      # data[0] = 0x02: End to send
        printData(data)
        recognizerMotion(magicid)

"""
        for i in range(4, len(data)-1,2):
            j += 1
            #print(j," : ","(",getSignedInt(data[i]),",",getSignedInt(data[i+1]),")")
            x.append(getSignedInt(data[i])+300)
            y.append(-1*getSignedInt(data[i+1])+300)
            point = (getSignedInt(data[i])+300,-1*getSignedInt(data[i+1])+300)
            #if(i%2==0):
            points.append(point)
        recognizerMotion(magicid)
    elif(len(data)>4):
        h = 0    
        print("length : " , len(data))
        print("type : " + str(data[0]))
        print("cds : " + str(data[1]))
        print("id : " + str(data[2]) + str(data[3]))
        magicid = str(data[2])+str(data[3])
        k = 4
        for i in range(4, len(data)-1,2):
            j += 1
            #print(j," : ","(",data[i],",",getSignedInt(data[i+1]),")")
            x.append(getSignedInt(data[i])+300)
            y.append(-1*getSignedInt(data[i+1])+300)
            point = (getSignedInt(data[i])+300,-1*getSignedInt(data[i+1])+300)
            #if(i%2==0):
            points.append(point)

        if(data[0]==2):
            recognizerMotion(magicid)
            #ser.close()
            #plt.close()
            #plt.xlim(50,350)
            #plt.ylim(50,350)

"""
