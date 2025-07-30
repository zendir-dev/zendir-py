#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

import numpy as np


def to_dcm(
    right: np.ndarray = None, forward: np.ndarray = None, up: np.ndarray = None
) -> np.ndarray:
    """
    Converts the DCM to a new DCM using the provided vectors.

    :param right: A unit vector representing the right axis.
    :param forward: A unit vector representing the forward axis.
    :param up: A unit vector representing the up axis.
    :return: The new DCM.
    """
    # Normalize the input vectors
    if right is not None and forward is not None and up is not None:
        axis_u = up / np.linalg.norm(up)
        axis_r = right / np.linalg.norm(right)
        axis_f = forward / np.linalg.norm(forward)

        # Assign matrix components
        M = np.array(
            [
                [axis_r[0], axis_f[0], axis_u[0]],
                [axis_r[1], axis_f[1], axis_u[1]],
                [axis_r[2], axis_f[2], axis_u[2]],
            ]
        )
    else:
        # Default to identity matrix if no vectors are provided
        M = np.eye(3)
    return M


def up_axis_to_dcm(up: np.ndarray) -> np.ndarray:
    """
    Returns a DCM matrix that aligns the up axis with the given direction.

    :param up: The up axis to align with.
    :return: The DCM aligned to the up axis.
    """
    right_vec = np.array([1, 0, 0])
    forward_vec = np.array([0, 1, 0])
    up_vec = np.array([0, 0, 1])

    # Skip if a zero vector
    if np.linalg.norm(up) == 0:
        raise ValueError("Zero vector provided for up axis.")

    # Check if vectors are aligned
    check = np.dot(right_vec, up)

    # Aligned with up axis
    if check >= 1 - 1e-15:
        return to_dcm(-up_vec, forward_vec, right_vec)

    # Anti-aligned with up axis (down axis)
    if check <= -1 + 1e-15:
        return to_dcm(up_vec, forward_vec, -right_vec)

    # Calculate the axis
    up_norm = up / np.linalg.norm(up)
    forward = np.cross(up_norm, right_vec)
    right = np.cross(forward, up)

    # Return the matrix
    return to_dcm(right, forward, up)


def mrp_to_dcm(mrp: np.ndarray) -> np.ndarray:
    """
    Converts a Modified Rodrigues Parameter (MRP) to a Direction Cosine Matrix (DCM).

    :param mrp: The MRP to convert.
    :return: The DCM representation of the MRP.
    """

    q1 = mrp[0]
    q2 = mrp[1]
    q3 = mrp[2]

    d1 = np.dot(mrp, mrp)
    s = 1 - d1
    d = (1 + d1) * (1 + d1)
    c = np.identity(3)
    c[0, 0] = 4 * (2 * q1 * q1 - d1) + s * s
    c[0, 1] = 8 * q1 * q2 + 4 * q3 * s
    c[0, 2] = 8 * q1 * q3 - 4 * q2 * s
    c[1, 0] = 8 * q2 * q1 - 4 * q3 * s
    c[1, 1] = 4 * (2 * q2 * q2 - d1) + s * s
    c[1, 2] = 8 * q2 * q3 + 4 * q1 * s
    c[2, 0] = 8 * q3 * q1 + 4 * q2 * s
    c[2, 1] = 8 * q3 * q2 - 4 * q1 * s
    c[2, 2] = 4 * (2 * q3 * q3 - d1) + s * s
    c *= 1 / d

    return c


def euler2(angle_rad: float) -> np.ndarray:
    """
    Create a rotation matrix for a rotation about the Y-axis.

    :param angle_rad: Rotation angle in radians.
    :type angle_rad: float
    :return: 3x3 rotation matrix about the Y-axis.
    :rtype: numpy.ndarray
    """
    cos_x = np.cos(angle_rad)
    sin_x = np.sin(angle_rad)
    rotation_matrix = np.array(
        [[cos_x, 0.0, sin_x], [0.0, 1.0, 0.0], [-sin_x, 0.0, cos_x]]
    )
    return rotation_matrix


def euler3(angle_rad: float) -> np.ndarray:
    """
    Create a rotation matrix for a rotation about the Z-axis.

    :param angle_rad: Rotation angle in radians.
    :type angle_rad: float
    :return: 3x3 rotation matrix about the Z-axis.
    :rtype: numpy.ndarray
    """
    cos_x = np.cos(angle_rad)
    sin_x = np.sin(angle_rad)
    rotation_matrix = np.array(
        [[cos_x, -sin_x, 0.0], [sin_x, cos_x, 0.0], [0.0, 0.0, 1.0]]
    )
    return rotation_matrix


def rotate_dcm(dcm: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotates a DCM matrix about an axis by a given angle. The DCM is assumed to be
    a 3x3 matrix and the axis is a 3x1 vector. The angle is measured in degrees.

    :param dcm: The DCM matrix to rotate, assumed to be a 3x3 matrix.
    :type dcm: numpy.ndarray
    :param axis: The axis to rotate about, assumed to be a 3x1 vector.
    :type axis: numpy.ndarray
    :param angle: The angle of rotation in degrees.
    :type angle: float

    :return: The rotated DCM matrix.
    :rtype: numpy.ndarray
    """

    # If a list is used, turn into a numpy array
    if isinstance(dcm, list):
        dcm = np.array(dcm)
    if isinstance(axis, list):
        axis = np.array(axis)

    # Validate the data
    if dcm.shape != (3, 3):
        raise ValueError("DCM matrix must be a 3x3 matrix.")
    if axis.shape != (3,):
        raise ValueError("Axis must be a 3x1 vector.")

    # Convert the angle to radians
    angle_rad = np.radians(angle)

    # Compute the rotation matrix
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    t = 1 - c
    x = axis[0]
    y = axis[1]
    z = axis[2]

    # Compute the rotation matrix
    rotation_matrix = np.array(
        [
            [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
            [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
            [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
        ]
    )

    # Return the rotated DCM
    return np.dot(rotation_matrix, dcm)
