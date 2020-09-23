#!/usr/bin/env python3

import tempfile
import shutil
import io
import csv
import time
from typing import Dict
import requests

from utils.PressureUtils import adjust_to_mean_sea_level
from wpiio.MCP23017 import MCP23017
from sensors.BME280 import BME280
from sensors.DigitalOnOffSensor import DigitalOnOffSensor
from sensors.SI1145 import SI1145
from sensors.GY271 import GY271
from sensors.Camera import Camera
from sensors.RainDetector import RainDetector
from utils import CompassUtils


def light_sensor():
    si1145_sensor = SI1145()
    print("SI1145 ID: %s, valid: %s" % (hex(si1145_sensor.chip_id), si1145_sensor.is_chip_id_valid()))
    try:
        while True:
            time.sleep(1)
            print("SI1145 UV index: %s" % (si1145_sensor.get_aux_data() * 0.01))
            print("SI1145 IR: %s" % (si1145_sensor.get_als_ir_data()))
            print("SI1145 visible light: %s" % (si1145_sensor.get_als_vis_data()))
    except KeyboardInterrupt:
        pass


def temperature_sensor(config: Dict):
    bme280_sensor = BME280()
    print("BME280 ID: %s, valid: %s" % (hex(bme280_sensor.chip_id), bme280_sensor.is_chip_id_valid()))
    bme280_sensor.start(BME280.CONTROL_MODE_NORMAL)
    try:
        while True:
            time.sleep(1)
            pressure_mean_sea_level = adjust_to_mean_sea_level(bme280_sensor.pressure, config["location"]["height"],
                                                               config["location"]["lat"], bme280_sensor.temperature)
            print("Temperature : %.4f°C, Pressure : %.4fhPa (%.4fhPa mean sea level), Humidity : %.4f%%" % (
                bme280_sensor.temperature, bme280_sensor.pressure, pressure_mean_sea_level, bme280_sensor.humidity))
    except KeyboardInterrupt:
        pass
    bme280_sensor.stop()


def compass_sensor(config: Dict):
    gy271_sensor = GY271(config)
    gy271_sensor.start()
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    points = []
    try:
        while True:
            raw = gy271_sensor.raw
            degrees = gy271_sensor.heading_degrees
            heading_str = CompassUtils.degrees_to_string(degrees)
            cardinal_point_8 = CompassUtils.get_cardinal_point(degrees, 8)
            cardinal_point_16 = CompassUtils.get_cardinal_point(degrees, 16)
            cardinal_point_32 = CompassUtils.get_cardinal_point(degrees, 32)
            print("GY271 heading %s / %s / %s (%s) - raw [x: %s, y: %s, z: %s, rel. tmp: %s]" % (
                cardinal_point_8, cardinal_point_16, cardinal_point_32, heading_str, raw[0], raw[1], raw[2], raw[3]))
            min_x = min(min_x, raw[0])
            min_y = min(min_y, raw[1])
            max_x = max(max_x, raw[0])
            max_y = max(max_y, raw[1])
            points.append(raw[0:3])
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    gy271_sensor.stop()
    print("GY271 calibration range [%s, %s, %s, %s] offset [%s, %s]" % (
        min_x, min_y, max_x, max_y, (max_x + min_x) * 0.5, (max_y + min_y) * 0.5))
    with io.open("/home/pi/calibration.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",", quotechar="\"")
        writer.writerow(["x", "y", "z"])
        for point in points:
            writer.writerow(point)


if __name__ == "__main__":
    config = {
       "location": {
           "lat": 52.038264,
           "lon": 8.4764692,
           "height": 111
       },
       "compass": {
           "calibration_offset": [803.0, 422.5],
           "calibration_norm_factor": [1606, 263 + 1108]
       }
    }
    light_sensor()
    # temperature_sensor(config)
    # compass_sensor(config)
    # camera_sensor = Camera()
    # target_path = tempfile.mkdtemp()
    # url = ""
    # headers = {
    #    # 'authorization': "Bearer {token}"
    # }
    # try:
    #    while True:
    #        print('Capture...')
    #        file_path = camera_sensor.snapshot(target_path)
    #        files = {'image': open(file_path, 'rb')}
    #        response = requests.request("POST", url, files=files, headers=headers)
    #        print('Captured', file_path)
    #        print('\t', response.status_code, response.text)
    #        time.sleep(60)
    # except KeyboardInterrupt:
    #    pass
    # shutil.rmtree(target_path)
    # camera_sensor.snapshot('/home/pi/')
    # rain_detector = RainDetector(24)
    # while True:
    #    print("Rain:", rain_detector.rain_detected)
    #    time.sleep(1)
    # gpio_extender = MCP23017(0x24)
    # while True:
    #    print("GPIO:", format(gpio_extender.read_ports(), '016b'))
    #    time.sleep(0.1)
