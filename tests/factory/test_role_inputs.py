"""Each role's input carries the spec sections it uses (T-0030 part C).

The planner, implementer, reviewer and verifier (the parent-close verifier included) get the pinned
spec without its `## Evidence` and `## Responses` sections, and a heading that names the full spec
file. A round-2 critic gets the unified diff from the previous spec version when that is smaller
than the version, and the version whole otherwise. `input_sources` is unchanged in both.
"""
from __future__ import annotations

import subprocess
import sys

from .test_p0_cli import REPO, js, run
from .test_shepherd import Shepherd

FENCE = "```"


def without_evidence(text: str) -> str:
    """compose.without_evidence, run from the harness checkout: `factory` here is the test package."""
    code = "import sys; from factory import compose; sys.stdout.write(compose.without_evidence(sys.stdin.read()))"
    cp = subprocess.run([sys.executable, "-c", code], input=text, capture_output=True, text=True, cwd=REPO)
    assert cp.returncode == 0, cp.stderr
    return cp.stdout


def test_the_cut_drops_evidence_and_responses_and_keeps_every_other_section():
    text = "\n".join([
        "=== proposal.md",
        "## Problem",
        "PROBLEM-MARK",
        "## Evidence   ",  # trailing spaces still start the section
        "EVIDENCE-MARK",
        FENCE + "sh",
        "## Not a heading: inside a fence",
        "=== not/a/part.md",
        "FENCED-EVIDENCE-MARK",
        FENCE,
        "AFTER-FENCE-EVIDENCE-MARK",
        "### A sub-heading is still Evidence",
        "SUB-EVIDENCE-MARK",
        "## Root cause",
        "ROOTCAUSE-MARK",
        FENCE,
        "## Evidence",
        "FENCED-NOT-A-SECTION-MARK",
        FENCE,
        "## Evidence of something else",
        "SIMILAR-HEADING-MARK",
        "=== verification.md",
        "## Acceptance",
        "ACCEPTANCE-MARK",
        "## Responses",
        "RESPONSES-MARK",
        "=== specs/demo/spec.md",
        "## ADDED Requirements",
        "SCENARIO-MARK",
    ]) + "\n"
    lines = without_evidence(text).splitlines()
    for gone in ("## Evidence   ", "EVIDENCE-MARK", "## Not a heading: inside a fence", "=== not/a/part.md",
                 "FENCED-EVIDENCE-MARK", "AFTER-FENCE-EVIDENCE-MARK", "### A sub-heading is still Evidence",
                 "SUB-EVIDENCE-MARK", "## Responses", "RESPONSES-MARK"):
        assert gone not in lines, gone
    for kept in ("=== proposal.md", "## Problem", "PROBLEM-MARK", "## Root cause", "ROOTCAUSE-MARK", "## Evidence",
                 "FENCED-NOT-A-SECTION-MARK", "## Evidence of something else", "SIMILAR-HEADING-MARK",
                 "=== verification.md", "## Acceptance", "ACCEPTANCE-MARK", "=== specs/demo/spec.md",
                 "## ADDED Requirements", "SCENARIO-MARK"):
        assert kept in lines, kept
    assert lines.count("## Evidence") == 1  # only the fenced one, which is text, not a section
    assert without_evidence("## Problem\nno cut sections\n") == "## Problem\nno cut sections\n"


MARKED_SPEC = """=== proposal.md
## Problem
PROBLEM-MARK The fixture thing is not done, and the requester needs it done.
## Evidence
EVIDENCE-MARK long captured output.
```
## Fenced, still Evidence
```
## Root cause
ROOTCAUSE-MARK unknown
## Out of scope
OUTOFSCOPE-MARK nothing else
## Open questions
none
## Decisions
- The thing is done the simple way.
## Risk
RISK-MARK none
=== design.md
## Proposed change
A. CHANGE-MARK do the thing
## Tests to change
none
=== specs/thing/spec.md
## ADDED Requirements
### Requirement: the-thing
The bot SHALL do the thing when asked. SCENARIO-MARK
#### Scenario: asked once
- WHEN `true`
- THEN exit 0
=== verification.md
## Acceptance
- asked once → NEW; today `true` is never run. ACCEPTANCE-MARK
## Responses
RESPONSES-MARK none
STATUS: READY-FOR-CRITIC
CONFIDENCE: high, fixture
ESCALATIONS: none
"""

KEPT = ("PROBLEM-MARK", "ROOTCAUSE-MARK", "OUTOFSCOPE-MARK", "RISK-MARK", "CHANGE-MARK", "SCENARIO-MARK",
        "ACCEPTANCE-MARK", "## Decisions", "## Tests to change", "## Open questions")


def test_planner_implementer_checkers_and_parent_close_get_the_spec_without_evidence_or_responses(tmp_path):
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    writer = tmp_path / "marked-spec.md"
    writer.write_text(MARKED_SPEC)
    f.dispatch("triage", tid)
    f.dispatch("spec_writer", tid, stub_path=writer)
    crit = f.dispatch("critic", tid)
    assert "EVIDENCE-MARK" in crit.input and "RESPONSES-MARK" in crit.input  # the critic's current spec is whole
    f.human_approves(tid)
    full = f.store / "specs" / tid / "v1.md"
    spec_rel = f"specs/{tid}/v1.md"

    planner = f.dispatch("planner", tid)
    (st,) = f.ok("ticket", "parent-check", tid)["subtickets"]
    impl = f.dispatch("implementer", st)
    rev = f.dispatch("reviewer", st)
    ver = f.dispatch("verifier", st)
    assert f.parent_check(tid) == "ready-for-parent-verify"
    close = f.dispatch("verifier", tid)

    for name, r, heading in (("planner", planner, "## Approved spec (v1, pinned)"),
                             ("implementer", impl, "## Parent spec (v1, pinned)"),
                             ("reviewer", rev, "## Parent spec (v1, pinned)"),
                             ("verifier", ver, "## Parent spec (v1, pinned)"),
                             ("parent-close", close, "## Parent spec (v1, pinned): verify every scenario on main")):
        assert "EVIDENCE-MARK" not in r.input and "## Fenced, still Evidence" not in r.input, name
        assert "RESPONSES-MARK" not in r.input, name
        assert all(k in r.input for k in KEPT), name
        line = next(x for x in r.input.splitlines() if x.startswith(heading))
        assert f"`{full}`" in line and "Evidence and Responses" in line, (name, line)
        assert r.input.count(str(full)) == 1, name
        assert spec_rel in r.sources, name  # input_sources still names the pinned version file
    assert close.status == "VERIFIED" and f.state(tid) == "closed"


def _round2_critic(store, tmp_path, v1: str, v2: str) -> tuple[str, list[str]]:
    req = tmp_path / "req.md"
    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
    (tmp_path / "v1.md").write_text(v1)
    (tmp_path / "v2.md").write_text(v2)
    (tmp_path / "c1.md").write_text("Findings: one.\nSTATUS: REVISE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    run(store, "ticket", "new", "--file", str(req))
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    run(store, "spec", "add", "T-0001", "--file", str(tmp_path / "v1.md"))
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    c1 = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
    run(store, "run", "finish", c1, "--output-file", str(tmp_path / "c1.md"))
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t", "--round", "spec:+1")
    run(store, "spec", "add", "T-0001", "--file", str(tmp_path / "v2.md"))
    run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    c2 = js(run(store, "run", "start", "--role", "critic", "--ticket", "T-0001"))["run_id"]
    composed = js(run(store, "run", "compose", c2))
    return (store / "runs" / c2 / "input.md").read_text(), composed["sources"]


V1 = "## Problem\n" + "".join(f"keep line {i}\n" for i in range(1, 201)) + "OLD-ONLY\nSTATUS: READY-FOR-CRITIC\n"


def test_a_round2_critic_gets_a_small_revision_as_a_diff(tmp_path):
    store = tmp_path / "state"
    inp, sources = _round2_critic(store, tmp_path, V1, V1.replace("OLD-ONLY", "NEW-ONLY"))
    lines = inp.splitlines()
    assert "## Previous spec version (v1), as a unified diff to v2" in lines
    assert "--- specs/T-0001/v1.md" in lines and "+++ specs/T-0001/v2.md" in lines
    assert "-OLD-ONLY" in lines and "+NEW-ONLY" in lines
    assert lines.count("keep line 100") == 1  # only the current spec carries it whole
    assert " keep line 198" in lines and " keep line 197" not in lines  # 3 lines of context
    assert "Findings: one." in inp
    assert sources == ["specs/T-0001/v2.md", sources[1], "specs/T-0001/v1.md"] and sources[1].startswith("runs/")


def test_a_round2_critic_gets_a_rewritten_spec_s_previous_version_whole(tmp_path):
    store = tmp_path / "state"
    inp, sources = _round2_critic(store, tmp_path, V1, V1.replace("keep line", "other line").replace("OLD-ONLY", "NEW-ONLY"))
    lines = inp.splitlines()
    assert "## Previous spec version (v1), whole: the diff to v2 is not smaller" in lines
    assert "-OLD-ONLY" not in lines and "--- specs/T-0001/v1.md" not in lines
    assert lines.count("keep line 100") == 1 and lines.count("other line 100") == 1
    assert sources[-1] == "specs/T-0001/v1.md"

