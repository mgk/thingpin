"""
|Downloads|

thingpin
========

`thingpin`_ monitors RaspBerry Pi inputs and reports them to AWS IoT. Use it
to build an door sensor, water sensor, motion detector, etc. that is IoT
enabled.

`See Documentation for Installation and Usage details`_

.. _See Documentation for Installation and Usage details: https://github.com\
/mgk/thingpin/blob/master/README.md

.. |Downloads| image:: https://img.shields.io/pypi/dm/thingpin.svg
   :target: https://pypi.python.org/pypi/thingpin
"""
import os
import sys

from setuptools import setup, find_packages

setup(
    name='thingpin',
    version='1.0.0',
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
        'thingamon',
        'pyyaml',
        'python-daemon',
        'docopt',
    ],
    entry_points={
        'console_scripts': ['thingpin=thingpin.main:main'],
    },
    tests_require=['pep8'],
    platforms='any',
    license='MIT',
    keywords="aws iot mqtt sensor gpio raspberry pi rpi",
    classifiers=[
        'Development Status :: 3 - Alpha',
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
