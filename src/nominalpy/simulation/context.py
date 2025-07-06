#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2025.

from ..connection import Client


class Context:
    """
    The context object contains some functions for the simulation. This can be used
    for passing data between different parts of the simulation, such as the simulation
    engine and the function library.
    """

    async def get_function_library(self) -> any:
        """
        Returns the function library for the context.
        """
        raise NotImplementedError(
            "get_function_library() must be implemented by subclasses."
        )

    def get_client(self) -> Client:
        """
        Returns the client for the context.
        """
        raise NotImplementedError("get_client() must be implemented by subclasses.")

    def get_id(self) -> str:
        """
        Returns the ID of the context.
        """
        raise NotImplementedError("get_id() must be implemented by subclasses.")
