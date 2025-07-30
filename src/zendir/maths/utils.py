#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

"""
This module contains public methods that aid with mathematical
calculations and astrophysical dimensions.
"""

import numpy as np


def acos_quadrant_check(adjacent: float, hypotenuse: float, test: float) -> float:
    """
    Calculate an angle using the arccosine function and perform a
    quadrant check. The function calculates the angle using the arccosine
    of the ratio of the adjacent side to the hypotenuse. It adjusts the
    angle based on the quadrant determined by the 'test' parameter.

    :param adjacent:    The length of the adjacent side of a right triangle.
    :type adjacent:     float
    :param hypotenuse:  The length of the hypotenuse of the triangle.
    :type hypotenuse:   float
    :param test:        A value to determine the quadrant of the angle.
    :type test:         float

    :returns:           The calculated angle in radians.
    :rtype:             float
    """
    # Calculate the ratio of the adjacent side to the hypotenuse
    rat = adjacent / hypotenuse

    # Adjust the ratio if the adjacent side is slightly greater than the hypotenuse
    if adjacent > hypotenuse:
        if np.fabs((adjacent - hypotenuse) / hypotenuse) < 1e-10:
            rat = 1.0
        else:
            raise ValueError(
                "The adjacent: {}, is greater than the hypotenuse: {}".format(
                    adjacent, hypotenuse
                )
            )
    # Calculate the angle using arccos; adjust based on the 'test' parameter
    return 2 * np.pi - np.arccos(rat) if test < 0 else np.arccos(rat)


def normalize_angle(
    angle: float | np.ndarray, angle_max: float = 2 * np.pi
) -> float | np.ndarray:
    """
    Normalize an angle or array of angles between 0 <= theta < angle_max, where angle_max is an arbitrary angle.

    :param angle: The angle (float) or array of angles (numpy.ndarray) to be normalized.
    :type angle: float or numpy.ndarray
    :param angle_max: The maximum value for the angle range (default: 2*pi for radians).
    :type angle_max: float

    :returns: The normalized angle (float) or array of angles (numpy.ndarray).
    :rtype: float or numpy.ndarray

    :example:
    >>> normalize_angle(-3.0, angle_max=360)
    357.0
    >>> normalize_angle(np.array([-3.0, 0.0, 6.5, 12.0, -9.0]), angle_max=360)
    array([357. ,   0. ,   6.5,  12. , 351. ])
    """
    angle = np.fmod(angle, angle_max)
    # Add the angle max if the angle is negative. Handle for both scalar and array angles
    if np.isscalar(angle):
        if angle < 0:
            angle += angle_max
    else:
        angle[angle < 0] += angle_max
    return angle


def shortest_angular_difference(angle1: float, angle2: float) -> float:
    """
    Calculate the shortest angular difference between two angles. This function
    calculates the shortest angular difference between two angles using the
    arccosine function and the quadrant check function.

    :param angle1:  The first angle
    :type angle1:   float
    :param angle2:  The second angle
    :type angle2:   float

    :returns:       The shortest angular difference between the two angles
    :rtype:         float
    """
    # Calculate the difference between the two angles
    d_angle: float = angle1 - angle2
    # Get the alternative angle
    alt_angle: float = -np.sign(d_angle) * (2 * np.pi - np.fabs(d_angle))
    # Return the shortest angle
    return alt_angle if np.fabs(alt_angle) < np.fabs(d_angle) else d_angle


def normalize_array(array: np.ndarray) -> np.ndarray:
    """
    Normalize a numpy array. This function normalizes a numpy array by
    dividing each element by the magnitude of the array.

    :param array:   The array to be normalized
    :type array:    np.ndarray

    :returns:       The normalized array
    :rtype:         np.ndarray
    """
    # Return the normalized array
    return array / np.linalg.norm(array)


def parallel_vector(v1: np.ndarray, v_ref: np.ndarray) -> np.ndarray:
    """
    Calculate the component of v1 that is parallel with v_ref.

    :param v1:  The first vector
    :type v1:   np.ndarray
    :param v_ref:  The second vector
    :type v_ref:   np.ndarray

    :returns:   The parallel vector of the two vectors
    :rtype:     np.ndarray
    """
    # find the parrallel component
    reference_normalised = normalize_array(v_ref)
    return reference_normalised * np.dot(v1, reference_normalised)


def perpendicular_vector(v1: np.ndarray, v_ref: np.ndarray) -> np.ndarray:
    """
    Calculate the perpendicular vector of two vectors. This function calculates
    the perpendicular vector of two vectors using the dot product and the magnitude
    of each vector. The perpendicular vector is calculated using the dot product
    and the magnitude of the first vector.

    :param v1:  The first vector
    :type v1:   np.ndarray
    :param v_ref:  The second vector
    :type v_ref:   np.ndarray

    :returns:   The perpendicular vector of the two vectors
    :rtype:     np.ndarray
    """
    # find the perpendicular component
    return v1 - parallel_vector(v1, v_ref)


def angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate the angle between two vectors. This function calculates the
    angle between two vectors using the dot product and the magnitude of
    each vector. The angle is calculated using the arccosine function.

    :param v1:  The first vector
    :type v1:   np.ndarray
    :param v2:  The second vector
    :type v2:   np.ndarray

    :returns:   The angle between the two vectors in radians.
    :rtype:     float
    """

    # Calculate the dot product of the two vectors
    dot: float = np.dot(v1, v2)

    # Calculate the magnitude of each vector
    denom: float = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        raise ZeroDivisionError
    # Calculate the angle between the two vectors
    angle: float = acos_quadrant_check(dot, denom, dot)

    return angle


def unit_vector_derivative(u: np.ndarray, udot: np.ndarray) -> np.ndarray:
    """
    Calculate the time derivative of a unit vector.

    :param u: The original vector.
    :type u: numpy.ndarray
    :param udot: The time derivative of the original vector.
    :type udot: numpy.ndarray
    :return: The time derivative of the unit vector derived from the original vector.
    :rtype: numpy.ndarray

    Computes the time derivative of a unit vector given a vector and its time derivative.
    If the magnitude of the original vector is zero, returns a zero vector to avoid division by zero.

    Example:
    --------
    >>> u = np.array([1, 0, 0])
    >>> udot = np.array([0, 1, 0])
    >>> unit_vector_derivative(u, udot)
    array([0., 1., 0.])
    """
    umag: float = np.linalg.norm(u)
    if umag == 0:
        uhatd: np.ndarray = np.zeros(3)
    else:
        uhat: np.ndarray = u / umag
        uhatd: np.ndarray = (udot - np.dot(uhat, udot) * uhat) / umag
    return uhatd
