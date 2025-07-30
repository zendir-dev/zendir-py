#                     [ ZENDIR ]
# This code is developed by Zendir to aid with communication
# to the public API. All code is under the the license provided
# with the 'zendir' module. Copyright Zendir, 2025.
import re
from pathlib import Path
from setuptools import setup, find_packages


def get_version():
    init_file = Path(__file__).parent / "src" / "zendir" / "__init__.py"
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise RuntimeError("Cannot find version string.")


# Setup the project
setup(
    name="zendir",
    version=get_version(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiohttp",
        "urllib3",
        "paho-mqtt",
        "numpy",
        "pandas",
        "matplotlib",
        "setuptools",
        "pytest-asyncio",
        "requests",
    ],
    author="Zendir",
    author_email="support@zendir.io",
    description="Python Interface to the Zendir API for simulations",
    long_description="This is the Python interface library for the Zendir API. \
        The Zendir API allows access to spacecraft and space-domain simulation functions \
        and the framework for simulating high-fidelity satellites. \
        It enables accessing the REST API simulation functions in an easy format.\
        Examples of how to construct Zendir simulations are provided on the\
        Zendir documentation found at https://docs.zendir.io.",
    url="https://github.com/zendir-dev/zendir-py",
)
