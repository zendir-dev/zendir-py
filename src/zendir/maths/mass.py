#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

import numpy as np


"""
[Zendir] A static library that helps with converting different
mass values between different frames of reference. These
include Center of Masses and Moment of Inertias. The frames
of reference are:
    L -> Component (Local) Frame
    B -> Body Frame (Spacecraft)
    N -> Inertial Frame
"""


def moment_of_inertia_L_to_B(
    moi_L_L: np.ndarray, dcm_LB: np.ndarray, com_B_B: np.ndarray, mass: float
) -> np.ndarray:
    """
    Converts a Moment of Inertia in the L frame to a Moment of
    Inertia in the B frame.

    :param moi_L_L: The moment of inertia in the L frame [kg m^2]
    :type moi_L_L: numpy.ndarray
    :param dcm_LB: The rotational matrix between the L frame and the B frame [-]
    :type dcm_LB: numpy.ndarray
    :param com_B_B: The center of mass in the B frame [m]
    :type com_B_B: numpy.ndarray
    :param mass: The mass of the object [kg]
    :type mass: float
    :return: The moment of inertia in the B frame [kg m^2]
    :rtype: numpy.ndarray
    """
    return inertia_point_transform(moi_L_L, dcm_LB, com_B_B, mass)


def moment_of_inertia_B_to_L(
    moi_B_B: np.ndarray, dcm_LB: np.ndarray, com_B_B: np.ndarray, mass: float
) -> np.ndarray:
    """
    Converts a Moment of Inertia in the B frame to a Moment of
    Inertia in the L frame.

    :param moi_B_B: The moment of inertia in the B frame [kg m^2]
    :type moi_B_B: numpy.ndarray
    :param dcm_LB: The rotational matrix between the L frame and the B frame [-]
    :type dcm_LB: numpy.ndarray
    :param com_B_B: The center of mass in the B frame [m]
    :type com_B_B: numpy.ndarray
    :param mass: The mass of the object [kg]
    :type mass: float
    :return: The moment of inertia in the L frame [kg m^2]
    :rtype: numpy.ndarray
    """
    # Transpose of the dcm_LB matrix to reverse the transformation
    dcm_BL = dcm_LB.T
    return inertia_inverse_point_transform(moi_B_B, dcm_BL, com_B_B, mass)


def moment_of_inertia_prime_L_to_B(
    moiPrime_L_L: np.ndarray,
    dcm_LB: np.ndarray,
    com_B_B: np.ndarray,
    comDot_B_B: np.ndarray,
    mass: float,
) -> np.ndarray:
    """
    Converts a Moment of Inertia Prime (which is a derivative) from the L
    frame to a B frame.

    :param moiPrime_L_L: The moment of inertia in the L frame [kg m^2/s]
    :type moiPrime_L_L: numpy.ndarray
    :param dcm_LB: The rotation matrix from the L to B frame [-]
    :type dcm_LB: numpy.ndarray
    :param com_B_B: The center of mass in the B frame [m]
    :type com_B_B: numpy.ndarray
    :param comDot_B_B: The center of mass change in time in the B frame [m/s]
    :type comDot_B_B: numpy.ndarray
    :param mass: The mass of the object [kg]
    :type mass: float
    :return: The moment of inertia in the B frame [kg m^2/s]
    :rtype: numpy.ndarray
    """
    return inertia_prime_point_transform(
        moiPrime_L_L, dcm_LB, com_B_B, comDot_B_B, mass
    )


def center_of_mass_L_to_B(
    com_L_L: np.ndarray, dcm_LB: np.ndarray, r_LB_B: np.ndarray
) -> np.ndarray:
    """
    Converts a Center of Mass in the L frame to a Center of Mass
    in the B frame.

    :param com_L_L: The center of mass in the L frame [m]
    :type com_L_L: numpy.ndarray
    :param dcm_LB: The rotation matrix from the L to B frames [-]
    :type dcm_LB: numpy.ndarray
    :param r_LB_B: The location difference between the L and B frames [m]
    :type r_LB_B: numpy.ndarray
    :return: The center of mass in the B frame [m]
    :rtype: numpy.ndarray
    """
    r_LmL_L = com_L_L
    r_LmL_B = np.dot(dcm_LB.T, r_LmL_L)
    r_LmB_B = r_LmL_B + r_LB_B
    return r_LmB_B


def center_of_mass_B_to_L(
    com_B_B: np.ndarray, dcm_LB: np.ndarray, r_LB_B: np.ndarray
) -> np.ndarray:
    """
    Converts a Center of Mass in the B frame to a Center of Mass
    in the L frame.

    :param com_B_B: The center of mass in the B frame [m]
    :type com_B_B: numpy.ndarray
    :param dcm_LB: The rotation matrix from the L to B frames [-]
    :type dcm_LB: numpy.ndarray
    :param r_LB_B: The location difference between the L and B frames [m]
    :type r_LB_B: numpy.ndarray
    :return: The center of mass in the L frame [m]
    :rtype: numpy.ndarray
    """
    r_LmB_B = com_B_B
    r_LmL_B = r_LmB_B - r_LB_B
    r_LmL_L = np.dot(dcm_LB, r_LmL_B)
    return r_LmL_L


def tensor_matrix(tensor: np.ndarray, dcm: np.ndarray) -> np.ndarray:
    """
    Transforms a given tensor using a directional cosine matrix (DCM).

    :param tensor: The input tensor to be transformed [3x3 matrix]
    :type tensor: numpy.ndarray
    :param dcm: The directional cosine matrix used for the transformation [-]
    :type dcm: numpy.ndarray
    :return: The transformed tensor [3x3 matrix]
    :rtype: numpy.ndarray
    """
    return np.dot(dcm.T, np.dot(tensor, dcm))


def tensor_transform(tensor: np.ndarray, dcm: np.ndarray) -> np.ndarray:
    """
    Transform a rank-2 tensor to be represented in a new frame.

    :param tensor: A rank-2 tensor in the original frame [3x3 matrix]
    :type tensor: numpy.ndarray
    :param dcm: The DCM for the frame transformation [-]
    :type dcm: numpy.ndarray
    :return: The transformed tensor in the new frame [3x3 matrix]
    :rtype: numpy.ndarray
    """
    return dcm.T @ tensor @ dcm


def inertia_point_transform(
    inertia: np.ndarray, dcm: np.ndarray, position: np.ndarray, mass: float
) -> np.ndarray:
    """
    Transform an inertia tensor from the center-of-mass frame to a new frame.

    :param inertia: The inertia tensor in the original frame [3x3 matrix]
    :type inertia: numpy.ndarray
    :param dcm: The DCM of the transformation [-]
    :type dcm: numpy.ndarray
    :param position: The position of the new frame relative to the original frame [m]
    :type position: numpy.ndarray
    :param mass: The mass of the object [kg]
    :type mass: float
    :return: The transformed inertia tensor in the new frame [3x3 matrix]
    :rtype: numpy.ndarray
    """
    i_parallel = tensor_matrix(inertia, dcm)
    r_tilde = skew_matrix(position)
    return i_parallel - mass * np.dot(r_tilde, r_tilde)


def inertia_inverse_point_transform(
    inertia: np.ndarray, dcm: np.ndarray, position: np.ndarray, mass: float
) -> np.ndarray:
    """
    Transform an inertia tensor from a new frame back to the center-of-mass frame.

    :param inertia: The inertia tensor in the new frame [3x3 matrix]
    :type inertia: numpy.ndarray
    :param dcm: The DCM of the transformation [-]
    :type dcm: numpy.ndarray
    :param position: The position of the new frame relative to the original frame [m]
    :type position: numpy.ndarray
    :param mass: The mass of the object [kg]
    :type mass: float
    :return: The transformed inertia tensor in the original frame [3x3 matrix]
    :rtype: numpy.ndarray
    """
    r_tilde = skew_matrix(position)
    i_parallel = inertia + mass * np.dot(r_tilde, r_tilde)
    return tensor_transform(i_parallel, dcm)


def inertia_prime_point_transform(
    inertia_prime: np.ndarray,
    dcm: np.ndarray,
    position: np.ndarray,
    position_dot: np.ndarray,
    mass: float,
) -> np.ndarray:
    """
    Transform an InertiaPrime tensor from the center-of-mass frame to a new frame.

    :param inertia_prime: The InertiaPrime tensor in the original frame [3x3 matrix]
    :type inertia_prime: numpy.ndarray
    :param dcm: The DCM of the transformation [-]
    :type dcm: numpy.ndarray
    :param position: The position of the new frame relative to the original frame [m]
    :type position: numpy.ndarray
    :param position_dot: The rate of change of the position of the center of mass [m/s]
    :type position_dot: numpy.ndarray
    :param mass: The mass of the object [kg]
    :type mass: float
    :return: The transformed InertiaPrime tensor in the new frame [3x3 matrix]
    :rtype: numpy.ndarray
    """
    # Transform InertiaPrime to a frame parallel to the target frame
    i_parallel = tensor_matrix(inertia_prime, dcm)

    # Compute skew matrices for the position and position rate (position_dot)
    r_tilde = skew_matrix(position)
    r_tilde_prime = skew_matrix(position_dot)

    # Apply the parallel axis theorem to the InertiaPrime tensor
    return i_parallel - mass * (
        np.dot(r_tilde_prime, r_tilde) + np.dot(r_tilde, r_tilde_prime)
    )


def skew_matrix(vector: np.ndarray) -> np.ndarray:
    """
    Generates a skew-symmetric matrix from a 3-element vector.

    :param vector: The input vector [m]
    :type vector: numpy.ndarray
    :return: The skew-symmetric matrix [3x3 matrix]
    :rtype: numpy.ndarray
    """
    return np.array(
        [
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0],
        ]
    )
