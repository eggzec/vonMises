from importlib.metadata import PackageNotFoundError, version

from vonmises import logger as logger

try:
    __version__ = version("vonMises")
except PackageNotFoundError:
    __version__ = "unknown"
