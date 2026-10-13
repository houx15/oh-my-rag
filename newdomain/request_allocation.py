"""Offline append-only request-allocation proposals; never grant live authority.

A proposal cannot alter a manifest, ledger, deadline, reservation or dispatch gate.
The original authority record must be resolved before a proposal is activated by
an independently reviewed runtime integration. Dollar caps are never widened.
"""
import copy
import json
import os
from decimal import Decimal
from pathlib import Path
from newdomain.batch import digest, validate_audit, validate_chain
from eval.optimization.budget import AuthorizationError, _validate_state

SCOPES = (
    ("complete_repeat_reviews", 0, 10),
    ("original60_part1", 48, 24),
    ("original60_part2", 48, 24),
    ("original60_part3", 24, 12),
)


def build_proposal(manifest, final_state, dev_state, budget, *, provenance, previous=None):
    if provenance.get("classification") not in ("unresolved", "administrative_verified") or not provenance.get("evidence"):
        raise AuthorizationError("explicit provenance evidence required")
    for stage, state in (("final", final_state), ("dev", dev_state)):
        _validate_state(state, manifest, stage, simulated=False)
        if state["halted"] or state["totals"]["open_reservations"]:
            raise AuthorizationError("unresolved canonical state")
    validate_audit(final_state)
    closed = {x["batch_id"] for x in final_state.get("batch_closures", [])}
    if any(x["id"] not in closed for x in final_state.get("batch_renewals", [])):
        raise AuthorizationError("unclosed batch")
    raw = manifest._raw
    if Decimal(str(raw.get("original_total_cap_usd", 0))) != Decimal("100"):
        raise AuthorizationError("unexpected original cumulative authority")
    prior = Decimal(str(raw["prior_spend_usd"]))
    if prior + Decimal(str(manifest.spend_cap_usd)) > Decimal("100"):
        raise AuthorizationError("cumulative cap widened")
    charged = sum(Decimal(str(s["totals"]["charged_cost_usd"])) for s in (final_state, dev_state))
    baseline = Decimal(budget["baseline_current_ledgers_usd"])
    if charged < baseline or Decimal(budget["additional_cap_usd"]) != Decimal("12"):
        raise AuthorizationError("nested allocation changed or spend moved backwards")
    headroom = Decimal("12") - (charged - baseline)
    if headroom <= 0:raise AuthorizationError("no nested budget remaining")
    scopes = [{"name": name, "models": {"deepseek-flash": flash, "deepseek-v4-pro": pro},
               "max_calls": flash + pro, "max_retries": 0, "max_seconds": 3600,
               "charged_plus_reserved_cap_usd": "4"} for name, flash, pro in SCOPES]
    additional = sum(s["max_calls"] for s in scopes)
    current = final_state["totals"]["requests_dispatched"]
    if current != manifest.request_cap:raise AuthorizationError("proposal requires exhausted original allocation")
    body = {"id": digest({"manifest":manifest.fingerprint(),"final":final_state,"dev":dev_state,"provenance":provenance}),
            "kind":"request_allocation_proposal_only", "authorizes_dispatch":False,
            "provenance":copy.deepcopy(provenance), "previous_sha256":previous,
            "manifest_fingerprint":manifest.fingerprint(), "original_request_cap":manifest.request_cap,
            "baseline_final_requests":current, "proposed_final_request_cap":current + additional,
            "additional_calls":additional, "scopes":scopes,
            "final_state_sha256":digest(final_state), "dev_state_sha256":digest(dev_state),
            "budget_freeze_sha256":digest(budget), "cumulative_spend_usd":str(prior + charged),
            "nested_remaining_usd":str(headroom), "global_remaining_usd":str(Decimal("100")-prior-charged),
            "activation_requirements":["resolve original request-allocation authority",
                "verify historical ledger file hashes", "pin exact missing and regression job hashes",
                "bind an append-only allowance event to the same canonical final ledger",
                "support review-only and 12-case batches without widening other batch limits",
                "map the prior pre-dispatch terminal failure to a new audited review job; never overwrite its journal",
                "enforce existing global, stage and nested budgets under reservation locks"]}
    return dict(body,sha256=digest(body))


def append_proposal(path, proposal):
    """Append to a private proposal journal only, with locking and chain checks."""
    import fcntl
    path=Path(path)
    # Prevent accidentally targeting any live JSON ledger or manifest.
    if not path.name.endswith(".proposals.jsonl"):
        raise AuthorizationError("proposal-only journal filename required")
    with path.open("a+",encoding="utf-8") as f:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX)
        try:
            f.seek(0);history=[json.loads(line) for line in f if line.strip()]
            if proposal.get("kind")!="request_allocation_proposal_only" or proposal.get("authorizes_dispatch") is not False:
                raise AuthorizationError("proposal must not grant dispatch")
            validate_chain(history+[proposal])
            f.seek(0,2);f.write(json.dumps(proposal,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
        finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)
