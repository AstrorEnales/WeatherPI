from wpiio.I2CDevice import I2CDevice

import time


class SI1145(I2CDevice):
    DEFAULT_DEVICE_I2C_ADDRESS = 0x60

    REGISTER_PART_ID = 0x00
    REGISTER_REV_ID = 0x01
    REGISTER_SEQ_ID = 0x02
    REGISTER_INT_CFG = 0x03
    REGISTER_IRQ_ENABLE = 0x04
    REGISTER_HW_KEY = 0x07
    REGISTER_MEAS_RATE0 = 0x08
    REGISTER_MEAS_RATE1 = 0x09
    REGISTER_PS_RATE = 0x0A
    REGISTER_PS_LED21 = 0x0F
    REGISTER_PS_LED3 = 0x10
    REGISTER_UCOEF0 = 0x13
    REGISTER_UCOEF1 = 0x14
    REGISTER_UCOEF2 = 0x15
    REGISTER_UCOEF3 = 0x16
    REGISTER_PARAM_WR = 0x17
    REGISTER_COMMAND = 0x18
    REGISTER_RESPONSE = 0x20
    REGISTER_IRQ_STATUS = 0x21
    REGISTER_ALS_VIS_DATA0 = 0x22
    REGISTER_ALS_VIS_DATA1 = 0x23
    REGISTER_ALS_IR_DATA0 = 0x24
    REGISTER_ALS_IR_DATA1 = 0x25
    REGISTER_PS1_DATA0 = 0x26
    REGISTER_PS1_DATA1 = 0x27
    REGISTER_PS2_DATA0 = 0x28
    REGISTER_PS2_DATA1 = 0x29
    REGISTER_PS3_DATA0 = 0x2A
    REGISTER_PS3_DATA1 = 0x2B
    REGISTER_AUX_DATA0 = REGISTER_UVINDEX0 = 0x2C
    REGISTER_AUX_DATA1 = REGISTER_UVINDEX1 = 0x2D
    REGISTER_PARAM_RD = 0x2E
    REGISTER_CHIP_STAT = 0x30
    REGISTER_ANA_IN_KEY = 0x3B  # - 0x3E

    STATUS_SLEEP = 1
    STATUS_SUSPEND = 2
    STATUS_RUNNING = 4

    # COMMANDS
    PARAM_QUERY = 0x80
    PARAM_SET = 0xA0
    NOP = 0x0
    RESET = 0x01
    BUSADDR = 0x02
    PS_FORCE = 0x05
    ALS_FORCE = 0x06
    PSALS_FORCE = 0x07
    PS_PAUSE = 0x09
    ALS_PAUSE = 0x0A
    PSALS_PAUSE = 0xB
    PS_AUTO = 0x0D
    ALS_AUTO = 0x0E
    PSALS_AUTO = 0x0F
    GET_CAL = 0x12

    # Parameters
    PARAM_I2CADDR = 0x00
    PARAM_CHLIST = 0x01
    PARAM_CHLIST_ENUV = 0x80
    PARAM_CHLIST_ENAUX = 0x40
    PARAM_CHLIST_ENALSIR = 0x20
    PARAM_CHLIST_ENALSVIS = 0x10
    PARAM_CHLIST_ENPS1 = 0x01
    PARAM_CHLIST_ENPS2 = 0x02
    PARAM_CHLIST_ENPS3 = 0x04

    PARAM_PSLED12SEL = 0x02
    PARAM_PSLED12SEL_PS2NONE = 0x00
    PARAM_PSLED12SEL_PS2LED1 = 0x10
    PARAM_PSLED12SEL_PS2LED2 = 0x20
    PARAM_PSLED12SEL_PS2LED3 = 0x40
    PARAM_PSLED12SEL_PS1NONE = 0x00
    PARAM_PSLED12SEL_PS1LED1 = 0x01
    PARAM_PSLED12SEL_PS1LED2 = 0x02
    PARAM_PSLED12SEL_PS1LED3 = 0x04
    PARAM_PSLED3SEL = 0x03

    PARAM_PSENCODE = 0x05  # defaults to MSB=0
    PARAM_ALSENCODE = 0x06  # defaults to MSB=0

    PARAM_PS1ADCMUX = 0x07
    PARAM_PS2ADCMUX = 0x08
    PARAM_PS3ADCMUX = 0x09

    PARAM_PSADCOUNTER = 0x0A
    PARAM_PSADCGAIN = 0x0B
    PARAM_PSADCMISC = 0x0C

    PARAM_PSADCMISC_PSMODE_PROX = 0x04
    PARAM_PSADCMISC_PSMODE_RAW = 0x00

    PARAM_ALSIRADCMUX = 0x0E
    PARAM_AUXADCMUX = 0x0F

    PARAM_ALSVISADCOUNTER = 0x10
    PARAM_ALSVISADCGAIN = 0x11
    PARAM_ALSVISADCMISC = 0x12

    PARAM_ALSIRADCOUNTER = 0x1D
    PARAM_ALSIRADCGAIN = 0x1E
    PARAM_ALSIRADCMISC = 0x1F

    PARAM_ADCCOUNTER_511CLK = 0x70

    PARAM_ADCMUX_SMALLIR = 0x00
    PARAM_ADCMUX_VIS = 0x02
    PARAM_ADCMUX_LARGEIR = 0x03
    PARAM_ADCMUX_NO_DIODE = 0x06
    PARAM_ADCMUX_GRD_VOLT = 0x25
    PARAM_ADCMUX_TEMP = 0x65
    PARAM_ADCMUX_VDD = 0x75
    # PARAM_CHLIST_ENUV
    PARAM_ADCMISC_RANGE_NORM = 0x00
    PARAM_ADCMISC_RANGE_HI = 0x20

    def __init__(self):
        super().__init__(SI1145.DEFAULT_DEVICE_I2C_ADDRESS)
        time.sleep(0.25)
        self.chip_id = self.get_chip_id()
        if self.has_chip_meas_rate_bug():
            print("[WARN] SI1145 chip has meas_rate bug!")

        self.set_measure_rate(0)
        self.set_int_pin(False)
        time.sleep(0.01)
        self.set_command(SI1145.RESET)
        time.sleep(0.01)
        self.set_hardware_key()
        # Enable UV index measurement coefficients!
        self.write_register(SI1145.REGISTER_UCOEF0, 0x29)
        self.write_register(SI1145.REGISTER_UCOEF1, 0x89)
        self.write_register(SI1145.REGISTER_UCOEF2, 0x02)
        self.write_register(SI1145.REGISTER_UCOEF3, 0x00)
        self.set_parameter(SI1145.PARAM_CHLIST,
                           SI1145.PARAM_CHLIST_ENUV | SI1145.PARAM_CHLIST_ENALSIR | SI1145.PARAM_CHLIST_ENALSVIS)
        # /****************************** IR Sensor */
        self.set_parameter(SI1145.PARAM_ALSIRADCMUX, SI1145.PARAM_ADCMUX_SMALLIR)
        # Fastest clocks, clock div 1 (integration time)
        self.set_parameter(SI1145.PARAM_ALSIRADCGAIN, 0)
        # Take 511 clocks to recover
        self.set_parameter(SI1145.PARAM_ALSIRADCOUNTER, SI1145.PARAM_ADCCOUNTER_511CLK)
        # in high range mode
        self.set_parameter(SI1145.PARAM_ALSIRADCMISC, SI1145.PARAM_ADCMISC_RANGE_HI)
        # /****************************** Visible Sensor */
        # fastest clocks, clock div 1 (integration time)
        self.set_parameter(SI1145.PARAM_ALSVISADCGAIN, 0)
        # Take 511 clocks to recover
        self.set_parameter(SI1145.PARAM_ALSVISADCOUNTER, SI1145.PARAM_ADCCOUNTER_511CLK)
        # in high signal range mode divides gain by 14.5
        self.set_parameter(SI1145.PARAM_ALSVISADCMISC, SI1145.PARAM_ADCMISC_RANGE_HI)

        # measurement rate for auto
        self.set_measure_rate(0xFF)  # 255 * 31.25 uS = 7.9 ms
        # auto run
        self.set_command(SI1145.ALS_FORCE)

    def get_chip_id(self) -> str or None:
        return self.read_register(SI1145.REGISTER_PART_ID, 1)[0]

    def is_chip_id_valid(self) -> bool:
        return self.chip_id == 0x45

    def has_chip_meas_rate_bug(self):
        return self.read_register(SI1145.REGISTER_SEQ_ID, 1)[0] == 0x01

    def set_int_pin(self, enabled: bool):
        # 0: INT pin is never driven
        # 1: INT pin driven low whenever an IRQ_STATUS and its corresponding IRQ_ENABLE bits match
        self.write_register(SI1145.REGISTER_INT_CFG, 1 if enabled else 0)

    def set_irq_enable(self, als_interrupt_enabled: bool, ps1_interrupt_enabled: bool, ps2_interrupt_enabled: bool,
                       ps3_interrupt_enabled: bool):
        als_shifted_bit = (1 if als_interrupt_enabled else 0)
        ps1_shifted_but = (1 if ps1_interrupt_enabled else 0) << 2
        ps2_shifted_but = (1 if ps2_interrupt_enabled else 0) << 3
        ps3_shifted_but = (1 if ps3_interrupt_enabled else 0) << 4
        data = als_shifted_bit | ps1_shifted_but | ps2_shifted_but | ps3_shifted_but
        self.write_register(SI1145.REGISTER_IRQ_ENABLE, data)

    def set_hardware_key(self):
        self.write_register(SI1145.REGISTER_HW_KEY, 0x17)

    def get_measure_rate(self):
        # The 16-bit value, when multiplied by 31.25 us, represents the time duration between wake-up periods where
        # measurements are made. Once the device wakes up, all measurements specified in CHLIST are made.
        # output as seconds
        return self.read_register_short(SI1145.REGISTER_MEAS_RATE0) * 31.25 * 0.000001

    def set_measure_rate(self, rate: int):
        self.write_register_short(SI1145.REGISTER_MEAS_RATE0, rate)

    def set_ps_led(self):
        # LED3_I Represents the irLED current sunk by the LED3 pin during a PS measurement.
        # LED1_I Represents the irLED current sunk by the LED1 pin during a PS measurement.
        # LED2_I Represents the irLED current sunk by the LED2 pin during a PS measurement.
        # On the Si1145, LED2_I and LED3_I bits must be set to zero.
        # LED3_I, LED2_I, and LED1_I current encoded as follows:
        #  0 - 0000: No current
        #  1 - 0001: Minimum current
        # 15 - 1111: Maximum current
        # Refer to Table 2, "Performance Characteristics", on page 5 for LED current values.
        self.write_register_short(SI1145.REGISTER_PS_LED21, 0)

    def set_parameter(self, parameter: int, value: int):
        # Mailbox register for passing parameters from the host to the sequencer.
        self.write_register(SI1145.REGISTER_PARAM_WR, value)
        self.set_command(SI1145.PARAM_SET | parameter)

    def get_parameter(self, parameter: int):
        # Mailbox register for passing parameters from the sequencer to the host.
        self.set_command(SI1145.PARAM_QUERY | parameter)
        return self.read_register(SI1145.REGISTER_PARAM_RD, 1)[0]

    def set_command(self, command: int):
        # The COMMAND Register is the primary mailbox register into the internal sequencer.
        # Writing to the COMMAND register is the only I2C operation that wakes the device from standby mode.
        self.write_register(SI1145.REGISTER_COMMAND, command)

    def get_response(self):
        # The Response register is used in conjunction with command processing. When an error is encountered, the
        # response register will be loaded with an error code. All error codes will have the MSB is set.
        # The error code is retained until a RESET or NOP command is received by the sequencer. Other commands other
        # than RESET or NOP will be ignored. However, any autonomous operation in progress continues normal operation
        # despite any error.
        # 0x00–0x0F: No Error. Bits 3:0 form an incrementing roll-over counter. The roll over counter in bit 3:0
        # increments when a command has been executed by the Si114x. Once autonomous measurements have started, the
        # execution timing of any command becomes non-deterministic since a measurement could be in progress when the
        # COMMAND register is written. The host software must make use of the rollover counter to ensure that commands
        # are processed.
        # 0x80: Invalid Command Encountered during command processing
        # 0x88: ADC Overflow encountered during PS1 measurement
        # 0x89: ADC Overflow encountered during PS2 measurement
        # 0x8A: ADC Overflow encountered during PS3 measurement
        # 0x8C: ADC Overflow encountered during ALS-VIS measurement
        # 0x8D: ADC Overflow encountered during ALS-IR measurement
        # 0x8E: ADC Overflow encountered during AUX measurement
        return self.read_register(SI1145.REGISTER_RESPONSE, 1)[0]

    def get_irq_status(self):
        data = self.read_register(SI1145.REGISTER_IRQ_STATUS, 1)[0]
        # Interrupt Status
        cmd_int = (data >> 5) & 1 == 1
        ps3_int = (data >> 4) & 1 == 1
        ps2_int = (data >> 3) & 1 == 1
        ps1_int = (data >> 2) & 1 == 1
        als_int = data & 3 == 1
        return als_int, ps1_int, ps2_int, ps3_int, cmd_int

    def get_als_vis_data(self):
        # Once autonomous measurements have started, this register must be read after INT has asserted but before the
        # next measurement is made. Refer to "AN498: Si114x Designer's Guide", section "5.6.2 Host Interrupt Latency"
        return self.read_register_short(SI1145.REGISTER_ALS_VIS_DATA0)

    def get_als_ir_data(self):
        # Once autonomous measurements have started, this register must be read after INT has asserted but before the
        # next measurement is made. Refer to "AN498: Si114x Designer's Guide", section "5.6.2 Host Interrupt Latency"
        return self.read_register_short(SI1145.REGISTER_ALS_IR_DATA0)

    def get_ps1_data(self):
        # Once autonomous measurements have started, this register must be read after INT has asserted but before the
        # next measurement is made. Refer to "AN498: Si114x Designer's Guide", section "5.6.2 Host Interrupt Latency"
        return self.read_register_short(SI1145.REGISTER_PS1_DATA0)

    def get_ps2_data(self):
        # Once autonomous measurements have started, this register must be read after INT has asserted but before the
        # next measurement is made. Refer to "AN498: Si114x Designer's Guide", section "5.6.2 Host Interrupt Latency"
        return self.read_register_short(SI1145.REGISTER_PS2_DATA0)

    def get_ps3_data(self):
        # Once autonomous measurements have started, this register must be read after INT has asserted but before the
        # next measurement is made. Refer to "AN498: Si114x Designer's Guide", section "5.6.2 Host Interrupt Latency"
        return self.read_register_short(SI1145.REGISTER_PS3_DATA0)

    def get_aux_data(self):
        # Once autonomous measurements have started, this register must be read after INT has asserted but before the
        # next measurement is made. Refer to "AN498: Si114x Designer's Guide", section "5.6.2 Host Interrupt Latency"
        return self.read_register_short(SI1145.REGISTER_AUX_DATA0)

    def get_status(self):
        return self.read_register(SI1145.REGISTER_CHIP_STAT, 1)[0]

    def get_ana_in_key(self):
        return self.read_register(SI1145.REGISTER_ANA_IN_KEY, 4)
