#!/usr/bin/env python3
# (C) Yoichi Tanibayashi

import evdev

devs = evdev.util.list_devices()
print('devs:', devs)

input_dev = evdev.device.InputDevice(devs[0])
print('input_dev:', input_dev)

print('Push buttons.. ([Ctrl]-C to end)')
for ev in input_dev.read_loop():
    print(ev)

