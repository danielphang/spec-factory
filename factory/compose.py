"""The one input composer: `run compose RUN` writes runs/<id>/input.md from declared sources only.

Per (role, round, resolution). No other code path assembles role input.
"""
from __future__ import annotations

import re
import shlex
from pathlib import Path

from factory import instance, store


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


def gate_commands(cfg: dict) -> list[str]:
    """The gate commands with `{integration}` replaced by the checkout that has the integration
    branch: the gate script and its baseline come from the integration branch, never from the branch
    under test, so a change cannot weaken its own gate."""
    from factory import gitops  # local: compose is otherwise git-free
    repo = gitops.repo_root(cfg)
    co = gitops.checkout_of(repo, gitops.integration_branch(cfg, repo)) or repo
    return [g.replace("{integration}", str(co)) for g in cfg.get("gate_commands", [])]


_ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def run_env(cfg: dict) -> dict:
    """The instance's `run_env`: variables the running-code wrapper exports after the throwaway HOME,
    for tools that keep a cache under HOME. Absent or null is empty. Refused when it is not a mapping,
    when a name is not a shell variable name, or when it names HOME, which the wrapper owns."""
    env = cfg.get("run_env")
    if env is None:
        return {}
    if not isinstance(env, dict):
        raise store.Refused(f"run_env must be a mapping of variable name to value, not a {type(env).__name__}")
    for name in env:
        if not isinstance(name, str) or not _ENV_NAME.fullmatch(name):
            raise store.Refused(f"run_env: {name!r} is not a variable name ([A-Za-z_][A-Za-z0-9_]*)")
        if name == "HOME":
            raise store.Refused("run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory")
    return env


def wrap(command: str, env: dict) -> str:
    """`command` in a subshell with HOME set to a fresh temporary directory, then each `run_env`
    variable exported in file order. A subshell, so the export covers every part of `a && b`."""
    exports = "".join(f" {k}={shlex.quote(str(v))}" for k, v in env.items())
    return f'(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{exports}; {command})'


def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]:
    role, run_id, tid = meta["role"], meta["run_id"], t["id"]
    out_path = root / "runs" / run_id / "output.md"
    env = run_env(cfg)
    parts = [(instance.require() / "context.md").read_text(encoding="utf-8").rstrip(),
             f"\n## Output file\n`{out_path}`\n",
             "\n## Running code\nRun every test, script or prototype through this wrapper, which gives it a fresh "
             "temporary HOME so it cannot write the operator's real home directory: "
             f"`{wrap('<command>', env)}`. Put your command in place of <command>. This includes every test or "
             "check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: "
             "never run anything that could write a protected path outside the repository.\n",
             "\n## Scratch directory\nPut every file you make for your own use in this run under "
             f"`{root / 'runs' / run_id / 'scratch'}`: no other run uses it. The harness clears it when the "
             "ticket moves on, and keeps it while the ticket is parked.\n"]
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

    def add_decisions() -> None:
        # an empty log (the one `factory init` creates) carries nothing, so it is no input
        p = root / "decisions.md"
        if p.exists() and p.read_text(encoding="utf-8").strip():
            add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")
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
        add_decisions()
        if rnd >= 1 and version >= 1:
            crit = _runs_for(root, tid, "critic", run_id)
            if crit:
                add(f"runs/{crit[-1]}/output.md", "Critic findings on your previous version")
            add(f"specs/{tid}/v{version}.md", f"Your previous spec (v{version})")
        # An answered question returns to the role that asked with its own previous output
        # (doc §Routing rules): the writer run that parked NEEDS-HUMAN is the one that asked.
        prev = _last_run_meta(root, tid, "spec_writer", run_id)
        if prev and prev.get("status") == "NEEDS-HUMAN":
            add(f"runs/{prev['run_id']}/output.md", "Your previous output (the question you asked is answered in the request above)")
        for p in _approvals(root, tid, "changes"):
            add(str(p.relative_to(root)), "Human gate: changes requested")
        for p in _approvals(root, tid, "ruling"):
            add(str(p.relative_to(root)), "Human ruling")
    elif role == "critic":
        add(f"specs/{tid}/v{version}.md", f"Spec under review (v{version})")
        add_truth()
        add_decisions()
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
        add_decisions()
        for p in _approvals(root, tid, "ruling"):
            add(str(p.relative_to(root)), "Human ruling")
        subs = store.subtickets_of(root, tid)
        if subs:  # a re-plan: the new plan numbers after these and may depend on them
            parts.append(f"\n## Sub-tickets already under {tid}\n\nA new plan's sub-tickets are numbered after these. "
                         "A `Depends on:` line may name any of these ids.\n\n"
                         + "".join(f"- {s['id']} / {s['title']}: {s['status']}\n" for s in subs))
    elif role in ("implementer", "reviewer", "verifier"):
        parent = t.get("parent") or tid  # the parent-close verifier runs on the parent itself
        pt = store.load_ticket(root, parent) if parent != tid else t
        av = pt["spec"]["approved_version"]
        if av is None:
            raise store.Refused(f"{parent} has no approved spec version")
        where = (f"\n## Where you work\nWorktree: `{meta.get('worktree')}` (branch `{meta.get('branch')}`, "
                 f"base `{meta.get('base')}`, head `{meta.get('head')}`). There is no remote: commit on the "
                 f"branch; the PR is the branch plus the description you return. Gate commands (run each from "
                 f"your worktree, exactly as written; each is already wrapped): "
                 + "; ".join(f"`{wrap(g, env)}`" for g in gate_commands(cfg)) + "\n")
        parts.append(where)
        if role == "implementer":
            if t.get("merge_refused"):
                parts.append("\n## This is a conflict run\nThe merge gate refused your branch: " + str(t["merge_refused"])
                             + ". The integration branch moved after you branched. Merge it into your branch, resolve any "
                             "conflict, re-run the gates, commit, and add one note on the resolution to the PR description. "
                             "Change nothing else.\n")
            add(f"specs/{tid}/subticket.md", f"Sub-ticket {tid}")
            add(f"specs/{parent}/v{av}.md", f"Parent spec (v{av}, pinned)")
            prnd = t["round"]["pr"]
            if prnd >= 1 and t.get("head"):
                for r in ("reviewer", "verifier"):
                    rows = store.results_for(root, t["head"])
                    rid = (rows.get(r) or {}).get("run_id")
                    if rid:
                        add(f"runs/{rid}/output.md", f"{r.capitalize()} findings on your previous head")
                ci = store.results_for(root, t["head"]).get("ci")
                if ci:
                    parts.append(f"\n## Gate suite on your previous head\n{ci.get('status')}\n{ci.get('detail') or ''}\n")
            for p in _approvals(root, tid, "ruling"):
                add(str(p.relative_to(root)), "Human ruling")
        else:
            if parent == tid:
                add(f"specs/{tid}/v{av}.md", f"Parent spec (v{av}, pinned): verify every scenario on main")
            else:
                add(f"specs/{tid}/subticket.md", f"Sub-ticket {tid}")
                add(f"specs/{parent}/v{av}.md", f"Parent spec (v{av}, pinned)")
                impl = _runs_for(root, tid, "implementer", run_id)
                if impl:
                    add(f"runs/{impl[-1]}/output.md", "PR description (the implementer's output)")
                diff_rel = f"runs/{run_id}/diff.patch"
                if (root / diff_rel).exists():
                    add(diff_rel, f"Diff `{meta.get('base')}...{meta.get('head')}`")
                prnd = t["round"]["pr"]
                if prnd >= 2:  # both checkers' findings from the previous round (doc §Routing table, Implementer row)
                    for r in ("reviewer", "verifier"):
                        prev = [x for x in _runs_for(root, tid, r, run_id)
                                if store.read_yaml(root / "runs" / x / "meta.yaml").get("round") == prnd - 1]
                        if prev:
                            who = "Your" if r == role else f"The {r}'s"
                            add(f"runs/{prev[-1]}/output.md", f"{who} prior findings (round {prnd - 1})")
            for p in _approvals(root, tid, "ruling"):
                add(str(p.relative_to(root)), "Human ruling")
    else:
        raise store.Refused(f"compose: role {role} not supported yet")
    return "".join(parts), sources
