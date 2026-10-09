"""The capability index (spec-factory T-0036, issue #75) and the whole decision log (T-0037, #78).

Triage names the capabilities a request touches on a `Capabilities:` line, from a capability index
in its input. The spec writer and critic then receive those capabilities in full, plus the ones
their spec cites by `specs/<name>/spec.md`, and one index line for every other capability. A ticket
whose triage output has no `Capabilities:` line gets every capability in full. The writer, critic
and planner receive the whole decision log whatever capabilities their ticket names: a standing
decision often names no capability. Black-box through `bin/factory`.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
CAPS = ("alpha", "beta", "gamma")
SPEC = "\n".join([
    "=== proposal.md", "## Problem", "Beta is lax.", "## Evidence", "Read `openspec/specs/gamma/spec.md`.",
    "## Decisions", "none", "## Risk", "none", "=== design.md", "## Proposed change", "A. Tighten beta.",
    "=== specs/beta/spec.md", "## MODIFIED Requirements", "### Requirement: The beta part works",
    "The beta part SHALL work strictly.", "#### Scenario: strict", "- WHEN `true`", "- THEN it exits 0",
    "=== verification.md", "## Acceptance", "- strict → NEW; today lax", ""])


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


def ok(store: Path, *argv: str) -> str:
    cp = run(store, *argv)
    assert cp.returncode == 0, cp.stderr
    return cp.stdout


def start(store: Path, role: str) -> str:
    rid = yaml.safe_load(ok(store, "run", "start", "--role", role, "--ticket", "T-0001").strip().splitlines()[-1])["run_id"]
    ok(store, "run", "compose", rid)
    return rid


def finish(store: Path, rid: str, body: str, status: str) -> None:
    (store / "runs" / rid / "output.md").write_text(f"{body}\nSTATUS: {status}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
    ok(store, "run", "finish", rid)


def text_of(store: Path, rid: str) -> str:
    return (store / "runs" / rid / "input.md").read_text()


def sources(store: Path, rid: str) -> list[str]:
    return yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())["input_sources"]


def truth(store: Path, cap: str) -> Path:
    return store / "openspec" / "specs" / cap / "spec.md"


DECISIONS = ["2026-10-01 T-0001 OWN-LINE decided for this ticket.",
             "2026-10-02 T-0007 BETA-LINE beta keeps its default.",
             "2026-10-03 T-0008 GAMMA-LINE gamma stays read-only.",
             "2026-10-04 T-0009 OTHER-LINE logs rotate weekly.",
             "2026-10-06 T-0009 OTHER2-LINE beta-two, beta_x and xbeta2 name other things."]


def setup(tmp_path: Path, decisions: list[str] | None = None, others: tuple[str, ...] = ()) -> Path:
    """A store with T-0001, one more ticket per title in `others`, alpha, beta and gamma, and a log."""
    s = tmp_path / "state"
    for n, title in enumerate(("Fixture", *others)):
        req = tmp_path / f"req{n}.md"
        req.write_text(f"# {title}\n\nMake beta stricter.\n")
        ok(s, "ticket", "new", "--file", str(req))
    ok(s, "init")
    for c in CAPS:
        truth(s, c).parent.mkdir(parents=True)
        truth(s, c).write_text(f"# {c}\n\n## Requirements\n\n### Requirement: The {c} part works\n"
                               f"{c.upper()}-BODY The {c} part SHALL work.\n\n### Requirement: {c} second\nMore.\n")
    (s / "decisions.md").write_text("\n".join(DECISIONS if decisions is None else decisions) + "\n")
    return s


def triage(s: Path, caps_line: str | None) -> str:
    rid = start(s, "triage")
    finish(s, rid, "Type: feature\nTitle: Fixture\nSummary: Make beta stricter.\n" + (caps_line or ""), "ACCEPT")
    return rid


def build(tmp_path: Path, caps_line: str | None, decisions: list[str] | None = None, others: tuple[str, ...] = ()):
    """T-0001 through triage (with `caps_line` on its output, or none), writer, critic, approval and
    planner. Returns (store, {role: run id})."""
    s = setup(tmp_path, decisions, others)
    runs = {"triage": triage(s, caps_line)}
    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    runs["spec_writer"] = start(s, "spec_writer")
    finish(s, runs["spec_writer"], SPEC, "READY-FOR-CRITIC")
    ok(s, "spec", "add", "T-0001", "--from-run", runs["spec_writer"])
    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    runs["critic"] = start(s, "critic")
    finish(s, runs["critic"], "Findings: none.", "APPROVE")
    ok(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
    ok(s, "approve-spec", "T-0001")
    runs["planner"] = start(s, "planner")
    return s, runs


def index_line(store: Path, cap: str) -> str:
    return (f"- {cap}, 1 kB, `{truth(store, cap)}`: The {cap} part works; {cap} second\n")


# ----- part B: the named capabilities in full, an index line for the rest ------------------------

def test_writer_gets_the_named_capability_in_full_and_an_index_line_for_each_other(tmp_path):
    s, r = build(tmp_path, "Capabilities: beta")
    text = text_of(s, r["spec_writer"])
    assert "BETA-BODY" in text and "ALPHA-BODY" not in text and "GAMMA-BODY" not in text
    head = ("\n## Capability index: current truth not given in full above\n\nThis list is complete: every "
            "current-truth capability not given in full above has one line here. Open a capability at its path "
            "before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, "
            "sends that capability in full to the critic, so cite under Evidence each capability you open.\n\n")
    assert head + index_line(s, "alpha") + index_line(s, "gamma") in text
    assert sources(s, r["spec_writer"]) == [f"runs/{r['triage']}/output.md", "requests/T-0001.md",
                                            "openspec/specs/beta/spec.md", "decisions.md"]


def test_critic_also_gets_the_capabilities_its_spec_cites(tmp_path):
    s, r = build(tmp_path, "Capabilities: beta")
    text = text_of(s, r["critic"])
    assert "BETA-BODY" in text and "GAMMA-BODY" in text and "ALPHA-BODY" not in text
    assert index_line(s, "alpha") in text and f"`{truth(s, 'gamma')}`" not in text
    assert text.count("sends that capability in full to the critic") == 1
    assert sources(s, r["critic"]) == ["specs/T-0001/v1.md", "openspec/specs/beta/spec.md",
                                       "openspec/specs/gamma/spec.md", "decisions.md"]


def test_planner_gets_no_current_truth_and_no_capability_index(tmp_path):
    s, r = build(tmp_path, "Capabilities: beta")
    text = text_of(s, r["planner"])
    assert "-BODY" not in text and "Capability index" not in text and "spec.md`:" not in text
    assert sources(s, r["planner"]) == ["specs/T-0001/v1.md", "decisions.md"]


def test_an_index_line_rounds_the_size_up_to_whole_kilobytes(tmp_path):
    s = setup(tmp_path)
    head = "# {0}\n\n## Requirements\n\n### Requirement: {0} sized\n"
    for cap, size in (("alpha", 2001), ("gamma", 2000)):
        truth(s, cap).write_text(head.format(cap) + "x" * (size - len(head.format(cap)) - 1) + "\n")
        assert truth(s, cap).stat().st_size == size
    triage(s, "Capabilities: beta")
    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    text = text_of(s, start(s, "spec_writer"))
    assert f"- alpha, 3 kB, `{truth(s, 'alpha')}`: alpha sized\n" in text
    assert f"- gamma, 2 kB, `{truth(s, 'gamma')}`: gamma sized\n" in text


@pytest.mark.parametrize("line, full", [
    ("Capabilities: `beta`, gamma.", {"beta", "gamma"}),
    ("Capabilities: beta,gamma", {"beta", "gamma"}),
    ("Capabilities: beta new delta", {"beta"}),
    ("Capabilities: none", set()),
    ("Capabilities:", set()),
])
def test_the_capabilities_line_is_split_on_commas_and_spaces_and_keeps_only_existing_names(tmp_path, line, full):
    s, r = build(tmp_path, line)
    text = text_of(s, r["spec_writer"])
    assert {c for c in CAPS if f"{c.upper()}-BODY" in text} == full
    assert {c for c in CAPS if index_line(s, c) in text} == set(CAPS) - full


def test_every_capability_named_leaves_no_capability_index(tmp_path):
    s, r = build(tmp_path, "Capabilities: alpha, beta, gamma")
    text = text_of(s, r["spec_writer"])
    assert all(f"{c.upper()}-BODY" in text for c in CAPS) and "Capability index" not in text


def test_the_latest_finished_triage_run_decides(tmp_path):
    s = setup(tmp_path)
    triage(s, "Capabilities: beta")
    ok(s, "ticket", "set", "T-0001", "status=ready-for-triage", "in_flight=[]")
    triage(s, "Capabilities: alpha")
    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
    text = text_of(s, start(s, "spec_writer"))
    assert "ALPHA-BODY" in text and "BETA-BODY" not in text


# ----- the whole decision log, whatever capabilities the ticket names (T-0037) --------------------

WHOLE_LOG = "\n## Decision log (decisions.md): standing decisions, read-only\n\n"


@pytest.mark.parametrize("caps_line", ["Capabilities: beta", "Capabilities: none"])
def test_each_role_gets_the_whole_decision_log_and_no_decision_index(tmp_path, caps_line):
    s, r = build(tmp_path, caps_line)
    for role in ("spec_writer", "critic", "planner"):
        text = text_of(s, r[role])
        assert WHOLE_LOG + "\n".join(DECISIONS) + "\n" in text, role
        assert "Decision index" not in text and "<ticket id>" not in text, role
        assert "decisions.md" in sources(s, r[role]), role


def test_a_whitespace_only_log_still_adds_nothing(tmp_path):
    s, r = build(tmp_path, "Capabilities: beta", ["  "])
    text = text_of(s, r["spec_writer"])
    assert "Decision log" not in text and "Decision index" not in text
    assert "decisions.md" not in sources(s, r["spec_writer"])


# ----- part B4: no Capabilities line keeps today's inputs -----------------------------------------

def test_without_a_capabilities_line_each_role_gets_today_s_inputs(tmp_path):
    s, r = build(tmp_path, None)
    for role in ("spec_writer", "critic"):
        text = text_of(s, r[role])
        assert all(f"{c.upper()}-BODY" in text for c in CAPS) and "Capability index" not in text, role
    for role in ("spec_writer", "critic", "planner"):
        text = text_of(s, r[role])
        assert "## Decision log (decisions.md): standing decisions, read-only\n\n" + "\n".join(DECISIONS) in text
        assert "Decision index" not in text, role
    assert sources(s, r["critic"]) == ["specs/T-0001/v1.md", *(f"openspec/specs/{c}/spec.md" for c in CAPS),
                                       "decisions.md"]


# ----- part A: triage gets the capability index and is asked for the line ------------------------

def test_triage_input_lists_every_capability_and_adds_no_source(tmp_path):
    s, r = build(tmp_path, "Capabilities: beta")
    text = text_of(s, r["triage"])
    assert ("\n## Capability index: every capability in current truth\n\nName the capabilities this request "
            "touches on your `Capabilities:` line. The spec writer receives those in full and this index for "
            "the rest.\n\n" + "".join(index_line(s, c) for c in CAPS)) in text
    assert text.index("## Request") < text.index("## Capability index")
    assert "-BODY" not in text and "-LINE" not in text
    assert sources(s, r["triage"]) == ["requests/T-0001.md"]


def test_triage_input_has_no_capability_index_without_current_truth(tmp_path):
    s = tmp_path / "state"
    req = tmp_path / "req.md"
    req.write_text("# Fixture\n\nA thing.\n")
    ok(s, "ticket", "new", "--file", str(req))
    ok(s, "init")
    assert "Capability index" not in text_of(s, start(s, "triage"))


def test_the_triage_prompts_ask_for_the_capabilities_line():
    ask = ["Capabilities: (names from the capability index, comma-separated; none",
           "  if the request touches none)"]
    for p in ("docs/prompts/01-triage.md", "factory/prompts/triage.md"):
        lines = (REPO / p).read_text().splitlines()
        i = lines.index(ask[0])
        assert lines[i - 1].startswith("Evidence:") and lines[i:i + 2] == ask, p
        assert sum(x.startswith("Capabilities:") for x in lines) == 1, p
    # the block's own width: every line this change wrote fits in 72 characters
    assert all(len(x) <= 72 for x in (REPO / "docs/prompts/01-triage.md").read_text().splitlines()
               if "capabilit" in x.lower())
