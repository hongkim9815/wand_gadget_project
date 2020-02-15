# Wand Gadget Project
This project is about an internship program at 'Jr Coding Lab' in 2019 Winter.
The project is making a gadget which is able to respond to electronic wand.

## Configuration
```
libraries                   python libraries
  /animatedgif.py           animated GIF library
  /dollar.py                1$ algorithm library for recognizing wand motion
  /templates.py             the geographical coordinate of each wand motion
  /wand.py                  wand controller library with class object
  /wandlib.py               wand controller library based on function (not revised)
  /weather.py               weather library with web crawler

sources/*                   image sources for the project

test                        testfiles to check some functions or features of Raspberry Pi
  /alpha.py                 a test for alpha channel of transparent png image file
  /api.py                   a test for API on our platform "magicoding.io"
  /autostart_led_blink.py   a test for autostart and led
  /button.py                a test for button
  /buzzer.py                a test for buzzer
  /gif_tk.py                a test for gif in Tkinter
  /interact_tk_wand.py      a test for interaction Tkinter and serial connection
  /multiprocessing_tk.py    a test for multiprocessing with Tkinter, wand, and requests module
  /thread_tk_wand.py        a test for thread-based programming
  /transparency_tk.py       a test for displaying transparent gif on Tkinter window
  /tts.py                   a test for Google TTS and audio player (mplayer)
  /ultrasonic.py            a test for distance sensor which is ultrasonic module HC-SR04
  /ultrasonic_advanced.py   a test for accuracy and compatibility of the distance sensor
  /weather_tk_hangeul.py    a test for displaying Hangeul on Tkinter window, and web crawler

main.py                     main python file of the gadget
requirements.txt            requirements file for pip. (generated by "pip freeze > requirements.txt")
setup.sh                    setup for manual installation
```

## Installation

### Manual installation

```
git clone https://github.com/hongkim9815/wand_gadget_project.git
cd wand_gadget_project && sudo ./setup.sh
```

### Requirements

This program is tested on python 3.7.3, but it might work well on python 3.7.\* or later.
Also, I strongly recommend utilizing this repository in Raspberry Pi 3 Model B+.

All required modules are in _requirements.txt_.
Although below code is in setup.sh, if you want to use it saperately, type this code in your command line:

```
pip3 install -r requirements.txt
```

### Electronic Circuit

<p align="center">
    <img src="../master/sources/report/circuit.png">
</p>


## Execution

All python main.py and testfiles are executable.
Both of below codes are available:

```
./<FILE>
```

```
python <FILE>
```

In this execution, make sure that the directory of bash is _wand\_gadget\_tool/test/_ or _wand\_gadget\_tool/_.
This is because of the python libraries directory.

For example:

```
cd wand_gadget_project/test && ./gif_tk.py
```
