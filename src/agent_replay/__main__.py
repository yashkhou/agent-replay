import json,sys
from .core import load,replay
d=replay(load(sys.argv[1]),json.load(open(sys.argv[2]))); print(json.dumps({'passed':not d,'diffs':d},indent=2)); raise SystemExit(1 if d else 0)
