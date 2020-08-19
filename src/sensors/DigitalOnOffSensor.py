from gpiozero import InputDevice

from sensors.Sensor import Sensor


class DigitalOnOffSensor(Sensor):
    def __init__(self, pin: int, inverted: bool = False):
        super().__init__()
        self.inverted = inverted
        self.device = InputDevice(pin, pull_up=False)

    @property
    def active(self) -> bool:
        return not self.device.is_active if self.inverted else self.device.is_active
