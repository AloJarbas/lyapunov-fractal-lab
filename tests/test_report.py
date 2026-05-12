import unittest

from lyaplab.report import summarize_sequence_grid


class SequenceReportTests(unittest.TestCase):
    def test_summary_fractions_sum_to_one(self):
        summary = summarize_sequence_grid("AB", size=12, burn_in=60, steps=120)
        total = summary.stable_fraction + summary.boundary_fraction + summary.chaotic_fraction
        self.assertAlmostEqual(total, 1.0, places=6)

    def test_different_words_give_different_summaries(self):
        ab = summarize_sequence_grid("AB", size=18, burn_in=80, steps=140)
        aabab = summarize_sequence_grid("AABAB", size=18, burn_in=80, steps=140)
        self.assertNotAlmostEqual(ab.chaotic_fraction, aabab.chaotic_fraction, places=3)

    def test_invalid_size_raises(self):
        with self.assertRaises(ValueError):
            summarize_sequence_grid("AB", size=1)


if __name__ == "__main__":
    unittest.main()
