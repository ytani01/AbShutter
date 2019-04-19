#!/usr/bin/env python3
#
# (C) Yoichi Tanibayashi

# ToDo
# * callback function

import evdev
import os
import click

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARN
logger = getLogger(__name__)
logger.setLevel(DEBUG)
console_handler = StreamHandler()
console_handler.setLevel(DEBUG)
handler_fmt = Formatter('%(asctime)s %(levelname)s %(funcName)s> %(message)s',
                        datefmt='%H:%M:%S')
console_handler.setFormatter(handler_fmt)
logger.addHandler(console_handler)
logger.propagate = False
def get_logger(name, debug=False):
    l = logger.getChild(name)
    if debug:
        l.setLevel(DEBUG)
        l.setLevel(INFO)

    return l


#####
class AbShutter:
    EV_VAL = ('RELEASE', 'PUSH', 'HOLD')

    def __init__(self, dev=0, cb_func=None, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('dev=%d', dev)

        self.dev            = dev
        self.cb_func        = cb_func
        
        self.input_dev_file = '/dev/input/event' + str(self.dev)
        if not os.path.exists(self.input_dev_file):
            self.logger.error('no such device: %s', self.input_dev_file)
            raise Exception('no such device : %s' % self.input_dev_file)

        self.logger.debug('input_dev_file=%s', self.input_dev_file)

        self.input_dev      = evdev.device.InputDevice(self.input_dev_file)

    def wait_event1(self):
        logger.debug('')
        
        for ev in self.input_dev.read_loop():
            logger.debug(ev)
            if ev.type == evdev.events.EV_KEY:
                break
            
        logger.debug('%s', (ev.code, ev.value))
        if self.cb_func != None:
            self.cb_func(ev.code, ev.value)
        return (ev.code, ev.value)

    def loop(self):
        logger.debug('')

        while True:
            (code, value) = self.wait_event1()
            logger.debug('%s(%d) %s(%d)',
                        evdev.events.keys[code],code,
                        __class__.EV_VAL[value], value)
        
    
#####
def cb_func(code, value):
    print('code=%d:%s, value=%d:%s' % (code, evdev.events.keys[code],
                                       value, AbShutter.EV_VAL[value]))

#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('dev', metavar='[0|1|2|..]', type=int, default=0)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(dev, debug):
    logger.setLevel(INFO)
    if debug:
        logger.setLevel(DEBUG)

    logger.debug('dev=%d', dev)
    
    obj = AbShutter(dev, cb_func, debug=debug)
    obj.loop()

if __name__ == '__main__':
    main()
