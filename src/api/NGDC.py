import wpiio
import os
import math
import json
import datetime
import urllib.parse
import urllib.request
import utils.AppUtils

API_URL = "http://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"

last_loaded_cache = None


def get_magnetic_declination(lat: float, lon: float) -> float:
    global last_loaded_cache
    now = datetime.datetime.now()
    update = True
    data = None
    appdata_path = utils.AppUtils.get_appdata_path()
    if not os.path.exists(appdata_path):
        os.mkdir(appdata_path)
    cache_file_path = os.path.join(appdata_path, "declinationData.json")
    if last_loaded_cache is not None:
        data = last_loaded_cache
    elif os.path.isfile(cache_file_path):
        with wpiio.open(cache_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_loaded_cache = data
    if data is not None:
        years, year_fraction = divmod(data["result"][0]["date"], 1)
        days = round(year_fraction * 365.2425)
        old_lat = data["result"][0]["latitude"]
        old_lon = data["result"][0]["longitude"]
        if math.floor(lat * 10000) == math.floor(old_lat * 10000) and math.floor(lon * 10000) == math.floor(
                old_lon * 10000) and years == now.year and days >= now.timetuple().tm_yday - 7:
            update = False
    if update:
        print("Updating magnetic declination for location [%s, %s]" % (lat, lon))
        params = urllib.parse.urlencode({'lat1': lat, 'lon1': lon, 'resultFormat': 'json', 'startMonth': now.month})
        with urllib.request.urlopen("%s?%s" % (API_URL, params)) as f:
            data = json.load(f)
            last_loaded_cache = data
        with wpiio.open(cache_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print("\tNew magnetic declination is %s" % data["result"][0]["declination"])
    declination = data["result"][0]["declination"]
    return declination


if __name__ == "__main__":
    print(get_magnetic_declination(52.038264, 8.4764692))
