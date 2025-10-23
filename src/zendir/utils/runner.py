#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

"""
This modules assists with some helper functions for running a certain number of
simulations in parallel, using the asyncio library. This is useful for quickly
running simulations.
"""

import asyncio
from ..connection import Client
from ..simulation import Simulation


def run_simulation(
    client: Client,
    main: callable,
    *args,
    dispose: bool = True,
    **kwargs,
) -> None:
    """
    Run a simulation with the provided client and main function. This is a
    synchronous function that creates a simulation handle and runs the main
    function with the simulation. The main function must have the first
    parameter as the simulation handle, and can take any number of additional
    parameters and keyword arguments.

    :param client: The client to use for the simulation.
    :type client:  Client
    :param main:   The main function to run with the simulation.
    :type main:    callable
    :param args:   Additional positional arguments to pass to the main function.
    :type args:   tuple
    :param dispose: Whether to dispose of the simulation handle after running
    :type dispose: bool
    :param kwargs: Additional keyword arguments to pass to the main function.
    :type kwargs: dict

    :return:       None
    :rtype:        None
    """

    # Define an asynchronous function to run the main function with the simulation
    async def __runner():

        # Create the simulation handle
        simulation: Simulation = await Simulation.create(client)

        # Run the main function with the simulation and additional arguments
        try:
            await main(simulation, *args, **kwargs)

        # In case of an exception, dispose of the simulation if required
        except Exception as e:
            if dispose and simulation.is_valid():
                await simulation.dispose()
            raise e

        # Dispose of the simulation if required
        if dispose and simulation.is_valid():
            await simulation.dispose()

    # Run the asynchronous function to run the main function
    asyncio.run(__runner())


def run_simulations(
    client: Client, number: int, main: callable, *args, dispose: bool = True, **kwargs
) -> None:
    """
    Run a number of simulations in parallel with the provided client and main
    function. This is a synchronous function that creates a simulation handle
    for each simulation and runs the main function with the simulation. The
    main function must have the first parameter as the simulation handle, the
    second parameter being the index and can take any number of additional
    parameters and keyword arguments.

    :param client: The client to use for the simulations.
    :type client:  Client
    :param number: The number of simulations to run.
    :type number:  int
    :param main:   The main function to run with each simulation.
    :type main:    callable
    :param args:   Additional positional arguments to pass to the main function.
    :type args:    tuple
    :param dispose: Whether to dispose of the simulation handles after running
    :type dispose: bool
    :param kwargs: Additional keyword arguments to pass to the main function.
    :type kwargs: dict

    :return:       None
    :rtype:        None
    """

    # Define an asynchronous function to create a simulation and run the main function
    async def create_simulation(client: Client) -> Simulation:
        return await Simulation.create(client)

    # Define an asynchronous function to run the main function with the simulation
    async def run_and_dispose(sim: Simulation, i, *args, **kwargs):
        try:
            await main(sim, i, *args, **kwargs)
        finally:
            if dispose and sim.is_valid():
                await sim.dispose()

    # Define an asynchronous function to run all simulations concurrently
    async def run_all():
        # Create all simulations concurrently
        simulations = await asyncio.gather(
            *(create_simulation(client) for _ in range(number))
        )
        # Run the main function for each simulation concurrently, then dispose
        tasks = [
            asyncio.create_task(run_and_dispose(sim, i, *args, **kwargs))
            for i, sim in enumerate(simulations)
        ]
        await asyncio.gather(*tasks)

    # Run the asynchronous function to run all simulations
    asyncio.run(run_all())
