from wpiio.I2CDevice import I2CDevice


class MCP23017(I2CDevice):
    DEFAULT_DEVICE_I2C_ADDRESS = 0x20

    # Register are mapped assuming IOCON.BANK = 0
    REGISTER_IODIRA = 0x00
    REGISTER_IODIRB = 0x01
    REGISTER_IPOLA = 0x02
    REGISTER_IPOLB = 0x03
    REGISTER_GPINTENA = 0x04
    REGISTER_GPINTENB = 0x05
    REGISTER_DEFVALA = 0x06
    REGISTER_DEFVALB = 0x07
    REGISTER_INTCONA = 0x08
    REGISTER_INTCONB = 0x09
    REGISTER_IOCON = 0x0A
    REGISTER_GPPUA = 0x0C
    REGISTER_GPPUB = 0x0D
    REGISTER_INTFA = 0x0E
    REGISTER_INTFB = 0x0F
    REGISTER_INTCAPA = 0x10
    REGISTER_INTCAPB = 0x11
    REGISTER_GPIOA = 0x12
    REGISTER_GPIOB = 0x13
    REGISTER_OLATA = 0x14
    REGISTER_OLATB = 0x15

    def __init__(self, i2c_address: int = DEFAULT_DEVICE_I2C_ADDRESS):
        super().__init__(i2c_address)
        # https://electronics.stackexchange.com/questions/325916/mcp23017-detecting-state-of-iocon-bank-bit-after-mcu-reset
        # Assume IOCON.BANK = 1
        value = self.read_register(MCP23017.REGISTER_GPINTENB, 1)[0]
        value = value & 0x7F
        self.write_register(MCP23017.REGISTER_GPINTENB, value)
        self.write_register(MCP23017.REGISTER_IOCON, (1 << 7) | (1 << 1))
        self.write_register(MCP23017.REGISTER_GPINTENA, 0x0)
        self.write_register(MCP23017.REGISTER_GPINTENB, 0x0)
        self.write_register(MCP23017.REGISTER_INTCONA, 0xFF)
        self.write_register(MCP23017.REGISTER_INTCONB, 0xFF)
        self.write_register(MCP23017.REGISTER_DEFVALA, 0x0)
        self.write_register(MCP23017.REGISTER_DEFVALB, 0x0)
        self.write_register(MCP23017.REGISTER_INTFA, 0x0)
        self.write_register(MCP23017.REGISTER_INTFB, 0x0)
        self.write_register(MCP23017.REGISTER_GPPUA, 0xFF)
        self.write_register(MCP23017.REGISTER_GPPUB, 0xFF)
        self.set_pins_input(*([True] * 16))
        self.set_pins_input(*([False] * 16))

    def get_chip_id(self) -> str or None:
        pass

    def is_chip_id_valid(self) -> bool:
        pass

    def set_pins_input(self, pin0: bool, pin1: bool, pin2: bool, pin3: bool, pin4: bool, pin5: bool, pin6: bool,
                       pin7: bool, pin8: bool, pin9: bool, pin10: bool, pin11: bool, pin12: bool, pin13: bool,
                       pin14: bool, pin15: bool):
        bits = [1 if x else 0 for x in
                [pin15, pin14, pin13, pin12, pin11, pin10, pin9, pin8, pin7, pin6, pin5, pin4, pin3, pin2, pin1, pin0]]
        value = int(''.join([str(x) for x in bits]), 2)
        self.write_register(MCP23017.REGISTER_IODIRA, value & 0xFF)
        self.write_register(MCP23017.REGISTER_IODIRB, (value >> 8) & 0xFF)

    def set_pins_inverted(self, pin0: bool, pin1: bool, pin2: bool, pin3: bool, pin4: bool, pin5: bool, pin6: bool,
                          pin7: bool, pin8: bool, pin9: bool, pin10: bool, pin11: bool, pin12: bool, pin13: bool,
                          pin14: bool, pin15: bool):
        bits = [1 if x else 0 for x in
                [pin15, pin14, pin13, pin12, pin11, pin10, pin9, pin8, pin7, pin6, pin5, pin4, pin3, pin2, pin1, pin0]]
        value = int(''.join([str(x) for x in bits]), 2)
        self.write_register(MCP23017.REGISTER_IPOLA, value & 0xFF)
        self.write_register(MCP23017.REGISTER_IPOLB, (value >> 8) & 0xFF)

    def read_ports(self):
        value = self.read_register(MCP23017.REGISTER_GPIOA, 2)
        return (value[1] << 8) | value[0]

    def read_port(self, index: int):
        if index < 8:
            value = self.read_register(MCP23017.REGISTER_GPIOA, 1)[0]
            return (value >> index) & 0x01
        else:
            value = self.read_register(MCP23017.REGISTER_GPIOB, 1)[0]
            return (value >> (index - 8)) & 0x01
