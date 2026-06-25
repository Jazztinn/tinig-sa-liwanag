import glob
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
import wave


ROOT = os.path.dirname(os.path.dirname(__file__))
ANNOTATIONS = os.path.join(ROOT, "data", "annotations")
AUDIO = os.path.join(ROOT, "data", "audio")
PREDICTIONS = os.path.join(ROOT, "data", "predictions")


def load_annotations():
    rows = []
    for path in sorted(glob.glob(os.path.join(ANNOTATIONS, "hil_cs_*.json"))):
        with open(path, encoding="utf-8") as f:
            rows.append(json.load(f))
    return rows


class DatasetIntegrityTest(unittest.TestCase):
    def test_audio_exists_and_duration_matches_when_set(self):
        for row in load_annotations():
            audio_path = os.path.join(ROOT, "data", row["audio_file"])
            self.assertTrue(os.path.exists(audio_path), row["clip_id"])
            with wave.open(audio_path) as w:
                duration = w.getnframes() / w.getframerate()
                self.assertEqual(w.getframerate(), 16000)
                self.assertEqual(w.getnchannels(), 1)
            if row.get("duration_sec") is not None:
                self.assertLess(abs(duration - float(row["duration_sec"])), 0.03, row["clip_id"])

    def test_no_duplicate_audio_or_transcripts(self):
        hashes = {}
        transcripts = {}
        for row in load_annotations():
            audio_path = os.path.join(ROOT, "data", row["audio_file"])
            with open(audio_path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            self.assertNotIn(digest, hashes, (row["clip_id"], hashes.get(digest)))
            hashes[digest] = row["clip_id"]
            transcript = row.get("transcript", "")
            self.assertNotIn(transcript, transcripts, (row["clip_id"], transcripts.get(transcript)))
            transcripts[transcript] = row["clip_id"]

    def test_switch_type_matches_token_languages(self):
        allowed = {
            "HIL": {"hil"},
            "HIL+EN": {"hil", "en"},
            "HIL+TL": {"hil", "tl"},
            "HIL+TL+EN": {"hil", "tl", "en"},
        }
        for row in load_annotations():
            langs = {token["lang"] for token in row["tokens"]}
            switch_type = row["switch_type"]
            self.assertLessEqual(langs, allowed[switch_type], row["clip_id"])
            if switch_type != "HIL":
                self.assertLessEqual(allowed[switch_type] - {"hil"}, langs, row["clip_id"])

    def test_predictions_cover_annotations(self):
        for row in load_annotations():
            path = os.path.join(PREDICTIONS, f"{row['clip_id']}.json")
            self.assertTrue(os.path.exists(path), row["clip_id"])
            with open(path, encoding="utf-8") as f:
                pred = json.load(f)
            self.assertEqual(pred.get("clip_id"), row["clip_id"])
            self.assertIn("text", pred)

    def test_package_script_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [
                    "python3",
                    "scripts/package_dataset.py",
                    "--output",
                    tmp,
                    "--overwrite",
                ],
                cwd=ROOT,
                check=True,
            )
            self.assertTrue(os.path.exists(os.path.join(tmp, "dataset", "metadata.csv")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "benchmark", "results.json")))


if __name__ == "__main__":
    unittest.main()
