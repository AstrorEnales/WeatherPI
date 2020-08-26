from datetime import datetime


class Sensor:
    def __init__(self):
        pass

    def get_now(self):
        return datetime.now().timestamp()
