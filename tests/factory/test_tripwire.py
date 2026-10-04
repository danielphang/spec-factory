"""The tripwire on live files (issue #38): an instance's `tripwire` lists files outside the repo;
`run start` hashes each into a git-ignored baseline, and the run is compared once, when it leaves
the in-flight list (`run finish`, killed runs included, or a `ticket set` that drops it). A changed
`park` file parks the ticket; a changed `escalate` file queues an escalation. Nothing prints a
file's contents.

Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE) and a copy of the
suite's fixture instance (FACTORY_INSTANCE) with a `tripwire` key appended. Every listed file that
exists lives under tmp_path.
"""
from __future__ import annotations

import hashlib
import json
import os
import pwd
import shutil
import subprocess
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
SECRET = '{"token": "TRIPWIRE-SECRET-A"}\n'
OUT = "Type: bug\nTitle: Fixture\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"


class Inst:
    """A scratch instance and store with ticket T-0001 ready for triage. `tripwire` is the YAML
    text appended to the instance (None: no key)."""

    def __init__(self, tmp_path: Path, tripwire: str | None):
        self.tmp = tmp_path
        self.store = tmp_path / "store"
        inst = tmp_path / "inst"
        shutil.copytree(FIXTURE_INSTANCE, inst)
        if tripwire is not None:
            with (inst / "instance.yaml").open("a", encoding="utf-8") as f:
                f.write(tripwire + "\n")
        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_INSTANCE": str(inst),
                    "PYTHONDONTWRITEBYTECODE": "1"}
        req = tmp_path / "req.md"
        req.write_text("# Fixture\n\nDo the thing.\n")
        self.ok("ticket", "new", "--file", str(req))
        (tmp_path / "out.md").write_text(OUT)

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def start(self) -> str:
        return self.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]

    def finish(self, rid: str, *extra: str) -> dict:
        return self.ok("run", "finish", rid, *(extra or ("--output-file", str(self.tmp / "out.md"))))

    def ticket(self) -> dict:
        return self.ok("ticket", "show", "T-0001", "--json")

    def events(self, name: str) -> list[dict]:
        cp = self.cli("log", "tail", "-n", "1000", "--event", name)
        return [json.loads(ln) for ln in cp.stdout.splitlines() if ln.strip()]

    def store_text(self) -> str:
        return "".join(p.read_text(encoding="utf-8", errors="replace") for p in self.store.rglob("*") if p.is_file())


def live(tmp_path: Path) -> tuple[Inst, Path, Path, Path]:
    """The fixture of the spec's scenarios: park [policies.json, new.json], escalate [pairing.json],
    policies.json and pairing.json present, new.json absent."""
    d = tmp_path / "live"
    d.mkdir()
    pol, new, pair = d / "policies.json", d / "new.json", d / "pairing.json"
    pol.write_text(SECRET)
    pair.write_text('{"chat": "TRIPWIRE-SECRET-B"}\n')
    return Inst(tmp_path, f"tripwire:\n  park: [{pol}, {new}]\n  escalate: [{pair}]"), pol, new, pair


def test_a_changed_park_file_parks_the_ticket_and_prints_no_contents(tmp_path):
    f, pol, _, _ = live(tmp_path)
    rid = f.start()
    pol.write_text('{"token": "TRIPWIRE-SECRET-C"}\n')
    cp = f.cli("run", "finish", rid, "--output-file", str(tmp_path / "out.md"))
    assert cp.returncode == 0, cp.stderr
    reason = f"tripwire: {pol} changed during {rid}"
    fin = json.loads(cp.stdout.strip().splitlines()[-1])
    assert fin["tripwire"] == {"park": [str(pol)], "escalate": []}
    assert fin["parked"] == reason
    t = f.ticket()
    assert t["state"] == "parked" and t["parked"]["reason"] == reason and t["parked"]["outputs"] == [rid]
    assert [e["items"] for e in f.events("escalation.queued")] == [[reason]]
    changed = f.events("tripwire.changed")
    assert [(e["run"], e["park"], e["escalate"]) for e in changed] == [(rid, [str(pol)], [])]
    assert "TRIPWIRE-SECRET" not in cp.stdout + cp.stderr + f.store_text()


def test_a_deleted_and_a_created_park_file_both_count_as_changed(tmp_path):
    f, pol, new, _ = live(tmp_path)
    rid = f.start()
    pol.unlink()
    new.write_text("{}\n")
    f.finish(rid)
    assert f.ticket()["parked"]["reason"] == f"tripwire: {pol}, {new} changed during {rid}"


def test_a_killed_run_is_still_compared(tmp_path):
    f, pol, _, _ = live(tmp_path)
    rid = f.start()
    pol.write_text("x\n")
    fin = f.finish(rid, "--status-override", "KILLED")
    assert fin["status"] == "KILLED" and fin["parked"] == f"tripwire: {pol} changed during {rid}"
    assert f.ticket()["state"] == "parked"


def test_a_changed_escalate_file_is_queued_and_the_ticket_still_moves(tmp_path):
    f, _, _, pair = live(tmp_path)
    rid = f.start()
    pair.write_text('{"chat": "TRIPWIRE-SECRET-D"}\n')
    fin = f.finish(rid)
    assert fin["tripwire"] == {"park": [], "escalate": [str(pair)]} and "parked" not in fin
    assert f.ticket()["state"] == "ready-for-triage"
    queued = f.events("escalation.queued")
    assert [(e["run"], e["items"]) for e in queued] == [(rid, [f"tripwire (escalate): {pair} changed during {rid}"])]
    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    assert "TRIPWIRE-SECRET" not in f.store_text()


def test_unchanged_files_neither_park_nor_escalate(tmp_path):
    f, _, _, _ = live(tmp_path)
    fin = f.finish(f.start())
    assert fin["status"] == "ACCEPT" and fin["tripwire"] == {"park": [], "escalate": []} and "parked" not in fin
    assert f.ticket()["state"] == "ready-for-triage"
    assert f.events("escalation.queued") == [] and f.events("tripwire.changed") == []


def test_a_park_change_on_a_ticket_already_parked_is_queued_not_parked_again(tmp_path):
    f, pol, _, _ = live(tmp_path)
    rid = f.start()
    f.ok("ticket", "park", "T-0001", "--reason", "operator hold")
    pol.write_text("x\n")
    fin = f.finish(rid)
    assert "parked" not in fin and fin["tripwire"]["park"] == [str(pol)]
    assert f.ticket()["parked"]["reason"] == "operator hold"
    reason = f"tripwire: {pol} changed during {rid}"
    assert [e["items"] for e in f.events("escalation.queued")] == [["operator hold"], [reason]]
    assert len(f.events("ticket.parked")) == 1


def test_ticket_set_compares_a_dropped_run_and_not_one_still_in_flight(tmp_path):
    f, pol, _, _ = live(tmp_path)
    rid = f.start()
    pol.write_text("x\n")
    f.ok("ticket", "set", "T-0001", "title=Renamed")
    assert f.ticket()["state"] == "ready-for-triage" and f.events("tripwire.changed") == []
    out = f.ok("ticket", "set", "T-0001", "in_flight=[]")
    reason = f"tripwire: {pol} changed during {rid}"
    assert out["parked"] == reason
    assert f.ticket()["parked"]["reason"] == reason
    # compared once: a later run finish of the same run does not compare it again
    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-triage", "--by", "t")
    pol.write_text("y\n")
    assert "parked" not in f.finish(rid)
    assert f.ticket()["state"] == "ready-for-triage" and len(f.events("tripwire.changed")) == 1


def test_a_home_entry_resolves_against_the_account_home_not_HOME(tmp_path):
    name = f".tripwire-probe-{uuid.uuid4().hex}"
    account = Path(pwd.getpwuid(os.getuid()).pw_dir) / name
    assert not account.exists()  # never list a real file under the account's home
    home = tmp_path / "home"
    home.mkdir()
    (home / name).write_text("a\n")
    other = tmp_path / "live.json"
    other.write_text("a\n")
    f = Inst(tmp_path, f'tripwire: {{park: ["~/{name}", {other}]}}')
    f.env["HOME"] = str(home)
    rid = f.start()
    base = (f.store / "runs" / rid / "tripwire.yaml").read_text()
    assert str(account) in base and str(home) not in base
    (home / name).write_text("b\n")
    other.write_text("b\n")
    f.finish(rid, "--status-override", "KILLED")
    assert f.ticket()["parked"]["reason"] == f"tripwire: {other} changed during {rid}"
    assert not account.exists()


def test_a_directory_refuses_run_start_and_records_no_run(tmp_path):
    d = tmp_path / "live"
    d.mkdir()
    f = Inst(tmp_path, f"tripwire: {{park: [{d}]}}")
    cp = f.cli("run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 2 and str(d) in cp.stderr and "tripwire" in cp.stderr
    assert not (f.store / "runs").exists() or not any((f.store / "runs").iterdir())
    assert f.ticket()["in_flight"] == []


def test_a_bad_list_refuses_run_start(tmp_path):
    for i, bad in enumerate(["tripwire: {park: [relative/file.json]}", "tripwire: {watch: []}",
                             "tripwire: [a]", "tripwire: {park: [1]}"]):
        (tmp_path / str(i)).mkdir()
        f = Inst(tmp_path / str(i), bad)
        cp = f.cli("run", "start", "--role", "triage", "--ticket", "T-0001")
        assert cp.returncode == 2 and "tripwire" in cp.stderr, (bad, cp.stderr)
        assert not (f.store / "runs").exists() or not any((f.store / "runs").iterdir())


def test_the_baseline_is_kept_once_and_never_committed(tmp_path):
    f, _, _, _ = live(tmp_path)
    f.start()
    digest = hashlib.sha256(SECRET.encode()).hexdigest()
    holders = [p for p in f.store.rglob("*") if p.is_file() and digest in p.read_text(errors="replace")]
    assert [p.name for p in holders] == ["tripwire.yaml"]
    subprocess.run(["git", "-C", str(f.store), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(f.store), "add", "-A"], check=True)
    staged = subprocess.run(["git", "-C", str(f.store), "grep", "--cached", "-l", digest],
                            capture_output=True, text=True)
    assert staged.stdout == ""


def test_no_tripwire_key_writes_and_prints_what_it_did_before(tmp_path):
    f = Inst(tmp_path, None)
    rid = f.start()
    fin = f.finish(rid)
    assert sorted(fin) == ["confidence", "escalations", "ok", "run_id", "status"]
    assert sorted(p.name for p in (f.store / "runs" / rid).iterdir()) == ["meta.yaml", "output.md", "scratch", "system-prompt.txt"]
    assert "runs/*/scratch/" in (f.store / ".gitignore").read_text().splitlines()


def test_empty_lists_are_off(tmp_path):
    f = Inst(tmp_path, "tripwire: {park: [], escalate: []}")
    rid = f.start()
    assert "tripwire" not in f.finish(rid)
    assert not (f.store / "runs" / rid / "tripwire.yaml").exists()
