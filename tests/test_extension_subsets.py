import glob
import json
import os
import unittest
import wave


ROOT = os.path.dirname(os.path.dirname(__file__))
SPK2_ANNOTATIONS = os.path.join(
    ROOT, "data", "extensions", "scripted_native_spk2", "annotations"
)
SPK2_AUDIO = os.path.join(ROOT, "data", "extensions", "scripted_native_spk2", "audio")
PRIMARY_ANNOTATIONS = os.path.join(ROOT, "data", "annotations")


class ExtensionSubsetTest(unittest.TestCase):
    def test_speaker2_is_reviewed_but_not_headline_released(self):
        allowed = {
            "HIL": {"hil"},
            "HIL+EN": {"hil", "en"},
            "HIL+TL": {"hil", "tl"},
            "HIL+TL+EN": {"hil", "tl", "en"},
        }
        paths = sorted(glob.glob(os.path.join(SPK2_ANNOTATIONS, "spk2_*.json")))
        self.assertEqual(len(paths), 40)
        for path in paths:
            with open(path, encoding="utf-8") as f:
                row = json.load(f)
            self.assertEqual(row.get("speaker", {}).get("id"), "spk02")
            self.assertEqual(row.get("subset"), "scripted_native")
            self.assertEqual(row.get("review_status"), "reviewed")
            self.assertEqual(row.get("lang_tags_status"), "reviewed")
            langs = {token.get("lang") for token in row.get("tokens", [])}
            self.assertNotIn(None, langs)
            self.assertLessEqual(langs, allowed[row["switch_type"]], row["clip_id"])
            if row["switch_type"] != "HIL":
                self.assertLessEqual(allowed[row["switch_type"]] - {"hil"}, langs, row["clip_id"])
            audio_path = os.path.join(SPK2_AUDIO, os.path.basename(row["audio_file"]))
            with wave.open(audio_path) as w:
                duration = w.getnframes() / w.getframerate()
                self.assertEqual(w.getframerate(), 16000)
                self.assertEqual(w.getnchannels(), 1)
            self.assertLess(abs(duration - float(row["duration_sec"])), 0.03, row["clip_id"])

    def test_speaker2_is_not_in_primary_annotations(self):
        primary_names = {
            os.path.basename(path)
            for path in glob.glob(os.path.join(PRIMARY_ANNOTATIONS, "*.json"))
        }
        self.assertFalse(any(name.startswith("spk2_") for name in primary_names))


if __name__ == "__main__":
    unittest.main()
