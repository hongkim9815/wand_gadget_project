#!/usr/bin/python3
"""
Title       wand.py
Author      Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made        21-Jan-2020 (cloned from libraries/wandlib.py)
Comment     This library python file is for controlling connection between wand and Raspberry Pi.
            Required electric circuit is connecting on pin8 for TXD, and pin9 for RXD of NDmesh
            module (RF connection module).
            DIFF:   - classfying functions
"""

import serial
import RPi.GPIO as GPIO
import time
import requests
import json
import time
import os
from libraries.dollar import Dollar


def _uint2int(x):
    return x if x < 128 else x - 256


def _data_encoding(data):
    data_enc = {}
    data_enc['data_type'] = data[0]
    data_enc['CDS'] = data[1]
    data_enc['wand_uid'] = int.from_bytes(data[2:4], byteorder='big')
    data_enc['data_rest'] = data[4:]
    return data_enc


def data2point(data_rest):
    pts = []
    for i in range(0, len(data_rest) - 1, 2):
        pts.append((_uint2int(data_rest[i]) + 300, -_uint2int(data_rest[i+1]) + 300))
    return pts


class WandController:
    def __init__(self, verbose=False):
        self.serial = self._connectNewSerial()
        self._VERBOSE = verbose

    def _connectNewSerial(self):
        # TROUBLESHOOTING: "Error: serial device /dev/ttyAMA0 does not exist"
        #     If you update Raspbian OS, then this error can be occurred.
        #     - Open "/boot/config.txt" with privilege on any editor.   ("sudo vi /boot/config.txt")
        #     - Change "enable_uart=0" to "enable_uart=1".
        #     - Reboot Raspbian OS.                                     ("sudo reboot")
        try:
            ser = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
        except serial.serialutil.SerialException:
            os.system('sudo chmod 777 /dev/ttyAMA0')
            time.sleep(0.1)
            ser = serial.Serial("/dev/ttyAMA0", 115200, timeout = 0.1)
        return ser

    def readSerial(self):
        if self.serial is None:
            self.serial = self._connectNewSerial()
            self.serial.inter_byte_timeout = 0.05
        try:
            data = self.serial.read(10000)
        except serial.serialutil.SerialException:
            print("Serial: Error Occurred... Wait a second to recover...")
            self.serial = self._connectNewSerial()
            time.sleep(0.8)
            self.serial.inter_byte_timeout = 0.05
            data = self.serial.read(10000)
        return data

    def printDataEnc(self, data):
        data_enc = _data_encoding(data)
        if self._VERBOSE:
            print("Wand:   ==================== SERIAL ====================")
            print("Wand:   DATA:    " + data.hex())
            print("Wand:   Length:  " + str(len(str(data))))
            print("Wand:   Start:   " + data[0:1].hex() + "(" + str(data_enc['data_type']) +")")
            print("Wand:   Cds:     " + data[1:2].hex() + "(" + str(data_enc['CDS']) +")")
            print("Wand:   Wand-id: " + data[2:4].hex() + "(" + str(data_enc['wand_uid']) +")")
            print("Wand:   rest:    " + data[4:].hex())
            print("Wand:   ================================================")
        return data_enc

    def getGesture(self, points):
        dollar = Dollar()
        points.reverse()

        if(len(points) < 100):
            return None

        gesture = dollar.get_gesture(points)

        return gesture

    def getUserInfo(self, wand_uid):
        try:
            result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                                  + "/api/Gateway/wand/%02d" % (wand_uid))
        except requests.exceptions.ConnectionError:
            print("Wand:   requests.get() got an exception...")
            return None
        print(result)
        return result

    def getAction(self, wand_uid, points):
        dollar = Dollar()
        points.reverse()

        if(len(points)<100):
            return None

        gesture = dollar.get_gesture(points)
        if self._VERBOSE:
            print("Wand:   Detected Gesture: " + gesture)
            print("Wand:   SEND REQUEST")

        try:
            result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                                  + "/api/Gateway/JSON/%02d" % (wand_uid))
        except requests.exceptions.ConnectionError:
            print("Wand:   requests.get() got an exception...")
            return None

        if self._VERBOSE:
            print("Wand:   GOT REQUEST")

        spell = json.loads(result.text)['result']
        data = json.loads(spell)

        if self._VERBOSE:
            print("Wand:  ", data)

        if data.get(gesture):
            action = data[gesture]
        else:
            action = None
        print(action)
        return action

    def setVerbose(self, verbose):
        if verbose in [True, False]:
            self._VERBOSE = verbose
        else:
            raise TypeError


if __name__ == "__main__":
    points = []
    while(True):
        wand = WandController(verbose=True)
        data = wand.readSerial()

        if (len(str(data)) > 4 and data[0] is 0x02):                # data[0] = 0x02: End to send
                                                                    #         = 0x01: Start to send
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))
            action = wand.getAction(data_enc['wand_uid'], points)
            points = []
        elif(len(str(data)) > 4):
            data_enc = wand.printDataEnc(data)
            points.extend(data2point(data_enc['data_rest']))
        else:
            print("Serial: Serial does not detect any signal.")

