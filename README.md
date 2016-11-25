# onewire-to-mqtt.py

Onewire-to-mqtt.py is intended to run as a service,it connects to [owserver](http://owfs.org/index.php?page=owserver) (from [owfs](http://owfs.org) and reads the temperature values from **DS18x20** onewire sensors.
The temperatures which have been aquired using owserver will be published using a mqtt-broker.

A running [owserver](http://owfs.org/index.php?page=owserver) and a mqtt-broker (e.g: [mosquitto](https://mosquitto.org)) are required to use this deamon.

## Usage

a configuration file is the only parameter which has to be passed to the program:

```
usage: onewire-to-mqtt.py [-h] <config_file>

reads temperature sensors from onewire-server and
publishes the temperaturs to a mqtt-broker

positional arguments:
  <config_file>  file with configuration

optional arguments:
  -h, --help     show this help message and exit
```

## Example

```
 ./onewire-to-mqtt.py myconfig.cfg
```

## Configuration file

a self explaining sample configuration file is included 

```
# sample configuration 
 
# MQTT broker  related config
[mqtt]
host = 127.0.0.1
port = 1883

# polling interval for sensors
pollinterval = 30

# topic for status messages
statustopic = onewire-to-mqtt/status

# Onewire related config 
[onewire]
host= ::1
port = 4304      

[log]
#verbose = false
verbose = true
logfile = /var/log/onewire-to-mqtt.log

# list of sensors to be polled and according mqtt topics 
[sensors]
28.100000000000 = home/floor1/room1
10.200000000000 = home/floor1/room2             
28.300000000000 = home/floor1/room3
10.400000000000 = home/floor2/room1
28.500000000000 = home/floor2/room2
28.600000000000 = home/floor2/room3
28.700000000000 = home/floor3/room1 
10.800000000000 = home/floor3/room2 
10.900000000000 = home/floor3/room3 
10.010000000000 = home/floor3/room4 
28.020000000000 = home/floor3/room5 
28.030000000000 = home/floor3/room6 
10.040000000000 = home/floor3/room7  
10.050000000000 = home/floor3/room8 
10.060000000000 = home/floor3/room9
```
## Libs required 
the following libraries are required by onewire-to-mqtt.py 
- python-mosquitto (tested with version: 1.3.4-2) 
- python-ow (tested with version: 2.9p8-6)
- python-setproctitle (tested with version: 1.1.8-1)

install with
```
apt-get install python-ow
apt-get install python-mosquitto 
apt-get install python-setproctitle

```

test which version is installed
```
# dpkg -s python-ow python-mosquitto python-setproctitle 
Package: python-ow
Status: install ok installed
Priority: extra
Section: python
Installed-Size: 144
Maintainer: Vincent Danjean <vdanjean@debian.org>
Architecture: amd64
Source: owfs
Version: 2.9p8-6
Provides: python2.7-ow
Depends: libc6 (>= 2.14), libow-2.9-8 (>= 2.8p4), python (>= 2.7), python (<< 2.8)
Description: Dallas 1-wire support: Python bindings
 The 1-Wire bus is a cheap low-speed bus for devices like weather
 sensors, access control, etc. It can be attached to your system via
 serial, USB, I2C, and other interfaces.
 .
 Python bindings for the OWFS 1-Wire support library have been produced
 with SWIG and allow access to libow functions from Python code.
Homepage: http://owfs.org/
Python-Version: 2.7

Package: python-mosquitto
Status: install ok installed
Priority: optional
Section: python
Installed-Size: 135
Maintainer: Roger A. Light <roger@atchoo.org>
Architecture: all
Source: mosquitto
Version: 1.3.4-2
Depends: python (>= 2.7), python (<< 2.8)
Description: MQTT version 3.1 Python client library
 This is a Python module for implementing MQTT version 3.1 clients.
 .
 MQTT provides a method of carrying out messaging using a publish/subscribe
 model. It is lightweight, both in terms of bandwidth usage and ease of
 implementation. This makes it particularly useful at the edge of the network
 where a sensor or other simple device may be implemented using an arduino for
 example.
Homepage: http://mosquitto.org/

Package: python-setproctitle
Status: install ok installed
Priority: extra
Section: python
Installed-Size: 72
Maintainer: Debian Python Modules Team <python-modules-team@lists.alioth.debian.org>
Architecture: amd64
Version: 1.1.8-1
Depends: libc6 (>= 2.2.5), python (>= 2.7), python (<< 2.8)
Description: A setproctitle implementation for Python (Python 2)
 The library allows a process to change its title (as displayed by system tools
 such as ps and top).
 .
 Changing the title is mostly useful in multi-process systems, for example when
 a master process is forked: changing the children's title allows to identify
 the task each process is busy with. The technique is used by PostgreSQL and
 the OpenSSH Server for example.
Homepage: http://code.google.com/p/py-setproctitle/
```

## References 
- https://mosquitto.org
- http://owfs.org
- http://owfs.org/index.php?page=owserver
