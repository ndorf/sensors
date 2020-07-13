#!/usr/bin/python3

import Adafruit_DHT
import argparse
from influxdb import InfluxDBClient
from datetime import datetime
from socket import gethostname
from sys import exit, stderr

SENSOR_CHOICES = {
    'DHT11': Adafruit_DHT.DHT11,
    'DHT22': Adafruit_DHT.DHT22,
    'AM2302': Adafruit_DHT.AM2302
}

args_parser = argparse.ArgumentParser(description='Ingest temperature/humidity sensor data into InfluxDB.')
args_parser.add_argument('-P', '--pin',
                         type=int,
                         default=4,
                         help='The GPIO pin the sensor is attached to. default: %(default)s')

args_parser.add_argument('-S', '--sensor',
                         choices=SENSOR_CHOICES.keys(),
                         default="DHT22",
                         help='The type of sensor. default: %(default)s')

args_parser.add_argument('-D', '--database',
                         default='sensors',
                         help='The name of the InfluxDB database to write to. default: %(default)s')

args_parser.add_argument('-M', '--measurement',
                         default='temp',
                         help='The name of the InfluxDB measurement to write to. default: %(default)s')

args = args_parser.parse_args()

DHT_SENSOR_NAME = args.sensor
DHT_SENSOR = SENSOR_CHOICES[DHT_SENSOR_NAME]
DHT_PIN = args.pin
HOSTNAME = gethostname()
MEASUREMENT = args.measurement

client = InfluxDBClient()
client.switch_database(args.database)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        if True != client.write_points([
            {
                "measurement": MEASUREMENT,
                "time": datetime.now().astimezone().isoformat(),
                "fields": {
                        "temperature": temperature,
                        "humidity": humidity
                },
                "tags": {
                        "host": HOSTNAME,
                        "sensor": DHT_SENSOR_NAME
                }
            }
        ]):
            print("Failed to write data to db", file=stderr)

    else:
        print("Failed to retrieve data from DHT sensor", file=stderr)
        exit(1)
