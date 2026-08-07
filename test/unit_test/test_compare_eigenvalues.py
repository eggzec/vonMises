import unittest

import numpy as np

from vonmises import eigen

test_array = np.array(
    [
        [10.0, -1.0, 2.0, 0.0],
        [-1.0, 11.0, -1.0, 3.0],
        [2.0, -1.0, 10.0, -1.0],
        [0.0, 3.0, -1.0, 8.0],
    ]
)


class TestCompareEigenvalues(unittest.TestCase):
    def test_compare_eigenvalues(self):
        eigenvalues = eigen.eigenvalues(test_array)
        ref_eigenvalues = np.linalg.eigvals(test_array)
        self.assertTrue(np.allclose(eigenvalues, ref_eigenvalues, atol=1e-7))


if __name__ == "__main__":
    unittest.main()
