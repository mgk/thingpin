#!/bin/bash

echo "Installing thingpin package..."
pip2 install /tmp/<%= name %>-<%= version %>.tar.gz

echo "Install Adafruit IO client package..."
pip2 install https://github.com/adafruit/io-client-python/zipball/65320a3a

mv /tmp/thingpin-service /etc/service/thingpin
