# thingpin

A Raspberry Pi sensor monitor that publishes to [AWS IoT](https://aws.amazon.com/iot/) using [MQTT](http://mqtt.org/). Features:

 + runs interactively or as a well behaved service daemon that starts automatically on boot
 + can watch any number of GPIO pins for HIGH or LOW state
 + reports pin changes immediately to AWS IoT
 + highly configurable
 	+ pin 21 HIGH can report {"door": "open"} and pin 15 LOW can report {"water": "detected": "yes"}} to AWS IoT
 	+ pull up or pull down resistors can be software configured independently for each input

## Getting Started

You'll need an AWS account with IoT enabled. Run through the AWS IoT Getting Started guide to create and test a sample thing. The setup may feel a little cumbersome, but it will be worth it.

Once setup you use an x.509 certificate to authenticate your thing: no AWS access keys are needed on your Raspberry Pi.

## Requirements

A Raspberry Pi with Raspian Jessie. If you have a different distro thingpin should still work if you have:

 - python 2.7 (`python -V` to check)
 - openssl 1.0.1+ linked into your python (`python -c "import ssl; print(ssl.OPENSSL_VERSION)"` to check)
 - RPi.GPIO 0.6.0a3 (`python -c "import RPi.GPIO; print(RPi.GPIO.VERSION)"` to check)

## Setup

There is Raspberry Pi setup and AWS IoT setup.

+ Raspberry Pi setup
	+ ensure python, openssl, and RPi.GPIO versions as above

 + AWS IoT setup
	+ requires AWS account, access keys, and `awscli` python package
	+ can be done on any computer

**(There are a lot of AWS IoT setups here. I'm working on streamlining this part)**

### Create AWS IoT Thing

You'll need an AWS account with IoT enabled. Follow the AWS IoT getting started instructions to create and test a Thing. You can do this on any computer: it need not be on the RPi. Create a Thing for each sensor you have. For example if you have single door sensor `door1` is a good name.

When you are done you should have:

 - a public certificate PEM file: `cert.pem`
 - a private key PEM file: `private-key.pem`

These are what your RPi will use to authenticate itself to your AWS account. You also need
the name of your AWS IoT host (a name like `SOME-HOST.iot.SOME-REGION.amazonaws.com`). This is created for you during the AWS IoT setup process.

Go through the tests with AWS IoT to make sure public cert, private key, and endpoint are correct before setting up the RPi.

### Install thingpin on the RPi

```console
pip install thingpin

```


### Running

Run interactively on RPi:

```console
thingpin -h

```

Install as daemon: (**doc in progress, watch tihs space**)

*todo: script for `installl-thingpin-daemon` includes certs, generates config, does init.d stuff, will still need to edit config for your sensors

## Cost

AWS IoT currently charges $5 / million messages sent. `thingpin` guesstimates its monthly AWS IoT cost for you at startup (for the default setup with 2 sensors it is around $0.87 / month). This is just a guess and depends on your config and sensor activity. For accurate and up to date info see the AWS IoT Pricing page.

## License
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
