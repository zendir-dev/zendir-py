import numpy as np


def calculate_focal_length(area_mm2: float | np.ndarray, fov_degrees: float | np.ndarray) -> float | np.ndarray:
    """
    Calculate the focal length of a camera given the sensor area and field of view.

    :param area_mm2: The area of the sensor in square millimeters.
    :type area_mm2: float
    :param fov_degrees: The field of view of the camera in degrees.
    :type fov_degrees: float
    :return: The focal length of the camera in millimeters.
    :rtype: float
    """
    # Sanitise the inputs
    if np.isnan(area_mm2) or np.isnan(fov_degrees):
        raise ValueError("Input values cannot be NaN")
    if np.isinf(area_mm2) or np.isinf(fov_degrees):
        raise ValueError("Input values cannot be infinite")
    if area_mm2 <= 0:
        raise ValueError("Sensor area must be positive")
    if fov_degrees <= 0 or fov_degrees >= 180:
        raise ValueError("Field of view must be greater than 0 and less than 180")
    # Assuming a square sensor
    sensor_width_mm = np.sqrt(area_mm2)
    # Convert FOV to radians
    fov_radians = np.radians(fov_degrees)
    # Calculate tan(fov/2) to use in the focal length calculation
    tan_half_fov = np.tan(fov_radians / 2)
    if tan_half_fov == 0:
        raise ZeroDivisionError("tan(fov/2) is zero, invalid field of view")
    # Calculate focal length
    focal_length_mm = sensor_width_mm / (2 * tan_half_fov)
    return focal_length_mm
