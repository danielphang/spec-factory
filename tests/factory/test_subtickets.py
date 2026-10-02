"""Sub-tickets from real plan shapes (the three pilot plans, 2026-10-01): `##` headings with
`T-0001-A` or `ST-1` ids, bold field names, shared preludes, and a dependency on another parent."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"

PLAN_LETTERS = """# Plan — T-0001: alert the operator

## Grounding for this plan
Checked on this base.

## Fixture (prelude for every sub-ticket)
```
cat > /tmp/fx.py <<'PY'
## not a heading
PY
```

## T-0001-A / Emit the truncation event
**Depends on:** none. Lands first.

**Parallel-safe:** yes, alongside T-0001-C. The two edit disjoint files.

Scope: A

## T-0001-C / Retire the margin signal
**Depends on:** none. Lands second, before T-0001-B.

**Parallel-safe:** yes, alongside T-0001-A (disjoint files).

## T-0001-B / Re-anchor the check
**Depends on:** T-0001-C.

**Parallel-safe:** no. Same file as T-0001-C.

## Coverage map
- criterion 1 → T-0001-A

## Out-of-scope observations
none
STATUS: PLANNED
CONFIDENCE: high, fixture
ESCALATIONS: none
"""

PLAN_ST = """# Plan — T-0002 (SPEC-26): warn before a prompt stops fitting

## ST-1 / Log the input budget per turn
**Depends on:** T-0001 (SPEC-21), all three of its sub-tickets — `T-0001-A`, `T-0001-C`,
`T-0001-B`.

**Parallel-safe:** n/a — it is the only sub-ticket.

## Coverage map: parent criterion → sub-ticket
- B1 → ST-1
STATUS: PLANNED
CONFIDENCE: high, fixture
ESCALATIONS: none
"""


def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)


def js(cp):
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout.strip().splitlines()[-1])


def planned_parent(store: Path, tmp_path: Path, n: int, plan: str) -> str:
    """A parent ticket approved (old-format spec; no spec store) with `plan` as its planner output."""
    req = tmp_path / f"r{n}.md"
    req.write_text(f"# SPEC-{n}: Fixture {n}\n\nThing {n}.\n")
    tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
    spec = tmp_path / f"s{n}.md"
    spec.write_text("## Problem\nx\n")
    js(run(store, "ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(store, "spec", "add", tid, "--file", str(spec)))
    js(run(store, "ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    js(run(store, "ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(store, "approve-spec", tid))
    rid = js(run(store, "run", "start", "--role", "planner", "--ticket", tid))["run_id"]
    js(run(store, "run", "compose", rid))
    (store / "runs" / rid / "output.md").write_text(plan)
    js(run(store, "run", "finish", rid))
    js(run(store, "plan", "add", tid, "--from-run", rid))
    subs = js(run(store, "subticket", "add", tid, "--run", rid))["subtickets"]
    js(run(store, "ticket", "transition", tid, "--to", "planned", "--by", "t"))
    return tid, subs


def ticket(store: Path, tid: str) -> dict:
    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())


def test_lettered_ids_become_numbered_sub_tickets_in_plan_order(tmp_path):
    store = tmp_path / "state"
    tid, subs = planned_parent(store, tmp_path, 21, PLAN_LETTERS)
    assert [(s["id"], s["label"]) for s in subs] == [("T-0001.1", "T-0001-A"), ("T-0001.2", "T-0001-C"), ("T-0001.3", "T-0001-B")]
    assert [s["depends_on"] for s in subs] == [[], [], ["T-0001.2"]]
    assert [s["parallel_safe"] for s in subs] == [True, True, False]
    assert [s["state"] for s in subs] == ["ready-for-implementer", "ready-for-implementer", "waiting-dependencies"]
    text = (store / "specs" / "T-0001.3" / "subticket.md").read_text()
    assert text.startswith("## T-0001-B / Re-anchor the check")
    assert "Coverage map" not in text and "T-0001-A / Emit" not in text
    assert "## Shared plan context" in text and "## Fixture (prelude for every sub-ticket)" in text and "## not a heading" in text


def test_ready_implementers_runs_parallel_safe_siblings_together_and_holds_the_dependant(tmp_path):
    store = tmp_path / "state"
    tid, _ = planned_parent(store, tmp_path, 21, PLAN_LETTERS)
    assert js(run(store, "ticket", "ready-implementers", tid))["ready"] == ["T-0001.1", "T-0001.2"]
    # once C (.2) is merged, B (.3) is released; it is not parallel-safe, so it is listed alone
    for st in ("T-0001.1", "T-0001.2"):
        t = ticket(store, st)
        t["status"] = "merged"
        (store / "tickets" / f"{st}.yaml").write_text(yaml.safe_dump(t, sort_keys=False))
    r = js(run(store, "ticket", "ready-implementers", tid))
    assert r["ready"] == ["T-0001.3"] and ticket(store, "T-0001.3")["status"] == "ready-for-implementer"


def test_a_not_parallel_safe_sub_ticket_waits_while_a_sibling_is_in_flight(tmp_path):
    store = tmp_path / "state"
    tid, _ = planned_parent(store, tmp_path, 21, PLAN_LETTERS)
    t = ticket(store, "T-0001.2")
    t["status"] = "merged"
    (store / "tickets" / "T-0001.2.yaml").write_text(yaml.safe_dump(t, sort_keys=False))
    a = ticket(store, "T-0001.1")
    a["status"] = "checks-in-flight"
    (store / "tickets" / "T-0001.1.yaml").write_text(yaml.safe_dump(a, sort_keys=False))
    assert js(run(store, "ticket", "ready-implementers", tid))["ready"] == []  # B is solo-only; A is still in flight


def test_a_dependency_on_another_parent_waits_until_that_parent_closes(tmp_path):
    store = tmp_path / "state"
    first, _ = planned_parent(store, tmp_path, 21, PLAN_LETTERS)
    second, subs = planned_parent(store, tmp_path, 26, PLAN_ST)
    assert second == "T-0002" and subs == [{"id": "T-0002.1", "label": "ST-1", "state": "waiting-dependencies",
                                           "depends_on": ["T-0001"], "parallel_safe": False}]  # "n/a" is not "yes": it runs alone
    assert js(run(store, "ticket", "ready-implementers", second))["ready"] == []
    js(run(store, "resolve", first, "--close"))
    r = js(run(store, "ticket", "ready-implementers", second))
    assert r["ready"] == ["T-0002.1"] and ticket(store, "T-0002.1")["status"] == "ready-for-implementer"


def test_subticket_add_refuses_a_plan_with_no_sub_tickets_and_a_dependency_on_nothing(tmp_path):
    store = tmp_path / "state"
    req = tmp_path / "r.md"
    req.write_text("# SPEC-1: x\n\ny\n")
    js(run(store, "ticket", "new", "--file", str(req)))
    spec = tmp_path / "s.md"
    spec.write_text("## Problem\nx\n")
    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(store, "spec", "add", "T-0001", "--file", str(spec)))
    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    js(run(store, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(store, "approve-spec", "T-0001"))
    f = tmp_path / "p.md"
    f.write_text("# Plan\nno sub-tickets here\n")
    cp = run(store, "subticket", "add", "T-0001", "--file", str(f))
    assert cp.returncode == 2 and "no sub-tickets found" in cp.stderr
    f.write_text("## ST-1 / One\n**Depends on:** T-0099.\n**Parallel-safe:** yes\n")
    cp = run(store, "subticket", "add", "T-0001", "--file", str(f))
    assert cp.returncode == 2 and "T-0099" in cp.stderr
    assert not (store / "tickets" / "T-0001.1.yaml").exists()


def test_a_bullet_that_names_a_sub_ticket_is_not_a_head_and_a_repeated_id_is_refused(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("factory_subtickets", REPO / "factory" / "subtickets.py")
    subtickets = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subtickets)
    plan = ("## ST-1 / One\n**Depends on:** none\n**Parallel-safe:** yes\n  Acceptance:\n- ST-1 / not a head, just a bullet\n- T-0001.1 passes\n\n"
            "## ST-2 / Two\n**Depends on:** .1\nSTATUS: PLANNED\n")
    subs = subtickets.parse(plan, "T-0001")
    assert [(s["id"], s["title"]) for s in subs] == [("T-0001.1", "One"), ("T-0001.2", "Two")]
    assert "not a head, just a bullet" in subs[0]["text"]
    assert subs[1]["depends_on"] == ["T-0001.1"] and subs[1]["parallel_safe"] is False  # no Parallel-safe line: runs alone
    store = tmp_path / "state"
    f = tmp_path / "dup.md"
    f.write_text("## ST-1 / One\n**Depends on:** none\n\n## ST-1 / One again\n**Depends on:** none\n")
    req = tmp_path / "r.md"
    req.write_text("# SPEC-1: x\n\ny\n")
    spec = tmp_path / "s.md"
    spec.write_text("## Problem\nx\n")
    js(run(store, "ticket", "new", "--file", str(req)))
    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
    js(run(store, "spec", "add", "T-0001", "--file", str(spec)))
    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
    js(run(store, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
    js(run(store, "approve-spec", "T-0001"))
    cp = run(store, "subticket", "add", "T-0001", "--file", str(f))
    assert cp.returncode == 2 and "used more than once" in cp.stderr
    import importlib.util
    spec = importlib.util.spec_from_file_location("factory_subtickets2", REPO / "factory" / "subtickets.py")
    st = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(st)
    for none in ("none", "None.", "n/a", "N/A — only sub-ticket", "— (none)", "-", ""):  # the ways planners say "no dependencies"
        assert st.parse(f"## ST-1 / One\n**Depends on:** {none}\n", "T-0001")[0]["depends_on"] == [], none
    for dep in (".5", "sub-ticket 1"):  # a dependency nobody can resolve is refused, never dropped
        f.write_text(f"## ST-1 / One\n**Depends on:** none\n\n## ST-2 / Two\n**Depends on:** {dep}\n")
        cp = run(store, "subticket", "add", "T-0001", "--file", str(f))
        assert cp.returncode == 2 and ("not a sub-ticket of this plan" in cp.stderr or "cannot resolve" in cp.stderr), dep
    assert not (store / "tickets" / "T-0001.1.yaml").exists()
