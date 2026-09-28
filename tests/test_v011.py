import json
import tempfile
import unittest
from pathlib import Path

from agent_replay.core import Recorder, load, replay, verify_chain


class IntegrityTests(unittest.TestCase):
    def test_recorded_events_form_a_valid_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            recorder = Recorder(path)
            recorder.append("tool", "search", {"q": "x"}, {"ok": True})
            recorder.append("tool", "fetch", {"id": 1}, {"value": 2})
            self.assertEqual(verify_chain(load(path)), [])

    def test_tampering_is_detected_before_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            recorder = Recorder(path)
            recorder.append("tool", "search", {"q": "x"}, {"ok": True})
            row = json.loads(path.read_text().strip())
            row["result"] = {"ok": False}
            path.write_text(json.dumps(row) + "\n")
            events = load(path)
            self.assertEqual(verify_chain(events)[0]["reason"], "event_hash mismatch")
            self.assertEqual(replay(events, {}, verify_integrity=True)[0]["kind"], "integrity")

    def test_recorder_continues_existing_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            Recorder(path).append("tool", "one", {}, 1)
            Recorder(path).append("tool", "two", {}, 2)
            events = load(path)
            self.assertEqual([e.seq for e in events], [1, 2])
            self.assertEqual(verify_chain(events), [])


if __name__ == "__main__":
    unittest.main()
