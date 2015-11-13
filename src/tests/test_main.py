try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call

import os
import sys
import pkg_resources

import thingpin
import thingpin.main
from thingpin.main import main

def test_run_not_on_pi():
    config = pkg_resources.resource_filename('thingpin',
                                             'thingpin-config.yml.sample')
    with patch.object(sys, 'argv', ['thingpin', '-c', config, 'run']):
        # returns non-zero (unless running on RPi)
        assert main() == 1

@patch.object(thingpin.main, 'Thingpin')
def test_run_on_pi(MockThingpin):
    config = pkg_resources.resource_filename('thingpin',
                                             'thingpin-config.yml.sample')
    with patch.object(sys, 'argv', ['thingpin', '-c', config, 'run']):
        mock_thingpin = Mock()
        MockThingpin.return_value = mock_thingpin
        assert main() is None
        mock_thingpin.run.assert_called_once_with()

@patch.object(thingpin.main, 'Thingpin')
def test_run_on_pi_ctrl_c(MockThingpin):
    config = pkg_resources.resource_filename('thingpin',
                                             'thingpin-config.yml.sample')
    with patch.object(sys, 'argv', ['thingpin', '-c', config, 'run']):
        mock_thingpin = Mock()
        MockThingpin.return_value = mock_thingpin
        mock_thingpin.run.side_effect = KeyboardInterrupt()
        assert main() is None
        mock_thingpin.run.assert_called_once_with()
        mock_thingpin.cleanup.assert_called_once_with()

@patch.object(thingpin.main, 'Thingpin')
@patch.object(thingpin.main, 'Logger')
@patch.object(thingpin.main.daemon, 'DaemonContext')
@patch.object(thingpin.main.daemon, 'pidfile')
def test_run_on_pi_as_daemon(MockThingpin, MockLogger, MockDaemonContext,
                             mock_pidfile, tmpdir):
    config = pkg_resources.resource_filename('thingpin',
                                             'thingpin-config.yml.sample')
    with patch.object(sys, 'argv',
                      [
                        'thingpin',
                        '-c', config,
                        '--pidfile', tmpdir.join('t.pid'),
                        'run']):
        mock_thingpin = Mock()
        MockThingpin.return_value = mock_thingpin
        assert main() is None
        # mock_thingpin.run.assert_called_once_with()

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


