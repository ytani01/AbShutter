# AbShutter


## Hardware

* Raspberry Pi (Zero WH etc.)

* AB Shutter3


## Install

```bash
$ sudo apt install -y bluetooth libbluetooth-dev build-essential evtest

$ sudo apt install python3-pip
$ sudo python3 -m pip install -U pip
$ sudo hash -r 
$ sudo pip3 install -U evdev click
```


## Pairing

```bash
$ sudo bluetoothctl
[...]# power on
[...]# scan on
[...]# connect FF:FF:C1:21:B3:FB
[...]# pair FF:FF:C1:21:B3:FB
[...]# trust FF:FF:C1:21:B3:FB
[...]# quit
```


## Test

```bash
$ sudo evtest
:
... (KEY_ENTER) ...
... (KEY_VOLUMEUP) ...
[Ctrl]-C


$ ./test1.py
devs: ['/dev/input/event0']
input_dev device /dev/input/event0, name "AB Shutter3       ", phys "B8:27:EB:73:30:CC"
---
Push buttons.. ([Ctrl]-C to end)
event at 1555345539.513055, code 04, type 04, val 786665
event at 1555345539.513055, code 115, type 01, val 01
event at 1555345539.513055, code 00, type 00, val 00
event at 1555345539.625007, code 04, type 04, val 786665
event at 1555345539.625007, code 115, type 01, val 00
event at 1555345539.625007, code 00, type 00, val 00
event at 1555345540.749932, code 04, type 04, val 786665
event at 1555345540.749932, code 115, type 01, val 01
event at 1555345540.749932, code 00, type 00, val 00
event at 1555345540.899922, code 04, type 04, val 786665
event at 1555345540.899922, code 115, type 01, val 00
event at 1555345540.899922, code 00, type 00, val 00

:

[Ctrl]-C


$ ./AbShutter.py

:

[Ctrl]-C
