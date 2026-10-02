"""`factory` store CLI (P0 subset of the build-harness spec, part B/K, plus the spec store).

Exit 0 success, 2 refused precondition (store unchanged, nothing logged), 1 error.
Every command prints one JSON object on stdout; refusals also print {"ok": false, "error"}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

from factory import compose, gitops, specstore, status, store, subtickets
from factory.store import Refused

ROLES = ("triage", "spec_writer", "critic", "planner", "implementer", "reviewer", "verifier")
BUILD_ROLES = ("implementer", "reviewer", "verifier")
PROMPTS = Path(__file__).resolve().parent / "prompts"


def out(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def _rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


# ----- ticket -----------------------------------------------------------------

def ticket_new(a, root, cfg):
    src = Path(a.file).expanduser().resolve()
    if not src.exists():
        raise Refused(f"no such file {src}")
    text = src.read_text(encoding="utf-8")
    h = store.content_hash(text)
    idx = store.load_index(root)
    for tid, rec in idx.items():
        if rec.get("hash") == h and not a.force:
            raise Refused(f"already imported as {tid} (same content); use --force to import again")
    tid = store.next_ticket_id(root)
    rel = f"requests/{tid}.md"
    store.write_text(root / rel, text)
    title = next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("#")), src.stem)
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
    out({"ok": True, "id": t["id"], "changes": changes})


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
    if a.to == "closed" and store.subtickets_of(root, t["id"]):
        # A parent closes through its parent-close run (then archive). A human who wants it closed
        # without one says so with `resolve --close`.
        if not _parent_close_verified(root, cfg, t):
            raise Refused(f"{t['id']} has sub-tickets: it closes after a VERIFIED parent-close run (or `resolve {t['id']} --close`)")
        if specstore.is_active(root) and specstore.change_dir(root, t["id"]).exists():
            raise Refused(f"{t['id']} is verified but not archived: run `archive {t['id']}` first")
    _apply_round(t, a.round, cfg)
    t["status"] = a.to
    if a.to != "parked":
        t["parked"] = None
    t["history"].append({"ts": store.now(), "from": frm, "to": a.to, "by": a.by, "round": dict(t["round"])})
    store.save_ticket(root, t)
    store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": a.to, "by": a.by, "round": t["round"]})
    out({"ok": True, "id": t["id"], "state": t["status"], "round": t["round"]})


def ticket_park(a, root, cfg):
    t = store.load_ticket(root, a.id)
    frm = t["status"]
    if frm in ("closed", "parked"):
        raise Refused(f"{t['id']} is {frm}; cannot park")
    t["status"] = "parked"
    t["parked"] = {"reason": a.reason, "since": store.now(), "from": frm,
                   "outputs": [x for x in (a.outputs or "").split(",") if x], "question": a.question}
    t["history"].append({"ts": store.now(), "from": frm, "to": "parked", "by": "park", "reason": a.reason})
    store.save_ticket(root, t)
    store.log_event(root, "ticket.parked", ticket=t["id"], **{"from": frm, "reason": a.reason})
    store.log_event(root, "escalation.queued", ticket=t["id"], items=[a.reason])
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
    rid = store.next_run_id(root, a.role)
    model = a.model or cfg["models"][a.role]
    d = root / "runs" / rid
    meta = {"run_id": rid, "role": a.role, "ticket": t["id"], "model": model, "round": t["round"]["spec"],
            "spec_version": t["spec"]["version"], "started": store.now(), "finished": None,
            "wall_s": None, "status": "running", "input_sources": None}
    if a.role in BUILD_ROLES:
        _start_build_run(root, cfg, t, meta, d, parent_close)
    store.write_yaml(d / "meta.yaml", meta)
    prompt_name = a.role
    sysp = (PROMPTS / "preamble.md").read_text(encoding="utf-8").rstrip() + "\n\n" + (PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8")
    store.write_text(d / "system-prompt.txt", sysp)
    t["in_flight"].append(rid)
    store.save_ticket(root, t)
    store.log_event(root, "run.started", ticket=t["id"], run=rid, role=a.role, model=model)
    out({"ok": True, "run_id": rid, "role": a.role, "model": model})


def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent_close: bool) -> None:
    """Worktrees for the build roles (build spec I.3, local stand-in): the implementer gets the
    ticket's branch (created from the integration branch at first dispatch); each checker gets a
    detached checkout of the head it checks, plus the diff written as runs/<id>/diff.patch."""
    repo = gitops.repo_root(cfg)
    integ = gitops.integration_branch(cfg, repo)
    meta["round"] = t["round"]["pr"]
    if meta["role"] == "implementer":
        branch = t.get("branch") or gitops.branch_of(t["id"])
        wt = root / "worktrees" / t["id"]
        if not wt.exists():
            gitops.add_worktree(repo, wt, branch, integ, new_branch=t.get("branch") is None)
        t["branch"] = branch
        meta.update({"branch": branch, "base": gitops.rev(repo, integ), "head": gitops.rev(repo, branch),
                     "worktree": str(wt), "resolution": "conflict" if t.get("merge_refused") else None})
    else:
        head = gitops.rev(repo, integ) if parent_close else t.get("head")
        base = (t.get("parent_base") or head) if parent_close else gitops.rev(repo, integ)
        if not head:
            raise Refused(f"{t['id']} has no head to check")
        wt = d / "wt"
        gitops.add_detached_worktree(repo, wt, head)
        if not parent_close:
            store.write_text(d / "diff.patch", gitops.diff(repo, base, head))
        meta.update({"branch": t.get("branch"), "base": base, "head": head, "worktree": str(wt)})


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
        parsed = {"status": "KILLED", "confidence": None, "escalations": [], "error": "empty output"}
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
    out({"ok": True, "run_id": a.run, "status": parsed["status"], "confidence": parsed.get("confidence"),
         "escalations": parsed.get("escalations", [])})


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


def _add_spec_version(root: Path, t: dict, text: str, source: str) -> int:
    n = t["spec"]["version"] + 1
    store.write_text(root / "specs" / t["id"] / f"v{n}.md", text)
    store.write_text(root / "specs" / f"{t['id']}.md", text)
    t["spec"]["version"] = n
    store.save_ticket(root, t)
    store.log_event(root, "spec.added", ticket=t["id"], version=n, source=source)
    return n


def spec_add(a, root, cfg):
    t = store.load_ticket(root, a.id)
    n = _add_spec_version(root, t, _text_from(a, root), a.from_run or a.file)
    out({"ok": True, "id": t["id"], "version": n, "path": f"specs/{t['id']}/v{n}.md"})


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

def subticket_add(a, root, cfg):
    parent = store.load_ticket(root, a.id)
    if parent["spec"]["approved_version"] is None:
        raise Refused(f"{parent['id']} has no approved spec")
    if a.run:
        d = _run_dir(root, a.run)
        meta = store.read_yaml(d / "meta.yaml")
        if meta.get("ticket") != parent["id"] or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
            raise Refused(f"{a.run} is not a PLANNED planner run of {parent['id']}")
        text = status.strip_trailer((d / "output.md").read_text(encoding="utf-8"))
    else:
        text = Path(a.file).read_text(encoding="utf-8")
    try:
        subs = subtickets.parse(text, parent["id"])
    except ValueError as e:
        raise Refused(str(e)) from None
    if not subs:
        raise Refused("no sub-tickets found (a head line `<id> / Title`, id like T-0001-A, ST-1 or T-0001.1, "
                      "then `Depends on:` and `Parallel-safe:`)")
    ids = {s["id"] for s in subs}
    made = []
    for sdef in subs:
        for dep in sdef["depends_on"]:
            if dep not in ids and not store.ticket_path(root, dep).exists():
                raise Refused(f"{sdef['id']} ({sdef['label']}) depends on {dep}, which is neither in this plan nor a ticket in the store")
        if store.ticket_path(root, sdef["id"]).exists():
            raise Refused(f"{sdef['id']} already exists")
    for sdef in subs:
        st = store.new_ticket(root, sdef["id"], sdef["title"], parent["request"], f"plan:{a.run or a.file}")
        st.update({"type": "sub-ticket", "parent": parent["id"], "label": sdef["label"], "depends_on": sdef["depends_on"],
                   "parallel_safe": sdef["parallel_safe"],
                   "status": "ready-for-implementer" if not sdef["depends_on"] else "waiting-dependencies"})
        st["spec"] = {"version": parent["spec"]["version"], "approved_version": parent["spec"]["approved_version"]}
        store.write_text(root / "specs" / sdef["id"] / "subticket.md", sdef["text"])
        store.save_ticket(root, st)
        store.log_event(root, "ticket.created", ticket=sdef["id"], parent=parent["id"], status=st["status"])
        made.append({"id": sdef["id"], "label": sdef["label"], "state": st["status"], "depends_on": sdef["depends_on"], "parallel_safe": sdef["parallel_safe"]})
    out({"ok": True, "parent": parent["id"], "subtickets": made})


def ticket_ready_implementers(a, root, cfg):
    subs = store.subtickets_of(root, a.id)

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
    out({"ok": True, "parent": a.id, "ready": ready,
         "remaining": [s["id"] for s in subs if s["status"] not in ("merged", "parked", "closed")],
         "in_flight": [s["id"] for s in subs if s["in_flight"] or s["status"] in subtickets.IN_FLIGHT_STATES],
         "parked": [s["id"] for s in subs if s["status"] == "parked"],
         "closed": [s["id"] for s in subs if s["status"] == "closed"]})


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
        else:  # a conflict run that did not merge the integration branch in: counted, so the loop is bounded
            t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
    store.save_ticket(root, t)
    out({"ok": True, "id": t["id"], "head": head, "branch": t["branch"], "changed": changed,
         "merge_refused": t.get("merge_refused"), "conflict_runs": int(t.get("conflict_runs") or 0)})


def results_record(a, root, cfg):
    t = store.load_ticket(root, a.id)
    if a.role not in ("reviewer", "verifier"):
        raise Refused("results record: --role reviewer|verifier")
    if not re.fullmatch(r"[0-9a-f]{40}", a.head or ""):
        raise Refused(f"results record: --head must be a full commit SHA, got {a.head!r}")
    text = Path(a.output).read_text(encoding="utf-8") if a.output else ""
    if a.killed:
        st = "KILLED"
    else:
        parsed = status.parse(text)
        st = parsed["status"] or "UNKNOWN"
    cm = re.search(r"^Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", text, re.M)
    if cm and not a.head.startswith(cm.group(1).lower()):
        raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
    stale = t.get("head") is not None and a.head != t.get("head")
    rows = [store.record_result(root, t["id"], a.head, a.role, st, a.run)]
    if a.role == "verifier" and not a.killed:
        m = re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)
        ci = (m.group(1), m.group(2).strip() or None) if m else ("FAIL", "missing Gate suite line")
        rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1]))
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


def merge_cmd(a, root, cfg):
    """Rule-4 checks (part G) in the local stand-in: ci PASS + APPROVE + VERIFIED on the current
    head, head contains the integration branch; then a local --no-ff merge. Exit 2 names the
    first failing condition; 'head does not contain main' is the conflict-run signal."""
    t = store.load_ticket(root, a.id)
    if t["status"] not in ("ready-for-merge", "checks-in-flight"):
        raise Refused(f"{t['id']} is {t['status']}, not ready-for-merge")
    repo = gitops.repo_root(cfg)
    integ = gitops.integration_branch(cfg, repo)
    head = t.get("head")
    if not head or gitops.rev(repo, t["branch"]) != head:
        raise Refused(f"{t['id']} head {head} is not the branch tip; run ticket head")
    rows = store.results_for(root, head)
    for role, want in (("ci", "PASS"), ("reviewer", "APPROVE"), ("verifier", "VERIFIED")):
        got = (rows.get(role) or {}).get("status")
        if got != want:
            raise Refused(f"{role} is {got or 'missing'} for {head[:9]}, need {want}")
    with gitops.MergeLock(repo):
        if not gitops.head_contains(repo, head, integ):
            t["merge_refused"] = "head does not contain main"
            t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
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
        if int(t.get("conflict_runs") or 0) > MAX_CONFLICT_RUNS:
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
    """When every sub-ticket is merged, the parent moves to ready-for-parent-verify (part G)."""
    parent = store.load_ticket(root, a.id)
    subs = store.subtickets_of(root, parent["id"])
    if not subs:
        raise Refused(f"{parent['id']} has no sub-tickets")
    if all(s["status"] == "merged" for s in subs) and parent["status"] == "planned":
        frm = parent["status"]
        parent["status"] = "ready-for-parent-verify"
        parent["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
        store.save_ticket(root, parent)
        store.log_event(root, "ticket.transition", ticket=parent["id"], **{"from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
    out({"ok": True, "id": parent["id"], "state": parent["status"],
         "subtickets": {s["id"]: s["status"] for s in subs}})


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
        n = _add_spec_version(root, t, text, f"gate edit {a.edit}")
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
    t = store.load_ticket(root, a.id)
    st, parked = t["status"], t["parked"] or {}
    reason = parked.get("reason", "")
    d = _approval_dir(root, t["id"])

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
        move(to, "answer", {"answer": n})
    elif a.ruling:
        if st != "parked" or not reason.startswith("ESCALATE"):
            if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
                raise Refused("use --answer")
            raise Refused(f"--ruling applies to an ESCALATE park; {t['id']} is {st} ({reason or 'no park'})")
        to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
        shutil.copyfile(a.ruling, dest)
        move(to, "ruling", {"ruling": _rel(root, dest)})
    elif a.to:
        if a.to != "spec-gate":
            raise Refused("--to accepts only spec-gate")
        if st != "parked" or t["spec"]["version"] < 1:
            raise Refused(f"--to spec-gate needs a parked ticket with a spec version; {t['id']} is {st}")
        move("awaiting-spec-gate", "to-spec-gate", {})
    elif a.close:
        if st == "closed":
            raise Refused(f"{t['id']} is already closed")
        move("closed", "close", {})
    else:
        raise Refused("resolve needs one of --answer F | --ruling F | --to spec-gate | --close")


# ----- spec store (doc §Harness, Spec store; part K) ----------------------------------

def init_cmd(a, root, cfg):
    written = specstore.init(root)
    store.log_event(root, "store.initialised", files=written)
    out({"ok": True, "written": written, "active": True})


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


def _parent_close_verified(root: Path, cfg: dict, t: dict) -> bool:
    """Every sub-ticket merged, and a finished verifier run on the parent itself said VERIFIED on a
    head that contains every one of those merges (a run from before the last merge does not count)."""
    subs = store.subtickets_of(root, t["id"])
    if any(s["status"] != "merged" for s in subs):
        return False
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
            return True
    return False


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
    p = rn.add_parser("cleanup")
    p.add_argument("run")
    p.set_defaults(fn=run_cleanup)

    sc = sp.add_parser("spec").add_subparsers(dest="sub", required=True)
    p = sc.add_parser("add")
    p.add_argument("id")
    p.add_argument("--from-run")
    p.add_argument("--file")
    p.set_defaults(fn=spec_add)
    pl = sp.add_parser("plan").add_subparsers(dest="sub", required=True)
    p = pl.add_parser("add")
    p.add_argument("id")
    p.add_argument("--from-run")
    p.add_argument("--file")
    p.set_defaults(fn=plan_add)

    p = sc.add_parser("tasks")
    p.add_argument("id")
    p.add_argument("--run", required=True)
    p.set_defaults(fn=spec_tasks)
    sb = sp.add_parser("subticket").add_subparsers(dest="sub", required=True)
    p = sb.add_parser("add")
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
    p.set_defaults(fn=init_cmd)
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
    p.add_argument("--to")
    p.add_argument("--close", action="store_true")
    p.set_defaults(fn=resolve)

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




def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    cfg = store.load_config()
    root = store.state_root(cfg)
    try:
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
