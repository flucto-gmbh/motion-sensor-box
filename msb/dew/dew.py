import board
import numpy as np
from adafruit_lps2x import LPS22, Rate
from adafruit_shtc3 import SHTC3


def _make_temperature_and_rel_humidity():
    i2c = board.I2C()
    sht = SHTC3(i2c)  # temperature / humidity sensor;  I2C adress: 0x70

    def _temperature_and_rel_humidity():
        temp, rel_hum = sht.measurements
        return {
            "temperature": temp,
            "relative_humidity": rel_hum,
        }

    return _temperature_and_rel_humidity


temperature_and_rel_humidity = _make_temperature_and_rel_humidity()


def _make_air_pressure():
    i2c = board.I2C()
    lps = LPS22(i2c, 0x5C)  # pressure sensor; I2C adress: 0x5C
    lps.data_rate = Rate.LSP22_RATE_10_HZ

    def _air_pressure():
        return {"air_pressure": lps.pressure}

    return _air_pressure


air_pressure = _make_air_pressure()


def _water_vapour_saturation_pressure(temperature):
    # https://web.archive.org/web/20200212215746im_/https://www.vaisala.com/en/system/files?file=documents/Humidity_Conversion_Formulas_B210973EN.pdf
    T_c = 647.096  # K, Critical temperature
    P_c = 220_640  # hPa, Critical pressure
    coeffs = np.array(
        [-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502]
    )
    exponents = np.array([1, 1.5, 3, 3.5, 4, 7.5])
    temp_kelvin = 273.15 + temperature

    tau = 1 - T_c / temp_kelvin  # eq. (2)

    # eq. (3)
    tau_exp = np.power(tau, exponents)
    term_right_side = T_c / temp_kelvin * np.sum(coeffs * tau_exp)
    P_ws = P_c * np.exp(term_right_side)
    return P_ws


def _eq_6_constants(temp):
    # coefficients for eq. (6) in
    # https://web.archive.org/web/20200212215746im_/https://www.vaisala.com/en/system/files?file=documents/Humidity_Conversion_Formulas_B210973EN.pdf
    if -20 <= temp < 50:
        A, m, T_n = 6.116441, 7.591386, 240.7263
    elif 50 <= temp < 100:
        A, m, T_n = 6.004918, 7.337936, 229.3975
    else:
        raise NotImplementedError("Temperature of {temp} °C is not supported.")
    return A, m, T_n


def _water_vapour_saturation_pressure_simple(temp):
    # https://web.archive.org/web/20200212215746im_/https://www.vaisala.com/en/system/files?file=documents/Humidity_Conversion_Formulas_B210973EN.pdf
    # eq. (6)
    A, m, T_n = _eq_6_constants(temp)
    exponent = m * temp / (temp + T_n)
    P_ws = A * 10**exponent
    return P_ws


def estimate_dew_point(temperature, relative_humidity, use_simple=False):
    # source: https://web.archive.org/web/20200212215746im_/https://www.vaisala.com/en/system/files?file=documents/Humidity_Conversion_Formulas_B210973EN.pdf
    if use_simple:
        P_ws = _water_vapour_saturation_pressure_simple(temperature)
    else:
        P_ws = _water_vapour_saturation_pressure(temperature)
    P_w = P_ws * relative_humidity / 100  # water vapour pressure
    A, m, T_n = _eq_6_constants(temperature)
    # eq. (7)
    denominator = m / (np.log10(P_w / A)) - 1
    Td = T_n / denominator
    return Td


# def dew_point(
#     self,
# ):  # still in development -- source:  https://www.wetterochs.de/wetter/feuchte.html
#     a = 7.5
#     b = 235
#     relative_humidity = 75
#     T = 20
#     dew_point = math.log(
#         ((relative_humidity / 100) * (6.1078 * 10 ** ((a * T) / (b + T)))) / 6.1078, 10
#     )
#     print(dew_point)
