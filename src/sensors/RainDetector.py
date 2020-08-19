from sensors.DigitalOnOffSensor import DigitalOnOffSensor


class RainDetector(DigitalOnOffSensor):
    def __init__(self, pin: int):
        super().__init__(pin, True)

    @property
    def rain_detected(self) -> bool:
        return self.active
