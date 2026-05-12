import unittest

from lyaplab.core import classify_exponent, exponent_grid, lyapunov_exponent


class LyapunovCoreTests(unittest.TestCase):
    def test_stable_region_is_negative(self):
        value = lyapunov_exponent("AB", 2.9, 3.1, burn_in=250, steps=800)
        self.assertLess(value, 0.0)
        self.assertEqual(classify_exponent(value), "stable")

    def test_chaotic_region_is_positive(self):
        value = lyapunov_exponent("AB", 3.9, 3.95, burn_in=250, steps=800)
        self.assertGreater(value, 0.0)
        self.assertEqual(classify_exponent(value), "chaotic")

    def test_grid_shape_matches_axes(self):
        grid = exponent_grid("AABAB", [2.5, 3.0, 3.5], [2.6, 3.2])
        self.assertEqual(len(grid), 3)
        self.assertTrue(all(len(row) == 2 for row in grid))

    def test_invalid_sequence_raises(self):
        with self.assertRaises(ValueError):
            lyapunov_exponent("AX", 3.5, 3.6)


if __name__ == "__main__":
    unittest.main()
