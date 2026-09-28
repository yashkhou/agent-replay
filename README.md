# agent-replay

Provider-neutral record/replay for agent tool sessions with redaction, fixture-backed execution and regression diffs.

## What it does

- records ordered tool calls and results as portable JSONL
- redacts configured sensitive keys before traces hit disk
- replays tool calls against deterministic fixtures
- reports exact result diffs instead of fuzzy success

## Quick start

```bash
PYTHONPATH=src python -m agent_replay examples/trace.jsonl examples/fixtures.json
```

No model API, network service, or third-party package is required.

## Architecture

A trace is an ordered JSONL event stream. Replay resolves each tool event against a fixture map, compares observed results with recorded results and returns structured mismatches.

See [`docs/architecture.md`](docs/architecture.md) for the data model and trade-offs.

## V1 boundary

V1 replays tool events, not model token streams; model outputs may be stored as events but are not regenerated.

## Development

```bash
python -m unittest discover -s tests -v
```

MIT licensed.


## v0.1.1

**Tamper-evident replay logs.** Recorder events are now SHA-256 hash chained, resumable across recorder instances, and can be integrity-verified before fixture replay.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
