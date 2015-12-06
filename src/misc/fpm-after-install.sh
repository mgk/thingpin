#!/bin/bash

echo "Installing thingpin package..."
pip2 install /tmp/<%= name %>-<%= version %>.tar.gz

echo "Install Adafruit IO client package..."
pip2 install https://github.com/mgk/io-client-python/zipball/disconnect-fix

