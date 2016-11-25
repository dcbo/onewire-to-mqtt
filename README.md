# check_onewire.py

publish onewire temperature sensor values to MQTT.

check_onewire.py is intended to run as a service. It connects to [owserver](http://owfs.org/index.php?page=owserver) (from [owfs](http://owfs.org) and reads the temperature values from **DS18x20** onewire sensors.
The temperatures which have been aquired using iwserver will be published using a mqtt-broker.

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

## References 
- https://mosquitto.org
- http://owfs.org
- http://owfs.org/index.php?page=owserver
