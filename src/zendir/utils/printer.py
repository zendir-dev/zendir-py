#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

"""
This module contains helper functions for printing lines to the console.
By default, any calls made to these functions will not print any data.
If the verbosity is enabled, then data will be printed to the console.
"""

import datetime
import os


# Defines ANSI escape sequences for colors
__RESET = "\033[0m"
__RED = "\033[31m"
__GREEN = "\033[32m"
__YELLOW = "\033[33m"
__BLUE = "\033[34m"
__PURPLE = "\033[35m"
__CYAN = "\033[36m"
__WHITE = "\033[37m"
__GREY = "\033[90m"

# Defines the colors for the specific verbose types
__LOG = __GREY
__WARNING = __YELLOW
__ERROR = __RED
__SUCCESS = __GREEN
__INFO = __CYAN
__DEBUG = __PURPLE

LOG_VERBOSITY: int = 0
"""Defines the verbosity for all messages coming from the API and requests."""

SUCCESS_VERBOSITY: int = 1
"""Defines the verbosity for all success and errors coming from the API and requests."""

INFO_VERBOSITY: int = 2
"""Defines the verbosity for all information coming from the API and requests."""

WARNING_VERBOSITY: int = 3
"""Defines the verbosity for any warnings or errors coming from the API and requests."""

ERROR_VERBOSITY: int = 4
"""Defines the verbosity for only errors coming from the API and requests."""

# Defines whether the printer should print
__verbose: bool = False
__verbose_level: int = 0

# Defines whether a timestamp should be shown
__display_time: bool = False

# Defines any callbacks
__callbacks: list = []


def set_verbosity(level: int) -> None:
    """
    Updates the verbosity level of the printing to a particular verbosity
    level. The levels are either LOG_VERBOSITY, WARNING_VERBOSITY,
    SUCCESS_VERBOSITY or ERROR_VERBOSITY.

    :param level:   The verbosity level to initialise the printer to
    :type level:    str
    """

    global __verbose, __verbose_level

    if level <= ERROR_VERBOSITY:
        __verbose_level = level
        __verbose = True
    else:
        __verbose_level = 0
        __verbose = False


def clear() -> None:
    """
    Clears the console output, if possible. This is useful for
    clearing the screen before printing new data.
    """

    # Clear the terminal screen
    os.system("cls" if os.name == "nt" else "clear")


def output(data: str, color: str = "") -> None:
    """
    Outputs text to the console assuming that the verbose level
    is enabled for that type.

    :param data:    The raw data to print to the screen
    :type data:     str
    :param color:   The unique character code format for the color or type of text
    :type color:    str
    """

    if __verbose:
        if __display_time:
            data = "[%s] %s" % (__get_time_str(), data)
        print(color + data + __RESET)


def log(data: str) -> None:
    """
    Prints general log text to the console, providing some information
    about the API calls or requests. This requires a LOG_VERBOSITY level.

    :param data:    The raw data to print to the screen
    :type data:     str
    """

    __call_callbacks("log", data)
    if __verbose_level <= LOG_VERBOSITY:
        output(data, __LOG)


def success(data: str) -> None:
    """
    Prints success messages coming from the simulation or the API calls
    to the screen. This requires at least a SUCCESS_VERBOSITY level.

    :param data:    The raw data to print to the screen
    :type data:     str
    """

    __call_callbacks("success", data)
    if __verbose_level <= SUCCESS_VERBOSITY:
        output(data, __SUCCESS)


def info(data: str) -> None:
    """
    Prints information messages to the console, providing information
    about potential results. This requires at least a INFO_VERBOSITY
    level.

    :param data:    The raw data to print to the screen
    :type data:     str
    """

    __call_callbacks("info", data)
    if __verbose_level <= INFO_VERBOSITY:
        output(data, __INFO)


def warning(data: str) -> None:
    """
    Prints warning messages to the console, providing information
    about potential errors. This requires at least a WARNING_VERBOSITY
    level.

    :param data:    The raw data to print to the screen
    :type data:     str
    """

    __call_callbacks("warning", data)
    if __verbose_level <= WARNING_VERBOSITY:
        output(data, __WARNING)


def error(data: str) -> None:
    """
    Prints error messages to the console, providing information about errors
    that occurred. This requires any valid verbosity level.

    :param data:    The raw data to print to the screen
    :type data:     str
    """

    __call_callbacks("error", data)
    if __verbose_level <= ERROR_VERBOSITY:
        output(data, __ERROR)


def debug(data: str) -> None:
    """
    Prints debug messages for testing certain features to the console. This
    will always print provided the printer is enabled, regardless of the
    verbosity level.

    :param data:    The raw data to print to the screen
    :type data:     str
    """

    __call_callbacks("debug", data)
    output(data, __DEBUG)


def display_time(enable: bool) -> None:
    """
    Defines whether time should be enabled on the printing output
    messages or not.

    :param enable:  A flag for enabling the timestamp on the print lines
    :param type:    bool
    """

    global __display_time
    __display_time = enable


def add_callback(callback: callable) -> None:
    """
    Adds a callback function that will be called whenever a message is printed.
    This can be used to log messages or perform other actions when printing.

    :param callback: The callback function to add
    :type callback: callable
    """

    if callable(callback):
        __callbacks.append(callback)
    else:
        raise TypeError("Callback must be a callable function.")


def remove_callback(callback: callable) -> None:
    """
    Removes a callback function from the list of callbacks.

    :param callback: The callback function to remove
    :type callback: callable
    """

    if callback in __callbacks:
        __callbacks.remove(callback)
    else:
        raise ValueError("Callback not found in the list of callbacks.")


def __call_callbacks(type: str, data: str) -> None:
    """
    Calls all registered callback functions with the given data.

    :param type: The type of the message (e.g., "log", "error", etc.)
    :type type: str
    :param data: The data to pass to the callback functions
    :type data: str
    """

    for callback in __callbacks:
        callback(type, data)


def __get_time_str() -> str:
    """
    Returns the current datetime in the suitable datetime
    format that can be printed.

    :returns:   The current time string of the current datatime in the correct format
    :rtype:     str
    """

    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]


# Define the base verbosity by default
set_verbosity(ERROR_VERBOSITY)
display_time(True)
