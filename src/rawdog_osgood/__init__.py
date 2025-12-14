from .client import RawdogClientBase, RawdogClientTcp, RawdogClientUnix
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("rawdog_osgood")
except PackageNotFoundError:
    __version__ = "v0.0.1"