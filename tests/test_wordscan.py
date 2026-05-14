import unittest

from lyaplab.wordscan import canonical_sequence, enumerate_short_words, ranked_rows, scan_short_words


class WordScanTests(unittest.TestCase):
    def test_canonical_sequence_collapses_rotation_and_label_swap(self):
        self.assertEqual(canonical_sequence("AB"), canonical_sequence("BA"))
        self.assertEqual(canonical_sequence("AABB"), canonical_sequence("BBAA"))

    def test_canonical_sequence_reduces_repeated_root(self):
        self.assertEqual(canonical_sequence("ABAB"), "AB")
        self.assertEqual(canonical_sequence("BABABA"), "AB")

    def test_enumerate_short_words_is_unique_and_mixed(self):
        words = enumerate_short_words(min_length=2, max_length=4)
        self.assertEqual(len(words), len(set(words)))
        self.assertTrue(all("A" in word and "B" in word for word in words))
        self.assertIn("AB", words)

    def test_scan_short_words_builds_rankable_rows(self):
        rows = scan_short_words(min_length=2, max_length=3, size=12, burn_in=60, steps=120)
        self.assertTrue(rows)
        self.assertTrue(all(row.frontier_score >= 0.0 for row in rows))
        top = ranked_rows(rows, key="frontier_score", limit=2)
        self.assertLessEqual(len(top), 2)
        if len(top) == 2:
            self.assertGreaterEqual(top[0].frontier_score, top[1].frontier_score)


if __name__ == "__main__":
    unittest.main()
