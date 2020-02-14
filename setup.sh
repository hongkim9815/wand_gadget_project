#!/bin/bash
chmod +x main.py
chmod -x libraries/*
chmod +x test/*
mkdir test/libraries
mkdir tmp
rm test/libraries/*
ln libraries/* test/libraries/
sudo apt-get install python3.7 -y
sudo apt-get install python3-pip -y
sudo apt-get install mplayer -y
sudo pip3 install -r requirements.txt
