# Change Log
This project uses [Semantic Versioning](http://semver.org/).

## *Unreleased*
### Added
- reconnect to Adafruit when disconnected
- install script that uses .deb package
  - installs the thingpin python package
  - installs the Adafruit IO python package (which is not yet on PyPI)
  - installs sample configs for AWS and Adafruit in /etc/thingpin
  - configures thingpin to run and restart automatically as runit service
- .deb package available on gemfury
- install script singed with mgk key available on MIT keyserver

The README needs an overhaul, but installing with the install script worked on both the Pi B+ and Pi2 test machines.

## [2.0.1](https://github.com/mgk/thingpin/releases/tag/v2.0.1) - [2015-11-22]

### Fixed
- doc fixes

## [2.0.0](https://github.com/mgk/thingpin/releases/tag/v2.0.0) - [2015-11-22]
### Added
- factor notification of changes to Notifier class
- support publishing to Adafruit IO

### Changed
- **breaking change**: config file format, pushing AWS config under notifiers section. Updating to new format should be straightforward. The sample config was updated and there is an AWS config in the new examples directory.

## [1.2.0](https://github.com/mgk/thingpin/releases/tag/v1.2.0) - [2015-11-11]
### Added
- tests
- reduced IoT cost dramatically by only reporting changes and factoring
  out the heartbeat

### Changed
- uses configurable sleep poll and [Limor Fried's version of debounce](https://www.arduino.cc/en/Tutorial/Debounce)
- no longer reports curr/prev/dt as AWS IoT rules can be used for change
  detection [as described here](https://forums.aws.amazon.com/thread.jspa?messageID=684890#684890)

## [1.1.0](https://github.com/mgk/thingpin/releases/tag/v1.1.0) - [2015-11-02]
### Added
- publish prev, curr, and dt in payload

## [1.0.0](https://github.com/mgk/thingpin/releases/tag/v1.0.0) - [2015-11-01]

### Added
- initial version
