import unittest
from scripts.grounded_prose_benchmark import Runtime

class BenchmarkRoutingTests(unittest.TestCase):
 def test_regression_fixture_uses_guangming_parser(self):
 
     class Base:
         def canonical(self, corpus, raw, context, arm):
             assert corpus == "guangming"
             assert raw["content"] == '{"sentences":[{"text":"supported","evidence":["E1S1"]}]}'
             return {"sentences": []}, True, {"parser": corpus}
     runtime = Runtime.__new__(Runtime)
     runtime.base = Base()
     raw = {"content": '{"sentences":[{"text":"supported","evidence":["E1S1"]}]}'}
     assert runtime.canonical({"arm":"baseline","corpus":"regression","context":{"x":"supported"}}, raw)[1]
