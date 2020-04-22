from ctypes import c_short
from typing import List

import smbus2


class Sensor:
    def __init__(self, i2c_address: int):
        self.i2c_address = i2c_address
        # Rev 1 Pi uses bus 0
        # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
        self.bus = smbus2.SMBus(1)

    @staticmethod
    def get_short(data: List, index: int):
        # return two bytes from data as a signed 16-bit value
        return c_short((data[index + 1] << 8) + data[index]).value

    @staticmethod
    def get_ushort(data: List, index: int):
        # return two bytes from data as an unsigned 16-bit value
        return (data[index + 1] << 8) + data[index]

    @staticmethod
    def get_char(data: List, index: int):
        # return one byte from data as a signed char
        return data[index] - 256 if data[index] > 127 else data[index]

    @staticmethod
    def get_uchar(data: List, index: int):
        # return one byte from data as an unsigned char
        return data[index] & 0xFF

    def read_register(self, register: int, num_bytes: int) -> List:
        return self.bus.read_i2c_block_data(self.i2c_address, register, num_bytes)

    def write_register(self, register: int, data: int):
        self.bus.write_byte_data(self.i2c_address, register, data)
