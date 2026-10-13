import unittest
from unittest.mock import MagicMock
from newdomain.bailian_transport_v2 import _ContinuationLedger

class ContinuationAccountingTest(unittest.TestCase):
    def test_resumed_failure_is_counted_without_touching_settlement(self):
        ledger=MagicMock();wrapped=_ContinuationLedger(ledger)
        wrapped.reserve('model',1,2,is_retry=False)
        ledger.reserve.assert_called_once_with('model',1,2,is_retry=True)
        wrapped.settle('reservation',usage=None)
        ledger.settle.assert_called_once_with('reservation',usage=None)
