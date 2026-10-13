import tempfile
import threading
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from newdomain.experiment import ExperimentContext


class ExperimentAllocation(unittest.TestCase):
    def test_conservative_admission_and_history_cannot_reset(self):
        with tempfile.TemporaryDirectory() as d:
            c = ExperimentContext.__new__(ExperimentContext)
            c.experiment_root = Path(d)
            c.manifest_path = Path(d) / "manifest.json"
            c.budget = {"baseline_current_ledgers_usd": "10", "additional_cap_usd": "12"}
            c._experiment_thread_lock = threading.Lock()
            c.manifest = SimpleNamespace(tariff=lambda model:SimpleNamespace(cost=lambda i,o:3))
            with patch("newdomain.experiment.chat_conservative_estimates", return_value=(100,10)):
                for charged, opened, accepted in [(10,0,True),(19,0,True),(20,0,False),(18,2,False),(9,0,False)]:
                    with self.subTest(charged=charged,opened=opened), patch("newdomain.experiment.canonical_totals",return_value=(Decimal(charged),Decimal(opened))):
                        if accepted:
                            with c.request_scope("approved-test-model"):
                                pass
                        else:
                            with self.assertRaises(RuntimeError), c.request_scope("approved-test-model"):
                                self.fail("overspend admitted")
