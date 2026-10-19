"""Gates: review and verification results, the merge gate, join, the parent check and archive."""
from __future__ import annotations

import re
from pathlib import Path

from factory import gitops, specstore, status, store, subtickets
from factory.common import out
from factory.store import Refused


def ticket_head(a, root, cfg):
    t = store.load_ticket(root, a.id)
    changed = store.set_head(root, cfg, t)
    out({"ok": True, "id": t["id"], "head": t["head"], "branch": t["branch"], "changed": changed,
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
    repo = gitops.repo_root()
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
    repo = gitops.repo_root()
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
                store.record_transition(root, s, "ready-for-implementer", "merge")
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
        store.record_transition(root, parent, "ready-for-parent-verify", "parent-check")
    reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
    out({"ok": True, "id": parent["id"], "state": parent["status"],
         "subtickets": {s["id"]: s["status"] for s in subs}, "superseded": [s["id"] for s in superseded],
         "reuse": reuse})


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
    repo = gitops.repo_root()
    if gitops.integration_tip(cfg, repo) != after:
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
    repo = gitops.repo_root()
    for rid, m in store.ticket_runs(root, t["id"], "verifier"):
        if m.get("status") != "VERIFIED" or not m.get("head"):
            continue
        if all(gitops.head_contains(repo, m["head"], s["merge"]["main_after"]) for s in subs if s["merge"].get("main_after")):
            return rid
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
