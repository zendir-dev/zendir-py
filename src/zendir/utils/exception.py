#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from . import printer


class ZendirException(Exception):
    """
    The Zendir Exception class defines a custom exception that is able
    to track errors with the Zendir API. Any connection errors or issues
    with the objects will throw an Zendir API if there are configuration
    issues.
    """

    def __init__(self, message: str):
        """
        Defines the constructor for the exception and is able to pass in
        some parameters in regards to the exception. This will also print
        the exception message

        :param message:     The information error message that will be thrown.
        :type message:      str
        """

        printer.error(message)
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """
        This is the automated cast to a string from the message, which is
        able to return the exception information.

        :returns:   The string formatted text of the message
        :rtype:     str
        """

        return "[ZENDIR ERROR] %s" % self.message
