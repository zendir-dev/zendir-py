"""
                    [ ZENDIR ]
This code is developed by Zendir to aid with communication
to the public API. All code is under the the license provided
with the 'zendir' module. Copyright Zendir, 2025.
"""

from typing import Optional, Dict, Union
from zendir.utils import printer, ZendirException, helper
import asyncio, aiohttp, json, atexit
import requests, time
from typing import Optional, Union, Dict, Any, List
from zendir import __version__ as zendir_version
from zendir.http import rqst


class Client:
    """
    A simple client to handle HTTP requests to an API.
    Each simulation ID processes requests sequentially using its own session.
    """

    def __init__(
        self,
        url: str = "https://api.zendir.io/v2.0",
        token: Optional[str] = None,
        timeout: Optional[float] = 30,
    ):
        """
        Initialize the client with a base URL and optional token.

        :param url: The base URL for the API.
        :param token: Authentication token for requests.
        """
        self.base_url = url.rstrip("/") + "/"
        self.url = ""
        self.session = ""
        self.token = token
        self.timeout = timeout

        # Fetch the session token if provided
        if self.token != None:

            # Fetch the session information
            self.session_info: List[dict] = self.__get_session_info()

            # If there is an active session, set the URL
            if len(self.session_info) > 0:

                # Find the first session that has a 'version' that matches the version
                version: str = self.get_version()
                valid_sessions: List[str] = [
                    session["guid"]
                    for session in self.session_info
                    if ("version" not in session or session["version"] == version)
                    and helper.is_valid_guid(session["guid"])
                ]

                # If there are no valid sessions, use the first session
                if len(valid_sessions) == 0:

                    # Try to create a new session with the current version
                    try:
                        session_id: str = self.create_session()

                    # If the session, creation fails
                    except Exception as e:

                        # Ask the user if they would like to delete the old sessions
                        input: str = input(
                            "An session with a different version exists. Would you like to delete it? (y/n): "
                        )

                        # If the user wants to delete the old sessions, delete all sessions and then create a new session
                        if input.lower() == "y":
                            for session in self.session_info:
                                self.delete_session(session["guid"])
                            session_id: str = self.create_session()

                        # Otherwise, just use the first session
                        else:
                            session_id = self.session_info[0]["guid"]
                            printer.warning(
                                "Using the first session with a different version. This may cause compatability issues."
                            )

                # If more than one valid session, use the first valid session that is in a 'RUNNING' state
                elif len(valid_sessions) > 1:
                    session_id: str = next(
                        (
                            session["guid"]
                            for session in self.session_info
                            if session["guid"] in valid_sessions
                            and session["status"] == "RUNNING"
                        ),
                        valid_sessions[0],
                    )
                    if not session_id:
                        session_id = valid_sessions[0]

                # Otherwise, use the first valid session
                else:
                    session_id: str = valid_sessions[0]

                # Wait for the session to become active
                self.__wait_for_session(session_id)

                # Session is good to go, set the URL
                self.url = f"{self.base_url}{session_id}/"
                printer.success(
                    f"Successfully connected to the API session '{session_id}'."
                )

            # If there are no active sessions, create a new session
            else:

                # Create a new session and wait for it to become active
                session: str = self.create_session()
                self.__wait_for_session(session)

                # Session is good to go, set the URL
                self.url = f"{self.base_url}{session}/"
                printer.success(
                    f"Successfully created and connected to a new API session '{session}'."
                )

        # If there is no token, set the URL to the base URL
        else:
            self.url = self.base_url
            if "127.0.0.1" not in self.url and "localhost" not in self.url:
                printer.warning(
                    "No token provided. Using the base URL for API requests. "
                    "This may not work as expected without authentication."
                )

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[str, list, dict]] = None,
    ):
        """
        Make an HTTP request for a given simulation ID.

        :param method: HTTP method (GET, POST, etc.).
        :param endpoint: API endpoint.
        :param data: Data to send with the request.
        :return: Response data as a dictionary or string.
        """

        url = f"{self.url}{endpoint.lstrip('/')}"
        printer.log(f":: {method} {url} {data}")
        return await rqst(method, url, data, { "X-Api-Key": self.token } if self.token else None)

    async def get(self, endpoint: str, id: str = "default"):
        """
        Perform an async GET request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]
        :param id: The ID of the context for the client, if applicable.
        :type id: str

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("GET", endpoint)

    async def post(
        self, endpoint: str, data: Optional[Any] = None, id: str = "default"
    ):
        """
        Perform an async POST request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]
        :param id: The ID of the context for the client, if applicable.
        :type id: str

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("POST", endpoint, data)

    async def delete(self, endpoint: str, id: str = "default"):
        """
        Perform an async DELETE request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]
        :param id: The ID of the context for the client, if applicable.
        :type id: str

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("DELETE", endpoint)

    @classmethod
    def create_local(cls, port: int = 25565, timeout: float = 30.0) -> "Client":
        """
        Create a local client with the specified port and request limits.

        :param port: The port to use for the local client.
        :type port: int
        :param timeout: The timeout for requests in seconds.
        :type timeout: float

        :return: A new local client.
        :rtype: Client
        """
        return Client(url=f"http://127.0.0.1:{port}", timeout=timeout)

    def __get_session_info(self) -> List[dict]:
        """
        Returns a list of all session information for the client, assuming a particular
        token is provided. This will return a list of dictionaries, each containing
        information about a session, including the 'guid' of the session, the 'status' of
        the session and the 'version' of the session.

        :return: A list of dictionaries containing session information.
        :rtype: List[dict]
        """

        # Check if the token is provided
        if self.token is None or self.token == "":
            raise ValueError("Token must be provided to list sessions.")

        # Make a GET request to the API endpoint for listing sessions, using the requests library
        printer.log(f"Requesting session information from {self.base_url}.")
        response = requests.get(
            f"{self.base_url}", headers={"X-Api-Key": self.token}, timeout=10
        )
        printer.log(f"Response status code: {response.status_code}")

        # Check if the response was successful
        if response.status_code != 200:
            raise ZendirException(
                f"Failed to list sessions with error: {response.status_code} {response.text}"
            )

        # Assume the response is a JSON array
        try:
            session_info = response.json()
        except json.JSONDecodeError:
            raise ZendirException("Failed to decode response from server.")

        # Ensure the response is a list of session IDs
        if not isinstance(session_info, list):
            raise ZendirException(
                "Failed to list sessions as the server response was not a list."
            )

        # Return the session information
        return session_info

    def __wait_for_session(self, session_id: str, timeout: int = 300) -> bool:
        """
        Waits for a session to become active. This will block until the session is active
        or the timeout is reached. The session will be considered active if the 'status' is
        'RUNNING'. It will make a request every 3 seconds to check the status of the session.

        :param session_id: The ID of the session to wait for.
        :type session_id: str
        :param timeout: The maximum time to wait for the session to become active, in seconds.
        :type timeout: int

        :return: True if the session becomes active, False if the timeout is reached.
        :rtype: bool
        """

        # If there is no session information yet, get it
        if self.session_info is None:
            self.session_info = self.__get_session_info()

        # Adds a flag to print the first time
        first_print: bool = True

        # Get the start time
        start_time = time.time()
        while True:

            # Check if the session is in the session information and is active
            for session in self.session_info:
                if session["guid"] == session_id and session["status"] == "RUNNING":
                    return True

            # If the session is not active, check if the timeout has been reached
            if time.time() - start_time > timeout:
                raise ZendirException(
                    f"Session {session_id} did not become active within {timeout} seconds."
                )

            # If this is the first time, print the message
            if first_print:
                printer.warning(
                    f"Waiting for session '{session_id}' to become active. This may take a few seconds."
                )
                first_print = False

            # Fetch the session information again
            self.session_info = self.__get_session_info()

            # Sleep for 3 seconds before checking again
            time.sleep(3)

    def get_version(self) -> str:
        """
        Fetch the version of the zendir package. This will return the version as a string.

        :return: The version of the zendir package.
        :rtype: str
        """

        # Fetch the version of 'zendir' to ensure compatibility
        version: str = ".".join(zendir_version.split(".")[:3])
        if len(version.split(".")) == 2:
            version += ".0"
        return version

    def create_session(self) -> str:
        """
        Create a new session and return its ID. This will make a POST request to the API
        endpoint for creating a session. The session will be created with the provided token.

        :return: The ID of the newly created session.
        :rtype: str
        """

        # Check if the token is provided
        if self.token is None or self.token == "":
            raise ValueError("Token must be provided to create a session.")

        # Fetch the version of 'zendir' to ensure compatibility
        version: str = self.get_version()

        # Create the data for the POST, including the version property
        data: dict = {
            "version": version,
        }

        # Print a warning that the session is being created
        printer.info(f"Creating a new session with version '{version}'.")

        # Make a POST request to the API endpoint for creating a session
        printer.log(
            f"Requesting session creation at {self.base_url} with data: {data}."
        )
        response = requests.post(
            f"{self.base_url}", headers={"X-Api-Key": self.token}, timeout=60, json=data
        )
        printer.log(f"Response status code: {response.status_code}")

        # Check if the response was successful
        if response.status_code != 200:
            raise ZendirException(
                f"Failed to create session: {response.status_code} {response.text}"
            )

        # Assume the response is a dictionary
        try:
            session_info = response.json()
        except json.JSONDecodeError:
            raise ZendirException(
                "Failed to decode response from server when creating a session."
            )

        # If there is no 'guid' in the response, raise an exception
        if "guid" not in session_info:
            raise ZendirException(
                "Failed to create session: 'guid' not found in response."
            )

        # Return the session ID
        return session_info["guid"]

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session with the given session ID. This will make a DELETE request to the API
        endpoint for deleting a session.

        :param session_id: The ID of the session to delete.
        :type session_id: str
        """

        # Check if the token is provided
        if self.token is None or self.token == "":
            raise ValueError("Token must be provided to delete a session.")

        # Make a DELETE request to the API endpoint for deleting a session
        printer.log(f"Requesting session deletion at {self.base_url}{session_id}/.")
        response = requests.delete(
            f"{self.base_url}{session_id}/",
            headers={"X-Api-Key": self.token},
            timeout=10,
        )
        printer.log(f"Response status code: {response.status_code}")

        # Check if the response was successful
        if response.status_code != 200:
            raise ZendirException(
                f"Failed to delete session {session_id}: {response.status_code} {response.text}"
            )

        # Delete the session from the session information
        printer.success(f"Session '{session_id}' deleted successfully.")

    def list_sessions(self) -> List[str]:
        """
        List all active sessions for the given token. This will return
        a list of session IDs.

        :return: A list of session IDs.
        :rtype: List[str]
        """

        # Get the session information
        self.session_info: List[dict] = self.__get_session_info()

        # Loop through all the sessions and extract the session IDs
        session_list: List[str] = []
        for session in self.session_info:

            # Get the session ID from the session information
            guid: str = session["guid"]
            session_list.append(guid)

        # Return the list of session IDs
        return session_list

    def get_chunk_size(self) -> int:
        """
        Get the maximum chunk size for the client. This is used to limit the size of
        requests to the API.

        :return: The maximum chunk size.
        :rtype: int
        """
        if "127.0.0.1" in self.url or "localhost" in self.url:
            return 1024 * 1024  # 1 MB for local API
        return 6000  # 16 KB for cloud API
