"""
Copyright (c) 2024 Saud Zahir

This file is part of vonMises.

vonMises is free software; you can redistribute it and/or
modify it under the terms of the MIT License.

vonMises is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT
License for more details.
"""

import ctypes
import glob
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    _LIBRARY_NAME = "libvonmises.dll"
elif sys.platform == "darwin":
    _LIBRARY_NAME = "libvonmises.dylib"
else:
    _LIBRARY_NAME = "libvonmises.so"


def _candidate_paths():
    """
    Yield the locations the shared library may occupy.

    A normal install places it under ``sys.prefix``. An editable install
    leaves it in the scikit-build tree instead, so that is searched too.

    Yields
    ------
    Path
        Candidate path to the shared library.
    """
    yield Path(sys.prefix, "bin", _LIBRARY_NAME)
    yield Path(sys.prefix, "lib", _LIBRARY_NAME)
    yield Path(__file__).parent / "lib" / _LIBRARY_NAME

    project_root = Path(__file__).resolve().parents[2]
    for sub in ("cmake-install/bin", "cmake-install/lib", "cmake-build"):
        pattern = str(project_root / "_skbuild" / "*" / sub / _LIBRARY_NAME)
        for match in sorted(glob.glob(pattern)):
            yield Path(match)


def _locate_library():
    """
    Find the shared library on disk.

    Returns
    -------
    Path
        Path to the first existing candidate.

    Raises
    ------
    FileNotFoundError
        If no candidate exists, listing where the search looked.
    """
    searched = []
    for candidate in _candidate_paths():
        if candidate.is_file():
            return candidate
        searched.append(str(candidate))

    raise FileNotFoundError(
        f"{_LIBRARY_NAME} not found. Build it with 'python build.py install'. "
        f"Searched: {', '.join(searched)}"
    )


shared_file_path = _locate_library()

if sys.platform == "win32":
    os.add_dll_directory(str(shared_file_path.parent))
    vonmises_lib = ctypes.CDLL(str(shared_file_path), winmode=0)
else:
    vonmises_lib = ctypes.CDLL(str(shared_file_path), mode=ctypes.RTLD_GLOBAL)
