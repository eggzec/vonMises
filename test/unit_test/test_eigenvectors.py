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
test_eigenvectors = np.array(
    [
        [
            -0.3934745132662989,
            0.6233611125319993,
            -0.6404299749594337,
            -0.21551839356810434,
        ],
        [
            0.680207701966034,
            0.4912946824964888,
            0.2267043001245381,
            -0.4945221708293822,
        ],
        [
            -0.4613009870624494,
            0.5009327057718649,
            0.7078520091508445,
            0.1876522229135619,
        ],
        [
            0.4119425796529732,
            0.3451331375304617,
            -0.19339115962115574,
            0.8208448622167394,
        ],
    ]
)


class TestEigenvectors(unittest.TestCase):
    def test_eigenvectors(self):
        eigenvectors = eigen.eigenvectors(test_array)
        eigenvectors_abs = np.abs(eigenvectors)
        test_eigenvectors_abs = np.abs(test_eigenvectors)

        self.assertTrue(np.allclose(eigenvectors_abs, test_eigenvectors_abs, atol=1e-7))


if __name__ == "__main__":
    unittest.main()
