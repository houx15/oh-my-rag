"""Consolidated transport chain for the new-domain evaluation pipeline.

Consolidates (behavior-preserving, from external task folders):
  - live_deepseek_transport.py  → DeepSeekStreamTransport (streaming HTTP)
  - deadline_transport.py       → DeadlineTransport (killable subprocess worker)
  - paid_transport.py           → budget-gated dispatch with privacy checks

Authorization model:
  - Low-level adapters (DeepSeekStreamTransport, DeadlineTransport) are
    default-deny: they require an explicit LiveContext to make any network
    call. Without one, .call() raises immediately.
  - A LiveContext is constructed ONLY by the CLI entrypoints when --live is
    passed, and carries the manifest/ledger/denylist configuration.
  - The eval/optimization budget module (AuthorizationManifest, SpendLedger)
    enforces caps, deadlines, prior-hash verification and reserve-before-dispatch.
  - All validation uses explicit exceptions (not assert) so python -O cannot
    bypass safety checks.

No credentials are read at import time or by any offline path.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from eval.optimization.budget import (AuthorizationError, AuthorizationManifest,
                                       SpendLedger, chat_conservative_estimates)
from eval.optimization.transports import DispatchGate, TransportError


class LiveAuthorizationError(RuntimeError):
    """Raised when live dispatch is attempted without proper authorization."""


class PrivacyViolation(RuntimeError):
    """Raised when outbound content matches a privacy pattern or denylist entry."""


class PriorLedgerError(RuntimeError):
    """Raised when prior-ledger hash verification fails."""


class LiveContext:
    """Explicit reviewed authorization for live provider calls.

    Constructed only by CLI entrypoints with --live; carries the external
    manifest, ledger directory (derived from manifest directory — not
    arbitrary), and denylist path. Validates prior hashes and current
    authorization state on construction.
    """
    def __init__(self, *, manifest_path: Path, redaction_names_path: Path,
                 stage: str = "dev", expected_ledger_path: Path = None):
        self.manifest_path = Path(manifest_path).resolve()
        self.redaction_names_path = Path(redaction_names_path).resolve()
        self.stage = stage
        self.ledger_dir = self.manifest_path.parent

        if not self.manifest_path.exists():
            raise LiveAuthorizationError(f"Manifest not found: {self.manifest_path}")
        self.manifest = AuthorizationManifest.load(self.manifest_path)
        self._manifest_sha256 = hashlib.sha256(self.manifest_path.read_bytes()).hexdigest()

        # Validate denylist exists and is a list of strings
        if not self.redaction_names_path.exists():
            raise LiveAuthorizationError(
                f"Redaction denylist not found: {self.redaction_names_path}; "
                "fail-closed: cannot verify outbound safety without it")
        try:
            names = json.loads(self.redaction_names_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise LiveAuthorizationError(f"Denylist unreadable: {e}") from e
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise LiveAuthorizationError(
                "Denylist must be a JSON array of strings; "
                f"got {type(names).__name__}")

        # Verify prior ledgers
        self._check_prior()

        # Require the canonical stage ledger to ALREADY EXIST (no fresh allowance)
        ledger_path = self.ledger_dir / f"ledger.{stage}.json"
        if expected_ledger_path is not None:
            expected = Path(expected_ledger_path).resolve()
            if expected != ledger_path.resolve():
                raise LiveAuthorizationError(
                    f"Ledger path mismatch: profile pins {expected} but "
                    f"manifest directory resolves to {ledger_path.resolve()}. "
                    "Canonical binding requires exact path equality.")
        if not ledger_path.exists():
            raise LiveAuthorizationError(
                f"Canonical {stage} ledger not found at {ledger_path}. "
                "Live dispatch requires an existing ledger with prior spend history; "
                "creating a new ledger at an arbitrary path would reset the allowance. "
                "Refusing to proceed.")
        # Validate existing ledger state (deadline, halted, fingerprint)
        try:
            ledger_state = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise PriorLedgerError(f"Existing ledger unreadable: {e}") from e
        deadline_epoch = ledger_state.get("deadline_epoch")
        if deadline_epoch is not None:
            import time as _time
            if _time.time() > float(deadline_epoch):
                raise LiveAuthorizationError(
                    f"Persisted global deadline has passed "
                    f"({_time.strftime('%Y-%m-%d %H:%M:%S UTC', _time.gmtime(deadline_epoch))}). "
                    "This is a legitimate authorization boundary. Resuming requires "
                    "an explicitly authorized new cycle with a new deadline.")
        if ledger_state.get("halted"):
            raise LiveAuthorizationError(
                f"Ledger is halted: {ledger_state['halted'].get('reason', 'unknown')}. "
                "Manual resume with a recorded human decision is required.")

        # Check authorization flag
        if not self.manifest.live_allowed():
            raise LiveAuthorizationError(
                "Manifest does not authorize live dispatch (authorized=false or cap=0).")

        # Bind to the existing canonical ledger
        self.ledger = SpendLedger(ledger_path, self.manifest, stage=stage, simulated=False)

    def request_scope(self, model):
        from contextlib import nullcontext
        return nullcontext()

    def _check_prior(self):
        """Verify prior-ledger hashes; explicit exceptions, not assert."""
        try:
            m = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise PriorLedgerError(f"Manifest unreadable: {e}") from e
        if hashlib.sha256(self.manifest_path.read_bytes()).hexdigest() != self._manifest_sha256:
            raise PriorLedgerError("authorization manifest changed during live context")
        total = 0.0
        for x in m.get("prior_runs", []):
            f = Path(x["path"])
            if not f.exists():
                raise PriorLedgerError(f"Prior ledger missing: {f}")
            b = f.read_bytes()
            got = hashlib.sha256(b).hexdigest()
            if got != x["sha256"]:
                raise PriorLedgerError(
                    f"Prior ledger hash mismatch: {f} expected {x['sha256'][:16]}… got {got[:16]}…")
            d = json.loads(b)
            if d.get("totals", {}).get("open_reservations", 0) != 0:
                raise PriorLedgerError(
                    f"Prior ledger {f} has open reservations")
            total += d["totals"]["charged_cost_usd"]
        expected = m.get("prior_spend_usd")
        if expected is not None and round(total, 8) != expected:
            raise PriorLedgerError(
                f"Prior spend mismatch: computed {total:.8f} != manifest {expected:.8f}")
        cap = m.get("spend_cap_usd")
        if cap is not None and round(cap + total, 8) != 100:
            raise PriorLedgerError(
                f"Cap chain broken: {cap} + {total} != 100")


# ---------------------------------------------------------------------------
# DeepSeek streaming transport (from live_deepseek_transport.py)
# ---------------------------------------------------------------------------
class DeepSeekStreamTransport:
    """Streaming HTTP adapter. Default-deny: requires a LiveContext to call."""

    def __init__(self, *, model: str, request_timeout_s: float = 45,
                 max_output_tokens: int = 800, thinking: bool = False,
                 temperature: float = 0.2):
        if model not in ("deepseek-v4-pro", "deepseek-flash"):
            raise ValueError("Unapproved model")
        if not 1 <= max_output_tokens <= 800:
            raise ValueError("Output bound")
        if not 1 <= request_timeout_s <= 60:
            raise ValueError("Request deadline bound")
        self.model = model
        self.timeout = request_timeout_s
        self.max_output = max_output_tokens
        self.thinking = thinking
        self.temperature = temperature
        self._live_context: Optional[LiveContext] = None

    def authorize(self, ctx: LiveContext) -> None:
        """Explicitly attach live authorization context."""
        self._live_context = ctx

    def _load_credentials(self) -> Dict[str, str]:
        v = {}
        env_file = _REPO / ".env.local"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, x = line.split("=", 1)
                    if k.strip() in ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"):
                        v[k.strip()] = x.strip().strip("\"'")
        return v

    def call(self, kind: str, payload: dict) -> dict:
        if self._live_context is None:
            raise LiveAuthorizationError(
                "DeepSeekStreamTransport.call requires explicit live context "
                "(construct via CLI --live; this is default-deny)")
        if kind != "chat":
            raise TransportError("Adapter only supports chat")
        messages = payload.get("messages")
        if not isinstance(messages, list) or len(messages) != 2:
            raise TransportError("Exactly two text messages required")
        for m in messages:
            if set(m) != {"role", "content"} or not isinstance(m["content"], str):
                raise TransportError("Invalid text message")
        if [m["role"] for m in messages] != ["system", "user"]:
            raise TransportError("Message roles invalid")
        request_bytes = len(json.dumps(messages, ensure_ascii=False).encode())
        if request_bytes > 30000:
            raise TransportError("Context byte cap exceeded before API request")

        v = self._load_credentials()
        if v.get("DEEPSEEK_BASE_URL", "").rstrip("/") != "https://api.deepseek.com/v1":
            raise TransportError("Existing provider route changed; review required")
        if not v.get("DEEPSEEK_API_KEY"):
            raise TransportError("Existing credential unavailable")

        import requests
        body = {"model": self.model, "messages": messages, "max_tokens": self.max_output,
                "temperature": self.temperature,
                "thinking": {"type": "enabled" if self.thinking else "disabled"},
                "stream": True, "stream_options": {"include_usage": True},
                "response_format": {"type": "json_object"}}
        start = time.perf_counter()
        first_content = first_reasoning = usage = finish = actual = rid = None
        content = []
        done = False
        session = requests.Session()
        try:
            with session.post("https://api.deepseek.com/v1/chat/completions",
                              headers={"Authorization": "Bearer " + v["DEEPSEEK_API_KEY"]},
                              json=body, stream=True,
                              timeout=(5, min(15, self.timeout))) as response:
                if response.status_code != 200:
                    raise TransportError("DeepSeek HTTP " + str(response.status_code))
                response.encoding = "utf-8"
                for line in response.iter_lines(chunk_size=1, decode_unicode=True):
                    now = time.perf_counter()
                    if now - start > self.timeout:
                        raise TransportError("Generation total deadline exceeded; usage may be unknown")
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        done = True
                        break
                    event = json.loads(data)
                    actual = event.get("model", actual)
                    rid = event.get("id", rid)
                    if event.get("usage") is not None:
                        usage = event["usage"]
                    for choice in event.get("choices", []):
                        delta = choice.get("delta", {})
                        if delta.get("reasoning_content") and first_reasoning is None:
                            first_reasoning = now
                        if delta.get("content"):
                            if first_content is None:
                                first_content = now
                                cb = getattr(self, "on_first_content", None)
                                if cb:
                                    cb()
                            content.append(delta["content"])
                        if choice.get("finish_reason") is not None:
                            finish = choice["finish_reason"]
        except requests.RequestException as e:
            raise TransportError("DeepSeek transport " + type(e).__name__ + "; usage may be unknown") from None
        except (ValueError, TypeError, KeyError):
            raise TransportError("Malformed stream; usage may be unknown") from None
        finally:
            session.close()
        end = time.perf_counter()
        parsed_usage = None
        if (isinstance(usage, dict) and type(usage.get("prompt_tokens")) is int
                and type(usage.get("completion_tokens")) is int):
            parsed_usage = {"input_tokens": usage["prompt_tokens"],
                            "output_tokens": usage["completion_tokens"]}
        return {"content": "".join(content), "usage": parsed_usage, "provider_usage": usage,
                "requested_model": self.model, "actual_model": actual, "response_id": rid,
                "finish_reason": finish, "stream_done": done,
                "request_input_bytes": request_bytes, "thinking": self.thinking,
                "events_perfcounter": {"first_reasoning_token": first_reasoning,
                                        "first_content_token": first_content,
                                        "full_response": end},
                "timings": {"request_start_monotonic": start,
                            "first_content_monotonic": first_content,
                            "first_reasoning_monotonic": first_reasoning,
                            "response_end_monotonic": end,
                            "ttft_ms": None if first_content is None else (first_content - start) * 1000,
                            "full_ms": (end - start) * 1000},
                "notes": "No reasoning text persisted. TTFT measures first content delta, not a verified complete answer."}


# ---------------------------------------------------------------------------
# Killable deadline transport (from deadline_transport.py)
# ---------------------------------------------------------------------------
def _request_worker(connection, settings, kind, payload, live_context_config):
    try:
        transport = DeepSeekStreamTransport(**settings)
        # Reconstruct LiveContext in the child process from serializable config
        ctx = LiveContext(
            manifest_path=Path(live_context_config["manifest_path"]),
            redaction_names_path=Path(live_context_config["redaction_names_path"]),
            stage=live_context_config["stage"])
        transport.authorize(ctx)
        transport.on_first_content = lambda: connection.send({"event": "first_content"})
        try:
            connection.send({"ok": True, "response": transport.call(kind, payload)})
        finally:
            pass
    except Exception as e:
        connection.send({"ok": False, "error": type(e).__name__ + ": " + str(e)})
    finally:
        connection.close()


class DeadlineTransport:
    def __init__(self, wall_timeout_s=60, **settings):
        if not 1 <= wall_timeout_s <= 60:
            raise ValueError("wall deadline bound")
        self.settings = settings
        self.wall_timeout_s = wall_timeout_s
        self._live_context: Optional[LiveContext] = None

    def authorize(self, ctx: LiveContext) -> None:
        self._live_context = ctx

    def call(self, kind, payload):
        if self._live_context is None:
            raise LiveAuthorizationError(
                "DeadlineTransport.call requires explicit live context")
        start = time.perf_counter()
        first = None
        ctx = multiprocessing.get_context("spawn")
        receive, send = ctx.Pipe(duplex=False)
        # Inject authorization into worker settings
        worker_settings = dict(self.settings)
        live_config = {
            "manifest_path": str(self._live_context.manifest_path),
            "redaction_names_path": str(self._live_context.redaction_names_path),
            "stage": self._live_context.stage,
        }
        p = ctx.Process(target=_request_worker, args=(send, worker_settings, kind, payload, live_config))
        p.start()
        send.close()
        try:
            while True:
                remaining = self.wall_timeout_s - (time.perf_counter() - start)
                if remaining <= 0 or not receive.poll(remaining):
                    raise TransportError("Hard wall deadline exceeded; outcome/usage unknown, reserve retained")
                try:
                    result = receive.recv()
                except EOFError:
                    raise TransportError("Worker exited without usage; reserve retained") from None
                if result.get("event") == "first_content":
                    if first is None:
                        first = time.perf_counter()
                    continue
                if not result["ok"]:
                    raise TransportError(result["error"])
                end = time.perf_counter()
                response = result["response"]
                response["events_perfcounter"] = {"first_content_token": first, "full_response": end}
                response["parent_observed_timings"] = {
                    "ttft_ms": None if first is None else (first - start) * 1000,
                    "full_ms": (end - start) * 1000,
                    "includes": "worker startup/auth/client/IPC; first content notification on parent monotonic clock"}
                response["clock_scope"] = "Child-local request durations are separate; parent events are comparable to the dispatcher on macOS Python3.9."
                return response
        finally:
            receive.close()
            p.join(timeout=0.2)
            if p.is_alive():
                p.terminate()
                p.join(timeout=1)
            if p.is_alive():
                p.kill()
                p.join(timeout=1)


# ---------------------------------------------------------------------------
# Budget-gated dispatch (ported from paid_transport.py / cycle2_transport.py)
# ---------------------------------------------------------------------------
def screen(messages, redaction_names_path: Path) -> int:
    s = json.dumps(messages, ensure_ascii=False)
    if len(s.encode()) > 30000:
        raise PrivacyViolation("outbound size bound exceeded")
    privacy_check(s, redaction_names_path)
    return len(s.encode())


def privacy_check(payload_text: str, redaction_names_path: Path) -> None:
    if re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", payload_text):
        raise PrivacyViolation("outbound contact-like value blocked")
    if not redaction_names_path.exists():
        raise PrivacyViolation(
            f"redaction denylist not found at {redaction_names_path}; "
            "fail-closed: cannot verify outbound safety without it")
    try:
        names = json.loads(redaction_names_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise PrivacyViolation(f"redaction denylist unreadable: {e}; fail-closed") from e
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise PrivacyViolation(
            f"denylist must be a JSON array of strings, got {type(names).__name__}; fail-closed")
    for n in names:
        if n in payload_text:
            raise PrivacyViolation("outbound personal-contact name blocked")


def chat(ctx: LiveContext, messages, model: str = "deepseek-flash") -> dict:
    """Budget-gated dispatch; revalidates prior hashes before EACH call."""
    with ctx.request_scope(model):
        ctx._check_prior()  # revalidate prior ledger hashes before every dispatch
        screen(messages, ctx.redaction_names_path)
        i, o = chat_conservative_estimates(ctx.manifest, model)
        transport = DeadlineTransport(model=model, thinking=False)
        transport.authorize(ctx)
        return DispatchGate(transport, ctx.ledger, ctx.manifest, simulated=False).dispatch(
            kind="chat", payload={"messages": messages},
            model=model, est_input_tokens=i, est_output_tokens=o)


def estimate_cost(manifest_path: Path, model: str = "deepseek-flash",
                  n_requests: int = 1) -> Dict[str, Any]:
    """Dry-run cost estimation — no credentials, no ledger mutation, no network."""
    if not manifest_path.exists():
        raise LiveAuthorizationError(f"Manifest not found: {manifest_path}")
    m = AuthorizationManifest.load(manifest_path)
    i, o = chat_conservative_estimates(m, model)
    tariff = m.tariff(model)
    per_request = tariff.cost(i, o)
    return {
        "model": model,
        "n_requests": n_requests,
        "input_tokens_per_request": i,
        "output_tokens_per_request": o,
        "cost_per_request_usd": round(per_request, 8),
        "total_estimated_usd": round(per_request * n_requests, 8),
        "spend_cap_usd": m.spend_cap_usd,
        "final_eval_reserve_usd": m.final_eval_reserve_usd,
        "dev_cap_usd": m.dev_cap_usd,
        "manifest_authorized": m.authorized,
        "note": "conservative full-context-bound estimate; actual settled cost may be lower",
    }
