# Wand Gadget Project
This project is about an internship program at 'Jr Coding Lab' in 2019 Winter.
The project is making a gadget which is able to respond to electronic wand.

## Configuration
```
libraries                   python libraries
  /dollar.py                1$ algorithm for recognizing wand motion
  /templates.py             the geographical coordinate of each wand motion
  
sources/*                   image sources for the project
  
test                        testfiles to check some functions or features of Raspberry Pi
  /autostart_led_blink.py   testfile for autostart and led
  /buzzer.py                testfile for buzzer
  /gif_tk.py                testfile for gif in Tkinter
  /interact_tk_wand.py      testfile for interaction Tkinter and serial connection
  /multiprocessing_tk.py    testfile for multiprocessing with Tkinter, wand, and requests module.
  /thread_tk_wand.py        testfile for thread-based programming
  /transparency_tk.py       testfile for displaying transparent gif on Tkinter window
  /weather_tk_hangeul.py    testfile for displaying hangeul on Tkinter window, and web crawler
  
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

This program is tested on python 3.7.3, but it might work well on python 3.7 or later.
Also, I strongly recommend utilizing this repository in Raspberry Pi 3+ Model B.

All required modules are in _requirements.txt_.
Although below code is in setup.sh, if you want to use it, type this code in your command line:

```
pip install -r requirements.txt
```


## Execution

All python testfiles and main.py is executable.
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
