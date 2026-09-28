# Architecture

A trace is an ordered JSONL event stream. Replay resolves each tool event against a fixture map, compares observed results with recorded results and returns structured mismatches.

## Design constraints

- deterministic offline behavior
- explicit machine-readable inputs and outputs
- small standard-library surface area
- failures are surfaced rather than hidden

## V1 limitation

V1 replays tool events, not model token streams; model outputs may be stored as events but are not regenerated.
