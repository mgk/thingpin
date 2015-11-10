import pytest
import unittest
import sys
import os
import datetime
import time
from freezegun import freeze_time

try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call

# pick up our RPi stub which will mock after Watcher imports it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import RPi
import thingpin
from thingpin.pin import Watcher

HIGH = 1
LOW = 0

# Each use case is run as a test using the py.test fixtures feature.
use_cases = [
    {
        # name for test case to help when tests fail, need not be unique
        'name': 'one value',

        # debounce_delay to set for Watcher
        'debounce': 0,

        # GPIO readings to mock as list of pairs. Each reading is a pair of
        # (delay, value) where delay is how long the next call to
        # GPIO.wait_for_edge will take and value is what GPIO.input will
        # return. This let's us test the debounce logic with any simulated
        # timing we like.
        'readings': [(0, HIGH)],   # array of pairs. Each pair is

        # The expected behavior of the Watcher. It should call update_pin
        # once for each element of expected_updates.
        'expected_updates': [HIGH],
    },
    {
        'name': 'two values',
        'debounce': 0,
        'readings': [(0, LOW), (0, HIGH)],
        'expected_updates': [LOW, HIGH],
    },

    {
        'name': 'two values too quickly, one reading',
        'debounce': .1,
        'readings': [(0, LOW), (.05, HIGH)],
        'expected_updates': [LOW],
    },
    {
        'name': 'two values slowly, two readings',
        'debounce': .1,
        'readings': [(0, LOW), (.11, HIGH)],
        'expected_updates': [LOW, HIGH],
    },
    {
        'name': 'debounce test',
        'debounce': 3,
        'readings': [(0, LOW), (2, HIGH), (2, HIGH), (1, HIGH)],
        'expected_updates': [LOW, HIGH],
    },
    {
        'name': 'debounce test',
        'debounce': 10,
        'readings': [(0, LOW), (1, HIGH), (1, LOW), (9, HIGH),],
        'expected_updates': [LOW],
    },
    {
        'name': 'debounce test',
        'debounce': 3,
        'readings': [(0, LOW), (5, HIGH), (0, LOW), (1, LOW), (2, LOW)],
        'expected_updates': [LOW, HIGH, LOW],
    },
    {
        'name': 'debounce test',
        'debounce': 1,
        'readings': [(0, LOW), (5, LOW), (0, LOW), (1, LOW), (2, LOW)],
        'expected_updates': [LOW],
    },
]

@pytest.fixture(params=use_cases)
def use_case(request):
    return request.param

freezer = None
def incr_time(seconds=0):
    """Mock time by freezing it at the last frozen time + seconds"""
    global freezer
    if freezer is None:
        freezer = freeze_time('1999')
    else:
        freezer.stop()
        freezer = freeze_time(freezer.time_to_freeze +
                              datetime.timedelta(seconds=seconds))
    freezer.start()

def assert_almost_equal(actual, expected, fraction=1e-3, msg=None):
    assert abs(actual - expected) < fraction * expected

@patch.object(thingpin.pin.GPIO, 'wait_for_edge')
@patch.object(thingpin.pin.GPIO, 'input')
def test_loop(input, wait_for_edge, use_case):
    """Test each use case"""
    pin = 19

    def wait_generator(readings):
        for r in readings:
            incr_time(r[0])
            yield

    def input_generator(readings):
        for r in readings:
            yield r[1]

    wait_for_edge.side_effect = wait_generator(use_case['readings'])
    input.side_effect = input_generator(use_case['readings'])

    observer = Mock()
    w = Watcher(observer, pin, debounce_delay=use_case['debounce'],
                daemon=False)
    w.start()
    w.join()

    assert wait_for_edge.call_count == len(use_case['readings']) + 1
    assert input.mock_calls == [
        call(pin) for i in range(len(use_case['readings']))
    ]
    assert observer.update_pin.mock_calls == [
        call(19, u) for u in use_case['expected_updates']
    ]
