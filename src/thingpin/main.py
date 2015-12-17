#!/usr/bin/env python

"""
Usage: thingpin -h
       thingpin [options] run
       thingpin create-config
       thingpin [options] install-service

Monitor GPIO pins and update AWS IoT via MQTT.

Arguments:
    run              run the thingpin monitor
    create-config    generate sample YAML thingpin-config.yml and exit
    install-service  install daemon to run automatically on boot

Options:
    -h --help               show usage and exit
    -c --config=CONFIG      YAML config file [default: thingpin-config.yml]
    -p --pidfile=PIDFILE    run as a daemon, writing process id to PIDFILE
    -l --log=LOG            log file to use. By default /var/log/thingpin.log
                            is used when running as a daemon and standard
                            out is used otherwise.
"""

import os
import sys
import time
import yaml
import docopt
import shutil
import pkg_resources
import traceback
import signal


from .logger import Logger
from .notifiers import create_notifier

try:
    from .thingpin import Thingpin
except ImportError:
    Thingpin = None


def main():
    args = docopt.docopt(__doc__)

    if args['create-config']:
        sample = pkg_resources.resource_filename('thingpin',
                                                 'thingpin-config.yml.sample')
        config_file = 'thingpin-config.yml'
        if os.path.exists(config_file):
            print('config file {} already exists, not overwriting'.format(
                config_file))
            return 2
        else:
            shutil.copyfile(sample, config_file)
            print('created config file: {}'.format(config_file))
            return

    config_file = os.path.expanduser(args['--config'])
    with open(config_file) as f:
        config = yaml.load(f)

    if args['install-service']:
        print('** coming soon - watch this space **')
        return

    log = get_logger(args)

    if Thingpin is None:
        log.error('must run on Raspberry Pi')
        return 1

    # TODO: support more than one
    notifier_config = config['notifiers'].items()[0]
    notifier = create_notifier(notifier_config[0], notifier_config[1])
    service = Thingpin(notifier,
                       pin_mode=config['pin_mode'],
                       things=config['things'],
                       debug=config.get('debug', False))

    pidfile = args.get('--pidfile')
    if pidfile is not None:
        with open(os.path.expanduser(pidfile), "w") as f:
            f.write(str(os.getpid()))

    try:
        service.run()
    except KeyboardInterrupt:
        log.info('exiting on Ctrl-C...')
        service.cleanup()
        return


def get_logger(args):
    log_file = args.get('--log')
    if log_file is None and args.get('--pidfile'):
        log_file = '/var/log/thingpin.log'
    return Logger(log_file=log_file)


if __name__ == '__main__':
    sys.exit(main())
