"""One task, shepherded through the factory end to end.

Each story below reads as rows of the design doc's routing table (docs/spec-factory.md
§Routing table): a role is dispatched, we look at what it received, it answers (a stub file
under fixtures/stubs/<case>/<role>-<n>.md, the same files the Workflow dispatcher uses in stub
mode), and the dispatcher routes on its STATUS. The human steps are the two gates and the
answers to questions.

The real dispatcher is factory/workflows/intake.js, a Workflow script that needs the Claude Code
agent runtime, so it cannot run under pytest. `Shepherd` at the bottom applies the same routing
table to the same store CLI; if the two ever disagree, the table in the design doc decides.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
STUBS = Path(__file__).resolve().parent / "fixtures" / "stubs"
MAX_SPEC_ROUNDS = 2  # factory/config.yaml max_rounds.spec


# ----- the stories --------------------------------------------------------------------------

def test_a_feature_request_becomes_current_truth(tmp_path):
    """Request → Triage ACCEPT → Spec writer → Critic APPROVE → human gate → Planner → archive."""
    f = Shepherd(tmp_path, case="accept-approve")
    f.human_runs("init")  # the store keeps specs in the OpenSpec tree from the start
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    assert f.state(tid) == "ready-for-triage"

    # | New request | — | Triage | The request, ticket search |
    triage = f.dispatch("triage", tid)
    assert "The bot should do the thing." in triage.input
    assert triage.status == "ACCEPT"
    assert f.state(tid) == "ready-for-spec-writer"
    assert f.ticket(tid)["title"] == "Fix thing"  # Triage's title becomes the ticket's

    # | Triage | ACCEPT | Spec writer | The ticket; current truth, read-only |
    writer = f.dispatch("spec_writer", tid)
    assert "Title: Fix thing" in writer.input and "The bot should do the thing." in writer.input
    assert writer.sources == [f"runs/{triage.run_id}/output.md", f"requests/{tid}.md"]  # no truth yet
    assert writer.status == "READY-FOR-CRITIC"
    assert f.state(tid) == "ready-for-critic" and f.ticket(tid)["spec"]["version"] == 1

    # | Spec writer | READY-FOR-CRITIC | Critic | Spec, repo and current truth read-only |
    critic = f.dispatch("critic", tid)
    assert critic.sources == [f"specs/{tid}/v1.md"]
    assert "### Requirement: the-thing" in critic.input
    assert critic.status == "APPROVE"
    assert f.state(tid) == "awaiting-spec-gate"

    # | Human spec gate | Approved | Planner | The pinned spec |  — the gate writes the change folder
    f.human_approves(tid)
    assert f.state(tid) == "ready-for-planner"
    change = f.store / "openspec" / "changes" / tid
    assert sorted(p.name for p in change.iterdir()) == ["design.md", "proposal.md", "specs", "verification.md"]
    assert "round 1 · spec v1" in (change / "verification.md").read_text()  # the critic's round rides along
    assert list((f.store / "openspec" / "specs").iterdir()) == []  # current truth is untouched until archive

    # | Planner | PLANNED | sub-tickets | The approved spec (pinned) |  — its output is the change's tasks.md
    planner = f.dispatch("planner", tid)
    assert planner.sources == [f"specs/{tid}/v1.md"]
    assert planner.status == "PLANNED"
    assert f.state(tid) == "planned"
    assert (change / "tasks.md").read_text().startswith("# Plan: T-0001")
    assert "STATUS:" not in (change / "tasks.md").read_text()

    # | Merge gate | parent-close VERIFIED | archive, then closed |  — the PR loop is a later build item;
    # here the human stands in for it and archives.
    f.human_runs("archive", tid)
    truth = (f.store / "openspec" / "specs" / "thing" / "spec.md").read_text()
    assert "### Requirement: the-thing" in truth and "#### Scenario: asked once" in truth
    assert not change.exists() and any(p.name.endswith(f"-{tid}") for p in (f.store / "openspec" / "changes" / "archive").iterdir())
    assert (f.store / "decisions.md").read_text().strip().endswith(f"{tid} The thing is done the simple way.")

    # The next ticket's writer starts from what the first one established.
    tid2 = f.request("# SPEC-98: Another\n\nAlso the thing, differently.\n")
    f.dispatch("triage", tid2, stub="accept-approve/triage-1.md")
    writer2 = f.dispatch("spec_writer", tid2, stub="accept-approve/spec_writer-1.md", finish=False)
    assert "openspec/specs/thing/spec.md" in writer2.sources
    assert "### Requirement: the-thing" in writer2.input

    # The log tells the same story, in order.
    events = [e["event"] for e in f.log() if e.get("ticket") == tid]
    assert events[:2] == ["request.created", "ticket.created"]
    assert events.index("approval.recorded") < events.index("change.pinned") < events.index("tasks.written") < events.index("change.archived")


def test_a_question_goes_to_the_human_and_comes_back_with_the_asker_s_context(tmp_path):
    """Triage CLARIFY → requester answers → Triage ACCEPT → writer NEEDS-HUMAN → operator answers →
    writer → Critic REVISE → writer round 2 → Critic APPROVE → gate."""
    f = Shepherd(tmp_path, case="question")
    f.human_runs("init")
    tid = f.request("# SPEC-97: Unclear\n\nThe thing, somewhere.\n")

    # | Triage | CLARIFY | requester | the question |
    t1 = f.dispatch("triage", tid)
    assert t1.status == "CLARIFY" and f.state(tid) == "waiting-requester"

    # | requester | answers | Triage | the request with the answer, Triage's previous output |
    f.human_answers(tid, "macOS 14\n")
    t2 = f.dispatch("triage", tid)
    assert "macOS 14" in t2.input and "- which OS" in t2.input  # the answer, read against the question
    assert t2.sources == [f"requests/{tid}.md", f"runs/{t1.run_id}/output.md"]
    assert t2.status == "ACCEPT"

    # | Spec writer | NEEDS-HUMAN | Human queue | the draft with its open question |
    w1 = f.dispatch("spec_writer", tid)
    assert w1.status == "NEEDS-HUMAN" and f.state(tid) == "parked"
    assert f.ticket(tid)["parked"]["reason"] == "NEEDS-HUMAN from spec writer"
    assert (f.store / "specs" / tid / "v1.md").exists()  # the draft is kept as a version

    # | Human queue | Answered (Spec writer asked) | Spec writer | the ticket, the answer, the writer's previous output |
    f.human_answers(tid, "B.\n")
    assert f.state(tid) == "ready-for-spec-writer"
    w2 = f.dispatch("spec_writer", tid)
    assert "B." in w2.input and "- A or B?" in w2.input
    assert f"runs/{w1.run_id}/output.md" in w2.sources
    assert w2.status == "READY-FOR-CRITIC" and f.ticket(tid)["spec"]["version"] == 2

    # | Critic | REVISE | Spec writer (round +1) | findings, the spec version they apply to |
    c1 = f.dispatch("critic", tid)
    assert c1.status == "REVISE" and f.state(tid) == "ready-for-spec-writer"
    assert f.ticket(tid)["round"]["spec"] == 2

    # | Spec writer | READY-FOR-CRITIC (round 2) | Critic | the new version; round 2+: prior findings, responses, previous version |
    w3 = f.dispatch("spec_writer", tid)
    assert "FIXTURE-FINDING-ONE" in w3.input and "A. do the thing the B way" in w3.input
    assert w3.status == "READY-FOR-CRITIC" and f.ticket(tid)["spec"]["version"] == 3
    c2 = f.dispatch("critic", tid)
    assert c2.sources == [f"specs/{tid}/v3.md", f"runs/{c1.run_id}/output.md", f"specs/{tid}/v2.md"]
    assert "## Responses" in c2.input and "FIXTURE-FINDING-ONE" in c2.input
    assert c2.status == "APPROVE" and f.state(tid) == "awaiting-spec-gate"

    f.human_approves(tid)
    assert f.ticket(tid)["spec"]["approved_version"] == 3
    v = (f.store / "openspec" / "changes" / tid / "verification.md").read_text()
    assert v.count("round ") == 2 and "FIXTURE-FINDING-ONE" in v  # both critic rounds are on the record


def test_the_critic_loop_stops_at_the_round_limit(tmp_path):
    """Two REVISE rounds and the ticket parks for the human; it never loops."""
    f = Shepherd(tmp_path, case="revise-twice")
    tid = f.request("# SPEC-96: Hard\n\nThe hard thing.\n")
    f.dispatch("triage", tid)
    for rnd in range(1, MAX_SPEC_ROUNDS + 1):
        f.dispatch("spec_writer", tid)
        c = f.dispatch("critic", tid)
        assert c.status == "REVISE"
        expected_round = rnd + 1 if rnd < MAX_SPEC_ROUNDS else MAX_SPEC_ROUNDS  # +1 per REVISE, never past the limit
        assert f.ticket(tid)["round"]["spec"] == expected_round
    assert f.state(tid) == "parked" and f.ticket(tid)["parked"]["reason"] == "max rounds"
    # | parked (max rounds) | human | amend and re-plan, or close |
    f.human_runs("resolve", tid, "--close")
    assert f.state(tid) == "closed"


def test_a_request_the_factory_should_not_take_is_closed_by_triage(tmp_path):
    f = Shepherd(tmp_path, case="reject")
    tid = f.request("# SPEC-95: Old\n\nSuperseded upstream.\n")
    t = f.dispatch("triage", tid)
    assert t.status == "REJECT" and f.state(tid) == "closed"


def test_the_gate_refuses_a_delta_that_does_not_fit_current_truth(tmp_path):
    """Two tickets ADD the same requirement; the second cannot pin after the first archives."""
    f = Shepherd(tmp_path, case="accept-approve")
    f.human_runs("init")
    first = f.request("# SPEC-94: First\n\nThe thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, first, stub=f"accept-approve/{role}-1.md")
    f.human_approves(first)
    f.human_runs("archive", first)
    second = f.request("# SPEC-93: Second\n\nThe thing again.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, second, stub=f"accept-approve/{role}-1.md")
    cp = f.cli("approve-spec", second)
    assert cp.returncode == 2 and "ADDED 'the-thing' is already in current truth" in cp.stderr
    assert f.state(second) == "awaiting-spec-gate"  # nothing moved; the human amends or closes


# ----- the shepherd: the routing table applied to the store CLI ----------------------------------

class Run:
    def __init__(self, run_id: str, input_text: str, sources: list[str], status: str | None):
        self.run_id, self.input, self.sources, self.status = run_id, input_text, sources, status


class Shepherd:
    def __init__(self, tmp_path: Path, case: str):
        self.store = tmp_path / "state"
        self.case = case
        self.tmp = tmp_path
        self.count: dict[str, int] = {}

    # --- the store CLI, as the clerk runs it
    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "FACTORY_STATE": str(self.store), "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def ticket(self, tid: str) -> dict:
        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())

    def state(self, tid: str) -> str:
        return self.ticket(tid)["status"]

    def log(self) -> list[dict]:
        return [json.loads(ln) for p in sorted((self.store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]

    # --- the humans
    def request(self, text: str) -> str:
        p = self.tmp / f"request-{len(list(self.tmp.glob('request-*.md'))) + 1}.md"
        p.write_text(text)
        return self.ok("ticket", "new", "--file", str(p))["id"]

    def human_runs(self, *argv: str) -> dict:
        return self.ok(*argv)

    def human_approves(self, tid: str) -> None:
        self.ok("approve-spec", tid)

    def human_answers(self, tid: str, text: str) -> None:
        p = self.tmp / f"answer-{tid}-{self.ticket(tid)['history'].__len__()}.md"
        p.write_text(text)
        self.ok("resolve", tid, "--answer", str(p))

    # --- one role run, then the routing table's row for its STATUS (as intake.js does)
    def dispatch(self, role: str, tid: str, stub: str | None = None, finish: bool = True) -> Run:
        self.count[role] = self.count.get(role, 0) + 1
        stub_path = STUBS / (stub or f"{self.case}/{role}-{self.count[role]}.md")
        rid = self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]
        composed = self.ok("run", "compose", rid)
        input_text = (self.store / "runs" / rid / "input.md").read_text()
        if not finish:
            return Run(rid, input_text, composed["sources"], None)
        (self.store / "runs" / rid / "output.md").write_text(stub_path.read_text())
        status = self.ok("run", "finish", rid)["status"]
        self.route(role, tid, rid, status)
        return Run(rid, input_text, composed["sources"], status)

    def route(self, role: str, tid: str, rid: str, status: str) -> None:
        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
        park = lambda reason: self.ok("ticket", "park", tid, "--reason", reason, "--outputs", rid)  # noqa: E731
        if role == "triage":
            {"ACCEPT": lambda: go("ready-for-spec-writer"), "REJECT": lambda: go("closed"),
             "CLARIFY": lambda: go("waiting-requester"), "NEEDS-HUMAN": lambda: park("NEEDS-HUMAN from triage")}[status]()
        elif role == "spec_writer":
            self.ok("spec", "add", tid, "--from-run", rid)  # every version the writer returns is kept
            if status == "NEEDS-HUMAN":
                park("NEEDS-HUMAN from spec writer")
            else:
                assert status in ("READY-FOR-CRITIC", "NEEDS-SPLIT"), status
                go("ready-for-critic", "spec:init")
        elif role == "critic":
            if status == "APPROVE":
                go("awaiting-spec-gate")
            elif status == "ESCALATE":
                park("ESCALATE from critic")
            else:
                assert status == "REVISE", status
                if self.ticket(tid)["round"]["spec"] < MAX_SPEC_ROUNDS:
                    go("ready-for-spec-writer", "spec:+1")
                else:
                    park("max rounds")
        elif role == "planner":
            if status == "PLANNED":
                self.ok("spec", "tasks", tid, "--run", rid)
                self.ok("plan", "add", tid, "--from-run", rid)
                go("planned")
            else:
                park(f"{status} from planner")
