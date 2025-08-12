#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

import paho.mqtt.client as mqtt
from typing import Callable
import uuid as Guid
import json, time
from ..utils import printer


# These are some static constants for the client
HIVEMQ_SERVER: str = "broker.hivemq.com"
"""The default MQTT server that is being used to communicate with the clients."""

SERVER_PORT: int = 1883
"""The default MQTT server port that is being used for the protocol."""

SERVER_TIMEOUT: int = 5
"""The server timeout in seconds to keep the connection alive for."""


class MqttClient:
    """
    This client acts as an MQTT interface with python, allowing for
    callbacks from topic subscriptions and publishing messages over
    topics. This acts as a wrapper for the Paho MQTT client, which
    must be installed to work correctly.
    """

    server: str = ""
    """Defines the name of the server being used to communicate with."""

    client_name: str = ""
    """Defines the unique name of the client."""

    connected: bool = False
    """A flag for if the MQTT client is connected to the server."""

    fail: bool = False
    """A flag for if a failure to communicate with the server occurred."""

    callbacks: dict = {}
    """A mapping of topic to functions to callback as a dictionary."""

    def __init__(self, server: str = HIVEMQ_SERVER) -> None:
        """
        Initialiases the client with a particular server, defaulted
        to the HiveMQT server. This will also settup the delegate
        function calls.

        :param server:  The name of the server to connect to
        :type server:   str
        """

        self.server = server
        self.client_name = str(Guid.uuid4())

        # Create the client
        self.client = mqtt.Client(self.client_name)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.on_connect_fail = self.__on_connect_fail

    def add_callback(self, topic: str, func: Callable[[str], None]) -> None:
        """
        Adds a particular function callback to the data when received over
        a topic. The callback function must be in the form of 'def func (data: str)'.
        Multiple functions can be added to each topic and will execute each
        of the functions with the same data.

        :param topic:   The topic name that should have a callback with
        :type topic:    str
        :param func:    The callback function when the topic receives data, in the form of func (data: str)
        :type func:     Callable
        """

        # Ensure the client has already connected
        if not self.connected:
            printer.error(
                "Failed to subscribe to topic. Mqtt client is not yet connected."
            )
            return

        # Check if the callback exists
        if topic in self.callbacks.keys():
            list(self.callbacks[topic]).append(func)

        # Add a new callback array
        else:
            self.client.subscribe(topic)
            self.callbacks[topic] = [func]

        # Add a message
        printer.log("Successfully subscribed to topic '%s'." % topic)

    def connect(self, wait: bool = False) -> None:
        """
        This method begins to connect to the server and makes
        sure that it will run until shutdown. If the wait flag
        is enabled, it will throttle the thread until a valid
        connection has been made.

        :param wait:    A flag whether to wait until the connection is reached and pause the thread
        :type wait:     bool
        """

        # Connect to the server
        self.client.connect(self.server, SERVER_PORT, SERVER_TIMEOUT)

        # Loop until connected
        printer.log(
            "Mqtt client '%s' is attempting to connect to the server..."
            % self.client_name
        )
        self.client.loop_start()

        # Wait for the connection if required
        if wait:
            self.wait_for_connection()

    def wait_for_connection(self, timeout: float = 3.0) -> bool:
        """
        Waits for a valid connection after calling connect. This will wait
        for a certain time until it time's out and returns out of the loop.

        :param timeout: The timeout in seconds for the connection to wait for
        :type timeout:  float

        :returns:       A valid connection flag if a connection has been reached
        :rtype:         bool
        """

        ticks: int = int(float(timeout) / 0.1)
        for _ in range(ticks):
            if self.connected:
                return True
            time.sleep(0.1)
        printer.warning("Failed to connect with a timeout of %f seconds." % timeout)
        return False

    def __on_connect(self, client, userdata, flags, rc):
        """
        This handles the callback from the connection and
        will display a message outlining if it has been connected.
        """

        printer.log("Mqtt client has connected with result code: '%s'." % str(rc))
        self.connected = True

    def __on_connect_fail(self):
        """
        This method is executed if the connection with a server fails
        and is unable to connect.
        """

        printer.error("Mqtt client has failed to connect.")
        self.fail = True

    def __on_message(self, client, userdata, message):
        """
        Handles when a particular message has come through
        the system. This will redirect a message to a callback
        unless otherwise noted.
        """

        # Check if the topic is valid
        if message.topic not in self.callbacks.keys():
            printer.warning("Undefined message on topic '%s'." % message.topic)

        # Execute each of the callbacks
        else:

            # Fetch the data as a string or a byte array
            data = None
            try:
                data = message.payload.decode()
            except:
                data = message.payload

            # Execute each of the functions with the data
            for func in self.callbacks[message.topic]:
                func(data)

    def publish(self, topic: str, data: str) -> None:
        """
        Publishes some data over a particular topic, assuming it is
        string data.

        :param topic:   The topic to publish the data over the MQTT connection
        :type topic:    str
        :param data:    The data to publish over the MQTT topic
        :type data:     str
        """

        self.client.publish(topic, payload=data)
        printer.log("Published a message over the topic '%s'." % topic)

    def publish_json(self, topic: str, data: dict) -> None:
        """
        Publishes some JSON data over a particular topic, assuming it
        is in the form of a dictionary or some other JSON configurable
        object.

        :param topic:   The topic to publish the data over the MQTT connection
        :type topic:    str
        :param data:    The JSON value to publish over the MQTT topic
        :type data:     dict
        """

        data_str: str = json.dumps(data)
        self.publish(topic, data_str)
