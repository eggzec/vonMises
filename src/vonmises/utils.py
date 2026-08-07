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

import numpy as np
from scipy.io import loadmat, savemat

from vonmises.logger import LOGGER


def mat_to_array(matfile_path, mat_key):
    """
    Load data from a MAT file and return as a NumPy array with dtype=np.double.

    Args:
        matfile_path (str): Path to the MAT file.
        mat_key (str): Key to access the matrix in the MAT file.

    Returns:
        numpy.ndarray: NumPy array containing the data from the MAT file.

    Raises:
        ValueError: If the key is not present in the MAT file.
        TypeError: If the value stored under the key is not a NumPy array.
    """
    LOGGER.debug(f"Reading MAT file '{matfile_path}'")

    with open(matfile_path, "rb") as f:
        mat_data = loadmat(f)

    if mat_key not in mat_data:
        available = ", ".join(k for k in mat_data if not k.startswith("__"))
        LOGGER.error(f"Key '{mat_key}' not found; available keys: {available}")
        raise ValueError(f"Key '{mat_key}' not found in the MAT file.")

    matrix = mat_data[mat_key]
    if not isinstance(matrix, np.ndarray):
        LOGGER.error(f"Key '{mat_key}' holds {type(matrix).__name__}, not an array")
        raise TypeError(f"Data associated with key '{mat_key}' is not a NumPy array.")

    LOGGER.info(f"Loaded matrix '{mat_key}' with shape {matrix.shape}")

    return np.array(matrix, dtype=np.double)


def array_to_mat(array, matfile_path, mat_key):
    """
    Save a NumPy array as a MATLAB matrix in a MAT file.

    Args:
        array (numpy.ndarray): NumPy array to be saved.
        matfile_path (str): Path to the MAT file.
        mat_key (str): Key to store the matrix in the MAT file.
    """
    LOGGER.info(
        f"Writing matrix '{mat_key}' with shape {array.shape} to '{matfile_path}'"
    )
    savemat(matfile_path, {mat_key: array})
