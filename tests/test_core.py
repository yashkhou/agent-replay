import unittest,sys,json; sys.path.insert(0,'src')
from agent_replay.core import *
class T(unittest.TestCase):
 def test_redact(self): self.assertEqual(redact({'token':'x','a':1})['token'],'[REDACTED]')
 def test_replay(self):
  e=[Event(1,'tool','x',{'a':1},{'ok':1})]; k=json.dumps({'a':1},sort_keys=True,separators=(',',':')); self.assertEqual(replay(e,{'x':{k:{'ok':1}}}),[])
 def test_missing_diff(self): self.assertTrue(replay([Event(1,'tool','x',{},1)],{}))
