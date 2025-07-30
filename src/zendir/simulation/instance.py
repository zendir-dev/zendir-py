#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from ..utils import ZendirException, helper
from .context import Context


class Instance:
    """
    The instance class is a base class that is used to define any simulation object
    that exists within the simulation. It is able to fetch and set data on the API,
    invoke methods and can be tracked by the API. This class is used to define the
    base functionality for the other types, but should not be created by the user
    itself.
    """

    __data: dict = None
    """Defines the data dictionary that is fetched from the API."""

    __type: str = None
    """Defines the type of the object that is fetched from the API."""

    _refresh_cache: bool = True
    """Defines whether the cache needs to be refreshed or not."""

    _ignore_refresh_override: bool = False
    """Defines an override for when to ignore the required refresh, so that when fetching data, there is no recursion."""

    _context: Context = None
    """Defines the context that is used to access the API."""

    __id: str = None
    """Defines the unique GUID identifier of the object. This needs to be in the correct GUID format."""

    def __init__(self, context: Context, id: str, type: str = None) -> None:
        """
        Initialises the instance with the context and the ID of the object.

        :param context:         The context used to access the API
        :type context:          Context
        :param id:              The GUID ID of the object
        :type id:               str
        :param type:            The type of the object, if known
        :type type:             str
        """

        # Check if the context and ID are valid
        if not context:
            raise ZendirException("Failed to create instance due to invalid context.")
        if not context.get_client():
            raise ZendirException("Failed to create instance due to invalid client.")
        if not helper.is_valid_guid(id):
            raise ZendirException(
                f"Failed to create instance with an invalid ID '{id}'."
            )

        # Set the values and default data
        self.__id = id
        self._context = context
        self.__data = None
        self.__type = type
        self._refresh_cache = True

    async def _get_data(self) -> None:
        """
        This function is used to fetch the data from the API and store it in the
        object. This is used to ensure that the data is fetched correctly and is
        up to date.
        """

        # Skip if the cache does not need to be refreshed
        if not self._refresh_cache:
            return

        # Fetch all data and then set the cache to false
        self.__data = await self._context.get_client().get(
            f"{self.get_id()}/get", id=self._context.get_id()
        )
        self._refresh_cache = (
            self._context.always_require_refresh and not self._ignore_refresh_override
        )

        # Loop through the data and deserialize it
        for key in self.__data:
            self.__data[key] = helper.deserialize(self.__data[key])

    def _reset_refresh_cache(self) -> None:
        """
        This function is used to set the flag for refreshing the cache to true.
        It can be overriden by a base class if additional functionality is required.
        """

        self._refresh_cache = True

    def get_id(self) -> str:
        """
        Returns the unique GUID identifier of the object. This is used to identify
        the object in the API and is used to fetch the data from the API.

        :returns:   The unique GUID identifier of the object
        :rtype:     str
        """

        # Return the ID of the object
        return self.__id

    async def get_type(self) -> str:
        """
        Returns the type of the object that is fetched from the API. This is the
        full type, including the namespace and the class name. If the type has not
        been fetched, it will fetch it from the API.

        :returns:   The type of the object
        :rtype:     str
        """

        # If the type is not provided, or empty, then fetch it from the API
        if not self.__type or self.__type == "":

            # Fetch the function library from the context
            function_library: Instance = await self._context.get_function_library()
            if not function_library:
                raise ZendirException(
                    "Failed to get type of instance due to missing function library."
                )

            # Fetch the type from the API
            self.__type = await function_library.invoke("GetObjectType", self.get_id())

            # If the type is still None, raise an exception
            if not self.__type or self.__type == "":
                raise ZendirException(
                    f"Failed to get type of instance with ID '{self.get_id()}'."
                )

            # Set the type to only be the last part of the "." separated string
            self.__type = self.__type.split(".")[-1]

        # If there is no type, find it
        return self.__type

    def get_instance_with_id(self, id: str, recurse: bool = False) -> "Instance":
        """
        Returns the instance that is attached to this instance with the specified ID. If the
        instance does not exist, None will be returned. This may be a message or a child instance
        of some kind.

        :param id:  The ID of the instance to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of children to find the instance
        :type recurse:   bool

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        """

        # To be overriden by the base class, this is just a placeholder
        return None

    async def get(self, param: str) -> any:
        """
        Fetches a parameter from the object that is stored in the API. This will
        return the parameter if it exists and will raise an exception if it does
        not exist. If the data has not been fetched, it will fetch the data from
        the API.

        :param param:   The parameter to fetch from the object
        :type param:    str

        :returns:       The parameter value from the object
        :rtype:         any
        """

        # Ensures that the data is fetched correctly
        await self._get_data()

        # Check if the param is in the data
        if param not in self.__data:
            raise ZendirException(
                f"Failed to get parameter '{param}' in object '{self.get_id()}' of type '{await self.get_type()}'."
            )
        return self.__data[param]

    async def get_all(self) -> dict:
        """
        Returns all of the data that is stored in the object. This will return
        the full dictionary of the object and will fetch the data if it has not
        been fetched yet.

        :returns:   The full dictionary of the object
        :rtype:     dict
        """

        # Ensures that the data is fetched correctly
        await self._get_data()
        return self.__data

    async def set(self, **kwargs) -> None:
        """
        Sets the parameters of the object that is stored in the API. This will
        take in a dictionary of parameters and values and will update the object
        with the new values. This will raise an exception if the data is invalid.

        :param kwargs:  The parameters and values to set on the object
        :type kwargs:   dict
        """

        # For each of the key values, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Call the method on the client
        await self._context.get_client().post(
            f"{self.get_id()}/set", data=kwargs, id=self._context.get_id()
        )

        # Ensure that the cache is refreshed for the next get
        self._reset_refresh_cache()

    async def invoke(self, function: str, *args) -> any:
        """
        Invoke a function on the object that is stored in the API. This will take
        in the function name and the arguments to pass to the function. This will
        return the response from the function call, if there is a response.

        :param function:    The function name to invoke on the object
        :type function:     str
        :param args:        The arguments to pass to the function
        :type args:         any

        :returns:           The response from the function call
        :rtype:             any
        """

        # For each of the arguments, serialize the data
        args = list(args)
        for i in range(len(args)):
            args[i] = helper.serialize(args[i])

        # Insert the function name as the first argument
        args.insert(0, function)

        # Create the response from the invoke request and get the return data
        response = await self._context.get_client().post(
            f"{self.get_id()}/ivk", args, id=self._context.get_id()
        )
        response = helper.deserialize(response)

        # Update the flag for needing to get values
        self._reset_refresh_cache()
        return response

    def __str__(self) -> str:
        """
        The automated cast of this object to a string will only return the
        GUID identifier of the object.

        :returns:   The formatted ID from the object
        :rtype:     str
        """

        # Return the ID of the object
        return self.get_id()
