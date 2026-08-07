"""
Copyright (c) 2024 Saud Zahir

This file is part of vonMises.

vonMises is free software; you can redistribute it and/or
modify it under the terms of the MIT License.

vonMises is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
License for more details.


Logging for vonMises.

The C++ library routes its messages into this same logger through the
CPython API (see src/vonmiseslib/logger.cpp), so C++ and Python output
share one stream, one format and one level.

C++ records are emitted one level above their Python counterparts, and
TRACE occupies level 5. That keeps the two sides distinguishable in the
log while still ordering correctly, so `p:INFO` and `c:INFO` are both
visible at INFO but obviously different in origin.
"""

import logging
import sys

__all__ = [
    "LOGGER",
    "TRACE",
    "add_file_handler",
    "set_output_level",
]

# Custom level for C++ trace output; below DEBUG so it is filtered out
# unless explicitly requested.
TRACE = 5

_LABEL_WIDTH = 9

logging.addLevelName(logging.ERROR, "p:ERROR".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(logging.WARNING, "p:WARNING".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(logging.INFO, "p:INFO".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(logging.DEBUG, "p:DEBUG".ljust(_LABEL_WIDTH, ":"))

logging.addLevelName(logging.ERROR + 1, "c:ERROR".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(logging.WARNING + 1, "c:WARNING".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(logging.INFO + 1, "c:INFO".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(logging.DEBUG + 1, "c:DEBUG".ljust(_LABEL_WIDTH, ":"))
logging.addLevelName(TRACE, "c:TRACE".ljust(_LABEL_WIDTH, ":"))

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)

# Errors go to stderr, everything else to stdout, so piping stdout does not
# swallow failures.
_CONSOLE_OUTPUT_HANDLER = logging.StreamHandler(stream=sys.stdout)
_CONSOLE_OUTPUT_HANDLER.setFormatter(_FORMATTER)
_CONSOLE_OUTPUT_HANDLER.addFilter(
    lambda record: record.levelno not in {logging.ERROR, logging.ERROR + 1}
)

_CONSOLE_ERROR_HANDLER = logging.StreamHandler(stream=sys.stderr)
_CONSOLE_ERROR_HANDLER.setFormatter(_FORMATTER)
_CONSOLE_ERROR_HANDLER.setLevel(logging.ERROR)

LOGGER = logging.getLogger("vonMises")
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_CONSOLE_OUTPUT_HANDLER)
LOGGER.addHandler(_CONSOLE_ERROR_HANDLER)

# Messages are emitted by this logger's own handlers only; without this a
# root handler configured by the host application would duplicate them.
LOGGER.propagate = False

_FILE_HANDLER = None


def add_file_handler(filename: str = "vonMises.log", mode: str = "w") -> None:
    """
    Write log records to ``filename`` in addition to the console.

    Replaces any handler added by a previous call, so repeated calls do not
    accumulate open files.

    Parameters
    ----------
    filename : str, optional
        Path of the log file. Defaults to ``"vonMises.log"``.
    mode : str, optional
        File mode passed to :class:`logging.FileHandler`. Defaults to ``"w"``.
    """
    global _FILE_HANDLER

    if _FILE_HANDLER is not None:
        LOGGER.removeHandler(_FILE_HANDLER)
        _FILE_HANDLER.close()

    _FILE_HANDLER = logging.FileHandler(filename, mode=mode)
    _FILE_HANDLER.setFormatter(_FORMATTER)
    LOGGER.addHandler(_FILE_HANDLER)


def set_output_level(level: int) -> None:
    """
    Set the verbosity of both Python and C++ output.

    Parameters
    ----------
    level : int
        ``0`` error, ``1`` warning, ``2`` info, ``3`` debug, ``4`` trace.

    Raises
    ------
    ValueError
        If ``level`` is not one of the documented values.
    """
    levels = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
        4: TRACE,
    }

    if level not in levels:
        raise ValueError(f"level must be one of {sorted(levels)}, got {level!r}")

    LOGGER.setLevel(levels[level])


def _handle_exception(exc_type, exc_value, exc_traceback) -> None:
    """
    Route uncaught exceptions through the logger.

    Keyboard interrupts are left to the default handler so that Ctrl-C does
    not produce a traceback.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    LOGGER.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = _handle_exception
