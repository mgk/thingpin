import time
from threading import Thread
import RPi
from RPi import GPIO
from collections import Iterable
import itertools

HIGH = GPIO.HIGH
LOW = GPIO.LOW


def set_pin_mode(mode):
    """
    Set pin numbering mode.

    Args:
        mode (str): mode to set, must be 'BOARD' or 'BCM'
    """
    GPIO.setmode(getattr(GPIO, mode))


def setup_input_pin(pin, resistor=None):
    """
    Setup input pin.

    Setup pin for input and optionally configure a pull up or pull down
    resistor. `set_pin_mode` must be called first.

    Args:
        pin (int): number of pin to setup for input
        resistor (str): how to configure the internal resistor for the pin.
            Allowable values:
                - `pull_up`: enable pull up resistor
                - `pull down`: enable pull down resistor
                - `float`: do not enable resistor
                - `None`: same as `float`
    """
    if resistor == 'pull_up':
        pull_up_down = GPIO.PUD_UP
    elif resistor == 'pull_down':
        pull_up_down = GPIO.PUD_DOWN
    elif resistor == 'float' or resistor is None:
        pull_up_down = None
    else:
        raise ValueError('invalid resistor setting {}'.format(resistor))

    GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)


def pin_cleanup():
    GPIO.cleanup()


class Watcher(Thread):
    def __init__(self, observer, pin, sleep, debounce_delay=0, daemon=True):
        super(Watcher, self).__init__(name='PinWatcher-{}'.format(pin))
        self.daemon = daemon
        self.observer = observer
        self.pin = pin
        self.debounce_delay = debounce_delay
        self.reading = None
        self.last_reading = None
        self.debounce_time = 0

    def run(self):
        while True:
            try:
                GPIO.wait_for_edge(self.pin, GPIO.BOTH)
            except StopIteration as e:
                return
            new_reading = GPIO.input(self.pin)
            now = time.time()
            dt = now - self.debounce_time
            if new_reading != self.last_reading:
                self.debounce_time = now
            if dt >= self.debounce_delay and new_reading != self.reading:
                self.observer.update_pin(self.pin, new_reading)
                self.reading = new_reading
            self.last_reading = new_reading
