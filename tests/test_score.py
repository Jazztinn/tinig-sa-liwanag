import unittest

import score


class ScoreTest(unittest.TestCase):
    def test_switch_region_flags_marks_window_around_switch(self):
        langs = ["hil", "hil", "en", "en", "hil"]
        self.assertEqual(
            score.switch_region_flags(langs),
            [False, True, True, True, True],
        )

    def test_score_clip_separates_switch_and_mono_errors(self):
        pairs = {}
        ref = ["pila", "ang", "grocery", "budget", "naton"]
        langs = ["hil", "hil", "en", "en", "hil"]
        hyp = ["pila", "foo", "grocery", "bar", "naton"]

        overall, switch, mono = score.score_clip(ref, langs, hyp, pairs)

        self.assertEqual((overall.errors, overall.words), (2, 5))
        self.assertEqual((switch.errors, switch.words), (2, 4))
        self.assertEqual((mono.errors, mono.words), (0, 1))
        self.assertEqual((pairs["hil<->en"].errors, pairs["hil<->en"].words), (2, 4))

    def test_insertions_count_only_overall(self):
        pairs = {}
        ref = ["pila", "ang"]
        langs = ["hil", "hil"]
        hyp = ["pila", "extra", "ang"]

        overall, switch, mono = score.score_clip(ref, langs, hyp, pairs)

        self.assertEqual((overall.errors, overall.words), (1, 2))
        self.assertEqual((switch.errors, switch.words), (0, 0))
        self.assertEqual((mono.errors, mono.words), (0, 2))
        self.assertEqual(pairs, {})

    def test_pair_breakdown_tracks_multiple_language_pairs(self):
        pairs = {}
        ref = ["a", "b", "c", "d", "e"]
        langs = ["hil", "tl", "en", "en", "hil"]
        hyp = ["x", "x", "x", "x", "x"]

        score.score_clip(ref, langs, hyp, pairs)

        self.assertIn("hil<->tl", pairs)
        self.assertIn("tl<->en", pairs)
        self.assertIn("hil<->en", pairs)


if __name__ == "__main__":
    unittest.main()
