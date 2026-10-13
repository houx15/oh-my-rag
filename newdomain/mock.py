"""Mock provider for offline testing of the generation and judge CLIs.

Injects deterministic responses without any network access, credential reads,
or ledger mutations. Used exclusively by tests; never in production paths.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional


class MockChatTransport:
    """Returns a deterministic valid response per call; records all calls."""

    def __init__(self, *, response_content: str = None, fail_on_call: int = None,
                 latency_s: float = 0.0):
        self.response_content = response_content or json.dumps(
            {"sentences": [{"text": "测试回答。", "citations": [
                {"id": "MOCK:1", "quote": "测试内容"}]}], "handoff": False},
            ensure_ascii=False)
        self.fail_on_call = fail_on_call
        self.latency_s = latency_s
        self.call_count = 0
        self.calls: List[Dict] = []

    def call(self, kind: str, payload: Dict) -> Dict:
        self.call_count += 1
        self.calls.append({"kind": kind, "payload_keys": sorted(payload.keys()),
                            "call_number": self.call_count})
        if self.latency_s:
            time.sleep(self.latency_s)
        if self.fail_on_call is not None and self.call_count >= self.fail_on_call:
            from eval.optimization.transports import TransportError
            raise TransportError(f"mock failure on call {self.call_count}")
        now = time.perf_counter()
        return {
            "content": self.response_content,
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "provider_usage": {"prompt_tokens": 100, "completion_tokens": 50},
            "requested_model": "mock", "actual_model": "mock",
            "response_id": f"mock-{self.call_count}", "finish_reason": "stop",
            "stream_done": True, "request_input_bytes": 500, "thinking": False,
            "events_perfcounter": {"first_content_token": now + 0.01,
                                    "full_response": now + 0.02},
            "timings": {"request_start_monotonic": now,
                         "first_content_monotonic": now + 0.01,
                         "response_end_monotonic": now + 0.02,
                         "ttft_ms": 10.0, "full_ms": 20.0},
            "notes": "mock response",
        }


class MockJudgeTransport:
    """Returns a deterministic judge score response."""

    def __init__(self, *, scores: Dict[str, Dict] = None):
        self.default_scores = scores or {
            "correctness": 2, "support": 2, "relevance": 2, "completeness": 2,
            "citation_entailment": True, "reference_complete": True, "issue": "测试"}
        self.call_count = 0

    def call(self, kind: str, payload: Dict) -> Dict:
        self.call_count += 1
        now = time.perf_counter()
        content = json.dumps({"A": self.default_scores}, ensure_ascii=False)
        return {
            "content": content,
            "usage": {"input_tokens": 200, "output_tokens": 30},
            "finish_reason": "stop", "stream_done": True,
            "response_id": f"mock-judge-{self.call_count}",
            "events_perfcounter": {"first_content_token": now, "full_response": now},
        }
