#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

import json


def create_command(trigger: dict, command: str, parameters: dict, priority: int = 0) -> dict:
    """
    Creates a command with a list of arguments as the parameters. This will create the JSON
    object with the list of parameters required.

    :param trigger: The trigger for the command.
    :type trigger: dict
    :param command: The command to execute.
    :type command: str
    :param parameters: The parameter dictionary containing keys and values for the command.
    :type parameters: dict
    :param priority: The priority of the command, default is 0.
    :type priority: int, optional
    :return: The JSON command that can be used.
    :rtype: dict
    """
    # Initialize an empty command dictionary
    cmd = {}

    # Set the 'command' field of the JSON object
    cmd["Trigger"] = trigger
    cmd["Type"] = command

    # Initialize an empty dictionary for parameters
    param_obj = {}

    # Iterate through the parameters and add them to the dictionary
    for key, value in parameters.items():
        param_obj[key] = value

    # Set the 'parameters' field of the JSON object
    cmd["Parameters"] = param_obj

    # Set the 'priority' field of the JSON object
    cmd["Priority"] = priority

    # Return the complete command object (JSON)
    return cmd


def create_guidance_start_command(
    trigger: dict,
    navigation: str = "Simple",
    pointing: str = "Inertial",
    controller: str = "MRP",
    mapping: str = "ReactionWheels",
    priority: int = 0,
) -> dict:
    """
    Creates a guidance command for the spacecraft operation computer to execute
    once loaded into the system at a particular time.

    :param trigger: The trigger for the command.
    :type trigger: dict
    :param navigation: The navigation mode to set (default is "Simple").
    :type navigation: str, optional
    :param pointing: The pointing mode to set (default is "Inertial").
    :type pointing: str, optional
    :param controller: The controller mode to set (default is "MRP").
    :type controller: str, optional
    :param mapping: The mapping mode to set (default is "ReactionWheels").
    :type mapping: str, optional
    :param priority: The priority of the command, default is 0.
    :type priority: int, optional
    :return: The appropriate command JSON to be executed.
    :rtype: dict
    """
    # Create a dictionary of arguments with navigation, pointing, controller, and mapping types
    args = {
        "Navigation": navigation,
        "Pointing": pointing,
        "Controller": controller,
        "Mapping": mapping,
    }

    # Return the generated command by calling create_command with the arguments
    return create_command(trigger, "GuidanceStart", args, priority)

def create_guidance_configure_command(
    trigger: dict,
    parameters: dict,
    priority: int = 0,
) -> dict:
    """
    Creates a guidance configure command for the spacecraft operation computer to execute
    once loaded into the system.

    :param trigger: The trigger for the command.
    :type trigger: dict
    :param parameters: The parameter dictionary containing keys and values for the command.
    :type parameters: dict
    :param priority: The priority of the command, default is 0.
    :type priority: int, optional
    :return: The appropriate command JSON to be executed.
    :rtype: dict
    """
    # Return the generated command by calling create_command with the arguments
    return create_command(trigger, "GuidanceConfigure", parameters, priority)

# def create_guidance_command_string(
#     navigation: str, pointing: str, controller: str, mapping: str, time: float
# ) -> str:
#     """
#     Creates a guidance command for the spacecraft operation computer and returns it as a JSON string.

#     :param navigation: The navigation mode to set.
#     :type navigation: str
#     :param pointing: The pointing mode to set.
#     :type pointing: str
#     :param controller: The controller mode to set.
#     :type controller: str
#     :param mapping: The mapping mode to set.
#     :type mapping: str
#     :param time: The time [s] at which the command is executed.
#     :type time: float
#     :return: The JSON command as a string.
#     :rtype: str
#     """
#     # Generate the command as a dictionary
#     command = create_guidance_command(navigation, pointing, controller, mapping, time)

#     # Convert the command dictionary to a JSON string and return it
#     return json.dumps(command)

def create_event_trigger(type: str, repeat: bool = False, is_done: bool = False) -> dict:
    """
    Creates a event trigger command for the spacecraft operation computer to execute
    once loaded into the system.

    :param type: The type of event trigger to create.
    :type type: str
    :param repeat: Whether the event trigger should repeat, default is False.
    :type repeat: bool, optional
    :param is_done: Whether the event trigger is done, default is False.
    :type is_done: bool, optional
    :return: An event trigger for a command.
    :rtype: dict
    """
    # Create a dictionary of arguments with type, repeat, and is_done
    args = {
        "Type": type,
        "Repeat": repeat,
        "IsDone": is_done,
    }

    return args

def create_time_event_trigger(time: float, interval: float = 0.0, repeat: bool = False, is_done: bool = False) -> dict:
    """
    Creates a time event trigger command for the spacecraft operation computer to execute
    once loaded into the system. It will repeat at the interval specified.

    :param time: The time [s] at which the event trigger is executed.
    :type time: float
    :param interval: The interval [s] at which the event trigger is executed.
    :type interval: float
    :param repeat: Whether the event trigger should repeat, default is False.
    :type repeat: bool, optional
    :param is_done: Whether the event trigger is done, default is False.
    :type is_done: bool, optional
    :return: An event trigger for a command based on time.
    :rtype: dict
    """
    # Create a dictionary of arguments with time and interval
    args = create_event_trigger("Time", repeat, is_done)
    args["Time"] = time
    args["Interval"] = interval

    return args

def create_parameter_event_trigger(object_id: str, parameter_name: str, value: float, operator: str, repeat: bool = False, is_done: bool = False) -> dict:
    """
    Creates a parameter event trigger command for the spacecraft operation computer to execute
    once loaded into the system.

    :param object_id: The ID of the object to trigger the event on.
    :type object_id: str
    :param parameter_name: The name of the parameter to trigger the event on.
    :type parameter_name: str
    :param value: The value of the parameter to trigger the event on.
    :type value: float
    :param operator: The operator to use for the event trigger.
    :type operator: str
    :param repeat: Whether the event trigger should repeat, default is False.
    :type repeat: bool, optional
    :param is_done: Whether the event trigger is done, default is False.
    :type is_done: bool, optional
    :return: An event trigger for a command based on a parameter.
    :rtype: dict
    """
    args = create_event_trigger("Parameter", repeat, is_done)
    args["ObjectID"] = object_id
    args["ParameterName"] = parameter_name
    args["Value"] = value
    args["Operator"] = operator

    return args