import unittest

import numpy as np
import numpy.testing as npt

from vonmises import eigen

test_matrix = np.array(
    [
        [10.0, -1.0, 2.0, 0.0],
        [-1.0, 11.0, -1.0, 3.0],
        [2.0, -1.0, 10.0, -1.0],
        [0.0, 3.0, -1.0, 8.0],
    ]
)


class TestEigenvalues(unittest.TestCase):
    def test_eigenvalues_and_eigenvectors(self):
        eigenvalues, eigenvectors = eigen.eigen(test_matrix)
        self.verify_eigen(test_matrix, eigenvalues, eigenvectors)

    def verify_eigen(self, matrix, eigenvalues, eigenvectors):
        for i in range(len(eigenvalues)):
            v = eigenvectors[:, i]
            c = eigenvalues[i]

            Av = np.dot(matrix, v)
            cv = c * v
            residual = np.linalg.norm(Av - cv)

            npt.assert_allclose(Av, cv, atol=1e-6)
            self.assertAlmostEqual(0, residual, places=8)


if __name__ == "__main__":
    unittest.main()
