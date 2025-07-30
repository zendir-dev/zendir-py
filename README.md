# zendir

[![PyPI Version](https://img.shields.io/pypi/v/zendir.svg)](https://pypi.org/project/zendir/)

`zendir` is a Python library that enables easy access to the Zendir API. The API is a REST interface to the Zendir simulation library, enabling simulations of spacecraft, ground stations, maritime objects and more. The API requires an [access key](#accessing-your-api-token) that is available with a free account from the Zendir website.

Example simulation scripts and usage of the zendir library can be found in the public repository [zendir Examples](https://github.com/zendir-dev/zendir-py-examples). This contains some sample scripts showcasing how to use the library and how to run spacecraft simulations with flight software and requesting data from the simulation API. This requires an API key to execute but can be used as a basis for development.

Additional tutorials and functionality for the library can be found on the public documentation at [docs.zendir.io](https://docs.zendir.io) under the Guides page.

![Sun Pointing Simulation](https://docs.zendir.io/v1.3/articles/guides/Python/GettingStarted/images/image.png)

---

## Installing `zendir`

'zendir' includes the interface for the Zendir API architecture, allowing for custom simulations to be constructed using API endpoints. For a non-local simulation, this requires correct authentication. To install `zendir`, install the project from the PyPi repository:

`
pip install zendir -user
`

Alternatively, this package can be downloaded, unzipped and installed via the following command instead.

`
pip install . --user
`

zendir requires the following Third-Party Python libraries to be installed alongside the installation of this package: 
- numpy
- pandas
- requests
- urllib3
- paho-mqtt
- matplotlib
- setuptools
- aiohttp

---

## Updating `zendir`

To upgrade a version of zendir, make sure to upgrade the python package. This can be done by the following command.

`
pip install zendir --user --upgrade
`

---

## Accessing your API Token

API Tokens are accessible via the [Zendir Website](https://www.zendir.io/account/log-in). Create a free account and start a 14-day trial of the software. This will give you access to unlimited sessions and requests during the trial period. The access token is available from the dashboard once the account is created and logged in.

To enable your token, create a Credential object and pass into the Simulation class when constructing simulations. Alternatively, if using the example library, update the token in the `credential_helper.py` class for easier access to the token over multiple files. More information can be found in the [API Access Keys](https://docs.zendir.io/v1.3/articles/guides/Python/GettingStarted/3_APIAccessKeys/index.html).

---

## API Sessions

Each token enables a single API session to be made. Multiple sessions cannot be created at once using the free-tier of the API. Each session is associated with a single cloud instance running the simulation that you have access to. This instance will run for 2 hours once connected. When first connected to the session, it may take between 30 seconds and 2 minutes for the instance to start. After that, the instance will be available without any load times for up to 2 hours. Upon the completion of the session, a new session can be started immediately after with a similar load-up time as before. There is no limit for the number of sessions available during a period of time, with the exception of having one session running concurrently.

---

## Creating a Simulation

To create a simulation, use the `Simulation` class. Once the client has been created, this can be used to set up all configurations of objects and data within your instance.

```python
from zendir import Client, Simulation

client = Client("https://api.zendir.io", token="$ACCESS_KEY$")
simulation = Simulation.create(client)
```

The simulation class can be used to manage the objects, tick the simulation and track the state of data over the lifetime of the session. As an example, a spacecraft could be created using the following code:

```python
from zendir import Object

spacecraft: Object = simulation.add_object(
    "Spacecraft",
    Position=[6671000, 0, 0],
    Velocity=[0, -7700, 0],
    TotalMass=15.0,
    AttitudeRate=[0.01, 0.02, -0.03]
)
```

---

## Ticking a Simulation

Once the objects have been created in the simulation, the simulation can be ticked. A `tick` can have a step-size, specified in seconds, and an optional duration. A `duration` will specify how long to tick the simulation for, with the specified step size, before finishing the process.

```python
simulation.tick(0.1)
simulation.tick_duration(time=1000.0, step=0.1)
```

---

## Recording Data

Before the simulation is ticked, specific objects, messages or instances can have their data tracked over the simulation lifetime. This allows for the data to be pulled back as a time-series set at the end of the simulation for data analysis and saving. By default, no components are recorded unless the simulation is told to start tracking them. To track an object, use the following.

```python
simulation.set_tracking_interval(10.0)
simulation.track_object(spacecraft)
simulation.track_object(spacecraft.get_message("Out_SpacecraftStateMsg"))
```

Once the simulation has finished ticking, to retrieve the data at the end of the simulation, use the `query` functions, which can also return a pandas data frame object that can be plotted. This will only work with ojects that have been tracked before the simulation started running.

```python
data_sc = simulation.query_object(spacecraft)
data_msg = simulation.query_dataframe(spacecraft.get_message("Out_SpacecraftStateMsg"))
```

---

</br>

![Orbit Raising Maneuver](https://docs.zendir.io/v1.3/articles/guides/images/image_2.png)