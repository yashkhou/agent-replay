from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

SENSITIVE = {"token", "password", "secret", "authorization", "api_key"}


def redact(value):
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if key.lower() in SENSITIVE else redact(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


@dataclass
class Event:
    seq: int
    kind: str
    name: str
    payload: object = None
    result: object = None
    prev_hash: str = ""
    event_hash: str = ""


def _event_hash(event: Event) -> str:
    data = asdict(event)
    data.pop("event_hash", None)
    wire = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(wire.encode()).hexdigest()


class Recorder:
    def __init__(self, path):
        self.path = Path(path)
        existing = load(self.path) if self.path.exists() else []
        self.seq = existing[-1].seq if existing else 0
        self.prev_hash = existing[-1].event_hash if existing and existing[-1].event_hash else ""

    def append(self, kind, name, payload=None, result=None):
        self.seq += 1
        event = Event(self.seq, kind, name, redact(payload), redact(result), self.prev_hash)
        event.event_hash = _event_hash(event)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")
        self.prev_hash = event.event_hash
        return event


def load(path):
    path = Path(path)
    if not path.exists():
        return []
    return [Event(**json.loads(line)) for line in path.read_text().splitlines() if line.strip()]


def verify_chain(events):
    problems = []
    previous = ""
    for event in events:
        if not event.event_hash:
            problems.append({"seq": event.seq, "reason": "missing event_hash"})
            previous = ""
            continue
        if event.prev_hash != previous:
            problems.append({"seq": event.seq, "reason": "prev_hash mismatch"})
        expected = _event_hash(event)
        if event.event_hash != expected:
            problems.append({"seq": event.seq, "reason": "event_hash mismatch"})
        previous = event.event_hash
    return problems


def replay(events, fixtures, verify_integrity=False):
    if verify_integrity:
        integrity = verify_chain(events)
        if integrity:
            return [{"kind": "integrity", **problem} for problem in integrity]
    diffs = []
    for event in events:
        if event.kind != "tool":
            continue
        key = json.dumps(event.payload, sort_keys=True, separators=(",", ":"))
        observed = fixtures.get(event.name, {}).get(key, {"__missing_fixture__": True})
        if observed != event.result:
            diffs.append({"seq": event.seq, "tool": event.name, "expected": event.result, "observed": observed})
    return diffs
