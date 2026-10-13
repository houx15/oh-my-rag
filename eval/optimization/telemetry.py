"""Request-level telemetry: monotonic spans, TTFT vs first verified answer, per-attempt accounting.

Timing contract: the DISPATCHER records its own dispatch start on the monotonic
clock; the TRANSPORT supplies measured `events_perfcounter` timestamps for
first_reasoning_token / first_content_token / full_response (a real streaming
adapter measures its stream events; the mock supplies ordered values). The gate
converts them to milliseconds relative to dispatch. TTFT (content) is distinct
from reasoning start and from full response — and from `first_verified_usable_ms`,
which is only set when deterministic verification accepts output: token arrival is
never treated as a usable, verified answer.
"""
from __future__ import annotations

import time


class Telemetry:
    def __init__(self, question_id: str, arm: str, exposure: str):
        self.base = time.perf_counter()
        self.record = {
            "question_id": question_id,
            "arm": arm,
            "exposure": exposure,
            "marks_perfcounter": {},
            "spans_ms": {},
            "generation": {"ttft_content_ms": None, "ttft_reasoning_ms": None,
                           "full_response_ms": None, "event_order_anomaly": False},
            "first_verified_usable_ms": None,
            "cache": {},
            "attempts": [],
            "fallback": None,
        }

    def mark(self, name: str) -> float:
        self.record["marks_perfcounter"][name] = time.perf_counter()
        return self.record["marks_perfcounter"][name]

    def span(self, start_mark: str, end_mark: str, span_name: str) -> float:
        a = self.record["marks_perfcounter"][start_mark]
        b = self.record["marks_perfcounter"][end_mark]
        ms = max(0.0, (b - a) * 1000.0)
        self.record["spans_ms"][span_name] = round(ms, 3)
        return ms

    def record_generation_events(self, dispatch_perfcounter: float, events: dict) -> None:
        """events: monotonic perf_counter timestamps measured by the transport."""
        g = self.record["generation"]
        try:
            r = events.get("first_reasoning_token")
            c = events.get("first_content_token")
            f = events.get("full_response")
            present = [p for p in (r, c, f) if p is not None]
            if len(present) >= 2 and any(present[i] > present[i + 1] + 1e-9 for i in range(len(present) - 1)):
                g["event_order_anomaly"] = True
            if r is not None:
                g["ttft_reasoning_ms"] = round(max(0.0, (r - dispatch_perfcounter) * 1000.0), 3)
            if c is not None:
                g["ttft_content_ms"] = round(max(0.0, (c - dispatch_perfcounter) * 1000.0), 3)
            if f is not None:
                g["full_response_ms"] = round(max(0.0, (f - dispatch_perfcounter) * 1000.0), 3)
        except (TypeError, ValueError):
            g["event_order_anomaly"] = True

    @property
    def ttft_ms(self):
        return self.record["generation"]["ttft_content_ms"]

    def set_first_verified(self) -> None:
        if self.record["first_verified_usable_ms"] is None:
            self.record["first_verified_usable_ms"] = round((time.perf_counter() - self.base) * 1000.0, 3)

    def cache(self, kind: str, hit: bool) -> None:
        self.record["cache"][kind] = "hit" if hit else "miss"

    def attempt(self, *, attempt: int, model: str, usage=None, cost_usd=None,
                error: str = None, is_retry: bool = False, conservative_charge: bool = False) -> None:
        self.record["attempts"].append({
            "attempt": attempt, "model": model,
            "usage": usage, "cost_usd": cost_usd,
            "error": error, "is_retry": is_retry,
            "conservative_charge": conservative_charge,
        })

    def set_fallback(self, reason: str) -> None:
        if self.record["fallback"] is None:
            self.record["fallback"] = reason

    def finalize(self) -> dict:
        out = dict(self.record)
        out.pop("marks_perfcounter", None)
        return out
