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

The C++ library forwards its records here through the CPython API, passing
__FILE__ and __LINE__ so that each line is attributed to its true origin.
Records from the shared library therefore appear as `von_mises.cpp:52`
while Python records appear as `eigen.py:31`, and both use the standard
logging levels.
"""

import logging
import sys

__all__ = [
    "LOGGER",
    "TRACE",
    "add_file_handler",
    "makeCppRecord",
    "set_output_level",
]

TRACE = 5
logging.addLevelName(TRACE, "TRACE")

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(levelname)-7s %(filename)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S",
)

_CONSOLE_OUTPUT_HANDLER = logging.StreamHandler(stream=sys.stdout)
_CONSOLE_OUTPUT_HANDLER.setFormatter(_FORMATTER)
_CONSOLE_OUTPUT_HANDLER.addFilter(lambda record: record.levelno < logging.ERROR)

_CONSOLE_ERROR_HANDLER = logging.StreamHandler(stream=sys.stderr)
_CONSOLE_ERROR_HANDLER.setFormatter(_FORMATTER)
_CONSOLE_ERROR_HANDLER.setLevel(logging.ERROR)

LOGGER = logging.getLogger("vonMises")
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_CONSOLE_OUTPUT_HANDLER)
LOGGER.addHandler(_CONSOLE_ERROR_HANDLER)
LOGGER.propagate = False

_FILE_HANDLER = None


def makeCppRecord(level: int, message: str, filename: str, lineno: int) -> None:
    """
    Emit a record originating in the C++ library.

    ``filename`` and ``lineno`` are reserved :class:`logging.LogRecord`
    attributes, so they cannot be supplied through ``extra``; the record is
    built directly instead, which attributes the line to the C++ source
    rather than to this function.

    Parameters
    ----------
    level : int
        Standard logging level.
    message : str
        Already-formatted message text.
    filename : str
        Value of ``__FILE__`` at the call site.
    lineno : int
        Value of ``__LINE__`` at the call site.
    """
    if not LOGGER.isEnabledFor(level):
        return

    record = LOGGER.makeRecord(
        LOGGER.name, level, filename, lineno, message, None, None
    )
    LOGGER.handle(record)


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
