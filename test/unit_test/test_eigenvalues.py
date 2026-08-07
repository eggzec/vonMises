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
test_eigenvalues = np.array(
    [14.073477752817423, 10.819060924370755, 8.143435247151785, 5.964026075660039]
)


class TestEigenvalues(unittest.TestCase):
    def test_eigenvalues(self):
        eigenvalues = eigen.eigenvalues(test_array)
        self.assertTrue(np.allclose(eigenvalues, test_eigenvalues, atol=1e-7))


if __name__ == "__main__":
    unittest.main()
