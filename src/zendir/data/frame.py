#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.

from __future__ import annotations
import json, os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from .. import ZendirException


class SimulationData:
    """
    The DataFrame class is able to store a series of parameters and data associated
    with a particular simulation instance. This class is a pure data class and is
    not able to invoke any methods. It is able to store the data in a structured
    format and is able to be exported to a JSON format.
    """

    __raw: dict = {}
    """Defines the raw data that is fetched from the API."""

    type: str = ""
    """Defines the object type that was used for this SimulationData."""

    id: str = ""
    """Defines the unique GUID identifier of the object. This needs to be in the correct GUID format."""

    fields: list = []
    """Defines the fields that are associated with the SimulationData."""

    data: list = []
    """Defines the data that is associated with the SimulationData."""

    def __init__(self, data: dict) -> None:
        """
        Initialises the SimulationData with the data that is fetched from the API. This must be
        created using the JSON data that is fetched from the API and is able to be exported
        back to the API in the same format.

        :param data:    The data that is fetched from the API
        :type data:     dict
        """

        # Reset the data
        self.id = ""
        self.type = ""
        self.fields = []
        self.data = []
        self.__raw = data

        # Fetch the header values
        if "ID" in data:
            self.id = data["ID"]
        if "Type" in data:
            self.type = data["Type"]
        if "Data" not in data:
            raise ZendirException(
                "Data not found. Please ensure the queried data name is correct and has been tracked."
            )

        # Data should be an array of arrays
        data = list(data["Data"])
        if len(data) == 0:
            raise ZendirException(
                "SimulationData Data is empty. Please ensure the queried data name is correct and has been tracked."
            )
        self.fields = data[0]

        # Loop through the data
        for i in range(1, len(data)):
            self.data.append(data[i])

    @classmethod
    def load(cls, path: str) -> SimulationData:
        """
        Loads a SimulationData from a file path and returns the SimulationData object. This is a
        class method and does not require an instance to be created.

        :param path:    The path to the file that contains the SimulationData
        :type path:     str

        :returns:       The SimulationData object that is loaded from the file
        :rtype:         SimulationData
        """

        # Check if the path is not valid and throw exception
        if not path or not os.path.exists(path):
            raise ZendirException("Invalid path provided to load SimulationData.")
        return SimulationData(json.loads(path))

    def get_times(self) -> np.ndarray:
        """
        Returns the time values that are associated with the SimulationData. This is a helper
        function that is able to fetch the time values from the SimulationData, where each
        value is in seconds.

        :returns:   The time values that are associated with the SimulationData in seconds
        :rtype:     np.ndarray
        """

        # Ensure that the time is casted as a float as a numpy arra
        times = [float(x) for x in self.get_values("Time")]

        # Convert and return as a numpy array
        return np.array(times)

    def get_values(self, parameter: str) -> np.ndarray:
        """
        Returns the values that are associated with a particular parameter in the SimulationData.
        This is a helper function that is able to fetch the values associated with a particular
        parameter in the SimulationData.

        :param parameter:   The parameter to fetch the values for
        :type parameter:    str

        :returns:           The values that are associated with the parameter
        :rtype:             np.ndarray
        """

        # Check if the parameter does not exist
        if parameter not in self.fields:
            raise ZendirException(
                f"Parameter '{parameter}' not found in SimulationData."
            )

        # Fetch the index and data associated with it
        index = self.fields.index(parameter)
        values: list = [row[index] for row in self.data]
        return np.array(values)

    def plot(self, title="Simulation Data", params=None) -> None:
        """
        Creates a quick plot of the SimulationData data. This will plot the data in a simple
        line plot format and will display the data in a single plot or multiple plots
        depending on the parameters provided. The following formats for the parameters
        will work:

        params = "MyParam"                    -> will plot 'MyParam' against Time in a single plot
        params = ["MyParam1", "MyParam2"]     -> will plot 'MyParam1' and 'MyParam2' against Time in a single plot
        params = [["MyParam1"], ["MyParam2"]] -> will plot 'MyParam1' and 'MyParam2' against Time in separate plots

        :param title:   The title of the plot
        :type title:    str
        :param params:  The parameters to plot
        :type params:   str or list
        """

        # Ensure params is initialized to an empty list if not provided
        if params is None:
            params = []

        # Check if params is a single string (single parameter case)
        if isinstance(params, str):
            params = [params]  # Convert to a list to handle uniformly

        # Check if params is a list of lists (multiple plots case)
        if all(isinstance(item, list) for item in params):
            _, axs = plt.subplots(len(params), 1, figsize=(8, len(params) * 4))
            # Ensure axs is always a list (even if there's only one subplot)
            if len(params) == 1:
                axs = [axs]

            for ax, param_list in zip(axs, params):
                for parameter in param_list:
                    ax.plot(
                        self.get_times(), self.get_values(parameter), label=parameter
                    )
                ax.set(xlabel="Time [s]", ylabel="Value", title=title)
                ax.grid()
                ax.legend()
        else:
            # Handle the case where params is a flat list
            _, ax = plt.subplots()
            for parameter in params:
                ax.plot(self.get_times(), self.get_values(parameter), label=parameter)
            ax.set(xlabel="Time [s]", ylabel="Value", title=title)
            ax.grid()
            ax.legend()

        # Display the plots on the screen
        plt.tight_layout()
        plt.show()

    def export(self) -> dict:
        """
        Exports the SimulationData to a dictionary format that is able to be exported to the API.
        This will return the SimulationData in the same format that is fetched from the API.

        :returns:   The SimulationData in a dictionary format
        :rtype:     dict
        """
        return self.__raw

    def save(self, path: str) -> None:
        """
        Saves the SimulationData to a file path in a JSON format. This will save the SimulationData
        in a JSON format that is able to be loaded back into the SimulationData class.

        :param path:    The path to save the SimulationData to
        :type path:     str
        """
        with open(path, "w") as f:
            f.write(self.__str__())

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the SimulationData to a pandas DataFrame. This will convert the SimulationData
        to a pandas DataFrame and will return the DataFrame object.

        :returns:   The SimulationData in a pandas DataFrame format
        :rtype:     pd.DataFrame
        """
        # Create a dictionary of the data
        data = {}
        for row in self.data:
            for i, field in enumerate(self.fields):
                # If any of the row values are a lists, then break the list into separate columns
                if isinstance(row[i], list):
                    for j, value in enumerate(row[i]):
                        # Check if the key exists in the dictionary, if not create it
                        if f"{field}_{j}" not in data:
                            data[f"{field}_{j}"] = []
                        data[f"{field}_{j}"].append(value)
                else:
                    # Check if the key exists in the dictionary, if not create it
                    if field not in data:
                        data[field] = []
                    data[field].append(row[i])
        return pd.DataFrame(data)

    def __str__(self) -> str:
        """
        Converts the SimulationData to a string format that is able to be exported to a JSON format.

        :returns:   The SimulationData in a string format
        :rtype:     str
        """
        return json.dumps(self.export(), indent=4)
