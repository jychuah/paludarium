# Paludarium Controller

Raspberry Pi GPIO based environmental controller for a paludarium - a greenhouse with an aquarium.

### Disclaimer

Work in progress! Soldering and Linux skills required! Proceed at your own risk. I take no responsibility for a bad configuration sending more than an analog 10v signal to your LED fixture, which you didn't know was PWM dimmed in the first place.

### Features

- 0-10v analog LED dimming controller
- Optional GrovePi temperature, humidity and soil moisture data logging
- X-Windows interface
- Web interface... eventually

### Requirements

The platform is Raspberry Pi B+ with Raspbian. You will need:

- python-dev
- wiringPi
- GrovePi
- python: sseclient, requests