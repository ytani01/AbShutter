#!/usr/bin/env python3
#
# (C) 2019 Yoichi Tanibayashi
#
from Led import Led
from Switch import Switch, SwitchListener, SwitchEvent
from AbShutter import AbShutter

import RPi.GPIO as GPIO
import subprocess
import time

import click

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARN
logger = getLogger(__name__)
logger.setLevel(DEBUG)
console_handler = StreamHandler()
console_handler.setLevel(DEBUG)
handler_fmt = Formatter(
    '%(asctime)s %(levelname)s %(name)s.%(funcName)s()> %(message)s',
                        datefmt='%H:%M:%S')
console_handler.setFormatter(handler_fmt)
logger.addHandler(console_handler)
logger.propagate = False
def get_logger(name, debug=False):
    l = logger.getChild(name)
    if debug:
        l.setLevel(DEBUG)
    else:
        l.setLevel(INFO)

    return l

#####
class app:
    def __init__(self, devs, led_pin, sw_pin, debug=False):
        self.debug  = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('led_pin=%d, sw_pin=%d', led_pin, sw_pin)

        self.devs       = devs
        self.led_pin    = led_pin
        self.sw_pin     = sw_pin

        self.long_press = [
            {'timeout':0.7, 'blink':{'on':1,    'off':0}},	# multi click
            {'timeout':1,   'blink':{'on':0.2,  'off':0.04}},	# blink1
            {'timeout':3,   'blink':{'on':0.1,  'off':0.04}},	# blink2
            {'timeout':5,   'blink':{'on':0.02, 'off':0.04}},	# blink3
            {'timeout':7,   'blink':{'on':0,    'off':0}}]	# end

        self.timeout_sec = []
        for i in range(len(self.long_press)):
            self.timeout_sec.append(self.long_press[i]['timeout'])

        self.sw  = Switch(self.sw_pin, self.timeout_sec, debug=self.debug)
        self.sl  = SwitchListener ([self.sw], self.sw_cb_func,
                                   debug=self.debug)
        self.led = Led(self.led_pin)

        self.objs = []
        devlst = list(self.devs)
        while len(devlst) != 0:
            self.logger.info('devlst=%s', str(devlst))
            
            d = devlst.pop(0)
            try:
                o = AbShutter(d, self.ab_cb_func, debug=self.debug)
            except Exception as e:
                self.logger.error('%s', str(e))
                devlst.append(d)
                time.sleep(2)
                continue
                
            o.start()
            self.objs.append(o)
                
        self.logger.debug(str(self.objs))

        while True:
            self.logger.info('%s', time.strftime('%Y/%m/%d(%a) %H:%M:%S'))
            time.sleep(10)

    def ab_cb_func(self, dev, code, value):
        self.logger.debug('dev=%d, code=%d, value=%d', dev, code, value)
        key_name = AbShutter.keycode2str(code)
        val_str  = AbShutter.val2str(value)
        self.logger.info('/dev/input/event%d, %s:%s', dev, key_name, val_str)

        if val_str == 'PUSH':
            self.led.on()
        if val_str == 'RELEASE':
            self.led.off()

    def sw_cb_func(self, event):
        self.logger.info('pin:%d, %s[%d,%d]:%s', event.pin, 
                event.name, event.push_count, event.timeout_idx, 
                Switch.val2str(event.value))

        if event.name == 'pressed':
            self.led.on()
        if event.name == 'released':
            self.led.off()

#####
def setup_GPIO():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

def cleanup_GPIO():
    GPIO.cleanup()

#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('devs', metavar='[0|1..]...', type=int, nargs=-1)
@click.option('--led_pin', '--led', '-l', type=int, default=10, 
              help='LED pin')
@click.option('--switch_pin', '--sw_pin', '--sw', '-s', type=int, default=24,
              help='Switch pin')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(devs, led_pin, switch_pin, debug):
    logger.setLevel(INFO)
    if debug:
        logger.setLevel(DEBUG)

    logger.debug('devs:        %s', str(devs))
    logger.debug('led_pin:     %d', led_pin)
    logger.debug('switch_pin:  %d', switch_pin)

    setup_GPIO()
    try:
        app(devs, led_pin, switch_pin, debug).main()
    finally:
        cleanup_GPIO()

#####
if __name__ == '__main__':
    main()
