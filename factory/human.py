"""Human decisions: approve-spec, request-changes, resolve, decision add, spec amend, and the escape and
intervention records the scorecard counts."""
from __future__ import annotations

import difflib
import getpass
import hashlib
import json
import shutil
from pathlib import Path

from factory import gitops, specstore, store, subtickets
from factory.common import _add_spec_version, _rel, out
from factory.gates import _branch_tip, undeclared_protected
from factory.store import Refused


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
    runs = store.in_flight_runs(root, t)
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
        _refuse_unless_applies(root, text, "spec not amended")
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


def _by() -> str:
    return getpass.getuser()


def _approval_dir(root: Path, tid: str) -> Path:
    d = root / "approvals" / tid
    d.mkdir(parents=True, exist_ok=True)
    return d


def _next_n(d: Path, kind: str) -> int:
    return len(list(d.glob(f"{kind}-*"))) + 1


def _refuse_unless_applies(root: Path, text: str, refusal: str) -> None:
    """Refuse spec `text` when it does not validate or its deltas do not apply to current truth."""
    _, deltas, errors = specstore.validate(text)
    errors += specstore.applies(root, deltas) if not errors else []
    if errors:
        raise Refused(f"{refusal}: " + "; ".join(errors))


def _copy_record(d: Path, kind: str, src) -> Path:
    """Copy `src` into approvals directory `d` as the next `<kind>-<n>.md`."""
    dest = d / f"{kind}-{_next_n(d, kind)}.md"
    shutil.copyfile(src, dest)
    return dest


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
        _refuse_unless_applies(root, text, "spec not pinned")
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
    dest = _copy_record(d, "changes", a.notes)
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
        # the harness failed to start an implementer run (e.g. a drift refusal the Workflow clerk
        # wrapped): routed as BLOCKED. Not a failed compose, which leaves its run in flight.
        start_bug = (reason.startswith("harness-bug: run start implementer:")
                     and parked.get("from") == "ready-for-implementer")
        if st != "parked" or not (reason.startswith(("ESCALATE", "BLOCKED")) or start_bug):
            if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
                raise Refused("use --answer")
            raise Refused("--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an "
                          f"implementer's run start; {t['id']} is {st} ({reason or 'no park'})")
        if reason.startswith("ESCALATE from reviewer"):
            # Back to its checks, same round: the reviewer runs again with the ruling in its input.
            head, moved = _supersede(root, t)
            dest = _copy_record(d, "ruling", a.ruling)
            move("checks-in-flight", "ruling", {"ruling": _rel(root, dest), "head": head, "superseded": moved})
            return
        if reason.startswith("BLOCKED") or start_bug:  # an implementer's or the gate's BLOCKED: back to the implementer, same round
            to = "ready-for-implementer"
        else:
            to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
        dest = _copy_record(d, "ruling", a.ruling)
        move(to, "ruling", {"ruling": _rel(root, dest)})
    elif a.accept_paths:
        # The merge gate refused a protected path the pinned spec does not declare; the human accepts
        # it under the approved design for this sub-ticket. Its results stand, so the build merges it.
        if st != "parked" or not reason.startswith("BLOCKED from merge gate:"):
            raise Refused("--accept-paths applies to a merge gate park (BLOCKED from merge gate); "
                          f"{t['id']} is {st} ({reason or 'no park'})")
        head = _branch_tip(gitops.repo_root(), t)
        paths, _ = undeclared_protected(root, cfg, t, head)
        if not paths:
            raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
        dest = _copy_record(d, "ruling", a.accept_paths)
        t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
        move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
    elif a.to == "checks":
        # A store command failed after the implementer finished (issue #112: its `run finish` reply
        # did not parse): back to its checks at the branch tip, with the round step the build applies.
        if not (st == "parked" and parked.get("from") == "ready-for-implementer" and reason.startswith("harness-bug:")
                and store.implemented_since_ready(root, t["id"])):
            raise Refused("--to checks applies to a sub-ticket parked by a harness-bug from ready-for-implementer after "
                          f"its implementer run finished READY-FOR-REVIEW; {t['id']} is {st} ({reason or 'no park'})")
        store.set_head(root, cfg, t)
        store._apply_round(t, "pr:init", cfg)
        move("checks-in-flight", "to-checks", {"head": t["head"]})
    elif a.to:
        if a.to != "spec-gate":
            raise Refused("--to accepts only spec-gate or checks")
        if st != "parked" or t["spec"]["version"] < 1:
            raise Refused(f"--to spec-gate needs a parked ticket with a spec version; {t['id']} is {st}")
        move("awaiting-spec-gate", "to-spec-gate", {})
    elif a.redispatch:
        # Re-run the checkers on the same head after the cause of the park is fixed outside the ticket
        # (a harness or gate defect, a killed checker). Round unchanged.
        if st != "parked" or parked.get("from") not in ("checks-in-flight", "ready-for-merge"):
            raise Refused(f"--redispatch applies to a sub-ticket parked from its checks; {t['id']} is {st} (from {parked.get('from')})")
        head, moved = _supersede(root, t)
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
        dest = _copy_record(d, "ruling", a.replan)
        move("ready-for-planner", "replan", {"ruling": _rel(root, dest)})
    elif a.close:
        if st == "closed":
            raise Refused(f"{t['id']} is already closed")
        move("closed", "close", decided("resolve --close"))
    else:
        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate|checks | --redispatch | "
                      "--replan F | --close")


def _supersede(root: Path, t: dict) -> tuple:
    """Set aside the head's failed result rows and log it; returns (head, roles moved)."""
    head, moved = t.get("head"), _set_aside_failed_rows(root, t)
    store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
    return head, moved


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


def escape_add(a, root, cfg):
    """`escape add T --issue TEXT [--note LINE]`: a merged change later needed a fix or a revert. The store
    is public and the issue may sit in a private tracker, so it keeps only the SHA-256 of the --issue text
    (UTF-8, exactly as given), never the text. Every refusal comes before the write."""
    parent, dot, _ = a.id.rpartition(".")
    if dot:
        raise Refused(f"escape add: {a.id} is a sub-ticket; record the escape on its parent {parent}")
    tid = store.load_ticket(root, a.id)["id"]
    events = (json.loads(ln) for ln in store.log_lines(root) if ln.strip())
    if not any(e.get("event") == "merge.done" and tid in (e.get("ticket"), str(e.get("ticket")).rpartition(".")[0])
               for e in events):  # a merge of the ticket itself or of one of its sub-tickets
        raise Refused(f"escape add: {tid} has no merge")
    if not a.issue.strip():
        raise Refused("escape add: --issue is empty")
    if a.note and "://" in a.note:
        raise Refused("escape add: keep links out of the note; the store keeps no link")
    digest = hashlib.sha256(a.issue.encode("utf-8")).hexdigest()
    store.log_event(root, "escape.recorded", ticket=tid, issue_sha256=digest, by=_by(),
                    **({"note": a.note} if a.note else {}))
    out({"ok": True, "id": tid, "issue_sha256": digest})


def intervention_add(a, root, cfg):
    """`intervention add --kind WORD [--ticket T] [--note LINE]`: the operator acted outside the CLI
    (a hand commit, a stopped run); the scorecard counts it as an intervention."""
    kind = a.kind.strip()
    if not kind:
        raise Refused("intervention add: --kind is empty")
    tid = store.load_ticket(root, a.ticket)["id"] if a.ticket else None
    if a.note and "://" in a.note:
        raise Refused("intervention add: keep links out of the note; the store keeps no link")
    extra = {k: v for k, v in (("ticket", tid), ("note", a.note)) if v}
    store.log_event(root, "intervention.recorded", kind=kind, by=_by(), **extra)
    out({"ok": True, "kind": kind, **({"id": tid} if tid else {})})
