"""Configurable data paths for the new-domain evaluation pipeline.

All private data (corpus, questions, results, ledgers) lives OUTSIDE the Git
repository. There are NO hardcoded defaults to historical task folders — every
data path must be provided explicitly via environment variable or CLI argument.
Imports, help text and synthetic-only tests work without any data present; a
clear error is raised only when a data path is actually used.

Environment variables (all optional; read lazily on first use):
  NEWDOMAIN_CORPUS      — screened corpus JSONL (e.g. documents-ocr-v2.jsonl)
  NEWDOMAIN_QUESTIONS   — question pool JSON (e.g. development.json)
  NEWDOMAIN_RESULTS_DIR — where run results are written/read

Safety invariants:
  - No path default points into any historical task folder or the repo itself.
  - All resolved private paths must be OUTSIDE the resolved repo root
    (symlink-checked). A path inside the repo raises immediately.
  - Paid dispatch is disabled by guard flags in the transport/generation/judge
    modules themselves; the auth manifest's state is not modified here.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class MissingDataPath(RuntimeError):
    """Raised when a data path is needed but not configured."""


def _resolve_repo_root() -> Path:
    """Symlink-resolved repo root for boundary checks."""
    return REPO_ROOT.resolve()


def _ensure_outside_repo(path: Path, what: str) -> Path:
    """Reject any private data path that resolves inside the repo."""
    resolved = path.resolve()
    repo = _resolve_repo_root()
    if resolved == repo or repo in resolved.parents:
        raise RuntimeError(
            f"{what} path {path} resolves inside the repo root {repo}; "
            "private data must stay outside tracked source")
    return resolved


def _required_env(name: str, what: str) -> Path:
    env = os.environ.get(name, "").strip()
    if not env:
        raise MissingDataPath(
            f"{what} not configured. Set ${name}=/path/to/data or pass "
            f"the equivalent CLI flag. No hardcoded defaults are provided.")
    return Path(env)


def _ensure_parent_for_output(path: Path, what: str) -> Path:
    """For output paths: verify the parent directory exists and is outside the
    repo BEFORE creating anything, so we never accidentally write into frozen
    folders or the repository itself."""
    resolved = _ensure_outside_repo(path, what)
    parent = resolved.parent
    if not parent.exists():
        raise RuntimeError(
            f"{what} parent directory {parent} does not exist; "
            "create it explicitly — no implicit directory creation")
    return resolved


class _PathConfig:
    """Lazy path resolution — evaluates on attribute access so imports and
    help text work without any data present. Every accessor either returns
    a validated external path or raises MissingDataPath."""

    @property
    def repo_root(self) -> Path:
        return _resolve_repo_root()

    @property
    def corpus(self) -> Path:
        p = _required_env("NEWDOMAIN_CORPUS", "Screened corpus JSONL")
        if not p.exists():
            raise FileNotFoundError(f"Corpus file not found: {p}")
        return _ensure_outside_repo(p, "Corpus")

    @property
    def questions_dev(self) -> Path:
        p = _required_env("NEWDOMAIN_QUESTIONS", "Development question pool")
        if not p.exists():
            raise FileNotFoundError(f"Question file not found: {p}")
        return _ensure_outside_repo(p, "Questions")

    @property
    def results_dir(self) -> Path:
        p = _required_env("NEWDOMAIN_RESULTS_DIR", "Results directory")
        if not p.exists():
            raise FileNotFoundError(f"Results directory not found: {p}")
        return _ensure_outside_repo(p, "Results directory")

    @property
    def budget_manifest(self) -> Path:
        """Repository auth manifest — always repo-internal (it is tracked
        configuration, not private data). Paid dispatch is disabled in the
        migrated transport wrappers themselves, not by editing this file."""
        return REPO_ROOT / "eval" / "optimization" / "data" / "auth.manifest.json"


PATHS = _PathConfig()
