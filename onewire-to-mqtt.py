#!/usr/bin/env python
#
# This file is licensed under the terms of the GPL, Version 3
# 
# Copyright 2016 Dario Carluccio <check_owserver.at.carluccio.de>

__author__ = "Dario Carluccio"
__copyright__ = "Copyright (C) Dario Carluccio"
__license__ = "GPLv3"
__version__ = "1.0"

import os
import logging
import signal
import socket
import time
import sys
import mosquitto
import argparse
import ConfigParser
import ow
import setproctitle
from datetime import datetime, timedelta

parser = argparse.ArgumentParser( formatter_class=argparse.RawDescriptionHelpFormatter,  
description='''reads temperature sensors from onewire-server and 
publishes the temperaturs to a mqtt-broker''')
parser.add_argument('config_file', metavar="<config_file>", help="file with configuration")
# parser.add_argument("-v", "--verbose", help="increase log verbosity", action="store_true")
args = parser.parse_args()

# read and parse config file
config = ConfigParser.RawConfigParser()
config.read(args.config_file)
# [mqtt]
MQTT_HOST = config.get("mqtt", "host")
MQTT_PORT = config.getint("mqtt", "port")
HEARTBEATTOPIC = config.get("mqtt", "heartbeattopic")
POLLINTERVAL = config.getint("mqtt", "pollinterval")
# [Onewire]
OW_HOST = config.get("onewire", "host")
OW_PORT = config.get("onewire", "port")
# [log]
LOGFILE = config.get("log", "logfile")
VERBOSE = config.get("log", "verbose")
# [sensors]
section_name = "sensors"
SENSORS = {}
for name, value in config.items(section_name):
    SENSORS[name] = value

# compose MQTT client ID from appname and PID
APPNAME = "onewire-to-mqtt"
setproctitle.setproctitle(APPNAME)
MQTT_CLIENT_ID = APPNAME + "[_%d]" % os.getpid()
MQTTC = mosquitto.Mosquitto(MQTT_CLIENT_ID)

# init logging 
LOGFORMAT = '%(asctime)-15s %(message)s'
if VERBOSE:
    logging.basicConfig(filename=LOGFILE, format=LOGFORMAT, level=logging.DEBUG)
else:
    logging.basicConfig(filename=LOGFILE, format=LOGFORMAT, level=logging.INFO)

logging.info("Starting " + APPNAME)
if VERBOSE:
    logging.info("INFO MODE")
else:
    logging.debug("DEBUG MODE")

### MQTT Callback handler ###

# MQTT: message is published 
def on_mqtt_publish(mosq, obj, mid):
    logging.debug("MID " + str(mid) + " published.")

# MQTT: connection to broker 
# client has received a CONNACK message from broker
# return code:
#   0: Success                                                      -> Set LASTWILL 
#   1: Refused - unacceptable protocol version->EXIT
#   2: Refused - identifier rejected                                -> EXIT 
#   3: Refused - server unavailable                                 -> RETRY
#   4: Refused - bad user name or password (MQTT v3.1 broker only)  -> EXIT
#   5: Refused - not authorised (MQTT v3.1 broker only)             -> EXIT
def on_mqtt_connect(mosq, obj, return_code):    
    logging.debug("on_connect return_code: " + str(return_code))
    if return_code == 0:
        logging.info("Connected to %s:%s", MQTT_HOST, MQTT_PORT)
        # set Lastwill 
        MQTTC.publish(HEARTBEATTOPIC, "1 - connected", retain=True)
        # process_connection()
    elif return_code == 1:
        logging.info("Connection refused - unacceptable protocol version")
        cleanup()
    elif return_code == 2:
        logging.info("Connection refused - identifier rejected")
        cleanup()
    elif return_code == 3:
        logging.info("Connection refused - server unavailable")
        logging.info("Retrying in 10 seconds")
        time.sleep(10)
    elif return_code == 4:
        logging.info("Connection refused - bad user name or password")
        cleanup()
    elif return_code == 5:
        logging.info("Connection refused - not authorised")
        cleanup()
    else:
        logging.warning("Something went wrong. RC:" + str(return_code))
        cleanup()

# MQTT: disconnected from broker 
def on_mqtt_disconnect(mosq, obj, return_code):
    if return_code == 0:
        logging.info("Clean disconnection")
    else:
        logging.info("Unexpected disconnection. Reconnecting in 5 seconds")
        logging.debug("return_code: %s", return_code)
        time.sleep(5)

# MQTT: debug log 
def on_mqtt_log(mosq, obj, level, string):
    if VERBOSE:    
        logging.debug(string)

### END of MQTT Callback handler ###


# clean disconnect on SIGTERM or SIGINT. 
def cleanup(signum, frame):
    logging.info("Disconnecting from broker")
    # Publish a retained message to state that this client is offline
    MQTTC.publish(HEARTBEATTOPIC, "0 - DISCONNECT", retain=True)
    MQTTC.disconnect()
    MQTTC.loop_stop()
    logging.info("Exiting on signal %d", signum)
    sys.exit(signum)


# init connection to MQTT broker 
def mqtt_connect():    
    logging.debug("Connecting to %s:%s", MQTT_HOST, MQTT_PORT)
    # Set the last will before connecting
    MQTTC.will_set(HEARTBEATTOPIC, "0 - LASTWILL", qos=0, retain=True)
    result = MQTTC.connect(MQTT_HOST, MQTT_PORT, 60, True)
    if result != 0:
        logging.info("Connection failed with error code %s. Retrying", result)
        time.sleep(10)
        mqtt_connect()
    # Define callbacks
    MQTTC.on_connect = on_mqtt_connect
    MQTTC.on_disconnect = on_mqtt_disconnect
    MQTTC.on_publish = on_mqtt_publish
    MQTTC.on_log = on_mqtt_log
    MQTTC.loop_start()


# Main Loop
def main_loop():
    logging.debug(("onewire server : %s") % (OW_HOST))    
    logging.debug(("  port         : %s") % (str(OW_PORT)))
    logging.debug(("MQTT broker    : %s") % (MQTT_HOST))
    logging.debug(("  port         : %s") % (str(MQTT_PORT)))
    logging.debug(("pollinterval   : %s") % (str(POLLINTERVAL)))
    logging.debug(("heartbeattopic : %s") % (str(HEARTBEATTOPIC)))
    logging.debug(("sensors        : %s") % (len(SENSORS)))
    for owid, owtopic in SENSORS.items():
        logging.debug(("  %s : %s") % (owid, owtopic))
    
    # Connect to the broker and enter the main loop
    mqtt_connect()

    # Connect to the broker and enter the main loop
    ow.init(("%s:%s") % (OW_HOST, str(OW_PORT))) 
    ow.error_level(ow.error_level.fatal)
    ow.error_print(ow.error_print.stderr)

    while True:
        # simultaneous temperature conversion
        ow._put("/simultaneous/temperature","1")
        item = 0        
        # iterate over all sensors
        for owid, owtopic in SENSORS.items():
            logging.debug(("Querying %s : %s") % (owid, owtopic))
            try:             
                sensor = ow.Sensor(owid)                 
                owtemp = sensor.temperature            
                logging.debug(("Sensor %s : %s") % (owid, owtemp))
                MQTTC.publish(owtopic, owtemp)
                
            except ow.exUnknownSensor:
                logging.info("Threw an unknown sensor exception for device %s - %s. Continuing", owid, owname)
                continue
            
            time.sleep(float(POLLINTERVAL) / len(SENSORS))
    
# Use the signal module to handle signals
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

# start main loop
try:
    main_loop()
except KeyboardInterrupt:
    logging.info("Interrupted by keypress")
    sys.exit(0)
    
