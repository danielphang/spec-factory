"""`factory` store CLI (P0 subset of the build-harness spec, part B/K, plus the spec store).

Exit 0 success, 2 refused precondition (store unchanged, nothing logged), 1 error.
Every command prints one JSON object on stdout; refusals also print {"ok": false, "error"}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from factory import compose, cost, gitops, instance, launch, specstore, status, store, subtickets, tripwire, truth
from factory.common import _add_spec_version, _rel, fence, out
from factory.drift import _check_drift, _check_sibling_tests
from factory.gates import (_parent_close_verified, archive_cmd, merge_cmd, results_record, results_show,
                           ticket_head, ticket_join, ticket_parent_check)
from factory.human import _refuse_unless_applies, approve_spec, decision_add, escape_add, intervention_add, request_changes, resolve, spec_amend
from factory.setup import init_cmd, paths_cmd, store_migrate
from factory.store import Refused

ROLES = ("triage", "spec_writer", "critic", "planner", "implementer", "reviewer", "verifier")
BUILD_ROLES = ("implementer", "reviewer", "verifier")
PROMPTS = Path(__file__).resolve().parent / "prompts"


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
    store._apply_round(t, a.round, cfg)
    if a.to != "parked":
        t["parked"] = None
    store.record_transition(root, t, a.to, a.by,
                            history={"round": dict(t["round"]), **({"verified_by": verified_by} if verified_by else {})},
                            event={"round": t["round"]})
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


def _planner_run(root: Path, run: str, tid: str) -> Path:
    """Run `run`'s directory, refused unless it is a PLANNED planner run of ticket `tid`."""
    d = _run_dir(root, run)
    meta = store.read_yaml(d / "meta.yaml")
    if meta.get("ticket") != tid or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
        raise Refused(f"{run} is not a PLANNED planner run of {tid}")
    return d


def run_start(a, root, cfg):
    if a.role not in ROLES:
        raise Refused(f"unknown role {a.role}; roles: {', '.join(ROLES)}")
    model = cfg["models"][a.role]  # the instance is the only source of a role's model; --model only cross-checks it
    if a.model is not None and a.model != model:
        raise Refused(f"model {a.model} refused for {a.role}: the instance names {model}")
    t = store.load_ticket(root, a.ticket)
    parent_close = a.role == "verifier" and t["status"] == "ready-for-parent-verify"
    ready = cfg["ready_state"][a.role]
    if t["status"] != ready and not parent_close:
        raise Refused(f"{t['id']} is {t['status']}, not {ready}")
    if a.role in ("triage", "spec_writer", "critic", "planner", "implementer") and t["in_flight"]:
        raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
    if a.role in ("reviewer", "verifier") and any(a.role in r for r in t["in_flight"]):
        raise Refused(f"{t['id']} already has a {a.role} run in flight")
    if a.role == "implementer" and t.get("parent"):
        _check_drift(root, cfg, t)
        _check_sibling_tests(root, cfg, t)
    if a.role in BUILD_ROLES:
        compose.gate_entries(cfg)  # a malformed gate entry refuses here, before a run id is reserved
        compose.environment_sync(cfg)  # so does a malformed environment_sync
    baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
    rid = store.next_run_id(root, a.role)
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
    preamble = instance.fill_preamble((PROMPTS / "preamble.md").read_text(encoding="utf-8"), cfg)
    role_prompt = instance.fill_standards((PROMPTS / f"{a.role}.md").read_text(encoding="utf-8"))
    sysp = preamble.rstrip() + "\n\n" + role_prompt
    store.write_text(d / "system-prompt.txt", sysp)
    t["in_flight"].append(rid)
    store.save_ticket(root, t)
    store.log_event(root, "run.started", ticket=t["id"], run=rid, role=a.role, model=model)
    out({"ok": True, "run_id": rid, "role": a.role, "model": model, "worktree": meta.get("worktree"), "head": meta.get("head")})


def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent_close: bool) -> None:
    """Worktrees for the build roles (build spec I.3, local stand-in): the implementer gets the
    ticket's branch (created from the integration branch at first dispatch); each checker gets a
    detached checkout of the head it checks, plus the diff written as runs/<id>/diff.patch. Each
    checkout then runs the instance's `environment_sync`, if set (`_sync_environment`)."""
    sync = compose.environment_sync(cfg)
    repo = gitops.repo_root()
    integ = gitops.integration_branch(cfg, repo)
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


# A kept last message that says the run ended its turn still waiting on a command it started.
# factory: a word match, not a reading of intent: any message that mentions waiting matches. It only
# adds a phrase to a park a human reads; replace it if a misleading waiting reason is seen.
WAITING = re.compile(r"\bwait(?:ing)?\b|\bstill (?:running|in progress)\b|\bin the background\b", re.I)


def run_last_message(a, root, cfg):
    """Keep the agent's last message with a run that ended EMPTY-OUTPUT, so a human can see why."""
    d = _run_dir(root, a.run)
    st = store.read_yaml(d / "meta.yaml").get("status")
    if st != "EMPTY-OUTPUT":
        raise Refused(f"{a.run} is {st or 'not finished'}, not EMPTY-OUTPUT: no last message to keep")
    store.write_text(d / "last-message.md", a.text + "\n")
    out({"ok": True, "run_id": a.run, "last_message": _rel(root, d / "last-message.md"),
         "waiting": bool(WAITING.search(a.text))})


def run_cleanup(a, root, cfg):
    d = _run_dir(root, a.run)
    meta = store.read_yaml(d / "meta.yaml")
    wt = Path(meta.get("worktree") or "")
    if meta.get("role") in ("reviewer", "verifier") and wt.exists():
        gitops.remove_worktree(gitops.repo_root(), wt)
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
    if a.reply:
        meta["claude"] = _claude_record(a.reply)
    if a.transcripts and not isinstance((meta.get("claude") or {}).get("usage"), dict) and (
            rec := cost.transcript_record(a.transcripts, str(root), a.run, meta["started"])):
        meta["claude"] = rec
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


def _claude_record(path: str) -> dict | None:
    """What `run finish --reply FILE` keeps of a role process's reply (`claude -p --output-format
    json`): its session and cost, or None when FILE is not one JSON object. The reply's `result`
    text is left out: it repeats output.md."""
    try:
        reply = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(reply, dict):
        return None
    return {k: reply.get(k) for k in ("session_id", "total_cost_usd", "num_turns", "usage")}


# ----- driver ---------------------------------------------------------------------

def drive_cmd(a, root, cfg):
    from factory import drive  # local: the driver calls back into main() for every store call
    drive.drive(a, root, cfg)


def _at_least_one(v: str) -> int:
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError(f"{v} is less than 1")
    return n


# ----- spec / plan ----------------------------------------------------------------

def _text_from(a, root) -> str:
    if a.from_run:
        p = _run_dir(root, a.from_run) / "output.md"
        if not p.exists():
            raise Refused(f"{a.from_run} has no output.md")
        return status.strip_trailer(p.read_text(encoding="utf-8"))
    if a.file:
        return Path(a.file).read_text(encoding="utf-8")
    raise Refused("need --from-run RUN or --file F")


def spec_add(a, root, cfg):
    t, text = store.load_ticket(root, a.id), _text_from(a, root)
    if specstore.is_active(root) and not (a.from_run and store.read_yaml(root / "runs" / a.from_run / "meta.yaml").get("status") == "NEEDS-HUMAN"):
        _refuse_unless_applies(root, text, "spec not added")  # a NEEDS-HUMAN draft is stored unchecked, for the operator to read
    out({"ok": True, "id": t["id"], "version": (n := _add_spec_version(root, t, text, a.from_run or a.file, cfg)), "path": f"specs/{t['id']}/v{n}.md"})


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
    for ln in store.log_lines(root):
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
        d = _planner_run(root, a.run, parent["id"])
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
    planned = [r for r, _ in store.ticket_runs(root, t["id"], "planner", finished=True)]
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
            store.record_transition(root, s, "ready-for-implementer", "ready-implementers")
    out({"ok": True, "parent": a.id, "ready": ready, "subtickets": [s["id"] for s in every],
         "remaining": [s["id"] for s in subs if s["status"] not in ("merged", "parked", "closed")],
         "in_flight": [s["id"] for s in subs if s["in_flight"] or s["status"] in subtickets.IN_FLIGHT_STATES],
         "parked": [s["id"] for s in subs if s["status"] == "parked"],
         # stopped mid-check (a dispatcher that died or was stopped): no run in flight, so buildOne
         # resumes it from its stored state; the checkers re-run on its current head
         "resumable": [s["id"] for s in subs if s["status"] in subtickets.IN_FLIGHT_STATES and not s["in_flight"]],
         "closed": [s["id"] for s in subs if s["status"] == "closed"],
         "superseded": [s["id"] for s in superseded]})


# ----- spec store (doc §Harness, Spec store; part K) ----------------------------------

def stats_cmd(a):
    """What each role catches and costs, counted from one or more stores (factory/stats.py). Like
    `paths`, it needs no instance, runs no fence or lock check and writes nothing. With no --store it
    reads FACTORY_STATE, else the store of the instance found from the caller's directory."""
    from factory import stats  # local: stats imports ROLES from here
    since = stats.parse_when(a.since, "--since") if a.since else None
    until = stats.parse_when(a.until, "--until") if a.until else None
    cwd = instance.caller_cwd()  # bin/factory runs from the harness checkout: paths are the caller's
    roots = [(cwd / Path(p).expanduser()).resolve() for p in a.store]
    if not roots:
        inst = instance.find()
        root = instance.env_path("FACTORY_STATE") or (
            instance.state_root(inst, instance.load_config(inst)) if inst is not None else None)
        if root is None:
            raise Refused(f"factory stats: no store found: give --store PATH, set FACTORY_STATE, or run from "
                          f"inside an instance ({instance.not_found_message()})")
        roots = [root.resolve()]
    for r in roots:
        if not (r / "runs").is_dir() and not (r / "log").is_dir():
            raise Refused(f"factory stats: {r} is not a store: it has neither runs/ nor log/")
    fn = stats.scorecard if a.scorecard else stats.report
    print(fn([str(r) for r in roots], since, until,
             [str((cwd / Path(d).expanduser()).resolve()) for d in a.transcripts]), end="")


def spec_tasks(a, root, cfg):
    t = store.load_ticket(root, a.id)
    d = _planner_run(root, a.run, t["id"])
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


# ----- misc ---------------------------------------------------------------------

def config_cmd(a, root, cfg):
    out({"ok": True, **launch.config_values(root, cfg)})


def status_parse(a, root, cfg):
    out(status.parse(Path(a.file).read_text(encoding="utf-8")))


def log_tail(a, root, cfg):
    lines = list(store.log_lines(root))
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
    p.add_argument("--model", help="must match the instance's model for the role")
    p.set_defaults(fn=run_start)
    p = rn.add_parser("compose")
    p.add_argument("run")
    p.set_defaults(fn=run_compose)
    p = rn.add_parser("finish")
    p.add_argument("run")
    p.add_argument("--output-file")
    p.add_argument("--status-override")
    p.add_argument("--reply", help="the role process's reply (claude -p --output-format json): its session "
                                   "id, cost, turns and usage are recorded under claude: in meta.yaml")
    p.add_argument("--transcripts", action="append", default=[], metavar="DIR",
                   help="Claude Code transcripts: with no reply usage, the run's transcript's tokens are recorded")
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
    p = sp.add_parser("stats", help="count runs, verdicts, parks, spec catches and cost per role and model; "
                                    "reads stores, writes nothing")
    p.add_argument("--store", action="append", default=[], metavar="PATH",
                   help="a store to read (repeatable); default: FACTORY_STATE, else the instance's own store")
    p.add_argument("--since", metavar="WHEN", help="ISO date or date-time, UTC when no zone; inclusive")
    p.add_argument("--until", metavar="WHEN", help="ISO date or date-time, UTC when no zone; exclusive")
    p.add_argument("--transcripts", action="append", default=[], metavar="DIR",
                   help="a directory of Claude Code transcripts (*.jsonl at any depth) for runs with no "
                        "cost record, and for implementer gate failures (repeatable)")
    p.add_argument("--scorecard", action="store_true", help="print only the north star's scorecard; needs --since")
    p.set_defaults(fn=stats_cmd)
    truth.add_parser(sp)
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
    p.add_argument("--to", metavar="spec-gate|checks",
                   help="spec-gate: a parked ticket with a spec back to the spec gate; checks: a sub-ticket parked "
                        "by a harness-bug after its implementer finished READY-FOR-REVIEW back to its checks")
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
    p = sp.add_parser("escape").add_subparsers(dest="sub", required=True).add_parser(
        "add", help="record that a merged change later needed a fix; keeps --issue only as its SHA-256")
    p.add_argument("id")
    p.add_argument("--issue", required=True, metavar="TEXT")
    p.add_argument("--note", metavar="LINE")
    p.set_defaults(fn=escape_add)
    p = sp.add_parser("intervention").add_subparsers(dest="sub", required=True).add_parser(
        "add", help="record an action you took outside the CLI, for the scorecard")
    p.add_argument("--kind", required=True, metavar="WORD")
    p.add_argument("--ticket", metavar="ID")
    p.add_argument("--note", metavar="LINE")
    p.set_defaults(fn=intervention_add)

    p = sp.add_parser("drive", help="route TICKET's roles as the Workflow scripts do, each role one "
                                    "`claude -p` process; stops at the spec gate")
    p.add_argument("ticket")
    p.add_argument("--phase", choices=("intake", "build"), help="default: the one the stored state is in")
    p.add_argument("--parallel", type=_at_least_one, default=2, help="sub-tickets built at once (default 2)")
    p.add_argument("--prompt-mode", choices=("append", "replace"), default="append",
                   help="append the role prompt to Claude Code's system prompt, or replace it")
    p.set_defaults(fn=drive_cmd)
    p = sp.add_parser("config")
    p.set_defaults(fn=config_cmd)
    p = sp.add_parser("launch-script", help="write a launch copy of a workflow script, the instance's models, "
                                            "round limits and store in one line; prints its path as `script`")
    p.add_argument("name", choices=("intake", "build"))
    p.set_defaults(fn=launch.launch_script)
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

# `truth check`, `paths` and `stats` never reach the fence (main() runs them before it); they are listed
# so this set matches the documents' read-only list.
READ_ONLY = {("ticket", "show"), ("ticket", "join"), ("results", "show"), ("config", None),
             ("launch-script", None), ("status", "parse"), ("log", "tail"), ("truth", "check"), ("paths", None), ("stats", None)}


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.cmd in ("init", "paths", "stats", "truth") and a.accept_harness:
            raise Refused(f"factory {a.cmd}{' ' + a.sub if a.cmd == 'truth' else ''} never checks the harness lock, so it "
                          f"cannot accept a revision; run factory --accept-harness {a.accept_harness} config")
        # exempt from the instance refusal (design B.1); `paths`, `stats` and `truth check` only read, so
        # they also skip the fence and the harness lock; all four refuse --accept-harness (above, T-0058)
        if a.cmd in ("init", "paths", "stats", "truth"):
            return a.fn(a) or 0
        inst = instance.require()  # refused when no instance is found: nothing is written
        cfg = instance.load_config(inst)
        root = store.state_root(cfg)
        if (a.cmd, getattr(a, "sub", None)) not in READ_ONLY or a.accept_harness:
            # before the lock, so a fenced --accept-harness rewrites nothing; drive keeps only the
            # location rule unless it accepts a harness
            fence(inst, cfg, root, in_flight=a.cmd != "drive" or bool(a.accept_harness))
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
