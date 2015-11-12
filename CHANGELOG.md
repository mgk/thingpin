# Change Log
This project uses [Semantic Versioning](http://semver.org/).

## *Unreleased*
### Added
- stuff

### Changed
- things

### Fixed
- bugs
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
