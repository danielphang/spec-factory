"""Ticket store on disk: tickets/, requests/, specs/, plans/, runs/, log/ under the state dir."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path

import yaml

RESULT_ROLES = ("reviewer", "verifier", "ci")


class Refused(Exception):  # noqa: N818
    """A guard refused the operation: exit 2, store unchanged, nothing logged."""


def state_root(cfg: dict | None = None) -> Path:
    """FACTORY_STATE, else the instance's `state_dir` under its repo root."""
    from factory import instance
    env = instance.env_path("FACTORY_STATE")
    if env:
        return env
    inst = instance.require()
    return instance.state_root(inst, cfg or instance.load_config(inst))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


STORE_GITIGNORE = ("# git worktrees the build half creates; they are checkouts, never store content\nworktrees/\nruns/*/wt/\n"
                   "# tripwire baselines: digests of the operator's live files, never committed\nruns/*/tripwire.yaml\n"
                   "# each run's scratch directory: its own temporary files, cleared when the ticket moves on\n"
                   "runs/*/scratch/\n"
                   "# the driver's status files: a live view of one `factory drive` process, never committed\n"
                   "drive/\n")


def ensure_gitignore(root: Path) -> None:
    """The store keeps implementer worktrees under worktrees/ and checker checkouts under runs/<id>/wt/.
    Both are nested git checkouts: a store committed by directory must not pick them up. Nor may it
    pick up a run's tripwire baseline, runs/<id>/tripwire.yaml, which holds digests of live files, or
    a run's temporary files under runs/<id>/scratch/, nor `factory drive`'s status files under drive/."""
    _ensure_block(root / ".gitignore", STORE_GITIGNORE)


STORE_GITATTRIBUTES = ("# run records embed verbatim diffs and outputs: their whitespace is not the store's to fix\n"
                       "runs/** -whitespace\n")


def ensure_gitattributes(root: Path) -> None:
    """Exempt run records from git's whitespace checks. A record under runs/ copies diffs and agent
    output verbatim, so `git diff --check` over store commits reported them (a blank diff context line
    is a single space). Every other store file is still checked."""
    _ensure_block(root / ".gitattributes", STORE_GITATTRIBUTES)


def _ensure_block(p: Path, block: str) -> None:
    """An absent or empty file gets the commented block; an existing one keeps its own lines and gains
    only the non-comment lines it lacks."""
    have = p.read_text(encoding="utf-8") if p.exists() else ""
    if not have.strip():
        write_text(p, block)
        return
    lines = have.splitlines()
    missing = [ln for ln in block.splitlines() if not ln.startswith("#") and ln not in lines]
    if missing:
        write_text(p, have.rstrip("\n") + "\n" + "".join(ln + "\n" for ln in missing))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_yaml(path: Path, obj) -> None:
    write_text(path, yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100))


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def log_event(root: Path, event: str, **fields) -> dict:
    line = {"ts": now(), "event": event, **fields}
    p = root / "log" / f"{line['ts'][:7]}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    return line


def log_lines(root: Path):
    """Each line of the event log, `log/*.jsonl` in file-name order; the caller parses it."""
    d = root / "log"
    for p in sorted(d.glob("*.jsonl")) if d.exists() else []:
        yield from p.read_text(encoding="utf-8").splitlines()


def implemented_since_ready(root: Path, tid: str) -> bool:
    """Whether ticket `tid`'s newest implementer run started after the ticket last entered
    ready-for-implementer, and finished READY-FOR-REVIEW. Read in the event log's order: its
    timestamps are whole seconds. A move into the state is any event of the ticket whose `to`, or
    for `ticket.created` whose `status`, is ready-for-implementer."""
    entered = started = -1
    run = status = None
    for i, ln in enumerate(log_lines(root)):
        e = json.loads(ln)
        if e.get("ticket") != tid:
            continue
        if e.get("to") == "ready-for-implementer" or (e["event"] == "ticket.created" and e.get("status") == "ready-for-implementer"):
            entered = i
        elif e["event"] == "run.started" and e.get("role") == "implementer":
            started, run, status = i, e.get("run"), None
        elif e["event"] == "run.finished" and e.get("run") == run:
            status = e.get("status")
    return started > entered and status == "READY-FOR-REVIEW"


def ticket_path(root: Path, tid: str) -> Path:
    return root / "tickets" / f"{tid}.yaml"


def load_ticket(root: Path, tid: str) -> dict:
    p = ticket_path(root, tid)
    if not p.exists():
        raise Refused(f"no ticket {tid}")
    return read_yaml(p)


def save_ticket(root: Path, t: dict) -> None:
    """Write ticket `t`. When its stored status changes to anything but `parked`, the ticket has moved
    on: clear its finished runs' scratch directories. A park keeps them for the human to inspect."""
    p = ticket_path(root, t["id"])
    before = read_yaml(p)["status"] if p.exists() else None
    write_yaml(p, t)
    if before is not None and t["status"] not in (before, "parked"):
        clear_scratch(root, t["id"])


def clear_scratch(root: Path, tid: str) -> None:
    """Remove runs/<id>/scratch of each finished run of ticket `tid`; runs in flight, other tickets'
    runs and every path outside runs/*/scratch are left alone."""
    for rid, _ in ticket_runs(root, tid, finished=True):
        d = root / "runs" / rid / "scratch"
        if d.is_symlink():
            d.unlink()
        elif d.is_dir():
            # factory: plain rmtree fails on a read-only directory inside scratch (a Go module cache,
            # say); add a chmod-and-retry handler if a run ever leaves one
            shutil.rmtree(d)


def ticket_runs(root: Path, ticket: str, role: str | None = None, finished: bool = False):
    """(run_id, meta) of each run of `ticket` in run-id order, only `role`'s when given and only
    finished ones when `finished`. A run whose meta.yaml is missing or still empty is skipped."""
    runs = root / "runs"
    for d in sorted(runs.iterdir()) if runs.exists() else []:
        mp = d / "meta.yaml"
        m = read_yaml(mp) if mp.exists() else None
        if (not m or m.get("ticket") != ticket or (role is not None and m.get("role") != role)
                or (finished and not m.get("finished"))):
            continue
        yield d.name, m


def in_flight_runs(root: Path, t: dict) -> list[str]:
    """The runs in flight on ticket `t` and on its sub-tickets."""
    return [r for x in (t, *subtickets_of(root, t["id"])) for r in x.get("in_flight") or []]


def record_transition(root: Path, t: dict, to: str, by: str, history: dict | None = None,
                      event: dict | None = None) -> str:
    """Move ticket `t` to status `to`: append its history entry (plus `history`), save it and log
    `ticket.transition` (plus `event`). Returns the status it left."""
    frm = t["status"]
    t["status"] = to
    t["history"].append({"ts": now(), "from": frm, "to": to, "by": by, **(history or {})})
    save_ticket(root, t)
    log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": to, "by": by, **(event or {})})
    return frm


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


def set_head(root: Path, cfg: dict, t: dict) -> bool:
    """Set ticket `t`'s head to the tip of its branch and save it, as `ticket head` does; returns
    whether the head changed. A merge-refused ticket whose new head contains the integration branch
    is cleared of the refusal; one whose head does not is a conflict run that did not merge it in."""
    from factory import gitops  # local: gitops imports this module
    if not t.get("branch"):
        raise Refused(f"{t['id']} has no branch yet")
    repo = gitops.repo_root()
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
            last = [r for r, _ in ticket_runs(root, t["id"], "implementer", finished=True)]
            if last and last[-1] != t.get("conflict_counted_run"):
                t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
                t["conflict_counted_run"] = last[-1]
    save_ticket(root, t)
    return changed


def park_ticket(root: Path, t: dict, reason: str, outputs: list[str], question: str | None = None,
                by: str = "park") -> None:
    """Park ticket `t` (the caller has checked it is not parked or closed): record where it came
    from, save it, and queue the reason for the operator."""
    frm = t["status"]
    t["status"] = "parked"
    t["parked"] = {"reason": reason, "since": now(), "from": frm, "outputs": outputs, "question": question}
    t["history"].append({"ts": now(), "from": frm, "to": "parked", "by": by, "reason": reason})
    save_ticket(root, t)
    log_event(root, "ticket.parked", ticket=t["id"], **{"from": frm, "reason": reason})
    log_event(root, "escalation.queued", ticket=t["id"], items=[reason])


def next_ticket_id(root: Path, prefix: str = "T") -> str:
    tickets = root / "tickets"
    nums = []
    if tickets.exists():
        for p in tickets.glob(f"{prefix}-*.yaml"):
            try:
                nums.append(int(p.stem.split("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefix}-{(max(nums) + 1 if nums else 1):04d}"


def next_run_id(root: Path, role: str) -> str:
    """Allocate a run id by creating its directory: mkdir is atomic, so two concurrent
    workflows on one store cannot be handed the same id (listing-then-naming could)."""
    runs = root / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    nums = []
    for p in runs.iterdir():
        try:
            nums.append(int(p.name.split("-")[1]))
        except (IndexError, ValueError):
            pass
    n = (max(nums) + 1) if nums else 1
    while True:
        rid = f"run-{n:04d}-{role}"
        try:
            (runs / rid).mkdir()
            return rid
        except FileExistsError:
            n += 1


def new_ticket(root: Path, tid: str, title: str, request_rel: str, source: str) -> dict:
    return {
        "id": tid,
        "type": None,
        "title": title,
        "request": request_rel,
        "source": source,
        "status": "ready-for-triage",
        "round": {"spec": 0, "pr": 0},
        "spec": {"version": 0, "approved_version": None},
        "plan": None,
        "in_flight": [],
        "parked": None,
        "created": now(),
        "history": [],
        # build half
        "parent": None, "depends_on": [], "parallel_safe": True,
        "branch": None, "head": None,
        "merge": {"base_before": None, "main_after": None},
        "parent_base": None,
    }


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def index_path(root: Path) -> Path:
    return root / "requests" / "index.yaml"


def load_index(root: Path) -> dict:
    p = index_path(root)
    return read_yaml(p) or {} if p.exists() else {}


def subtickets_of(root: Path, parent: str) -> list[dict]:
    """The parent's sub-ticket records, in id order (T-0001.1, T-0001.2, …)."""
    d = root / "tickets"
    out = []
    if d.exists():
        for p in d.glob(f"{parent}.*.yaml"):
            out.append(read_yaml(p))
    return sorted(out, key=lambda t: int(t["id"].rsplit(".", 1)[1]))


# ----- commit-bound results table (build spec part D) -----------------------------------------

def result_path(root: Path, head: str, role: str) -> Path:
    return root / "results" / head / f"{role}.yaml"


def record_result(root: Path, tid: str, head: str, role: str, status: str, run_id: str | None, detail: str | None = None,
                  extra: dict | None = None) -> dict:
    row = {"ticket": tid, "head": head, "role": role, "status": status, "run_id": run_id, "at": now()}
    if detail:
        row["detail"] = detail
    row.update(extra or {})
    write_yaml(result_path(root, head, role), row)
    return row


def results_for(root: Path, head: str) -> dict[str, dict]:
    d = root / "results" / head
    out = {}
    if d.exists():
        for p in d.glob("*.yaml"):
            out[p.stem] = read_yaml(p)
    return out
