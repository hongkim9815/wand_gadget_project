#!/bin/bash
chmod -x libraries/*
chmod +x test/*
mkdir test/libraries
mkdir tmp
rm test/libraries/*
ln libraries/* test/libraries/
sudo apt-get install python3.7
sudo pip3 install -r requirements.txt
