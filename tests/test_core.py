import unittest

from lyaplab.core import classify_exponent, exponent_grid, lyapunov_exponent
from lyaplab.orbit import histogram_density, summarize_orbit_density


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

    def test_histogram_density_sums_to_one(self):
        values = [0.1, 0.2, 0.2, 0.8]
        density = histogram_density(values, bins=4)
        self.assertAlmostEqual(sum(density), 1.0, places=6)

    def test_chaotic_orbit_occupies_more_bins_than_stable_orbit(self):
        stable = summarize_orbit_density("AB", 2.9, 3.1, burn_in=300, steps=1200, bins=24)
        chaotic = summarize_orbit_density("AB", 3.9, 3.95, burn_in=300, steps=1200, bins=24)
        self.assertLess(stable.occupied_bins, chaotic.occupied_bins)
        self.assertLess(stable.exponent, 0.0)
        self.assertGreater(chaotic.exponent, 0.0)

    def test_near_zero_case_spreads_more_than_stable_case(self):
        stable = summarize_orbit_density("AABAB", 3.35, 3.35, burn_in=360, steps=1400, bins=24)
        frontier = summarize_orbit_density("AABAB", 2.9, 3.715, burn_in=360, steps=1400, bins=24)
        self.assertLess(abs(frontier.exponent), 0.05)
        self.assertGreater(frontier.occupied_bins, stable.occupied_bins)


if __name__ == "__main__":
    unittest.main()
