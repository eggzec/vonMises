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

import numpy as np

from vonmises.lib import vonmises_lib
from vonmises.logger import LOGGER


class EigenValueProblem:
    def __init__(self, lib):
        self.lib = lib

    def solve(self, A):
        LOGGER.debug(f"Solving eigenvalue problem for a {len(A)}x{len(A)} matrix")

        solveEigenValueProblem = self.lib.solveEigenValueProblem
        solveEigenValueProblem.argtypes = [
            ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
        ]
        solveEigenValueProblem.restype = None

        size = len(A)

        A_ptr = (ctypes.POINTER(ctypes.c_double) * size)()
        for i, row in enumerate(A):
            A_ptr[i] = (ctypes.c_double * len(row))(*row)

        eigenvalues = (ctypes.c_double * size)()
        eigenvectors = (ctypes.POINTER(ctypes.c_double) * size)()
        for i in range(size):
            eigenvectors[i] = (ctypes.c_double * size)()

        solveEigenValueProblem(A_ptr, size, eigenvalues, eigenvectors)

        eigenvalues = list(eigenvalues)
        eigenvectors = [list(eigenvectors[i][0:size]) for i in range(size)]

        LOGGER.info(f"Computed {size} eigenvalues")
        LOGGER.debug(f"Eigenvalues: {eigenvalues}")

        return np.array(eigenvalues), np.array(eigenvectors).T


def eigen(A):
    return EigenValueProblem(vonmises_lib).solve(A)


def eigenvalues(A):
    _eigenvalues, _ = eigen(A)
    return _eigenvalues


def eigenvectors(A):
    _, _eigenvectors = eigen(A)
    return _eigenvectors
