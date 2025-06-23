"""
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2025.
"""

from typing import Optional, Dict, Union
from nominalpy.utils import printer, NominalException
import asyncio, aiohttp, json, atexit
import requests, time
from typing import Optional, Union, Dict, Any, List
from nominalpy import __version__ as nominalpy_version


class Client:
    """
    A simple client to handle HTTP requests to an API.
    Each simulation ID processes requests sequentially using its own session.
    """

    def __init__(self, url: str = "https://api.zendir.io", token: Optional[str] = None):
        """
        Initialize the client with a base URL and optional token.

        :param url: The base URL for the API.
        :param token: Authentication token for requests.
        """
        self.base_url = url.rstrip("/") + "/"
        self.url = ""
        self.session = ""
        self.token = token
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.queues: Dict[str, asyncio.Queue] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self._closed = False
        atexit.register(self._sync_cleanup)

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
                    if "version" not in session or session["version"] == version
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
            print("No token provided, using base URL for API requests.")

    def _sync_cleanup(self):
        """
        Synchronous cleanup for program exit.
        """
        if self._closed:
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(self._close())
            if not loop.is_closed():
                loop.close()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._close())
            loop.close()
        except Exception:
            pass

    def __del__(self):
        """
        Ensure cleanup when the object is garbage-collected.
        """
        if not self._closed:
            self._sync_cleanup()

    async def _close(self):
        """
        Close all sessions and cancel tasks.
        """
        if self._closed:
            return
        self._closed = True
        for id, task in self.tasks.items():
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        for id, session in self.sessions.items():
            if not session.closed:
                await session.close()
        self.sessions.clear()
        self.queues.clear()
        self.tasks.clear()

    async def _process_requests(self, id: str):
        """
        Process requests for a simulation ID sequentially.

        :param id: The simulation ID.
        """
        queue = self.queues.get(id)
        if not queue:
            return
        if id not in self.sessions:
            self.sessions[id] = aiohttp.ClientSession(trust_env=True)
        session = self.sessions[id]

        while not self._closed:
            future = None
            try:
                async with asyncio.timeout(60.0):
                    method, endpoint, data, future = await queue.get()

                if session.closed:
                    if not future.done():
                        future.set_exception(NominalException("Session closed"))
                    queue.task_done()
                    continue

                headers = {"Accept": "application/json"}
                if self.token:
                    headers["X-Api-Key"] = self.token
                timeout = aiohttp.ClientTimeout(total=60.0)

                body = None
                if isinstance(data, str):
                    headers["Content-Type"] = "text/plain"
                    body = data.encode("utf-8") if data else None
                elif isinstance(data, (list, dict)):
                    headers["Content-Type"] = "application/json"
                    body = data
                elif data is None:
                    headers["Content-Type"] = "application/json"
                    body = None
                else:
                    if not future.done():
                        future.set_exception(
                            ValueError("Data must be a string, list, dict, or None")
                        )
                    queue.task_done()
                    continue

                url = f"{self.url}{endpoint.lstrip('/')}"

                # Print the request details for debugging
                printer.log(f"Requesting {method} {url} with data: {body}")

                for attempt in range(3):
                    try:
                        async with session.request(
                            method,
                            url,
                            json=body if isinstance(body, (list, dict)) else None,
                            data=body if not isinstance(body, (list, dict)) else None,
                            headers=headers,
                            timeout=timeout,
                        ) as response:
                            content = await response.read()
                            if response.status != 200:
                                content_data: str = (
                                    content.decode("utf-8") if content else None
                                )
                                raise NominalException(
                                    f"Request failed: {response.status} {content_data}"
                                )
                            result = None
                            if content:
                                try:
                                    result = json.loads(content)
                                except json.JSONDecodeError:
                                    result = content.decode("utf-8")

                            # Print the response details for debugging
                            printer.log(f"Response from {method} {url}: {result}.")

                            if not future.done():
                                future.set_result(result)
                            break
                    except (aiohttp.ClientError, NominalException) as e:
                        if attempt < 2:
                            await asyncio.sleep(1)
                            continue
                        if not future.done():
                            future.set_exception(
                                NominalException(f"Request failed: {e}")
                            )
                queue.task_done()
            except asyncio.TimeoutError:
                if queue.empty() and self._closed:
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                if future is not None and not future.done():
                    future.set_exception(e)
                try:
                    if "queue" in locals():
                        queue.task_done()
                except:
                    pass

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[str, list, dict]] = None,
        id: str = "default",
    ):
        """
        Make an HTTP request for a given simulation ID.

        :param method: HTTP method (GET, POST, etc.).
        :param endpoint: API endpoint.
        :param data: Data to send with the request.
        :param id: Simulation ID for sequential processing.
        :return: Response data as a dictionary or string.
        """
        if self._closed:
            raise RuntimeError("Client is closed")
        if id not in self.queues:
            self.queues[id] = asyncio.Queue()
            self.tasks[id] = asyncio.create_task(self._process_requests(id))

        future = asyncio.Future()
        await self.queues[id].put((method, endpoint, data, future))
        try:
            async with asyncio.timeout(200.0):
                return await future
        except asyncio.TimeoutError:
            if not future.done():
                future.set_exception(NominalException("Request timed out"))
            raise

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
        return await self._request("GET", endpoint, id=id)

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
        return await self._request("POST", endpoint, data, id=id)

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
        return await self._request("DELETE", endpoint, id=id)

    @classmethod
    def create_local(cls, port: int = 25565) -> "Client":
        """
        Create a local client with the specified port and request limits.

        :param port: The port to use for the local client.
        :type port: int
        :param max_requests_per_client: The maximum number of requests per client.
        :type max_requests_per_client: int
        :param max_total_concurrent_requests: The maximum number of total concurrent requests.
        :type max_total_concurrent_requests: int

        :return: A new local client.
        :rtype: Client
        """
        return Client(url=f"http://localhost:{port}")

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
        response = requests.get(
            f"{self.base_url}", headers={"X-Api-Key": self.token}, timeout=10
        )

        # Check if the response was successful
        if response.status_code != 200:
            raise NominalException(
                f"Failed to list sessions with error: {response.status_code} {response.text}"
            )

        # Assume the response is a JSON array
        try:
            session_info = response.json()
        except json.JSONDecodeError:
            raise NominalException("Failed to decode response from server.")

        # Ensure the response is a list of session IDs
        if not isinstance(session_info, list):
            raise NominalException(
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
                raise NominalException(
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
        Fetch the version of the nominalpy package. This will return the version as a string.

        :return: The version of the nominalpy package.
        :rtype: str
        """

        # Fetch the version of 'nominalpy' to ensure compatibility
        version: str = ".".join(nominalpy_version.split(".")[:3])
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

        # Fetch the version of 'nominalpy' to ensure compatibility
        version: str = self.get_version()

        # Create the data for the POST, including the version property
        data: dict = {
            "version": version,
        }

        # Print a warning that the session is being created
        printer.info(f"Creating a new session with version '{version}'.")

        # Make a POST request to the API endpoint for creating a session
        response = requests.post(
            f"{self.base_url}", headers={"X-Api-Key": self.token}, timeout=10, json=data
        )

        # Check if the response was successful
        if response.status_code != 200:
            raise NominalException(
                f"Failed to create session: {response.status_code} {response.text}"
            )

        # Assume the response is a dictionary
        try:
            session_info = response.json()
        except json.JSONDecodeError:
            raise NominalException(
                "Failed to decode response from server when creating a session."
            )

        # If there is no 'guid' in the response, raise an exception
        if "guid" not in session_info:
            raise NominalException(
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
        response = requests.delete(
            f"{self.base_url}{session_id}/",
            headers={"X-Api-Key": self.token},
            timeout=10,
        )

        # Check if the response was successful
        if response.status_code != 200:
            raise NominalException(
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
