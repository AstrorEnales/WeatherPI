from unittest import TestCase

from utils import CompassUtils


class TestCompassUtils(TestCase):
    def test_get_cardinal_point(self):
        for divisions in [4, 8, 16, 32]:
            self.assertEquals(CompassUtils.get_cardinal_point(0, divisions), "N")
            self.assertEquals(CompassUtils.get_cardinal_point(90, divisions), "O")
            self.assertEquals(CompassUtils.get_cardinal_point(180, divisions), "S")
            self.assertEquals(CompassUtils.get_cardinal_point(270, divisions), "W")
        for divisions in [8, 16, 32]:
            self.assertEquals(CompassUtils.get_cardinal_point(45, divisions), "NO")
            self.assertEquals(CompassUtils.get_cardinal_point(135, divisions), "SO")
            self.assertEquals(CompassUtils.get_cardinal_point(225, divisions), "SW")
            self.assertEquals(CompassUtils.get_cardinal_point(315, divisions), "NW")

    def test_degrees_to_string(self):
        self.assertEquals(CompassUtils.degrees_to_string(2.82), "2° 49'")

    def test_degree_decimal_to_degree_minutes(self):
        self.assertEquals(CompassUtils.degree_decimal_to_degree_minutes(2.82), (2, 49))

    def test_degree_minutes_to_string(self):
        self.assertEquals(CompassUtils.degree_minutes_to_string(2, 49), "2° 49'")
