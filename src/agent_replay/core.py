from dataclasses import dataclass,asdict
import json
SENSITIVE={'token','password','secret','authorization','api_key'}
def redact(v):
    if isinstance(v,dict): return {k:('[REDACTED]' if k.lower() in SENSITIVE else redact(x)) for k,x in v.items()}
    if isinstance(v,list): return [redact(x) for x in v]
    return v
@dataclass
class Event: seq:int; kind:str; name:str; payload:object=None; result:object=None
class Recorder:
    def __init__(self,path): self.path=path; self.seq=0
    def append(self,kind,name,payload=None,result=None):
        self.seq+=1; e=Event(self.seq,kind,name,redact(payload),redact(result))
        with open(self.path,'a') as f: f.write(json.dumps(asdict(e),sort_keys=True)+'\n')
        return e
def load(path): return [Event(**json.loads(line)) for line in open(path) if line.strip()]
def replay(events,fixtures):
    diffs=[]
    for e in events:
        if e.kind!='tool': continue
        key=json.dumps(e.payload,sort_keys=True,separators=(',',':')); observed=fixtures.get(e.name,{}).get(key,{'__missing_fixture__':True})
        if observed!=e.result: diffs.append({'seq':e.seq,'tool':e.name,'expected':e.result,'observed':observed})
    return diffs
