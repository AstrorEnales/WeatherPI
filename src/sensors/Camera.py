from picamera import PiCamera
from time import sleep
import datetime
import os.path


class Camera:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.led = False
        self.camera.resolution = (1296, 972)

    def snapshot(self, target_path: str) -> str:
        self.camera.start_preview()
        self.camera.exposure_mode = 'auto'  # self.get_exposure_by_time_of_day()
        sleep(5)
        timestamp = datetime.datetime.now().replace(microsecond=0).astimezone().isoformat()
        file_path = os.path.join(target_path, timestamp + '_ldr_1.png')
        self.camera.capture(file_path, format='png')
        self.camera.stop_preview()
        return file_path

    @staticmethod
    def get_exposure_by_time_of_day():
        now = datetime.datetime.now()
        # TODO: test 'night' or 'verylong'
        return 'night' if now.hour >= 22 or now.hour < 4 else 'auto'
