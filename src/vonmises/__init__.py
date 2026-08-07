import pkg_resources

# Imported for its side effects: registers the c:* log level names and
# configures the "vonMises" logger that src/vonmiseslib/logger.cpp
# looks up through the CPython API. Must happen before the shared
# library emits its first record.
from vonmises import logger as logger

__version__ = pkg_resources.get_distribution("vonMises").version
