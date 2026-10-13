"""Exercise real runner entrypoints using synthetic inputs and no network."""
import contextlib
import hashlib
import io
import json
import socket
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test_newdomain import _write_synth_corpus, _resp
from newdomain.generation import run_live_v2, run_cycle2
from newdomain.judge import judge_live_v2, judge_cycle2
from newdomain.journal import DispatchJournal


class RunnerRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.corpus = _write_synth_corpus(self.root)
        self.questions = self.root / "questions.json"
        self.questions.write_text(json.dumps([{"qid": "Q1", "question": "补贴比例是多少？",
            "provided_reference": "最高不超过50%", "fixed_context": {"X:1": "补贴比例最高不超过50%。"}}]))
        self.deny = self.root / "deny.json"
        self.deny.write_text("[]")
        self.ctx = SimpleNamespace(ledger=SimpleNamespace(snapshot=lambda: {"totals": {}}))
        self.net = patch.object(socket.socket, "connect", side_effect=AssertionError("no network"))
        self.net.start()
        self.addCleanup(self.net.stop)

    def variants(self):
        for arm in ("B0", "C1", "C3B", "C2P", "C2R"):
            runner = run_live_v2 if arm in ("B0", "C1", "C3B") else run_cycle2
            content = {"sentences": [{"text": "补贴比例最高不超过50%。",
                **({"citations": [{"id": "X:1", "quote": "补贴比例最高不超过50%。"}]} if arm == "B0" else {"evidence": ["E1S1" if arm in ("C1", "C3B") else "E1"]})}]}
            if arm == "B0":
                content["handoff"] = False
            yield arm, runner, dict(stage="dev", arms=[arm], revision="test"), _resp(json.dumps(content)), "dev-test-results.jsonl", "dev-test-journal.jsonl"
        source = self.root / "source.jsonl"
        source.write_text(json.dumps({"qid": "Q1", "arm": "C1", "valid": True, "complete": True,
            "answer": {"sentences": [{"text": "补贴比例最高不超过50%。", "citations": [{"id": "X:1", "quote": "补贴比例最高不超过50%。"}]}]},
            "context": {"X:1": "补贴比例最高不超过50%。"}, "retrieval": {"results": []}}) + "\n")
        scores = dict(correctness=2, support=2, relevance=2, completeness=2,
                      citation_entailment=True, reference_complete=True, issue="")
        for name, runner in (("judge-v2", judge_live_v2), ("judge-c2", judge_cycle2)):
            args = dict(stage="dev", files=[source], name="test", dataset="synthetic")
            if runner is judge_cycle2:
                args["redaction_names_path"] = self.deny
            yield name, runner, args, _resp(json.dumps({"A": scores})), "dev-test-judge.jsonl", "dev-test-judge-journal.jsonl"

    def exercise(self, mutation=None):
        for name, runner, kwargs, response, filename, journalname in self.variants():
            with self.subTest(runner=name):
                outdir = self.root / name
                outdir.mkdir()
                kwargs.update(output_dir=outdir, corpus_path=self.corpus,
                              casefile=self.questions, live_context=self.ctx)
                with patch("newdomain.transport.chat", return_value=response) as call, contextlib.redirect_stdout(io.StringIO()):
                    runner(**kwargs)
                    self.assertEqual(call.call_count, 1)
                    result = outdir / filename
                    saved = result.read_bytes()
                    self.assertTrue(json.loads(saved).get("valid", True))
                    if mutation:
                        mutation(result, outdir / journalname, name)
                        with self.assertRaises((RuntimeError, ValueError)):
                            runner(**kwargs, resume=True)
                    else:
                        runner(**kwargs, resume=True)
                        self.assertEqual(saved, result.read_bytes())
                    self.assertEqual(call.call_count, 1)
                # The run lock must be released even when preflight fails.
                with DispatchJournal(outdir / journalname):
                    pass

    def test_completed_resume_calls_nothing_and_preserves_results(self):
        self.exercise()

    def test_tampered_results_block_all_runners(self):
        self.exercise(lambda result, journal, name: result.write_text("{}\n"))

    def test_missing_result_hash_blocks_all_runners(self):
        def mutate(result, journal, name):
            rows = [json.loads(line) for line in journal.read_text().splitlines()]
            rows[-1].pop("result_sha256")
            journal.write_text("".join(json.dumps(row) + "\n" for row in rows))
        self.exercise(mutate)

    def test_unresolved_job_blocks_all_dispatch(self):
        def mutate(result, journal, name):
            # An unresolved older job must be checked before *any* worker starts.
            with journal.open("a") as fh:
                fh.write(json.dumps({"key": "orphan|C1|" + "a" * 64 + "|deepseek-flash", "status": "started"}) + "\n")
        self.exercise(mutate)

    def test_duplicate_questions_rejected_before_dispatch(self):
        rows = json.loads(self.questions.read_text())
        self.questions.write_text(json.dumps(rows * 2))
        with patch("newdomain.transport.chat") as call:
            with self.assertRaises(ValueError):
                run_live_v2("dev", ["C1"], "dup", output_dir=self.root,
                    corpus_path=self.corpus, casefile=self.questions, live_context=self.ctx)
            call.assert_not_called()

    def test_corrupt_journal_releases_process_lock(self):
        path = self.root / "journal.jsonl"
        path.write_text("{}\n")
        first = DispatchJournal(path)
        with self.assertRaises(RuntimeError):
            first.acquire()
        self.assertIsNone(first._lock_fd)
        path.unlink()
        with DispatchJournal(path):
            pass

    def test_model_mismatch_blocks_all_dispatch(self):
        def mutate(result, journal, name):
            rows = [json.loads(line) for line in journal.read_text().splitlines()]
            for row in rows:
                row["key"] = row["key"].rsplit("|", 1)[0] + "|wrong-model"
            journal.write_text("".join(json.dumps(row) + "\n" for row in rows))
        self.exercise(mutate)

    def test_direct_runner_private_output_boundary(self):
        root = Path(__file__).resolve().parents[1]
        with patch("newdomain.transport.chat") as call:
            with self.assertRaises(RuntimeError):
                run_live_v2("dev", ["C1"], "boundary", output_dir=root / "forbidden-private-output",
                    corpus_path=self.corpus, casefile=self.questions, live_context=self.ctx)
            call.assert_not_called()
        self.assertFalse((root / "forbidden-private-output").exists())
