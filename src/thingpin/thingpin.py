import os
import time
import traceback
from thingamon import Client, Thing
from .pin import *
import logging

log = logging.getLogger('thingpin')


class Thingpin(object):
    """
    Monitor GPIO pins and report to AWS IoT.

    Each GPIO pin is associated with an AWS IoT Thing. As the GPIO pin
    state changes the AWS IoT Thing state is published via MQTT. An example
    is a GPIO pin connected to a reed switch to detect whether a door is open
    or closed. This would be associated with an AWS IoT Thing named "door".

    Once started it does not return.
    """

    def __init__(self, host=None, client_cert=None, private_key=None,
                 aws_iot_message_unit_cost=None, heartbeat_thing=None,
                 heartbeat_interval_seconds=None,
                 estimated_change_freq=1.0 / 3600,
                 pin_mode=None, things=None, debug=False):
        """
        Create and configure a Thingpin.

        Args:
            host (str): host name of AWS IoT endpoint
            client_cert (str): name of client certificate file
            private_key (str): name of private key for client certificate
            aws_iot_message_unit_cost (float): cost of an AWS IoT message
                used to estimate monthly cost of operating this thingpin
            heartbeat_thing (str): name of AWS IoT Thing for state of
                thingpin process. This can be used to verify that thingpin
                is healthy even if it hasn't reported any pin changes in
                a long time. If None, no heartbeat is reported.
            heartbeat_interval_seconds (float): how often to report thingpin
                state if `heartbeat_thing` is not None. If <= 0 then
                no heartbeat is reported.
            estimated_change_freq (float): estimate of how often each
                pin will change. Only used for guessing AWS costs at startup.
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
        self.host = host
        self.client_cert = os.path.expanduser(client_cert)
        self.private_key = os.path.expanduser(private_key)
        self.aws_iot_message_unit_cost = aws_iot_message_unit_cost
        self.heartbeat_thing = heartbeat_thing
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        if heartbeat_interval_seconds <= 0:
            self.heartbeat_thing = None
            self.heartbeat_interval_seconds = None
        self.estimated_change_freq = estimated_change_freq
        self.thing_config = things
        self.debug = debug
        self.pin_mode = pin_mode
        self.pins = {}

        self.client = None
        self.initialized = False

    def initialize(self):
        """Initialize GPIO pins and connect to AWS IoT"""
        if not self.initialized:

            log.info('initializing')

            for k in ['host', 'client_cert', 'private_key', 'heartbeat_thing',
                      'heartbeat_interval_seconds', 'thing_config', 'debug']:
                log.info('{} = {}'.format(k, getattr(self, k)))

            log.info('AWS monthly cost guesstimate ${:,.6f}'.format(
                self.guess_monthly_cost()))
            log.info('(don''t take the guesstimate too seriously!)')

            set_pin_mode(self.pin_mode)

            # MQTT client
            self.client = Client(self.host,
                                 client_cert_filename=self.client_cert,
                                 private_key_filename=self.private_key,
                                 log_mqtt=self.debug)

            # Pins
            for name, config in self.thing_config.items():
                self.pins[name] = Pin(self.client, name, config)

            self.initialized = True
            log.info('initialize complete')

    def cleanup(self):
        """Release system resources and reset GPIO pins"""
        self.client.disconnect()
        pin_cleanup()

    def guess_monthly_cost(self):
        seconds_in_month = 60 * 60 * 24 * 30
        if self.heartbeat_interval_seconds:
            heartbeat_freq = 1.0 / self.heartbeat_interval_seconds
        else:
            heartbeat_freq = 0

        msgs = heartbeat_freq + self.estimated_change_freq * seconds_in_month
        return msgs * self.aws_iot_message_unit_cost

    def heartbeat(self):
        # TODO: implement me!
        pass

    def run(self):
        self.initialize()
        log.info('run')

        for pin in self.pins.values():
            pin.run()

        while True:
            time.sleep(self.heartbeat_interval_seconds or 1e6)
            self.heartbeat()


class Pin(object):
    """Composite of: a Watcher() thread, an MQTT Thing(), and config info"""

    def __init__(self, mqtt_client, name, config):
        """Setup an input pin"""
        self.mqtt_client = mqtt_client
        self.name = name
        self.config = config
        setup_input_pin(config['pin'], config.get('resistor'))

        self.watcher = Watcher(observer=self,
                               pin=config['pin'],
                               sleep=config.get('sleep', .010),
                               debounce_delay=config.get('debounce_delay'))

        self.thing = Thing(self.name, self.mqtt_client)

    def update_pin(self, pin, reading):
        log.info('update_pin({},{})'.format(pin, reading))
        self.thing.publish_state(self.get_state(reading))

    def get_state(self, reading):
        if reading == GPIO.HIGH:
            return self.config['iot_states']['HIGH']
        else:
            return self.config['iot_states']['LOW']

    def run(self):
        self.watcher.start()
