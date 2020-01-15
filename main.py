#!/usr/bin/python3
"""
Title       main.py
Author      Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made        28-Dec-2019
Comment     This program is a file for controlling connection between wand and Raspberry Pi.
            Required electric circuit is connecting on pin11, pin13, pin15, and pin19 for LED, pin8
            for TXD, and pin9 for RXD of NDmesh module (RF connection module).
            Usage:
                Copy this file into rc.local or systemd for autostart.
"""

import serial
import RPi.GPIO as GPIO
import time
import requests
import json
import time
import os
from libraries.dollar import Dollar


GPIO.setwarnings(False)                     # Ignore any warning
GPIO.setmode(GPIO.BOARD)                    # Use physical pin numbering system (40pin) on the board
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(19, GPIO.OUT, initial=GPIO.LOW)


def uint2int(x):
    return x if x < 128 else x - 256


def recognizerMotion(magicid, points):
    recognizer = Dollar()
    points.reverse()

    if(len(points)<100):
        return

    gesture = recognizer.get_gesture(points)
    print(gesture)
    print("SEND REQUEST")
    result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                          + "/api/Gateway/JSON/%02d" % (magicid))
    print("GOT REQUEST")
    print(result.text)
    spell = json.loads(result.text)['result']
    data = json.loads(spell)

    if data.get(gesture):
        print("==================")
        action = data[gesture]
        print(action)
        for i in action['marble']:
            color = i['color']
            delay = i['delay']
            if color == 'red':
                port = 11
            elif color == 'yellow':
                port = 13
            elif color == 'blue':
                port = 15
            else:
                port = 19
            GPIO.output(port, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(port, GPIO.LOW)
        print("==================")


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


def connect_new_serial():
    try:
        ser = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
    except serial.serialutil.SerialException:
        os.system('sudo chmod 777 /dev/ttyAMA0')
        time.sleep(1)
        ser = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
    return ser



if __name__ == "__main__":
    s = connect_new_serial()
    s.inter_byte_timeout = 0.05

    points = []
    while(True):
        try:
            data = s.read(10000)
        except serial.serialutil.SerialException:
            print("wait a second...")
            time.sleep(1)
            s = connect_new_serial()
            points = []

        # data = b"Kihong Working Now"                              # example data
        if (len(str(data)) > 4 and data[0] is 0x02):                # data[0] = 0x02: End to send
            printData(data)
            magicid = int.from_bytes(data[2:4], byteorder='big')
            for i in range(4, len(data) - 1, 2):
                point = (uint2int(data[i]) + 300, -uint2int(data[i+1]) + 300)
                points.append(point)
            recognizerMotion(magicid, points)
            points = []
        elif(len(str(data)) > 4):                                   # data[0] = 0x01: Start to send
            printData(data)
            magicid = int.from_bytes(data[2:4], byteorder='big')
            for i in range(4, len(data) - 1, 2):
                point = (uint2int(data[i]) + 300, -uint2int(data[i+1]) + 300)
                points.append(point)
