# Python based thermostat example (bridge) device to thermostat of FLH.

## Installation

Build the Python/C library:

```shell
cd ~/connectedhomeip/
git submodule update --init
source scripts/activate.sh

./scripts/build_python_device.sh --chip_detail_logging true

sudo su # dhclient is called, needs root
source ./out/python_env/bin/activate
```

Install the python dependencies:

## Usage

Run the Python lighting matter device:

```shell
cd examples/flh-thermostat/python
python flh-thermostat.py
```

Control the Python thermostat of FLH matter device:

```shell
source ./out/python_env/bin/activate

$ ./out/chip-tool/chip-tool interactive start
>>> pairing code-wifi 554433 SSID SSID_PWD MT:-24J042C00KA0648G00
>>> thermostat setpoint-raise-lower 0 29 554433 1
>>> thermostat setpoint-raise-lower 1 21 554433 1
>>> thermostat setpoint-raise-lower 2 24 554433 1

```
