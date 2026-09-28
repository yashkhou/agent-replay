# Implementation note

Working V1 scope: Provider-neutral record/replay for agent tool sessions with redaction, fixture-backed execution and regression diffs.

Verified with `python -m unittest discover -s tests -v`.

Known boundary: V1 replays tool events, not model token streams; model outputs may be stored as events but are not regenerated.
