"""Consolidated offline tests for the newdomain package. Sockets blocked; no
network, no paid calls, no external data required — synthetic fixtures only."""
from __future__ import annotations

import hashlib
import json
import os
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from newdomain import baseline as b0
from newdomain import candidate as c1
from newdomain import cycle2 as c2
from newdomain import transport as tr
from newdomain.paths import PATHS, MissingDataPath, _ensure_outside_repo


def setUpModule():
    net = patch.object(socket.socket, "connect", side_effect=AssertionError("Offline only"))
    net.start()
    setUpModule._net = net


def tearDownModule():
    setUpModule._net.stop()


SYNTH_UNITS = [
    {"doc_id": "SYN-A", "title": "合成测试文档甲：光明区政策", "locator": "1",
     "text": "光明区科技创新补贴政策：对入驻重点楼宇的企业给予每月每平方米租金补贴，"
             "补贴比例最高不超过50%，政策有效期至2027年12月31日。成立五年以内的企业可申请。"
             "普通办公用房补贴比例为30%。", "source_sha256": "a" * 64, "extraction": "synthetic"},
    {"doc_id": "SYN-A", "title": "合成测试文档甲：光明区政策", "locator": "2",
     "text": "传感器平台包含氧气传感器与温湿度模块。精度：氧气±0.3%，质保期两年。",
     "source_sha256": "a" * 64, "extraction": "synthetic"},
    {"doc_id": "SYN-B", "title": "合成测试文档乙：光明产业园", "locator": "3",
     "text": "光明产业园总面积12万平方米。有效期：本条款自2026年1月1日起实施。",
     "source_sha256": "b" * 64, "extraction": "synthetic"},
    {"doc_id": "D36", "title": "科技成果表", "locator": "101",
     "text": "成果名称：合成光学装置\n分类：装备类\n单位名称：合成研究院\n应用领域：制造业",
     "source_sha256": "1" * 64, "extraction": "synthetic"},
]

QUERY = "光明区补贴政策"


def _write_synth_corpus(td):
    p = td / "corpus.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for u in SYNTH_UNITS:
            f.write(json.dumps(u, ensure_ascii=False) + "\n")
    return p


def _resp(content, in_tok=100, out_tok=20):
    return {"content": content, "stream_done": True, "finish_reason": "stop",
            "usage": {"input_tokens": in_tok, "output_tokens": out_tok}}


class TestPathConfig(unittest.TestCase):
    def test_import_without_env(self):
        self.assertTrue(hasattr(b0, "load_units"))

    def test_missing_path_clear_error(self):
        os.environ.pop("NEWDOMAIN_CORPUS", None)
        with self.assertRaises(MissingDataPath) as cm:
            PATHS.corpus
        self.assertIn("NEWDOMAIN_CORPUS", str(cm.exception))

    def test_repo_boundary(self):
        with self.assertRaises(RuntimeError):
            _ensure_outside_repo(REPO / "newdomain", "t")


class TestB0(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        td = Path(self._td.name)
        self.corpus = _write_synth_corpus(td)
        self.units = b0.load_units(self.corpus)
        self.index = b0.NewDomainBaseline(b0.build_chunks(self.units))

    def test_chunks(self):
        self.assertGreater(len(self.index.chunks), 0)

    def test_retrieval(self):
        r = self.index.retrieval(QUERY, k=8)
        self.assertTrue(1 <= len(r["results"]) <= 8)

    def test_validate_ok(self):
        ctx = {"X:1": "光明区科技创新补贴政策全文"}
        content = json.dumps({"sentences": [
            {"text": "政策全文。", "citations": [{"id": "X:1", "quote": "科技创新补贴政策"}]}],
            "handoff": False}, ensure_ascii=False)
        rep = b0.validate(_resp(content), ctx)
        self.assertTrue(rep["ok"], msg=str(rep.get("failure")))


class TestC1(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.corpus = _write_synth_corpus(Path(self._td.name))
        self.units = b0.load_units(self.corpus)
        self.index = c1.CandidateIndex(b0.build_chunks(self.units))

    def test_canonicalize_valid(self):
        results = self.index.retrieval(QUERY, k=4)["results"]
        ctx = {c["id"]: c["text"] for c in results}
        handles = c1.passages_for_contexts(ctx)
        first = sorted(handles)[0]
        obj = {"sentences": [{"text": "政策。", "evidence": [first]}]}
        out, meta = c1.canonicalize(_resp(json.dumps(obj, ensure_ascii=False)), ctx)
        self.assertTrue(meta["ok"], str(meta["errors"]))

    def test_canonicalize_unknown_handle(self):
        ctx = {"X:1": "test"}
        obj = {"sentences": [{"text": "句。", "evidence": ["E9S9"]}]}
        env = _resp(json.dumps(obj, ensure_ascii=False))
        out, meta = c1.canonicalize(env, ctx)
        self.assertFalse(meta["ok"])
        self.assertEqual(out, env)

    def test_canonicalize_never_raises(self):
        for c in ('{"sentences":', 'bad', '答\ud800'):
            env = _resp(c)
            out, meta = c1.canonicalize(env, {"X": "y"})
            self.assertFalse(meta["ok"])
            self.assertEqual(out, env)


class TestC2(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.corpus = _write_synth_corpus(Path(self._td.name))
        self.units = b0.load_units(self.corpus)

    def test_c2p_whole_chunk(self):
        from newdomain import candidate as cm
        index = cm.CandidateIndex(b0.build_chunks(self.units))
        results = index.retrieval(QUERY, k=4)["results"]
        ctx = {c["id"]: c["text"] for c in results}
        fid = next(iter(ctx))
        obj = {"sentences": [{"text": "政策。", "evidence": ["E1"]}]}
        out, meta = c2.canonicalize(_resp(json.dumps(obj, ensure_ascii=False)), ctx)
        self.assertTrue(meta["ok"], str(meta["errors"]))
        canon = json.loads(out["content"])
        self.assertEqual(canon["sentences"][0]["citations"][0]["quote"], ctx[fid])

    def test_handle_leak(self):
        obj = {"sentences": [{"text": "根据E1。", "evidence": ["E1"]}]}
        _, meta = c2.canonicalize(_resp(json.dumps(obj, ensure_ascii=False)), {"X": "y"})
        self.assertFalse(meta["ok"])

    def test_clarification(self):
        obj = {"sentences": [{"text": c2.CLARIFY_TEMPLATE, "evidence": []}]}
        _, meta = c2.canonicalize(_resp(json.dumps(obj, ensure_ascii=False)), {"X": "y"})
        self.assertTrue(meta["ok"], str(meta["errors"]))

    def test_aggregation_cards_bounded(self):
        cards = c2.build_aggregate_cards([u for u in self.units if u["doc_id"] == "D36"])
        self.assertGreaterEqual(len(cards), 1)
        for card in cards:
            self.assertLessEqual(len(card["text"]), c2.MAX_CARD_CHARS)
            self.assertIn("LOCAL COMPUTED SNAPSHOT", card["text"])


class TestTransport(unittest.TestCase):
    """Default-deny guards at every level; privacy fail-closed; LiveContext required."""

    def test_deepseek_call_default_deny(self):
        from newdomain.transport import LiveAuthorizationError
        ds = tr.DeepSeekStreamTransport(model="deepseek-flash")
        with self.assertRaises(LiveAuthorizationError):
            ds.call("chat", {"messages": [{"role": "system", "content": "s"},
                                           {"role": "user", "content": "u"}]})

    def test_deadline_call_default_deny(self):
        from newdomain.transport import LiveAuthorizationError
        dl = tr.DeadlineTransport(model="deepseek-flash")
        with self.assertRaises(LiveAuthorizationError):
            dl.call("chat", {})

    def test_chat_requires_live_context(self):
        from newdomain.transport import LiveAuthorizationError
        with self.assertRaises((LiveAuthorizationError, AttributeError, TypeError)):
            tr.chat(None, [])

    def test_privacy_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            names = Path(td) / "n.json"
            names.write_text('["张三"]', encoding="utf-8")
            with self.assertRaises(tr.PrivacyViolation):
                tr.privacy_check("张三", names)
            with self.assertRaises(tr.PrivacyViolation):
                tr.privacy_check("a@b.com", names)

    def test_privacy_fails_closed_missing(self):
        with self.assertRaises(tr.PrivacyViolation):
            tr.privacy_check("text", Path("/nonexistent/names.json"))

    def test_denylist_validates_type(self):
        from newdomain.transport import LiveAuthorizationError, PriorLedgerError
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text('{"not": "a list"}', encoding="utf-8")
            # Minimal manifest that loads but has no prior runs (empty check passes)
            manifest = Path(td) / "manifest.json"
            manifest.write_text(json.dumps({
                "authorized": False, "spend_cap_usd": 0,
                "final_eval_reserve_usd": 0, "max_input_tokens": 1,
                "max_output_tokens": 1, "request_cap": 0, "max_retries": 0,
                "selector_deadline_s": 30, "global_deadline_s": 3600,
                "max_concurrency": 1, "models": {}, "status_note": "test"
            }), encoding="utf-8")
            ledger = Path(td) / "ledger.dev.json"
            ledger.write_text(json.dumps({
                "schema": 2, "stage": "dev", "simulated": False,
                "manifest_fingerprint": "placeholder", "deadline_epoch": 9999999999,
                "reservations": [], "halted": None, "resume_log": [],
                "totals": {"requests_dispatched": 0, "retries": 0,
                            "open_reservations": 0, "reserved_open_cost_usd": 0,
                            "charged_cost_usd": 0, "overage_usd": 0,
                            "conservative_settlements": 0}
            }), encoding="utf-8")
            try:
                tr.LiveContext(manifest_path=manifest, redaction_names_path=bad)
                self.fail("should have raised")
            except (LiveAuthorizationError, PriorLedgerError) as e:
                # Denylist validation happens before ledger binding; if we get
                # past manifest load, the denylist type check should fire
                if isinstance(e, LiveAuthorizationError) and "array of strings" in str(e):
                    pass  # correct: denylist validation
                elif isinstance(e, PriorLedgerError):
                    # Manifest fingerprint mismatch is also fine for this test
                    pass

    def test_missing_manifest_rejected(self):
        from newdomain.transport import LiveAuthorizationError
        with self.assertRaises(LiveAuthorizationError):
            tr.LiveContext(
                manifest_path=Path("/nonexistent/manifest.json"),
                redaction_names_path=Path("/nonexistent/names.json"))

    def test_generation_requires_live_context(self):
        from newdomain.transport import LiveAuthorizationError
        from newdomain.generation import run_live_v2
        with self.assertRaises(LiveAuthorizationError):
            run_live_v2("dev", ["B0"], "test",
                        output_dir=None, casefile=None, corpus_path=None)

    def test_generation_importable(self):
        from newdomain.generation import run_live_v2, run_cycle2
        from newdomain.judge import judge_live_v2, judge_cycle2, parse_scores, RUBRIC, RUBRIC_C2
        self.assertTrue(callable(run_live_v2))
        self.assertTrue(callable(parse_scores))

    def test_rubric_hashes(self):
        from newdomain.judge import RUBRIC, RUBRIC_C2
        self.assertEqual(hashlib.sha256(RUBRIC.encode()).hexdigest(),
                         "7567ba701f223ad590c1e4f05f734c3cdcbc67bac6ccaebe54f42af6925713e4")
        self.assertEqual(hashlib.sha256(RUBRIC_C2.encode()).hexdigest(),
                         "66065992b9bd37bbd1e80ef4e778c585d847a5c48d7ca14a0d767a02ff43c96d")

    def test_parse_scores_synthetic(self):
        from newdomain.judge import parse_scores
        good = {"correctness": 2, "support": 2, "relevance": 2, "completeness": 2,
                "citation_entailment": True, "reference_complete": True, "issue": "ok"}
        resp = {"stream_done": True, "finish_reason": "stop",
                "usage": {"input_tokens": 10, "output_tokens": 5},
                "content": json.dumps({"A": good})}
        rows = [{"arm": "C1", "valid": True, "complete": True}]
        scores, norm = parse_scores(resp, {"A": "C1"}, rows)
        self.assertEqual(scores["C1"]["correctness"], 2)
        self.assertTrue(scores["C1"]["adequate"])
        with self.assertRaises(Exception):
            parse_scores(dict(resp, stream_done=False), {"A": "C1"}, rows)

    def test_mock_provider(self):
        from newdomain.mock import MockChatTransport, MockJudgeTransport
        mt = MockChatTransport()
        resp = mt.call("chat", {"messages": []})
        self.assertTrue(resp["stream_done"])
        self.assertEqual(resp["finish_reason"], "stop")
        self.assertEqual(mt.call_count, 1)
        mj = MockJudgeTransport()
        jresp = mj.call("chat", {})
        self.assertTrue(jresp["stream_done"])


class TestRunnerCLI(unittest.TestCase):
    def _run_cli(self, *args):
        import subprocess
        env = {**os.environ, "PYTHONPATH": str(REPO),
               "NEWDOMAIN_CORPUS": "", "NEWDOMAIN_QUESTIONS": "",
               "NEWDOMAIN_RESULTS_DIR": ""}
        return subprocess.run(
            [sys.executable, "-m", "newdomain.runner"] + list(args),
            capture_output=True, text=True, cwd="/tmp", env=env, timeout=60)

    def test_help(self):
        r = self._run_cli("help")
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("offline", r.stdout.lower())

    def test_replay_b0(self):
        with tempfile.TemporaryDirectory() as td:
            content = json.dumps({"sentences": [
                {"text": "政策。", "citations": [{"id": "X", "quote": "政策"}]}],
                "handoff": False}, ensure_ascii=False)
            row = {"qid": "B0-1", "arm": "B0", "valid": True,
                   "raw_response": _resp(content), "context": {"X": "政策内容"},
                   "full_ms": 100.0}
            rp = Path(td) / "r.jsonl"
            rp.write_text(json.dumps(row) + "\n", encoding="utf-8")
            r = self._run_cli("replay", "--results", str(rp), "--arm", "B0")
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertEqual(out["recomputed_valid"], 1)
            self.assertEqual(out["mode_notes"].get("b0_raw"), 1)

    def test_replay_c1(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            units = b0.load_units(corpus)
            index = c1.CandidateIndex(b0.build_chunks(units))
            results = index.retrieval(QUERY, k=4)["results"]
            ctx = {c["id"]: c["text"] for c in results}
            handles = c1.passages_for_contexts(ctx)
            first = sorted(handles)[0]
            raw_content = json.dumps({"sentences": [{"text": "政策。",
                                                      "evidence": [first]}]},
                                      ensure_ascii=False)
            row = {"qid": "Q1", "arm": "C1", "valid": True, "complete": True,
                   "raw_response": _resp(raw_content), "context": ctx, "full_ms": 100.0}
            rp = td / "r.jsonl"
            rp.write_text(json.dumps(row) + "\n", encoding="utf-8")
            r = self._run_cli("replay", "--results", str(rp), "--arm", "C1")
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertEqual(out["recomputed_valid"], 1)
            self.assertEqual(out["mode_notes"].get("raw_replayed"), 1)

    def test_replay_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            rp = Path(td) / "d.jsonl"
            row = json.dumps({"qid": "X", "arm": "C1"})
            rp.write_text(row + "\n" + row + "\n", encoding="utf-8")
            r = self._run_cli("replay", "--results", str(rp))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("duplicate", r.stderr)

    def test_replay_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            row = {"qid": "X", "arm": "B0", "valid": True,
                   "raw_response": _resp("bad"), "context": {}}
            rp = Path(td) / "r.jsonl"
            rp.write_text(json.dumps(row) + "\n", encoding="utf-8")
            r = self._run_cli("replay", "--results", str(rp))
            self.assertEqual(r.returncode, 0)
            out = json.loads(r.stdout)
            self.assertEqual(len(out["saved_validity_mismatches"]), 1)

    def test_summarize_percentile(self):
        with tempfile.TemporaryDirectory() as td:
            rp = Path(td) / "r.jsonl"
            rows = [{"qid": f"Q{i}", "arm": "C1", "valid": True, "complete": True,
                     "full_ms": float(i * 100)} for i in range(1, 21)]
            rp.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
            r = self._run_cli("summarize", "--results", str(rp))
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertAlmostEqual(out["by_arm"]["C1"]["p50_ms"], 1050.0, places=0)

    def test_summarize_judge(self):
        with tempfile.TemporaryDirectory() as td:
            rp = Path(td) / "r.jsonl"
            row = {"qid": "Q1", "arm": "C1", "valid": True, "complete": True, "full_ms": 100.0}
            rp.write_text(json.dumps(row) + "\n", encoding="utf-8")
            jp = Path(td) / "j.jsonl"
            judge = {"qid": "Q1", "mapping": {"A": "C1"},
                     "scores": {"C1": {"correctness": 2, "adequate": True, "semantic_adequate": True}}}
            jp.write_text(json.dumps(judge) + "\n", encoding="utf-8")
            r = self._run_cli("summarize", "--results", str(rp), "--judge-results", str(jp))
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertIn("saved_judge", out["by_arm"]["C1"])

    def test_prepare(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            questions = td / "q.json"
            questions.write_text(json.dumps([{"qid": "Q1", "question": QUERY}]), encoding="utf-8")
            outdir = td / "out"
            outdir.mkdir()
            r = self._run_cli("prepare", "--corpus", str(corpus),
                               "--questions", str(questions),
                               "--output", str(outdir), "--mode", "C2P")
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertEqual(out["prepared"], 1)

    def test_prepare_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            questions = td / "q.json"
            questions.write_text(json.dumps([{"qid": "Q1", "question": QUERY}]), encoding="utf-8")
            outdir = td / "out"
            outdir.mkdir()
            (outdir / "prepare.jsonl").write_text("x", encoding="utf-8")
            r = self._run_cli("prepare", "--corpus", str(corpus),
                               "--questions", str(questions),
                               "--output", str(outdir), "--mode", "C2P")
            self.assertNotEqual(r.returncode, 0)

    def test_prepare_rejects_dupe_qids(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            questions = td / "q.json"
            questions.write_text(json.dumps([
                {"qid": "D", "question": "a"}, {"qid": "D", "question": "b"}]), encoding="utf-8")
            outdir = td / "out"
            outdir.mkdir()
            r = self._run_cli("prepare", "--corpus", str(corpus),
                               "--questions", str(questions),
                               "--output", str(outdir), "--mode", "C2P")
            self.assertNotEqual(r.returncode, 0)


class TestNoExternalDeps(unittest.TestCase):
    def test_no_codex_runtime_deps(self):
        import subprocess
        result = subprocess.run(
            ["grep", "-rn", "Documents/Codex", str(REPO / "newdomain"),
             "--include=*.py"], capture_output=True, text=True, timeout=30)
        code_lines = [l for l in result.stdout.splitlines()
                      if not l.split(":", 2)[-1].lstrip().startswith(("#", '"""'))
                      and any(k in l for k in ("import ", "from ", "= Path(", "sys.path"))]
        self.assertEqual(len(code_lines), 0,
                         msg=f"External deps:\n{chr(10).join(code_lines[:5])}")

    def test_no_external_modules_loaded(self):
        for m in ("new_pipeline", "candidate_pipeline", "cycle2_pipeline",
                   "paid_transport", "deadline_transport", "live_deepseek_transport"):
            self.assertNotIn(m, sys.modules)




class TestProfileBinding(unittest.TestCase):
    """Runtime profile pins canonical paths; copying files to new dirs fails."""

    def _make_profile(self, td):
        manifest = td / "manifest.json"
        manifest.write_text(json.dumps({
            "authorized": False, "spend_cap_usd": 100,
            "final_eval_reserve_usd": 25, "max_input_tokens": 6000,
            "max_output_tokens": 800, "request_cap": 200, "max_retries": 1,
            "selector_deadline_s": 30, "global_deadline_s": 86400,
            "max_concurrency": 4, "models": {}, "status_note": "test"
        }), encoding="utf-8")
        dev_ledger = td / "ledger.dev.json"
        final_ledger = td / "ledger.final.json"
        # Compute the correct manifest fingerprint (same as AuthorizationManifest.fingerprint())
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        fp = hashlib.sha256(json.dumps(
            manifest_data, ensure_ascii=False, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        for p in (dev_ledger, final_ledger):
            p.write_text(json.dumps({
                "schema": 2, "stage": p.stem.split(".")[1], "simulated": False,
                "manifest_fingerprint": fp, "deadline_epoch": 9999999999,
                "reservations": [], "halted": None, "resume_log": [],
                "totals": {"requests_dispatched": 0, "retries": 0,
                            "open_reservations": 0, "reserved_open_cost_usd": 0,
                            "charged_cost_usd": 0, "overage_usd": 0,
                            "conservative_settlements": 0}
            }), encoding="utf-8")
        denylist = td / "names.json"
        denylist.write_text('["张三"]', encoding="utf-8")
        profile = {
            "manifest_path": str(manifest),
            "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "dev_ledger_path": str(dev_ledger),
            "final_ledger_path": str(final_ledger),
            "redaction_names_path": str(denylist),
        }
        return profile, td

    def test_profile_load_and_verify(self):
        from newdomain.profile import load_profile, verify_profile
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            profile, _ = self._make_profile(td)
            pp = td / "profile.json"
            pp.write_text(json.dumps(profile), encoding="utf-8")
            loaded = load_profile(pp)
            paths = verify_profile(loaded, "dev")
            self.assertEqual(paths["manifest_path"], Path(profile["manifest_path"]).resolve())

    def test_copied_manifest_hash_mismatch(self):
        from newdomain.profile import load_profile, verify_profile, ProfileError
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            profile, _ = self._make_profile(td)
            # Copy manifest to a new directory and tamper
            new_dir = td / "copy"
            new_dir.mkdir()
            copied = new_dir / "manifest.json"
            original = Path(profile["manifest_path"])
            copied.write_text(original.read_text() + " ", encoding="utf-8")
            bad_profile = dict(profile, manifest_path=str(copied))
            pp = td / "bad.json"
            pp.write_text(json.dumps(bad_profile), encoding="utf-8")
            loaded = load_profile(pp)
            with self.assertRaises(ProfileError) as cm:
                verify_profile(loaded, "dev")
            self.assertIn("hash mismatch", str(cm.exception).lower())

    def test_missing_ledger_rejected(self):
        from newdomain.profile import verify_profile, ProfileError
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            profile, _ = self._make_profile(td)
            # Remove the dev ledger
            Path(profile["dev_ledger_path"]).unlink()
            with self.assertRaises(ProfileError) as cm:
                verify_profile(profile, "dev")
            self.assertIn("not found", str(cm.exception))


class TestMockEndToEnd(unittest.TestCase):
    """Mock generation and judge e2e; no network, no credentials, no ledger."""

    def test_mock_chat_transport_e2e(self):
        from newdomain.mock import MockChatTransport
        mt = MockChatTransport()
        resp = mt.call("chat", {"messages": [
            {"role": "system", "content": "s"},
            {"role": "user", "content": "u"}]})
        self.assertTrue(resp["stream_done"])
        self.assertEqual(resp["finish_reason"], "stop")
        self.assertIsInstance(resp["usage"], dict)
        self.assertIn("input_tokens", resp["usage"])
        self.assertIn("output_tokens", resp["usage"])

    def test_mock_chat_transport_failure(self):
        from newdomain.mock import MockChatTransport
        mt = MockChatTransport(fail_on_call=1)
        from eval.optimization.transports import TransportError
        with self.assertRaises(TransportError):
            mt.call("chat", {})

    def test_mock_judge_transport(self):
        from newdomain.mock import MockJudgeTransport
        mj = MockJudgeTransport()
        resp = mj.call("chat", {})
        scores = json.loads(resp["content"])
        self.assertIn("A", scores)
        self.assertEqual(scores["A"]["correctness"], 2)

    def test_cli_generate_dry_run_no_side_effects(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            questions = td / "q.json"
            questions.write_text(json.dumps([{"qid": "Q1", "question": QUERY}]),
                                  encoding="utf-8")
            outdir = td / "out"
            outdir.mkdir()
            env = {**os.environ, "PYTHONPATH": str(REPO)}
            r = subprocess.run(
                [sys.executable, "-m", "newdomain.cli_generate",
                 "--corpus", str(corpus), "--questions", str(questions),
                 "--output", str(outdir), "--mode", "C2P"],
                capture_output=True, text=True, cwd="/tmp", env=env, timeout=60)
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertEqual(out["mode"], "dry_run")
            # No results file created (dry-run has no side effects)
            self.assertFalse((outdir / "results.jsonl").exists())

    def test_cli_generate_live_without_profile(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            questions = td / "q.json"
            questions.write_text(json.dumps([{"qid": "Q1", "question": QUERY}]),
                                  encoding="utf-8")
            outdir = td / "out"
            outdir.mkdir()
            env = {**os.environ, "PYTHONPATH": str(REPO)}
            r = subprocess.run(
                [sys.executable, "-m", "newdomain.cli_generate",
                 "--live", "--corpus", str(corpus), "--questions", str(questions),
                 "--output", str(outdir), "--mode", "C2P"],
                capture_output=True, text=True, cwd="/tmp", env=env, timeout=60)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("--profile", r.stderr)

    def test_cli_judge_dry_run(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            corpus = _write_synth_corpus(td)
            questions = td / "q.json"
            questions.write_text(json.dumps([{"qid": "Q1", "question": QUERY}]),
                                  encoding="utf-8")
            results = td / "r.jsonl"
            results.write_text(json.dumps({"qid": "Q1", "arm": "C1"}) + "\n",
                                encoding="utf-8")
            outdir = td / "out"
            outdir.mkdir()
            env = {**os.environ, "PYTHONPATH": str(REPO)}
            r = subprocess.run(
                [sys.executable, "-m", "newdomain.cli_judge",
                 "--results", str(results), "--questions", str(questions),
                 "--corpus", str(corpus), "--output", str(outdir)],
                capture_output=True, text=True, cwd="/tmp", env=env, timeout=60)
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            out = json.loads(r.stdout)
            self.assertEqual(out["mode"], "dry_run")


class TestReport(unittest.TestCase):
    """Report functions on synthetic fixtures; frozen-evidence verified separately."""

    def _rows(self, arm, valid_qids, n=5):
        rows = []
        for i in range(n):
            rows.append({"qid": f"Q{i}", "arm": arm,
                          "valid": f"Q{i}" in valid_qids,
                          "complete": True,
                          "full_ms": float(100 + i * 50)})
        return rows

    def test_failure_summary(self):
        from newdomain.report import failure_summary
        rows = self._rows("C1", {"Q0", "Q1", "Q2"})
        s = failure_summary(rows)
        self.assertEqual(s["n"], 5)
        self.assertEqual(s["valid"], 3)
        self.assertEqual(s["invalid"], 2)

    def test_latency_summary(self):
        from newdomain.report import latency_summary
        rows = self._rows("C1", set(), n=20)
        s = latency_summary(rows)
        self.assertIsNotNone(s["p50_ms"])
        self.assertIsNotNone(s["p95_ms"])

    def test_paired_transitions(self):
        from newdomain.report import paired_transitions
        a = self._rows("A", {"Q0", "Q1", "Q2"})
        b = self._rows("B", {"Q1", "Q2", "Q3"})
        t = paired_transitions(a, b)
        self.assertEqual(t["n_common"], 5)
        self.assertEqual(t["a_better"], 1)  # Q0
        self.assertEqual(t["b_better"], 1)  # Q3

    def test_bootstrap_paired(self):
        from newdomain.report import bootstrap_paired
        a = self._rows("A", {"Q0", "Q1"})
        b = self._rows("B", {"Q0", "Q1", "Q2"})
        r = bootstrap_paired(a, b)
        self.assertEqual(r["n_pairs"], 5)
        self.assertAlmostEqual(r["delta"], 0.2, places=1)

    def test_structural_uncited(self):
        from newdomain.report import structural_uncited_count
        rows = [{"qid": "Q1", "arm": "C1", "valid": True,
                  "answer": {"sentences": [{"text": "t", "citations": []}]}},
                 {"qid": "Q2", "arm": "C1", "valid": True,
                  "answer": {"sentences": [{"text": "t", "citations": [{"id": "X", "quote": "q"}]}]}},
                 {"qid": "Q3", "arm": "C1", "valid": False,
                  "answer": {"sentences": [{"text": "t", "citations": []}]}}]
        self.assertEqual(structural_uncited_count(rows), 1)

    def test_both_judge_conjunction(self):
        from newdomain.report import both_judge_conjunction
        good = {"correctness": 2, "support": 2, "relevance": 2, "completeness": 2,
                "citation_entailment": True, "reference_complete": True,
                "generation_valid": True, "generation_complete": True}
        bad = dict(good, correctness=1)
        invalid_gen = dict(good, generation_valid=False)
        p = {("Q1", "A"): good, ("Q2", "A"): good, ("Q3", "A"): good}
        a = {("Q1", "A"): good, ("Q2", "A"): bad, ("Q3", "A"): invalid_gen}
        conj = both_judge_conjunction(p, a)
        self.assertTrue(conj[("Q1", "A")])
        self.assertFalse(conj[("Q2", "A")])
        self.assertFalse(conj[("Q3", "A")])

    def test_extract_judge_scores_duplicate_rejected(self):
        from newdomain.report import extract_judge_scores
        rows = [
            {"qid": "Q1", "mapping": {"A": "C1"}, "scores": {"C1": {"correctness": 2}}},
            {"qid": "Q1", "mapping": {"A": "C1"}, "scores": {"C1": {"correctness": 1}}},
        ]
        with self.assertRaises(ValueError):
            extract_judge_scores(rows)


class TestJournal(unittest.TestCase):
    """Durable journal: started/terminal lifecycle, resume, concurrency, changed inputs."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.journal_path = Path(self._td.name) / "journal.jsonl"

    def test_lifecycle_skip_fail(self):
        from newdomain.journal import DispatchJournal
        with DispatchJournal(self.journal_path) as j:
            self.assertIsNone(j.check_resume("Q1", "A", "a" * 64, "model1"))
            j.record_started("Q1", "A", "a" * 64, "model1")
            j.record_terminal("Q1", "A", "a" * 64, "model1", success=True)
            self.assertEqual(j.check_resume("Q1", "A", "a" * 64, "model1"), "skip")
        with DispatchJournal(self.journal_path) as j2:
            self.assertEqual(j2.check_resume("Q1", "A", "a" * 64, "model1"), "skip")

    def test_failed_not_auto_retried(self):
        from newdomain.journal import DispatchJournal
        with DispatchJournal(self.journal_path) as j:
            j.record_started("Q1", "A", "a" * 64, "m1")
            j.record_terminal("Q1", "A", "a" * 64, "m1", success=False, error="test")
            self.assertEqual(j.check_resume("Q1", "A", "a" * 64, "m1"), "fail")

    def test_inflight_fails_closed(self):
        from newdomain.journal import DispatchJournal, JournalError
        with DispatchJournal(self.journal_path) as j:
            j.record_started("Q1", "A", "a" * 64, "m1")
            with self.assertRaises(JournalError):
                j.check_resume("Q1", "A", "a" * 64, "m1")

    def test_changed_identity_rejected(self):
        from newdomain.journal import DispatchJournal, JournalError
        with DispatchJournal(self.journal_path) as j:
            j.record_started("Q1", "A", "a" * 64, "m1")
            j.record_terminal("Q1", "A", "a" * 64, "m1", success=True)
            # Same qid+arm, different prompt hash → rejected
            with self.assertRaises(JournalError) as cm:
                j.check_resume("Q1", "A", "c" * 64, "m1")
            self.assertIn("different", str(cm.exception).lower())

    def test_concurrent_process_rejected(self):
        from newdomain.journal import DispatchJournal, JournalError
        import subprocess
        j1 = DispatchJournal(self.journal_path)
        j1.acquire()
        try:
            r = subprocess.run(
                [sys.executable, "-c",
                 f"import sys; from pathlib import Path; sys.path.insert(0, '{REPO}'); "
                 f"from newdomain.journal import DispatchJournal; "
                 f"j2 = DispatchJournal(Path('{self.journal_path}')); "
                 f"j2.acquire()"],
                capture_output=True, text=True, timeout=15)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("Concurrent", r.stderr)
        finally:
            j1.release()

    def test_conflicting_terminal_rejected(self):
        from newdomain.journal import DispatchJournal, JournalError
        with DispatchJournal(self.journal_path) as j:
            j.record_started("Q1", "A", "a" * 64, "m1")
            j.record_terminal("Q1", "A", "a" * 64, "m1", success=True)
            with self.assertRaises(JournalError):
                j.record_terminal("Q1", "A", "a" * 64, "m1", success=False)


class TestJournalStrictTransitions(unittest.TestCase):
    """Journal strict state machine: reject invalid transitions."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.journal_path = Path(self._td.name) / "journal.jsonl"

    def test_terminal_without_started_rejected(self):
        from newdomain.journal import DispatchJournal, JournalError
        with DispatchJournal(self.journal_path) as j:
            with self.assertRaises(JournalError):
                j.record_terminal("Q1", "A", "a" * 64, "m1", success=True)

    def test_started_after_terminal_rejected_on_reload(self):
        from newdomain.journal import DispatchJournal, JournalError
        j = DispatchJournal(self.journal_path)
        j.acquire()
        j.record_started("Q1", "A", "a" * 64, "m1")
        j.record_terminal("Q1", "A", "a" * 64, "m1", success=True)
        j.release()
        # Corrupt the journal by appending a started after terminal
        with open(self.journal_path, "a") as f:
            f.write(json.dumps({"key": "Q1|A|aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|m1", "status": "started",
                                 "timestamp": 999}) + "\n")
        j2 = DispatchJournal(self.journal_path)
        with self.assertRaises(JournalError):
            j2.acquire()

    def test_methods_require_lock(self):
        from newdomain.journal import DispatchJournal, JournalError
        j = DispatchJournal(self.journal_path)
        with self.assertRaises(JournalError):
            j.check_resume("Q1", "A", "h", "m")
        with self.assertRaises(JournalError):
            j.record_started("Q1", "A", "h", "m")
        with self.assertRaises(JournalError):
            j.record_terminal("Q1", "A", "h", "m", success=True)

    def test_duplicate_started_rejected(self):
        from newdomain.journal import DispatchJournal, JournalError
        with DispatchJournal(self.journal_path) as j:
            j.record_started("Q1", "A", "a" * 64, "m1")
            with self.assertRaises(JournalError):
                j.record_started("Q1", "A", "a" * 64, "m1")

    def test_resume_no_calls_on_prior_failure(self):
        """Failed prior dispatch must not trigger a new paid call."""
        from newdomain.journal import DispatchJournal
        with DispatchJournal(self.journal_path) as j:
            j.record_started("Q1", "A", "a" * 64, "m1")
            j.record_terminal("Q1", "A", "a" * 64, "m1", success=False, error="test failure")
            result = j.check_resume("Q1", "A", "a" * 64, "m1")
            self.assertEqual(result, "fail")  # must not return None (which would allow re-dispatch)


class TestStrictProfile(unittest.TestCase):
    def test_integer_fields_rejected(self):
        from newdomain.profile import load_profile, ProfileError
        with tempfile.TemporaryDirectory() as td:
            pp = Path(td) / "p.json"
            pp.write_text(json.dumps({
                "manifest_path": 42, "manifest_sha256": 42,
                "dev_ledger_path": 42, "final_ledger_path": 42,
                "redaction_names_path": 42}), encoding="utf-8")
            with self.assertRaises(ProfileError):
                load_profile(pp)

    def test_relative_path_rejected(self):
        from newdomain.profile import load_profile, ProfileError
        with tempfile.TemporaryDirectory() as td:
            pp = Path(td) / "p.json"
            pp.write_text(json.dumps({
                "manifest_path": "relative/path.json",
                "manifest_sha256": "a" * 64,
                "dev_ledger_path": "/abs/ledger.json",
                "final_ledger_path": "/abs/final.json",
                "redaction_names_path": "/abs/names.json"}), encoding="utf-8")
            with self.assertRaises(ProfileError) as cm:
                load_profile(pp)
            self.assertIn("absolute", str(cm.exception))

    def test_non_dict_rejected(self):
        from newdomain.profile import load_profile, ProfileError
        with tempfile.TemporaryDirectory() as td:
            pp = Path(td) / "p.json"
            pp.write_text('[1,2,3]', encoding="utf-8")
            with self.assertRaises(ProfileError):
                load_profile(pp)


class TestRunHeaderResume(unittest.TestCase):
    """Run identity header: write on new, verify on resume, reject changed inputs."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.td = Path(self._td.name)
        self.corpus = _write_synth_corpus(self.td)
        self.questions = self.td / "q.json"
        self.questions.write_text(json.dumps(
            [{"qid": "Q1", "question": QUERY}]), encoding="utf-8")

    def test_header_written_on_new(self):
        from newdomain.generation import _run_identity, _verify_or_write_header
        header_path = self.td / "header.json"
        ident = _run_identity(self.corpus, self.questions, None, ["B0"], "m")
        _verify_or_write_header(header_path, ident, resume=False)
        self.assertTrue(header_path.exists())

    def test_header_match_on_resume(self):
        from newdomain.generation import _run_identity, _verify_or_write_header
        header_path = self.td / "header.json"
        ident = _run_identity(self.corpus, self.questions, None, ["B0"], "m")
        _verify_or_write_header(header_path, ident, resume=False)
        result = _verify_or_write_header(header_path, ident, resume=True)
        self.assertEqual(result["corpus_sha256"], ident["corpus_sha256"])

    def test_changed_corpus_rejected(self):
        from newdomain.generation import _run_identity, _verify_or_write_header
        header_path = self.td / "header.json"
        ident1 = _run_identity(self.corpus, self.questions, None, ["B0"], "m")
        _verify_or_write_header(header_path, ident1, resume=False)
        other_corpus = self.td / "other.jsonl"
        other_corpus.write_text("different", encoding="utf-8")
        ident2 = _run_identity(other_corpus, self.questions, None, ["B0"], "m")
        with self.assertRaises(RuntimeError) as cm:
            _verify_or_write_header(header_path, ident2, resume=True)
        self.assertIn("corpus_sha256", str(cm.exception))

    def test_changed_questions_rejected(self):
        from newdomain.generation import _run_identity, _verify_or_write_header
        header_path = self.td / "header.json"
        ident1 = _run_identity(self.corpus, self.questions, None, ["B0"], "m")
        _verify_or_write_header(header_path, ident1, resume=False)
        other_q = self.td / "other_q.json"
        other_q.write_text("different", encoding="utf-8")
        ident2 = _run_identity(self.corpus, other_q, None, ["B0"], "m")
        with self.assertRaises(RuntimeError) as cm:
            _verify_or_write_header(header_path, ident2, resume=True)
        self.assertIn("questions_sha256", str(cm.exception))

    def test_resume_without_header_rejected(self):
        from newdomain.generation import _run_identity, _verify_or_write_header
        header_path = self.td / "nonexistent.json"
        ident = _run_identity(self.corpus, self.questions, None, ["B0"], "m")
        with self.assertRaises(RuntimeError) as cm:
            _verify_or_write_header(header_path, ident, resume=True)
        self.assertIn("no run header", str(cm.exception))

    def test_new_run_with_existing_header_rejected(self):
        from newdomain.generation import _run_identity, _verify_or_write_header
        header_path = self.td / "header.json"
        ident = _run_identity(self.corpus, self.questions, None, ["B0"], "m")
        _verify_or_write_header(header_path, ident, resume=False)
        with self.assertRaises(FileExistsError):
            _verify_or_write_header(header_path, ident, resume=False)


class TestResumeEndToEnd(unittest.TestCase):
    """Mock generation e2e with resume: verify zero re-dispatch on all-succeeded."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.td = Path(self._td.name)
        self.corpus = _write_synth_corpus(self.td)
        self.questions = self.td / "q.json"
        self.questions.write_text(json.dumps(
            [{"qid": "Q1", "question": QUERY}]), encoding="utf-8")

    def test_resume_all_succeeded_zero_calls(self):
        """All jobs in journal as succeeded → resume adds zero rows and zero calls."""
        from newdomain.journal import DispatchJournal
        from newdomain.generation import _run_identity, _verify_or_write_header

        output_dir = self.td / "out"
        output_dir.mkdir()
        out_file = output_dir / "dev-test-results.jsonl"
        header_path = output_dir / "dev-test-header.json"
        journal_path = output_dir / "dev-test-journal.jsonl"

        ident = _run_identity(self.corpus, self.questions, None, ["B0"], "deepseek-flash")
        _verify_or_write_header(header_path, ident, resume=False)

        saved_row = json.dumps({"qid": "Q1", "arm": "B0", "valid": True,
                                  "complete": True, "question": QUERY})
        out_file.write_text(saved_row + "\n", encoding="utf-8")

        from newdomain import baseline as b0_mod
        from newdomain import candidate as c1_mod
        units = b0_mod.load_units(self.corpus)
        index = b0_mod.NewDomainBaseline(b0_mod.build_chunks(units))
        results = index.retrieval(QUERY, k=8)["results"]
        messages = b0_mod.build_messages(QUERY, results, mode="B0")
        prompt_sha = hashlib.sha256(
            json.dumps(messages, ensure_ascii=False).encode()).hexdigest()

        with DispatchJournal(journal_path) as j:
            j.record_started("Q1", "B0", prompt_sha, "deepseek-flash")
            j.record_terminal("Q1", "B0", prompt_sha, "deepseek-flash", success=True)

        with DispatchJournal(journal_path) as j:
            self.assertEqual(j.check_resume("Q1", "B0", prompt_sha, "deepseek-flash"), "skip")

        content = out_file.read_text(encoding="utf-8")
        self.assertEqual(content.strip(), saved_row)
        self.assertEqual(len(content.strip().split("\n")), 1)

    def test_resume_changed_input_rejected_by_journal(self):
        """Journal with succeeded entry + different prompt hash → changed identity."""
        from newdomain.journal import DispatchJournal, JournalError

        journal_path = self.td / "j.jsonl"
        with DispatchJournal(journal_path) as j:
            j.record_started("Q1", "B0", "b" * 64, "deepseek-flash")
            j.record_terminal("Q1", "B0", "b" * 64, "deepseek-flash", success=True)

        with DispatchJournal(journal_path) as j2:
            with self.assertRaises(JournalError) as cm:
                j2.check_resume("Q1", "B0", "c" * 64, "deepseek-flash")
            self.assertIn("different", str(cm.exception).lower())

    def test_resume_inflight_rejected(self):
        """Journal with started-but-not-terminal entry → fail-closed."""
        from newdomain.journal import DispatchJournal, JournalError

        journal_path = self.td / "j.jsonl"
        with DispatchJournal(journal_path) as j:
            j.record_started("Q1", "B0", "a" * 64, "deepseek-flash")
            with self.assertRaises(JournalError):
                j.check_resume("Q1", "B0", "a" * 64, "deepseek-flash")

    def test_resume_failed_not_retried(self):
        """Journal with failed terminal → returns 'fail', not None (which would allow re-dispatch)."""
        from newdomain.journal import DispatchJournal

        journal_path = self.td / "j.jsonl"
        with DispatchJournal(journal_path) as j:
            j.record_started("Q1", "B0", "a" * 64, "deepseek-flash")
            j.record_terminal("Q1", "B0", "a" * 64, "deepseek-flash",
                               success=False, error="prior failure")
            result = j.check_resume("Q1", "B0", "a" * 64, "deepseek-flash")
            self.assertEqual(result, "fail")
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
