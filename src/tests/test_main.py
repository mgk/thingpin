try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call

import os
import sys
import pkg_resources
import thingpin
from thingpin.main import main

def test_run():
    config = pkg_resources.resource_filename('thingpin',
                                             'thingpin-config.yml.sample')
    with patch.object(sys, 'argv', ['thingpin', '-c', config, 'run']):
        # returns non-zero (unless running on RPi)
        assert main() == 1

def test_install_service():
    config = pkg_resources.resource_filename('thingpin',
                                             'thingpin-config.yml.sample')
    with patch.object(sys, 'argv',
        ['thingpin', '-c', config, 'install-service']):
        assert main() is None

def test_create_config(tmpdir):
    wd = os.getcwd()
    try:
        os.chdir(str(tmpdir))
        with patch.object(sys, 'argv', ['thingpin', 'create-config']):
            assert main() is None
    finally:
        os.chdir(wd)

def test_create_config_already_exists(tmpdir):
    wd = os.getcwd()
    try:
        os.chdir(str(tmpdir))
        with open('thingpin-config.yml', 'w') as f:
            f.write('---')
            with patch.object(sys, 'argv', ['thingpin', 'create-config']):
                assert main() == 2
    finally:
        os.chdir(wd)


