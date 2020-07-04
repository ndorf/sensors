#!/usr/bin/python3

import Adafruit_DHT
from influxdb import InfluxDBClient
from datetime import datetime
from socket import gethostname
from sys import exit, stderr

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 27
HOSTNAME = gethostname()

client = InfluxDBClient()
client.switch_database('temps')

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        if True != client.write_points([
            {
                "measurement": "temp",
                "time": datetime.now().astimezone().isoformat(),
                "fields": {
                        "temperature": temperature,
                        "humidity": humidity
                },
                "tags": {
                        "host": HOSTNAME,
                        "sensor": "DHT22"
                }
            }
        ]):
            print("Failed to write data to db", file=stderr)

    else:
        print("Failed to retrieve data from DHT sensor", file=stderr)
        exit(1)
