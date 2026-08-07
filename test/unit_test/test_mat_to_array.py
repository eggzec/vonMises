import unittest
from pathlib import Path

import numpy as np

from vonmises.utils import mat_to_array


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_matfile_path = Path("test/test-data/MATRIX.mat")
        self.key = "A"
        self.test_array = np.array(
            [
                [10.0, -1.0, 2.0, 0.0],
                [-1.0, 11.0, -1.0, 3.0],
                [2.0, -1.0, 10.0, -1.0],
                [0.0, 3.0, -1.0, 8.0],
            ]
        )

    def test_mat_to_array(self):
        loaded_array = mat_to_array(self.test_matfile_path, self.key)
        self.assertTrue(np.array_equal(loaded_array, self.test_array))


if __name__ == "__main__":
    unittest.main()
