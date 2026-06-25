import importlib.util
import pathlib
import unittest

import score

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "freeze_benchmark.py"
SPEC = importlib.util.spec_from_file_location("freeze_benchmark", SCRIPT)
freeze = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freeze)


class FreezeManifestTest(unittest.TestCase):
    def test_build_manifest_shape(self):
        m = freeze.build_manifest()
        self.assertEqual(m["version"], freeze.VERSION)
        self.assertIn("headline", m["cohorts"])
        self.assertEqual(m["cohorts"]["headline"]["role"], "test")
        self.assertEqual(m["cohorts"]["headline"]["n_clips"], 40)
        self.assertEqual(m["splits"]["train"], None)
        self.assertTrue(m["scorer"]["sha256"])

    def test_build_manifest_is_deterministic_except_date(self):
        a, b = freeze.build_manifest(), freeze.build_manifest()
        self.assertEqual(a["cohorts"], b["cohorts"])
        self.assertEqual(a["scorer"]["sha256"], b["scorer"]["sha256"])

    def test_clip_hashes_match_recompute(self):
        # This is exactly what --verify checks: per-clip content hashes must be
        # reproducible from the working tree.
        m = freeze.build_manifest()
        clips = m["cohorts"]["headline"]["clips"]
        self.assertTrue(all(c["annotation_sha256"] for c in clips))
        self.assertTrue(all(c["audio_sha256"] for c in clips))
        again = freeze.build_manifest()["cohorts"]["headline"]["clips"]
        self.assertEqual(
            {c["clip_id"]: c["annotation_sha256"] for c in clips},
            {c["clip_id"]: c["annotation_sha256"] for c in again},
        )


class BootstrapCITest(unittest.TestCase):
    def _per_clip(self):
        # 4 synthetic clips: errors/words per bucket.
        return [
            {"overall": (2, 5), "switch": (1, 2), "mono": (1, 3)},
            {"overall": (0, 4), "switch": (0, 1), "mono": (0, 3)},
            {"overall": (3, 6), "switch": (2, 3), "mono": (1, 3)},
            {"overall": (1, 5), "switch": (0, 2), "mono": (1, 3)},
        ]

    def test_ci_brackets_point_estimate(self):
        clips = self._per_clip()
        lo, hi = score.bootstrap_ci(clips, "overall", resamples=500, seed=7)
        self.assertLessEqual(lo, hi)
        point = sum(c["overall"][0] for c in clips) / sum(c["overall"][1] for c in clips)
        self.assertLessEqual(lo, point)
        self.assertGreaterEqual(hi, point)
        self.assertGreaterEqual(lo, 0.0)
        self.assertLessEqual(hi, 1.0)

    def test_ci_deterministic_with_seed(self):
        clips = self._per_clip()
        self.assertEqual(
            score.bootstrap_ci(clips, "switch", resamples=500, seed=11),
            score.bootstrap_ci(clips, "switch", resamples=500, seed=11),
        )

    def test_ci_none_for_empty_bucket(self):
        clips = [{"overall": (0, 0), "switch": (0, 0), "mono": (0, 0)}]
        self.assertIsNone(score.bootstrap_ci(clips, "overall"))


if __name__ == "__main__":
    unittest.main()
