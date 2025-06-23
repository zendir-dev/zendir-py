# Define the version of the package
__version__ = "1.3.0.0"

# Import the standard utilities
from .utils import NominalException, printer, helper

# Import the standard classes that are commonly used
from .connection import Credentials, Client
from .simulation import *
