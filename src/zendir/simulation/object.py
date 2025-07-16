#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from __future__ import annotations
from ..utils import printer, ZendirException, helper
from .instance import Instance
from .behaviour import Behaviour
from .model import Model
from .message import Message
from .context import Context


class Object(Instance):
    """
    The Object class is able to define an instance that can exist within the simulation.
    An object will have a 3D representation within the simulation and can have behaviours
    and models attached to it. Objects can also have children objects attached to them.
    Objects will always have a position and rotation within the simulation and are the main
    structure for simulation object.
    """

    __instances: dict[str:Instance] = {}
    """Defines all instances that have been connected to the object, by ID."""

    __children: list[Object] = []
    """Defines all children objects that are attached to the object."""

    __behaviours: list[Behaviour] = []
    """Defines all behaviours that are attached to the object."""

    __models: dict[str:Model] = {}
    """Defines all models that are attached to the object, by type."""

    __messages: dict[str:Message] = {}
    """Defines all messages that are attached to the object, by name."""

    __parent: Object = None
    """Defines the parent object that the object is attached to."""

    def __init__(
        self, context: Context, id: str, type: str = None, parent: Object = None
    ) -> None:
        """
        Initialises the object with the context and the ID of the object.

        :param context:         The context of the object
        :type context:          Context
        :param id:              The GUID ID of the object
        :type id:               str
        :param type:            The type of the system, if applicable
        :type type:             str
        :param parent:          The parent object that the object is attached to, if applicable
        :type parent:           Object
        """

        super().__init__(context, id, type)

        # Clear and reset the data
        self.__instances = {}
        self.__children = []
        self.__behaviours = []
        self.__models = {}
        self.__messages = {}
        self.__parent = parent

    @classmethod
    def from_instance(cls, instance: Instance) -> Object:
        """
        Converts the instance object to an object object.

        :param instance:    The instance object to convert
        :type instance:     Instance

        :returns:           The object object that was created
        :rtype:             Object
        """

        # Create the object and set the data
        object = Object(
            instance._context, instance.get_id(), instance._Instance__type, None
        )
        object.__dict__ = instance.__dict__
        object._Instance__data = instance._Instance__data
        object._refresh_cache = instance._refresh_cache

        # Return the object
        return object

    async def _get_data(self) -> None:
        """
        Overrides the base class method to fetch the data from the API and store it in the
        object. This is used to ensure that the data is fetched correctly and is up to date.
        Additionally, this function will also fetch all the children, behaviours, models and
        messages that are attached to the object.
        """

        # Fetch the base data
        if not self._refresh_cache:
            return
        self._ignore_refresh_override = True
        await super()._get_data()

        # Reload the heirarchies of the data
        await self.__reload_heirarchy(recurse=False)

        # Now, set the override and the required refresh again
        self._ignore_refresh_override = False
        self._refresh_cache = self._context.always_require_refresh

    async def __reload_heirarchy(self, recurse: bool = True) -> None:
        """
        Reloads the heirarchy of the object by fetching all the children, behaviours,
        and models that are attached to the object. This will also ensure that all
        objects are registered with the object and that the data is up to date.

        :param recurse:  Whether to recursively reload the heirarchy of the children
        :type recurse:   bool
        """

        # Get the children of the object
        children_ids: list[str] = await self.get("Children")
        for child_id in children_ids:
            if child_id not in self.__instances:
                self.__register_child(child_id, type="")

        # Get the behaviours of the object
        behaviours_ids: list[str] = await self.get("Behaviours")
        for behaviour_id in behaviours_ids:
            if behaviour_id not in self.__instances:
                self.__register_behaviour(behaviour_id, type="")

        # Now, get the models of the object
        models_ids: list[str] = await self.get("Models")
        for model_id in models_ids:
            if model_id not in self.__instances:
                model = Model(self._context, model_id, None, parent=self)
                self.__instances[model_id] = model
                self.__models[await model.get_type()] = model

        # Now, for each of the children, reload the heirarchy
        if recurse:
            for child in self.__children:
                await child.__reload_heirarchy()

    def _reset_refresh_cache(self) -> None:
        """
        Overrides the base class method to set the flag for refreshing the cache to true.
        This will ensure that all sub-objects will also require a refresh.
        """

        # Ensure all sub-objects require a refresh too
        for _, instance in self.__instances.items():
            instance._reset_refresh_cache()
        super()._reset_refresh_cache()

    def get_parent(self) -> Object:
        """
        Returns the parent object that the object is attached to, if it exists.

        :returns:   The parent object that the object is attached to
        :rtype:     Object
        """

        return self.__parent

    def get_instance_with_id(self, id: str, recurse: bool = False) -> Instance:
        """
        Returns the instance that is attached to the object with the specified ID. If the
        instance does not exist, None will be returned.

        :param id:  The ID of the instance to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of children to find the instance
        :type recurse:   bool

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        """

        # Start by looking at the instances for the ID
        if id in self.__instances:
            return self.__instances[id]

        # If recurse is enabled, look down the chain of children
        if recurse:
            for child in self.__children:
                result = child.get_instance_with_id(id, recurse)
                if result:
                    return result
            for behaviour in self.__behaviours:
                result = behaviour.get_instance_with_id(id)
                if result:
                    return result
            for model in self.__models.values():
                result = model.get_instance_with_id(id)
                if result:
                    return result

        # Return None if the instance is not found
        return None

    async def add_child(self, type: str, **kwargs) -> Object:
        """
        Adds a child object to the object with the specified type. The child object will
        be created and attached to the object and will be returned to the user.

        :param type:    The type of the child object to create
        :type type:     str
        :param kwargs:  Optional additional data to set on the child object when created
        :type kwargs:   dict

        :returns:       The child object that was created
        :rtype:         Object
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Invoke the function library to create the object
        child_id: str = await self.invoke("AddObject", type)

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(child_id):
            raise ZendirException(f"Failed to create child object of type '{type}'.")

        # Create the object and add it to the array
        child: Object = self.__register_child(child_id, type)
        if child is None:
            raise ZendirException(f"Failed to create child object of type '{type}'.")

        # If there are any kwargs, set them on the child object
        if len(kwargs) > 0:
            await child.set(**kwargs)

        # Regsiter the child object with the ID
        return child

    def __register_child(self, id: str, type: str = "") -> Object:
        """
        Registers a child object to the object with the specified ID. The child object will
        be created and attached to the object and will be returned to the user.

        :param id:  The ID of the child object to create
        :type id:   str
        :param type:    The type of the child object to create
        :type type:     str

        :returns:   The child object that was created
        :rtype:     Object
        """

        # Create the object
        object = Object(self._context, id, type, parent=self)
        self.__children.append(object)
        self.__instances[id] = object

        # Print the success message
        if type != "":
            printer.success(f"Successfully created child object of type '{type}'.")
        return object

    def __is_child_registered(self, id: str) -> bool:
        """
        Checks if a child object with the specified ID is registered. This will
        check down the hierarchy of child objects.

        :param id:  The ID of the child object to check
        :type id:   str

        :returns:   True if the child object is registered, False otherwise
        :rtype:     bool
        """

        # Check if the ID is in the instances
        if id in self.__instances:
            return True

        # Check down the hierarchy of child objects
        for child in self.__children:
            if child.__is_child_registered(id):
                return True

        # If not found, return False
        return False

    def __get_registered_child(self, id: str, recurse: bool = True) -> Object:
        """
        Returns the child object that is attached to the object with the specified ID. If the
        child object does not exist, None will be returned. This will also look down the chain
        of instances to find the child object, if specified.

        :param id:  The ID of the child object to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of instances to find the child object
        :type recurse:   bool

        :returns:   The child object that is attached to the object with the specified ID
        :rtype:     Object
        """

        # Start by looking at the children for the ID
        for child in self.__children:
            if child.get_id() == id:
                return child

        # If recurse is enabled, look down the chain of instances
        if recurse:
            for child in self.__children:
                result = child.__get_registered_child(id, recurse)
                if result:
                    return result

        # Return None if the child object is not found
        return None

    def get_child(self, index: int) -> Object:
        """
        Returns the child object at the specified index. If the index is invalid, an
        exception will be raised.

        :param index:   The index of the child object to fetch
        :type index:    int

        :returns:       The child object at the specified index
        :rtype:         Object
        """

        # Fetch the child and perform a safety check
        if index < 0 or index >= len(self.__children):
            raise IndexError(f"Failed to get child object at index: {index}.")
        return self.__children[index]

    def get_children(self) -> list[Object]:
        """
        Returns all of the children objects that are attached to the object.

        :returns:   All of the children objects that are attached to the object
        :rtype:     list[Object]
        """

        return self.__children

    async def find_child_with_type(self, type: str, recurse: bool = True) -> Object:
        """
        Finds the first child object that is attached to the object of the specified
        type. If the type is not found, None will be returned.

        :param type:    The type of the child object to fetch
        :type type:     str
        :param recurse: Whether to search recursively through child objects
        :type recurse:  bool

        :returns:       The first child object that is attached to the object of the specified type
        :rtype:         Object
        """

        # Fetch the children with the specified type and return the first one
        children: list[Object] = await self.find_children_with_type(
            type, recurse=recurse
        )
        if len(children) > 0:
            return children[0]

        # If no children were found, return None
        return None

    async def find_children_with_type(
        self, type: str, recurse: bool = True
    ) -> list[Object]:
        """
        Finds all of the children objects that are attached to the object of the specified
        type. If the type is not found, an empty list will be returned.

        :param type:    The type of the children objects to fetch
        :type type:     str
        :param recurse: Whether to search recursively through child objects
        :type recurse:  bool

        :returns:       All of the children objects that are attached to the object of the specified type
        :rtype:         list[Object]
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Fetch the children with the specified type
        children_ids: list[str] = await self.invoke(
            "FindChildrenWithType", type, recurse
        )

        # For each child, check if it exists. If it does not, we need to require
        # a reload of the heirarchy to ensure that the child is registered.
        require_reload: bool = False
        for child_id in children_ids:
            if not self.__is_child_registered(child_id):
                require_reload = True
                break

        # If required a reload, reload the heirarchy
        if require_reload:
            await self.__reload_heirarchy(recurse=True)

        # Now, create an array with all children from the IDs
        children: list[Object] = [
            self.__get_registered_child(child_id, recurse=True)
            for child_id in children_ids
        ]

        # Return the list
        return children

    async def find_child_with_id(self, id: str, recurse: bool = True) -> Object:
        """
        Returns the child object that is attached to the object with the specified ID. If the
        child object does not exist, None will be returned. This will also look down the chain
        of instances to find the child object, if specified.

        :param id:  The ID of the child object to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of instances to find the child object
        :type recurse:   bool

        :returns:   The child object that is attached to the object with the specified ID
        :rtype:     Object
        """

        # Fetch the child with the specified ID
        child_id: str = await self.invoke("FindChildWithID", id, recurse)

        # If the child ID is not valid, return None
        if not helper.is_valid_guid(child_id):
            return None

        # Check if the child is not registered, and reload the heirarchy
        if not self.__is_child_registered(child_id):
            await self.__reload_heirarchy(recurse=True)

        # Now, return the registered child with the ID
        child: Object = self.__get_registered_child(child_id, recurse=recurse)
        if child is None:
            return None

        # If the child is found, return it
        return child

    async def add_behaviour(self, type: str, **kwargs) -> Behaviour:
        """
        Adds a behaviour to the object with the specified type. The behaviour will be created
        and attached to the object and will be returned to the user.

        :param type:    The type of the behaviour to create
        :type type:     str
        :param kwargs:  Optional additional data to set on the behaviour when created
        :type kwargs:   dict

        :returns:       The behaviour that was created
        :rtype:         Behaviour
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Invoke the function library to create the behaviour
        behaviour_id: str = await self.invoke("AddObject", type)

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(behaviour_id):
            raise ZendirException(f"Failed to create child behaviour of type '{type}'.")

        # Create the behaviour and add it to the array
        behaviour: Behaviour = self.__register_behaviour(behaviour_id, type)
        if behaviour is None:
            raise ZendirException(f"Failed to create child behaviour of type '{type}'.")

        # If there are any kwargs, set them on the child behaviour
        if len(kwargs) > 0:
            await behaviour.set(**kwargs)

        # Regsiter the child behaviour with the ID
        return behaviour

    def __register_behaviour(self, id: str, type: str = "") -> Behaviour:
        """
        Registers a child behaviour to the object with the specified ID. The child behaviour will
        be created and attached to the behaviour and will be returned to the user.

        :param id:  The ID of the child behaviour to create
        :type id:   str
        :param type:    The type of the child behaviour to create
        :type type:     str

        :returns:   The child behaviour that was created
        :rtype:     Object
        """

        # Create the behaviour
        behaviour = Behaviour(self._context, id, type, parent=self)
        self.__behaviours.append(behaviour)
        self.__instances[id] = behaviour

        # Print the success message
        if type != "":
            printer.success(f"Successfully created child behaviour of type '{type}'.")
        return behaviour

    def __is_behaviour_registered(self, id: str) -> bool:
        """
        Checks if a child behaviour with the specified ID is registered. This will
        check down the hierarchy of child behaviours.

        :param id:  The ID of the child behaviour to check
        :type id:   str

        :returns:   True if the child behaviour is registered, False otherwise
        :rtype:     bool
        """

        # Check if the ID is in the instances
        if id in self.__instances:
            return True

        # Check down the hierarchy of child objects
        for child in self.__children:
            if child.__is_behaviour_registered(id):
                return True

        # If not found, return False
        return False

    def __get_registered_behaviour(self, id: str, recurse: bool = True) -> Behaviour:
        """
        Returns the behaviour that is attached to the object with the specified ID. If the
        behaviour does not exist, None will be returned. This will also look down the chain
        of instances to find the behaviour, if specified.

        :param id:  The ID of the behaviour to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of instances to find the child object
        :type recurse:   bool

        :returns:   The behaviour that is attached to the object with the specified ID
        :rtype:     Behaviour
        """

        # Start by looking at the children for the ID
        for behaviour in self.__behaviours:
            if behaviour.get_id() == id:
                return behaviour

        # If recurse is enabled, look down the chain of instances
        if recurse:
            for child in self.__children:
                result = child.__get_registered_behaviour(id, recurse)
                if result:
                    return result

        # Return None if the behaviour is not found
        return None

    def get_behaviour(self, index: int) -> Behaviour:
        """
        Gets the behaviour at the specified index. If the index is invalid, an exception
        will be raised.

        :param index:   The index of the behaviour to fetch
        :type index:    int

        :returns:       The behaviour at the specified index
        :rtype:         Behaviour
        """

        # Fetch the child and perform a safety check
        if index < 0 or index >= len(self.__behaviours):
            raise IndexError(f"Failed to get behaviour at index: {index}.")
        return self.__behaviours[index]

    def get_behaviours(self) -> list[Behaviour]:
        """
        Returns all of the behaviours that are attached to the object.

        :returns:   All of the behaviours that are attached to the object
        :rtype:     list[Behaviour]
        """

        return self.__behaviours

    async def find_behaviour_with_type(
        self, type: str, recurse: bool = True
    ) -> Behaviour:
        """
        Finds the first behaviour that is attached to the object of the specified
        type. If the type is not found, None will be returned.

        :param type:    The type of the behaviour to fetch
        :type type:     str
        :param recurse: Whether to search recursively through child objects
        :type recurse:  bool

        :returns:       The first behaviour that is attached to the object of the specified type
        :rtype:         Behaviour
        """

        # Fetch the children with the specified type and return the first one
        behaviours: list[Behaviour] = await self.find_behaviours_with_type(
            type, recurse=recurse
        )
        if len(behaviours) > 0:
            return behaviours[0]

        # If no behaviours were found, return None
        return None

    async def find_behaviours_with_type(
        self, type: str, recurse: bool = True
    ) -> list[Behaviour]:
        """
        Finds all of the behaviours that are attached to the object of the specified
        type. If the type is not found, an empty list will be returned.

        :param type:    The type of the behaviours to fetch
        :type type:     str
        :param recurse: Whether to search recursively through child objects
        :type recurse:  bool

        :returns:       All of the behaviours that are attached to the object of the specified type
        :rtype:         list[Behaviour]
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Fetch the behaviours with the specified type
        behaviours_ids: list[str] = await self.invoke(
            "FindBehavioursWithType", type, recurse
        )

        # For each behaviour, check if it exists. If it does not, we need to require
        # a reload of the heirarchy to ensure that the behaviour is registered.
        require_reload: bool = False
        for behaviour_id in behaviours_ids:
            if not self.__is_behaviour_registered(behaviour_id):
                require_reload = True
                break

        # If required a reload, reload the heirarchy
        if require_reload:
            await self.__reload_heirarchy(recurse=True)

        # Now, create an array with all behaviours from the IDs
        behaviours: list[Behaviour] = [
            self.__get_registered_behaviour(behaviour_id, recurse=True)
            for behaviour_id in behaviours_ids
        ]

        # Return the list
        return behaviours

    async def find_behaviour_with_id(self, id: str, recurse: bool = True) -> Behaviour:
        """
        Returns the behaviour that is attached to the object with the specified ID. If the
        behaviour does not exist, None will be returned. This will also look down the chain
        of instances to find the behaviour, if specified.

        :param id:  The ID of the behaviour to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of instances to find the behaviour
        :type recurse:   bool

        :returns:   The behaviour that is attached to the object with the specified ID
        :rtype:     Behaviour
        """

        # Fetch the behaviour with the specified ID
        behaviour_id: str = await self.invoke("FindBehaviourWithID", id, recurse)

        # If the behaviour ID is not valid, return None
        if not helper.is_valid_guid(behaviour_id):
            return None

        # Check if the behaviour is not registered, and reload the heirarchy
        if not self.__is_behaviour_registered(behaviour_id):
            await self.__reload_heirarchy(recurse=True)

        # Now, return the registered behaviour with the ID
        behaviour: Behaviour = self.__get_registered_behaviour(
            behaviour_id, recurse=recurse
        )
        if behaviour is None:
            return None

        # If the behaviour is found, return it
        return behaviour

    async def get_model(self, type: str, **kwargs) -> Model:
        """
        Attempts to get the model of the specified type that is attached to the object. If the
        model does not exist, it will be created and attached to the object. If the model cannot
        be created, an exception will be raised.

        :param type:    The type of the model to fetch
        :type type:     str
        :param kwargs:  The additional data to add to the model
        :type kwargs:   dict

        :returns:       The model of the specified type that is attached to the object
        :rtype:         Model
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Check to see if the model exists
        if type in self.__models.keys():
            model: Model = self.__models[type]
            if len(kwargs) > 0:
                await model.set(**kwargs)
            return model

        # Attempt to find or create the model
        id: str = await self._context.get_client().post(
            f"{self.get_id()}/ivk", ["GetModel", type], id=self._context.get_id()
        )
        if not helper.is_valid_guid(id):
            raise ZendirException(f"Failed to create model of type '{type}'.")

        # Create the model with the ID
        model = self.__register_model(id, type)

        # Set the data if it exists
        if len(kwargs) > 0:
            await model.set(**kwargs)
        return model

    def __register_model(self, id: str, type: str = "") -> Model:
        """
        Registers a model to the object with the specified ID. The modelr will
        be created and attached to the object and will be returned to the user.

        :param id:      The ID of the model to create
        :type id:       str
        :param type:    The type of the model to create
        :type type:     str

        :returns:   The model that was created
        :rtype:     Object
        """

        # Create the model with the ID
        model = Model(self._context, id, type, parent=self)
        self.__models[type] = model
        self.__instances[id] = model

        # Print the success message
        printer.success(f"Successfully created model of type '{type}'.")
        return model

    def get_models(self) -> list[Model]:
        """
        Returns all of the models that are attached to the object.

        :returns:   All of the models that are attached to the object
        :rtype:     list[Model]
        """

        return list(self.__models.values())

    async def get_message(self, name: str) -> Message:
        """
        Attempts to get the message with the specified name that is attached to the object. If the
        message does not exist, it will be created and attached to the object. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the object
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
        self.__instances[message_id] = message

        # Return the message of that name
        printer.success(f"Successfully created message with name '{name}'.")
        return message

    async def get_messages(self) -> list[Message]:
        """
        Returns all of the messages that are attached to the object. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the object
        :rtype:     list[Message]
        """

        # Fetch all values on the object
        data: dict = await self.get_all()

        # If any data starts with 'Out_', then it is a message
        for key in data.keys():
            if str(key).startswith("Out_"):
                await self.get_message(key)
            if str(key).startswith("In_"):
                if helper.is_valid_guid(data[key]):
                    await self.get_message(key)

        # Return all the messages
        return self.__messages.values()
