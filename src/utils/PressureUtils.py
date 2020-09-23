import math


def adjust_to_mean_sea_level(pressure: float, height: float, latitude: float, temperature: float) -> float:
    """
    http://www.wind101.net/sea-level-pressure-advanced/sea-level-pressure-advanced.html
    :param pressure:
    :param height:
    :param latitude:
    :param temperature:
    :return:
    """
    # delta height from upper and lower (mean sea level) station
    dZ = height - 0
    # mean pressure of aqueous vapour in the air column (hPa)
    e = math.pow(10, 7.5 * temperature / (237.3 + temperature)) * 6.1078
    # mean barometric pressure of the air column (hPa)
    b = 1013.25
    # Barometric constant (hypsometric constant) K=delta.bldelta1.M (18400 m)
    K = 18400.0
    # coefficient of thermal expansion of the air
    a = 0.0037
    # constant depending on the figure of the earth
    k = 0.0026
    # Correction for atmospheric temperature
    cor_temperature = K * (1 + a * temperature)
    # Correction for humidity
    cor_humidity = 1 / (1 - 0.378 * (e / b))
    # Correction for asphericity of the earth
    cor_e = 1 / (1 - (k * math.cos(2 * latitude)))
    p0c = math.pow(10, dZ / (cor_temperature * cor_humidity * cor_e) + math.log10(pressure))
    return round(p0c * 10000.0) / 10000.0
