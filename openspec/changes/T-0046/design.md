## Proposed change

Every part keeps each caller's refusal text, park reason, event fields, field order and result exactly. The parts are listed in the order to build them. Every function this change makes unused is deleted: `compose._runs_for`, and `stats.py`'s import of `_records`. The harness-code requirement that the harness keeps no unused definition applies.

**A. One run iterator (`factory/store.py`).**
Add `ticket_runs(root: Path, ticket: str, role: str | None = None, finished: bool = False)`.
- It yields `(run_id, meta)` for each `runs/<run_id>/meta.yaml`, in run-id (directory name) order.
- It skips a directory with no `meta.yaml`, or with an empty one (see Decisions).
- It yields only runs whose meta has `ticket == ticket`. When `role` is given, it also requires `role == role`. When `finished` is true, it also requires a truthy `finished`.
- A missing `runs/` yields nothing.

Its callers:
- `compose.py`: delete `_runs_for`. Its two uses become `[r for r, _ in store.ticket_runs(root, tid, role, finished=True) if r != run_id]`. The round filter at `compose.py:413` reads `round` from the yielded meta and does not re-read the file.
- `specstore.critic_rounds`: `ticket_runs(root, tid, "critic", finished=True)`. It reads `output.md` from `root / "runs" / run_id`.
- `cli._parent_close_verified`: `ticket_runs(root, t["id"], "verifier")`, with no finished filter, keeping its own `status == "VERIFIED"` and `head` checks. It returns the run id.
- `store.clear_scratch`: `ticket_runs(root, tid, finished=True)`. For each run, `runs/<id>/scratch` is unlinked when it is a symlink, removed with `shutil.rmtree` when it is a directory, and otherwise left alone. The comment about read-only directories stays.

`next_run_id` (`store.py:163`) lists run names, not a ticket's runs, and stays as it is.

**B. Event-log readers (`factory/store.py`, `factory/cost.py`, `factory/stats.py`).**
- Add `store.log_lines(root: Path)`. It yields each line (`str.splitlines()`) of each `log/*.jsonl` file, files in sorted name order. A missing `log/` yields nothing.
- `cli._recorded_plan_run` loops over `store.log_lines(root)` with `json.loads`. `cli.log_tail` builds its list from it. Both keep their own parsing, filtering and printing.
- Add `cost._log_records(store: str)`. It yields `_records(lf)` for each `log/*.jsonl` file of `store`, in sorted name order.
- `cost._store_paths` and `stats._load` loop over `_log_records`. `stats._load` keeps its `isinstance(e, dict) and e.get("ts")` filter and its sort.
- `stats.py` imports `_log_records` in place of `_records`.

**C. One transition record (`factory/store.py`).**
Add `record_transition(root, t, to, by, history=None, event=None) -> str`. It does the following, in order, and returns `frm`:
1. Set `frm = t["status"]` and `t["status"] = to`.
2. Append `{"ts": now(), "from": frm, "to": to, "by": by, **(history or {})}` to `t["history"]`.
3. `save_ticket(root, t)`.
4. `log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": to, "by": by, **(event or {})})`.

Its callers:
- `cli.ticket_transition`. It sets `t["parked"] = None` when `a.to != "parked"` before the call. It passes `history={"round": dict(t["round"]), **({"verified_by": verified_by} if verified_by else {})}` and `event={"round": t["round"]}`.
- `ticket_ready_implementers` (`cli.py:818-821`), with by `"ready-implementers"`.
- the dependant release in `merge` (`cli.py:1000-1003`), with by `"merge"`.
- `parent_check` (`cli.py:1063-1067`), with by `"parent-check"`.

`approve_spec` is not changed.

**D. In-flight runs (`factory/store.py`).**
Add `in_flight_runs(root, t) -> list[str]`, which returns `[r for x in (t, *subtickets_of(root, t["id"])) for r in x.get("in_flight") or []]`. `cli.spec_amend` (`cli.py:602-605`) and `drive._same_ticket_guard` (`drive.py:626`) use it. `spec_amend` keeps its own `subs` for its later lines. Both refusal texts are unchanged.

**E. Integration-branch tip (`factory/gitops.py`).**
Add `integration_tip(cfg, repo) -> str`, which returns `rev(repo, integration_branch(cfg, repo))`. The four `cli.py` sites (`254`, `328`, `545`, `1693`) call it.

**F. Smaller `cli.py` repeats (`factory/cli.py`).** Four helpers:
- `_copy_record(d: Path, kind: str, src) -> Path` sets `dest = d / f"{kind}-{_next_n(d, kind)}.md"`, runs `shutil.copyfile(src, dest)` and returns `dest`. It is used for the changes notes (`request_changes`) and the four ruling copies in `resolve`.
- `_supersede(root, t) -> tuple` reads `head = t.get("head")` and `moved = _set_aside_failed_rows(root, t)`, logs `results.superseded` with `ticket`, `head` and `roles=moved`, and returns `(head, moved)`. It is used by the reviewer-ESCALATE ruling and by `--redispatch`, at the same point in each branch as today.
- `_planner_run(root, run: str, tid: str) -> Path` returns `_run_dir(root, run)`. When that run's meta is not a PLANNED planner run of `tid`, it raises `Refused(f"{run} is not a PLANNED planner run of {tid}")`. `subticket_add` and `spec_tasks` use it, each at the point where it checks today.
- `_refuse_unless_applies(root, text, refusal: str)` runs `specstore.validate` and then, when that is clean, `specstore.applies`. On any error it raises `Refused(f"{refusal}: " + "; ".join(errors))`. `approve_spec` passes `"spec not pinned"` and `spec_amend` passes `"spec not amended"`, each inside its existing `is_active` block.

**G. Dispatcher parks (`factory/drive.py`).** Two module-level helpers:
- `_harness_bug(what: str, res: dict) -> str` returns `f"harness-bug: {what}: {res.get('stderr') or ''}"`, written on one line. All 18 reasons of that form use it, including the three inside conditional expressions (`192`, `453`, `517`) and the loop at `353`, which passes its `what`. Each `what` is the text between `harness-bug: ` and `: {` today, so `run start {role}`, `run compose {role}`, `run finish {role}`, `results record {role}`, `spec add`, `transition to critic`, `round increment refused`, `plan whole-spec`, `ready-implementers`, `ticket head`, `join`, `transition to checks`, `no head for the checkers`, `results show` and `merge` keep their current text.
- `_cleanup_checker(role: str, rid: str)` calls `call("run", "cleanup", rid)` when `role in CHECKERS`. It is used at `drive.py:225-226`, `233-234` and `574-575`.

The five "unknown STATUS" parks and the `wait` park (`drive.py:529`) do not carry a command's error text and stay as they are.

**PR description.** It reports `git diff --stat main...HEAD -- factory` (the line change per file), as the request asks.

## Tests to change

none

