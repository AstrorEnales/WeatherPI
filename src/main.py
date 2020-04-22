#!/usr/bin/env python3
from sensors.BME280 import BME280

if __name__ == "__main__":
    bme280_sensor = BME280()
    print("Chip id: %s, valid: %s" % (hex(bme280_sensor.chip_id), bme280_sensor.is_chip_id_valid()))
    bme280_sensor.start(BME280.CONTROL_MODE_FORCED)
    print("Temperature : ", bme280_sensor.temperature, "°C")
    print("Pressure : ", bme280_sensor.pressure, "hPa")
    print("Humidity : ", bme280_sensor.humidity, "%")
