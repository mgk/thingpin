import os
import time
import traceback
from .pin import *
import logging


class Thingpin(object):
    """
    Monitor GPIO pins and report to AWS IoT.

    Each GPIO pin is associated with an AWS IoT Thing. As the GPIO pin
    state changes the AWS IoT Thing state is published via MQTT. An example
    is a GPIO pin connected to a reed switch to detect whether a door is open
    or closed. This would be associated with an AWS IoT Thing named "door".

    Once started it does not return.
    """

    def __init__(self, notifier, pin_mode=None, things=None, debug=True):
        """
        Create and configure a Thingpin.

        Args:
            notifier (Notifier): Adafruit IO or AWS IoT notifier to publish
                messages to
            pin_mode (str): GPIO pin mode, 'BOARD' or 'BCM'
            things (dict of str: dict): each key is athing name
                and each value is the config for the Thing. For
                example:

                    {'door1' : {
                      'pin': 21,
                      'resistor': 'pull_up',
                      'iot_states': {
                        'HIGH': { 'state': 'open' },
                        'LOW': { 'state': 'closed'}
                      }
                    }}

            daemon (bool): if True run as a daemon and log to syslog, else
                run as a foreground process and log to stdout
            debug (bool): if True log debugging info
        """
        self.log = logging.getLogger('thingpin')
        self.notifier = notifier
        self.pin_mode = pin_mode
        self.thing_config = things
        self.debug = debug
        self.pins = {}

        self.initialized = False

    def initialize(self):
        """Initialize GPIO pins and connect to AWS IoT"""
        if not self.initialized:

            self.log.info('initializing')

            for k in ['pin_mode', 'thing_config', 'debug']:
                self.log.info('{} = {}'.format(k, getattr(self, k)))

            set_pin_mode(self.pin_mode)

            self.notifier.initialize()

            # Pins
            for name, config in self.thing_config.items():
                self.pins[name] = Pin(self.notifier, name, config)

            self.initialized = True
            self.log.info('initialize complete')

    def cleanup(self):
        """Release system resources and reset GPIO pins"""
        self.notifier.cleanup()
        pin_cleanup()

    def run(self):
        self.initialize()
        self.log.info('run')

        for pin in self.pins.values():
            pin.run()

        while True:
            time.sleep(1000)


class Pin(object):
    """Connect a GPIO pin to a notifier, interpreting pin state per config"""

    def __init__(self, notifier, name, config):
        """Setup an input pin"""
        self.name = name
        self.config = config
        setup_input_pin(config['pin'], config.get('resistor'))
        self.notifier = notifier
        self.watcher = Watcher(observer=self,
                               pin=config['pin'],
                               sleep=config.get('sleep', .010),
                               debounce_delay=config.get('debounce_delay'))

    def update_pin(self, pin, reading):
        self.notifier.notify(self.name, self.get_state(reading))

    def get_state(self, reading):
        """Get state to report for GPIO reading"""
        if reading == GPIO.HIGH:
            return self.config['iot_states']['HIGH']
        else:
            return self.config['iot_states']['LOW']

    def run(self):
        self.watcher.start()
