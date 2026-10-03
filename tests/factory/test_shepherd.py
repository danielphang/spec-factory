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
MAX_PR_ROUNDS = 2  # factory/config.yaml max_rounds.pr


# ----- the stories --------------------------------------------------------------------------

def test_a_feature_request_becomes_an_approved_planned_change(tmp_path):
    """Request → Triage ACCEPT → Spec writer → Critic APPROVE → human gate → Planner PLANNED."""
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

    # The plan became a sub-ticket; from here the ticket's life is the build half (next story but one).
    assert f.state(f"{tid}.1") == "ready-for-implementer"
    events = [e["event"] for e in f.log() if e.get("ticket") == tid]
    assert events[:2] == ["request.created", "ticket.created"]
    assert events.index("approval.recorded") < events.index("change.pinned") < events.index("tasks.written")

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


def test_the_planned_ticket_is_built_checked_merged_and_archived(tmp_path):
    """Planner PLANNED → sub-ticket → Implementer READY-FOR-REVIEW → Reviewer APPROVE + Verifier
    VERIFIED on the same head → merge gate (gate suite PASS, local --no-ff merge) → every sub-ticket
    merged → parent-close Verifier on the integration branch → archive → closed.

    Local-commit stand-in: no remote, no CI; the gate suite result is the verifier's `Gate suite:` line."""
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)

    # | Planner | PLANNED | Implementer, one run per sub-ticket. Each branches from main at dispatch |
    planner = f.dispatch("planner", tid)
    assert planner.status == "PLANNED" and f.state(tid) == "planned"
    st = f"{tid}.1"
    assert f.state(st) == "ready-for-implementer"
    assert f.ticket(st)["parent"] == tid and f.ticket(st)["depends_on"] == []
    assert (f.store / "specs" / st / "subticket.md").read_text().startswith(f"{st} / Do the thing")
    assert f.ready_implementers(tid) == [st]

    # | Implementer | READY-FOR-REVIEW | Gate runner, Reviewer, and Verifier, all on the same head |
    main_at_dispatch = f.repo_rev("main")
    impl = f.dispatch("implementer", st)
    assert yaml.safe_load((f.store / "runs" / impl.run_id / "meta.yaml").read_text())["environment_files"] == []  # target has no uv.lock
    ignore = (f.store / ".gitignore").read_text().splitlines()
    assert "worktrees/" in ignore and "runs/*/wt/" in ignore  # nested checkouts never ride along with the store
    assert "Sub-ticket T-0001.1" in impl.input and "### Requirement: the-thing" in impl.input
    assert "There is no remote" in impl.input
    assert f.git("merge-base", "main", f"factory/{st}").strip() == main_at_dispatch  # branched from main at dispatch
    assert impl.status == "READY-FOR-REVIEW" and f.state(st) == "checks-in-flight"
    head = f.ticket(st)["head"]
    assert head != f.repo_rev("main")  # the implementer committed on its branch
    assert f.repo_rev(f"factory/{st}") == head

    # | Reviewer | APPROVE | Results table, keyed to head |  | Verifier | VERIFIED | Results table, keyed to head |
    rev = f.dispatch("reviewer", st)
    assert "+the thing" in rev.input and "PR description" in rev.input  # the diff and the implementer's description
    ver = f.dispatch("verifier", st)
    assert f"head `{head}`" in ver.input
    assert f.results(st) == {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}
    assert rev.status == "APPROVE" and ver.status == "VERIFIED"

    # | Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main | Merge |
    assert f.state(st) == "merged"
    assert f.repo_rev("main") == f.ticket(st)["merge"]["main_after"] and f.repo_rev("main") != f.ticket(st)["merge"]["base_before"]
    assert (f.repo / "thing.txt").read_text() == "the thing\n"  # main is checked out here, so the merge lands in the working tree
    assert f.git("show", "main:thing.txt").strip() == "the thing"
    assert f.ticket(tid)["parent_base"] == f.ticket(st)["merge"]["base_before"]

    # | When all sub-tickets have merged | one verifier run on main against the parent's full Acceptance list |
    assert f.parent_check(tid) == "ready-for-parent-verify"
    cp = f.cli("archive", tid)  # current truth does not change before the parent-close run says VERIFIED
    assert cp.returncode == 2 and "no VERIFIED parent-close verifier run" in cp.stderr
    close = f.dispatch("verifier", tid)
    assert "verify every scenario on main" in close.input and close.status == "VERIFIED"
    # | VERIFIED archives the change (Spec store), then closes the parent |
    assert f.state(tid) == "closed"
    truth = (f.store / "openspec" / "specs" / "thing" / "spec.md").read_text()
    assert "### Requirement: the-thing" in truth and "#### Scenario: asked once" in truth
    change = f.store / "openspec" / "changes" / tid
    assert not change.exists() and any(p.name.endswith(f"-{tid}") for p in (f.store / "openspec" / "changes" / "archive").iterdir())
    assert (f.store / "decisions.md").read_text().strip().endswith(f"{tid} The thing is done the simple way.")
    events = [e["event"] for e in f.log() if e.get("ticket") in (tid, st)]
    assert events.index("merge.done") < events.index("change.archived")

    # The next ticket's writer starts from what this one established.
    tid2 = f.request("# SPEC-98: Another\n\nAlso the thing, differently.\n")
    f.dispatch("triage", tid2, stub="accept-approve/triage-1.md")
    writer2 = f.dispatch("spec_writer", tid2, stub="accept-approve/spec_writer-1.md", finish=False)
    assert "openspec/specs/thing/spec.md" in writer2.sources and "### Requirement: the-thing" in writer2.input


def test_a_merge_waits_for_every_checker_and_refuses_a_red_gate(tmp_path):
    """The merge gate reads the results table, not the dispatcher's mood: a missing or red row is a refusal."""
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    f.dispatch("planner", tid)
    st = f"{tid}.1"
    f.dispatch("implementer", st)
    cp = f.cli("merge", st)
    assert cp.returncode == 2 and "ci is missing" in cp.stderr
    cp = f.cli("results", "record", st, "--head", "undefined", "--role", "reviewer", "--output", str(f.tmp / "request-1.md"))
    assert cp.returncode == 2 and "full commit SHA" in cp.stderr and not (f.store / "results" / "undefined").exists()
    f.dispatch("reviewer", st)
    red = f.tmp / "red.md"
    red.write_text("Commit: HEAD\nPer criterion: none\nGate suite: FAIL\n  1 failed\nSTATUS: FAILED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    assert f.last_join["decision"] == "wait" and f.last_join["missing"] == ["verifier", "ci"]  # the join waits for every row
    ver = f.dispatch("verifier", st, stub_path=red, route=False)
    head = f.ticket(st)["head"]
    f.ok("results", "record", st, "--head", head, "--role", "verifier", "--output", str(f.store / "runs" / ver.run_id / "output.md"), "--run", ver.run_id)
    assert f.results(st) == {"reviewer": "APPROVE", "verifier": "FAILED", "ci": "FAIL"}
    cp = f.cli("merge", st)  # the gate reads the table: APPROVE is not enough when ci and the verifier are red
    assert cp.returncode == 2 and "ci is FAIL" in cp.stderr and f.repo_rev("main") != head
    join = f.act_on_join(st)
    assert join["decision"] == "revise" and "verifier FAILED" in join["reason"]
    assert f.state(st) == "ready-for-implementer" and f.ticket(st)["round"]["pr"] == 2  # round +1, back to the implementer
    # the implementer's next input carries both checkers' outputs and the gate result for that head
    rid = f.ok("run", "start", "--role", "implementer", "--ticket", st)["run_id"]
    f.ok("run", "compose", rid)
    inp = (f.store / "runs" / rid / "input.md").read_text()
    assert "Reviewer findings on your previous head" in inp and "Verifier findings on your previous head" in inp
    assert "Gate suite on your previous head" in inp and "FAIL" in inp


def test_a_second_sibling_gets_a_conflict_run_that_says_why_and_merges_after_it(tmp_path):
    """Two parallel-safe siblings: the first merges; the second's head no longer contains main, so the
    merge gate refuses, the implementer is told why, merges main into its branch, and the checks re-run."""
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    plan = f.tmp / "plan.md"
    plan.write_text("## ST-1 / First\n**Depends on:** none\n**Parallel-safe:** yes\n\n## ST-2 / Second\n**Depends on:** none\n**Parallel-safe:** yes\n\n"
                    "Coverage map: asked once → ST-1\nSTATUS: PLANNED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    f.dispatch("planner", tid, stub_path=plan)
    a, b = f"{tid}.1", f"{tid}.2"
    assert f.ready_implementers(tid) == [a, b]
    f.dispatch("implementer", a, stub="accept-approve/implementer-1.md", file="a.txt")
    f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", file="b.txt")
    for st in (a, b):
        f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
        f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
    assert f.state(a) == "merged"
    # b was green too, but main moved: the gate refused, and the join calls it a conflict run (same round)
    assert f.last_join["decision"] == "conflict" and f.state(b) == "ready-for-implementer" and f.ticket(b)["round"]["pr"] == 1
    assert f.git("show", "main:a.txt").strip() == "the thing"
    impl = f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", merge_main=True)
    assert "This is a conflict run" in impl.input and "head does not contain main" in impl.input
    assert f.ticket(b).get("merge_refused") is None  # cleared once the new head contains main
    f.dispatch("reviewer", b, stub="accept-approve/reviewer-1.md")
    f.dispatch("verifier", b, stub="accept-approve/verifier-1.md")
    assert f.state(b) == "merged" and f.git("show", "main:b.txt").strip() == "the thing"
    assert f.parent_check(tid) == "ready-for-parent-verify"


def test_an_unknown_checker_status_parks_as_a_harness_bug_not_a_failed_round(tmp_path):
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    f.dispatch("planner", tid)
    st = f"{tid}.1"
    f.dispatch("implementer", st)
    odd = f.tmp / "odd.md"
    odd.write_text("Commit: HEAD\nFindings: none\nSTATUS: LGTM\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    f.dispatch("reviewer", st, stub_path=odd)
    f.dispatch("verifier", st)
    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"] == "harness-bug: unknown STATUS LGTM from reviewer"
    assert f.ticket(st)["round"]["pr"] == 1  # not counted as a round
    # a result that names another commit is refused outright
    cp = f.cli("results", "record", st, "--head", f.ticket(st)["head"], "--role", "reviewer", "--output", str(f.tmp / "wrong.md"))
    (f.tmp / "wrong.md").write_text("Commit: 0123456789abcdef\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n")
    cp = f.cli("results", "record", st, "--head", f.ticket(st)["head"], "--role", "reviewer", "--output", str(f.tmp / "wrong.md"))
    assert cp.returncode == 2 and "not the head" in cp.stderr


def test_two_merges_at_once_are_serialised_and_leave_the_checkout_clean(tmp_path):
    import threading
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    plan = f.tmp / "plan.md"
    plan.write_text("## ST-1 / First\n**Depends on:** none\n**Parallel-safe:** yes\n\n## ST-2 / Second\n**Depends on:** none\n**Parallel-safe:** yes\n\n"
                    "STATUS: PLANNED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    f.dispatch("planner", tid, stub_path=plan)
    a, b = f"{tid}.1", f"{tid}.2"
    f.dispatch("implementer", a, stub="accept-approve/implementer-1.md", file="a.txt")
    f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", file="b.txt")
    for st in (a, b):  # record green rows on both heads without routing, then race the two merges
        for role in ("reviewer", "verifier"):
            r = f.dispatch(role, st, stub=f"accept-approve/{role}-1.md", route=False)
            f.ok("results", "record", st, "--head", f.ticket(st)["head"], "--role", role, "--output", str(f.store / "runs" / r.run_id / "output.md"))
    codes: dict[str, subprocess.CompletedProcess] = {}
    threads = [threading.Thread(target=lambda s=s: codes.__setitem__(s, f.cli("merge", s))) for s in (a, b)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    won = [s for s in (a, b) if codes[s].returncode == 0]
    lost = [s for s in (a, b) if codes[s].returncode != 0]
    assert len(won) == 1 and len(lost) == 1, {s: codes[s].stderr for s in codes}
    assert "head does not contain main" in codes[lost[0]].stderr  # a conflict run, not a git lock error
    assert f.git("status", "--porcelain").strip() == ""  # the integration checkout is consistent
    assert f.state(won[0]) == "merged"


def test_a_planned_parent_can_be_parked_and_a_closed_sibling_is_reported(tmp_path):
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    f.dispatch("planner", tid)
    st = f"{tid}.1"
    f.human_runs("resolve", st, "--close")
    r = f.ok("ticket", "ready-implementers", tid)
    assert r["ready"] == [] and r["closed"] == [st]
    # | a sub-ticket closed by the human parks the parent |
    f.ok("ticket", "park", tid, "--reason", f"sub-ticket closed by a human: {st}")
    assert f.state(tid) == "parked"


def built_to_implementer(tmp_path, plan: str | None = None):
    """A ticket approved, planned and split; returns the shepherd, the parent id and its sub-ticket ids."""
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    if plan:
        p = f.tmp / "plan.md"
        p.write_text(plan + "STATUS: PLANNED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
        f.dispatch("planner", tid, stub_path=p)
    else:
        f.dispatch("planner", tid)
    return f, tid, list(f.ok("ticket", "parent-check", tid)["subtickets"])


TWO_PARALLEL = "## ST-1 / First\n**Depends on:** none\n**Parallel-safe:** yes\n\n## ST-2 / Second\n**Depends on:** none\n**Parallel-safe:** yes\n\n"
CHAIN = "## ST-1 / First\n**Depends on:** none\n**Parallel-safe:** yes\n\n## ST-2 / Second\n**Depends on:** ST-1\n**Parallel-safe:** yes\n\n"
REQUEST_CHANGES = "Commit: HEAD\nFindings: [BLOCKING] thing.txt:1: FINDING-ROUND-{n} → wrong\nSTATUS: REQUEST-CHANGES\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"
FAILED = "Commit: HEAD\nPer criterion: NEW | x | base: FAIL | PR: FAIL | FAIL VERIFIER-ROUND-{n}\nGate suite: PASS\nSTATUS: FAILED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"


def test_a_conflict_run_that_never_merges_main_parks_after_two_tries(tmp_path):
    f, tid, (a, b) = built_to_implementer(tmp_path, TWO_PARALLEL)
    f.dispatch("implementer", a, stub="accept-approve/implementer-1.md", file="a.txt")
    f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", file="b.txt")
    for st in (a, b):
        f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
        f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
    assert f.state(a) == "merged" and f.state(b) == "ready-for-implementer" and f.ticket(b)["conflict_runs"] == 0
    runs_before = len(list((f.store / "runs").iterdir()))
    f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", no_change=True)  # returns without merging main
    assert f.last_join["decision"] == "conflict" and f.state(b) == "ready-for-implementer" and f.ticket(b)["conflict_runs"] == 1
    assert f.ok("ticket", "head", b)["conflict_runs"] == 1  # asking again does not count the same run twice
    f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", no_change=True)
    assert f.state(b) == "parked" and "still does not contain main after 2 conflict runs" in f.ticket(b)["parked"]["reason"]
    assert len(list((f.store / "runs").iterdir())) == runs_before + 2  # no checker ran on a head the gate would refuse
    assert f.ticket(b)["round"]["pr"] == 1  # a conflict run is not a round


def test_a_killed_checker_parks_as_a_budget_kill_and_the_round_does_not_move(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path)
    f.dispatch("implementer", st)
    f.dispatch("reviewer", st)
    f.dispatch("verifier", st, killed=True)
    assert f.results(st) == {"reviewer": "APPROVE", "verifier": "KILLED"}  # a killed verifier writes no ci row
    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"] == "budget kill: verifier"
    assert f.ticket(st)["round"]["pr"] == 1


def test_the_pr_loop_stops_at_the_round_limit_and_each_round_sees_the_previous_round_only(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path)
    red = {}
    for n in (1, 2):
        for role, body in (("reviewer", REQUEST_CHANGES), ("verifier", FAILED)):
            red[role, n] = f.tmp / f"{role}-{n}.md"
            red[role, n].write_text(body.format(n=n))
    f.dispatch("implementer", st)
    f.dispatch("reviewer", st, stub_path=red["reviewer", 1])
    f.dispatch("verifier", st, stub_path=red["verifier", 1])
    assert f.state(st) == "ready-for-implementer" and f.ticket(st)["round"]["pr"] == 2
    impl2 = f.dispatch("implementer", st, stub="accept-approve/implementer-1.md", file="second.txt")
    assert "FINDING-ROUND-1" in impl2.input and "VERIFIER-ROUND-1" in impl2.input and "Gate suite on your previous head" in impl2.input
    rev2 = f.dispatch("reviewer", st, stub_path=red["reviewer", 2])
    assert "Your prior findings (round 1)" in rev2.input and "FINDING-ROUND-1" in rev2.input and "VERIFIER-ROUND-1" in rev2.input
    ver2 = f.dispatch("verifier", st, stub_path=red["verifier", 2])
    # the verifier composes after the round-2 reviewer finished: it must still get round 1's findings, not round 2's
    assert "The reviewer's prior findings (round 1)" in ver2.input and "FINDING-ROUND-1" in ver2.input and "FINDING-ROUND-2" not in ver2.input
    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"].startswith("max-round cutoff")
    assert f.ticket(st)["round"]["pr"] == 2


def test_a_dependant_is_released_when_its_dependency_merges(tmp_path):
    f, tid, (a, b) = built_to_implementer(tmp_path, CHAIN)
    assert f.state(b) == "waiting-dependencies" and f.ready_implementers(tid) == [a]
    cp = f.cli("run", "start", "--role", "implementer", "--ticket", b)
    assert cp.returncode == 2 and "waiting-dependencies, not ready-for-implementer" in cp.stderr
    f.dispatch("implementer", a, stub="accept-approve/implementer-1.md", file="a.txt")
    cp = f.cli("run", "start", "--role", "implementer", "--ticket", a)
    assert cp.returncode == 2 and "checks-in-flight, not ready-for-implementer" in cp.stderr
    f.dispatch("reviewer", a, stub="accept-approve/reviewer-1.md")
    f.dispatch("verifier", a, stub="accept-approve/verifier-1.md")
    assert f.state(a) == "merged" and f.state(b) == "ready-for-implementer" and f.ready_implementers(tid) == [b]
    impl = f.dispatch("implementer", b, stub="accept-approve/implementer-1.md", file="b.txt")
    assert f.git("merge-base", "--is-ancestor", f.ticket(a)["merge"]["main_after"], f"factory/{b}") == ""  # b branched from main after a merged
    assert impl.status == "READY-FOR-REVIEW"


def test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_run(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path)
    cp = f.cli("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
    assert cp.returncode == 2 and "closes after a VERIFIED parent-close run" in cp.stderr and f.state(tid) == "planned"
    f.dispatch("implementer", st)
    f.dispatch("reviewer", st)
    f.dispatch("verifier", st)
    assert f.parent_check(tid) == "ready-for-parent-verify"
    cp = f.cli("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
    assert cp.returncode == 2 and f.state(tid) == "ready-for-parent-verify"
    bad = f.tmp / "failed.md"
    bad.write_text("Commit: HEAD\nGate suite: FAIL\nSTATUS: FAILED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    f.dispatch("verifier", tid, stub_path=bad)
    # | parent-close FAILED | parks the parent: the human amends the spec and re-plans, or closes |
    assert f.state(tid) == "parked" and f.ticket(tid)["parked"]["reason"] == "FAILED from parent-close verifier"
    assert list((f.store / "openspec" / "specs").iterdir()) == []  # current truth untouched
    f.human_runs("resolve", tid, "--close")  # the human's own close is always available
    assert f.state(tid) == "closed"


def test_a_sibling_refused_three_times_and_fixed_each_time_still_merges(tmp_path):
    """The last of four parallel siblings can be refused once per sibling that merges ahead of it.
    The bound is on conflict runs that fail to fix the branch, not on refusals."""
    four = "".join(f"## ST-{n} / File {n}\n**Depends on:** none\n**Parallel-safe:** yes\n\n" for n in (1, 2, 3, 4))
    f, tid, (a, b, c, d) = built_to_implementer(tmp_path, four)
    for st, name in ((a, "a.txt"), (b, "b.txt"), (c, "c.txt"), (d, "d.txt")):
        f.dispatch("implementer", st, stub="accept-approve/implementer-1.md", file=name)
    for st in (a, b, c, d):
        f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
        f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
    assert [f.state(x) for x in (a, b, c, d)] == ["merged"] + ["ready-for-implementer"] * 3  # refusal 1 for b, c, d
    for ahead in (b, c):  # d fixes its branch, but a sibling merges before d's checks finish: refusals 2 and 3
        f.dispatch("implementer", d, stub="accept-approve/implementer-1.md", merge_main=True)
        f.dispatch("reviewer", d, stub="accept-approve/reviewer-1.md")
        f.dispatch("implementer", ahead, stub="accept-approve/implementer-1.md", merge_main=True)
        f.dispatch("reviewer", ahead, stub="accept-approve/reviewer-1.md")
        f.dispatch("verifier", ahead, stub="accept-approve/verifier-1.md")
        assert f.state(ahead) == "merged"
        f.dispatch("verifier", d, stub="accept-approve/verifier-1.md")
        assert f.state(d) == "ready-for-implementer" and f.last_join["decision"] == "conflict"
    f.dispatch("implementer", d, stub="accept-approve/implementer-1.md", merge_main=True)
    f.dispatch("reviewer", d, stub="accept-approve/reviewer-1.md")
    f.dispatch("verifier", d, stub="accept-approve/verifier-1.md")
    assert f.state(d) == "merged" and f.ticket(d)["round"]["pr"] == 1
    assert [f.git("show", f"main:{n}").strip() for n in ("a.txt", "b.txt", "c.txt", "d.txt")] == ["the thing"] * 4
    assert f.parent_check(tid) == "ready-for-parent-verify"


def test_a_killed_reviewer_parks_and_a_second_implementer_run_on_one_branch_is_refused(tmp_path):
    f, tid, (st,) = built_to_implementer(tmp_path)
    rid = f.ok("run", "start", "--role", "implementer", "--ticket", st)["run_id"]
    cp = f.cli("run", "start", "--role", "implementer", "--ticket", st)  # never two implementer runs on one branch
    assert cp.returncode == 2 and f"already has run {rid} in flight" in cp.stderr
    f.ok("run", "finish", rid, "--status-override", "KILLED")
    assert f.ticket(st)["in_flight"] == []
    f.dispatch("implementer", st)
    f.dispatch("reviewer", st, killed=True)
    assert f.last_join["decision"] == "wait"  # the verifier has not reported yet
    f.dispatch("verifier", st)
    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"] == "budget kill: reviewer"


def test_a_sub_ticket_stopped_mid_check_is_reported_as_resumable(tmp_path):
    """A dispatcher stopped while the checkers ran leaves the sub-ticket in checks-in-flight with no run
    in flight; ready-implementers names it so the next build.js resumes it instead of skipping it."""
    f, tid, (st,) = built_to_implementer(tmp_path)
    f.dispatch("implementer", st)
    r = f.ok("ticket", "ready-implementers", tid)
    assert r["ready"] == [] and r["resumable"] == [st]
    rid = f.ok("run", "start", "--role", "reviewer", "--ticket", st)["run_id"]  # a checker in flight is not resumable
    assert f.ok("ticket", "ready-implementers", tid)["resumable"] == []
    f.ok("run", "finish", rid, "--status-override", "KILLED")
    assert f.ok("ticket", "ready-implementers", tid)["resumable"] == [st]


def test_worktrees_get_the_integration_checkout_s_untracked_lockfile(tmp_path):
    """An untracked uv.lock in the integration checkout is copied into the implementer's worktree and each
    checker's checkout, so the branch is tested against the same resolved packages."""
    f, tid, (st,) = built_to_implementer(tmp_path)
    (f.repo / ".gitignore").write_text("uv.lock\n")
    (f.repo / "uv.lock").write_text("# the integration lock\n")
    impl = f.dispatch("implementer", st)
    wt = Path(yaml.safe_load((f.store / "runs" / impl.run_id / "meta.yaml").read_text())["worktree"])
    assert (wt / "uv.lock").read_text() == "# the integration lock\n"
    rid = f.ok("run", "start", "--role", "verifier", "--ticket", st)["run_id"]
    meta = yaml.safe_load((f.store / "runs" / rid / "meta.yaml").read_text())
    assert meta["environment_files"] == ["uv.lock"] and (Path(meta["worktree"]) / "uv.lock").read_text() == "# the integration lock\n"


def test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix(tmp_path):
    """A SPEC-DEFECT caused by the gate, not the change: the human fixes the gate and redispatches. The
    checkers run again on the same commit, the round does not move, and the old rows are set aside."""
    f, tid, (st,) = built_to_implementer(tmp_path)
    f.dispatch("implementer", st)
    head = f.ticket(st)["head"]
    f.dispatch("reviewer", st)
    defect = f.tmp / "defect.md"
    defect.write_text("Commit: HEAD\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    f.dispatch("verifier", st, stub_path=defect)
    assert f.state(st) == "parked" and f.ticket(st)["parked"]["reason"] == "SPEC-DEFECT from verifier"
    cp = f.cli("resolve", tid, "--redispatch")  # only a sub-ticket parked from its checks
    assert cp.returncode == 2
    f.human_runs("resolve", st, "--redispatch")
    assert f.state(st) == "checks-in-flight" and f.ticket(st)["round"]["pr"] == 1 and f.ticket(st)["head"] == head
    assert f.results(st) == {} and sorted(p.name for p in (f.store / "results" / head / "superseded-1").iterdir()) == ["ci.yaml", "reviewer.yaml", "verifier.yaml"]
    assert f.ok("ticket", "ready-implementers", tid)["resumable"] == [st]
    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
    f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
    assert f.state(st) == "merged"


# ----- the shepherd: the routing table applied to the store CLI ----------------------------------

class Run:
    def __init__(self, run_id: str, input_text: str, sources: list[str], status: str | None):
        self.run_id, self.input, self.sources, self.status = run_id, input_text, sources, status


class Shepherd:
    def __init__(self, tmp_path: Path, case: str, with_repo: bool = False):
        self.store = tmp_path / "state"
        self.case = case
        self.tmp = tmp_path
        self.count: dict[str, int] = {}
        self.last_join: dict = {}
        self.repo: Path | None = None
        if with_repo:  # a scratch target repo: one commit on `main`, the integration branch
            self.repo = tmp_path / "target"
            self.repo.mkdir()
            self.git("init", "-q", "-b", "main")
            self.git("config", "user.email", "fixture@example.com")
            self.git("config", "user.name", "fixture")
            (self.repo / "README.md").write_text("target repo\n")
            self.git("add", "README.md")
            self.git("commit", "-q", "-m", "initial")

    def git(self, *argv: str, cwd: Path | None = None) -> str:
        cp = subprocess.run(["git", *argv], cwd=cwd or self.repo, capture_output=True, text=True)
        assert cp.returncode == 0, f"git {' '.join(argv)}: {cp.stderr}"
        return cp.stdout

    def repo_rev(self, ref: str) -> str:
        return self.git("rev-parse", ref).strip()

    # --- the store CLI, as the clerk runs it
    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "FACTORY_STATE": str(self.store), "PYTHONDONTWRITEBYTECODE": "1"}
        if self.repo:
            env["FACTORY_REPO"] = str(self.repo)
            env["FACTORY_INTEGRATION_BRANCH"] = "main"
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def ticket(self, tid: str) -> dict:
        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())

    def state(self, tid: str) -> str:
        return self.ticket(tid)["status"]

    def results(self, tid: str) -> dict:
        return self.ok("results", "show", tid)["rows"]

    def ready_implementers(self, parent: str) -> list[str]:
        return self.ok("ticket", "ready-implementers", parent)["ready"]

    def parent_check(self, parent: str) -> str:
        return self.ok("ticket", "parent-check", parent)["state"]

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
    def dispatch(self, role: str, tid: str, stub: str | None = None, finish: bool = True, stub_path: Path | None = None, route: bool = True,
                 file: str = "thing.txt", merge_main: bool = False, no_change: bool = False, killed: bool = False) -> Run:
        self.count[role] = self.count.get(role, 0) + 1
        stub_path = stub_path or STUBS / (stub or f"{self.case}/{role}-{self.count[role]}.md")
        rid = self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]
        composed = self.ok("run", "compose", rid)
        input_text = (self.store / "runs" / rid / "input.md").read_text()
        if not finish:
            return Run(rid, input_text, composed["sources"], None)
        meta = yaml.safe_load((self.store / "runs" / rid / "meta.yaml").read_text())
        if role == "implementer":  # the stub implementer's one code change, committed on its branch
            wt = Path(meta["worktree"])
            if merge_main:  # a conflict run: merge the integration branch into the branch, nothing else
                self.git("merge", "-q", "--no-edit", "main", cwd=wt)
            elif no_change:
                pass  # an implementer that returns without touching its branch
            else:
                (wt / file).write_text("the thing\n")
                self.git("add", file, cwd=wt)
                self.git("commit", "-q", "-m", f"{tid}: the thing", cwd=wt)
        if killed:  # the run returned nothing (budget kill): no output, a KILLED row
            status = self.ok("run", "finish", rid, "--status-override", "KILLED")["status"]
            self.ok("run", "cleanup", rid)
            self.ok("results", "record", tid, "--head", self.ok("ticket", "head", tid)["head"], "--role", role, "--run", rid, "--killed")
            self.act_on_join(tid, rid)
            return Run(rid, input_text, composed["sources"], status)
        text = stub_path.read_text().replace("Commit: HEAD", f"Commit: {meta.get('head')}")
        (self.store / "runs" / rid / "output.md").write_text(text)
        status = self.ok("run", "finish", rid)["status"]
        if role in ("reviewer", "verifier"):
            self.ok("run", "cleanup", rid)
        if route:
            self.route(role, tid, rid, status, meta)
        return Run(rid, input_text, composed["sources"], status)

    def route(self, role: str, tid: str, rid: str, status: str, meta: dict | None = None) -> None:
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
                self.ok("subticket", "add", tid, "--run", rid)
                go("planned")
            else:
                park(f"{status} from planner")
        elif role == "implementer":
            if status == "BLOCKED":
                park("BLOCKED from implementer")
            else:
                assert status == "READY-FOR-REVIEW", status
                moved = self.ok("ticket", "head", tid)
                if moved["merge_refused"]:  # a conflict run that did not merge main in: ask the join, skip the checkers
                    self.act_on_join(tid, rid)
                else:
                    go("checks-in-flight", "pr:init")
        elif role in ("reviewer", "verifier"):
            if self.ticket(tid)["status"] == "ready-for-parent-verify":
                # | parent-close | VERIFIED archives the change, then closes; anything else parks the parent |
                if status == "VERIFIED":
                    self.ok("archive", tid)
                    go("closed")
                else:
                    park(f"{status} from parent-close verifier")
                return
            head = self.ok("ticket", "head", tid)["head"]  # as build.js does: the CLI names the head, never the store file
            assert self.ok("ticket", "show", tid, "--json")["head"] == head
            self.ok("results", "record", tid, "--head", head, "--role", role, "--output", str(self.store / "runs" / rid / "output.md"), "--run", rid)
            self.act_on_join(tid, rid)

    def act_on_join(self, tid: str, rid: str | None = None) -> dict:
        """`factory ticket join` decides; the dispatcher (build.js, and this shepherd) only carries it out."""
        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
        join = self.ok("ticket", "join", tid)
        self.last_join = join
        if join["decision"] == "merge":
            go("ready-for-merge")
            cp = self.cli("merge", tid)
            if cp.returncode != 0:
                again = self.ok("ticket", "join", tid)
                self.last_join = again
                if again["decision"] == "conflict":
                    go("ready-for-implementer")
                else:
                    self.ok("ticket", "park", tid, "--reason", again["reason"])
        elif join["decision"] == "revise":
            go("ready-for-implementer", join["round_op"])
        elif join["decision"] == "conflict":
            if self.state(tid) != "ready-for-implementer":
                go("ready-for-implementer")
        elif join["decision"] == "park":
            self.ok("ticket", "park", tid, "--reason", join["reason"], *(["--outputs", rid] if rid else []))
        return join  # "wait": the other checker has not reported on this head yet
