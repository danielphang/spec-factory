"""`factory` store CLI (P0 subset of the build-harness spec, part B/K, plus the spec store).

Exit 0 success, 2 refused precondition (store unchanged, nothing logged), 1 error.
Every command prints one JSON object on stdout; refusals also print {"ok": false, "error"}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from factory import compose, gitops, instance, specstore, status, store, subtickets, tripwire
from factory.store import Refused

ROLES = ("triage", "spec_writer", "critic", "planner", "implementer", "reviewer", "verifier")
BUILD_ROLES = ("implementer", "reviewer", "verifier")
PROMPTS = Path(__file__).resolve().parent / "prompts"


def out(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def _rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


# ----- ticket -----------------------------------------------------------------

def _frontmatter(text: str, src: Path) -> dict:
    """A request's optional YAML header between a leading `---` line and the next `---` line.
    {} when there is none; Refused when it is unterminated, does not parse, or is not a mapping."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, ln in enumerate(lines[1:], 1) if ln.strip() == "---"), None)
    if end is None:
        raise Refused(f"{src}: frontmatter opened with --- but never closed")
    try:
        fm = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as e:
        first = str(e).splitlines()[0]
        raise Refused(f"{src}: frontmatter is not valid YAML ({first}); quote a value that contains ': '")
    if fm is None:
        return {}
    if not isinstance(fm, dict):
        raise Refused(f"{src}: frontmatter must be a YAML mapping (key: value lines)")
    return fm


def ticket_new(a, root, cfg):
    src = Path(a.file).expanduser().resolve()
    if not src.exists():
        raise Refused(f"no such file {src}")
    text = src.read_text(encoding="utf-8")
    fm = _frontmatter(text, src)  # refuse a bad header before anything is written
    h = store.content_hash(text)
    idx = store.load_index(root)
    for tid, rec in idx.items():
        if rec.get("hash") == h and not a.force:
            raise Refused(f"already imported as {tid} (same content); use --force to import again")
    tid = store.next_ticket_id(root)
    rel = f"requests/{tid}.md"
    store.write_text(root / rel, text)
    title = str(fm["title"]).strip() if fm.get("title") else \
        next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("#")), src.stem)
    t = store.new_ticket(root, tid, title, rel, str(src))
    store.save_ticket(root, t)
    idx[tid] = {"source": str(src), "hash": h, "imported": store.now()}
    store.write_yaml(store.index_path(root), idx)
    store.log_event(root, "request.created", ticket=tid, source=str(src))
    store.log_event(root, "ticket.created", ticket=tid, status=t["status"])
    out({"ok": True, "id": tid, "title": title, "state": t["status"]})


def ticket_show(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if a.json:
        out({"ok": True, "id": t["id"], "state": t["status"], "round": t["round"], "title": t["title"],
             "type": t["type"], "spec": t["spec"], "in_flight": t["in_flight"], "parked": t["parked"],
             "parent": t.get("parent"), "label": t.get("label"), "depends_on": t.get("depends_on", []),
             "parallel_safe": t.get("parallel_safe", True), "branch": t.get("branch"), "head": t.get("head"),
             "merge": t.get("merge"), "parent_base": t.get("parent_base")})
    else:
        sys.stdout.write(yaml.safe_dump(t, sort_keys=False, allow_unicode=True))


def _set_dotted(obj: dict, key: str, value) -> None:
    parts = key.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            raise Refused(f"unknown key {key}")
        cur = cur[p]
    if parts[-1] not in cur:
        raise Refused(f"unknown key {key}")
    cur[parts[-1]] = value


def ticket_set(a, root, cfg):
    t = store.load_ticket(root, a.id)
    was_in_flight = list(t.get("in_flight") or [])
    changes = {}
    for kv in a.assignments:
        if "=" not in kv:
            raise Refused(f"expected key=value, got {kv}")
        k, v = kv.split("=", 1)
        val = yaml.safe_load(v) if v != "" else None
        _set_dotted(t, k, val)
        changes[k] = val
    store.save_ticket(root, t)
    store.log_event(root, "ticket.set", ticket=t["id"], changes=changes)
    res = {"ok": True, "id": t["id"], "changes": changes}
    for rid in was_in_flight:  # a run dropped by hand is compared now, as run finish would
        if rid not in (t.get("in_flight") or []):
            tw = tripwire.compare(root, rid, t["id"])
            if tw and tw["parked"]:
                res["parked"] = tw["parked"]
    out(res)


def _apply_round(t: dict, op: str | None, cfg: dict) -> None:
    if not op:
        return
    m = re.fullmatch(r"(spec|pr):(init|\+1|reset)", op)
    if not m:
        raise Refused(f"bad --round {op}; expected spec|pr:init|+1|reset")
    loop, act = m.groups()
    cur = t["round"][loop]
    mx = cfg["max_rounds"][loop]
    if act == "init":
        if cur == 0:
            t["round"][loop] = 1
    elif act == "+1":
        if cur + 1 > mx:
            raise Refused(f"round.{loop} {cur} is at max_rounds {mx}")
        t["round"][loop] = cur + 1
    else:
        t["round"][loop] = 0


def _check_edge(cfg: dict, frm: str, to: str) -> None:
    if to not in cfg["routing"].get(frm, []):
        raise Refused(f"no route {frm} → {to}: not a routing edge")


def ticket_transition(a, root, cfg):
    t = store.load_ticket(root, a.id)
    frm = t["status"]
    _check_edge(cfg, frm, a.to)
    verified_by = None
    if a.to == "closed" and store.subtickets_of(root, t["id"]):
        # A parent closes through its parent-close run (then archive). A human who wants it closed
        # without one says so with `resolve --close`.
        verified_by = _parent_close_verified(root, cfg, t)
        if not verified_by:
            raise Refused(f"{t['id']} has sub-tickets: it closes after a VERIFIED parent-close run (or `resolve {t['id']} --close`)")
        if specstore.is_active(root) and specstore.change_dir(root, t["id"]).exists():
            raise Refused(f"{t['id']} is verified but not archived: run `archive {t['id']}` first")
    _apply_round(t, a.round, cfg)
    t["status"] = a.to
    if a.to != "parked":
        t["parked"] = None
    t["history"].append({"ts": store.now(), "from": frm, "to": a.to, "by": a.by, "round": dict(t["round"]),
                         **({"verified_by": verified_by} if verified_by else {})})
    store.save_ticket(root, t)
    store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": a.to, "by": a.by, "round": t["round"]})
    out({"ok": True, "id": t["id"], "state": t["status"], "round": t["round"]})


def ticket_park(a, root, cfg):
    t = store.load_ticket(root, a.id)
    frm = t["status"]
    if frm in ("closed", "parked"):
        raise Refused(f"{t['id']} is {frm}; cannot park")
    store.park_ticket(root, t, a.reason, [x for x in (a.outputs or "").split(",") if x], a.question)
    out({"ok": True, "id": t["id"], "state": "parked", "reason": a.reason})


# ----- runs ---------------------------------------------------------------------

def _run_dir(root: Path, rid: str) -> Path:
    d = root / "runs" / rid
    if not (d / "meta.yaml").exists():
        raise Refused(f"no run {rid}")
    return d


def run_start(a, root, cfg):
    if a.role not in ROLES:
        raise Refused(f"unknown role {a.role}; roles: {', '.join(ROLES)}")
    t = store.load_ticket(root, a.ticket)
    parent_close = a.role == "verifier" and t["status"] == "ready-for-parent-verify"
    ready = cfg["ready_state"][a.role]
    if t["status"] != ready and not parent_close:
        raise Refused(f"{t['id']} is {t['status']}, not {ready}")
    if a.role == "implementer" and t["in_flight"]:
        raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
    if a.role in ("reviewer", "verifier") and any(a.role in r for r in t["in_flight"]):
        raise Refused(f"{t['id']} already has a {a.role} run in flight")
    if a.role in ("triage", "spec_writer", "critic", "planner") and t["in_flight"]:
        raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
    if a.role == "implementer" and t.get("parent"):
        _check_drift(root, cfg, t)
        _check_sibling_tests(root, cfg, t)
    if a.role in BUILD_ROLES:
        compose.gate_entries(cfg)  # a malformed gate entry refuses here, before a run id is reserved
        compose.environment_sync(cfg)  # so does a malformed environment_sync
    baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
    rid = store.next_run_id(root, a.role)
    model = a.model or cfg["models"][a.role]
    d = root / "runs" / rid
    meta = {"run_id": rid, "role": a.role, "ticket": t["id"], "model": model, "round": t["round"]["spec"],
            "spec_version": t["spec"]["version"], "started": store.now(), "finished": None,
            "wall_s": None, "status": "running", "input_sources": None}
    if a.role in BUILD_ROLES:
        _start_build_run(root, cfg, t, meta, d, parent_close)
    store.write_yaml(d / "meta.yaml", meta)
    store.ensure_gitignore(root)
    store.ensure_gitattributes(root)
    (d / "scratch").mkdir(exist_ok=True)
    if baseline:
        store.write_yaml(d / "tripwire.yaml", baseline)
    prompt_name = a.role
    preamble = instance.fill_preamble((PROMPTS / "preamble.md").read_text(encoding="utf-8"), cfg)
    role_prompt = instance.fill_standards((PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8"))
    sysp = preamble.rstrip() + "\n\n" + role_prompt
    store.write_text(d / "system-prompt.txt", sysp)
    t["in_flight"].append(rid)
    store.save_ticket(root, t)
    store.log_event(root, "run.started", ticket=t["id"], run=rid, role=a.role, model=model)
    out({"ok": True, "run_id": rid, "role": a.role, "model": model, "worktree": meta.get("worktree"), "head": meta.get("head")})


def _check_sibling_tests(root: Path, cfg: dict, t: dict) -> None:
    """Doc §Harness, "Tests a sibling added": each file the sub-ticket's "Tests to change" lists as
    added by a sibling must be absent at the parent's base, and first added on the integration
    branch by a commit inside one merged sibling's recorded merge (reachable from its main_after,
    not from its base_before). Else refused, so the build parks the sub-ticket as BLOCKED."""
    sub = root / "specs" / t["id"] / "subticket.md"
    paths = subtickets.sibling_tests(sub.read_text(encoding="utf-8")) if sub.exists() else []
    if not paths:
        return
    parent = store.load_ticket(root, t["parent"])
    base = parent.get("parent_base")
    repo = gitops.repo_root(cfg)
    tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
    merges = [s["merge"] for s in store.subtickets_of(root, parent["id"])
              if s["id"] != t["id"] and s["status"] == "merged"
              and (s.get("merge") or {}).get("main_after") and s["merge"].get("base_before")]
    for path in paths:
        added = gitops.first_added(repo, base, tip, path) if base else None
        if added and any(gitops.head_contains(repo, m["main_after"], added)
                         and not gitops.head_contains(repo, m["base_before"], added) for m in merges):
            continue
        since = f"since {base[:9]}" if base else "(no sibling has merged)"
        raise Refused(f"BLOCKED from harness: Tests to change lists {path} as added by a sibling, but no merged "
                      f"sibling of {parent['id']} added it {since}; list it in the parent spec's Tests to change, "
                      f"or remove it")


TEST_FILE_RE = re.compile(r"(^|/)test_[^/]*$|_test\.[A-Za-z0-9]+$|\.test\.[A-Za-z0-9]+$")
TICK_RE = re.compile(r"`([^`\n]+)`")


def _check_drift(root: Path, cfg: dict, t: dict) -> None:
    """Doc §Harness, "Spec drift": before a sub-ticket's first implementer run (none finished, no
    ruling on file), refuse when its Acceptance names an unmerged sibling of the current plan that it
    does not depend on, or when a test file changed on the integration branch since the parent's
    approved version was written, by a first-parent commit that also changed a file the version's
    design names, and no Tests to change list names it. The build parks the refusal as BLOCKED."""
    tid = t["id"]
    if compose._runs_for(root, tid, "implementer", "") or list((root / "approvals" / tid).glob("ruling-*")):
        return
    sub = root / "specs" / tid / "subticket.md"
    sub_text = sub.read_text(encoding="utf-8") if sub.exists() else ""
    parent = store.load_ticket(root, t["parent"])
    findings = _sibling_drift(root, t, parent, sub_text) + _test_drift(root, cfg, parent, sub_text)
    if findings:
        raise Refused(f"BLOCKED from harness: spec drift: {'; '.join(findings)}. Amend the spec "
                      f"(`spec amend {parent['id']}`) or rule (`resolve {tid} --ruling F`)")


def _sibling_drift(root: Path, t: dict, parent: dict, sub_text: str) -> list[str]:
    """The sibling rule: each current sibling, not merged and outside the sub-ticket's dependency
    closure, whose id or plan label is a whole token of its Acceptance field."""
    current = {s["id"]: s for s in subtickets.split_plan(store.subtickets_of(root, parent["id"]))[0]}
    closure, todo = set(), list(t.get("depends_on") or [])
    while todo:
        dep = todo.pop()
        if dep not in closure:
            closure.add(dep)
            todo += (current.get(dep) or {}).get("depends_on") or []
    acceptance = subtickets.field_text(sub_text, "acceptance")
    findings = []
    for s in current.values():
        if s["id"] == t["id"] or s["status"] == "merged" or s["id"] in closure:
            continue
        if any(re.search(rf"(?<![\w.-]){re.escape(tok)}(?![\w-]|\.\d)", acceptance)
               for tok in (s["id"], s.get("label")) if tok):
            findings.append(f"its Acceptance names {s['id']} ({s['status']}), which has not merged and is not "
                            "one of its dependencies")
    return findings


def _test_drift(root: Path, cfg: dict, parent: dict, sub_text: str) -> list[str]:
    """The test rule, counted from the integration head recorded with the parent's approved version.
    No record (a version stored before the record existed), a null head or one that is not a commit
    in the target repo: no findings."""
    n = parent["spec"]["approved_version"]
    rec = root / "specs" / parent["id"] / f"v{n}.yaml"
    base = (store.read_yaml(rec) or {}).get("integration_head") if rec.exists() else None
    if not base:
        return []
    repo = gitops.repo_root(cfg)
    if not gitops.git(repo, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", check=False):
        return []
    tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
    design = dict(specstore.split_parts((root / "specs" / parent["id"] / f"v{n}.md").read_text(encoding="utf-8")))
    design_text = design.get("design.md", "")
    at_tip = set(gitops.git(repo, "ls-tree", "-r", "--name-only", tip).splitlines())
    named = {p for p in TICK_RE.findall(design_text)
             if p in at_tip and not TEST_FILE_RE.search(p) and not p.endswith(".md")}
    if not named:
        return []
    listed_text = subtickets.field_text(sub_text, "tests to change") + "\n" + _tests_to_change_section(design_text)
    listed = {p.split("::", 1)[0] for p in TICK_RE.findall(listed_text)}
    last: dict[str, str] = {}
    # factory: one git diff per first-parent commit since the spec was written; fold into one
    # `git log --diff-merges=first-parent --name-only` call if that range grows to hundreds of commits
    for c in gitops.git(repo, "rev-list", "--first-parent", "--reverse", f"{base}..{tip}").split():
        files = gitops.git(repo, "diff", "--name-only", "--no-renames", f"{c}^1", c, check=False).splitlines()
        if named.intersection(files):
            for f in files:
                if TEST_FILE_RE.search(f) and f not in listed:
                    last[f] = c
    return [f"{f} changed by {c[:9]} since spec v{n} was written at {base[:9]}" for f, c in last.items()]


def _tests_to_change_section(design_text: str) -> str:
    """The design part's `## Tests to change` section, up to the next heading outside a fence."""
    lines, inside = [], False
    for line, in_fence in specstore.lines_outside_fences(design_text):
        if specstore._heading(line, in_fence):
            inside = line.strip() == "## Tests to change"
            continue
        if inside:
            lines.append(line)
    return "\n".join(lines)


def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent_close: bool) -> None:
    """Worktrees for the build roles (build spec I.3, local stand-in): the implementer gets the
    ticket's branch (created from the integration branch at first dispatch); each checker gets a
    detached checkout of the head it checks, plus the diff written as runs/<id>/diff.patch. Each
    checkout then runs the instance's `environment_sync`, if set (`_sync_environment`)."""
    sync = compose.environment_sync(cfg)
    repo = gitops.repo_root(cfg)
    integ = gitops.integration_branch(cfg, repo)
    store.ensure_gitignore(root)
    meta["round"] = t["round"]["pr"]
    meta["gate_skipped"] = []  # only a checker of a sub-ticket's diff skips a gate command
    if meta["role"] == "implementer":
        branch = t.get("branch") or gitops.branch_of(t["id"])
        wt = root / "worktrees" / t["id"]
        if not wt.exists():
            gitops.add_worktree(repo, wt, branch, integ, new_branch=t.get("branch") is None)
        t["branch"] = branch
        meta.update({"branch": branch, "base": gitops.rev(repo, integ), "head": gitops.rev(repo, branch),
                     "worktree": str(wt), "resolution": "conflict" if t.get("merge_refused") else None,
                     "environment_files": gitops.copy_environment_files(cfg, repo, wt)})
        _sync_environment(cfg, sync, meta, repo, wt, d, checker=False)
    else:
        head = gitops.rev(repo, integ) if parent_close else t.get("head")
        base = (t.get("parent_base") or head) if parent_close else gitops.rev(repo, integ)
        if not head:
            raise Refused(f"{t['id']} has no head to check")
        if not parent_close:
            meta["gate_skipped"] = compose.gate_skips(cfg, repo, base, head)
        wt = d / "wt"
        gitops.add_detached_worktree(repo, wt, head)
        meta["environment_files"] = gitops.copy_environment_files(cfg, repo, wt)
        _sync_environment(cfg, sync, meta, repo, wt, d, checker=True)
        if not parent_close:
            store.write_text(d / "diff.patch", gitops.diff(repo, base, head))
        meta.update({"branch": t.get("branch"), "base": base, "head": head, "worktree": str(wt)})


def _sync_environment(cfg: dict, sync: str | None, meta: dict, repo: Path, wt: Path, d: Path, checker: bool) -> None:
    """Run the instance's `environment_sync` in the checkout `wt` through the running-code wrapper and
    record it in `meta`. A failure writes runs/<id>/environment-sync.log, removes a checker's checkout,
    and refuses the run start with one line that carries neither the command nor its output."""
    if sync is None:
        return
    cp = subprocess.run(["sh", "-c", compose.wrap(sync, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)
    if cp.returncode == 0:
        meta["environment_sync"] = sync
        return
    log = d / "environment-sync.log"
    store.write_text(log, f"command: {sync}\nexit: {cp.returncode}\n--- stdout\n{cp.stdout}--- stderr\n{cp.stderr}")
    if checker:
        gitops.remove_worktree(repo, wt)
    raise Refused(f"environment_sync failed (exit {cp.returncode}) in {wt}; its command and output are in {log}")


def run_last_message(a, root, cfg):
    """Keep the agent's last message with a run that ended EMPTY-OUTPUT, so a human can see why."""
    d = _run_dir(root, a.run)
    st = store.read_yaml(d / "meta.yaml").get("status")
    if st != "EMPTY-OUTPUT":
        raise Refused(f"{a.run} is {st or 'not finished'}, not EMPTY-OUTPUT: no last message to keep")
    store.write_text(d / "last-message.md", a.text + "\n")
    out({"ok": True, "run_id": a.run, "last_message": _rel(root, d / "last-message.md")})


def run_cleanup(a, root, cfg):
    d = _run_dir(root, a.run)
    meta = store.read_yaml(d / "meta.yaml")
    wt = Path(meta.get("worktree") or "")
    if meta.get("role") in ("reviewer", "verifier") and wt.exists():
        gitops.remove_worktree(gitops.repo_root(cfg), wt)
    out({"ok": True, "run_id": a.run, "removed": str(wt) if wt else None})


def run_compose(a, root, cfg):
    d = _run_dir(root, a.run)
    meta = store.read_yaml(d / "meta.yaml")
    t = store.load_ticket(root, meta["ticket"])
    text, sources = compose.compose(root, cfg, meta, t)
    store.write_text(d / "input.md", text)
    meta["input_sources"] = sources
    store.write_yaml(d / "meta.yaml", meta)
    out({"ok": True, "run_id": a.run, "input": _rel(root, d / "input.md"), "sources": sources})


def run_finish(a, root, cfg):
    d = _run_dir(root, a.run)
    meta = store.read_yaml(d / "meta.yaml")
    if meta.get("finished"):
        raise Refused(f"{a.run} already finished")
    t = store.load_ticket(root, meta["ticket"])
    if a.output_file:
        src = sys.stdin.read() if a.output_file == "-" else Path(a.output_file).read_text(encoding="utf-8")
        store.write_text(d / "output.md", src)
    text = (d / "output.md").read_text(encoding="utf-8") if (d / "output.md").exists() else ""
    if a.status_override:
        parsed = {"status": a.status_override, "confidence": None, "escalations": []}
    elif not text.strip():
        # The agent call reports no reason a run stopped, so an empty output is never a budget kill.
        parsed = {"status": "EMPTY-OUTPUT", "confidence": None, "escalations": [], "error": "empty output"}
    else:
        parsed = status.parse(text)
        if parsed["status"] is None:
            parsed = {**parsed, "status": "UNKNOWN", "escalations": []}
    started = dt.datetime.fromisoformat(meta["started"])
    fin = dt.datetime.fromisoformat(store.now())
    meta.update({"finished": fin.isoformat(), "wall_s": int((fin - started).total_seconds()),
                 "status": parsed["status"], "confidence": parsed.get("confidence"),
                 "escalations": parsed.get("escalations", []),
                 "escalations_note": parsed.get("escalations_note")})
    store.write_yaml(d / "meta.yaml", meta)
    if a.run in t["in_flight"]:
        t["in_flight"].remove(a.run)
    if meta["role"] == "triage" and parsed["status"] == "ACCEPT":
        for ln in text.splitlines():
            if ln.startswith("Title:") and ln.split(":", 1)[1].strip():
                t["title"] = ln.split(":", 1)[1].strip()
            if ln.startswith("Type:") and ln.split(":", 1)[1].strip():
                t["type"] = ln.split(":", 1)[1].strip().split()[0].strip(" |")
    store.save_ticket(root, t)
    ev = "run.killed" if parsed["status"] == "KILLED" else "run.finished"
    store.log_event(root, ev, ticket=t["id"], run=a.run, role=meta["role"], status=parsed["status"], wall_s=meta["wall_s"])
    if parsed.get("escalations"):
        store.log_event(root, "escalation.queued", ticket=t["id"], run=a.run, items=parsed["escalations"])
    res = {"ok": True, "run_id": a.run, "status": parsed["status"], "confidence": parsed.get("confidence"),
           "escalations": parsed.get("escalations", [])}
    tw = tripwire.compare(root, a.run, t["id"])
    if tw:
        res["tripwire"] = {"park": tw["park"], "escalate": tw["escalate"]}
        if tw["parked"]:
            res["parked"] = tw["parked"]
    out(res)


# ----- spec / plan ----------------------------------------------------------------

def _text_from(a, root) -> str:
    if a.from_run:
        d = _run_dir(root, a.from_run)
        p = d / "output.md"
        if not p.exists():
            raise Refused(f"{a.from_run} has no output.md")
        return status.strip_trailer(p.read_text(encoding="utf-8"))
    if a.file:
        return Path(a.file).read_text(encoding="utf-8")
    raise Refused("need --from-run RUN or --file F")


def _integration_head(cfg: dict) -> str | None:
    """The integration branch's head in the target repo, or None when the repo or branch does not resolve."""
    try:
        repo = gitops.repo_root(cfg)
        return gitops.rev(repo, gitops.integration_branch(cfg, repo))
    except (Refused, OSError):
        return None


def _add_spec_version(root: Path, t: dict, text: str, source: str, cfg: dict) -> int:
    """Write the next spec version, and beside it `v<n>.yaml` with the integration head it was written
    against, which the spec drift check counts from (doc §Harness, Spec drift)."""
    n = t["spec"]["version"] + 1
    store.write_text(root / "specs" / t["id"] / f"v{n}.md", text)
    store.write_yaml(root / "specs" / t["id"] / f"v{n}.yaml", {"integration_head": _integration_head(cfg)})
    store.write_text(root / "specs" / f"{t['id']}.md", text)
    t["spec"]["version"] = n
    store.save_ticket(root, t)
    store.log_event(root, "spec.added", ticket=t["id"], version=n, source=source)
    return n


def spec_add(a, root, cfg):
    t = store.load_ticket(root, a.id)
    n = _add_spec_version(root, t, _text_from(a, root), a.from_run or a.file, cfg)
    out({"ok": True, "id": t["id"], "version": n, "path": f"specs/{t['id']}/v{n}.md"})


def _restart_note(root: Path, t: dict) -> str:
    """What a restart keeps (merged sub-tickets) and discards (the rest not closed), and its two routes."""
    subs = store.subtickets_of(root, t["id"])
    kept = [f"{s['id']} / {s['title']} (merge {((s.get('merge') or {}).get('main_after') or '')[:9] or 'not recorded'})"
            for s in subs if s["status"] == "merged"]
    lost = [f"{s['id']} / {s['title']}: {s['status']}" + (f", branch {s['branch']}" if s.get("branch") else "")
            for s in subs if s["status"] not in ("merged", "closed")]
    tid = t["id"]
    return (f"Restart instead of amending. Merged, and their merge commits stay on the integration branch: "
            f"{'; '.join(kept) or 'none'}. Not merged, which a restart discards: {'; '.join(lost) or 'none'}. "
            f"To re-spec and re-plan: `factory ticket park {tid} --reason \"<why>\"`, `factory resolve {tid} "
            f"--to spec-gate`, then `factory approve-spec {tid} --edit F`; the new plan supersedes the unmerged "
            f"sub-tickets. To close and re-file: `factory resolve {tid} --close`, then `factory ticket new --file F`. "
            "The factory never restarts by itself.")


def spec_amend(a, root, cfg):
    """`spec amend PARENT --file F --reason LINE --intent unchanged`: a human writes F as the next spec
    version and makes it the approved one, re-pinning the change folder and keeping its tasks.md.
    Doc §Harness, Spec store. Every refusal comes before the first write."""
    t = store.load_ticket(root, a.id)
    tid, av = t["id"], t["spec"]["approved_version"]
    if t.get("parent"):
        raise Refused(f"{tid} is a sub-ticket; amend its parent's spec: spec amend {t['parent']}")
    if t["status"] == "awaiting-spec-gate":
        raise Refused(f"{tid} is awaiting-spec-gate; amend it at the gate with approve-spec {tid} --edit F")
    if av is None:
        raise Refused(f"{tid} has no approved spec to amend")
    if t["status"] == "closed":
        raise Refused(f"{tid} is closed")
    reason = (a.reason or "").strip()
    if not reason or len(reason.splitlines()) > 1:
        raise Refused("--reason is one non-blank line of text")
    subs = store.subtickets_of(root, tid)
    runs = [r for x in (t, *subs) for r in x.get("in_flight") or []]
    if runs:
        raise Refused(f"{tid} has runs in flight on it or its sub-tickets: {', '.join(runs)}; amend once they finish")
    if a.intent == "changed":
        raise Refused(f"intent changed: an amendment keeps the spec's intent, so --intent changed is never "
                      f"applied. {_restart_note(root, t)}")
    old = (root / "specs" / tid / f"v{av}.md").read_text(encoding="utf-8")
    text = Path(a.file).read_text(encoding="utf-8")
    changes = specstore.intent_changes(old, text)
    if changes:
        raise Refused(f"intent changed ({'; '.join(changes)}). --intent unchanged keeps the Problem section, "
                      "every Decisions line, and each requirement's name, operation and statement; scenarios, "
                      f"their setup, Evidence, design text and Tests to change may change. {_restart_note(root, t)}")
    if specstore.is_active(root):
        if not specstore.change_dir(root, tid).exists():
            raise Refused(f"{tid} has no change folder ({_rel(root, specstore.change_dir(root, tid))}): "
                          "it was archived, so its spec can no longer be amended")
        _, deltas, errors = specstore.validate(text)
        errors += specstore.applies(root, deltas) if not errors else []
        if errors:
            raise Refused("spec not amended: " + "; ".join(errors))
    n = _add_spec_version(root, t, text, f"amend {a.file}", cfg)
    if specstore.is_active(root):
        tasks = specstore.change_dir(root, tid) / "tasks.md"
        kept = tasks.read_text(encoding="utf-8") if tasks.exists() else None
        specstore.pin(root, tid, text)
        if kept is not None:
            store.write_text(tasks, kept)
    t["spec"]["approved_version"] = n
    store.save_ticket(root, t)
    for s in subs:
        if s["status"] not in ("merged", "closed"):
            s["spec"] = {"version": n, "approved_version": n}  # planned_from stays: no plan is superseded
            store.save_ticket(root, s)
    ob, nb = specstore.scenario_blocks(old), specstore.scenario_blocks(text)
    scen = ([f"- changed: {k}" for k in nb if k in ob and ob[k] != nb[k]] + [f"- added: {k}" for k in nb if k not in ob]
            + [f"- removed: {k}" for k in ob if k not in nb])
    merged = [f"- {s['id']} / {s['title']}: merged" for s in subs if s["status"] == "merged"]
    diff = "".join(difflib.unified_diff(old.splitlines(keepends=True), text.splitlines(keepends=True),
                                        f"specs/{tid}/v{av}.md", f"specs/{tid}/v{n}.md")).rstrip("\n")
    fence = "```"
    while fence in diff:  # the spec's own fences must not close the record's
        fence += "`"
    d = _approval_dir(root, tid)
    rec = d / f"amendment-{_next_n(d, 'amendment')}.md"
    store.write_text(rec, "\n\n".join([
        f"# {tid}: spec amended, v{av} to v{n}", f"By {_by()} at {store.now()}.", f"Reason: {reason}",
        "Intent: unchanged", "## Scenarios changed", "\n".join(scen) or "none",
        "## Sub-tickets merged before this amendment", "\n".join(merged) or "none",
        "## Diff", f"{fence}diff\n{diff}\n{fence}"]) + "\n")
    store.log_event(root, "spec.amended", ticket=tid, by=_by(), previous=av, version=n, reason=reason,
                    record=_rel(root, rec))
    out({"ok": True, "id": tid, "version": n, "record": _rel(root, rec)})


def plan_add(a, root, cfg):
    t = store.load_ticket(root, a.id)
    text = _text_from(a, root)
    rel = f"plans/{t['id']}.md"
    store.write_text(root / rel, text)
    t["plan"] = rel
    store.save_ticket(root, t)
    store.log_event(root, "plan.added", ticket=t["id"], source=a.from_run or a.file)
    out({"ok": True, "id": t["id"], "path": rel})


# ----- build half: sub-tickets, results, merge (parts B, D, G; local stand-in) -------------------

def _recorded_plan_run(root: Path, tid: str) -> str:
    """The run named by the ticket's latest `plan.added` event, when that is a run of this store."""
    source = None
    for p in sorted((root / "log").glob("*.jsonl")):
        for ln in p.read_text(encoding="utf-8").splitlines():
            e = json.loads(ln)
            if e.get("event") == "plan.added" and e.get("ticket") == tid:
                source = e.get("source")
    if not source or "/" in source or not (root / "runs" / source / "meta.yaml").exists():
        raise Refused(f"no recorded planner run found for {tid} (latest plan.added source: {source or 'none'}); "
                      "pass --run RUN or --file F")
    return source


def subticket_add(a, root, cfg):
    parent = store.load_ticket(root, a.id)
    if parent["spec"]["approved_version"] is None:
        raise Refused(f"{parent['id']} has no approved spec")
    if not a.run and not a.file:
        a.run = _recorded_plan_run(root, parent["id"])
    if a.run:
        d = _run_dir(root, a.run)
        meta = store.read_yaml(d / "meta.yaml")
        if meta.get("ticket") != parent["id"] or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
            raise Refused(f"{a.run} is not a PLANNED planner run of {parent['id']}")
        text = status.strip_trailer((d / "output.md").read_text(encoding="utf-8"))
    else:
        text = Path(a.file).read_text(encoding="utf-8")
    existing = store.subtickets_of(root, parent["id"])
    try:
        subs = subtickets.parse(text, parent["id"], [s["id"] for s in existing])
    except ValueError as e:
        raise Refused(str(e)) from None
    if not subs:
        raise Refused("no sub-tickets found (a head line `<id> / Title`, id like T-0001-A, ST-1 or T-0001.1, "
                      "then `Depends on:` and `Parallel-safe:`)")
    ids = {s["id"] for s in subs}
    av = parent["spec"]["approved_version"]
    before = {s["id"] for s in subtickets.split_plan(existing)[1]}
    after = subtickets.superseded_by_plan(existing, av)
    for sdef in subs:
        for dep in sdef["depends_on"]:
            if dep in after:  # never dispatched, so the dependant would wait forever
                raise Refused(f"{sdef['id']} ({sdef['label']}) depends on {dep}, which this plan supersedes")
            if dep not in ids and not store.ticket_path(root, dep).exists():
                raise Refused(f"{sdef['id']} ({sdef['label']}) depends on {dep}, which is neither in this plan nor a ticket in the store")
        if store.ticket_path(root, sdef["id"]).exists():
            raise Refused(f"{sdef['id']} already exists")
    made = _create_subtickets(root, parent, subs, f"plan:{a.run or a.file}")
    superseded = [i for i in after if i not in before]
    if superseded:
        store.log_event(root, "subtickets.superseded", ticket=parent["id"], subtickets=superseded, approved_version=av)
    out({"ok": True, "parent": parent["id"], "subtickets": made, "superseded": superseded})


def _create_subtickets(root: Path, parent: dict, subs: list[dict], source: str) -> list[dict]:
    """Write each checked sub-ticket definition as a ticket record under `parent`, with its text at
    specs/<id>/subticket.md; returns them as `subticket add` prints them."""
    made = []
    for sdef in subs:
        st = store.new_ticket(root, sdef["id"], sdef["title"], parent["request"], source)
        st.update({"type": "sub-ticket", "parent": parent["id"], "label": sdef["label"], "depends_on": sdef["depends_on"],
                   "parallel_safe": sdef["parallel_safe"],
                   "status": "ready-for-implementer" if not sdef["depends_on"] else "waiting-dependencies"})
        st["spec"] = {"version": parent["spec"]["version"], "approved_version": parent["spec"]["approved_version"]}
        st["planned_from"] = parent["spec"]["approved_version"]  # never changed afterwards, unlike `spec`
        store.write_text(root / "specs" / sdef["id"] / "subticket.md", sdef["text"])
        store.save_ticket(root, st)
        store.log_event(root, "ticket.created", ticket=sdef["id"], parent=parent["id"], status=st["status"])
        made.append({"id": sdef["id"], "label": sdef["label"], "state": st["status"], "depends_on": sdef["depends_on"], "parallel_safe": sdef["parallel_safe"]})
    return made


WHOLE_SPEC_REASON = "one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run"
SEAM_HEADING_RE = re.compile(r"^#{2,3}\s")


def _planner_needed(root: Path, t: dict, spec_text: str) -> str | None:
    """The first reason the parent needs a planner run, or None when the approved spec becomes one
    sub-ticket as it stands (doc §Routing table, Human spec gate row)."""
    subs = store.subtickets_of(root, t["id"])
    if subs:
        return f"it already has sub-tickets: {', '.join(s['id'] for s in subs)}"
    planned = compose._runs_for(root, t["id"], "planner", "")
    if planned:
        return f"a planner already ran on it: {planned[-1]}"
    writer = compose._last_run_meta(root, t["id"], "spec_writer", "")
    if writer and writer.get("status") == "NEEDS-SPLIT":
        return f"its spec writer marked it NEEDS-SPLIT ({writer['run_id']})"
    for line, in_fence in specstore.lines_outside_fences(spec_text):
        if (not in_fence and SEAM_HEADING_RE.match(line) and not line.startswith("### Requirement:")
                and re.search(r"\bseams?\b", line, re.I)):
            return f"its approved spec has a seam heading: {line.strip()}"
    return None


def plan_whole_spec(a, root, cfg):
    """`plan whole-spec PARENT`: when the approved spec needs one sub-ticket, create it from the
    whole spec in place of a planner run; otherwise report why the planner is needed, writing nothing."""
    t = store.load_ticket(root, a.id)
    if t["status"] != "ready-for-planner":
        raise Refused(f"{t['id']} is {t['status']}, not ready-for-planner")
    if t["in_flight"]:
        raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
    av = t["spec"]["approved_version"]
    spec = root / "specs" / t["id"] / f"v{av}.md"
    if av is None or not spec.exists():
        raise Refused(f"{t['id']} has no approved spec")
    spec_text = spec.read_text(encoding="utf-8")
    reason = _planner_needed(root, t, spec_text)
    if reason:
        out({"ok": True, "id": t["id"], "planner": "needed", "reason": reason})
        return
    if specstore.is_active(root) and not specstore.change_dir(root, t["id"]).exists():
        raise Refused(f"{t['id']} has no change folder (no pinned version)")
    sid = f"{t['id']}.1"
    names = "".join(f"- {n}\n" for n in specstore.scenario_names(spec_text))
    text = (f"{sid} / {t['title']}\nDepends on: none\nParallel-safe: yes\n\n"
            f"Parent: {t['id']}, approved spec v{av}. This sub-ticket is the whole of it; read it in full. "
            f"The planner was skipped: {WHOLE_SPEC_REASON}.\n\n"
            "Scope: every lettered part of the parent's Proposed change.\n"
            "Acceptance: every scenario of the parent spec, with the label its verification.md gives it:\n"
            f"{names}Tests to change: the parent's list.\nProtected paths: the parent's Risk list.\n")
    made = _create_subtickets(root, t, [{"id": sid, "title": t["title"], "label": "whole-spec", "depends_on": [],
                                          "parallel_safe": True, "text": text}], "plan:whole-spec")
    rel = f"plans/{t['id']}.md"
    store.write_text(root / rel, text)
    t["plan"] = rel
    store.save_ticket(root, t)
    if specstore.is_active(root):
        store.write_text(specstore.change_dir(root, t["id"]) / "tasks.md", text)
        store.log_event(root, "tasks.written", ticket=t["id"], source="plan:whole-spec")
    store.log_event(root, "plan.skipped", ticket=t["id"], subticket=sid, reason=WHOLE_SPEC_REASON)
    out({"ok": True, "id": t["id"], "planner": "skipped", "reason": WHOLE_SPEC_REASON, "subtickets": made})


def ticket_ready_implementers(a, root, cfg):
    every = store.subtickets_of(root, a.id)
    subs, superseded = subtickets.split_plan(every)  # a later plan's superseded sub-tickets count nowhere

    def status_of(tid: str):
        p = store.ticket_path(root, tid)
        return store.read_yaml(p)["status"] if p.exists() else None

    ready = subtickets.ready_implementers(subs, status_of)
    for s in subs:  # a dependency that just became met releases its dependant (siblings at merge; other parents here)
        if s["id"] in ready and s["status"] == "waiting-dependencies":
            s["status"] = "ready-for-implementer"
            s["history"].append({"ts": store.now(), "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
            store.save_ticket(root, s)
            store.log_event(root, "ticket.transition", ticket=s["id"], **{"from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
    out({"ok": True, "parent": a.id, "ready": ready, "subtickets": [s["id"] for s in every],
         "remaining": [s["id"] for s in subs if s["status"] not in ("merged", "parked", "closed")],
         "in_flight": [s["id"] for s in subs if s["in_flight"] or s["status"] in subtickets.IN_FLIGHT_STATES],
         "parked": [s["id"] for s in subs if s["status"] == "parked"],
         # stopped mid-check (a dispatcher that died or was stopped): no run in flight, so buildOne
         # resumes it from its stored state; the checkers re-run on its current head
         "resumable": [s["id"] for s in subs if s["status"] in subtickets.IN_FLIGHT_STATES and not s["in_flight"]],
         "closed": [s["id"] for s in subs if s["status"] == "closed"],
         "superseded": [s["id"] for s in superseded]})


def ticket_head(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if not t.get("branch"):
        raise Refused(f"{t['id']} has no branch yet")
    repo = gitops.repo_root(cfg)
    head = gitops.rev(repo, t["branch"])
    changed = head != t.get("head")
    t["head"] = head
    if t.get("merge_refused"):
        if gitops.head_contains(repo, head, gitops.integration_branch(cfg, repo)):
            t["merge_refused"] = None
            t["conflict_runs"] = 0
        else:
            # A conflict run that did not merge the integration branch in. Counted once per
            # implementer run (this command may be called more than once), so the loop is bounded.
            last = compose._runs_for(root, t["id"], "implementer", "")
            if last and last[-1] != t.get("conflict_counted_run"):
                t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
                t["conflict_counted_run"] = last[-1]
    store.save_ticket(root, t)
    out({"ok": True, "id": t["id"], "head": head, "branch": t["branch"], "changed": changed,
         "merge_refused": t.get("merge_refused"), "conflict_runs": int(t.get("conflict_runs") or 0)})


def results_record(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if a.role not in ("reviewer", "verifier"):
        raise Refused("results record: --role reviewer|verifier")
    if not re.fullmatch(r"[0-9a-f]{40}", a.head or ""):
        raise Refused(f"results record: --head must be a full commit SHA, got {a.head!r}")
    # A killed run's output is never read: the build loop passes --output even when the run wrote none.
    text = Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""
    if a.killed:
        st = "KILLED"
    else:
        parsed = status.parse(text)
        st = parsed["status"] or "UNKNOWN"
    if not a.killed:  # every Commit: line must name the head; with none, the verdict is for no known commit
        lines = re.findall(r"^Commit:.*$", text, re.M)
        if not lines:
            raise Refused("results record: the output has no Commit: line")
        for line in lines:
            cm = re.match(r"Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", line)
            if not cm:
                raise Refused(f"results record: Commit: {line[len('Commit:'):].strip()} is not a commit id")
            if not a.head.startswith(cm.group(1).lower()):
                raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
    stale = t.get("head") is not None and a.head != t.get("head")
    rows = [store.record_result(root, t["id"], a.head, a.role, st, a.run)]
    if a.role == "verifier" and not a.killed:
        # Heading and emphasis marks may wrap the line (`## Gate suite: PASS`, `**Gate suite:** PASS`);
        # other text before `Gate suite:` is prose, not a verdict.
        m = re.search(r"^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$", text, re.M)
        ci = (m.group(1), m.group(2).strip(" \t\r*") or None) if m else ("FAIL", "missing Gate suite line")
        mp = root / "runs" / str(a.run) / "meta.yaml"
        skipped = (store.read_yaml(mp) or {}).get("gate_skipped") if a.run and mp.exists() else None
        rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1],
                                        {"skipped": skipped} if skipped else None))
    ev = "result.stale-discarded" if stale else "result.recorded"
    for r in rows:
        store.log_event(root, ev, ticket=t["id"], head=a.head, role=r["role"], status=r["status"], run=a.run)
    out({"ok": True, "id": t["id"], "head": a.head, "stale": stale, "rows": [{k: r[k] for k in ("role", "status")} for r in rows]})


def results_show(a, root, cfg):
    t = store.load_ticket(root, a.id)
    head = t.get("head")
    rows = store.results_for(root, head) if head else {}
    missing = [r for r in store.RESULT_ROLES if r not in rows]
    out({"ok": True, "id": t["id"], "head": head, "rows": {k: v["status"] for k, v in rows.items()}, "missing": missing})


DECLARED_RE = re.compile(r"^\s*(?:[-*]\s+)?Protected paths:\s*(none|`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\.?\s*$")


def _in_repo(globs: list[str]) -> list[str]:
    """The patterns a repository diff can match: one starting `~` or `/` names a path outside it."""
    return [g for g in globs if not g.startswith(("~", "/"))]


def declared_paths(spec_text: str) -> list[str]:
    """The entries of each `Protected paths:` line (DECLARED_RE) in the spec's `## Risk` section, in
    order. The section runs from a line that is exactly `## Risk` to the next line starting `## ` or
    `=== `; a line inside a fenced code block neither starts nor ends it and declares nothing."""
    entries, in_risk = [], False
    for line, in_fence in specstore.lines_outside_fences(spec_text):
        if in_fence:
            continue
        if line.startswith(("## ", "=== ")):
            in_risk = line.rstrip() == "## Risk"
        elif in_risk and (m := DECLARED_RE.match(line)) and m.group(1) != "none":
            entries += re.findall(r"`([^`]+)`", m.group(1))
    return _in_repo(entries)


def undeclared_protected(root: Path, cfg: dict, t: dict, head: str) -> tuple[list[str], str]:
    """(the changed protected paths of `t` at `head` that the pinned spec does not declare, sorted;
    where the declarations were read, for the refusal). Changed is `integration...head`. The pinned
    spec is the parent's approved version, or the ticket's own when it has no parent; a path in the
    ticket's `accepted_paths` counts as declared (`resolve --accept-paths`)."""
    sid = t.get("parent") or t["id"]
    av = (store.load_ticket(root, sid) if sid != t["id"] else t)["spec"]["approved_version"]
    where = f"in {sid} spec v{av}" if av is not None else f"({sid} has no approved spec)"
    patterns = [g for globs in (cfg.get("protected_paths") or {}).values()
                for g in ([globs] if isinstance(globs, str) else list(globs or []))]
    repo = gitops.repo_root(cfg)
    integ = gitops.integration_branch(cfg, repo)
    changed = gitops.changed_files(repo, integ, head, _in_repo(patterns))
    if not changed:
        return [], where
    spec = root / "specs" / sid / f"v{av}.md"
    declared = declared_paths(spec.read_text(encoding="utf-8")) if av is not None and spec.exists() else []
    ok = set(gitops.changed_files(repo, integ, head, declared)) | set(t.get("accepted_paths") or [])
    return sorted(p for p in changed if p not in ok), where


def _branch_tip(repo: Path, t: dict) -> str:
    """The ticket's head, refused unless it is the tip of its branch."""
    head = t.get("head")
    if not head or gitops.rev(repo, t["branch"]) != head:
        raise Refused(f"{t['id']} head {head} is not the branch tip; run ticket head")
    return head


def merge_cmd(a, root, cfg):
    """Rule-4 checks (part G) in the local stand-in: ci PASS + APPROVE + VERIFIED on the current
    head, every changed protected path declared by the pinned spec (piece 8), head contains the
    integration branch; then a local --no-ff merge. Exit 2 names the first failing condition;
    'BLOCKED from merge gate' parks for a human; 'head does not contain main' is the conflict-run
    signal."""
    t = store.load_ticket(root, a.id)
    if t["status"] not in ("ready-for-merge", "checks-in-flight"):
        raise Refused(f"{t['id']} is {t['status']}, not ready-for-merge")
    repo = gitops.repo_root(cfg)
    integ = gitops.integration_branch(cfg, repo)
    head = _branch_tip(repo, t)
    rows = store.results_for(root, head)
    for role, want in (("ci", "PASS"), ("reviewer", "APPROVE"), ("verifier", "VERIFIED")):
        got = (rows.get(role) or {}).get("status")
        if got != want:
            raise Refused(f"{role} is {got or 'missing'} for {head[:9]}, need {want}")
    undeclared, where = undeclared_protected(root, cfg, t, head)
    if undeclared:
        store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="protected paths not declared",
                        paths=undeclared)
        raise Refused(f"BLOCKED from merge gate: protected paths not declared {where}: {', '.join(undeclared)}")
    with gitops.MergeLock(repo):
        if not gitops.head_contains(repo, head, integ):
            t["merge_refused"] = "head does not contain main"
            t["conflict_runs"] = 0  # unfixed conflict runs since this refusal
            store.save_ticket(root, t)
            store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="head does not contain main")
            raise Refused(f"head does not contain main ({integ} moved; merge it into {t['branch']} and re-check)")
        before, after = gitops.merge_no_ff(repo, head, integ, f"Merge {t['branch']}: {t['title']} ({t['id']})")
    t.update({"status": "merged", "merge": {"base_before": before, "main_after": after}, "merge_refused": None})
    t["history"].append({"ts": store.now(), "from": "ready-for-merge", "to": "merged", "by": "merge", "head": head})
    store.save_ticket(root, t)
    store.log_event(root, "merge.done", ticket=t["id"], head=head, base_before=before, main_after=after)
    released = []
    if t.get("parent"):
        parent = store.load_ticket(root, t["parent"])
        if parent.get("parent_base") is None:
            parent["parent_base"] = before
            store.save_ticket(root, parent)
        for s in store.subtickets_of(root, t["parent"]):
            if s["status"] == "waiting-dependencies" and all(
                    store.load_ticket(root, dep)["status"] in subtickets.SATISFIED for dep in s["depends_on"]):
                s["status"] = "ready-for-implementer"
                s["history"].append({"ts": store.now(), "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "merge"})
                store.save_ticket(root, s)
                store.log_event(root, "ticket.transition", ticket=s["id"], **{"from": "waiting-dependencies", "to": "ready-for-implementer", "by": "merge"})
                released.append(s["id"])
    gitops.remove_worktree(repo, root / "worktrees" / t["id"])
    out({"ok": True, "id": t["id"], "state": "merged", "base_before": before, "main_after": after, "released": released})


REVIEWER_STATUSES = ("APPROVE", "REQUEST-CHANGES", "ESCALATE", "KILLED")
VERIFIER_STATUSES = ("VERIFIED", "FAILED", "SPEC-DEFECT", "KILLED")
MAX_CONFLICT_RUNS = 2


def ticket_join(a, root, cfg):
    """The PR-loop join as a decision, read from the results table for the current head. The
    dispatcher and the tests both ask here, so the routing lives in one place:
    merge | revise (round +1) | conflict (same round) | wait | park, each with its reason."""
    t = store.load_ticket(root, a.id)
    head = t.get("head")
    rows = store.results_for(root, head) if head else {}
    st = {r: (rows.get(r) or {}).get("status") for r in store.RESULT_ROLES}
    rnd, mx = t["round"]["pr"], cfg["max_rounds"]["pr"]

    def decide(decision: str, reason: str, **extra):
        out({"ok": True, "id": t["id"], "head": head, "rows": st, "round": rnd, "decision": decision, "reason": reason, **extra})

    if t.get("merge_refused"):
        if int(t.get("conflict_runs") or 0) >= MAX_CONFLICT_RUNS:
            return decide("park", f"conflict: head still does not contain main after {MAX_CONFLICT_RUNS} conflict runs")
        return decide("conflict", "head does not contain main: the implementer merges the integration branch into its branch, same round")
    missing = [r for r in ("reviewer", "verifier", "ci") if st[r] is None]
    if st["verifier"] == "KILLED" and st["ci"] is None:
        missing.remove("ci")  # a killed verifier writes no ci row
    if missing:
        return decide("wait", f"results missing for the current head: {', '.join(missing)}", missing=missing)
    for role, known in (("reviewer", REVIEWER_STATUSES), ("verifier", VERIFIER_STATUSES)):
        if st[role] not in known:
            return decide("park", f"harness-bug: unknown STATUS {st[role]} from {role}")
    killed = [r for r in ("reviewer", "verifier") if st[r] == "KILLED"]
    if killed:
        return decide("park", f"budget kill: {', '.join(killed)}")
    if st["reviewer"] == "ESCALATE":
        return decide("park", "ESCALATE from reviewer")
    if st["verifier"] == "SPEC-DEFECT":
        return decide("park", "SPEC-DEFECT from verifier")
    if st == {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}:
        return decide("merge", "ci PASS + APPROVE + VERIFIED on the current head")
    red = ", ".join(f"{r} {v}" for r, v in st.items() if v not in ("APPROVE", "VERIFIED", "PASS"))
    if rnd < mx:
        return decide("revise", f"{red}; implementer round {rnd + 1}", round_op="pr:+1")
    return decide("park", f"max-round cutoff ({red} at round {rnd})")


def ticket_parent_check(a, root, cfg):
    """When every sub-ticket of the current plan is merged, the parent moves to ready-for-parent-verify
    (part G); sub-tickets a later plan superseded do not count."""
    parent = store.load_ticket(root, a.id)
    every = store.subtickets_of(root, parent["id"])
    if not every:
        raise Refused(f"{parent['id']} has no sub-tickets")
    subs, superseded = subtickets.split_plan(every)
    if all(s["status"] == "merged" for s in subs) and parent["status"] == "planned":
        frm = parent["status"]
        parent["status"] = "ready-for-parent-verify"
        parent["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
        store.save_ticket(root, parent)
        store.log_event(root, "ticket.transition", ticket=parent["id"], **{"from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
    reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
    out({"ok": True, "id": parent["id"], "state": parent["status"],
         "subtickets": {s["id"]: s["status"] for s in subs}, "superseded": [s["id"] for s in superseded],
         "reuse": reuse})


# ----- human surface (K-lite) -----------------------------------------------------

def _by() -> str:
    return getpass.getuser()


def _approval_dir(root: Path, tid: str) -> Path:
    d = root / "approvals" / tid
    d.mkdir(parents=True, exist_ok=True)
    return d


def _next_n(d: Path, kind: str) -> int:
    return len(list(d.glob(f"{kind}-*"))) + 1


def approve_spec(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if a.edit:
        text = Path(a.edit).read_text(encoding="utf-8")
    else:
        n = a.version or t["spec"]["version"]
        if not (root / "specs" / t["id"] / f"v{n}.md").exists():
            raise Refused(f"{t['id']} has no spec v{n}")
        text = (root / "specs" / t["id"] / f"v{n}.md").read_text(encoding="utf-8")
    pinned: list[str] = []
    if specstore.is_active(root):
        # Part K: refuse a malformed version or a delta that does not apply; nothing is written.
        _, deltas, errors = specstore.validate(text)
        errors += specstore.applies(root, deltas) if not errors else []
        if errors:
            raise Refused("spec not pinned: " + "; ".join(errors))
    if t["status"] != "awaiting-spec-gate":
        raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
    if a.edit:
        n = _add_spec_version(root, t, text, f"gate edit {a.edit}", cfg)
    if specstore.is_active(root):
        pinned = specstore.pin(root, t["id"], text)
    t["spec"]["approved_version"] = n
    store.write_text(root / "specs" / f"{t['id']}.md", text)
    store.write_yaml(_approval_dir(root, t["id"]) / f"spec-v{n}.yaml", {"by": _by(), "at": store.now(), "version": n})
    frm = t["status"]
    t["status"] = "ready-for-planner"
    t["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-planner", "by": _by(), "approved_version": n})
    store.save_ticket(root, t)
    store.log_event(root, "approval.recorded", ticket=t["id"], kind="spec", version=n, by=_by())
    if pinned:
        store.log_event(root, "change.pinned", ticket=t["id"], version=n, files=pinned)
    store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": "ready-for-planner", "by": _by()})
    out({"ok": True, "id": t["id"], "approved_version": n, "state": "ready-for-planner", "spec": f"specs/{t['id']}.md",
         "change": pinned})


def request_changes(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if t["status"] != "awaiting-spec-gate":
        raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
    d = _approval_dir(root, t["id"])
    dest = d / f"changes-{_next_n(d, 'changes')}.md"
    shutil.copyfile(a.notes, dest)
    frm = t["status"]
    t["status"] = "ready-for-spec-writer"
    t["round"]["spec"] = 0
    t["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-spec-writer", "by": _by(), "notes": _rel(root, dest)})
    store.save_ticket(root, t)
    store.log_event(root, "human.resolved", ticket=t["id"], kind="request-changes", by=_by(), notes=_rel(root, dest))
    out({"ok": True, "id": t["id"], "state": "ready-for-spec-writer", "notes": _rel(root, dest)})


def resolve(a, root, cfg):
    if a.decision is not None:  # refuse before anything is written, so a decision is never dropped
        # the branch below that will run: --answer wins, and --close runs only with no other mode
        if not (a.answer or (a.close and not (a.ruling or a.accept_paths or a.to or a.redispatch or a.replan))):
            raise Refused("--decision applies only with --answer or --close")
        specstore.decision_text(a.decision)
    t = store.load_ticket(root, a.id)
    st, parked = t["status"], t["parked"] or {}
    reason = parked.get("reason", "")
    d = _approval_dir(root, t["id"])

    def decided(via: str) -> dict:
        """Log `--decision`, once this mode's own refusals have passed; the `extra` for move()."""
        if a.decision is None:
            return {}
        line = specstore.record_decision(root, t["id"], a.decision)
        store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via=via)
        return {"decision": line}

    def move(to: str, kind: str, extra: dict) -> None:
        t["status"] = to
        if to != "parked":
            t["parked"] = None
        t["history"].append({"ts": store.now(), "from": st, "to": to, "by": _by(), "resolve": kind, **extra})
        store.save_ticket(root, t)
        store.write_yaml(d / f"resolve-{_next_n(d, 'resolve')}.yaml", {"by": _by(), "at": store.now(), "kind": kind, "from": st, "to": to, **extra})
        store.log_event(root, "human.resolved", ticket=t["id"], kind=kind, by=_by(), **{"from": st, "to": to})
        out({"ok": True, "id": t["id"], "state": to, "kind": kind, **extra})

    if a.answer:
        if st == "waiting-requester":
            to = "ready-for-triage"
        elif st == "parked" and reason.startswith("NEEDS-HUMAN"):
            to = "ready-for-spec-writer" if "spec writer" in reason else "ready-for-triage"
        else:
            raise Refused(f"--answer applies to waiting-requester or a NEEDS-HUMAN park; {t['id']} is {st} ({reason or 'no park'})")
        req = root / t["request"]
        n = req.read_text(encoding="utf-8").count("\n## Answer ") + 1
        with req.open("a", encoding="utf-8") as fh:
            fh.write(f"\n\n## Answer {n}\n\n{Path(a.answer).read_text(encoding='utf-8').rstrip()}\n")
        move(to, "answer", {"answer": n, **decided("resolve --answer")})
    elif a.ruling:
        if st != "parked" or not reason.startswith(("ESCALATE", "BLOCKED")):
            if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
                raise Refused("use --answer")
            raise Refused(f"--ruling applies to an ESCALATE or BLOCKED park; {t['id']} is {st} ({reason or 'no park'})")
        if reason.startswith("ESCALATE from reviewer"):
            # Back to its checks, same round: the reviewer runs again with the ruling in its input.
            head, moved = t.get("head"), _set_aside_failed_rows(root, t)
            store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
            dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
            shutil.copyfile(a.ruling, dest)
            move("checks-in-flight", "ruling", {"ruling": _rel(root, dest), "head": head, "superseded": moved})
            return
        if reason.startswith("BLOCKED"):  # an implementer's or the gate's BLOCKED: back to the implementer, same round
            to = "ready-for-implementer"
        else:
            to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
        shutil.copyfile(a.ruling, dest)
        move(to, "ruling", {"ruling": _rel(root, dest)})
    elif a.accept_paths:
        # The merge gate refused a protected path the pinned spec does not declare; the human accepts
        # it under the approved design for this sub-ticket. Its results stand, so the build merges it.
        if st != "parked" or not reason.startswith("BLOCKED from merge gate:"):
            raise Refused("--accept-paths applies to a merge gate park (BLOCKED from merge gate); "
                          f"{t['id']} is {st} ({reason or 'no park'})")
        head = _branch_tip(gitops.repo_root(cfg), t)
        paths, _ = undeclared_protected(root, cfg, t, head)
        if not paths:
            raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
        shutil.copyfile(a.accept_paths, dest)
        t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
        move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
    elif a.to:
        if a.to != "spec-gate":
            raise Refused("--to accepts only spec-gate")
        if st != "parked" or t["spec"]["version"] < 1:
            raise Refused(f"--to spec-gate needs a parked ticket with a spec version; {t['id']} is {st}")
        move("awaiting-spec-gate", "to-spec-gate", {})
    elif a.redispatch:
        # Re-run the checkers on the same head after the cause of the park is fixed outside the ticket
        # (a harness or gate defect, a killed checker). Round unchanged.
        if st != "parked" or parked.get("from") not in ("checks-in-flight", "ready-for-merge"):
            raise Refused(f"--redispatch applies to a sub-ticket parked from its checks; {t['id']} is {st} (from {parked.get('from')})")
        head, moved = t.get("head"), _set_aside_failed_rows(root, t)
        store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
        move("checks-in-flight", "redispatch", {"head": head, "superseded": moved})
    elif a.replan:
        # After a failed parent-close check: back to the planner with F as a ruling. Its new
        # sub-tickets take the next free ids under this parent; the merged ones stay merged.
        if st != "parked":
            raise Refused(f"--replan applies to a parked parent; {t['id']} is {st}")
        subs = store.subtickets_of(root, t["id"])
        if not subs:
            raise Refused(f"--replan applies to a parent with sub-tickets; {t['id']} has none")
        unmerged = [f"{s['id']} is {s['status']}" for s in subtickets.split_plan(subs)[0] if s["status"] != "merged"]
        if unmerged:
            raise Refused(f"--replan needs every sub-ticket merged: {', '.join(unmerged)}")
        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
        shutil.copyfile(a.replan, dest)
        move("ready-for-planner", "replan", {"ruling": _rel(root, dest)})
    elif a.close:
        if st == "closed":
            raise Refused(f"{t['id']} is already closed")
        move("closed", "close", decided("resolve --close"))
    else:
        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate | --redispatch | "
                      "--replan F | --close")


def _set_aside_failed_rows(root: Path, t: dict) -> list[str]:
    """Move the head's rows that did not pass under results/<head>/superseded-<n>/, so the join cannot
    read them as current and the build runs only the checkers with no row. The reviewer row stays
    when it is APPROVE; the verifier and ci rows, written by one verifier run, stay together when
    they are VERIFIED and PASS. Returns the roles moved."""
    head = t.get("head")
    moved: list[str] = []
    if head:
        rows = {k: v.get("status") for k, v in store.results_for(root, head).items()}
        stale = [] if rows.get("reviewer") == "APPROVE" else ["reviewer"]
        if not (rows.get("verifier") == "VERIFIED" and rows.get("ci") == "PASS"):
            stale += ["verifier", "ci"]
        rd = root / "results" / head
        todo = [store.result_path(root, head, r) for r in stale if r in rows]
        if todo:
            dest = rd / f"superseded-{len(list(rd.glob('superseded-*'))) + 1}"
            dest.mkdir(parents=True, exist_ok=True)
            for f in todo:
                f.rename(dest / f.name)
                moved.append(f.stem)
    return moved


def decision_add(a, root, cfg):
    t = store.load_ticket(root, a.id)  # any state, closed included
    line = specstore.record_decision(root, t["id"], a.text)
    store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via="decision add")
    out({"ok": True, "id": t["id"], "decision": line})


# ----- spec store (doc §Harness, Spec store; part K) ----------------------------------

def _git_toplevel(cwd: Path) -> Path:
    cp = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if cp.returncode != 0 or not cp.stdout.strip():
        raise Refused(f"factory init: {cwd} is not inside a git work tree")
    return Path(cp.stdout.strip()).resolve()


def _new_instance_yaml(repo_name: str) -> str:
    """factory/instance.template.yaml with the per-instance values filled (design B.5)."""
    text = instance.INSTANCE_TEMPLATE.read_text(encoding="utf-8")
    for key, val in (("__REPO_NAME__", repo_name), ("__HARNESS__", str(instance.HARNESS))):
        if key not in text:
            raise Refused(f"{instance.INSTANCE_TEMPLATE} has no {key}")
        text = text.replace(key, json.dumps(val, ensure_ascii=False))
    return text


def _revision() -> str:
    rev = instance.harness_revision()
    if rev is None:
        raise Refused(f"factory init: cannot read the harness revision of {instance.HARNESS} (not a git checkout?)")
    return rev


def _refuse_inside_store(cwd: Path, top: Path) -> None:
    """Refuse `init` from inside the store checkout, where it would build a second instance inside
    the live store (design A.1). Called only with FACTORY_INSTANCE unset."""
    if gitops.git(top, "symbolic-ref", "-q", "HEAD", check=False) == f"refs/heads/{gitops.STORE_BRANCH}":  # unborn too
        raise Refused(f"factory init: {cwd} is inside the store checkout {top} (branch {gitops.STORE_BRANCH}); "
                      "run init from the repository root")
    # Whatever the store has checked out (a detached HEAD, another branch): the instance found by
    # walking up names its store, and a checkout of the same repository at or under it is that store.
    found = instance.find()
    if found is None:
        return
    try:
        cfg = instance.load_config(found)
    except (OSError, yaml.YAMLError):  # an unreadable config names no store: nothing to compare
        return
    if not isinstance(cfg, dict) or not isinstance(cfg.get("state_dir"), str):
        return
    own = instance.own_state_root(found, cfg)
    if top == own or (top.is_relative_to(own)
                      and gitops.common_dir(top) == gitops.common_dir(instance.repo_root(found))):
        raise Refused(f"factory init: {cwd} is inside the store {own} of the instance {found}; "
                      "run init from the repository root")


def _head_branch(repo: Path) -> str:
    """The branch checked out at `repo`, or HEAD when it is detached."""
    return gitops.git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False) or "HEAD"


def _add_store_checkout(repo: Path, root: Path, branch: str, cfg_path: Path) -> None:
    """Make the missing own store `root` a checkout of the store branch (design A.3): refused at a
    path `branch` has ever tracked; the branch comes from a local branch, else the one remote that
    carries it, else a new orphan, which needs no commit and so no git identity."""
    store_branch = gitops.STORE_BRANCH
    rel = root.relative_to(repo).as_posix() if root.is_relative_to(repo) else None
    if rel is not None:
        sha = gitops.last_tracked(repo, branch, rel)
        if sha:
            raise Refused(f"factory init: {branch} has tracked files under {rel} (last in commit {sha}); a checkout "
                          f"of any older commit would overwrite a store kept there; set another state_dir in {cfg_path}")
    local = bool(gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{store_branch}", check=False))
    remotes = [] if local else gitops.remote_branches(repo, store_branch)
    if len(remotes) > 1:
        raise Refused(f"factory init: no local branch {store_branch}, and more than one remote carries it "
                      f"({', '.join(remotes)}); run git branch {store_branch} <remote>/{store_branch} for the one "
                      "to use, then init again")
    if local:
        args = ["worktree", "add", "-q", str(root), store_branch]
    elif remotes:
        args = ["worktree", "add", "-q", "--track", "-b", store_branch, str(root), remotes[0]]
    else:
        args = ["worktree", "add", "-q", "--orphan", "-b", store_branch, str(root)]
    try:
        gitops.git(repo, *args)
    except Refused as e:
        raise Refused(f"factory init: cannot check out the store at {root}: {e}") from None
    if rel is not None:
        _exclude_store(repo, rel)


def _exclude_store(repo: Path, rel: str) -> None:
    """The integration checkout ignores the store at `rel` through the repo's exclude file."""
    exclude = Path(gitops.git(repo, "rev-parse", "--git-path", "info/exclude"))
    exclude = exclude if exclude.is_absolute() else repo / exclude
    have = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    line = f"/{rel}/"
    if line not in have.splitlines():
        store.write_text(exclude, have + ("" if not have or have.endswith("\n") else "\n") + line + "\n")


def _store_hint(repo: Path, root: Path) -> None:
    """An existing own store that is not the store branch's checkout is left alone (design A.5)."""
    top = gitops.git(root, "rev-parse", "--show-toplevel", check=False)
    if top and Path(top).resolve() == root.resolve() and gitops.common_dir(root) == gitops.common_dir(repo):
        if _head_branch(root) == "HEAD":
            print(f"the store worktree {root} is on a detached HEAD; check out {gitops.STORE_BRANCH} there",
                  file=sys.stderr)
        return
    print(f"the store {root} is not on its branch {gitops.STORE_BRANCH}; factory store migrate --to PATH moves it",
          file=sys.stderr)


def init_cmd(a):
    """Create whatever of the instance is missing (design B.5); idempotent. The instance is
    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory, which may not
    be inside the store checkout (A.1). Its pieces (instance.yaml, context.md, harness.lock, agent
    files) are written only when the store in use is the instance's own: a run on a throwaway store
    (FACTORY_STATE elsewhere, as every test does) initialises that store and nothing else. So
    creating an instance while FACTORY_STATE names another store is refused before anything is
    written: it would leave an instance.yaml with no context.md. A missing own store becomes a git
    worktree of the store branch (A.3) before any instance file is written, so a refusal or a
    failed git step leaves nothing behind."""
    cwd = instance.caller_cwd()
    top = _git_toplevel(cwd)
    if instance.env_path("FACTORY_INSTANCE") is None:
        _refuse_inside_store(cwd, top)
    inst = instance.env_path("FACTORY_INSTANCE") or top / instance.DIRNAME
    created: list[str] = []
    cfg_path = inst / instance.CONFIG_NAME
    new_text = None
    if cfg_path.exists():
        cfg = instance.load_config(inst)
    else:
        if not a.repo_name:
            raise Refused(f"factory init: {cfg_path} does not exist; pass --repo-name NAME to create it")
        new_text = _new_instance_yaml(a.repo_name)
        cfg = yaml.safe_load(new_text)
    root = instance.state_root(inst, cfg)
    fence(inst, cfg, root)
    own = instance.is_own_store(inst, cfg, root)
    if new_text is not None:
        if not own:
            raise Refused(f"factory init: {inst} has no {instance.CONFIG_NAME}, and FACTORY_STATE names another "
                          f"store ({root}); create the instance with FACTORY_STATE unset, then init that store")
        _revision()  # refuse before writing anything if the lock cannot be written
    repo = instance.repo_root(inst)
    existed = root.exists()
    if own and not existed:
        if new_text is None and (os.environ.get("FACTORY_INTEGRATION_BRANCH") or cfg.get("integration_branch")):
            branch = gitops.integration_branch(cfg, repo)
        else:  # its own fallback, rev-parse --abbrev-ref HEAD, fails on an unborn branch, never tracked (A.3.1)
            branch = _head_branch(repo)
        _add_store_checkout(repo, root, branch, cfg_path)
    if new_text is not None:
        store.write_text(cfg_path, new_text)
        created.append(str(cfg_path))
    agents: list[str] = []
    store_branch = None
    if own:
        ctx = inst / "context.md"
        if not ctx.exists():
            store.write_text(ctx, instance.CONTEXT_TEMPLATE.read_text(encoding="utf-8"))
            created.append(str(ctx))
        lock = inst / "harness.lock"
        if not lock.exists():
            store.write_text(lock, _revision() + "\n")
            created.append(str(lock))
        dest = repo / ".claude" / "agents"
        for src in sorted(instance.AGENTS.glob("factory-*.md")):
            if not (dest / src.name).exists():
                (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest / src.name)
                agents.append(str(dest / src.name))
        checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
        if checkout is not None and checkout.resolve() == root:
            store_branch = gitops.STORE_BRANCH
        elif existed:
            _store_hint(repo, root)
    had_gitignore, had_gitattributes = (root / ".gitignore").exists(), (root / ".gitattributes").exists()
    store.ensure_gitignore(root)
    store.ensure_gitattributes(root)
    written = specstore.init(root)
    if not had_gitignore:
        written.insert(0, ".gitignore")
    if not had_gitattributes:
        written.insert(0, ".gitattributes")
    if written or created or agents:
        store.log_event(root, "store.initialised", files=written, instance=created, agents=agents)
    if agents:
        print("restart the session so the agents register", file=sys.stderr)
    out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
         "created": created, "agents": agents, "store_branch": store_branch})


STATE_DIR_LINE = re.compile(r"^(state_dir:[ \t]*)([^#\n]*?)([ \t]*(?:#.*)?)$", re.M)


def _ignored_files(where: Path) -> list[str]:
    """Every file git ignores under the directory `where`, relative to it. Git lists a nested
    repository (a role's clone in its scratch directory) as its directory: its files are listed
    here one by one. Empty directories are not files and are not listed."""
    # factory: empty directories are not carried (git lists no such entry); copy whole trees if a
    # role's scratch ever needs one
    files = []
    listed = gitops.git(where, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", ".")
    for entry in filter(None, listed.split("\0")):
        if entry.endswith("/"):
            files += sorted(p.relative_to(where).as_posix() for p in (where / entry).rglob("*")
                            if p.is_symlink() or p.is_file())
        else:
            files.append(entry)
    return files


def _copy_mismatch(old: Path, new: Path, listed: list[str]) -> str | None:
    """The first way the copy at `new` differs from `old` (design B step 4), or None."""
    for f in listed:
        src, dst = old / f, new / f
        if src.is_symlink():
            same = dst.is_symlink() and os.readlink(dst) == os.readlink(src)
        else:
            same = dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes()
        if not same:
            return f"{f} differs"
    copied = _ignored_files(new)
    if len(copied) != len(listed):
        return f"{len(copied)} ignored files at the new path, {len(listed)} listed"
    status = gitops.git(new, "status", "--porcelain")
    return f"git status there is not clean ({status.splitlines()[0].strip()})" if status else None


def store_migrate(a, root, cfg):
    """Move the instance's own store, a plain directory tracked on the integration branch, onto the
    store branch checked out at --to PATH (design B). Every refusal comes before the first write. A
    copy that does not match is undone and exits 1, before anything is deleted. Makes no commit on
    the integration branch and pushes nothing: the operator reviews and commits both sides."""
    def refuse(msg: str):
        raise Refused(f"factory store migrate: {msg}")

    inst = instance.require()
    repo = instance.repo_root(inst)
    sb = gitops.STORE_BRANCH
    if not instance.is_own_store(inst, cfg, root):
        refuse(f"the store in use, {root}, is not the instance's own (FACTORY_STATE names another); unset FACTORY_STATE")
    old, rel_old = root.resolve(), cfg["state_dir"]
    checkout = gitops.checkout_of(repo, sb)
    if checkout is not None and checkout.resolve() == old:
        refuse(f"the store {old} is already the checkout of {sb}")
    if checkout is not None or gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{sb}", check=False):
        refuse(f"a local branch {sb} already exists; this command starts it from the store")
    branch, head = gitops.integration_branch(cfg, repo), _head_branch(repo)
    if head == "HEAD" or head != branch:
        refuse(f"the integration branch {'' if head == 'HEAD' else branch + ' '}is not checked out at {repo} "
               f"({'its HEAD is detached' if head == 'HEAD' else head + ' is'}); check it out first")
    runs = _in_flight(root)
    if runs:
        refuse(f"runs in flight on the store: {', '.join(runs)}; wait until they finish")
    under = [ln.split(" ", 1)[1] for ln in gitops.git(repo, "worktree", "list", "--porcelain").splitlines()
             if ln.startswith("worktree ") and Path(ln.split(" ", 1)[1]).resolve().is_relative_to(old)]
    if under:
        refuse(f"git worktrees under the store: {', '.join(under)}; remove them first")
    status = gitops.git(repo, "status", "--porcelain", "--untracked-files=all", "--", rel_old)
    if status:
        names = [ln.strip().split(None, 1)[1] for ln in status.splitlines()]
        refuse(f"uncommitted store files: {', '.join(names)}; commit them on {branch} first")
    new = (repo / a.to).resolve()
    if new.exists():
        refuse(f"{a.to} exists; choose a path that does not")
    if new.is_relative_to(old):
        refuse(f"{a.to} is inside the store {old}, which this command deletes once it has moved")
    rel_new = new.relative_to(repo).as_posix() if new.is_relative_to(repo) else None
    if rel_new is not None:
        sha = gitops.last_tracked(repo, branch, rel_new)  # init's never-tracked test (design A.3.1)
        if sha:
            refuse(f"{branch} has tracked files under {rel_new} (last in commit {sha}); a checkout of any older "
                   "commit would overwrite a store kept there; choose another path")
    cfg_path = inst / instance.CONFIG_NAME
    text = cfg_path.read_text(encoding="utf-8")
    m = STATE_DIR_LINE.search(text)
    if m is None:
        refuse(f"{cfg_path} has no state_dir: line to rewrite")
    tree = gitops.git(repo, "rev-parse", "-q", "--verify", f"{branch}:{rel_old}", check=False)
    if not tree or gitops.git(repo, "cat-file", "-t", tree) != "tree":
        refuse(f"the store {rel_old} is not tracked on {branch}")
    carried = gitops.rev(repo, branch)

    # 1-2. The branch, one root commit of the store as last committed, checked out at PATH.
    created = new  # the outermost directory this command creates, removed on undo
    while not created.parent.exists():
        created = created.parent
    msg = f"store: carried over from {branch} at {carried}; earlier history: git log {carried} -- {rel_old}"
    gitops.git(repo, "branch", sb, gitops.git(repo, "commit-tree", tree, "-m", msg))
    try:
        gitops.git(repo, "worktree", "add", "-q", str(new), sb)
        # 3. The files git ignores, which the branch does not carry: run scratch directories, tripwire baselines.
        listed = _ignored_files(old)
        for f in listed:
            (new / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old / f, new / f, follow_symlinks=False)
        # 4. Verify before deleting anything.
        bad = _copy_mismatch(old, new, listed)
        if bad:
            raise RuntimeError(f"factory store migrate: the copy at {a.to} does not match: {bad}; "
                               f"removed the new worktree and branch {sb}, the store at {rel_old} is unchanged")
    except BaseException:
        gitops.git(repo, "worktree", "remove", "--force", str(new), check=False)
        gitops.git(repo, "worktree", "prune", check=False)
        gitops.git(repo, "branch", "-D", sb, check=False)
        shutil.rmtree(created, ignore_errors=True)
        raise
    # 5. The integration checkout: untrack the old path, ignore the new one, point state_dir at it.
    gitops.git(repo, "rm", "-r", "-q", "--cached", rel_old)
    if rel_new is not None:
        _exclude_store(repo, rel_new)
    store.write_text(cfg_path, text[:m.start(2)] + a.to + text[m.end(2):])
    shutil.rmtree(old)
    # 6.
    fields = {"from": rel_old, "to": a.to, "branch": sb, "carried_from": carried, "copied": len(listed)}
    store.log_event(new, "store.migrated", **fields)
    out({"ok": True, **fields})
    print(f"next: review git status and commit on {branch} (the old store untracked, state_dir now {a.to}); "
          f"then commit the store (git -C {a.to} add -A && git -C {a.to} commit) and push it "
          f"(git push origin {sb})", file=sys.stderr)


def paths_cmd(a):
    """Absolute paths a dispatcher needs (design B.6). Runs no lock check and writes nothing."""
    inst = instance.find()
    state = None
    if inst is not None:
        state = str(instance.state_root(inst, instance.load_config(inst)))
    h = instance.HARNESS
    out({"ok": True, "harness": str(h), "bin": str(h / "bin" / "factory"),
         "intake_workflow": str(h / "factory" / "workflows" / "intake.js"),
         "build_workflow": str(h / "factory" / "workflows" / "build.js"),
         "harness_revision": instance.harness_revision(),
         "instance": str(inst) if inst is not None else None, "state": state})


def spec_tasks(a, root, cfg):
    t = store.load_ticket(root, a.id)
    d = _run_dir(root, a.run)
    meta = store.read_yaml(d / "meta.yaml")
    if meta.get("ticket") != t["id"] or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
        raise Refused(f"{a.run} is not a PLANNED planner run of {t['id']}")
    if not specstore.is_active(root):
        out({"ok": True, "id": t["id"], "skipped": "no spec store (factory init not run)"})
        return
    if not specstore.change_dir(root, t["id"]).exists():
        raise Refused(f"{t['id']} has no change folder (no pinned version)")
    text = status.strip_trailer((d / "output.md").read_text(encoding="utf-8"))
    dest = specstore.change_dir(root, t["id"]) / "tasks.md"
    store.write_text(dest, text)
    store.log_event(root, "tasks.written", ticket=t["id"], run=a.run)
    out({"ok": True, "id": t["id"], "path": _rel(root, dest)})


def _verifier_rows(root: Path, tid: str) -> list[str]:
    """`<head> · <ticket> · <STATUS> · <run_id>` per verifier row in results/ for the parent and
    its sub-tickets, oldest first. results/ is a later build item; absent → no rows."""
    res = root / "results"
    rows = []
    if res.exists():
        for p in sorted(res.rglob("*.yaml")):
            r = store.read_yaml(p) or {}
            if str(r.get("ticket", "")).split(".")[0] == tid and r.get("role") == "verifier":
                rows.append(f"{r.get('head')} · {r.get('ticket')} · {r.get('status')} · {r.get('run_id')}")
    return rows


def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
    """The run id of a sub-ticket's VERIFIED verifier run that stands for the parent-close run
    (design doc routing table, Merge gate row), or None when the parent needs its own run."""
    # factory: one sub-ticket only, and scenario coverage is read from scenario names occurring in
    # the sub-ticket's text; widen only when the store can check a coverage map per sub-ticket.
    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
    if len(subs) != 1 or not t.get("parent_base"):
        return None
    s = subs[0]
    after = (s.get("merge") or {}).get("main_after")
    if s["status"] != "merged" or not after or not s.get("head"):
        return None
    repo = gitops.repo_root(cfg)
    if gitops.rev(repo, gitops.integration_branch(cfg, repo)) != after:
        return None
    row = store.results_for(root, s["head"]).get("verifier") or {}
    rid = row.get("run_id")
    mp = root / "runs" / str(rid) / "meta.yaml"
    if row.get("status") != "VERIFIED" or not rid or not mp.exists():
        return None
    m = store.read_yaml(mp) or {}
    if m.get("status") != "VERIFIED" or m.get("head") != s["head"] or m.get("base") != t["parent_base"]:
        return None
    spec = root / "specs" / t["id"] / f"v{t['spec'].get('approved_version')}.md"
    sub = root / "specs" / s["id"] / "subticket.md"
    if not spec.exists() or not sub.exists():
        return None
    names = specstore.scenario_names(spec.read_text(encoding="utf-8"))
    text = sub.read_text(encoding="utf-8")
    return rid if names and all(n in text for n in names) else None


def _parent_close_verified(root: Path, cfg: dict, t: dict) -> str | None:
    """The run that verifies the parent: every current sub-ticket merged (a superseded one does not
    count), and a finished verifier run on the parent itself said VERIFIED on a head that contains
    every one of those merges (a run from before the last merge does not count); else a
    sub-ticket's run that stands for it; else None."""
    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
    if any(s["status"] != "merged" for s in subs):
        return None
    repo = gitops.repo_root(cfg)
    runs = root / "runs"
    for d in sorted(runs.iterdir()) if runs.exists() else []:
        mp = d / "meta.yaml"
        if not mp.exists():
            continue
        m = store.read_yaml(mp)
        if m.get("ticket") != t["id"] or m.get("role") != "verifier" or m.get("status") != "VERIFIED" or not m.get("head"):
            continue
        if all(gitops.head_contains(repo, m["head"], s["merge"]["main_after"]) for s in subs if s["merge"].get("main_after")):
            return d.name
    return _reused_subticket_run(root, cfg, t)


def archive_cmd(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if not specstore.is_active(root):
        raise Refused("no spec store (factory init not run)")
    if not specstore.change_dir(root, t["id"]).exists():
        raise Refused(f"{t['id']} has no change folder to archive")
    errors = specstore.applies(root, specstore.delta_ops_of_change(root, t["id"]))
    if errors:
        raise Refused("archive does not apply: " + "; ".join(errors))
    if store.subtickets_of(root, t["id"]) and not _parent_close_verified(root, cfg, t):
        raise Refused(f"{t['id']} has sub-tickets but no VERIFIED parent-close verifier run on the integration branch")
    res = specstore.archive(root, t["id"], _verifier_rows(root, t["id"]))
    store.log_event(root, "change.archived", ticket=t["id"], **res)
    out({"ok": True, "id": t["id"], **res})


# ----- misc ---------------------------------------------------------------------

def config_cmd(a, root, cfg):
    out({"ok": True, "models": cfg["models"], "max_rounds": cfg["max_rounds"], "state_dir": str(root)})


def status_parse(a, root, cfg):
    out(status.parse(Path(a.file).read_text(encoding="utf-8")))


def log_tail(a, root, cfg):
    files = sorted((root / "log").glob("*.jsonl")) if (root / "log").exists() else []
    lines: list[str] = []
    for p in files:
        lines.extend(p.read_text(encoding="utf-8").splitlines())
    if a.event:
        lines = [ln for ln in lines if json.loads(ln).get("event") == a.event]
    if a.ticket:
        lines = [ln for ln in lines if json.loads(ln).get("ticket") == a.ticket]
    for ln in lines[-a.n:]:
        print(ln)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="factory", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--accept-harness", metavar="SHA", default=None,
                    help="accept the running harness revision SHA for this instance (design C.3); "
                         "written before the subcommand")
    sp = ap.add_subparsers(dest="cmd", required=True)

    tk = sp.add_parser("ticket").add_subparsers(dest="sub", required=True)
    p = tk.add_parser("new")
    p.add_argument("--file", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=ticket_new)
    p = tk.add_parser("show")
    p.add_argument("id")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=ticket_show)
    p = tk.add_parser("set")
    p.add_argument("id")
    p.add_argument("assignments", nargs="+")
    p.set_defaults(fn=ticket_set)
    p = tk.add_parser("transition")
    p.add_argument("id")
    p.add_argument("--to", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--round")
    p.set_defaults(fn=ticket_transition)
    p = tk.add_parser("park")
    p.add_argument("id")
    p.add_argument("--reason", required=True)
    p.add_argument("--outputs")
    p.add_argument("--question")
    p.set_defaults(fn=ticket_park)
    p = tk.add_parser("ready-implementers")
    p.add_argument("id")
    p.set_defaults(fn=ticket_ready_implementers)
    p = tk.add_parser("head")
    p.add_argument("id")
    p.set_defaults(fn=ticket_head)
    p = tk.add_parser("join")
    p.add_argument("id")
    p.set_defaults(fn=ticket_join)
    p = tk.add_parser("parent-check")
    p.add_argument("id")
    p.set_defaults(fn=ticket_parent_check)

    rn = sp.add_parser("run").add_subparsers(dest="sub", required=True)
    p = rn.add_parser("start")
    p.add_argument("--role", required=True)
    p.add_argument("--ticket", required=True)
    p.add_argument("--model")
    p.set_defaults(fn=run_start)
    p = rn.add_parser("compose")
    p.add_argument("run")
    p.set_defaults(fn=run_compose)
    p = rn.add_parser("finish")
    p.add_argument("run")
    p.add_argument("--output-file")
    p.add_argument("--status-override")
    p.set_defaults(fn=run_finish)
    p = rn.add_parser("last-message")
    p.add_argument("run")
    p.add_argument("--text", required=True)
    p.set_defaults(fn=run_last_message)
    p = rn.add_parser("cleanup")
    p.add_argument("run")
    p.set_defaults(fn=run_cleanup)

    sc = sp.add_parser("spec").add_subparsers(dest="sub", required=True)
    p = sc.add_parser("add")
    p.add_argument("id")
    p.add_argument("--from-run")
    p.add_argument("--file")
    p.set_defaults(fn=spec_add)
    p = sc.add_parser("amend", help="a human amends PARENT's pinned spec when its intent is unchanged: F becomes "
                                    "the next and approved version, re-pinned with tasks.md kept")
    p.add_argument("id")
    p.add_argument("--file", required=True)
    p.add_argument("--reason", required=True, help="one line: why the spec is amended")
    p.add_argument("--intent", required=True, choices=("unchanged", "changed"))
    p.set_defaults(fn=spec_amend)
    pl = sp.add_parser("plan").add_subparsers(dest="sub", required=True)
    p = pl.add_parser("add")
    p.add_argument("id")
    p.add_argument("--from-run")
    p.add_argument("--file")
    p.set_defaults(fn=plan_add)
    p = pl.add_parser("whole-spec", help="when the approved spec needs one sub-ticket, create it from the whole "
                                         "spec and skip the planner; otherwise report why the planner is needed")
    p.add_argument("id")
    p.set_defaults(fn=plan_whole_spec)

    p = sc.add_parser("tasks")
    p.add_argument("id")
    p.add_argument("--run", required=True)
    p.set_defaults(fn=spec_tasks)
    sb = sp.add_parser("subticket").add_subparsers(dest="sub", required=True)
    p = sb.add_parser("add", help="create the parent's sub-tickets from a plan; with neither --run nor --file, "
                                  "from the planner run named by its latest plan.added event")
    p.add_argument("id")
    p.add_argument("--run")
    p.add_argument("--file")
    p.set_defaults(fn=subticket_add)
    rs = sp.add_parser("results").add_subparsers(dest="sub", required=True)
    p = rs.add_parser("record")
    p.add_argument("id")
    p.add_argument("--head", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--output")
    p.add_argument("--run")
    p.add_argument("--killed", action="store_true")
    p.set_defaults(fn=results_record)
    p = rs.add_parser("show")
    p.add_argument("id")
    p.set_defaults(fn=results_show)
    p = sp.add_parser("merge")
    p.add_argument("id")
    p.set_defaults(fn=merge_cmd)
    p = sp.add_parser("init")
    p.add_argument("--repo-name")
    p.set_defaults(fn=init_cmd)
    sm = sp.add_parser("store").add_subparsers(dest="sub", required=True)
    p = sm.add_parser("migrate", help="move a store tracked on the integration branch onto the factory-store "
                                      "branch, checked out at PATH (relative to the repo root)")
    p.add_argument("--to", required=True, metavar="PATH")
    p.set_defaults(fn=store_migrate)
    p = sp.add_parser("paths")
    p.set_defaults(fn=paths_cmd)
    p = sp.add_parser("archive")
    p.add_argument("id")
    p.set_defaults(fn=archive_cmd)

    p = sp.add_parser("approve-spec")
    p.add_argument("id")
    p.add_argument("--version", type=int)
    p.add_argument("--edit")
    p.set_defaults(fn=approve_spec)
    p = sp.add_parser("request-changes")
    p.add_argument("id")
    p.add_argument("--notes", required=True)
    p.set_defaults(fn=request_changes)
    p = sp.add_parser("resolve")
    p.add_argument("id")
    p.add_argument("--answer")
    p.add_argument("--ruling")
    p.add_argument("--accept-paths", metavar="F", help="a sub-ticket the merge gate refused for undeclared protected paths: accept them under the approved design and return it to its reviewer and verifier")
    p.add_argument("--to")
    p.add_argument("--redispatch", action="store_true")
    p.add_argument("--replan", metavar="F", help="a parked parent whose sub-tickets all merged: back to the planner with F as a ruling")
    p.add_argument("--close", action="store_true")
    p.add_argument("--decision", metavar="TEXT", help="with --answer or --close: also log TEXT to decisions.md")
    p.set_defaults(fn=resolve)
    dc = sp.add_parser("decision").add_subparsers(dest="sub", required=True)
    p = dc.add_parser("add", help="log one standing decision against a ticket in any state")
    p.add_argument("id")
    p.add_argument("text")
    p.set_defaults(fn=decision_add)

    p = sp.add_parser("config")
    p.set_defaults(fn=config_cmd)
    st = sp.add_parser("status").add_subparsers(dest="sub", required=True)
    p = st.add_parser("parse")
    p.add_argument("file")
    p.set_defaults(fn=status_parse)
    lg = sp.add_parser("log").add_subparsers(dest="sub", required=True)
    p = lg.add_parser("tail")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--event")
    p.add_argument("--ticket")
    p.set_defaults(fn=log_tail)
    return ap




# ----- live-store fence: only the dispatcher writes a live store during a run ------------------

READ_ONLY = {("ticket", "show"), ("ticket", "join"), ("results", "show"), ("config", None),
             ("status", "parse"), ("log", "tail"), ("paths", None)}


def _in_flight(root: Path) -> list[str]:
    """Every run in flight on the store: the union of its tickets' in_flight lists."""
    return [rid for p in sorted((root / "tickets").glob("*.yaml"))
            for rid in store.read_yaml(p).get("in_flight") or []]


def fence(inst: Path, cfg: dict, root: Path) -> None:
    """Refuse a write to the instance's own store from inside its runs/ or worktrees/ (marker or
    not), or while a run is in flight there unless FACTORY_DISPATCH=1. Accidents, not isolation."""
    if not instance.is_own_store(inst, cfg, root):
        return
    own, cwd = instance.own_state_root(inst, cfg), instance.caller_cwd()
    for sub in ("runs", "worktrees"):
        if cwd.is_relative_to(own / sub):
            raise Refused(f"role runs may not write the live store ({own}; called from inside its {sub}/); "
                          "use a throwaway FACTORY_STATE")
    if os.environ.get("FACTORY_DISPATCH") == "1":
        return
    runs = _in_flight(root)
    if runs:
        raise Refused(f"role runs may not write the live store ({root}; in flight: {', '.join(runs)}); "
                      "use a throwaway FACTORY_STATE")


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.cmd in ("init", "paths"):  # exempt from the instance refusal (design B.1)
            a.fn(a)
            return 0
        inst = instance.require()  # refused when no instance is found: nothing is written
        cfg = instance.load_config(inst)
        root = store.state_root(cfg)
        if (a.cmd, getattr(a, "sub", None)) not in READ_ONLY or a.accept_harness:
            fence(inst, cfg, root)  # before the lock, so a fenced --accept-harness rewrites nothing
        instance.guard(inst, cfg, root, a.accept_harness)  # the harness lock (design C.2-C.4)
        a.fn(a, root, cfg)
        return 0
    except Refused as e:
        print(str(e), file=sys.stderr)
        out({"ok": False, "error": str(e)})
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"factory: {type(e).__name__}: {e}", file=sys.stderr)
        out({"ok": False, "error": f"{type(e).__name__}: {e}"})
        return 1


if __name__ == "__main__":
    sys.exit(main())
