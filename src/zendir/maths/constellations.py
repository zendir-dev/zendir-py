#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from abc import ABC, abstractmethod
from collections.abc import Container
from typing import Dict, Optional, Union, List

import numpy as np

from ..maths.astro import (
    classical_to_vector_elements,
    mean_to_osculating_elements,
    get_planet_property,
    argument_of_latitude,
)


def state_vectors(method):
    """
    Decorator to convert a collection of orbital elements into their equivalent inertial state vectors
    :param method: the method to be decorated
    :return: the decorated method
    """

    def wrapper(self, *args, **kwargs):
        orbital_elements = method(self, *args, **kwargs)
        result = dict()
        # use dictionary comprehension to efficiently convert the state vectors to classical orbital elements
        for i, elements in orbital_elements.items():
            vectors = classical_to_vector_elements(
                semi_major_axis=elements["semi_major_axis"],
                eccentricity=elements["eccentricity"],
                inclination=elements["inclination"],
                right_ascension=elements["right_ascension"],
                argument_of_periapsis=elements["argument_of_periapsis"],
                true_anomaly=elements["true_anomaly"],
                *args,
                **kwargs,
            )
            result[i] = {
                "r_bn_n": np.array(vectors[0]),
                "v_bn_n": np.array(vectors[1]),
            }
        return result

    return wrapper


def classical_elements_mean(mean_to_osculating=False):
    """
    Decorator to calculate the mean classical orbital elements from osculating elements
    :param method: the method to be decorated
    :return: the decorated method
    """

    def decorator(method):
        def wrapper(self, *args, **kwargs):
            orbital_elements = method(self, *args, **kwargs)
            planet = kwargs.get("planet", "earth")
            req = get_planet_property(planet, "REQ")
            j2 = get_planet_property(planet, "J2")
            # define the keys that will be used to access the orbital elements
            keys = (
                "semi_major_axis",
                "eccentricity",
                "inclination",
                "right_ascension",
                "argument_of_periapsis",
                "true_anomaly",
            )
            # use dictionary comprehension to efficiently convert between mean and osculating orbital elements or
            #   vice versa
            return {
                # use dictionary comprehension to map the keys to their respective orbital elements
                i: {
                    keys[j]: el
                    for j, el in enumerate(
                        mean_to_osculating_elements(
                            req=req,
                            j2=j2,
                            semi_major_axis=elements["semi_major_axis"],
                            eccentricity=elements["eccentricity"],
                            inclination=elements["inclination"],
                            right_ascension=elements["right_ascension"],
                            argument_of_periapsis=elements["argument_of_periapsis"],
                            true_anomaly=elements["true_anomaly"],
                            mean_to_osculating=mean_to_osculating,
                        )
                    )
                }
                for i, elements in orbital_elements.items()
            }

        return wrapper

    return decorator


class Constellation(ABC):

    _spacecraft: Dict[int, Dict] = None

    # the number of satellites in the constellation. There must be at least one spacecraft in the constellation
    _num_satellites: int = None

    # the semi-major axis of every spacecraft in the co-planar constellation
    _semi_major_axis: float = None
    # the eccentricity of every spacecraft in the co-planar constellation
    _eccentricity: float = 0.0
    # the inclination of every spacecraft in the co-planar constellation
    _inclination: float = None
    # the right ascension of every spacecraft in the co-planar constellation
    _right_ascension: float = 0.0
    # the argument of periapsis of every spacecraft in the co-planar constellation
    _argument_of_periapsis: float = 0.0
    # the reference true anomaly offset of every spacecraft in the co-planar constellation
    _true_anomaly_offset: float = 0.0

    @property
    def num_satellites(self) -> int:
        """
        get the number of satellites in the constellation
        :return: the number of satellites in the constellation
        :rtype: int
        """
        return self._num_satellites

    @num_satellites.setter
    def num_satellites(self, num_satellites: int):
        """
        set the number of satellites in the constellation
        :param num_satellites: the number of satellites in the constellation
        :type num_satellites: int
        """
        try:
            num_satellites = int(num_satellites)
        except Exception as e:
            raise TypeError
        # ensure the number of satellites is greater than 0
        if num_satellites < 1:
            raise ValueError
        self._num_satellites = num_satellites

    @property
    def semi_major_axis(self) -> float:
        """
        get the semi-major axis of every spacecraft in the constellation
        :return: the semi-major axis of every spacecraft in the constellation
        :rtype: float
        """
        if self._semi_major_axis is None:
            raise ValueError
        return self._semi_major_axis

    @semi_major_axis.setter
    def semi_major_axis(self, semi_major_axis: float):
        """
        set the semi-major axis of every spacecraft in the constellation
        :param semi_major_axis: the semi-major axis of every spacecraft in the constellation
        :type semi_major_axis: float
        """
        try:
            semi_major_axis = float(semi_major_axis)
        except Exception as e:
            raise TypeError
        # ensure the semi-major axis is greater than 0
        if semi_major_axis < 0:
            raise ValueError
        self._semi_major_axis = semi_major_axis

    @property
    def eccentricity(self) -> float:
        """
        get the eccentricity of every spacecraft in the constellation
        :return: the eccentricity of every spacecraft in the constellation
        :rtype: float
        """
        if self._eccentricity is None:
            raise ValueError
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, eccentricity: float):
        """
        set the eccentricity of every spacecraft in the constellation
        :param eccentricity: the eccentricity of every spacecraft in the constellation
        :type eccentricity: float
        """
        try:
            eccentricity = float(eccentricity)
        except Exception as e:
            raise TypeError
        # ensure the eccentricity is greater than 0
        if eccentricity < 0:
            raise ValueError
        self._eccentricity = eccentricity

    @property
    def inclination(self) -> float:
        """
        get the inclination of every spacecraft in the constellation
        :return: the inclination of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._inclination is None:
            raise ValueError
        return self._inclination

    @inclination.setter
    def inclination(self, inclination: float):
        """
        set the inclination of every spacecraft in the constellation
        :param inclination: the inclination of every spacecraft in the constellation [rad]
        :type inclination: float
        """
        try:
            inclination = float(inclination)
        except Exception as e:
            raise TypeError
        self._inclination = inclination

    @property
    def right_ascension(self) -> float:
        """
        get the right ascension of every spacecraft in the constellation
        :return: the right ascension of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._right_ascension is None:
            raise ValueError
        return self._right_ascension

    @right_ascension.setter
    def right_ascension(self, right_ascension: float):
        """
        set the right ascension of every spacecraft in the constellation
        :param right_ascension: the right ascension of every spacecraft in the constellation [rad]
        :type right_ascension: float
        """
        try:
            right_ascension = float(right_ascension)
        except Exception as e:
            raise TypeError
        self._right_ascension = right_ascension

    @property
    def argument_of_periapsis(self) -> float:
        """
        get the argument of periapsis of every spacecraft in the constellation
        :return: the argument of periapsis of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._argument_of_periapsis is None:
            raise ValueError
        return self._argument_of_periapsis

    @argument_of_periapsis.setter
    def argument_of_periapsis(self, argument_of_periapsis: float):
        """
        set the argument of periapsis of every spacecraft in the constellation
        :param argument_of_periapsis: the argument of periapsis of every spacecraft in the constellation [rad]
        :type argument_of_periapsis: float
        """
        try:
            argument_of_periapsis = float(argument_of_periapsis)
        except Exception as e:
            raise TypeError
        self._argument_of_periapsis = argument_of_periapsis

    @property
    def true_anomaly_offset(self) -> float:
        """
        get the true anomaly offset of every spacecraft in the constellation
        :return: the true anomaly offset of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._true_anomaly_offset is None:
            raise ValueError
        return self._true_anomaly_offset

    @true_anomaly_offset.setter
    def true_anomaly_offset(self, true_anomaly_offset: float):
        """
        set the true anomaly offset of every spacecraft in the constellation
        :param true_anomaly_offset: the true anomaly offset of every spacecraft in the constellation [rad]
        :type true_anomaly_offset: float
        """
        try:
            true_anomaly_offset = float(true_anomaly_offset)
        except Exception as e:
            raise TypeError
        self._true_anomaly_offset = true_anomaly_offset

    @property
    def spacecraft(self) -> dict:
        """
        get the spacecraft in the constellation
        :return: the spacecraft in the constellation
        :rtype: dict
        """
        return self._spacecraft

    @spacecraft.setter
    def spacecraft(self, spacecraft: dict):
        """
        set the spacecraft in the constellation
        :param spacecraft: the spacecraft in the constellation
        :type spacecraft: dict
        """
        if not isinstance(spacecraft, dict):
            raise TypeError
        self._spacecraft = spacecraft

    def __init__(self, init_classical_elements=False, **kwargs):
        """
        initialize the constellation

        :param init_classical_elements: whether to initialize the orbital elements for every spacecraft in the
            constellation
        :type init_classical_elements: bool
        :param num_satellites: the number of satellites in the constellation
        :type num_satellites: int
        :param semi_major_axis: the semi-major axis of every spacecraft in the constellation
        :type semi_major_axis: float
        :param eccentricity: the eccentricity of every spacecraft in the constellation
        :type eccentricity: float
        :param inclination: the inclination of every spacecraft in the constellation
        :type inclination: float
        :param right_ascension: the right ascension of every spacecraft in the constellation
        :type right_ascension: float
        :param argument_of_periapsis: the argument of periapsis of every spacecraft in the constellation
        :type argument_of_periapsis: float
        :param true_anomaly_offset: the true anomaly offset of every spacecraft in the constellation
        :type true_anomaly_offset: float
        :param kwargs:
        """
        super().__init__()
        self.num_satellites = kwargs.get("num_satellites", 1)
        if "semi_major_axis" in kwargs:
            self.semi_major_axis = kwargs.get("semi_major_axis")
        if "eccentricity" in kwargs:
            self.eccentricity = kwargs.get("eccentricity")
        if "inclination" in kwargs:
            self.inclination = kwargs.get("inclination")
        if "right_ascension" in kwargs:
            self.right_ascension = kwargs.get("right_ascension")
        if "argument_of_periapsis" in kwargs:
            self.argument_of_periapsis = kwargs.get("argument_of_periapsis")
        if "true_anomaly_offset" in kwargs:
            self.true_anomaly_offset = kwargs.get("true_anomaly_offset")
        # initialize the spacecraft dictionary
        self.spacecraft = {}
        for i in range(self.num_satellites):
            self.spacecraft[i] = dict()
        # initialize the orbital elements for every spacecraft in the constellation
        if init_classical_elements:
            self.init_classical_elements(**kwargs)

    def set_mean_elements(
        self,
        semi_major_axis_mean: float = None,
        eccentricity_mean: float = None,
        inclination_mean: float = None,
        right_ascension_mean: float = None,
        argument_of_periapsis_mean: float = None,
        true_anomaly_mean: float = None,
        **kwargs,
    ):
        """
        set the mean orbital elements for every spacecraft in the constellation

        :param semi_major_axis_mean: the mean semi-major axis of every spacecraft in the constellation
        :type semi_major_axis_mean: float
        :param eccentricity_mean: the mean eccentricity of every spacecraft in the constellation
        :type eccentricity_mean: float
        :param inclination_mean: the mean inclination of every spacecraft in the constellation
        :type inclination_mean: float
        :param right_ascension_mean: the mean offset in right ascension
        :type right_ascension_mean: float
        :param argument_of_periapsis_mean: the mean offset in argument of periapsis
        :type argument_of_periapsis_mean: float
        :param true_anomaly_mean: the mean offset in true anomaly
        :type true_anomaly_mean: float
        :return:
        """
        if semi_major_axis_mean is None:
            raise ValueError(
                "Cannot set the mean orbital elements if the semi_major_axis is None"
            )
        if eccentricity_mean is None:
            raise ValueError(
                "Cannot set the mean orbital elements if the eccentricity is None"
            )
        if inclination_mean is None:
            raise ValueError(
                "Cannot set the mean orbital elements if the inclination is None"
            )
        if right_ascension_mean is None:
            raise ValueError(
                "Cannot set the mean orbital elements if the right_ascension is None"
            )
        if argument_of_periapsis_mean is None:
            raise ValueError(
                "Cannot set the mean orbital elements if the argument_of_periapsis is None"
            )
        if true_anomaly_mean is None:
            raise ValueError(
                "Cannot set the mean orbital elements if the true_anomaly is None"
            )
        planet = kwargs.get("planet", "earth")
        req = get_planet_property(planet, "REQ")
        j2 = get_planet_property(planet, "J2")
        # convert the mean to their equivalent osculating orbital elements so they can be stored
        elements_osculating = mean_to_osculating_elements(
            req=req,
            j2=j2,
            semi_major_axis=semi_major_axis_mean,
            eccentricity=eccentricity_mean,
            inclination=inclination_mean,
            right_ascension=right_ascension_mean,
            argument_of_periapsis=argument_of_periapsis_mean,
            true_anomaly=true_anomaly_mean,
            mean_to_osculating=True,
        )
        self.semi_major_axis = elements_osculating[0]
        self.eccentricity = elements_osculating[1]
        self.inclination = elements_osculating[2]
        self.right_ascension = elements_osculating[3]
        self.argument_of_periapsis = elements_osculating[4]
        self.true_anomaly_offset = elements_osculating[5]

    @abstractmethod
    def init_classical_elements(self, *args, **kwargs):
        """
        initialize the orbital elements for every spacecraft in the constellation, if the orbital element
            properties of this class are osculating then the initial orbital elements will be osculating, otherwise
            they will be mean
        :return:
        """
        raise NotImplementedError

    @classical_elements_mean(mean_to_osculating=True)
    def init_classical_elements_osculating(self, *args, **kwargs):
        """
        initialize the osculating classical orbital elements for every spacecraft in the constellation assuming that the
            orbital element properties of this object are mean
        :param mean_to_osculating: whether to convert the mean orbital elements to their equivalent osculating orbital
            elements
        :type mean_to_osculating: bool
        :return:
        """
        return self.init_classical_elements(*args, **kwargs)

    @classical_elements_mean(mean_to_osculating=False)
    def init_classical_elements_mean(self, *args, **kwargs):
        """
        initialize the mean classical orbital elements for every spacecraft in the constellation assuming that the
            orbital element properties of this object are osculating
        :return:
        """
        return self.init_classical_elements(*args, **kwargs)

    @state_vectors
    def init_state_vectors(self, *args, **kwargs):
        """
        initialize the inertial state vectors for every spacecraft in the constellation
        :return:
        """
        return self.init_classical_elements()

    @state_vectors
    def init_state_vectors_mean(self, *args, **kwargs):
        """
        initialize the mean inertial state vectors for every spacecraft in the constellation
        :return:
        """
        return self.init_classical_elements_mean(*args, **kwargs)

    @state_vectors
    def init_state_vectors_osculating(self, *args, **kwargs):
        """
        initialize the osculating inertial state vectors for every spacecraft in the constellation
        :return:
        """
        return self.init_classical_elements_osculating(*args, **kwargs)

    def __iter__(self):
        """
        iterate over the spacecraft in the constellation
        :return: an iterator over the spacecraft in the constellation
        """
        return iter(self._spacecraft.items())

    def __getitem__(self, item):
        """
        get a spacecraft in the constellation
        :param item: the spacecraft id
        :return: the spacecraft
        """
        return self._spacecraft[item]

    def __setitem__(self, key, value):
        """
        set a spacecraft in the constellation
        :param key: the spacecraft id
        :param value: the spacecraft
        """
        self._spacecraft[key] = value

    def __delitem__(self, key):
        """
        delete a spacecraft in the constellation
        :param key: the spacecraft id
        """
        del self._spacecraft[key]

    def __len__(self):
        """
        get the number of spacecraft in the constellation
        :return: the number of spacecraft in the constellation
        """
        return len(self._spacecraft)

    def __contains__(self, item):
        """
        check if a spacecraft is in the constellation
        :param item: the spacecraft id
        :return: true if the spacecraft is in the constellation, false otherwise
        """
        return item in self._spacecraft

    def __str__(self):
        """
        get the string representation of the constellation
        :return: the string representation of the constellation
        """
        return str(self._spacecraft)

    def __repr__(self):
        """
        get the string representation of the constellation
        :return: the string representation of the constellation
        """
        return repr(self._spacecraft)

    def __eq__(self, other):
        """
        check if two constellations are equal
        :param other: the other constellation
        :return: true if the two constellations are equal, false otherwise
        """
        raise NotImplementedError

    def __ne__(self, other):
        """
        check if two constellations are not equal
        :param other: the other constellation
        :return: true if the two constellations are not equal, false otherwise
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        get the hash of the constellation
        :return: the hash of the constellation
        """
        return hash(self._spacecraft)

    def __bool__(self):
        """
        check if the constellation is not empty
        :return: true if the constellation is not empty, false otherwise
        """
        return bool(self._spacecraft)

    def __enter__(self):
        """
        enter the context of the constellation
        :return: the constellation
        """
        self.init_classical_elements()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        exit the context of the constellation
        :param exc_type: the exception type
        :param exc_val: the exception value
        :param exc_tb: the exception traceback
        """
        pass

    def iter_state_vectors(self, *args, **kwargs):
        """
        iterate over the state vectors of the spacecraft in the constellation
        :return: an iterator over the state vectors of the spacecraft in the constellation
        """
        return iter(self.init_state_vectors(*args, **kwargs).items())

    def true_argument_of_latitude(self, spacecraft_id: int):
        """
        get the true argument of latitude of the spacecraft in the constellation
        :return: the true argument of latitude of the spacecraft in the constellation
        """
        return argument_of_latitude(
            argument_of_periapsis=self[spacecraft_id][4],
            anomaly=self[spacecraft_id][5],
        )

    def is_valid_spacecraft_id(self, spacecraft_id: int) -> bool:
        """
        check if the spacecraft id is valid
        :param spacecraft_id: the spacecraft id
        :return: true if the spacecraft id is valid, false otherwise
        """
        return spacecraft_id in self.spacecraft.keys()

    def set_variable(
        self, spacecraft_ids: Optional[Union[int, List[int]]] = None, **kwargs
    ):
        """
        set variables for spacecraft in the constellation where the variables are input into the method as keyword
            arguments
        :param spacecraft_ids: the spacecraft ids to set the variable for. If None, then the variable will be set for
            every spacecraft in the constellation
        :type spacecraft_ids: Optional[Union[int, List[int]]]
        :param kwargs: the variables to set for the spacecraft in the constellation
        """
        # if the spacecraft ids are None, then set the variable for every spacecraft in the constellation
        if spacecraft_ids is None:
            spacecraft_ids = range(len(self))
        # if the spacecraft ids are an integer, then convert it to a list
        if isinstance(spacecraft_ids, int):
            spacecraft_ids = [spacecraft_ids]
        # set the variable for every spacecraft in the constellation
        for spacecraft_id in spacecraft_ids:
            for variable, value in kwargs.items():
                if not self.is_valid_spacecraft_id(spacecraft_id):
                    raise KeyError(f"The spacecraft id {spacecraft_id} does not exist")

                # if the value is a container, then set the variable for every spacecraft in the constellation
                if isinstance(value, Container) and not isinstance(value, str):
                    if len(value) != len(spacecraft_ids):
                        raise ValueError(
                            f"The length of the value {variable} does not match the number of "
                            + f"spacecraft in the constellation {len(self)}"
                        )
                    self[spacecraft_id][variable] = value[spacecraft_id]
                else:
                    self[spacecraft_id][variable] = value


class Coplanar(Constellation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def init_classical_elements(self, *args, **kwargs):
        """
        initialize the orbital elements for every spacecraft in the constellation
        :return:
        """
        relative_phase: float = 2 * np.pi / self.num_satellites
        # use dictionary comprehension to efficiently initialize the orbital elements for every spacecraft in the
        #   constellation
        for i in range(self.num_satellites):
            self.spacecraft[i]["semi_major_axis"] = self.semi_major_axis
            self.spacecraft[i]["eccentricity"] = self.eccentricity
            self.spacecraft[i]["inclination"] = self.inclination
            self.spacecraft[i]["right_ascension"] = self.right_ascension
            self.spacecraft[i]["argument_of_periapsis"] = self.argument_of_periapsis
            self.spacecraft[i]["true_anomaly"] = (
                self.true_anomaly_offset + i * relative_phase
            )
        return self._spacecraft


class CoplanarCircular(Coplanar):

    _eccentricity = 0.0

    @property
    def eccentricity(self) -> float:
        return 0.0

    @eccentricity.setter
    def eccentricity(self, eccentricity: float):
        self._eccentricity = 0.0

    def __init__(self, **kwargs):
        self.eccentricity = 0
        super().__init__(**kwargs)


class Walker(Constellation):
    """
    A Walker constellation is a constellation of satellites that are evenly spaced in a Walker pattern.
    """

    _num_planes: int = 1

    @property
    def num_planes(self) -> int:
        """
        get the number of planes in the constellation
        :return: the number of planes in the constellation
        :rtype: int
        """
        return self._num_planes

    @num_planes.setter
    def num_planes(self, num_planes: int):
        """
        set the number of planes in the constellation
        :param num_planes: the number of planes in the constellation
        :type num_planes: int
        """
        try:
            num_planes = int(num_planes)
        except Exception as e:
            raise TypeError
        # ensure the number of planes is greater than 0
        if num_planes < 1:
            raise ValueError
        self._num_planes = num_planes

    def __init__(self, **kwargs):
        self.num_planes = kwargs.get("num_planes", 1)
        super().__init__(**kwargs)


class WalkerDelta(Walker):
    """
    A Walker Delta constellation is a constellation of satellites that are evenly spaced in a Walker Delta pattern.
    """

    _relative_spacing = 1.0

    @property
    def relative_spacing(self) -> float:
        """
        get the relative spacing of the constellation
        :return: the relative spacing of the constellation
        :rtype: float
        """
        return self._relative_spacing

    @relative_spacing.setter
    def relative_spacing(self, relative_spacing: float):
        """
        set the relative spacing of the constellation
        :param relative_spacing: the relative spacing of the constellation
        :type relative_spacing: float
        """
        try:
            relative_spacing = float(relative_spacing)
        except Exception as e:
            raise TypeError
        # ensure the relative spacing is greater than or equal to 0
        if relative_spacing < 0:
            raise ValueError
        self._relative_spacing = relative_spacing

    def __init__(self, **kwargs):
        self.relative_spacing = kwargs.get("relative_spacing", 1.0)
        super().__init__(**kwargs)

    def init_classical_elements(self, *args, **kwargs):
        """
        initialize the orbital elements for every spacecraft in the constellation
        :param args:
        :param kwargs:
        :return:
        """
        if self.num_planes > self.num_satellites:
            self.num_planes = self.num_satellites
        # define the full rotation
        full_rotation = 2 * np.pi
        # get the relative spacing parameter which must be within 0 and the number of planes
        relative_spacing = min(max(abs(self.relative_spacing), 0), self.num_planes)
        # calculate the relative phase which will determine the phase offset in true anomaly of spacecraft in every
        #   plane
        relative_phase = relative_spacing * full_rotation / self.num_satellites
        # perform integer division to get the number of satellites per plane as a discrete number
        num_satellites_plane = self.num_satellites // self.num_planes
        # calculate the relative anomaly which will determine the difference in true anomaly between every spacecraft
        relative_anom = full_rotation / num_satellites_plane
        # raise an exception if the number of satellites isn't perfectly divisible into the number of planes
        if self.num_satellites % self.num_planes != 0:
            raise ValueError(
                "The number of satellites should be divisible by the number of planes"
            )
        # set the initial orbital elements for each spacecraft in the constellation
        for i in range(self.num_planes):
            for j in range(num_satellites_plane):
                true_anom = (
                    relative_phase * i + relative_anom * j + self.true_anomaly_offset
                )
                raan = full_rotation / self.num_planes * i + self.right_ascension
                index = i * num_satellites_plane + j
                self.spacecraft[index]["semi_major_axis"] = self.semi_major_axis
                self.spacecraft[index]["eccentricity"] = self.eccentricity
                self.spacecraft[index]["inclination"] = self.inclination
                self.spacecraft[index]["right_ascension"] = raan
                self.spacecraft[index]["argument_of_periapsis"] = self.argument_of_periapsis
                self.spacecraft[index]["true_anomaly"] = true_anom
        # return the orbital elements
        return self._spacecraft
