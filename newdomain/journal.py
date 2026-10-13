"""Durable pre-dispatch journal for safe resume of paid experiments.

Design:
  - Exclusive process-level lock (fcntl) acquired BEFORE loading journal state,
    held for the entire runner execution (context manager).
  - In-process threading lock guards journal state and file appends.
  - Keys use FULL prompt SHA-256 + model identity (no truncation).
  - Strict state machine: new → started → terminal. Any deviation is corruption.
  - record_started rejects if entry already exists (any state).
  - record_terminal rejects if no prior started entry.
  - _load rejects terminal-without-started and started-after-terminal.
  - All public methods require the process lock to be held.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class JournalError(RuntimeError):
    """Raised on journal corruption, concurrent access, or unsafe resume."""


class DispatchJournal:
    """Durable journal keyed by (qid, arm, full_prompt_sha256, model)."""

    def __init__(self, journal_path: Path):
        self.path = Path(journal_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_path = self.path.with_suffix(".lock")
        self._entries: Dict[str, Dict] = {}
        self._thread_lock = threading.Lock()
        self._lock_fd = None

    def __enter__(self) -> "DispatchJournal":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def _require_lock(self):
        if self._lock_fd is None:
            raise JournalError(
                "journal operation requires the process lock to be held; "
                "use 'with DispatchJournal(path) as j:' or call j.acquire() first")

    def acquire(self):
        if self._lock_fd is not None:
            return
        self._lock_fd = open(self._lock_path, "a+", encoding="utf-8")
        try:
            fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_fd.close()
            self._lock_fd = None
            raise JournalError(
                f"Another process holds the journal lock: {self._lock_path}. "
                "Concurrent paid runs are forbidden.")
        try:
            self._load()
        except BaseException:
            self.release()
            raise

    def release(self):
        if self._lock_fd is not None:
            fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_UN)
            self._lock_fd.close()
            self._lock_fd = None

    def _load(self):
        self._entries.clear()
        if not self.path.exists():
            return
        started_keys = set()  # keys that have seen a 'started' in the file
        with open(self.path, encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    raise JournalError(
                        f"journal line {line_no} corrupt: {e}; fail-closed") from e
                if not isinstance(entry, dict):
                    raise JournalError(f"journal line {line_no} must be an object")
                key = entry.get("key")
                if not isinstance(key, str) or len(key.split("|")) != 4:
                    raise JournalError(f"journal line {line_no} missing key")
                qid, arm, digest, model = key.split("|")
                self.make_key(qid, arm, digest, model)
                status = entry.get("status")
                if status not in ("started", "terminal"):
                    raise JournalError(
                        f"journal line {line_no} unknown status: {status}")
                prev = self._entries.get(key)
                if status == "started":
                    if key in started_keys:
                        raise JournalError(
                            f"journal line {line_no}: duplicate started for {key}; "
                            "prior crash mid-dispatch; fail-closed")
                    started_keys.add(key)
                    self._entries[key] = entry
                elif status == "terminal":
                    if key not in started_keys:
                        raise JournalError(
                            f"journal line {line_no}: terminal without prior started "
                            f"for {key}; journal corruption; fail-closed")
                    if type(entry.get("success")) is not bool:
                        raise JournalError(f"journal line {line_no}: invalid success flag")
                    if prev and prev.get("status") == "terminal":
                        raise JournalError(f"journal line {line_no}: duplicate terminal for {key}")
                    self._entries[key] = entry

    @staticmethod
    def make_key(qid: str, arm: str, prompt_sha256: str, model: str) -> str:
        if any(not isinstance(v, str) or not v or "|" in v
               for v in (qid, arm, prompt_sha256, model)):
            raise JournalError("journal identities must be nonempty strings without pipes")
        if len(prompt_sha256) != 64 or any(c not in "0123456789abcdef" for c in prompt_sha256):
            raise JournalError("prompt identity must be a full lowercase SHA-256")
        return f"{qid}|{arm}|{prompt_sha256}|{model}"

    def check_resume(self, qid: str, arm: str, prompt_sha256: str, model: str) -> Optional[str]:
        """Returns 'skip' if succeeded, 'fail' if failed, None if new.
        Rejects changed identity for ANY prior state. In-flight → error."""
        self._require_lock()
        with self._thread_lock:
            for k in self._entries:
                parts = k.split("|", 3)
                if len(parts) == 4 and parts[0] == qid and parts[1] == arm:
                    if parts[2] != prompt_sha256 or parts[3] != model:
                        raise JournalError(
                            f"prior entry for ({qid}, {arm}) used different "
                            f"prompt/model identity; refusing changed input")
            key = self.make_key(qid, arm, prompt_sha256, model)
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry["status"] == "terminal":
                return "skip" if entry.get("success") else "fail"
            raise JournalError(
                f"in-flight entry for ({qid}, {arm}): previous dispatch may "
                "not have completed; fail-closed — manual investigation required")

    def record_started(self, qid: str, arm: str, prompt_sha256: str, model: str):
        self._require_lock()
        with self._thread_lock:
            key = self.make_key(qid, arm, prompt_sha256, model)
            if key in self._entries:
                raise JournalError(
                    f"record_started: entry already exists for {key} "
                    f"(status={self._entries[key]['status']}); "
                    "duplicate started is corruption")
            entry = {"key": key, "status": "started", "timestamp": time.time()}
            self._append(entry)
            self._entries[key] = entry

    def record_terminal(self, qid: str, arm: str, prompt_sha256: str, model: str,
                         success: bool, error: str = None, result_sha256: str = None):
        self._require_lock()
        with self._thread_lock:
            key = self.make_key(qid, arm, prompt_sha256, model)
            prev = self._entries.get(key)
            if prev is None or prev.get("status") != "started":
                raise JournalError(
                    f"record_terminal: no started entry for {key}; "
                    "terminal without started is corruption")
            entry = {"key": key, "status": "terminal", "success": success,
                      "timestamp": time.time()}
            if error:
                entry["error"] = error
            if result_sha256 and success:
                entry["result_sha256"] = result_sha256
            self._append(entry)
            self._entries[key] = entry

    def _append(self, entry: Dict):
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def summary(self) -> Dict:
        self._require_lock()
        with self._thread_lock:
            started = sum(1 for e in self._entries.values() if e.get("status") == "started")
            terminal_ok = sum(1 for e in self._entries.values()
                               if e.get("status") == "terminal" and e.get("success"))
            terminal_fail = sum(1 for e in self._entries.values()
                                  if e.get("status") == "terminal" and not e.get("success"))
            return {"total_entries": len(self._entries), "in_flight": started,
                    "succeeded": terminal_ok, "failed": terminal_fail}
