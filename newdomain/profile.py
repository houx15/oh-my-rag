"""Runtime profile: pins canonical manifest/ledger/denylist paths for live dispatch.

A profile is a private external JSON file (never committed) that binds live
dispatch to specific absolute paths, preventing manifest+ledger copying into
a fresh directory to reset the spend allowance. The CLI requires --profile
for --live mode and verifies every path against the profile before creating
any LiveContext.

Profile schema:
{
  "manifest_path": "/absolute/path/to/manifest.json",
  "manifest_sha256": "<sha256 of manifest file bytes>",
  "dev_ledger_path": "/absolute/path/to/ledger.dev.json",
  "final_ledger_path": "/absolute/path/to/ledger.final.json",
  "redaction_names_path": "/absolute/path/to/denylist.json"
}
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Any


class ProfileError(RuntimeError):
    """Raised when the runtime profile is invalid or paths don't match."""


def load_profile(profile_path: Path) -> Dict[str, str]:
    if not profile_path.exists():
        raise ProfileError(f"Profile not found: {profile_path}")
    try:
        p = json.loads(profile_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise ProfileError(f"Profile unreadable: {e}") from e
    if not isinstance(p, dict):
        raise ProfileError(f"Profile must be a JSON object, got {type(p).__name__}")
    required = {"manifest_path", "manifest_sha256", "dev_ledger_path",
                 "final_ledger_path", "redaction_names_path"}
    missing = required - set(p)
    if missing:
        raise ProfileError(f"Profile missing required fields: {sorted(missing)}")
    # Strict type validation: every field must be a non-empty absolute-path string
    from newdomain.paths import REPO_ROOT
    for field in required:
        val = p[field]
        if not isinstance(val, str) or not val.strip():
            raise ProfileError(
                f"Profile field '{field}' must be a non-empty string, "
                f"got {type(val).__name__}: {val!r}")
        if field != "manifest_sha256":
            path_val = Path(val)
            if not path_val.is_absolute():
                raise ProfileError(
                    f"Profile field '{field}' must be an absolute path, got: {val}")
            resolved = path_val.resolve()
            repo = REPO_ROOT.resolve()
            if resolved == repo or repo in resolved.parents:
                raise ProfileError(
                    f"Profile field '{field}' resolves inside the repo: {resolved}")
    # manifest_sha256 must look like a hex digest
    sha = p["manifest_sha256"]
    if not isinstance(sha, str) or len(sha) != 64:
        raise ProfileError(
            f"Profile manifest_sha256 must be a 64-char hex string, got: {sha!r}")
    try:
        int(sha, 16)
    except ValueError:
        raise ProfileError(f"Profile manifest_sha256 not valid hex: {sha!r}")
    return p


def verify_profile(profile: Dict[str, str], stage: str) -> Dict[str, Path]:
    """Verify all canonical paths exist and manifest hash matches.

    Returns resolved paths dict for LiveContext construction.
    Raises ProfileError on any mismatch — copying files to a new directory
    fails because the profile pins absolute paths.
    """
    if stage not in ("dev", "final"):
        raise ProfileError("invalid stage")
    manifest = Path(profile["manifest_path"]).resolve()
    if not manifest.exists():
        raise ProfileError(f"Profile manifest not found: {manifest}")
    got_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if got_sha != profile["manifest_sha256"]:
        raise ProfileError(
            f"Manifest hash mismatch: profile pins {profile['manifest_sha256'][:16]}… "
            f"but file has {got_sha[:16]}… — manifest changed or wrong file")

    for scope in ("dev", "final"):
        if Path(profile[f"{scope}_ledger_path"]).resolve() != (manifest.parent / f"ledger.{scope}.json").resolve():
            raise ProfileError(f"canonical {scope} ledger must be ledger.{scope}.json beside the manifest")

    ledger_key = f"{stage}_ledger_path"
    ledger = Path(profile[ledger_key]).resolve()
    if not ledger.exists():
        raise ProfileError(
            f"Canonical {stage} ledger not found: {ledger}. "
            "Live dispatch requires existing ledgers with prior history; "
            "no fresh allowance at arbitrary paths.")
    other_stage = "final" if stage == "dev" else "dev"
    other_ledger = Path(profile[f"{other_stage}_ledger_path"]).resolve()
    if not other_ledger.exists():
        raise ProfileError(
            f"Canonical {other_stage} ledger also required but not found: {other_ledger}")

    # Reuse the existing budget-module validator for BOTH ledgers
    from eval.optimization.budget import AuthorizationManifest as _AM
    from eval.optimization.budget import _validate_state as _vs
    try:
        budget_manifest = _AM.load(manifest)
    except Exception as e:
        raise ProfileError(f"Cannot load manifest for ledger validation: {e}") from e
    for ledger_path, ledger_stage in [(ledger, stage), (other_ledger, other_stage)]:
        try:
            state = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise ProfileError(f"Ledger unreadable {ledger_path}: {e}") from e
        try:
            _vs(state, budget_manifest, ledger_stage, simulated=False)
        except Exception as e:
            raise ProfileError(f"Ledger validation failed for {ledger_path}: {e}") from e

    denylist = Path(profile["redaction_names_path"]).resolve()
    if not denylist.exists():
        raise ProfileError(f"Denylist not found: {denylist}")

    # Path identity check: manifest and ledgers must be in the same directory
    if manifest.parent != ledger.parent:
        raise ProfileError(
            f"Manifest ({manifest.parent}) and {stage} ledger ({ledger.parent}) "
            "are in different directories — canonical binding requires same directory")

    return {
        "manifest_path": manifest,
        "ledger_path": ledger,
        "redaction_names_path": denylist,
    }
