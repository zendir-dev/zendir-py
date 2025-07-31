#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

"""
This file contains public constants related to general mathematics,
as well as astrophysical constants. These include planetary data
and useful values that can be used for conversions.
"""

M_PI: float = 3.141592653589793
"""[-] The value of PI"""

M_PI_2: float = 1.5707963267948966
"""[-] The value of PI/2"""

M_E: float = 2.718281828459045
"""[-] The value of the exponential constant E"""

D2R: float = M_PI / 180.0
"""[-] Degrees to Radians constant"""

R2D: float = 180.0 / M_PI
"""[-] Radians to Degrees constant"""

RPM: float = 0.10471975511965977
"""[-] Conversion from revolutions per minute to rad/s"""

SEC2DAY: float = 1.0 / (60.0 * 60.0 * 24.0)
"""[d] The number of days in a second"""


G: float = 6.67259e-11
"""[m^3/s^2/kg] Universial Gravitational Constant"""

AU: float = 149597870693.0
"""[m] Astronomical unit"""

LIGHT_SPEED: float = 299792458
"""[m/s] The absolute speed of light in a vacuum in meters per second"""

CELCIUS_TO_KELVIN: float = 273.15
"""[K] The value of temperature in Kelvin at 0 degrees Celcius"""


SUN_REQ: float = 695000000
"""[m] The equatorial radius of the Sun"""

SUN_RP: float = 6.95508e8
"""[m] Polar radius of the Sun"""

SUN_MASS: float = 1.989e30
"""[kg] The total mass of the Sun"""

SUN_J2: float = 0.0
"""[-] The Sun J2 value (implicitely zero)"""

SUN_MU: float = 132712440023.310 * 1e9
"""[m^3/s^2] The Sun Gravitational constant"""

SUN_DENSITY: float = 1410
"""[kg/m^3] The density of Sun"""

SUN_ALBEDO_AVG: float = 0.0
"""[-] A reflection albedo constant from the Sun's surface"""


MERCURY_REQ: float = 2439700
"""[m] Equatorial radius of Mercury"""

MERCURY_RP: float = 2.4397e6
"""[m] Polar radius of Mercury"""

MERCURY_MASS: float = 0.330e24
"""[kg] The total mass of Mercury"""

MERCURY_J2: float = 60.0e-6
"""[-] Mercury J2 value"""

MERCURY_ORBIT_SMA: float = 0.38709893 * AU
"""[m] Mercury Semi-Major Axis of it's orbit"""

MERCURY_ORBIT_INC: float = 7.00487 * D2R
"""[rad] The axis inclination of Mercury's orbit"""

MERCURY_ORBIT_E: float = 0.20563069
"""[-] The eccentricity for Mercury's orbit"""

MERCURY_OMEGA: float = 2 * M_PI / 1407.6 / 3600.0
"""[r/s] Rotation rate of the planet"""

MERCURY_MU: float = 22032.080 * 1e9
"""[m^3/s^2] The gravitational constant for Mercury"""

MERCURY_DENSITY: float = 5427
"""[kg/m^3] The density of Mercury"""

MERCURY_ALBEDO_AVG: float = 0.119
"""[-] A reflection albedo constant from Mercury's surface"""


VENUS_REQ: float = 6051800
"""[m] Equatorial radius of Venus"""

VENUS_RP: float = 6.0518e6
"""[m] Polar radius of Venus"""

VENUS_MASS: float = 4.87e24
"""[kg] The total mass of Venus"""

VENUS_J2: float = 4.458e-6
"""[-] Venus J2 value"""

VENUS_ORBIT_SMA: float = 0.72333199 * AU
"""[m] Venus Semi-Major Axis of its orbit"""

VENUS_ORBIT_INC: float = 3.39471 * D2R
"""[rad] The axis inclination of Venus's orbit"""

VENUS_ORBIT_E: float = 0.00677323
"""[-] The eccentricity for Venus's orbit"""

VENUS_OMEGA: float = 2 * M_PI / -5832.6 / 3600.0
"""[r/s] Rotation rate of the planet"""

VENUS_MU: float = 324858.599 * 1e9
"""[k=m^3/s^2] The gravitational constant for Venus"""

VENUS_DENSITY: float = 5243
"""[kg/m^3] The density of Venus"""

VENUS_ALBEDO_AVG: float = 0.75
"""[-] A reflection albedo constant from Venus's surface"""


EARTH_REQ: float = 6378136.6
"""[m] Equatorial radius of Earth"""

EARTH_FLATTENING: float = 1.0 / 298.257223563
"""[-] The flattening of the Earth"""

EARTH_RP: float = 6356751.9
"""[m] Polar radius of Earth"""

EARTH_MASS: float = 5.97e24
"""[kg] The total mass of Earth"""

EARTH_J2: float = 1082.616e-6
"""[-] Earth J2 value"""

EARTH_J3: float = -2.53881e-6
"""[-] Earth J3 value"""

EARTH_J4: float = -1.65597e-6
"""[-] Earth J4 value"""

EARTH_J5: float = -0.15e-6
"""[-] Earth J5 value"""

EARTH_J6: float = 0.57e-6
"""[-] Earth J6 value"""

EARTH_ORBIT_SMA: float = 1.00000011 * AU
"""[m] Earth Semi-Major Axis of its orbit"""

EARTH_ORBIT_INC: float = 0.00005 * D2R
"""[rad] The axis inclination of Earth's orbit"""

EARTH_ORBIT_E: float = 0.01671022
"""[-] The eccentricity for Earth's orbit"""

EARTH_OMEGA: float = 2 * M_PI / 23.9345 / 3600.0
"""[rad/s] Rotation rate of the planet"""

EARTH_MU: float = 3.986004414e14
"""[m^3/s^2] The gravitational constant for Earth"""

EARTH_DENSITY: float = 5514
"""[kg/m^3] The density of Earth"""

EARTH_ALBEDO_AVG: float = 0.29
"""[-] A reflection albedo constant from Earth's surface"""

EARTH_SOLAR_FLUX: float = 1372.5398
"""[W/m^2] Median solar flux at Earth"""

EARTH_GRAV: float = 9.80665
"""[m/s] The gravitational acceleration at the surface of the Earth"""

MOON_REQ: float = 1737400
"""[m] Equatorial radius of the Moon"""

MOON_RP: float = 1.7374e6
"""[m] Polar radius of the Moon"""

MOON_MASS: float = 0.073e24
"""[kg] The total mass of the Moon"""

MOON_J2: float = 202.7e-6
"""[-] J2 constant for the Moon"""

MOON_ORBIT_SMA: float = 0.3844e9
"""[m] Semi-Major Axis of the Moon's orbit"""

MOON_ORBIT_E: float = 0.0549
"""[-] Eccentricity of the Moon's orbit"""

MOON_OMEGA: float = 2 * M_PI / 655.728 / 3600.0
"""[rad/s] The Moon's rotation rate"""

MOON_MU: float = 4.9048695e12
"""[m^3/s^2] The gravitational constant for the Moon"""

MOON_DENSITY: float = 3340
"""[kg/m^3] The density of the Moon"""

MOON_ALBEDO_AVG: float = 0.123
"""[-] A reflection albedo constant from the Moon's surface"""


MARS_REQ: float = 3396190
"""[m] Equatorial radius of Mars"""

MARS_RP: float = 3376200
"""[m] Polar radius of Mars"""

MARS_MASS: float = 0.642e24
"""[kg] The total mass of Mars"""

MARS_J2: float = 1960.45e-6
"""[-] Mars J2 value"""

MARS_ORBIT_SMA: float = 1.52366231 * AU
"""[m] Mars Semi-Major Axis of its orbit"""

MARS_ORBIT_INC: float = 1.85061 * D2R
"""[rad] The axis inclination of Mars's orbit"""

MARS_ORBIT_E: float = 0.09341233
"""[-] The eccentricity for Mars's orbit"""

MARS_OMEGA: float = 2 * M_PI / 24.6229 / 3600.0
"""[r/s] Rotation rate of the planet"""

MARS_MU: float = 42828.314 * 1e9
"""[m^3/s^2] The gravitational constant for Mars"""

MARS_DENSITY: float = 3933
"""[kg/m^3] The density of Mars"""

MARS_ALBEDO_AVG: float = 0.16
"""[-] A reflection albedo constant from Mars's surface"""

PHOBOS_REQ: float = 11200
"""[m] The radius of Phobos"""

DEIMOS_REQ: float = 6100
"""[m] The radius of Deimos"""


JUPITER_REQ: float = 71492000
"""[m] Equatorial radius of Jupiter"""

JUPITER_RP: float = 7.1492e7
"""[m] Polar radius of Jupiter"""

JUPITER_MASS: float = 1898e24
"""[kg] The total mass of Jupiter"""

JUPITER_J2: float = 14736.0e-6
"""[-] Jupiter J2 value"""

JUPITER_ORBIT_SMA: float = 5.20336301 * AU
"""[m] Jupiter Semi-Major Axis of its orbit"""

JUPITER_ORBIT_INC: float = 1.30530 * D2R
"""[rad] The axis inclination of Jupiter's orbit"""

JUPITER_ORBIT_E: float = 0.04839266
"""[-] The eccentricity for Jupiter's orbit"""

JUPITER_OMEGA: float = 2 * M_PI / 9.9250 / 3600.0
"""[r/s] Rotation rate of the planet"""

JUPITER_MU: float = 126712767.881 * 1e9
"""[m^3/s^2] The gravitational constant for Jupiter"""

JUPITER_DENSITY: float = 1326
"""[kg/m^3] The density of Jupiter"""

JUPITER_ALBEDO_AVG: float = 0.34
"""[-] A reflection albedo constant from Jupiter's surface"""


SATURN_REQ: float = 60268000
"""[m] Equatorial radius of Saturn"""

SATURN_RP: float = 6.0268e7
"""[m] Polar radius of Saturn"""

SATURN_MASS: float = 568e24
"""[kg] The total mass of Saturn"""

SATURN_J2: float = 16298.0e-6
"""[-] Saturn J2 value"""

SATURN_ORBIT_SMA: float = 9.53707032 * AU
"""[m] Saturn Semi-Major Axis of its orbit"""

SATURN_ORBIT_INC: float = 2.48446 * D2R
"""[rad] The axis inclination of Saturn's orbit"""

SATURN_ORBIT_E: float = 0.05415060
"""[-] The eccentricity for Saturn's orbit"""

SATURN_OMEGA: float = 2 * M_PI / 10.656 / 3600.0
"""[r/s] Rotation rate of the planet"""

SATURN_MU: float = 37940626.068 * 1e9
"""[m^3/s^2] The gravitational constant for Saturn"""

SATURN_DENSITY: float = 687
"""[kg/m^3] The density of Saturn"""

SATURN_ALBEDO_AVG: float = 0.34
"""[-] A reflection albedo constant from Saturn's surface"""


URANUS_REQ: float = 25559000
"""[m] Equatorial radius of Uranus"""

URANUS_RP: float = 2.5559e7
"""[m] Polar radius of Uranus"""

URANUS_MASS: float = 86.8e24
"""[kg] The total mass of Uranus"""

URANUS_J2: float = 3343.43e-6
"""[-] Uranus J2 value"""

URANUS_ORBIT_SMA: float = 19.19126393 * AU
"""[m] Uranus Semi-Major Axis of its orbit"""

URANUS_ORBIT_INC: float = 0.76986 * D2R
"""[rad] The axis inclination of Uranus's orbit"""

URANUS_ORBIT_E: float = 0.04716771
"""[-] The eccentricity for Uranus's orbit"""

URANUS_OMEGA: float = 2 * M_PI / -17.24 / 3600.0
"""[r/s] Rotation rate of the planet"""

URANUS_MU: float = 5794559.128 * 1e9
"""[m^3/s^2] The gravitational constant for Uranus"""

URANUS_DENSITY: float = 1271
"""[kg/m^3] The density of Uranus"""

URANUS_ALBEDO_AVG: float = 0.29
"""[-] A reflection albedo constant from Uranus's surface"""


NEPTUNE_REQ: float = 24746000
"""[m] Equatorial radius of Neptune"""

NEPTUNE_RP: float = 2.4746e7
"""[m] Polar radius of Neptune"""

NEPTUNE_MASS: float = 102e24
"""[kg] The total mass of Neptune"""

NEPTUNE_J2: float = 3411.0e-6
"""[-] Neptune J2 value"""

NEPTUNE_ORBIT_SMA: float = 30.06896348 * AU
"""[m] Neptune Semi-Major Axis of its orbit"""

NEPTUNE_ORBIT_INC: float = 1.76917 * D2R
"""[rad] The axis inclination of Neptune's orbit"""

NEPTUNE_ORBIT_E: float = 0.00858587
"""[-] The eccentricity for Neptune's orbit"""

NEPTUNE_OMEGA: float = 2 * M_PI / 16.11 / 3600.0
"""[r/s] Rotation rate of the planet"""

NEPTUNE_MU: float = 6836534.065 * 1e9
"""[m^3/s^2] The gravitational constant for Neptune"""

NEPTUNE_DENSITY: float = 1638
"""[kg/m^3] The density of Neptune"""

NEPTUNE_ALBEDO_AVG: float = 0.31
"""[-] A reflection albedo constant from Neptune's surface"""


PLUTO_REQ: float = 1137000
"""[m] Equatorial radius of Pluto"""

PLUTO_RP: float = 1.37e6
"""[m] Polar radius of Pluto"""

PLUTO_MASS: float = 0.0146e24
"""[kg] The total mass of Pluto"""

PLUTO_J2: float = 0.0
"""[-] Pluto J2 value"""

PLUTO_ORBIT_SMA: float = 39.48168677 * AU
"""[m] Pluto Semi-Major Axis of its orbit"""

PLUTO_ORBIT_INC: float = 17.14175 * D2R
"""[rad] The axis inclination of Pluto's orbit"""

PLUTO_ORBIT_ECC: float = 0.24880766
"""[-] The eccentricity for Pluto's orbit"""

PLUTO_OMEGA: float = 2 * M_PI / -153.2928 / 3600.0
"""[r/s] Rotation rate of the planet"""

PLUTO_MU: float = 983.055 * 1e9
"""[m^3/s^2] The gravitational constant for Pluto"""

PLUTO_DENSITY: float = 2095
"""[kg/m^3] The density of Pluto"""

PLUTO_ALBEDO_AVG: float = 0.0
"""[-] A reflection albedo constant from Pluto's surface"""
