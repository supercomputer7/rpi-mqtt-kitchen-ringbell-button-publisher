#!/usr/bin/env python3

#   Copyright (c) 2023 Liav A
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import argparse
import random
import logging
from paho.mqtt import client as mqtt_client
import RPi.GPIO as GPIO
from time import sleep
from systemd.journal import JournalHandler
import asyncio

button_gpio_button_gpio_active = False

def button_callback(channel):
    global button_gpio_active
    button_gpio_active = GPIO.input(channel)

async def publish_on_input(client, mqtt_topic, gpio_pin_input, mqtt_published_data):
    global button_gpio_active
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin_input, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(gpio_pin_input, GPIO.FALLING, callback=button_callback) 

    while True:
        if button_gpio_active:
            result = client.publish(mqtt_topic, mqtt_published_data)
            if result[0] == 0:
                print(f"Send `{mqtt_published_data}` to topic `{mqtt_topic}`")
            else:
                print(f"Failed to send message to topic {mqtt_topic}, gracefully ignoring.")
            sleep(10)

def connect_mqtt(broker_ip, broker_port, broker_username, broker_password, client_id) -> mqtt_client:
    log = logging.getLogger('pymqtt-kitchen-button-ringbell-publisher')
    log.addHandler(JournalHandler())
    log.setLevel(logging.INFO)
    def on_disconnect(client, userdata, rc):
        log.info("Exit due to disconnecting from MQTT Broker, reason: " + str(rc))
        exit(1)
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")
            log.info("Exit due to connection failure to MQTT Broker, reason: " + str(rc))
            exit(1)

    client = mqtt_client.Client(client_id)
    if broker_username is not None and broker_password is not None:
        client.username_pw_set(broker_username, broker_password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker_ip, broker_port, keepalive=0)
    return client

def main():
    parser = argparse.ArgumentParser(
        description='An MQTT client that can be used to send a notification ' + 
                    'with a push button being pressed, on the Raspberry Pi.')
    parser.add_argument('--gpio-pin-input', default=27, type=int,
        help='Raspberry Pi GPIO pin button input (default GPIO 27)')
    parser.add_argument('--mqtt-broker-ip', required=True,
        help='MQTT Broker IP')
    parser.add_argument('--mqtt-broker-port', default=1883, type=int,
        help='MQTT Broker TCP port')
    parser.add_argument('--mqtt-topic', required=True,
        help='MQTT Broker topic to be subscribed')
    parser.add_argument('--mqtt-user', default=None,
        help='MQTT Broker username')
    parser.add_argument('--mqtt-password', default=None,
        help='MQTT Broker username')
    parser.add_argument('--mqtt-published-data', required=True,
        help='MQTT Data to be published')

    args = parser.parse_args()

    client_id = f'python-mqtt-{random.randint(0, 65536)}'
    client = connect_mqtt(args.mqtt_broker_ip, args.mqtt_broker_port, args.mqtt_user, args.mqtt_password, client_id)
    asyncio.run(publish_on_input(client, args.mqtt_topic, args.gpio_pin_input, args.mqtt_published_data))
    client.loop_forever()

if __name__ == '__main__':
    main()
