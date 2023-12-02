# MQTT Raspberry-Pi Kitchen Ring-Bell Publisher ‒ A minimal MQTT client to ring when the food is ready!

*MQTT Raspberry-Pi Kitchen Ring Publisher* is a minimal Python solution that integrates paho-mqtt for creating an MQTT client, that is triggered upon button press.

## How to use on the Raspberry Pi (Debian based OSes)

```sh
sudo apt install libsystemd-dev python3-systemd
git clone https://github.com/supercomputer7/rpi-mqtt-kitchen-ringbell-button-publisher
cd rpi-mqtt-kitchen-ringbell-button-publisher
sudo python3 -m pip install -r requirements.txt

# Execute the MQTT publisher script
python3 publisher.py \ 
    --mqtt-broker-ip MQTT_IP \
    --mqtt-topic MQTT_TOPIC \
    --mqtt-user MQTT_USER \
    --mqtt-password MQTT_PASS \
    --mqtt-published-data MQTT_DATA \
    --gpio-pin-input GPIO_PIN
```

You can use this Python script as a `systemd` service with the provided
`mqtt-kitchen-button-publisher.service` file. Please configure the script as desired by
editing the service file. Then install the service by running the following
commands:
```sh
sudo mkdir -p /opt/mqtt_kitchen_button_publisher/
sudo install publisher.py /opt/mqtt_kitchen_button_publisher
sudo install mqtt-kitchen-button-publisher.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable mqtt-kitchen-button-publisher.service
sudo systemctl start mqtt-kitchen-button-publisher.service
```

## Frequent Disconnections from the MQTT broker

You might consider disabling WiFi Power saving mode due to frequent disconnections
from the MQTT broker.

- Disable WiFi Power Saving: Suggestions are taken from answers to this [question](https://raspberrypi.stackexchange.com/questions/96606/make-iw-wlan0-set-power-save-off-permanent).
- Ensure the keepalive timeout when connecting the MQTT broker is infinite (0)

Either disable WiFi Power Saving by:
- Creating new [systemd service and enabling/disabling it appropriately](https://raspberrypi.stackexchange.com/questions/96606/make-iw-wlan0-set-power-save-off-permanent/96644#96644)
- Adding new line to `/etc/rc.local` to [disable WiFi power saving](https://raspberrypi.stackexchange.com/a/96608).

Both problems were resolved for me, but you might need to investigate further.
Check the journal log to examine the `rc` (return code) on why the program failed
and also if possible, check the logs of your MQTT broker.

## License

The project is licensed under the MIT license.
