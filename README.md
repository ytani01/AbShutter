AbShutter

# Hardware

* Raspberry Pi (Zero WH etc.)

* AB Shutter3

# Install

```bash
$ sudo apt install -y bluetooth libbluetooth-dev build-essential evtest
$ sudo pip3 install -U evdev
```

# pairing

```bash
$ sudo bluetoothctl
[...]# power on
[...]# scan on
[...]# connect FF:FF:C1:21:B3:FB
[...]# pair FF:FF:C1:21:B3:FB
[...]# trust FF:FF:C1:21:B3:FB
[...]# quit
```

(3) test

```bash
$ sudo evtest
:
... (KEY_ENTER) ...
... (KEY_VOLUMEUP) ...

[Ctrl]-C

$ python3
>>> import evdev
>>> aaa = evdev.list_devices()
>>> print(aaa)
['/dev/input/event0']
>>> bbb = evdev.InputDevice(aaa[0])
>>> print(bbb)
.....
>>> for ccc in bbb.read_loop():
...   if ccc.type == evdev.ecodes.EV_KEY:
...     print(evdev.util.categorize(ccc))
...

[Ctrl]-C
```
