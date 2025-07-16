#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

"""
This modules assists with some helper functions for defining what values
can be turned into JSON and whether GUID IDs are valid. This also includes
some methods for serializing and deserializing JSON data to standard formats.
"""

import re
import numpy as np
from datetime import datetime
from ..utils import ZendirException


def empty_guid() -> str:
    """
    Returns an empty GUID, which is a string of zeros.

    :returns:   An empty GUID
    :rtype:     str
    """

    return "00000000-0000-0000-0000-000000000000"


def is_valid_guid(guid: str) -> bool:
    """
    Determines if a parsed GUID, as a string,
    is valid. This will ensure that it is of
    the correct format.

    :param guid:    The unique GUID of the object, in the correct form
    :type guid:     str

    :returns:       A flag whether the GUID is valid
    :rtype:         bool
    """

    empty: str = empty_guid()
    if guid == None:
        return False
    if guid == empty:
        return False
    if len(guid) != len(empty):
        return False
    if guid[8] != empty[8]:
        return False
    if guid[13] != empty[13]:
        return False
    if guid[18] != empty[18]:
        return False
    if guid[23] != empty[23]:
        return False
    return True


def validate_type(type: str) -> str:
    """
    Validates the type of the object and ensures that it is in the correct format.

    :param type:        The type of the object to validate
    :type type:         str

    :returns:           The validated type with the namespace
    :rtype:             str
    """

    # Check for an invalid or missing
    if type == None or type == "":
        raise ZendirException(
            "Invalid Type: No instance type passed when constructing an instance."
        )

    # Make sure the type is pascal cased
    type = type[0].upper() + type[1:]
    return type


def serialize(value: any) -> any:
    """
    Serializes the value into a JSON serializable format. This will
    convert the value into a list if it is a numpy array or a datetime
    into a string.

    :param value:   The value to serialize
    :type value:    any

    :returns:       The serialized value
    :rtype:         any
    """

    # Check if the value is a numpy array
    if isinstance(value, np.ndarray):
        # Check if the numpy array contains numbers
        if np.issubdtype(value.dtype, np.number):
            return value.tolist()  # Convert to list or list of lists
        return value

    # Check if the value is a datetime
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Check if the value is a simulation instance
    if hasattr(value, "get_id") and hasattr(value, "get_type"):
        return value.get_id()

    # Return the value as is for other types
    return value


def deserialize(value: any) -> any:
    """
    Deserializes the value from a JSON serializable format. This will
    convert the value into a numpy array if it is a list of numbers or
    a datetime string into a datetime object.

    :param value:   The value to deserialize
    :type value:    any

    :returns:       The deserialized value
    :rtype:         any
    """

    # Check if the value is a list
    if isinstance(value, list):

        # Attempt to convert list of numbers to a numpy array
        try:
            array = np.array(value)
            if np.issubdtype(array.dtype, np.number):
                return array
        except:
            pass

        # If conversion fails or is not a list of numbers, return the list as is
        return value

    # Check if the value is a datetime string
    if isinstance(value, str):

        # Regular expression to match the expected datetime format
        datetime_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{7}Z$"

        # Check if the value matches the expected format
        if re.match(datetime_regex, value):
            # Attempt to parse the datetime
            try:
                # Attempt to parse the datetime
                return datetime.strptime(value[:-2], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                pass  # If parsing fails, return the original string

    # Check if the value is a dictionary and then deserialize all values
    if isinstance(value, dict):
        for key, val in value.items():
            value[key] = deserialize(val)
        return value

    # Return the value as is for other types
    return value
