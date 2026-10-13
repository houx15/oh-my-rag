"""Transports: offline mocked first, live fail-closed. Dispatch always goes through the budget gate.

MockTransport serves scripted responses/errors per request kind (script mutation
is lock-protected; a `closed` flag makes late calls after a selector deadline fail
loudly so abandoned calls can never pass untracked) and records every call plus
observed concurrency — it never touches the network. DispatchGate wraps ANY
transport with reserve-before-dispatch accounting, bounded retries, the global
deadline and telemetry. It catches ARBITRARY transport exceptions (not just
TransportError) so a reservation can never be left open by an unexpected crash:
unknown outcome settles conservatively, without refund.

Responses may carry `usage` {input_tokens, output_tokens} and measured
`events_perfcounter` timestamps (first_reasoning_token / first_content_token /
full_response) which the gate converts to TTFT/full durations relative to the
dispatch start it measured itself.

The LiveTransport in this offline build ALWAYS refuses: live dispatch requires
(1) manifest.authorized == true (currently false pending the user's independent
review), (2) a pinned AND verified non-paused tariff, (3) manifest bounds, request
cap and ledger — and even then a real provider adapter must be registered in a
separate, independently reviewed change. For Jev, that adapter must re-serialize
payloads through the official SDK types (typesafe_sdk Noul/NoulCriteria via
client.system_one) — the dict payloads used with the mock are labeled
mock abstractions, not raw API bodies. No credentials are read here.
"""
from __future__ import annotations

import threading
import time

from eval.optimization.budget import AuthorizationError, SpendLedger
from eval.optimization.telemetry import Telemetry

KINDS = ("rerank_noul", "classify_passage", "chat", "embed")


class TransportError(RuntimeError):
    pass


class MockTransport:
    """Scripted transport. scripts: {kind: [step, ...]}; a step is
    {"response": {...}} or {"error": "..."}; steps advance in order and cycle
    only when a single step remains. Thread-safe; `close()` refuses late calls."""

    def __init__(self, scripts: dict | None = None, *, latency_s: float = 0.0):
        self.scripts = {k: list(v) for k, v in (scripts or {}).items()}
        self.latency_s = latency_s
        self.calls: list[dict] = []
        self._active = 0
        self.max_concurrency_observed = 0
        self._closed = False
        self._lock = threading.Lock()

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def _step_locked(self, kind: str) -> dict:
        steps = self.scripts.get(kind)
        if not steps:
            raise TransportError(f"mock transport: no scripted steps for kind {kind!r}")
        step = steps[0] if len(steps) == 1 else steps.pop(0)
        if "error" in step:
            raise TransportError(str(step["error"]))
        return step["response"]

    def call(self, kind: str, payload: dict) -> dict:
        if kind not in KINDS:
            raise TransportError(f"unknown request kind {kind!r}")
        with self._lock:
            if self._closed:
                raise TransportError("mock transport closed (selector deadline passed) — late call refused")
            self._active += 1
            self.max_concurrency_observed = max(self.max_concurrency_observed, self._active)
            self.calls.append({"kind": kind, "payload": payload, "epoch": time.time()})
        try:
            if self.latency_s:
                time.sleep(self.latency_s)
            with self._lock:
                return self._step_locked(kind)
        finally:
            with self._lock:
                self._active -= 1


class LiveTransport:
    """Placeholder live transport: refuses everything in this offline build."""

    def __init__(self, manifest):
        if not manifest.live_allowed():
            raise AuthorizationError(
                "live transport unavailable: authorization manifest is not authorized "
                "(missing approval defaults to cap zero)")
        raise AuthorizationError(
            "live provider adapters are not registered in this offline build — register, validate "
            "payload serialization against the official API/SDK, and review them in a separate "
            "change before any live dispatch")

    def call(self, kind: str, payload: dict) -> dict:
        raise AuthorizationError("live dispatch disabled in offline build")


class DispatchGate:
    """Reserve -> dispatch -> settle. Bounded retries; global deadline; telemetry.

    Any exception from the transport (arbitrary, not only TransportError) settles
    the reservation conservatively — an open reservation is never leaked.
    """

    def __init__(self, transport, ledger: SpendLedger, manifest, *, simulated: bool = False):
        self.transport = transport
        self.ledger = ledger
        self.manifest = manifest
        self.simulated = simulated

    def dispatch(self, *, kind: str, payload: dict, model: str, est_input_tokens: int,
                 est_output_tokens: int, telemetry: Telemetry | None = None) -> dict:
        attempt = 0
        last_error: Exception | None = None
        while attempt <= self.manifest.max_retries:
            is_retry = attempt > 0
            dispatch_start = time.perf_counter()
            try:
                reservation = self.ledger.reserve(model, est_input_tokens, est_output_tokens, is_retry=is_retry)
            except AuthorizationError as e:
                if telemetry is not None:
                    telemetry.attempt(attempt=attempt, model=model, error=f"reserve rejected: {e}", is_retry=is_retry)
                raise
            try:
                response = self.transport.call(kind, payload)
            except Exception as e:  # arbitrary failure: unknown outcome -> conservative charge
                last_error = e
                rec = self.ledger.settle(reservation["id"], usage=None, error=f"{type(e).__name__}: {e}")
                if telemetry is not None:
                    telemetry.attempt(attempt=attempt, model=model, error=str(e), is_retry=is_retry,
                                      cost_usd=rec["charged_usd"], conservative_charge=True)
                attempt += 1
                if attempt > self.manifest.max_retries:
                    raise
                continue  # the retry re-reserves, so the ledger's persisted deadline still guards it
            usage = response.get("usage") if isinstance(response, dict) else None
            rec = self.ledger.settle(reservation["id"], usage=usage)
            if telemetry is not None:
                telemetry.attempt(attempt=attempt, model=model, usage=usage,
                                  cost_usd=rec["charged_usd"], is_retry=is_retry,
                                  conservative_charge=usage is None)
                events = response.get("events_perfcounter") if isinstance(response, dict) else None
                if isinstance(events, dict):
                    telemetry.record_generation_events(dispatch_start, events)
            return response
        raise last_error or TransportError("dispatch retries exhausted")
