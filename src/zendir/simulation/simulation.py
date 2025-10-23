#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from __future__ import annotations
import os, json
import pandas as pd
from .instance import Instance
from .message import Message
from .object import Object
from .behaviour import Behaviour
from .context import Context
from .model import Model
from .system import System
from ..connection import Client
from ..utils import ZendirException, printer, helper
from ..data import SimulationData


class Simulation(Context):
    """
    The Simulation class is the root object that is used to interact with the simulation.
    This can be used to create objects, behaviours, systems and messages within the simulation.
    Additionally, it can be used to track objects, query objects and save and load the state
    of the simulation. A simulation requires a client to be able to access the API. These
    clients are used to authenticate the user and ensure that the simulation is accessible.
    """

    __client: Client = None
    """Defines the client that is used to access the API."""

    __id: str = None
    """Defines the ID of the simulation. This is used to identify the simulation within the API."""

    __objects: list[Object] = []
    """Defines all objects that are created within the simulation, with the simulation root."""

    __behaviours: list[Behaviour] = []
    """Defines all behaviours that are created within the simulation, with the simulation root."""

    __systems: dict[str:System] = {}
    """Defines all systems that are created within the simulation, with the simulation root."""

    __messages: list[Message] = []
    """Defines all messages that are created within the simulation, with the simulation root."""

    __planets: dict[str:Object] = {}
    """Defines all planets that are created within the simulation, with the simulation root."""

    __time: float = 0.0
    """Defines the current time of the simulation."""

    __ticked: bool = False
    """Defines whether the simulation has been ticked or not."""

    def __init__(self, client: Client, id: str) -> None:
        """
        Initialises the simulation with the client and the ID of the simulation. If the ID is
        not provided, a new simulation will be created. If the reset flag is set to true, the simulation
        will be disposed and cleaned before initialising.

        :param client:          The client to access the API
        :type client:           Client
        :param id:              The ID of the simulation that exists
        :type id:               str
        """

        # Store a reference to the client
        self.__client: Client = client

        # If the client is are bad, throw an exception
        if not self.__client:
            raise ZendirException(
                "Failed to create a simulation due to invalid client."
            )

        # Configure the root object
        self.__id = id

        # If the ID is not valid, throw an exception
        if not helper.is_valid_guid(self.__id):
            raise ZendirException(
                "Failed to create a simulation due to invalid simulation ID."
            )

        # Reset the objects and systems
        self.__reset()

    @classmethod
    async def create(cls, client: Client) -> Simulation:
        """
        Creates a new simulation with the specified client. This will create a new simulation
        session with the API and return the simulation that has been created. If the client is
        invalid, an exception will be raised.

        :param client:          The client to access the API
        :type client:           Client

        :returns:               The simulation that has been created
        :rtype:                 Simulation
        """

        # Attempt to register a new simulation with the API
        id: str = await client.post("new", "Simulation")
        if not helper.is_valid_guid(id):
            raise ZendirException(
                "Failed to create a simulation due to invalid simulation ID."
            )

        # Create the simulation object with the ID and client
        sim: Simulation = Simulation(client, id=id)
        return sim

    @classmethod
    async def list(cls, client: Client) -> list[Simulation]:
        """
        Lists all the simulations that are currently running. This will return a list of
        simulations that are currently running and their IDs. If the client is invalid, an
        exception will be raised.

        :param client:          The client to access the API
        :type client:           Client

        :returns:               The list of simulations that are currently running
        :rtype:                 list[Simulation]
        """

        # Get the list of simulations from the API
        result = await client.get("")
        return [Simulation(client, id) for id in result]

    async def dispose(self) -> None:
        """
        Disposes of the simulation. This will dispose of the simulation and clear all objects,
        behaviours, systems and messages that have been created within the simulation. The
        simulation can no longer be used after this has been called.
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Dispose of the simulation and reset the state
        await self.__client.delete(f"{self.get_id()}", id=self.get_id())
        self.__reset()
        self.__id = None
        self.__client = None

    @classmethod
    async def dispose_all(cls, client: Client) -> None:
        """
        Disposes of all simulations that are currently running. This will dispose of all simulations
        and clear all objects, behaviours, systems and messages that have been created within the
        simulations. The simulations can no longer be used after this has been called.

        :param client:          The client to access the API
        :type client:           Client
        """

        # Dispose of all simulations
        simulations: list[Simulation] = await cls.list(client)
        for sim in simulations:
            await sim.dispose()

    def __reset(self) -> None:
        """
        Resets the simulation. This will reset the simulation and clear all objects, behaviours,
        systems and messages that have been created within the simulation. This will also reset
        the time of the simulation to zero.
        """

        # Reset the objects and systems
        self.__objects = []
        self.__behaviours = []
        self.__systems = {}
        self.__messages = []
        self.__planets = {}
        self.__time = 0.0
        self.__ticked = False

    def get_id(self) -> str:
        """
        Returns the ID of the simulation. This is used to identify the simulation within the API.

        :returns:   The ID of the simulation
        :rtype:     str
        """

        # Return the ID of the simulation, which should have been set by the API
        return self.__id

    def get_client(self) -> Client:
        """
        Returns the client that is used to access the API. This is used to authenticate the user
        and ensure that the simulation is accessible.

        :returns:   The client that is used to access the API
        :rtype:     Client
        """

        # Return the client that is used to access the API
        return self.__client

    def is_valid(self) -> bool:
        """
        Returns whether the simulation is valid or not. This will check if the simulation ID is
        valid and if the client is valid. If the simulation ID is not valid, an exception will be raised.

        :returns:   Whether the simulation is valid or not
        :rtype:     bool
        """

        # Check if the simulation ID is valid
        return (
            self.get_id() != None
            and helper.is_valid_guid(self.get_id())
            and self.__client != None
        )

    def __validate(self) -> None:
        """
        Validates the simulation. This will ensure that the simulation is valid and that the ID
        and client are set. If the simulation is not valid, an exception will be raised.
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise ZendirException(
                "Failed to call function on an invalid or deleted simulation."
            )

    async def get_function_library(self) -> System:
        """
        Returns the function library for the simulation. This will return the function library
        that is used to access the API and authenticate the user.

        :returns:   The function library for the simulation
        :rtype:     System
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Create the request to the function
        return await self.get_system("ExtensionSystem")

    def __reset_refresh_cache(self) -> None:
        """
        Ensures that the simulation requires a refresh. This will ensure that all objects, behaviours,
        systems and messages will also require a refresh.
        """

        # Ensure all sub-objects require a refresh too
        for object in self.__objects:
            object._reset_refresh_cache()
        for behaviour in self.__behaviours:
            behaviour._reset_refresh_cache()
        for system in self.__systems.values():
            system._reset_refresh_cache()
        for message in self.__messages:
            message._reset_refresh_cache()
        for planet in self.__planets.values():
            planet._reset_refresh_cache()

    def __get_registered_instance(self, id: str) -> Instance:
        """
        Attempts to get the instance with the specified ID within the simulation. This will
        search through all objects, behaviours, systems and messages to get the instance. If
        the instance is not found, None will be returned.

        :param id:      The ID of the instance to get
        :type id:       str

        :returns:       The instance with the specified ID
        :rtype:         Instance
        """

        for object in self.__objects:
            if object.get_id() == id:
                return object
            get: Instance = object.get_instance_with_id(id, True)
            if get != None:
                return get
        for behaviour in self.__behaviours:
            if behaviour.get_id() == id:
                return behaviour
            get: Instance = behaviour.get_instance_with_id(id, True)
            if get != None:
                return get
        for system in self.__systems.values():
            if system.get_id() == id:
                return system
            get: Instance = system.get_instance_with_id(id, True)
            if get != None:
                return get
        for message in self.__messages:
            if message.get_id() == id:
                return message
        return None

    async def __is_valid_instance_id(self, id: str) -> bool:
        """
        Attempts to check if the ID is a valid instance ID within the simulation. This will
        call the API to check if the ID exists and is valid. If the ID is not valid, then this
        will return False. If the ID is valid, then this will return True.

        :param id:      The ID of the instance to check
        :type id:       str

        :returns:       Whether the ID is a valid instance ID or not
        :rtype:         bool
        """

        # See if the ID already exists in the local mapping
        if not helper.is_valid_guid(id):
            raise ZendirException(
                "Failed to find a instance with an ID as the guid was incorrect."
            )

        # Create the request to the function
        result_id: str = await self.__client.post(
            f"{self.get_id()}/ivk", ["FindObjectWithID", id], id=self.get_id()
        )

        # Return whether the ID is valid or not
        return helper.is_valid_guid(result_id)

    async def add_object(self, type: str, **kwargs) -> Object:
        """
        Adds an object to the simulation with the specified type and data. This will create
        an object within the simulation and return the object that has been created. If the
        object cannot be created, an exception will be raised. This will add the object to the
        root of the simulation. An object will always have a position and orientation in the
        simulation.

        :param type:    The type of the object to create
        :type type:     str
        :param kwargs:  The optional data to set on the object
        :type kwargs:   dict

        :returns:       The object that has been created
        :rtype:         Object
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the type is valid
        type = helper.validate_type(type)

        # Create the Object ID
        object_id: str = await self.__client.post(
            f"{self.get_id()}/ivk", ["AddObject", type], id=self.get_id()
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(object_id):
            raise ZendirException(f"Failed to create object of type '{type}'.")

        # Create the object and add it to the array
        object: Object = Object(self, object_id, type=type)
        self.__objects.append(object)

        # Set the data if the kwargs exist
        if len(kwargs) > 0:
            await object.set(**kwargs)

        # Print the success message
        printer.success(f"Successfully created object of type '{type}'.")

        # Return the object
        return object

    def get_objects(self, recurse: bool = True) -> list[Object]:
        """
        Returns all the objects that have been created within the simulation. This will return
        the objects as a list. If the recurse flag is set to true, all children of the objects
        will be returned as well.

        :param recurse:     Whether to return all children of the objects
        :type recurse:      bool

        :returns:           The objects that have been created within the simulation
        :rtype:             list[Object]
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Create a list of all objects.
        objects: list[Object] = self.__objects.copy()

        # If recursing, loop through all objects and get all children and then keep going
        # down the chain of children to get all objects. This might be multiple levels deep.
        if recurse:

            # Define a recursive function to get all children of an object
            def __inner_get_children(
                child: Object, children: list[Object]
            ) -> list[Object]:
                for c in child.get_children():
                    children.append(c)
                    __inner_get_children(c, children)
                return children

            # Loop through all objects and get all children
            for obj in self.__objects:
                children: list[Object] = __inner_get_children(obj, [])
                objects.extend(children)

        # Return the objects
        return objects

    def get_root_objects(self) -> list[Object]:
        """
        Returns all the root objects that have been created within the simulation. This will
        return all the objects that have been created directly within the simulation and not
        part of any other object. This will return the objects as a list.

        :returns:   The root objects that have been created within the simulation
        :rtype:     list[Object]
        """

        return self.get_objects(recurse=False)

    async def find_object_with_id(self, id: str) -> Object:
        """
        Attempts to find an object in the simulation with a specified ID. This will look through all objects
        that exist and will attempt to find one that has been created. If the object does not exist, it will
        create a Python object with the ID and, provided it exists in the simulation already, the data will
        be fetched when used.

        :param id:  The ID of the object to create
        :type id:   str

        :returns:   The object that has been found or newly created.
        :rtype:     Object
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(id):
            raise ZendirException(
                "Failed to create a object from an ID as the guid was incorrect."
            )

        # Validate if any of the current objects have the same ID
        for obj in self.__objects:
            if obj.get_id() == id:
                return obj

            # Check children
            obj: Object = await obj.find_child_with_id(id, recurse=True)
            if obj != None:
                return obj

        # Attempt to find the object with the ID from the API
        if not await self.__is_valid_instance_id(id):
            return None

        # Otherwise, assume it is a root object and create the Object instance
        object: Object = Object(self, id)
        self.__objects.append(object)

        # Print the success message
        printer.success(f"Successfully created object with ID '{id}'.")

        # Return the object that has been found
        return object

    async def add_behaviour(self, type: str, **kwargs) -> Behaviour:
        """
        Adds a behaviour to the simulation with the specified type and data. This will create
        a behaviour within the simulation and return the behaviour that has been created. If the
        behaviour cannot be created, an exception will be raised. This will add the behaviour to
        the root of the simulation. A behaviour is a type of object that can be attached to other
        objects to provide additional functionality, but has no physical representation.

        :param type:    The type of the behaviour to create
        :type type:     str
        :param kwargs:  The optional data to set on the behaviour
        :type kwargs:   dict

        :returns:       The behaviour that has been created
        :rtype:         Behaviour
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the type is valid
        type = helper.validate_type(type)

        # Create the behaviour ID
        behaviour_id: str = await self.__client.post(
            f"{self.get_id()}/ivk", ["AddObject", type], id=self.get_id()
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(behaviour_id):
            raise ZendirException(f"Failed to create behaviour of type '{type}'.")

        # Create the behaviour and add it to the array
        behaviour: Behaviour = Behaviour(self, behaviour_id, type=type, parent=None)
        self.__behaviours.append(behaviour)

        # Set the data if the kwargs exist
        if len(kwargs) > 0:
            await behaviour.set(**kwargs)

        # Print the success message
        printer.success(f"Successfully created behaviour of type '{type}'.")

        # Return the behaviour
        return behaviour

    def get_behaviours(self, recurse: bool = True) -> list[Behaviour]:
        """
        Returns all the behaviours that have been created within the simulation. This will return
        the behaviours as a list. If the recurse flag is set to true, all child behaviours of the objects
        will be returned as well.

        :param recurse:     Whether to return all behaviours of the objects
        :type recurse:      bool

        :returns:           The behaviours that have been created within the simulation
        :rtype:             list[Behaviour]
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Create a list of all behaviours
        behaviours: list[Behaviour] = self.__behaviours.copy()

        # If recursing, loop through all objects and get all behaviours
        if recurse:
            for obj in self.get_objects(True):

                # Get the children of the object
                child_behaviours: list[Behaviour] = obj.get_behaviours()
                behaviours.extend(child_behaviours)

        # Return the behaviours
        return behaviours

    def get_root_behaviours(self) -> list[Behaviour]:
        """
        Returns all the root behaviours that have been created within the simulation. This will
        return all the behaviours that have been created directly within the simulation and not
        part of any other object. This will return the behaviours as a list.

        :returns:   The root behaviours that have been created within the simulation
        :rtype:     list[Behaviour]
        """

        return self.get_behaviours(recurse=False)

    async def find_behaviour_with_id(self, id: str) -> Behaviour:
        """
        Attempts to find a behaviour in the simulation with a specified ID. This will look through all behaviours
        that exist and will attempt to find one that has been created.

        :param id:  The ID of the behaviour to get
        :type id:   str

        :returns:   The behaviour that has been found
        :rtype:     Behaviour
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(id):
            raise ZendirException("Failed to find behaviour with ID.")

        # Validate if any of the current behaviours have the same ID
        for behaviour in self.__behaviours:
            if behaviour.get_id() == id:
                return behaviour

        # Fetch the children
        for child in self.get_objects(True):

            # Check if the behaviour is in the children
            for behaviour in child.get_behaviours():
                if behaviour.get_id() == id:
                    return behaviour

        # Attempt to find the object with the ID from the API
        if not await self.__is_valid_instance_id(id):
            return None

        # Otherwise, assume it is a root behaviour and create the Behaviour instance
        behaviour: Behaviour = Behaviour(self, id)
        self.__behaviours.append(behaviour)

        # Print the success message
        printer.success(f"Successfully created behaviour with ID '{id}'.")

        # Return the behaviour that has been found
        return behaviour

    async def get_system(self, type: str, **kwargs) -> System:
        """
        Attempts to get the system with the specified type within the simulation. If the system
        does not exist, it will be created with the specified type and data. If the system cannot
        be created, an exception will be raised. This will add the system to the root of the simulation.

        :param type:    The type of the system to get or create
        :type type:     str
        :param kwargs:  The optional data to set on the system
        :type kwargs:   dict

        :returns:       The system with the specified type
        :rtype:         System
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the type is valid
        type = helper.validate_type(type)

        # Check if the system exists and return it
        if type in self.__systems:
            system: System = self.__systems[type]

            # Update the values if there are any
            if len(kwargs) > 0:
                await system.set(**kwargs)
            return system

        # Attempt to find the object of type
        id: str = await self.__client.post(
            f"{self.get_id()}/ivk", ["FindObjectWithType", type], id=self.get_id()
        )
        if not helper.is_valid_guid(id):

            # Attempt to create the system
            id = await self.__client.post(
                f"{self.get_id()}/ivk", ["AddObject", type], id=self.get_id()
            )

            # If the ID is not valid, raise an exception
            if not helper.is_valid_guid(id):
                raise ZendirException(f"Failed to create system of type '{type}'.")

        # Create the system object from the ID and update any kwargs if there are any
        system: System = System(self, id, type=type)
        if len(kwargs) > 0:
            await system.set(**kwargs)
        self.__systems[type] = system

        # Print the success message
        printer.success(f"Successfully created system of type '{type}'.")
        return system

    def get_systems(self) -> list[System]:
        """
        Returns all the systems that have been created within the simulation. This will return
        all the systems that have been created within the simulation as a list.

        :returns:   The systems that have been created within the simulation
        :rtype:     list[System]
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Return the systems that have been created within the simulation
        return list(self.__systems.values())

    def get_models(self) -> list[Model]:
        """
        Returns all the models that have been created within the simulation. This will return
        all the models that have been created within the simulation as a list.

        :returns:   The models that have been created within the simulation
        :rtype:     list[Model]
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Fetch all objects
        objects: list[Object] = self.get_objects(True)
        models: list[Model] = []

        # Loop through all objects and get all models
        for obj in objects:
            child_models: list[Model] = obj.get_models()
            models.extend(child_models)

        # Return the models that have been created within the simulation
        return models

    async def add_message(self, type: str, **kwargs) -> Message:
        """
        Creates a message within the simulation with the specified type and data. This will create
        a message within the simulation and return the message that has been created. If the message
        cannot be created, an exception will be raised. This will add the message to the root of the
        simulation. A message is a type of object that can be used to communicate between objects and
        systems within the simulation.

        :param type:    The type of the message to create
        :type type:     str
        :param kwargs:  The optional data to set on the message
        :type kwargs:   dict

        :returns:       The message that has been created
        :rtype:         Message
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the type is valid
        type = helper.validate_type(type)

        # Create the message ID
        message_id: str = await self.__client.post(
            f"{self.get_id()}/ivk", ["AddObject", type], id=self.get_id()
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(message_id):
            raise ZendirException(f"Failed to create message of type '{type}'.")

        # Create the message and add it to the array
        message: Message = Message(self, message_id, type=type)
        self.__messages.append(message)

        # Set the data if the kwargs exist
        if len(kwargs) > 0:
            await message.set(**kwargs)

        # Print the success message
        printer.success(f"Successfully created message of type '{type}'.")

        # Return the message
        return message

    def get_messages(self, recurse: bool = True) -> list[Message]:
        """
        Returns all the messages that have been created within the simulation. This will return
        the messages as a list. If the recurse flag is set to true, all child messages of the instances
        will be returned as well.

        :param recurse:     Whether to return all messages of the instances
        :type recurse:      bool

        :returns:           The messages that have been created within the simulation
        :rtype:             list[Message]
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Create a list of all messages
        messages: list[Message] = self.__messages.copy()

        # If recursing, loop through all objects and get all messages
        if recurse:

            # Loop through all objects and get all messages
            for obj in self.get_objects(True):
                child_messages: list[Message] = obj._Object__messages.values()
                messages.extend(child_messages)

            # Loop through all behaviours and get all messages
            for behaviour in self.get_behaviours(True):
                child_messages: list[Message] = behaviour._Behaviour__messages.values()
                messages.extend(child_messages)

            # Loop through all systems and get all messages
            for system in self.get_systems():
                child_messages: list[Message] = system._System__messages.values()
                messages.extend(child_messages)

            # Loop through all models and get all messages
            for model in self.get_models():
                child_messages: list[Message] = model._Model__messages.values()
                messages.extend(child_messages)

        # Return the messages
        return messages

    def get_root_messages(self) -> list[Message]:
        """
        Returns all the root messages that have been created within the simulation. This will
        return all the messages that have been created directly within the simulation and not
        part of any other object. This will return the messages as a list.

        :returns:   The root messages that have been created within the simulation
        :rtype:     list[Message]
        """

        return self.get_messages(recurse=False)

    async def get_planet(self, name: str) -> Object:
        """
        Returns the planet with the specified name within the simulation. This will return the
        planet object that has been created within the simulation. If the planet does not exist,
        it will be created and returned. If the planet cannot be created, None will be returned.

        :param name:    The name of the planet to get or create
        :type name:     str

        :returns:       The planet with the specified name
        :rtype:         Object
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the planet already exists
        name = name.strip().lower()
        if name in self.__planets:
            return self.__planets[name]

        # Fetch the solar system
        system: System = await self.get_system("SolarSystem")

        # Grab the planet by invoking the method
        id: str = await system.invoke("GetBody", name)
        if not helper.is_valid_guid(id):
            raise ZendirException(f"Failed to create planet with name '{name}'.")

        # Construct the object
        object: Object = Object(self, id, "CelestialBody")
        self.__planets[name] = object
        self.__objects.append(object)

        # Return the object
        return object

    async def find_message_with_id(self, id: str) -> Message:
        """
        Attempts to find a message in the simulation with a specified ID. This will look through all messages
        that exist and will attempt to find one that has been created. If the message does not exist, it will
        create a Python message with the ID and, provided it exists in the simulation already, the data will
        be fetched when used.

        :param id:  The ID of the message to create
        :type id:   str

        :returns:   The message that has been found or newly created.
        :rtype:     Message
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(id):
            raise ZendirException(
                "Failed to create a message from an ID as the guid was incorrect."
            )

        # Validate if any of the current messages have the same ID
        for message in self.__messages:
            if message.get_id() == id:
                return message

        # Loop through all objects and check for messages
        for message in self.get_messages(recurse=True):
            if message.get_id() == id:
                return message

        # Attempt to find the message with the ID from the API
        if not await self.__is_valid_instance_id(id):
            return None

        # Otherwise, assume it is a root message and create the Message instance
        message: Message = Message(self, id)
        self.__messages.append(message)

        # Print the success message
        printer.success(f"Successfully created message with ID '{id}'.")

        # Return the message that has been found
        return message

    async def find_instance_with_type(self, type: str) -> Instance:
        """
        Searches for an instance of the specified type within the simulation. If the instance
        does not exist, it will be created and returned. If the instance cannot be created, None
        will be returned. This will search through all objects, behaviours, systems and messages
        within the simulation to find the instance.

        :param type:    The type of the instance to find
        :type type:     str

        :returns:       The instance of the specified type
        :rtype:         Instance
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the type is valid
        type = helper.validate_type(type)

        # Create the request to the function
        id: str = await self.__client.post(
            f"{self.get_id()}/ivk", ["FindObjectWithType", type], id=self.get_id()
        )

        # If the result is not a valid GUID, return None
        if not helper.is_valid_guid(id):
            return None

        # Otherwise, check if the instance is already in the list
        instance: Instance = self.__get_registered_instance(id)
        if instance != None:
            return instance

        # Otherwise, create the instance and return it
        return Instance(self, id, type)

    async def find_instances_with_type(self, type: str) -> list[Instance]:
        """
        Finds all instances of the specified type within the simulation. This will search through
        all objects, behaviours, systems and messages within the simulation to find the instances.
        If the instances do not exist, an empty list will be returned.

        :param type:    The type of the instances to find
        :type type:     str

        :returns:       The instances of the specified type
        :rtype:         list[Instance]
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Check if the type is valid
        type = helper.validate_type(type)

        # Create the request to the function
        result = await self.__client.post(
            f"{self.get_id()}/ivk", ["FindObjectsWithType", type], id=self.get_id()
        )

        # If the result is not a list or is empty, return a missing list
        if not isinstance(result, list) or len(result) == 0:
            return []

        # Loop through the list
        instances: list = []
        for i in range(len(result)):
            instance: Instance = self.__get_registered_instance(result[i])
            if instance != None:
                instances.append(instance)
            else:
                instances.append(Instance(self, result[i], type))

        # Return the list
        return instances

    async def find_instance_with_id(self, id: str) -> Instance:
        """
        Searches for an instance of the specified ID within the simulation. If the instance
        does not exist, it will not be created. If the instance cannot be created, None
        will be returned. This will search through all objects, behaviours, systems and messages
        within the simulation to find the instance.

        :param id:    The ID of the instance to find
        :type id:     str

        :returns:       The instance of the specified ID
        :rtype:         Instance
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # See if the ID already exists in the local mapping
        if not helper.is_valid_guid(id):
            raise ZendirException(
                "Failed to find a instance with an ID as the guid was incorrect."
            )

        # If the ID is already in the list, return it
        instance: Instance = self.__get_registered_instance(id)
        if instance != None:
            return instance

        # Create the request to the function
        if not await self.__is_valid_instance_id(id):
            return None

        # Otherwise, create the instance and return it
        return Instance(self, id)

    async def __load_cache(self) -> None:
        """
        Loads the cache for the simulation. This will load all objects, behaviours, systems and messages
        that have been created within the simulation. This will create all the appropriate instances and
        objects in the correct structure.
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Get the extension system
        system: System = await self.get_function_library()

        # Get the structure of the simulation
        structure: dict = await system.invoke("GetSimulationStructure")
        if structure is None:
            raise ZendirException("Failed to load the simulation structure.")

        # Set the time of the simulation
        self.__time = float(structure.get("Time", 0.0))
        self.__ticked = self.__time > 0.0

        # Defines a function to register a message with the instance
        def __register_msg(instance: Instance, msg_data: dict) -> None:
            msg: Message = Message(self, msg_data["ID"], type=msg_data["Type"])
            name: str = msg_data.get("Name", "")
            if type(instance) is System:
                if name not in instance._System__messages:
                    instance._System__messages[name] = msg
            elif type(instance) is Behaviour:
                if name not in instance._Behaviour__messages:
                    instance._Behaviour__messages[name] = msg
            elif type(instance) is Object:
                if name not in instance._Object__messages:
                    instance._Object__messages[name] = msg
                    instance._Object__instances[msg.get_id()] = msg
            elif type(instance) is Model:
                if name not in instance._Model__messages:
                    instance._Model__messages[name] = msg

        # Defines a function to register a behaviour
        def __register_behaviour(behaviour: Behaviour, behaviour_data: dict) -> None:

            # Loop through all messages and register them
            for msg_data in behaviour_data.get("Messages", []):
                __register_msg(behaviour, msg_data)

        # Defines a function to register a model
        def __register_model(model: Model, model_data: dict) -> None:

            # Loop through all messages and register them
            for msg_data in model_data.get("Messages", []):
                __register_msg(model, msg_data)

        # Defines a function to register an object
        def __register_object(object: Object, object_data: dict) -> None:

            # Loop through all messages and register them
            for msg_data in object_data.get("Messages", []):
                __register_msg(object, msg_data)

            # Loop through all models and register them
            for model_data in object_data.get("Models", []):
                model_type: str = model_data["Type"]
                model: Model = None
                if model_type in object._Object__models:
                    model = object._Object__models[model_type]
                else:
                    model: Model = Model(
                        self, model_data["ID"], type=model_type, parent=object
                    )
                    object._Object__models[model_type] = model
                    object._Object__instances[model.get_id()] = model
                __register_model(model, model_data)

            # Loop through all behaviours and register them
            for behaviour_data in object_data.get("Behaviours", []):
                behaviour: Behaviour = None
                for b in object._Object__behaviours:
                    if b.get_id() == behaviour_data["ID"]:
                        behaviour = b
                        break
                if behaviour is None:
                    behaviour: Behaviour = Behaviour(
                        self,
                        id=behaviour_data["ID"],
                        type=behaviour_data["Type"],
                        parent=object,
                    )
                    object._Object__behaviours.append(behaviour)
                    object._Object__instances[behaviour.get_id()] = behaviour
                __register_behaviour(behaviour, behaviour_data)

            # Loop through all children and register them
            for child_data in object_data.get("Children", []):
                child: Object = None
                for c in object._Object__children:
                    if c.get_id() == child_data["ID"]:
                        child = c
                        break
                if child is None:
                    child: Object = Object(
                        self,
                        id=child_data["ID"],
                        type=child_data["Type"],
                        parent=object,
                    )
                    object._Object__children.append(child)
                    object._Object__instances[child.get_id()] = child
                __register_object(child, child_data)

        # Loop through all systems and create them
        for system_data in structure.get("Systems", []):

            # If the system already exists, get it, otherwise create it
            system: System = None
            if system_data["Type"] in self.__systems:
                system = self.__systems[system_data["Type"]]
            else:
                system: System = System(
                    self, id=system_data["ID"], type=system_data["Type"]
                )
                self.__systems[system._Instance__type] = system

            # Register the messages in each system
            messages: list = system_data.get("Messages", [])
            for msg_data in messages:
                __register_msg(system, msg_data)

        # Loop through all behaviours and create them
        for behaviour_data in structure.get("Behaviours", []):

            # If the behaviour already exists, get it, otherwise create it
            behaviour: Behaviour = None
            for b in self.__behaviours:
                if b.get_id() == behaviour_data["ID"]:
                    behaviour = b
                    break

            # If the behaviour was not found, create it
            if behaviour is None:
                behaviour: Behaviour = Behaviour(
                    self, id=behaviour_data["ID"], type=behaviour_data["Type"]
                )
                self.__behaviours.append(behaviour)

            # Register the behaviour data
            __register_behaviour(behaviour, behaviour_data)

        # Loop through all objects and create them
        for object_data in structure.get("Objects", []):

            # If the object already exists, get it, otherwise create it
            object: Object = None
            for o in self.__objects:
                if o.get_id() == object_data["ID"]:
                    object = o
                    break

            # If the object was not found, create it
            if object is None:
                object: Object = Object(
                    self, id=object_data["ID"], type=object_data["Type"]
                )
                self.__objects.append(object)

            # Register the object data
            __register_object(object, object_data)

    async def get_state(self) -> dict:
        """
        Returns the state of the simulation. This will fetch the state from the API and return
        the state as a dictionary.

        :returns:   The state of the simulation
        :rtype:     dict
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Get the extension system
        system: System = await self.get_function_library()

        # Store the total data and the current page being called
        data: str = ""
        page_count: int = 1
        page: int = 0

        # Loop through all pages (which is at least 1)
        while page < page_count:

            # Invoke the query object on the API, with the current page
            page_data: dict = await system.invoke("GetState", page)
            if page_data == None:
                return None

            # If the first page, then store the page data including the metadata
            if page == 0:
                data = page_data["Data"]

            # Otherwise, simply extend the data from the next pages
            else:
                data += page_data["Data"]

            # Update the page count
            # Handle the case where the page count is not present in the page data
            if "Count" not in page_data:
                raise ZendirException(
                    "No data can be retrieved for this query. Make sure the data was subscribed to."
                )
            page_count = page_data["Count"]
            page += 1

        # Finally, we need to deserialize the data
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ZendirException("Failed to decode the state data as JSON.")

    async def save_state(self, path: str) -> None:
        """
        Saves the state of the simulation to the specified path. This will save the state of the
        simulation to the path as a JSON file. If the path does not exist, an exception will be raised.

        :param path:    The path to save the state of the simulation to
        :type path:     str
        """

        # Get the state of the simulation as a raw JSON
        state: dict = await self.get_state()

        # Create the directory if it does not exist
        directory: str = os.path.dirname(path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except:
                pass

        # Save the state to the path
        with open(path, "w") as file:
            json.dump(state, file)

    async def set_state(self, state: dict) -> bool:
        """
        Sets the state of the simulation to the specified state from a JSON object. This
        will also reset and load all objects, behaviours, systems and messages within the
        simulation correctly, storing them into the Python module.

        :param state:       The state to set the simulation to
        :type state:        dict

        :returns:       Whether the state was set successfully
        :rtype:         bool
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Clear the current state
        self.__reset()

        # Get the extension system
        system: System = await self.get_function_library()

        # Start by converting the state to a JSON string
        state_json: str = json.dumps(state)

        # Break it up into chunks of a maximum amount of characters
        chunks: list[str] = []
        CHUNK_SIZE: int = self.__client.get_chunk_size()
        for i in range(0, len(state_json), CHUNK_SIZE):
            chunks.append(state_json[i : i + CHUNK_SIZE])

        # Now, we need to load the chunks individually
        for index, chunk in enumerate(chunks):
            success: bool = await system.invoke("SetState", chunk, index, len(chunks))
            if not success:
                return False

        # Next, load the cache
        await self.__load_cache()

        # Ensure the refresh is required
        self.__reset_refresh_cache()

        # Return the success
        return True

    async def load_state(self, path: str) -> bool:
        """
        Loads the state of the simulation from the specified path. This will load the state of the
        simulation from the path as a JSON file and return whether the state was loaded successfully.
        If the path does not exist, an exception will be raised. This will also reset and load all objects,
        behaviours, systems and messages within the simulation correctly, storing them into the Python module.

        :param path:        The path to load the state of the simulation from
        :type path:         str

        :returns:       Whether the state was loaded successfully
        :rtype:         bool
        """

        # Check if the path exists
        if not os.path.exists(path):
            raise ZendirException(
                f"Failed to load state from path '{path}' as it does not exist."
            )

        # Load the state from the path
        with open(path, "r") as file:
            state: dict = json.load(file)
            return await self.set_state(state)

    async def reload_data(self) -> None:
        """
        Reloads the data of the simulation. This will reload all objects, behaviours, systems and messages
        within the simulation correctly, storing them into the Python module. This is useful if the simulation
        has been modified externally and the data needs to be refreshed.
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Clear the current state
        self.__reset()

        # Load the cache
        await self.__load_cache()

        # Ensure the refresh is required
        self.__reset_refresh_cache()

    async def get_time(self) -> float:
        """
        Returns the current time of the simulation. This will fetch the time from the API
        and return the time as a floating point number.

        :returns:   The current time of the simulation in seconds
        :rtype:     float
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # If the time is not zero, return the time
        if self.__time > 0:
            return self.__time

        # Get the extension system and grab the time
        system: System = await self.get_function_library()
        self.__time = float(await system.invoke("GetSimulationTime"))

        # Return the time
        return self.__time

    async def tick(self, step: float = 0.1) -> None:
        """
        Ticks the simulation by the specified amount of time. This will invoke the tick function
        on the simulation and update the time by the specified amount. If the step is not provided,
        the default step of 0.1 seconds will be used.

        :param step:    The amount of time to tick the simulation by in seconds
        :type step:     float
        """

        # Tick the simulation by the specified amount of time
        await self.tick_duration(step, step)

    async def tick_duration(self, time: float, step: float = 0.1) -> None:
        """
        Ticks the simulation by the specified amount of time. This will invoke the tick function
        on the simulation and update the time by the specified amount. If the step is not provided,
        the default step of 0.1 seconds will be used. If the step is too small, it will do the final
        step with the remaining time.

        :param time:    The totalamount of time to tick the simulation by in seconds
        :type time:     float
        :param step:    The time-step of the tick, used for physics calculations in seconds
        :type step:     float
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # If the time is zero, throw an exception
        if time < 1e-6:
            raise ZendirException(
                "Failed to tick simulation as the time is zero or negative."
            )

        # If the step is zero, throw an exception
        if step < 1e-6:
            raise ZendirException(
                "Failed to tick simulation as the step is zero or negative."
            )

        # Get the extension system
        system: System = await self.get_function_library()

        # If the simulation has not been ticked yet, call a tick with 0.0 to initialise the tracking data
        if not self.__ticked:
            await system.invoke("InitializeSimulation")
            self.__ticked = True

        # Calculate the number of steps to take
        iterations = int(time / step)

        # Determine the final time to tick to (roundede to 1microsecond precision)
        final_time: float = round(time + self.__time, 6)

        # While there are steps remaining, tick
        while iterations > 0:

            # Tick the iterations and get the amount of iterations completed
            result = await system.invoke("TickIterations", iterations, step)
            iterations -= result

            # Update the time
            self.__time += result * step

        # Check if there is any remaining time to tick
        if abs(self.__time - final_time) > 1e-6:
            await system.invoke("TickIterations", 1, final_time - self.__time)
            self.__time = final_time

        # Ensure the refresh is required
        self.__reset_refresh_cache()

    async def get_tracking_interval(self) -> float:
        """
        Returns the current tracking interval for all the objects that have been tracked. This will
        return the interval in simulation seconds. The default value is 10.0 seconds.

        :returns:   The interval to track the objects by in seconds
        :rtype:     float
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Get the tracking system
        system: System = await self.get_system("TrackingSystem")

        # Invoke the get track interval
        return await system.get("Interval")

    async def set_tracking_interval(self, interval: float) -> None:
        """
        Updates the tracking interval for all the objects that have been tracked. This will
        be an interval in simulation seconds and will be the same across all objects. The
        default value is 10.0 seconds.

        :param interval:    The interval to track the objects by in seconds
        :type interval:     float
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # If the interval is not positive, throw an exception
        if interval < 1e-6:
            raise ZendirException(
                "Failed to set tracking interval as the interval must be positive."
            )

        # Get the tracking system
        system: System = await self.get_system("TrackingSystem")

        # Invoke the set track interval
        await system.set(Interval=interval)

    async def track_object(self, instance: Instance, is_advanced: bool = False) -> None:
        """
        Starts tracking the object within the simulation. This will start tracking the object
        which will store the object's data and state every specified tick in a local database.
        This can be used to retrieve the object's data at a later time.

        :param instance:    The instance to track within the simulation
        :type instance:     Instance
        :param is_advanced:  Whether the advanced variables are also being tracked
        :type is_advanced:   bool
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Get the tracking system
        system: System = await self.get_system("TrackingSystem")

        # Get the instance ID, based on whether it is an instance or a string
        id: str = instance.get_id() if isinstance(instance, Instance) else instance

        # If the ID is not a valid GUID, raise an exception
        if not helper.is_valid_guid(id):
            raise ZendirException("Failed to track object as the ID was not valid.")

        # Invoke the track object on the API, with the ID and whether it is advanced
        await system.invoke("TrackObject", id, is_advanced)

    async def query_object(self, instance: Instance) -> SimulationData:
        """
        Queries the object within the simulation. This will query the object and return the data
        that has been stored for the object. This will return the data as a data frame. If there
        is no data for the object, or if the object has not yet been tracked, an empty data frame
        will be returned. Due to the API having a maximum limit of data, this will also fetch the
        data in pages before pre-compiling the data into a single data frame.

        :param instance:    The instance to query within the simulation
        :type instance:     Instance

        :returns:           The data that has been stored for the object
        :rtype:             DataFrame
        """

        # Throw exception if the simulation is not valid
        self.__validate()

        # Get the tracking system
        system: System = await self.get_system("TrackingSystem")

        # Store the total data and the current page being called
        data: dict = {}
        page_count: int = 1
        page: int = 0

        # Get the instance ID, based on whether it is an instance or a string
        id: str = instance.get_id() if isinstance(instance, Instance) else instance

        # If the ID is not a valid GUID, raise an exception
        if not helper.is_valid_guid(id):
            raise ZendirException("Failed to query object as the ID was not valid.")

        # Loop through all pages (which is at least 1)
        while page < page_count:

            # Invoke the query object on the API, with the current page
            page_data: dict = await system.invoke("ExportToAPI", id, page)
            if page_data == None:
                return None

            # If the first page, then store the page data including the metadata
            if page == 0:
                data = page_data

            # Otherwise, simply extend the data from the next pages
            else:
                data["Data"].extend(page_data["Data"])

            # Update the page count
            # Handle the case where the page count is not present in the page data
            if "Count" not in page_data:
                raise ZendirException(
                    "No data can be retrieved for this query. Make sure the data was subscribed to."
                )
            page_count = page_data["Count"]
            page += 1

        # Remove the page information as it is not needed
        del data["Page"]
        del data["Count"]

        # Create and return the data frame
        return SimulationData(data)

    async def query_dataframe(self, instance: Instance) -> pd.DataFrame:
        """
        Queries the object within the simulation. This will query the object and return the data
        that has been stored for the object. This will return the data as a data frame. If there
        is no data for the object, or if the object has not yet been tracked, an empty data frame
        will be returned.

        :param instance:    The instance to query within the simulation
        :type instance:     Instance

        :returns:           The data that has been stored for the object
        :rtype:             DataFrame
        """

        # Create and return the data frame
        return (await self.query_object(instance=instance)).to_dataframe()
