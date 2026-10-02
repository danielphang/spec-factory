"""The one input composer: `run compose RUN` writes runs/<id>/input.md from declared sources only.

Per (role, round, resolution). No other code path assembles role input.
"""
from __future__ import annotations

from pathlib import Path

from factory import store

PROMPTS = Path(__file__).resolve().parent / "prompts"


def _runs_for(root: Path, ticket: str, role: str, exclude: str) -> list[str]:
    runs = root / "runs"
    out = []
    if runs.exists():
        for p in sorted(runs.iterdir()):
            if p.name == exclude or not (p / "meta.yaml").exists():
                continue
            m = store.read_yaml(p / "meta.yaml")
            if m.get("ticket") == ticket and m.get("role") == role and m.get("finished"):
                out.append(p.name)
    return out


def _approvals(root: Path, ticket: str, kind: str) -> list[Path]:
    d = root / "approvals" / ticket
    return sorted(d.glob(f"{kind}-*.md")) if d.exists() else []


def current_truth(root: Path) -> list[Path]:
    """Every current-truth spec in the store (doc §Harness, Spec store), in path order.
    Empty until `factory init` has created openspec/specs/ and an archive has filled it."""
    d = root / "openspec" / "specs"
    return sorted(d.glob("*/spec.md")) if d.exists() else []


def _last_run_meta(root: Path, ticket: str, role: str, exclude: str) -> dict | None:
    runs = _runs_for(root, ticket, role, exclude)
    return store.read_yaml(root / "runs" / runs[-1] / "meta.yaml") if runs else None


def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]:
    role, run_id, tid = meta["role"], meta["run_id"], t["id"]
    out_path = root / "runs" / run_id / "output.md"
    parts = [(PROMPTS / "context.md").read_text(encoding="utf-8").rstrip(),
             f"\n## Output file\n`{out_path}`\n"]
    sources: list[str] = []

    def add(rel: str, heading: str) -> None:
        p = root / rel
        if p.exists():
            sources.append(rel)
            parts.append(f"\n## {heading}\n\n{p.read_text(encoding='utf-8').rstrip()}\n")

    version = t["spec"]["version"]
    rnd = t["round"]["spec"]

    def add_truth() -> None:
        for p in current_truth(root):
            add(str(p.relative_to(root)), f"Current truth: {p.parent.name}")
    if role == "triage":
        add(t["request"], "Request (raw, with any answers appended)")
        prior = _runs_for(root, tid, "triage", run_id)
        if prior:
            add(f"runs/{prior[-1]}/output.md", "Your previous Triage output (the question you asked is answered above)")
    elif role == "spec_writer":
        tri = _runs_for(root, tid, "triage", run_id)
        if tri:
            add(f"runs/{tri[-1]}/output.md", "Ticket (Triage output)")
        add(t["request"], "Request (raw)")
        add_truth()
        # An answered question returns to the role that asked with its own previous output
        # (doc §Routing rules): the writer run that parked NEEDS-HUMAN is the one that asked.
        prev = _last_run_meta(root, tid, "spec_writer", run_id)
        if prev and prev.get("status") == "NEEDS-HUMAN":
            add(f"runs/{prev['run_id']}/output.md", "Your previous output (the question you asked is answered in the request above)")
        if rnd >= 1 and version >= 1:
            crit = _runs_for(root, tid, "critic", run_id)
            if crit:
                add(f"runs/{crit[-1]}/output.md", "Critic findings on your previous version")
            add(f"specs/{tid}/v{version}.md", f"Your previous spec (v{version})")
        for p in _approvals(root, tid, "changes"):
            add(str(p.relative_to(root)), "Human gate: changes requested")
        for p in _approvals(root, tid, "ruling"):
            add(str(p.relative_to(root)), "Human ruling")
    elif role == "critic":
        add(f"specs/{tid}/v{version}.md", f"Spec under review (v{version})")
        add_truth()
        if rnd >= 2 and version >= 2:
            crit = _runs_for(root, tid, "critic", run_id)
            if crit:
                add(f"runs/{crit[-1]}/output.md", "Your prior findings (round %d)" % (rnd - 1))
            add(f"specs/{tid}/v{version - 1}.md", f"Previous spec version (v{version - 1})")
        for p in _approvals(root, tid, "ruling"):
            add(str(p.relative_to(root)), "Human ruling")
    elif role == "planner":
        av = t["spec"]["approved_version"]
        if av is None:
            raise store.Refused(f"{tid} has no approved spec version")
        add(f"specs/{tid}/v{av}.md", f"Approved spec (v{av}, pinned)")
        for p in _approvals(root, tid, "ruling"):
            add(str(p.relative_to(root)), "Human ruling")
    else:
        raise store.Refused(f"compose: role {role} not supported yet")
    return "".join(parts), sources
