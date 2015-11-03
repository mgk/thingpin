import os
import time
import traceback
from threading import Lock
from thingamon import Client, Thing
from RPi import GPIO


class Pin(object):
    def __init__(self, context, pin, resistor=None):
        self.context = context
        self.pin = pin
        self.resistor = resistor

        self._reading_lock = Lock()
        self._curr_reading = None
        self._reading_time = 0

        if self.resistor is not None:
            if self.resistor == 'pull_up':
                self.resistor = GPIO.PUD_UP
            elif self.resistor == 'pull_down':
                self.resistor = GPIO.PUD_DOWN
            else:
                raise ValueError('resistor must be "pull_up" or "pull_down"')

    def read(self):
        new_reading = GPIO.input(self.pin)
        now = time.time()
        with self._reading_lock:
            prev_reading = self._curr_reading
            dt = now - self._reading_time
            self._reading_time = now
            self._curr_reading = new_reading

        return (prev_reading, new_reading, dt)

    def start_reading(self):
        GPIO.setup(self.pin, GPIO.IN)
        if self.resistor is not None:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.resistor)

        def change(pin):
            prev_reading, new_reading, dt = self.read()
            if prev_reading != new_reading:
                self.context.update_pin(self.pin,
                                        prev_reading,
                                        new_reading,
                                        dt)

        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=change)


class Thingpin(object):
    """
    Monitor GPIO pins and report to AWS IoT.

    Each GPIO pin is associated with an AWS IoT Thing. As the GPIO pin
    state changes the AWS IoT Thing state is published via MQTT. An example
    is a GPIO pin connected to a reed switch to detect whether a door is open
    or closed. This would be associated with an AWS IoT Thing named "door".

    Once started it does not return.
    """

    def __init__(self, log, host=None, client_cert=None, private_key=None,
                 aws_iot_message_unit_cost=None, heartbeat_interval_seconds=60,
                 pin_mode=None, things=None, debug=False):
        """
        Create and configure a Thingpin.

        Args:
            log (logger): log to use
            host (str): host name of AWS IoT endpoint
            client_cert (str): name of client certificate file
            private_key (str): name of private key for client certificate
            aws_iot_message_unit_cost (float): cost of an AWS IoT message
                used to estimate monthly cost of operating this thingpin
            heartbeat_interval_seconds (float):  maximum time between reports
                to AWS IoT. Thanks to GPIO interrupts Thing status is reported
                immediately when it changes. Additionally the current Thing
                status is reported to AWS IoT every
                `heartbeat_interval_seconds` seconds. This lets you know
                thingpin is healthy. If `heartbeat_interval_seconds` is 60
                and a Thing in IoT has a state that is an hour old it means
                that there is a problem with thingpin, your Raspberry PI,
                the network, or AWS.

            things (dict of str: dict): each key is an AWS IoT Thing name
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
            debug (bool): if True log all MQTT traffic. The default is True
                as it is useful to see and not too noisy.
        """
        self.log = log
        self.host = host
        self.client_cert = os.path.expanduser(client_cert)
        self.private_key = os.path.expanduser(private_key)
        self.aws_iot_message_unit_cost = aws_iot_message_unit_cost
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self.thing_config = things
        self.debug = debug
        self.pin_mode = pin_mode
        self.things = None

        self.client = None
        self.initialized = False

    def initialize(self):
        """Initialize GPIO pins and connect to AWS IoT"""
        if not self.initialized:

            self.log.info('initializing')

            for k in ['host', 'client_cert', 'private_key',
                      'thing_config', 'debug']:
                self.log.info('{} = {}'.format(k, getattr(self, k)))

            self.log.info('AWS monthly cost guesstimate ${:,.2f}'.format(
                self.guess_monthly_cost()))
            self.log.info('(don\'t take the guesstimate too seriously!)')

            GPIO.setmode(getattr(GPIO, self.pin_mode))

            self.client = Client(self.host,
                                 client_cert_filename=self.client_cert,
                                 private_key_filename=self.private_key,
                                 log_mqtt=self.debug)

            self.initialized = True
            self.log.info('initialize complete')

    def cleanup(self):
        """Release system resources and reset GPIO pins"""

        # TODO: thingamon support disconnect() -> loop_stop()
        self.client.client.loop_stop()
        GPIO.cleanup()

    def update_pin(self, pin, prev_reading, curr_reading, dt):
        self.log.info('update: {} {}->{}, dt={}'.format(
            pin, prev_reading, curr_reading, dt))
        thing = self.things[pin]
        state = dict(curr=self.pin_reading_to_state(thing, curr_reading))
        if prev_reading is not None:
            state['prev'] = self.pin_reading_to_state(thing, prev_reading)
            state['dt'] = dt
        thing['thing'].publish_state(state)

    def pin_reading_to_state(self, thing, reading):
        if reading == GPIO.HIGH:
            return thing['iot_states']['HIGH']
        else:
            return thing['iot_states']['LOW']

    def guess_monthly_cost(self):
        # assumptions:
        #  - 30 days in a month
        #  - things don't change much: use heartbeat msg count + 1%
        msg_count = (
            (1.0 / self.heartbeat_interval_seconds) *
            1.01 *
            60 * 60 * 24 * 30 *
            len(self.thing_config)
        )
        return msg_count * self.aws_iot_message_unit_cost

    def run(self):
        """Monitor the things and report their states to AWS IoT"""
        self.initialize()
        self.log.info('run')

        # things indexed by pin number
        self.things = {}

        for name, value in self.thing_config.items():
            pin_num = value['pin']
            pin = Pin(self, pin_num, resistor=value['resistor'])
            self.things[pin_num] = {
                'thing': Thing(name, self.client),
                'iot_states': value['iot_states'],
                'pin': pin
            }
            pin.start_reading()

        while True:
            for thing in self.things.values():
                pin = thing['pin']
                prev_reading, new_reading, dt = pin.read()
                self.update_pin(pin.pin, prev_reading, new_reading, dt)
            time.sleep(self.heartbeat_interval_seconds)

        self.client.client.loop_stop()
