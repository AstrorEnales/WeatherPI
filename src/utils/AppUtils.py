import sys
from os import path, environ

APP_NAME = "WeatherPI"


def get_appdata_path() -> str:
    if sys.platform == 'win32':
        return path.join(environ['APPDATA'], APP_NAME)
    # if sys.platform == 'darwin':
    else:
        return path.expanduser(path.join("~", "." + APP_NAME))
