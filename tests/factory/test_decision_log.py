"""The decision log (spec-factory T-0017): `decision add` and `resolve --decision` write
`decisions.md` at any ticket state; the spec writer, critic and planner receive a non-empty log;
the triage and spec-writer prompts ask whether an answer is a standing decision.

Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_spec_store.py does.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FENCE = "`" * 3


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


def js(cp):
    return json.loads(cp.stdout.strip().splitlines()[-1])


def today() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")


def log_lines(store: Path) -> list[str]:
    """The decision log's lines with the UTC date replaced by TODAY."""
    p = store / "decisions.md"
    if not p.exists():
        return []
    d = today() + " "
    return ["TODAY " + ln[len(d):] if ln.startswith(d) else ln for ln in p.read_text(encoding="utf-8").splitlines()]


def events(store: Path, name: str) -> list[dict]:
    return [json.loads(ln) for ln in run(store, "log", "tail", "-n", "200", "--event", name).stdout.splitlines()]


def ticket(store: Path) -> dict:
    return yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())


@pytest.fixture
def store(tmp_path: Path) -> Path:
    s = tmp_path / "state"
    req = tmp_path / "r.md"
    req.write_text("# demo\n\nDo it.\n")
    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
    return s


def park(store: Path, reason: str) -> None:
    assert run(store, "ticket", "park", "T-0001", "--reason", reason).returncode == 0


# ----- part A: decision add -----------------------------------------------------------------

def test_decision_add_logs_against_a_closed_ticket_in_archives_format(store):
    assert run(store, "resolve", "T-0001", "--close").returncode == 0
    cp = run(store, "decision", "add", "T-0001", "Lionbot code lives under lionbot/")
    assert cp.returncode == 0, cp.stderr
    assert js(cp) == {"ok": True, "id": "T-0001", "decision": f"{today()} T-0001 Lionbot code lives under lionbot/"}
    assert ticket(store)["status"] == "closed"
    assert run(store, "decision", "add", "T-0001", "  Second rule  ").returncode == 0
    assert log_lines(store) == ["TODAY T-0001 Lionbot code lives under lionbot/", "TODAY T-0001 Second rule"]
    ev = events(store, "decision.recorded")
    assert [(e["ticket"], e["via"], e["line"]) for e in ev] == [
        ("T-0001", "decision add", f"{today()} T-0001 Lionbot code lives under lionbot/"),
        ("T-0001", "decision add", f"{today()} T-0001 Second rule")]
    assert all(e["by"] for e in ev)


def test_decision_add_needs_no_spec_store_and_appends_to_an_existing_log(store):
    assert not (store / "openspec").exists()
    (store / "decisions.md").write_text("2026-01-01 T-0009 kept\n")
    assert run(store, "decision", "add", "T-0001", "new").returncode == 0
    assert (store / "decisions.md").read_text() == f"2026-01-01 T-0009 kept\n{today()} T-0001 new\n"
    assert not (store / "openspec").exists()


@pytest.mark.parametrize("tid, text", [("T-0009", "x"), ("T-0001", "  "), ("T-0001", ""),
                                       ("T-0001", "one\ntwo"), ("T-0001", "one\rtwo")])
def test_decision_add_refuses_an_unknown_ticket_and_blank_or_multi_line_text(store, tid, text):
    cp = run(store, "decision", "add", tid, text)
    assert cp.returncode == 2, cp.stderr
    assert js(cp)["ok"] is False
    assert not (store / "decisions.md").exists()
    assert events(store, "decision.recorded") == []


# ----- part A: resolve --decision ----------------------------------------------------------

def test_resolve_answer_and_close_each_log_a_decision_and_keep_it_in_the_record(store, tmp_path):
    ans = tmp_path / "a.md"
    ans.write_text("Use option B.\n")
    park(store, "NEEDS-HUMAN from triage")
    cp = run(store, "resolve", "T-0001", "--answer", str(ans), "--decision", "Option B is the standing rule")
    assert cp.returncode == 0, cp.stderr
    line1 = f"{today()} T-0001 Option B is the standing rule"
    assert js(cp)["decision"] == line1 and js(cp)["state"] == "ready-for-triage"
    assert (store / "requests" / "T-0001.md").read_text().count("## Answer ") == 1
    cp = run(store, "resolve", "T-0001", "--close", "--decision", "Closed as a recorded decision")
    assert cp.returncode == 0, cp.stderr
    line2 = f"{today()} T-0001 Closed as a recorded decision"
    assert ticket(store)["status"] == "closed"
    assert log_lines(store) == ["TODAY T-0001 Option B is the standing rule", "TODAY T-0001 Closed as a recorded decision"]
    recs = [yaml.safe_load((store / "approvals" / "T-0001" / f"resolve-{n}.yaml").read_text()) for n in (1, 2)]
    assert [(r["kind"], r["decision"]) for r in recs] == [("answer", line1), ("close", line2)]
    hist = [h for h in ticket(store)["history"] if "resolve" in h]
    assert [(h["resolve"], h["decision"]) for h in hist] == [("answer", line1), ("close", line2)]
    ev = events(store, "decision.recorded")
    assert [(e["via"], e["line"]) for e in ev] == [("resolve --answer", line1), ("resolve --close", line2)]


def test_resolve_without_decision_writes_no_decision_key(store):
    assert run(store, "resolve", "T-0001", "--close").returncode == 0
    rec = yaml.safe_load((store / "approvals" / "T-0001" / "resolve-1.yaml").read_text())
    assert "decision" not in rec
    assert not (store / "decisions.md").exists()


def test_resolve_decision_alone_or_with_a_mode_that_cannot_carry_one_is_refused(store, tmp_path):
    ruling = tmp_path / "r2.md"
    ruling.write_text("Ruling.\n")
    park(store, "ESCALATE from critic")
    before = ticket(store)
    for argv in (["--decision", "x"],
                 ["--ruling", str(ruling), "--decision", "x"],
                 ["--to", "spec-gate", "--decision", "x"],
                 ["--redispatch", "--decision", "x"],
                 # --ruling runs ahead of --close, so the close (and its decision) would not happen
                 ["--ruling", str(ruling), "--close", "--decision", "x"]):
        cp = run(store, "resolve", "T-0001", *argv)
        assert cp.returncode == 2, (argv, cp.stderr)
        assert "--decision applies only with --answer or --close" in cp.stderr
    assert ticket(store) == before
    assert not list((store / "approvals" / "T-0001").glob("ruling-*"))
    assert not (store / "decisions.md").exists()


def test_resolve_decision_is_not_logged_when_the_close_or_answer_is_refused(store, tmp_path):
    ans = tmp_path / "a.md"
    ans.write_text("B.\n")
    # --answer on a ticket that is not parked NEEDS-HUMAN: refused, no answer, no decision
    cp = run(store, "resolve", "T-0001", "--answer", str(ans), "--decision", "x")
    assert cp.returncode == 2
    assert "## Answer" not in (store / "requests" / "T-0001.md").read_text()
    assert run(store, "resolve", "T-0001", "--close", "--decision", "Closed with a rule").returncode == 0
    cp = run(store, "resolve", "T-0001", "--close", "--decision", "Again")
    assert cp.returncode == 2
    assert log_lines(store) == ["TODAY T-0001 Closed with a rule"]
    assert len(events(store, "decision.recorded")) == 1


def test_resolve_bad_decision_text_refuses_before_the_answer_is_appended(store, tmp_path):
    ans = tmp_path / "a.md"
    ans.write_text("B.\n")
    park(store, "NEEDS-HUMAN from triage")
    req_before = (store / "requests" / "T-0001.md").read_text()
    for text in ("   ", "one\ntwo"):
        cp = run(store, "resolve", "T-0001", "--answer", str(ans), "--decision", text)
        assert cp.returncode == 2, cp.stderr
    assert (store / "requests" / "T-0001.md").read_text() == req_before
    assert ticket(store)["status"] == "parked"
    assert not (store / "approvals" / "T-0001").exists() or not list((store / "approvals" / "T-0001").glob("resolve-*"))
    assert not (store / "decisions.md").exists()


# ----- part B: the decision log as role input --------------------------------------------------

def start_and_compose(store: Path, role: str, status: str) -> tuple[list[str], str]:
    assert run(store, "ticket", "set", "T-0001", f"status={status}", "in_flight=[]").returncode == 0
    rid = js(run(store, "run", "start", "--role", role, "--ticket", "T-0001"))["run_id"]
    cp = run(store, "run", "compose", rid)
    assert cp.returncode == 0, cp.stderr
    return js(cp)["sources"], (store / "runs" / rid / "input.md").read_text()


@pytest.fixture
def spec_store(store: Path) -> Path:
    assert run(store, "init").returncode == 0
    (store / "openspec" / "specs" / "thing").mkdir(parents=True)
    (store / "openspec" / "specs" / "thing" / "spec.md").write_text("# thing\n\n## Requirements\n")
    (store / "specs" / "T-0001").mkdir(parents=True)
    (store / "specs" / "T-0001" / "v1.md").write_text("spec\n")
    assert run(store, "ticket", "set", "T-0001", "spec.version=1", "spec.approved_version=1").returncode == 0
    return store


def test_spec_writer_critic_and_planner_receive_a_non_empty_log_and_triage_does_not(spec_store):
    s = spec_store
    (s / "decisions.md").write_text("2026-10-01 T-0009 SENTINEL keep the old format\n")
    got = {r: start_and_compose(s, r, st) for r, st in (
        ("triage", "ready-for-triage"), ("spec_writer", "ready-for-spec-writer"),
        ("critic", "ready-for-critic"), ("planner", "ready-for-planner"))}
    assert got["triage"][0] == ["requests/T-0001.md"]
    assert got["spec_writer"][0] == ["requests/T-0001.md", "openspec/specs/thing/spec.md", "decisions.md"]
    assert got["critic"][0] == ["specs/T-0001/v1.md", "openspec/specs/thing/spec.md", "decisions.md"]
    assert got["planner"][0] == ["specs/T-0001/v1.md", "decisions.md"]
    assert "SENTINEL" not in got["triage"][1]
    for r in ("spec_writer", "critic", "planner"):
        text = got[r][1]
        assert text.count("SENTINEL") == 1
        assert "## Decision log (decisions.md): standing decisions, read-only\n\n2026-10-01 T-0009 SENTINEL" in text


def test_planner_gets_the_log_before_a_ruling(spec_store):
    s = spec_store
    (s / "decisions.md").write_text("2026-10-01 T-0009 SENTINEL\n")
    (s / "approvals" / "T-0001").mkdir(parents=True)
    (s / "approvals" / "T-0001" / "ruling-1.md").write_text("Ruling.\n")
    sources, _ = start_and_compose(s, "planner", "ready-for-planner")
    assert sources == ["specs/T-0001/v1.md", "decisions.md", "approvals/T-0001/ruling-1.md"]


@pytest.mark.parametrize("content", [None, "", "\n", "  \n\t\n"])
def test_an_absent_or_whitespace_only_log_adds_no_source(spec_store, content):
    s = spec_store
    if content is None:
        (s / "decisions.md").unlink()
    else:
        (s / "decisions.md").write_text(content)
    assert start_and_compose(s, "spec_writer", "ready-for-spec-writer")[0] == ["requests/T-0001.md", "openspec/specs/thing/spec.md"]
    assert start_and_compose(s, "critic", "ready-for-critic")[0] == ["specs/T-0001/v1.md", "openspec/specs/thing/spec.md"]
    assert start_and_compose(s, "planner", "ready-for-planner")[0] == ["specs/T-0001/v1.md"]


# ----- part C: the questions ask whether an answer is standing ------------------------------------

def test_triage_and_spec_writer_system_prompts_ask_about_standing_decisions(store):
    for role, status in (("triage", "ready-for-triage"), ("spec_writer", "ready-for-spec-writer")):
        assert run(store, "ticket", "set", "T-0001", f"status={status}", "in_flight=[]").returncode == 0
        rid = js(run(store, "run", "start", "--role", role, "--ticket", "T-0001"))["run_id"]
        assert "standing decision" in (store / "runs" / rid / "system-prompt.txt").read_text(), role


@pytest.mark.parametrize("heading, copy", [("1. Triage", "01-triage.md"), ("2. Spec writer", "02-spec-writer.md")])
def test_triage_and_spec_writer_design_blocks_equal_their_copies(heading, copy):
    design = (REPO / "docs" / "design.md").read_text(encoding="utf-8")
    m = re.search(r"^## " + re.escape(heading) + r"\n.*?^" + FENCE + r"text\n(.*?)^" + FENCE + "$", design, re.M | re.S)
    assert m is not None
    block = m.group(1)
    assert "standing decision" in block
    assert block == (REPO / "docs" / "prompts" / copy).read_text(encoding="utf-8")
