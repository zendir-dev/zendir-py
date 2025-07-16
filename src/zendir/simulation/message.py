#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from .instance import Instance
from .context import Context


class Message(Instance):
    """
    The Message class is able to store a series of parameters and data
    associated with the particular message type. This class is a pure
    data class and is not able to invoke any methods.
    """

    def __init__(self, context: Context, id: str, type: str = None) -> None:
        """
        Initialises the message with a context and a
        unique GUID identifier for the message.

        :param context:     The context object that is used for the API
        :type context:      Context
        :param id:          The unique identifier for the Entity in a GUID format
        :type id:           str
        :param type:        The type of the system, if applicable
        :type type:         str
        """

        super().__init__(context, id, type)
