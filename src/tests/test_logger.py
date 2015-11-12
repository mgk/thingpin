import thingpin
from thingpin.logger import Logger

def test_logger_file():
    assert Logger(log_file='foo.log')

def test_logger_stdout():
    assert Logger()
