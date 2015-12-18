"""
|Build Status| |Coverage Status| |Downloads| |Flux Cap|

thingpin
========

`thingpin`_ monitors Raspberry Pi inputs and reports them to AWS IoT. Use it
to build an door sensor, water sensor, motion detector, etc. that is IoT
enabled.

`See Documentation for Installation and Usage details`_

.. _See Documentation for Installation and Usage details: https://github.com/\
mgk/thingpin/blob/master/README.md

.. |Build Status| image:: https://img.shields.io/travis/mgk/thingpin.svg
   :target: https://travis-ci.org/mgk/thingpin

.. |Coverage Status| image:: https://img.shields.io/coveralls/mgk/thingpin.svg
   :target: https://coveralls.io/github/mgk/thingpin?branch=master

.. |Downloads| image:: https://img.shields.io/pypi/dm/thingpin.svg
   :target: https://pypi.python.org/pypi/thingpin

.. |Flux Cap| image:: https://img.shields.io/badge/\
flux%20capacitor-1.21%20GW-orange.svg
"""
import os
import sys

from setuptools import setup, find_packages

setup(
    name='thingpin',
    version='3.0.1',
    description='Raspberry Pi pin monitor that reports to AWS IoT',
    long_description=__doc__,
    url='https://github.com/mgk/thingpin/blob/master/README.md',
    author='Michael Keirnan',
    author_email='michael@keirnan.com',
    packages=['thingpin'],
    package_dir={'': 'src'},
    package_data={
      'thingpin': ['*'],
      },
    install_requires=[
        'thingamon >= 0.2.2',
        'pyyaml',
        'python-daemon',
        'docopt',
    ],
    entry_points={
        'console_scripts': ['thingpin=thingpin.main:main'],
    },
    tests_require=[
        'mock',
        'pep8',
        'pytest',
        'freezegun'
    ],
    platforms='any',
    license='MIT',
    keywords="aws iot thing mqtt sensor gpio raspberry pi rpi",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Home Automation',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ]
)
