import math
from typing import Tuple

data = {
    4: {
        "angle_step": 360.0 / 4.0,
        "angle_step_offset": 360.0 / 8.0,
        "names": ["N", "O", "S", "W"]
    },
    8: {
        "angle_step": 360.0 / 8.0,
        "angle_step_offset": 360.0 / 16.0,
        "names": ["N", "NO", "O", "SO", "S", "SW", "W", "NW"]
    },
    16: {
        "angle_step": 360.0 / 16.0,
        "angle_step_offset": 360.0 / 32.0,
        "names": ["N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    },
    32: {
        "angle_step": 360.0 / 32.0,
        "angle_step_offset": 360.0 / 64.0,
        "names": [
            "N", "NzO", "NNO", "NOzN", "NO", "NOzO", "ONO", "OzN",
            "O", "OzS", "OSO", "SOzO", "SO", "SOzS", "SSO", "SzO",
            "S", "SzW", "SSW", "SWzS", "SW", "SWzW", "WSW", "WzS",
            "W", "WzN", "WNW", "NWzW", "NW", "NWzN", "NNW", "NzW"
        ]
    }
}


def get_cardinal_point(degrees: float, divisions: int = 8) -> str:
    index = math.floor(((degrees + data[divisions]["angle_step_offset"]) % 360.0) / data[divisions]["angle_step"])
    return data[divisions]["names"][index]


def degrees_to_string(degrees: float) -> str:
    return degree_minutes_to_string(*degree_decimal_to_degree_minutes(degrees))


def degree_decimal_to_degree_minutes(degrees: float) -> Tuple[int, int]:
    (degrees, degrees_fraction) = divmod(degrees, 1)
    minutes = round(degrees_fraction * 60.0)
    return int(degrees), minutes


def degree_minutes_to_string(degrees: int, minutes: int) -> str:
    return "%s° %s'" % (degrees, minutes)
