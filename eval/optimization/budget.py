"""Hard budget controls: authorization manifest, pinned tariffs, reserve-before-dispatch ledger.

Fail-closed rules (independent budget reviews 1 & 2, 2026-10-10, incorporated):
- missing manifest file -> CAP ZERO; present-but-invalid -> loud error; `authorized`
  is a STRICT boolean; token/request bounds are STRICT integers; USD-only currency;
- tariffs: null rates + status = PAUSED; finite unverified rates are simulation-only
  (live dispatch requires a verified tariff); unknown model = unknown pricing = reject;
- stage separation with ONE canonical ledger per stage shared by all providers:
  data/spend_ledger.dev.json (allowance = cap - reserve) and
  data/spend_ledger.final.json (allowance = reserve); a changed manifest NEVER gets a
  fresh allowance automatically — a ledger file created under a different manifest
  fingerprint is refused, and a vanished ledger at a known path (lockfile present)
  is refused rather than recreated;
- every dispatch reserves conservatively BEFORE the call; in-flight reservations
  count against the stage allowance; concurrency-safe across threads AND processes
  (fcntl file lock around reload->mutate->persist);
- reload validation on EVERY operation (not just construction): schema, stage,
  simulation flag, manifest fingerprint, persisted absolute deadline epoch, and
  totals-vs-reservations recomputation. A corrupt or inconsistent ledger fails
  closed — it is never silently repaired from stale in-memory state (that could
  discard another worker's committed spend);
- the global deadline is persisted as an ABSOLUTE epoch at ledger creation:
  restarting the process does not reset it;
- settling with missing/incomplete/malformed usage retains the estimate (no refund);
  settlement above its reservation persists the ACTUAL overage, flags the violated
  bound and HALTS new dispatch until an explicit human resume() (recorded);
- dev/final committed sums are reported TOGETHER against their caps (stage_report).

This module never reads .env.local or any credentials.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "eval" / "optimization" / "data"
DEFAULT_MANIFEST = DATA_DIR / "auth.manifest.json"
STAGES = ("dev", "final")
EPS = 1e-6


class AuthorizationError(RuntimeError):
    pass


def canonical_ledger_path(stage: str) -> Path:
    if stage not in STAGES:
        raise AuthorizationError(f"stage must be one of {STAGES}")
    return DATA_DIR / f"spend_ledger.{stage}.json"


def stage_report(dev_snapshot: dict | None, final_snapshot: dict | None,
                 manifest: "AuthorizationManifest") -> dict:
    """Dev and final committed sums reported together against their caps."""
    def committed(snap):
        if not snap:
            return 0.0
        t = snap["totals"]
        return round(t["charged_cost_usd"] + t["reserved_open_cost_usd"], 8)

    dev = committed(dev_snapshot)
    fin = committed(final_snapshot)
    return {"currency": "USD",
            "spend_cap_usd": manifest.spend_cap_usd,
            "final_eval_reserve_usd": manifest.final_eval_reserve_usd,
            "dev": {"cap_usd": manifest.dev_cap_usd, "committed_usd": dev},
            "final": {"cap_usd": manifest.final_eval_reserve_usd, "committed_usd": fin},
            "total_committed_usd": round(dev + fin, 8)}


def _num(x, name: str, *, positive: bool = False) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise AuthorizationError(f"{name}: expected a number, got {x!r}")
    v = float(x)
    if math.isnan(v) or math.isinf(v):
        raise AuthorizationError(f"{name}: NaN/inf rejected ({x!r})")
    if v < 0 or (positive and v <= 0):
        raise AuthorizationError(f"{name}: must be {'positive' if positive else 'non-negative'}, got {x!r}")
    return v


def _strict_bool(x, name: str) -> bool:
    if not isinstance(x, bool):
        raise AuthorizationError(f"{name}: must be a strict boolean, got {x!r}")
    return x


def _strict_int(x, name: str, *, minimum: int = 0) -> int:
    if isinstance(x, bool):
        raise AuthorizationError(f"{name}: booleans are not integers (got {x!r})")
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x) or not x.is_integer():
            raise AuthorizationError(f"{name}: fractional/NaN/inf value rejected (got {x!r})")
        x = int(x)
    if not isinstance(x, int):
        raise AuthorizationError(f"{name}: expected an integer, got {x!r}")
    if x < minimum:
        raise AuthorizationError(f"{name}: must be >= {minimum}, got {x!r}")
    return x


def chat_conservative_estimates(manifest: AuthorizationManifest, model: str) -> tuple[int, int]:
    """Proved-cost chat reservation: full pinned model context upper bound for input
    (no tokenizer installed — any smaller number is a guess) plus the output bound."""
    t = manifest.tariff(model)
    if t.context_tokens_upper_bound is None:
        raise AuthorizationError(
            f"{model}: no context_tokens_upper_bound pinned — cannot form a proved input-cost "
            "reservation without a tokenizer; refuse rather than guess")
    return t.context_tokens_upper_bound, manifest.max_output_tokens


def payload_byte_bound(payload, manifest: AuthorizationManifest) -> tuple[int, int]:
    """Proved-cost reservation for typed Noul requests: a UTF-8 token count can never
    exceed the payload's byte count (every token encodes to >=1 byte), so bytes are a
    conservative input upper bound; output bound from the manifest."""
    import json as _json
    est_in = len(_json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    return max(1, est_in), manifest.max_output_tokens


class Tariff:
    def __init__(self, model: str, input_per_1m, output_per_1m, *, verified: bool, status: str = "",
                 context_tokens_upper_bound=None):
        self.model = model
        self.verified = _strict_bool(verified, f"{model}.verified")
        self.status = str(status or "")
        self.context_tokens_upper_bound = (None if context_tokens_upper_bound is None
                                           else _strict_int(context_tokens_upper_bound,
                                                            f"{model}.context_tokens_upper_bound", minimum=1))
        if input_per_1m is None or output_per_1m is None:
            if self.verified:
                raise AuthorizationError(f"{model}: null rates cannot be marked verified")
            self.input_per_1m = None
            self.output_per_1m = None
            self.paused = True
            if not self.status:
                raise AuthorizationError(f"{model}: paused entry requires a status reason")
        else:
            self.input_per_1m = _num(input_per_1m, f"{model}.input_per_1m")
            self.output_per_1m = _num(output_per_1m, f"{model}.output_per_1m")
            self.paused = False

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        if self.paused:
            raise AuthorizationError(f"{self.model}: provider PAUSED ({self.status}) — cost unbounded, dispatch refused")
        return input_tokens / 1e6 * self.input_per_1m + output_tokens / 1e6 * self.output_per_1m

    def live_dispatchable(self) -> bool:
        return self.verified and not self.paused

    def as_dict(self) -> dict:
        return {"input_per_1m": self.input_per_1m, "output_per_1m": self.output_per_1m,
                "verified": self.verified, "status": self.status or None, "paused": self.paused}


class AuthorizationManifest:
    def __init__(self, data: dict, path: Path | None = None):
        self.path = path
        self._raw = data
        self.authorized = _strict_bool(data.get("authorized", False), "authorized")
        self.currency = str(data.get("currency", "USD"))
        if self.currency != "USD":
            raise AuthorizationError(
                f"currency must be USD for this authorization (explicit validation); got {self.currency!r}")
        self.spend_cap_usd = _num(data.get("spend_cap_usd", 0), "spend_cap_usd")
        self.final_eval_reserve_usd = _num(data.get("final_eval_reserve_usd", 0), "final_eval_reserve_usd")
        if self.final_eval_reserve_usd > self.spend_cap_usd:
            raise AuthorizationError("final_eval_reserve_usd exceeds spend_cap_usd")
        self.dev_cap_usd = self.spend_cap_usd - self.final_eval_reserve_usd
        self.max_input_tokens = _strict_int(data.get("max_input_tokens", 0), "max_input_tokens", minimum=1)
        self.max_output_tokens = _strict_int(data.get("max_output_tokens", 0), "max_output_tokens", minimum=1)
        self.request_cap = _strict_int(data.get("request_cap", 0), "request_cap", minimum=0)
        self.max_retries = _strict_int(data.get("max_retries", 0), "max_retries", minimum=0)
        self.selector_deadline_s = _num(data.get("selector_deadline_s", 30), "selector_deadline_s", positive=True)
        self.global_deadline_s = _num(data.get("global_deadline_s", 0), "global_deadline_s", positive=True)
        self.max_concurrency = _strict_int(data.get("max_concurrency", 1), "max_concurrency", minimum=1)
        self.status_note = str(data.get("status_note", ""))
        self.models: dict[str, Tariff] = {}
        for name, spec in (data.get("models") or {}).items():
            self.models[str(name)] = Tariff(
                str(name), spec.get("input_per_1m"), spec.get("output_per_1m"),
                verified=spec.get("verified", False), status=str(spec.get("status") or ""),
                context_tokens_upper_bound=spec.get("context_tokens_upper_bound"))
        self.created_monotonic = time.monotonic()

    def fingerprint(self) -> str:
        return hashlib.sha256(
            json.dumps(self._raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    def stage_allowance(self, stage: str) -> float:
        if stage == "dev":
            return self.dev_cap_usd
        if stage == "final":
            return self.final_eval_reserve_usd
        raise AuthorizationError(f"unknown stage {stage!r}; expected one of {STAGES}")

    @classmethod
    def cap_zero(cls) -> "AuthorizationManifest":
        return cls({"authorized": False, "spend_cap_usd": 0, "final_eval_reserve_usd": 0,
                    "max_input_tokens": 1, "max_output_tokens": 1, "request_cap": 0,
                    "max_retries": 0, "selector_deadline_s": 30,
                    "global_deadline_s": 3600, "max_concurrency": 1, "models": {},
                    "status_note": "CAP ZERO — no manifest found; missing approval defaults to cap zero"})

    @classmethod
    def load(cls, path: Path = DEFAULT_MANIFEST) -> "AuthorizationManifest":
        p = Path(path)
        if not p.exists():
            return cls.cap_zero()
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise AuthorizationError(f"authorization manifest {p} is corrupt: {e}") from e
        return cls(data, path=p)

    def tariff(self, model: str) -> Tariff:
        t = self.models.get(model)
        if t is None:
            raise AuthorizationError(
                f"unknown pricing for model {model!r} — not pinned in the authorization manifest; "
                "state tariffs explicitly, never invent them")
        return t

    def live_allowed(self) -> bool:
        return self.authorized and self.spend_cap_usd > 0

    def summary(self) -> dict:
        return {"authorized": self.authorized, "currency": self.currency,
                "spend_cap_usd": self.spend_cap_usd,
                "final_eval_reserve_usd": self.final_eval_reserve_usd, "dev_cap_usd": self.dev_cap_usd,
                "request_cap": self.request_cap, "models": {k: v.as_dict() for k, v in self.models.items()}}


def _fresh_state(manifest: AuthorizationManifest, stage: str, simulated: bool) -> dict:
    return {"schema": 2, "stage": stage, "simulated": simulated,
            "manifest_fingerprint": manifest.fingerprint(),
            "deadline_epoch": time.time() + manifest.global_deadline_s,
            "reservations": [], "halted": None, "resume_log": [],
            "totals": {"requests_dispatched": 0, "retries": 0, "open_reservations": 0,
                       "reserved_open_cost_usd": 0.0, "charged_cost_usd": 0.0,
                       "overage_usd": 0.0, "conservative_settlements": 0}}


def _strict_bool_state(x, name: str) -> bool:
    return isinstance(x, bool)


def _validate_state(state, manifest: AuthorizationManifest, stage: str, simulated: bool) -> None:
    """Full consistency validation on EVERY reload. Any problem fails closed."""
    if not isinstance(state, dict) or state.get("schema") != 2:
        raise AuthorizationError("spend ledger: unsupported/missing schema — refusing")
    if state.get("stage") != stage or bool(state.get("simulated")) != simulated:
        raise AuthorizationError(
            f"spend ledger stage/simulation mismatch (file: {state.get('stage')}/{state.get('simulated')}, "
            f"requested: {stage}/{simulated})")
    if state.get("manifest_fingerprint") != manifest.fingerprint():
        raise AuthorizationError(
            "spend ledger was created under a DIFFERENT authorization manifest — a changed manifest "
            "never gets a fresh allowance automatically; use a new ledger path after explicit review")
    de = state.get("deadline_epoch")
    if isinstance(de, bool) or not isinstance(de, (int, float)) or math.isnan(de) or math.isinf(de):
        raise AuthorizationError("spend ledger: invalid persisted deadline_epoch — refusing")
    if not _strict_bool_state(state.get("simulated"), "simulated"):
        raise AuthorizationError("spend ledger: simulated flag corrupted — refusing")
    reservations = state.get("reservations")
    if not isinstance(reservations, list):
        raise AuthorizationError("spend ledger: reservations corrupted — refusing")
    ids = []
    allowed_states = {"open", "settled_usage", "settled_error_with_usage", "settled_conservative"}
    for r in reservations:
        if not isinstance(r, dict):
            raise AuthorizationError("spend ledger: reservation entry corrupted — refusing")
        rid = r.get("id")
        if not isinstance(rid, str) or not rid:
            raise AuthorizationError("spend ledger: reservation id corrupted — refusing")
        ids.append(rid)
        if r.get("state") not in allowed_states:
            raise AuthorizationError(f"spend ledger: reservation {rid} state corrupted — refusing")
        if not isinstance(r.get("model"), str) or not r.get("model"):
            raise AuthorizationError(f"spend ledger: reservation {rid} model corrupted — refusing")
        for field in ("est_input_tokens", "est_output_tokens"):
            v = r.get(field)
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise AuthorizationError(f"spend ledger: reservation {rid} {field} corrupted — refusing")
        fields = ["est_cost_usd"] if r.get("state") == "open" else ["est_cost_usd", "charged_usd"]
        for field in fields:
            v = r.get(field)
            if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) \
               or math.isnan(v) or math.isinf(v) or v < 0:
                raise AuthorizationError(f"spend ledger: reservation {rid} {field} corrupted "
                                         "(must be finite non-negative) — refusing")
    if len(set(ids)) != len(ids):
        raise AuthorizationError("spend ledger: reservation ids duplicated — refusing")
    t = state.get("totals")
    if not isinstance(t, dict):
        raise AuthorizationError("spend ledger: totals corrupted — refusing")
    for field in ("requests_dispatched", "retries", "open_reservations", "conservative_settlements"):
        v = t.get(field)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise AuthorizationError(f"spend ledger: totals.{field} corrupted (must be a non-negative int) — refusing")
    for field in ("reserved_open_cost_usd", "charged_cost_usd", "overage_usd"):
        v = t.get(field)
        if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) \
           or math.isnan(v) or math.isinf(v) or v < 0:
            raise AuthorizationError(f"spend ledger: totals.{field} corrupted "
                                     "(must be finite non-negative; NaN/negative refused) — refusing")
    open_recs = [r for r in reservations if r.get("state") == "open"]
    settled = [r for r in reservations if r.get("state") != "open"]
    expect = {
        "open_reservations": len(open_recs),
        "reserved_open_cost_usd": sum(r.get("est_cost_usd", 0.0) for r in open_recs),
        "charged_cost_usd": sum(r.get("charged_usd", 0.0) for r in settled),
        "requests_dispatched": len(settled),
        "retries": sum(1 for r in reservations if r.get("is_retry")),
        "conservative_settlements": sum(1 for r in settled if r.get("state") == "settled_conservative"),
        "overage_usd": sum(max(0.0, r.get("charged_usd", 0.0) - r.get("est_cost_usd", 0.0))
                           for r in settled if r.get("bound_violated")),
    }
    for key, want in expect.items():
        have = t.get(key)
        if have is None or abs(float(have) - float(want)) > EPS:
            raise AuthorizationError(
                f"spend ledger inconsistent: totals.{key}={have!r} but reservations recompute to {want!r} — refusing")


class SpendLedger:
    """Durable reserve-before-dispatch ledger; one canonical file per stage."""

    def __init__(self, path: Path | None, manifest: AuthorizationManifest, *, stage: str = "dev",
                 simulated: bool = False, batch_policy=None):
        self.batch_policy = batch_policy
        if stage not in STAGES:
            raise AuthorizationError(f"stage must be one of {STAGES}, got {stage!r}")
        self.path = Path(path) if path else canonical_ledger_path(stage)
        self.manifest = manifest
        self.stage = stage
        self.simulated = simulated
        self._tlock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lockfile = self.path.with_suffix(self.path.suffix + ".lock")
        with self._locked(initial=True):
            pass  # construction path handled below

    # -- locking / persistence ---------------------------------------------
    @contextmanager
    def _locked(self, *, initial: bool = False):
        with self._tlock:
            with open(self._lockfile, "a+", encoding="utf-8") as lf:
                fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
                try:
                    if self.path.exists():
                        try:
                            raw = self.path.read_text(encoding="utf-8")
                        except OSError as e:
                            raise AuthorizationError(f"spend ledger unreadable: {e}") from e
                        try:
                            state = json.loads(raw)
                        except json.JSONDecodeError as e:
                            raise AuthorizationError(
                                f"spend ledger {self.path} is corrupt — failing closed, "
                                "never repairing from stale memory (that could discard committed spend)"
                            ) from e
                        _validate_state(state, self.manifest, self.stage, self.simulated)
                        self._state = state
                    elif initial:
                        if self._lockfile.exists() and self._lockfile.stat().st_size >= 0 and self._ever_created():
                            raise AuthorizationError(
                                f"refusing fresh allowance at {self.path}: ledger file vanished while a "
                                "lockfile exists — investigate before recreating (a changed manifest must "
                                "not silently reset the cap)")
                        self._state = _fresh_state(self.manifest, self.stage, self.simulated)
                        self._persist_locked()
                    else:
                        raise AuthorizationError(
                            f"spend ledger {self.path} disappeared mid-run — failing closed")
                    yield
                    self._persist_locked()
                finally:
                    fcntl.flock(lf.fileno(), fcntl.LOCK_UN)

    def _ever_created(self) -> bool:
        marker = self.path.with_suffix(self.path.suffix + ".created")
        return marker.exists()

    def _persist_locked(self) -> None:
        marker = self.path.with_suffix(self.path.suffix + ".created")
        if not marker.exists():
            marker.write_text(str(time.time()), encoding="utf-8")
        tmp = self.path.with_suffix(self.path.suffix + f".tmp{os.getpid()}.{threading.get_ident()}")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._state, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    # -- guards -------------------------------------------------------------
    def _require_not_halted_locked(self) -> None:
        if self._state.get("successor_allocation"):
            raise AuthorizationError("ledger retired into recorded successor allocation; historical counters are preserved")
        if self._state.get("halted"):
            raise AuthorizationError(
                f"ledger HALTED: {self._state['halted'].get('reason')} — "
                "manual resume() with a recorded human decision is required")

    def _require_before_deadline_locked(self) -> None:
        if self.batch_policy is not None:
            self.batch_policy.check_deadline(self._state)
            return
        if time.time() > float(self._state["deadline_epoch"]):
            raise AuthorizationError(
                "persisted global deadline (absolute epoch) passed — no further dispatch or retry; "
                "restarting the process does not reset it")

    def _stage_committed_locked(self) -> float:
        t = self._state["totals"]
        return t["charged_cost_usd"] + t["reserved_open_cost_usd"]

    # -- API --------------------------------------------------------------
    def reserve(self, model: str, est_input_tokens: int, est_output_tokens: int,
                *, is_retry: bool = False) -> dict:
        est_in = _strict_int(est_input_tokens, "est_input_tokens", minimum=1)
        est_out = _strict_int(est_output_tokens, "est_output_tokens", minimum=1)
        if est_out > self.manifest.max_output_tokens:
            raise AuthorizationError(
                f"output estimate ({est_out}) exceeds manifest bound ({self.manifest.max_output_tokens}); "
                "note: max_input_tokens is a REQUEST-CONTENT budget enforced by the shared context "
                "adapter (byte/passage caps), not a cost-reservation limit — the proved-cost path may "
                "reserve the full pinned model context upper bound")
        if not self.simulated and not self.manifest.live_allowed():
            raise AuthorizationError(
                "live dispatch not authorized (authorized=false or cap=0) — missing approval defaults to cap zero")
        tariff = self.manifest.tariff(model)
        if not self.simulated and not tariff.live_dispatchable():
            raise AuthorizationError(
                f"{model}: tariff is not verified for live dispatch "
                f"(verified={tariff.verified}, paused={tariff.paused}) — unverified live rates are refused")
        if (not self.simulated and tariff.context_tokens_upper_bound is not None
                and est_in < tariff.context_tokens_upper_bound):
            raise AuthorizationError(
                f"{model}: live reservation must cover the pinned context upper bound "
                f"({tariff.context_tokens_upper_bound}) — no tokenizer is installed, smaller input "
                "estimates are guesses; use chat_conservative_estimates()")
        est_cost = tariff.cost(est_in, est_out)
        with self._locked():
            self._require_not_halted_locked()
            self._require_before_deadline_locked()
            if self.batch_policy is not None:
                self.batch_policy.admit(self._state, model, est_cost, is_retry)
            t = self._state["totals"]
            if t["open_reservations"] + 1 > self.manifest.max_concurrency:
                raise AuthorizationError(
                    f"concurrency cap reached: in_flight={t['open_reservations']} would exceed "
                    f"max_concurrency={self.manifest.max_concurrency} — settle or lower arm parallelism")
            if t["requests_dispatched"] + t["open_reservations"] + 1 > self.manifest.request_cap:
                raise AuthorizationError(
                    f"request cap reached (dispatched={t['requests_dispatched']}, "
                    f"in_flight={t['open_reservations']}, cap={self.manifest.request_cap})")
            allowance = self.manifest.stage_allowance(self.stage)
            if self._stage_committed_locked() + est_cost > allowance + 1e-12:
                raise AuthorizationError(
                    f"{self.stage} stage cap exceeded: committed={self._stage_committed_locked():.6f} + "
                    f"est={est_cost:.6f} > allowance={allowance:.6f} "
                    f"(dev cap and final reserve are enforced separately)")
            rid = uuid.uuid4().hex[:12]
            rec = {"id": rid, "model": model, "est_input_tokens": est_in, "est_output_tokens": est_out,
                   "est_cost_usd": round(est_cost, 8), "state": "open",
                   "is_retry": is_retry, "created_epoch": time.time()}
            if self.batch_policy is not None:
                rec["batch_id"] = self.batch_policy.id
            self._state["reservations"].append(rec)
            t["open_reservations"] += 1
            t["reserved_open_cost_usd"] = round(t["reserved_open_cost_usd"] + est_cost, 8)
            if is_retry:
                t["retries"] += 1
            return dict(rec)

    def settle(self, reservation_id: str, usage, *, error: str | None = None) -> dict:
        with self._locked():
            rec = next((r for r in self._state["reservations"] if r["id"] == reservation_id), None)
            if rec is None or rec["state"] != "open":
                raise AuthorizationError(f"reservation {reservation_id} not open")
            t = self._state["totals"]
            complete = (isinstance(usage, dict)
                        and "input_tokens" in usage and "output_tokens" in usage)
            if complete:
                try:
                    in_tok = _strict_int(usage.get("input_tokens"), "usage.input_tokens")
                    out_tok = _strict_int(usage.get("output_tokens"), "usage.output_tokens")
                    charge = self.manifest.tariff(rec["model"]).cost(in_tok, out_tok)
                    rec.update({"state": "settled_usage" if not error else "settled_error_with_usage",
                                "error": error, "charged_usd": round(charge, 8),
                                "usage": {"input_tokens": in_tok, "output_tokens": out_tok}})
                except AuthorizationError:
                    complete = False
            if not complete:
                rec.update({"state": "settled_conservative", "error": error,
                            "charged_usd": rec["est_cost_usd"], "usage": None})
                charge = rec["est_cost_usd"]
                t["conservative_settlements"] += 1
            t["open_reservations"] -= 1
            t["reserved_open_cost_usd"] = round(t["reserved_open_cost_usd"] - rec["est_cost_usd"], 8)
            t["charged_cost_usd"] = round(t["charged_cost_usd"] + charge, 8)
            t["requests_dispatched"] += 1
            if charge > rec["est_cost_usd"] + 1e-9:
                over = round(charge - rec["est_cost_usd"], 8)
                t["overage_usd"] = round(t["overage_usd"] + over, 8)
                rec["bound_violated"] = True
                self._state["halted"] = {
                    "reason": (f"settlement {reservation_id} exceeded its reservation estimate "
                               f"by ${over:.8f} (actual ${charge:.8f} vs est ${rec['est_cost_usd']:.8f}) — "
                               "overage persisted, new dispatch halted pending human resume"),
                    "since_epoch": time.time()}
            return dict(rec)

    def resume(self, human_decision: str) -> None:
        with self._locked():
            if self._state.get("halted"):
                self._state["resume_log"].append({"decision": str(human_decision),
                                                  "resumed_epoch": time.time(),
                                                  "halted_was": self._state["halted"]})
                self._state["halted"] = None

    def snapshot(self) -> dict:
        with self._locked():
            return json.loads(json.dumps(self._state))
