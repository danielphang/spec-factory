"""The scorecard and its records (T-0056 parts B to D), black-box through `bin/factory`.

- `stats --scorecard`: the figures of a fixture built like the acceptance fixture, two instances (one
  whose instance.yaml sets `target_is_factory: true`) in both windows, with and without transcripts;
  the 2-second rule that tells a person's transition from one an approval made; a store with no
  instance; the two refusals; and that it writes nothing.
- `escape add`: its five refusals, each exit 2 with nothing written; its one event, which keeps the
  `--issue` text only as its SHA-256; and that the text appears nowhere under the store.
- `intervention add`: its event and its refusals.
- The live-store fence refuses both unmarked while a run is in flight on an instance's own store.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import yaml

from ._cli import BIN, STRIP, cli, js, run, tree
from ._fixtures import assert_refused, snapshot, start_triage, target  # noqa: F401  (target is a fixture)

LINK = "https://tracker.example/9"


def stats(*argv: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in STRIP}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([str(BIN), "stats", "--scorecard", *argv], capture_output=True, text=True, env=env)


def rows(text: str, heading: str) -> list[str]:
    """The table rows under `## <heading>`, the separator row left out."""
    block = text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    return [ln for ln in block.splitlines() if ln.startswith("| ")]


def _run(store: Path, rid: str, tid: str, started: str, finished: str | None, wall: int | None, status: str,
         claude: dict | None = None) -> None:
    d = store / "runs" / rid
    d.mkdir(parents=True)
    meta = {"run_id": rid, "role": rid.split("-", 2)[2], "ticket": tid, "model": "opus", "started": started,
            "finished": finished, "wall_s": wall, "status": status}
    if claude is not None:
        meta["claude"] = claude
    (d / "meta.yaml").write_text(yaml.safe_dump(meta))


def _rec(inp: int, cache: int, out: int, usd: float | None) -> dict:
    return {"usage": {"input_tokens": inp, "cache_read_input_tokens": cache, "cache_creation_input_tokens": 0,
                      "output_tokens": out}, "total_cost_usd": usd, **({} if usd is not None else {"source": "transcript"})}


def _log(store: Path, *events: tuple) -> None:
    with (store / "log" / "2026-10.jsonl").open("a") as fh:
        for ts, event, tid, *extra in events:
            fh.write(json.dumps({"ts": ts, "event": event, "ticket": tid, **(extra[0] if extra else {})}) + "\n")


def fixture(tmp_path: Path) -> Path:
    """Two instances, f/fw (target_is_factory: true) and f/tg, each with its store at .factory/store, and
    transcripts under f/tx for tg's two runs with no cost record. The same figures as the acceptance
    fixture of `stats --scorecard`."""
    f = tmp_path / "f"
    for i in ("fw", "tg"):
        (f / i / ".factory" / "store" / "log").mkdir(parents=True)
        (f / i / ".factory" / "instance.yaml").write_text("state_dir: .factory/store\n")
    with (f / "fw" / ".factory" / "instance.yaml").open("a") as fh:
        fh.write("target_is_factory: true\n")
    tg, fw = f / "tg" / ".factory" / "store", f / "fw" / ".factory" / "store"
    _run(tg, "run-0001-triage", "T-0001", "2026-10-02T00:10:00+00:00", "2026-10-02T00:20:00+00:00", 600, "ACCEPT", _rec(100, 0, 50, 1.00))
    _run(tg, "run-0002-implementer", "T-0001.1", "2026-10-03T10:00:00+00:00", "2026-10-03T10:50:00+00:00", 3000, "READY-FOR-REVIEW", _rec(200, 0, 100, 2.00))
    _run(tg, "run-0003-triage", "T-0002", "2026-10-08T00:10:00+00:00", "2026-10-08T00:40:00+00:00", 1800, "ACCEPT", _rec(1000, 0, 100, 0.50))
    _run(tg, "run-0004-implementer", "T-0002.1", "2026-10-08T10:00:00+00:00", "2026-10-08T11:30:00+00:00", 5400, "READY-FOR-REVIEW", _rec(2000, 3000, 300, None))
    _run(tg, "run-0005-implementer", "T-0002.2", "2026-10-09T10:00:00+00:00", "2026-10-09T11:00:00+00:00", 3600, "READY-FOR-REVIEW")
    _run(tg, "run-0006-reviewer", "T-0002.2", "2026-10-09T12:00:00+00:00", "2026-10-09T12:30:00+00:00", 1800, "KILLED")
    _run(tg, "run-0007-triage", "T-0003", "2026-10-09T00:05:00+00:00", "2026-10-09T00:20:00+00:00", 900, "ACCEPT", _rec(400, 0, 100, 0.25))
    _run(tg, "run-0008-implementer", "T-0003.1", "2026-10-09T03:00:00+00:00", "2026-10-09T03:39:00+00:00", 2340, "READY-FOR-REVIEW", _rec(500, 0, 200, None))
    _run(tg, "run-0009-critic", "T-0002", "2026-10-08T05:00:00+00:00", None, None, "running")
    _run(tg, "run-0010-triage", "T-0004", "2026-10-08T00:00:00+00:00", "2026-10-08T00:10:00+00:00", 600, "REJECT")
    _run(fw, "run-0001-implementer", "T-0010.1", "2026-10-10T11:00:00+00:00", "2026-10-10T11:30:00+00:00", 1800, "READY-FOR-REVIEW")
    op = {"by": "op"}
    _log(tg,
         ("2026-10-02T00:00:00+00:00", "ticket.created", "T-0001"),
         ("2026-10-02T01:00:00+00:00", "approval.recorded", "T-0001", {"kind": "spec", "version": 1, **op}),
         ("2026-10-02T01:00:01+00:00", "ticket.transition", "T-0001", {"from": "awaiting-spec-gate", "to": "ready-for-planner", **op}),
         ("2026-10-03T00:00:00+00:00", "human.resolved", "T-0001.1", {"kind": "ruling", **op}),
         ("2026-10-03T00:00:00+00:00", "ticket.transition", "T-0001.1", {"from": "parked", "to": "ready-for-implementer", **op}),
         ("2026-10-03T12:00:00+00:00", "merge.done", "T-0001.1"),
         ("2026-10-03T12:00:00+00:00", "ticket.transition", "T-0001.1", {"from": "ready-for-merge", "to": "merged", "by": "merge"}),
         ("2026-10-03T12:00:02+00:00", "ticket.transition", "T-0001", {"from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}),
         ("2026-10-08T00:00:00+00:00", "ticket.created", "T-0002"),
         ("2026-10-08T00:00:00+00:00", "ticket.created", "T-0004"),
         ("2026-10-08T00:30:00+00:00", "spec.added", "T-0002", {"version": 1, "source": "run-0011-spec_writer"}),
         ("2026-10-08T01:00:00+00:00", "approval.recorded", "T-0002", {"kind": "spec", "version": 1, **op}),
         ("2026-10-08T01:00:01+00:00", "ticket.transition", "T-0002", {"from": "awaiting-spec-gate", "to": "ready-for-planner", **op}),
         ("2026-10-08T12:00:00+00:00", "ticket.transition", "T-0002.1", {"from": "parked", "to": "ready-for-implementer", **op}),
         ("2026-10-09T00:00:00+00:00", "ticket.created", "T-0003"),
         ("2026-10-09T00:00:00+00:00", "merge.done", "T-0002.1"),
         ("2026-10-09T01:00:00+00:00", "spec.added", "T-0003", {"version": 2, "source": "gate edit /x/T-0003-gate.md"}),
         ("2026-10-09T01:00:00+00:00", "approval.recorded", "T-0003", {"kind": "spec", "version": 2, **op}),
         ("2026-10-09T01:00:00+00:00", "ticket.transition", "T-0003", {"from": "awaiting-spec-gate", "to": "ready-for-planner", **op}),
         ("2026-10-09T02:00:00+00:00", "human.resolved", "T-0004", {"kind": "close", **op}),
         ("2026-10-09T02:00:01+00:00", "ticket.transition", "T-0004", {"from": "parked", "to": "closed", **op}),
         ("2026-10-09T06:00:00+00:00", "merge.done", "T-0003.1"),
         ("2026-10-09T06:00:02+00:00", "ticket.transition", "T-0003", {"from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}),
         ("2026-10-10T00:00:00+00:00", "ticket.created", "T-0006"),
         ("2026-10-10T06:00:00+00:00", "merge.done", "T-0002.2"),
         ("2026-10-10T06:00:02+00:00", "ticket.transition", "T-0002", {"from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}),
         ("2026-10-11T00:00:00+00:00", "decision.recorded", "T-0002", {"line": "x", "via": "decision add", **op}),
         ("2026-10-11T00:00:00+00:00", "decision.recorded", "T-0003", {"line": "y", "via": "resolve --answer", **op}),
         ("2026-10-12T00:00:00+00:00", "ticket.created", "T-0005"),
         ("2026-10-12T00:00:00+00:00", "escape.recorded", "T-0002", {"issue_sha256": "0" * 63 + "1", **op}),
         ("2026-10-13T00:00:00+00:00", "escape.recorded", "T-0002", {"issue_sha256": "0" * 63 + "2", **op}),
         ("2026-10-14T00:00:00+00:00", "merge.done", "T-0005.1"),
         ("2026-10-16T00:00:00+00:00", "escape.recorded", "T-0001", {"issue_sha256": "0" * 63 + "3", **op}),
         ("2026-10-16T00:00:00+00:00", "merge.done", "T-0006.1"),
         ("2026-10-16T00:00:02+00:00", "ticket.transition", "T-0006", {"from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}))
    _log(fw,
         ("2026-10-10T00:00:00+00:00", "ticket.created", "T-0010"),
         ("2026-10-10T12:00:00+00:00", "merge.done", "T-0010.1"),
         ("2026-10-10T12:00:01+00:00", "ticket.transition", "T-0010", {"from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}))
    for name, ts, rid, inp, cache, out in (("a/agent-1.jsonl", "2026-10-09T10:00:05Z", "run-0005-implementer", 10, 90, 20),
                                           ("b/agent-2.jsonl", "2026-10-09T12:00:05Z", "run-0006-reviewer", 5, 45, 10)):
        p = f / "tx" / name
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"type": "user", "timestamp": ts, "message": {"role": "user", "content":
                                 f"[Workflow harness — computed task] Your entire input is the file {tg}/runs/{rid}/input.md"}})
                     + "\n" + json.dumps({"type": "assistant", "timestamp": ts, "message": {"id": f"m-{rid}", "usage": {
                         "input_tokens": inp, "cache_read_input_tokens": cache, "cache_creation_input_tokens": 0,
                         "output_tokens": out}}}) + "\n")
    return f


def scorecard(f: Path, *argv: str) -> str:
    cp = stats("--store", str(f / "fw" / ".factory" / "store"), "--store", str(f / "tg" / ".factory" / "store"),
               "--since", "2026-10-08", "--until", "2026-10-15", *argv)
    assert cp.returncode == 0, cp.stderr
    return cp.stdout


HEAD = "| measure | 2026-10-01 to 2026-10-08 | 2026-10-08 to 2026-10-15 |"


# ----- stats --scorecard ----------------------------------------------------------------------

def test_the_scorecard_gives_each_instances_measures_for_both_windows_and_writes_nothing(tmp_path):
    f = fixture(tmp_path)
    before = tree(f)
    text = scorecard(f)
    assert tree(f) == before
    assert text.startswith("# factory stats: scorecard\n\nWindows: 2026-10-01 to 2026-10-08, and 2026-10-08 to "
                           "2026-10-15; each from its first bound (inclusive) to its second (exclusive), in UTC. "
                           "Escapes count when recorded before 2026-10-15.\n\n## fw: factory work\n")
    assert str(f) not in text and "sha256" not in text
    assert rows(text, "fw: factory work") == [
        HEAD,
        "| Factory work merged | 0 | 1 |",
        "| Escapes | 0 | 0 |",
        "| Operator decisions and interventions per change | - | 0.0 |",
        "| … CLI decisions | 0 | 0 |",
        "| … interventions | 0 | 0 |",
        "| Tokens and wall time per change: wall time, median (range) | - | 0.5 h (0.5 to 0.5 h) |",
        "| … tokens, median (changes whose every run has tokens) | - (0 of 0) | - (0 of 1) |",
        "| … runs with tokens from a record, a transcript or neither | record 0, transcript 0, none 0 | record 0, transcript 0, none 1 |",
        "| … USD on the records that carry dollars | 0.00 (0 runs) | 0.00 (0 runs) |",
        "| Lead time, median (range) | - | 12.0 h (12.0 to 12.0 h) |"]
    assert rows(text, "tg: target changes") == [
        HEAD,
        "| Target changes merged | 1 | 2 |",
        "| Escapes | 0 | 1 (T-0002) |",
        "| Operator decisions and interventions per change | 2.0 | 3.0 |",
        "| … CLI decisions | 2 | 3 |",
        "| … interventions | 0 | 3 |",
        "| Tokens and wall time per change: wall time, median (range) | 1.0 h (1.0 to 1.0 h) | 2.2 h (0.9 to 3.5 h) |",
        "| … tokens, median (changes whose every run has tokens) | 450 (1 of 1) | 1200 (1 of 2) |",
        "| … runs with tokens from a record, a transcript or neither | record 2, transcript 0, none 0 | record 4, transcript 0, none 2 |",
        "| … USD on the records that carry dollars | 3.00 (2 runs) | 0.75 (2 runs) |",
        "| Lead time, median (range) | 36.0 h (36.0 to 36.0 h) | 30.0 h (6.0 to 54.0 h) |"]


def test_a_run_with_no_cost_record_takes_its_tokens_from_its_transcript(tmp_path):
    f = fixture(tmp_path)
    before = tree(f)
    got = rows(scorecard(f, "--transcripts", str(f / "tx")), "tg: target changes")
    assert tree(f) == before
    assert got[7:9] == [
        "| … tokens, median (changes whose every run has tokens) | 450 (1 of 1) | 3890 (2 of 2) |",
        "| … runs with tokens from a record, a transcript or neither | record 2, transcript 0, none 0 | record 4, transcript 2, none 0 |"]


def test_a_persons_transition_counts_unless_an_approval_or_resolve_of_its_ticket_is_within_2_seconds(tmp_path):
    f = fixture(tmp_path)
    s = f / "tg" / ".factory" / "store"
    _log(s, ("2026-10-12T05:00:00+00:00", "approval.recorded", "T-0005", {"kind": "spec", "version": 1, "by": "op"}),
         ("2026-10-12T05:00:03+00:00", "ticket.transition", "T-0005", {"from": "a", "to": "b", "by": "op"}),
         ("2026-10-12T05:00:01+00:00", "ticket.transition", "T-0006", {"from": "a", "to": "b", "by": "op"}),
         ("2026-10-12T06:00:00+00:00", "ticket.transition", "T-0005", {"from": "a", "to": "b", "by": "parent-check"}),
         ("2026-10-12T07:00:00+00:00", "intervention.recorded", None, {"kind": "commit", "by": "op"}))
    got = rows(scorecard(f), "tg: target changes")
    # two transitions with no approval of their own ticket within 2 s, and the intervention record
    assert got[4:6] == ["| … CLI decisions | 2 | 4 |", "| … interventions | 0 | 6 |"]


def test_a_store_with_no_instance_is_named_by_its_path_and_counts_target_changes(tmp_path):
    f = fixture(tmp_path)
    loose = tmp_path / "loose"
    (f / "tg" / ".factory" / "store").rename(loose)
    cp = stats("--store", str(loose), "--since", "2026-10-08", "--until", "2026-10-15")
    assert cp.returncode == 0, cp.stderr
    assert rows(cp.stdout, f"{loose}: target changes (no instance found)")[1] == "| Target changes merged | 1 | 2 |"


def test_an_instance_whose_state_dir_names_another_store_is_passed_over(tmp_path):
    f = fixture(tmp_path)
    (f / "tg" / ".factory" / "instance.yaml").write_text("state_dir: elsewhere\ntarget_is_factory: true\n")
    s = f / "tg" / ".factory" / "store"
    cp = stats("--store", str(s), "--since", "2026-10-08", "--until", "2026-10-15")
    assert cp.returncode == 0, cp.stderr
    assert f"## {s}: target changes (no instance found)\n" in cp.stdout


def test_refused_without_since(tmp_path):
    f = fixture(tmp_path)
    cp = stats("--store", str(f / "tg" / ".factory" / "store"), "--until", "2026-10-15")
    assert cp.returncode == 2
    assert cp.stderr.strip() == "factory stats: --scorecard needs --since"
    assert "scorecard\n" not in cp.stdout and "| " not in cp.stdout


def test_refused_for_a_target_is_factory_that_is_not_a_boolean(tmp_path):
    f = fixture(tmp_path)
    inst = f / "tg" / ".factory" / "instance.yaml"
    for bad in ("maybe", "1", "''", "null"):
        inst.write_text(f"state_dir: .factory/store\ntarget_is_factory: {bad}\n")
        cp = stats("--store", str(f / "fw" / ".factory" / "store"), "--store", str(f / "tg" / ".factory" / "store"),
                   "--since", "2026-10-08")
        assert cp.returncode == 2, bad
        assert cp.stderr.strip() == f"factory stats: target_is_factory in {inst} must be true or false"
        assert "| " not in cp.stdout
    inst.write_text("state_dir: .factory/store\ntarget_is_factory: false\n")
    assert "## tg: target changes\n" in scorecard(f)


def test_the_window_before_has_the_same_length_and_a_bound_off_midnight_shows_its_time(tmp_path):
    f = fixture(tmp_path)
    cp = stats("--store", str(f / "tg" / ".factory" / "store"), "--since", "2026-10-08", "--until", "2026-10-09T12:00")
    assert cp.returncode == 0, cp.stderr
    assert "| measure | 2026-10-06 12:00 to 2026-10-08 | 2026-10-08 to 2026-10-09 12:00 |" in cp.stdout
    assert "Escapes count when recorded before 2026-10-09 12:00." in cp.stdout


# ----- escape add and intervention add ---------------------------------------------------------

def _store(tmp_path: Path) -> Path:
    """A throwaway store with T-0001, whose sub-ticket merged, and T-0002, with no merge."""
    s = tmp_path / "store"
    for name, text in (("r1.md", "# F\n\nDo x.\n"), ("r2.md", "# G\n\nDo y.\n")):
        (tmp_path / name).write_text(text)
        assert run(s, "ticket", "new", "--file", str(tmp_path / name)).returncode == 0
    (s / "log" / "fixture.jsonl").write_text(
        json.dumps({"ts": "2026-10-02T00:00:00+00:00", "event": "merge.done", "ticket": "T-0001.1"}) + "\n"
        + json.dumps({"ts": "2026-10-02T00:00:02+00:00", "event": "ticket.transition", "ticket": "T-0001",
                      "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}) + "\n")
    return s


def _events(s: Path, name: str) -> list[dict]:
    return [e for p in sorted((s / "log").glob("*.jsonl")) for e in map(json.loads, p.read_text().splitlines())
            if e["event"] == name]


def test_escape_add_refuses_five_cases_and_writes_nothing(tmp_path):
    s = _store(tmp_path)
    before = tree(s)
    for argv, message in (
            (("T-0002", "--issue", LINK), "escape add: T-0002 has no merge"),
            (("T-0001.1", "--issue", LINK), "escape add: T-0001.1 is a sub-ticket; record the escape on its parent T-0001"),
            (("T-0009", "--issue", LINK), "no ticket T-0009"),
            (("T-0001", "--issue", ""), "escape add: --issue is empty"),
            (("T-0001", "--issue", LINK, "--note", f"see {LINK}"),
             "escape add: keep links out of the note; the store keeps no link")):
        cp = run(s, "escape", "add", *argv)
        assert cp.returncode == 2, argv
        assert cp.stderr.strip() == message
        assert "tracker.example" not in cp.stdout + cp.stderr
    assert tree(s) == before


def test_escape_add_keeps_the_issue_only_as_its_hash(tmp_path):
    s = _store(tmp_path)
    digest = hashlib.sha256(LINK.encode("utf-8")).hexdigest()
    cp = run(s, "escape", "add", "T-0001", "--issue", LINK, "--note", "needed a fix")
    assert cp.returncode == 0, cp.stderr
    assert js(cp) == {"ok": True, "id": "T-0001", "issue_sha256": digest}
    assert "tracker.example" not in cp.stdout + cp.stderr
    got = [{k: v for k, v in e.items() if k not in ("ts", "by")} for e in _events(s, "escape.recorded")]
    assert got == [{"event": "escape.recorded", "ticket": "T-0001", "issue_sha256": digest, "note": "needed a fix"}]
    assert not [p for p, b in tree(s).items() if b"tracker.example" in b]
    cp = stats("--store", str(s), "--since", "2026-10-01")
    assert "| Escapes | 0 | 1 (T-0001) |" in cp.stdout.splitlines()


def test_a_merge_of_the_ticket_itself_also_allows_an_escape(tmp_path):
    s = _store(tmp_path)
    with (s / "log" / "fixture.jsonl").open("a") as fh:
        fh.write(json.dumps({"ts": "2026-10-03T00:00:00+00:00", "event": "merge.done", "ticket": "T-0002"}) + "\n")
    cp = run(s, "escape", "add", "T-0002", "--issue", "x")
    assert cp.returncode == 0, cp.stderr
    assert js(cp)["issue_sha256"] == hashlib.sha256(b"x").hexdigest()


def test_intervention_add_records_one_event_the_scorecard_counts(tmp_path):
    s = _store(tmp_path)
    cp = run(s, "intervention", "add", "--kind", "commit", "--ticket", "T-0001", "--note", "hand commit to the gate config")
    assert cp.returncode == 0, cp.stderr
    assert js(cp) == {"ok": True, "kind": "commit", "id": "T-0001"}
    cp = run(s, "intervention", "add", "--kind", "stop")
    assert js(cp) == {"ok": True, "kind": "stop"}
    got = [{k: v for k, v in e.items() if k not in ("ts", "by")} for e in _events(s, "intervention.recorded")]
    assert got == [{"event": "intervention.recorded", "kind": "commit", "ticket": "T-0001",
                    "note": "hand commit to the gate config"},
                   {"event": "intervention.recorded", "kind": "stop"}]
    assert "| … interventions | 0 | 2 |" in stats("--store", str(s), "--since", "2026-10-01").stdout.splitlines()


def test_intervention_add_refuses_an_unknown_ticket_a_link_in_the_note_and_an_empty_kind(tmp_path):
    s = _store(tmp_path)
    before = tree(s)
    for argv, message in (
            (("--kind", "commit", "--ticket", "T-0009"), "no ticket T-0009"),
            (("--kind", "commit", "--note", f"see {LINK}"),
             "intervention add: keep links out of the note; the store keeps no link"),
            (("--kind", " "), "intervention add: --kind is empty")):
        cp = run(s, "intervention", "add", *argv)
        assert cp.returncode == 2, argv
        assert cp.stderr.strip() == message
    assert tree(s) == before


def test_the_fence_refuses_both_records_unmarked_while_a_run_is_in_flight(target, tmp_path):
    rid = start_triage(target)
    before = snapshot(target)
    for argv in (("escape", "add", "T-0001", "--issue", LINK), ("intervention", "add", "--kind", "commit")):
        assert_refused(cli(target, *argv), f"in flight: {rid}")
    assert snapshot(target) == before
