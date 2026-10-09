"""The one input composer: `run compose RUN` writes runs/<id>/input.md from declared sources only.

Per (role, round, resolution). No other code path assembles role input.
"""
from __future__ import annotations

import difflib
import math
import re
import shlex
from pathlib import Path

from factory import instance, specstore, store


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


def triage_capabilities(root: Path, tid: str) -> list[str] | None:
    """The current-truth capabilities on the first `Capabilities:` line of the ticket's latest
    finished triage output, split on commas and whitespace, backticks and periods stripped, unknown
    names (`none`, `new`) dropped. None when there is no such run or no such line: the ticket then
    gets the whole of current truth and the decision log, as before the line existed."""
    runs = _runs_for(root, tid, "triage", "")
    p = root / "runs" / runs[-1] / "output.md" if runs else None
    if p is None or not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("Capabilities:"):
            have = {c.parent.name for c in current_truth(root)}
            names = (w.strip("`.") for w in re.split(r"[,\s]+", line[len("Capabilities:"):]))
            return list(dict.fromkeys(n for n in names if n in have))
    return None


def cited_capabilities(root: Path, text: str) -> list[str]:
    """The current-truth capabilities whose `specs/<name>/spec.md` appears anywhere in `text`."""
    return [c.parent.name for c in current_truth(root) if f"specs/{c.parent.name}/spec.md" in text]


def capability_index(paths: list[Path]) -> str:
    """One line per current-truth spec: its name, size in kB rounded up, absolute path and
    requirement names."""
    return "".join(f"- {p.parent.name}, {math.ceil(p.stat().st_size / 1000)} kB, `{p}`: "
                   + "; ".join(specstore.requirement_blocks(p.read_text(encoding="utf-8"))) + "\n"
                   for p in paths)


def _last_run_meta(root: Path, ticket: str, role: str, exclude: str) -> dict | None:
    runs = _runs_for(root, ticket, role, exclude)
    return store.read_yaml(root / "runs" / runs[-1] / "meta.yaml") if runs else None


def gate_entries(cfg: dict) -> list[tuple[str, list[str] | None]]:
    """Each `gate_commands` entry as (command as written, paths or None). An entry is a command
    string, or a mapping of a non-empty string `command` and an optional non-empty list of git
    pathspecs `paths`. Absent or null is empty. Anything else is refused, naming its index: a typo
    such as `path:` read as unscoped would leave the operator believing a scope is in force."""
    out: list[tuple[str, list[str] | None]] = []
    for i, e in enumerate(cfg.get("gate_commands") or []):
        def bad(why: str) -> store.Refused:
            return store.Refused(f"gate_commands entry {i}: {why}; an entry is a command string or "
                                 "{command: <string>, paths: [<git pathspec>, ...]}, and a command that "
                                 "always runs omits paths")
        if isinstance(e, str):
            out.append((e, None))
            continue
        if not isinstance(e, dict):
            raise bad(f"{e!r} is neither a string nor a mapping")
        extra = [str(k) for k in e if k not in ("command", "paths")]
        if extra:
            raise bad(f"unknown key {', '.join(extra)}")
        if not isinstance(e.get("command"), str) or not e["command"]:
            raise bad("command must be a non-empty string")
        paths = e.get("paths")
        if "paths" in e and (not isinstance(paths, list) or not paths
                             or not all(isinstance(p, str) and p for p in paths)):
            raise bad("paths must be a non-empty list of non-empty strings")
        out.append((e["command"], paths))
    return out


def gate_commands(cfg: dict) -> list[str]:
    """The gate commands with `{integration}` replaced by the checkout that has the integration
    branch: the gate script and its baseline come from the integration branch, never from the branch
    under test, so a change cannot weaken its own gate."""
    from factory import gitops  # local: compose is otherwise git-free
    repo = gitops.repo_root(cfg)
    co = gitops.checkout_of(repo, gitops.integration_branch(cfg, repo)) or repo
    return [g.replace("{integration}", str(co)) for g, _ in gate_entries(cfg)]


def gate_skips(cfg: dict, repo: Path, base: str, head: str) -> list[dict]:
    """The gate commands a checker of the diff base...head skips: each one with `paths` that the
    diff touches none of, by git's own pathspec matching. A git error is refused."""
    from factory import gitops  # local: compose is otherwise git-free
    return [{"command": cmd, "status": "SKIPPED",
             "reason": f"the diff {base[:9]}...{head[:9]} touches none of its paths: {', '.join(paths)}"}
            for cmd, paths in gate_entries(cfg)
            if paths and not gitops.git(repo, "diff", "--name-only", f"{base}...{head}", "--", *paths)]


def without_evidence(text: str) -> str:
    """A spec text without its `## Evidence` and `## Responses` sections. Each runs from its heading
    line (trailing spaces ignored) up to the next line starting `## ` or `=== `; a line inside a
    fenced code block neither starts nor ends a section."""
    out, cut = [], False
    for line, in_fence in specstore.lines_outside_fences(text):
        if not in_fence and line.startswith(("## ", "=== ")):
            cut = line.rstrip() in ("## Evidence", "## Responses")
        if not cut:
            out.append(line)
    return "\n".join(out) + ("\n" if out and text.endswith("\n") else "")


CAPABILITY_INDEX_NOTE = (
    "This list is complete: every current-truth capability not given in full above has one line here. Open a "
    "capability at its path before you rely on it. A spec that cites a capability's path, as "
    "`openspec/specs/<name>/spec.md`, sends that capability in full to the critic, so cite under Evidence each "
    "capability you open.")

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
    briefing = instance.require() / "context.md"
    if not briefing.is_file():
        raise store.Refused(f"{briefing} is missing: it is the role-context block every role reads first; "
                            "run factory init with FACTORY_STATE unset to create it from the template")
    parts = [briefing.read_text(encoding="utf-8").rstrip(),
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

    def add(rel: str, heading: str, edit=lambda text: text) -> None:
        p = root / rel
        if p.exists():
            sources.append(rel)
            parts.append(f"\n## {heading}\n\n{edit(p.read_text(encoding='utf-8')).rstrip()}\n")

    def add_spec(rel: str, heading: str) -> None:
        # Evidence and Responses serve the critic and the spec gate; the full file stays one read away
        add(rel, f"{heading}. Its Evidence and Responses sections are left out; the full spec is `{root / rel}`",
            without_evidence)

    version = t["spec"]["version"]
    rnd = t["round"]["spec"]

    def selected(spec_rel: str | None) -> set[str] | None:
        """The capabilities this role gets in full (doc §Harness, Spec store): triage's names plus
        those the spec it works from cites. None, meaning all of them, without a `Capabilities:` line."""
        names = triage_capabilities(root, tid)
        if names is None:
            return None
        spec = root / spec_rel if spec_rel else None
        return set(names) | set(cited_capabilities(root, spec.read_text(encoding="utf-8"))
                                if spec and spec.exists() else [])

    def add_truth(sel: set[str] | None) -> None:
        rest = []
        for p in current_truth(root):
            if sel is None or p.parent.name in sel:
                add(str(p.relative_to(root)), f"Current truth: {p.parent.name}")
            else:
                rest.append(p)
        if rest:
            parts.append("\n## Capability index: current truth not given in full above\n\n" + CAPABILITY_INDEX_NOTE
                         + "\n\n" + capability_index(rest))

    def add_decisions() -> None:
        # the whole log, whatever capabilities the ticket names: a standing decision often names no
        # capability, yet every ticket must follow it (#78). An empty log (the one `factory init`
        # creates) carries nothing, so it is no input.
        p = root / "decisions.md"
        if p.exists() and p.read_text(encoding="utf-8").strip():
            add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")
    if role == "triage":
        add(t["request"], "Request (raw, with any answers appended)")
        every = current_truth(root)
        if every:
            parts.append("\n## Capability index: every capability in current truth\n\nName the capabilities this "
                         "request touches on your `Capabilities:` line. The spec writer receives those in full and "
                         "this index for the rest.\n\n" + capability_index(every))
        prior = _runs_for(root, tid, "triage", run_id)
        if prior:
            add(f"runs/{prior[-1]}/output.md", "Your previous Triage output (the question you asked is answered above)")
    elif role == "spec_writer":
        tri = _runs_for(root, tid, "triage", run_id)
        if tri:
            add(f"runs/{tri[-1]}/output.md", "Ticket (Triage output)")
        add(t["request"], "Request (raw)")
        sel = selected(f"specs/{tid}/v{version}.md" if version >= 1 else None)
        add_truth(sel)
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
        sel = selected(f"specs/{tid}/v{version}.md")
        add_truth(sel)
        add_decisions()
        if rnd >= 2 and version >= 2:
            crit = _runs_for(root, tid, "critic", run_id)
            if crit:
                add(f"runs/{crit[-1]}/output.md", "Your prior findings (round %d)" % (rnd - 1))
            # the smaller of the diff and the previous version: a rewrite's diff outgrows the version
            prev_rel, cur_rel = f"specs/{tid}/v{version - 1}.md", f"specs/{tid}/v{version}.md"
            prev, cur = ((root / r).read_text(encoding="utf-8") if (root / r).exists() else ""
                         for r in (prev_rel, cur_rel))
            diff = "\n".join(difflib.unified_diff(prev.splitlines(), cur.splitlines(), prev_rel, cur_rel,
                                                  n=3, lineterm=""))
            if len(diff.encode()) < len(prev.encode()):
                add(prev_rel, f"Previous spec version (v{version - 1}), as a unified diff to v{version}",
                    lambda _: diff)
            else:
                add(prev_rel, f"Previous spec version (v{version - 1}), whole: the diff to v{version} is not smaller")
        for p in _approvals(root, tid, "ruling"):
            add(str(p.relative_to(root)), "Human ruling")
    elif role == "planner":
        av = t["spec"]["approved_version"]
        if av is None:
            raise store.Refused(f"{tid} has no approved spec version")
        add_spec(f"specs/{tid}/v{av}.md", f"Approved spec (v{av}, pinned)")
        add_decisions()  # no current truth for the planner, and the whole log
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
        # A checker of a sub-ticket gets the commands its diff skips (meta `gate_skipped`, set at run
        # start) apart from the ones to run; the implementer and the parent-close verifier have none.
        skipped = meta.get("gate_skipped") or []
        gone = {s["command"] for s in skipped}
        run = [g for (raw, paths), g in zip(gate_entries(cfg), gate_commands(cfg)) if paths is None or raw not in gone]
        where = (f"\n## Where you work\nWorktree: `{meta.get('worktree')}` (branch `{meta.get('branch')}`, "
                 f"base `{meta.get('base')}`, head `{meta.get('head')}`). There is no remote: commit on the "
                 f"branch; the PR is the branch plus the description you return. ")
        if role == "reviewer":  # the reviewer judges the diff; the verifier runs the gate (doc §6)
            where += "The verifier runs the gate commands on this head; you do not run them.\n"
        else:
            where += ("Gate commands (run each from your worktree, exactly as written; each is already wrapped): "
                      + ("; ".join(f"`{wrap(g, env)}`" for g in run) if run or not skipped
                         else "none (every gate command is skipped below)") + "\n")
        where += "".join(f"SKIPPED by the harness for this diff, do not run: `{s['command']}`: {s['reason']}\n"
                         for s in skipped)
        parts.append(where)
        if role == "implementer":
            if t.get("merge_refused"):
                parts.append("\n## This is a conflict run\nThe merge gate refused your branch: " + str(t["merge_refused"])
                             + ". The integration branch moved after you branched. Merge it into your branch, resolve any "
                             "conflict, re-run the gates, commit, and add one note on the resolution to the PR description. "
                             "Change nothing else.\n")
            add(f"specs/{tid}/subticket.md", f"Sub-ticket {tid}")
            add_spec(f"specs/{parent}/v{av}.md", f"Parent spec (v{av}, pinned)")
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
                add_spec(f"specs/{tid}/v{av}.md", f"Parent spec (v{av}, pinned): verify every scenario on main")
            else:
                add(f"specs/{tid}/subticket.md", f"Sub-ticket {tid}")
                add_spec(f"specs/{parent}/v{av}.md", f"Parent spec (v{av}, pinned)")
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
