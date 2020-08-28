from wpiio.I2CDevice import I2CDevice
import time


class BMP280(I2CDevice):
    DEFAULT_DEVICE_I2C_ADDRESS = 0x76

    REGISTER_TEMP_XLSB = 0xFC
    REGISTER_TEMP_LSB = 0xFB
    REGISTER_TEMP_MSB = 0xFA
    REGISTER_PRESS_XLSB = 0xF9
    REGISTER_PRESS_LSB = 0xF8
    REGISTER_PRESS_MSB = 0xF7
    REGISTER_CONFIG = 0xF5
    REGISTER_CTRL_MEAS = 0xF4
    REGISTER_STATUS = 0xF3
    REGISTER_RESET = 0xE0
    REGISTER_ID = 0xD0
    REGISTER_CALIBRATION_00 = 0x88
    REGISTER_CALIBRATION_01 = 0x89
    REGISTER_CALIBRATION_02 = 0x8A
    REGISTER_CALIBRATION_03 = 0x8B
    REGISTER_CALIBRATION_04 = 0x8C
    REGISTER_CALIBRATION_05 = 0x8D
    REGISTER_CALIBRATION_06 = 0x8E
    REGISTER_CALIBRATION_07 = 0x8F
    REGISTER_CALIBRATION_08 = 0x90
    REGISTER_CALIBRATION_09 = 0x91
    REGISTER_CALIBRATION_10 = 0x92
    REGISTER_CALIBRATION_11 = 0x93
    REGISTER_CALIBRATION_12 = 0x94
    REGISTER_CALIBRATION_13 = 0x95
    REGISTER_CALIBRATION_14 = 0x96
    REGISTER_CALIBRATION_15 = 0x97
    REGISTER_CALIBRATION_16 = 0x98
    REGISTER_CALIBRATION_17 = 0x99
    REGISTER_CALIBRATION_18 = 0x9A
    REGISTER_CALIBRATION_19 = 0x9B
    REGISTER_CALIBRATION_20 = 0x9C
    REGISTER_CALIBRATION_21 = 0x9D
    REGISTER_CALIBRATION_22 = 0x9E
    REGISTER_CALIBRATION_23 = 0x9F
    REGISTER_CALIBRATION_24 = 0xA0
    REGISTER_CALIBRATION_25 = 0xA1

    OVERSAMPLE_SKIPPED = 0
    OVERSAMPLE_X1 = 1
    OVERSAMPLE_X2 = 2
    OVERSAMPLE_X4 = 3
    OVERSAMPLE_X8 = 4
    OVERSAMPLE_X16 = 5

    CONFIG_STANDBY_0_5 = 0
    CONFIG_STANDBY_62_5 = 1
    CONFIG_STANDBY_125 = 2
    CONFIG_STANDBY_250 = 3
    CONFIG_STANDBY_500 = 4
    CONFIG_STANDBY_1000 = 5
    CONFIG_STANDBY_2000 = 6
    CONFIG_STANDBY_4000 = 7

    CONFIG_FILTER_OFF = 0
    CONFIG_FILTER_2 = 1
    CONFIG_FILTER_4 = 2
    CONFIG_FILTER_8 = 3
    CONFIG_FILTER_16 = 4

    CONFIG_SPI_OFF = 0
    CONFIG_SPI_ON = 1

    # Sleep mode: no operation, all registers accessible, lowest power, selected after startup
    CONTROL_MODE_SLEEP = 0
    # Forced mode: perform one measurement, store results and return to sleep mode
    CONTROL_MODE_FORCED = 1
    # Normal mode: perpetual cycling of measurements and inactive periods
    CONTROL_MODE_NORMAL = 3

    def __init__(self):
        super().__init__(BMP280.DEFAULT_DEVICE_I2C_ADDRESS)
        self.config_standby_sec_lookup = {
            0: 0.5 / 1000.0,  # CONFIG_STANDBY_0_5
            1: 62.5 / 1000.0,  # CONFIG_STANDBY_62_5
            2: 125.0 / 1000.0,  # CONFIG_STANDBY_125
            3: 250.0 / 1000.0,  # CONFIG_STANDBY_250
            4: 500.0 / 1000.0,  # CONFIG_STANDBY_500
            5: 1000.0 / 1000.0,  # CONFIG_STANDBY_1000
            6: 2000.0 / 1000.0,  # CONFIG_STANDBY_2000
            7: 4000.0 / 1000.0  # CONFIG_STANDBY_4000
        }
        self.config_standby = BMP280.CONFIG_STANDBY_0_5
        self.config_filter = BMP280.CONFIG_FILTER_2
        self.config_spi = BMP280.CONFIG_SPI_OFF
        self.mode = BMP280.CONTROL_MODE_SLEEP
        self.oversample_temperature = BMP280.OVERSAMPLE_X2
        self.oversample_pressure = BMP280.OVERSAMPLE_X2
        self.dig_T1 = 0
        self.dig_T2 = 0
        self.dig_T3 = 0
        self.dig_P1 = 0
        self.dig_P2 = 0
        self.dig_P3 = 0
        self.dig_P4 = 0
        self.dig_P5 = 0
        self.dig_P6 = 0
        self.dig_P7 = 0
        self.dig_P8 = 0
        self.dig_P9 = 0
        self.dig_H1 = 0
        self.last_temperature = 0.0
        self.last_pressure = 0.0
        self.started = False
        self.last_measure_time = 0
        self.chip_id = self.get_chip_id()
        self.read_calibration()
        time.sleep(0.002)
        self.write_config()

    def get_chip_id(self) -> str or None:
        return self.read_register(BMP280.REGISTER_ID, 1)[0]

    def is_chip_id_valid(self) -> bool:
        return self.chip_id == 0x58

    def read_calibration(self):
        # Read blocks of calibration data from EEPROM
        cal1 = self.read_register(BMP280.REGISTER_CALIBRATION_00, 24)
        cal2 = self.read_register(BMP280.REGISTER_CALIBRATION_25, 1)
        self.dig_T1 = self.get_ushort(cal1, 0)
        self.dig_T2 = self.get_short(cal1, 2)
        self.dig_T3 = self.get_short(cal1, 4)
        self.dig_P1 = self.get_ushort(cal1, 6)
        self.dig_P2 = self.get_short(cal1, 8)
        self.dig_P3 = self.get_short(cal1, 10)
        self.dig_P4 = self.get_short(cal1, 12)
        self.dig_P5 = self.get_short(cal1, 14)
        self.dig_P6 = self.get_short(cal1, 16)
        self.dig_P7 = self.get_short(cal1, 18)
        self.dig_P8 = self.get_short(cal1, 20)
        self.dig_P9 = self.get_short(cal1, 22)
        self.dig_H1 = self.get_uchar(cal2, 0)

    def write_config(self):
        config = self.config_standby << 5 | self.config_filter << 2 | self.config_spi
        self.write_register(BMP280.REGISTER_CONFIG, config)

    def start(self, mode: int):
        if not self.started and mode != BMP280.CONTROL_MODE_SLEEP:
            self.mode = mode
            self.write_control_modes()
            if mode == BMP280.CONTROL_MODE_NORMAL:
                self.started = True
            self.last_measure_time = self.get_now()
            self.wait_before_measure()
            self.read()
            print('[BME280] Max measure time: %s ms' % (self.get_max_measure_time() * 1000))
            print('[BME280] Interval time: %s ms' % (self.get_interval_time() * 1000))

    def write_control_modes(self):
        time.sleep(0.002)
        control_modes = self.oversample_temperature << 5 | self.oversample_pressure << 2 | self.mode
        self.write_register(BMP280.REGISTER_CTRL_MEAS, control_modes)

    def wait_before_measure(self):
        time.sleep(self.get_max_measure_time())

    def get_max_measure_time(self):
        # measure time in ms (Appendix B: Measurement time and current calculation)
        return (1.25 + (2.3 * self.oversample_temperature) + ((2.3 * self.oversample_pressure) + 0.575)) / 1000.0

    def get_interval_time(self):
        return self.get_max_measure_time() + self.config_standby_sec_lookup[self.config_standby]

    def stop(self):
        if self.mode != BMP280.CONTROL_MODE_SLEEP:
            self.mode = BMP280.CONTROL_MODE_SLEEP
            self.write_control_modes()
            self.started = False

    def read(self):
        raw_pressure, raw_temperature = self.read_raw_values()
        self.last_temperature, t_fine = self.refine_temperature(raw_temperature)
        self.last_pressure = self.refine_pressure(raw_pressure, t_fine)

    def read_raw_values(self) -> (int, int, int):
        # Read 6 bytes starting at pressure MSB up to humidity LSB
        data = self.read_register(BMP280.REGISTER_PRESS_MSB, 6)
        raw_pressure = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        raw_temperature = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return raw_pressure, raw_temperature

    def refine_temperature(self, raw_temperature: int) -> (float, int):
        var1 = (((raw_temperature >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var3 = (raw_temperature >> 4) - self.dig_T1
        var2 = (((var3 * var3) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        temperature = float(((t_fine * 5) + 128) >> 8)
        return temperature / 100.0, t_fine

    def refine_pressure(self, raw_pressure: int, t_fine: int) -> float:
        # Refine pressure and adjust for temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        if var1 == 0:
            pressure = 0.0
        else:
            pressure = 1048576.0 - raw_pressure
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = self.dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * self.dig_P8 / 32768.0
            pressure = pressure + (var1 + var2 + self.dig_P7) / 16.0
        return pressure / 100.0

    @property
    def temperature(self) -> float:
        self.read_if_needed()
        return self.last_temperature

    def read_if_needed(self):
        if self.mode == BMP280.CONTROL_MODE_NORMAL and self.started and (
                self.get_now() - self.last_measure_time) > self.get_interval_time():
            self.last_measure_time = self.get_now()
            self.read()

    @property
    def pressure(self) -> float:
        self.read_if_needed()
        return self.last_pressure
