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
    CMDLINE = { 'shutdown': ['sudo', 'shutdown', '-h', 'now'],
                'reboot':   ['sudo', 'shutdown', '-r', 'now'] }
    
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

        self.level = 0

        self.timeout_sec = []
        for i in range(len(self.long_press)):
            self.timeout_sec.append(self.long_press[i]['timeout'])

        self.sw  = Switch(self.sw_pin, self.timeout_sec, debug=self.debug)
        self.sl  = SwitchListener ([self.sw], self.cb_sw, debug=self.debug)
        self.led = Led(self.led_pin)

        self.led.blink(0.5, 0.5)

        self.objs = []
        devlst = list(self.devs)
        while len(devlst) != 0:
            self.logger.info('devlst=%s', str(devlst))
            
            d = devlst.pop(0)
            try:
                o = AbShutter(d, self.cb_ab, debug=self.debug)
            except Exception as e:
                self.logger.error('%s', str(e))
                devlst.append(d)
                time.sleep(2)
                continue
                
            o.start()
            self.objs.append(o)
                
        self.logger.debug(str(self.objs))

    def main(self):
        self.led.blink(0.05, 0.95)
        while True:
            self.logger.info('%s  level:%d',
                             time.strftime('%Y/%m/%d(%a) %H:%M:%S'),
                             self.level)
            time.sleep(10)

    def exec_cmd(self, cmd):
        self.logger.debug('CMDLINE[%s]: %s', cmd, str(self.CMDLINE[cmd]))
        subprocess.run(self.CMDLINE[cmd])

    def shutdown(self):
        self.logger.debug('')
        
        self.led.off()
        GPIO.setup(self.led_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.exec_cmd('shutdown')

    def reboot(self):
        self.logger.debug('')

        self.led.off()
        GPIO.setup(self.led_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.exec_cmd('reboot')
        

    # callback function for AB Shutter
    def cb_ab(self, dev, code, value):
        self.logger.debug('level=%d, dev=%d, code=%d, value=%d', 
                self.level, dev, code, value)
        key_name = AbShutter.keycode2str(code)
        val_str  = AbShutter.val2str(value)
        self.logger.info('/dev/input/event%d, %s:%s', dev, key_name, val_str)

        prev_level = self.level

        if val_str == 'PUSH':
            self.led.on()
            self.push_start_sec = time.time()
            self.level = 0
            return

        if val_str == 'RELEASE':
            if self.level == len(self.long_press) - 2:
                self.reboot()

            self.led.off()
            self.push_start_sec = 0
            self.level = 0
            return

        if val_str == 'HOLD':
            push_sec = time.time() - self.push_start_sec
            idx = 0
            for lp in self.long_press:
                if push_sec >= lp['timeout']:
                    self.level = idx
                    idx += 1
                    continue
                else:
                    break

            if self.level != prev_level:
                self.logger.debug('push_sec=%f, level=%d',
                                  push_sec, self.level)
                if self.level > 0 and self.level < len(self.long_press) - 1:
                    self.led.off()
                    self.led.blink(self.long_press[self.level]['blink']['on'],
                                   self.long_press[self.level]['blink']['off'])
                else:
                    self.led.off()

                if self.level >= len(self.long_press) - 1:
                    self.shutdown()
        
    # callback function for switch
    def cb_sw(self, event):
        self.logger.info('level=%d, pin:%d, %s[%d,%d]:%s',
                self.level,
                event.pin, 
                event.name, event.push_count, event.timeout_idx, 
                Switch.val2str(event.value))

        if event.name == 'pressed':
            self.led.on()
            return

        if event.name == 'released':
            if self.level == len(self.long_press) - 2:
                self.reboot()

            self.level = 0
            self.led.off()
            return

        if event.name == 'timer':
            self.level = event.timeout_idx
            if self.level > 0 and self.level < len(self.long_press) - 1:
                self.led.off()
                self.led.blink(self.long_press[self.level]['blink']['on'],
                               self.long_press[self.level]['blink']['off'])
            else:
                self.led.off()

            if self.level >= len(self.long_press) - 1:
                self.shutdown()
        

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
@click.option('--led_pin', '-l', type=int, default=5, 
              help='LED pin')
@click.option('--switch_pin', '-s', type=int, default=3,
              help='Switch pin')
@click.option('--switch_vcc', '-v', type=int, default=0,
              help='Switch pin')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(devs, led_pin, switch_pin, switch_vcc, debug):
    logger.setLevel(INFO)
    if debug:
        logger.setLevel(DEBUG)

    logger.debug('devs:        %s', str(devs))
    logger.debug('led_pin:     %d', led_pin)
    logger.debug('switch_pin:  %d', switch_pin)
    logger.debug('switch_vcc:  %d', switch_vcc)

    setup_GPIO()
    if switch_vcc != 0:
        GPIO.setup(switch_vcc, GPIO.OUT)
        GPIO.output(switch_vcc, GPIO.HIGH)
        
    try:
        app(devs, led_pin, switch_pin, debug).main()
    finally:
        cleanup_GPIO()

#####
if __name__ == '__main__':
    main()
