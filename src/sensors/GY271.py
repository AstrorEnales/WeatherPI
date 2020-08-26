from typing import Dict, Tuple

from api import NGDC
from wpiio.I2CDevice import I2CDevice

import math
import time


class GY271(I2CDevice):
    DEFAULT_DEVICE_I2C_ADDRESS = 0x0D

    # Each channel in range -32768 to 32767 muTesla
    REGISTER_DATA_X_LSB = 0x00  # read only
    REGISTER_DATA_X_MSB = 0x01  # read only
    REGISTER_DATA_Y_LSB = 0x02  # read only
    REGISTER_DATA_Y_MSB = 0x03  # read only
    REGISTER_DATA_Z_LSB = 0x04  # read only
    REGISTER_DATA_Z_MSB = 0x05  # read only
    REGISTER_DOR_OVL_DRDY = 0x06  # read only
    # only relative temperature value is accurate
    REGISTER_TEMP_OUT_LSB = 0x07  # read only
    REGISTER_TEMP_OUT_MSB = 0x08  # read only
    REGISTER_OSR_RNG_ODR_MODE = 0x09  # read/write
    REGISTER_SOFTRST_ROLPNT_INTENB = 0x0A  # read/write
    REGISTER_PERIOD_FBR = 0x0B  # read/write

    MODE_STANDBY = 0
    MODE_CONTINUOUS = 1

    DATA_RATE_10_HZ = 0
    DATA_RATE_50_HZ = 1
    DATA_RATE_100_HZ = 2
    DATA_RATE_200_HZ = 3

    DATA_RATE_HZ_MS_LOOKUP = {
        0: 1.0 / 10.0,
        1: 1.0 / 50.0,
        2: 1.0 / 100.0,
        3: 1.0 / 200.0
    }

    RANGE_2G = 0
    RANGE_8G = 1

    OVER_SAMPLE_RATIO_512 = 0
    OVER_SAMPLE_RATIO_256 = 1
    OVER_SAMPLE_RATIO_128 = 2
    OVER_SAMPLE_RATIO_64 = 3

    POINTER_ROLL_OVER_NORMAL = 0
    POINTER_ROLL_OVER_ENABLED = 1

    def __init__(self, config: Dict):
        super().__init__(GY271.DEFAULT_DEVICE_I2C_ADDRESS)
        self.config_data_rate = GY271.DATA_RATE_200_HZ
        self.config_range = GY271.RANGE_8G
        self.config_oversampling = GY271.OVER_SAMPLE_RATIO_128
        self.config_pointer_roll_over = GY271.POINTER_ROLL_OVER_NORMAL
        self.latitude = config["location"]["lat"]
        self.longitude = config["location"]["lon"]
        self.calibration_offset = config["compass"]["calibration_offset"]
        self.calibration_norm_factor = config["compass"]["calibration_norm_factor"]
        self.last_x = 0
        self.last_y = 0
        self.last_z = 0
        self.last_temperature = 0
        self.last_heading = 0
        self.last_heading_degrees = 0
        self.mode = GY271.MODE_STANDBY
        self.started = False
        self.last_measure_time = 0
        self.chip_id = self.get_chip_id()

    def get_chip_id(self) -> str or None:
        return None

    def is_chip_id_valid(self) -> bool:
        return True

    def start(self):
        if not self.started:
            self.mode = GY271.MODE_CONTINUOUS
            self.write_config()
            self.write_control_modes()
            self.started = True
            self.last_measure_time = self.get_now()
            self.wait_before_measure()
            self.read()

    def write_config(self):
        # disable interrupt pin
        config = (self.config_pointer_roll_over << 6) | 1
        self.write_register(GY271.REGISTER_PERIOD_FBR, 0x01)
        self.write_register(GY271.REGISTER_SOFTRST_ROLPNT_INTENB, config)

    def write_control_modes(self):
        control_modes = self.mode | (self.config_data_rate << 2) | (self.config_range << 4) | (
                self.config_oversampling << 6)
        self.write_register(GY271.REGISTER_OSR_RNG_ODR_MODE, control_modes)

    def wait_before_measure(self):
        time.sleep(0.1)

    def read(self):
        data = self.read_register(GY271.REGISTER_DATA_X_LSB, 9)
        self.last_x = int.from_bytes(data[0:2], byteorder='little', signed=True)
        self.last_y = int.from_bytes(data[2:4], byteorder='little', signed=True)
        self.last_z = int.from_bytes(data[4:6], byteorder='little', signed=True)
        self.last_temperature = int.from_bytes(data[7:9], byteorder='little', signed=True)

        self.last_x -= self.calibration_offset[0]
        self.last_y -= self.calibration_offset[1]
        self.last_x /= self.calibration_norm_factor[0]
        self.last_y /= self.calibration_norm_factor[1]

        declination_angle = NGDC.get_magnetic_declination(self.latitude, self.longitude) * math.pi / 180.0
        self.last_heading = math.atan2(self.last_y, self.last_x) + declination_angle
        if self.last_heading < 0.0:
            self.last_heading += 2 * math.pi
        if self.last_heading > 2 * math.pi:
            self.last_heading -= 2 * math.pi
        self.last_heading_degrees = self.last_heading * 180.0 / math.pi

    def stop(self):
        if self.mode != GY271.MODE_STANDBY:
            self.mode = GY271.MODE_STANDBY
            self.write_control_modes()
            self.started = False

    @property
    def raw(self) -> Tuple[float, float, float, float]:
        self.read_if_needed()
        return self.last_x, self.last_y, self.last_z, self.last_temperature

    def read_if_needed(self):
        if self.started and (self.get_now() - self.last_measure_time) > self.get_interval_time():
            self.last_measure_time = self.get_now()
            self.read()

    def get_interval_time(self):
        return GY271.DATA_RATE_HZ_MS_LOOKUP[self.config_data_rate]

    @property
    def x(self) -> float:
        self.read_if_needed()
        return self.last_x

    @property
    def y(self) -> float:
        self.read_if_needed()
        return self.last_y

    @property
    def z(self) -> float:
        self.read_if_needed()
        return self.last_z

    @property
    def temperature(self) -> float:
        self.read_if_needed()
        return self.last_temperature

    @property
    def heading(self) -> float:
        self.read_if_needed()
        return self.last_heading

    @property
    def heading_degrees(self) -> float:
        return self.last_heading_degrees
