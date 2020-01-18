#!/usr/bin/python3
"""
Title       wandlib.py
Author      Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made        16-Jan-2020
Comment     This library python file is for controlling connection between wand and Raspberry Pi.
            Required electric circuit is connecting on pin8 for TXD, and pin9 for RXD of NDmesh
            module (RF connection module).
"""

import serial
import RPi.GPIO as GPIO
import time
import requests
import json
import time
import os
from libraries.dollar import Dollar

VERBOSE = False

def setVerbose(v):
    global VERBOSE
    if v in [True, False]:
        VERBOSE = v
    else:
        raise TypeError


def uint2int(x):
    return x if x < 128 else x - 256


def getAction(wand_uid, points):
    dollar = Dollar()
    points.reverse()

    if(len(points)<100):
        return

    gesture = dollar.get_gesture(points)
    print("Detected Gesture: " + gesture)
    print("SEND REQUEST")
    result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                          + "/api/Gateway/JSON/%02d" % (wand_uid))
    print("GOT REQUEST")
    print(result.text)
    spell = json.loads(result.text)['result']
    data = json.loads(spell)

    print("==================")
    if data.get(gesture):
        action = data[gesture]
    else:
        print("Motion is not defined for this gesture:", gesture)
        action = None
    print("==================")
    return action


def data_encoding(data):
    data_enc = {}
    data_enc['data_type'] = data[0]
    data_enc['CDS'] = data[1]
    data_enc['wand_uid'] = int.from_bytes(data[2:4], byteorder='big')
    data_enc['data_rest'] = data[4:]
    return data_enc


def print_data_enc(data):
    data_enc = data_encoding(data)
    if VERBOSE:
        print("====================")
        print("DATA:    " + data.hex())
        print("Length:  " + str(len(str(data))))
        print("Start:   " + data[0:1].hex() + "(" + str(data_enc['data_type']) +")")
        print("Cds:     " + data[1:2].hex() + "(" + str(data_enc['CDS']) +")")
        print("Wand-id: " + data[2:4].hex() + "(" + str(data_enc['wand_uid']) +")")
        print("rest:    " + data[4:].hex())
    return data_enc


def connect_new_serial():
    # TROUBLESHOOTING: "Error: serial device /dev/ttyAMA0 does not exist"
    #     If you update Raspbian OS, then this error can be occurred.
    #     - Open "/boot/config" with sudo privilege on any editor.      ("sudo vi /boot/config")
    #     - Change "enable_uart=0" to "enable_uart=1".
    #     - Reboot Raspbian OS.                                         ("sudo reboot")
    try:
        ser = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
    except serial.serialutil.SerialException:
        os.system('sudo chmod 777 /dev/ttyAMA0')
        time.sleep(0.01)
        ser = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
    return ser


def read_serial(ser=None):
    if ser is None:
        ser = connect_new_serial()
        ser.inter_byte_timeout = 1
    try:
        data = ser.read(100000)
    except serial.serialutil.SerialException:
        print("Serial:  Error Occurred... Wait a second to recover...")
        time.sleep(1)
        ser = connect_new_serial()
        ser.inter_byte_timeout = 1
        data = ser.read(100000)
    return ser, data


def data2point(data_rest):
    pts = []
    for i in range(0, len(data_rest) - 1, 2):
        pts.append((uint2int(data_rest[i]) + 300, -uint2int(data_rest[i+1]) + 300))
    return pts


if __name__ == "__main__":
    serial = None

    points = []
    while(True):
        serial, data = read_serial(serial)
        # data = b"Kihong Working Now"                              # example data

        if (len(str(data)) > 4 and data[0] is 0x02):                # data[0] = 0x02: End to send
                                                                    #         = 0x01: Start to send
            data_enc = print_data_enc(data)
            points.extend(data2point(data_enc['data_rest']))
            action = get_action(data['wand_uid'], points)
        elif(len(str(data)) > 4):
            data_enc = print_data_enc(data)
            for i in range(4, len(data) - 1, 2):
                points.append((uint2int(data[i]) + 300, -uint2int(data[i+1]) + 300))
        else:
            print("Serial does not detect any signal.")

