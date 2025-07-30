#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

import json


def create_command(command: str, parameters: dict, time: float = 0.0) -> dict:
    """
    Creates a command with a list of arguments as the parameters. This will create the JSON
    object with the list of parameters required.

    :param command: The command to execute.
    :type command: str
    :param parameters: The parameter dictionary containing keys and values for the command.
    :type parameters: dict
    :param time: The time [s] that the command must be executed at, default is 0.0.
    :type time: float, optional
    :return: The JSON command that can be used.
    :rtype: dict
    """
    # Initialize an empty command dictionary
    cmd = {}

    # Set the 'command' field of the JSON object
    cmd["command"] = command

    # Initialize an empty dictionary for parameters
    param_obj = {}

    # Iterate through the parameters and add them to the dictionary
    for key, value in parameters.items():
        param_obj[key] = value

    # Set the 'parameters' field of the JSON object
    cmd["parameters"] = param_obj

    # Add the timestamp to the JSON object
    cmd["_t"] = time

    # Return the complete command object (JSON)
    return cmd


def create_guidance_command(
    navigation: str = "Simple",
    pointing: str = "Inertial",
    controller: str = "MRP",
    mapping: str = "ReactionWheels",
    time: float = 0.0,
) -> dict:
    """
    Creates a guidance command for the spacecraft operation computer to execute
    once loaded into the system at a particular time.

    :param navigation: The navigation mode to set (default is "Simple").
    :type navigation: str, optional
    :param pointing: The pointing mode to set (default is "Inertial").
    :type pointing: str, optional
    :param controller: The controller mode to set (default is "MRP").
    :type controller: str, optional
    :param mapping: The mapping mode to set (default is "ReactionWheels").
    :type mapping: str, optional
    :param time: The time [s] at which the command is executed, default is 0.0.
    :type time: float, optional
    :return: The appropriate command JSON to be executed.
    :rtype: dict
    """
    # Create a dictionary of arguments with navigation, pointing, controller, and mapping types
    args = {
        "navigation": navigation,
        "pointing": pointing,
        "controller": controller,
        "mapping": mapping,
    }

    # Return the generated command by calling create_command with the arguments
    return create_command("guidance", args, time)


def create_guidance_command_string(
    navigation: str, pointing: str, controller: str, mapping: str, time: float
) -> str:
    """
    Creates a guidance command for the spacecraft operation computer and returns it as a JSON string.

    :param navigation: The navigation mode to set.
    :type navigation: str
    :param pointing: The pointing mode to set.
    :type pointing: str
    :param controller: The controller mode to set.
    :type controller: str
    :param mapping: The mapping mode to set.
    :type mapping: str
    :param time: The time [s] at which the command is executed.
    :type time: float
    :return: The JSON command as a string.
    :rtype: str
    """
    # Generate the command as a dictionary
    command = create_guidance_command(navigation, pointing, controller, mapping, time)

    # Convert the command dictionary to a JSON string and return it
    return json.dumps(command)
