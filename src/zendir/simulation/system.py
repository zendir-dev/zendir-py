#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from ..utils import printer, ZendirException, helper
from .instance import Instance
from .message import Message
from .context import Context


class System(Instance):
    """
    A system is a singleton object within the simulation. It only exists once
    per simulation and is used to define the global state of the simulation.
    """

    __messages: dict[str:Message] = {}
    """Defines all messages that are attached to the object, by name."""

    def __init__(self, context: Context, id: str, type: str = None) -> None:
        """
        Initialises the system with the context and the ID of the system.

        :param context:         The context of the simulation
        :type context:          Context
        :param id:              The GUID ID of the system
        :type id:               str
        :param type:            The type of the system, if applicable
        :type type:             str
        """

        super().__init__(context, id, type)

        # Initialised the base data
        self.__messages = {}

    def _reset_refresh_cache(self) -> None:
        """
        Overrides the base class method to set the flag for refreshing the cache to true.
        This will ensure that all messages will also require a refresh.
        """

        # Ensure all messages require a refresh too
        for message in self.__messages.values():
            message._reset_refresh_cache()
        super()._reset_refresh_cache()

    def get_instance_with_id(self, id: str, recurse: bool = False) -> Instance:
        """
        Returns the instance that is attached to this behaviour with the specified ID. If the
        instance does not exist, None will be returned. This may be a message or a child instance
        of some kind.

        :param id:  The ID of the instance to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of children to find the instance
        :type recurse:   bool

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        """

        # Start by looking at the instances for the ID
        for msg in self.__messages.values():
            if msg.get_id() == id:
                return msg

        # Return none otherwise
        return None

    async def get_message(self, name: str) -> Message:
        """
        Attempts to get the message with the specified name that is attached to the system. If the
        message does not exist, it will be created and attached to the system. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the system
        :rtype:         Message
        """

        # Check if the name is within the message structure and return that
        if name in self.__messages.keys():
            return self.__messages[name]

        # Fetch the data
        message_id: str = await self.get(name)
        if not helper.is_valid_guid(message_id):
            raise ZendirException(f"Failed to find message with name '{name}'.")

        # Create the message object with the ID
        message = Message(self._context, message_id)
        self.__messages[name] = message

        # Return the message of that name
        printer.success(f"Successfully created message with name '{name}'.")
        return message

    def get_messages(self) -> list[Message]:
        """
        Returns all of the messages that are attached to the system. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the system
        :rtype:     list[Message]
        """

        return list(self.__messages.values())
