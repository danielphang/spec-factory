"""`factory drive TICKET`: the dispatcher as an ordinary process, with no clerk (T-0040).

It does the Workflow scripts' job without the Workflow tool. Every store call goes through the
CLI's own entry point, `factory.cli.main`, in this process, one at a time, so every guard, the
fence and the harness lock run as they do for `bin/factory`. Every role runs as one headless
`claude -p` process from its run directory, with its role's prompt, model, effort and tool limits;
its reply is kept as `runs/<id>/reply.json` and its cost recorded by `run finish --reply`.

The routing is a port of factory/workflows/intake.js and factory/workflows/build.js from
`// --- start` (build.js with its buildOne), branch for branch: the same commands, transitions,
round operations and park reasons, so a ticket driven here leaves the same records the script
leaves. Like the intake script, the driver stops at the spec gate. A head's two checkers run at
once, and ready sub-tickets build at once up to `--parallel N`.

One stdout line per step, `<ticket id> "<title>": <step>`, naming the ticket the step concerns (a
sub-ticket's steps name the sub-ticket), then the result as one JSON object. The store's
`drive/<ticket>.yaml` is a live view of this process (git ignores it). SIGINT or SIGTERM ends the
role processes, records their runs KILLED and parks nothing: running `factory drive` again
resumes from the stored state.
"""
from __future__ import annotations

import asyncio
import contextlib
import io
import json
import os
import re
import signal
import tempfile
from pathlib import Path

from factory import cli, store

INTAKE_STATES = ("ready-for-triage", "ready-for-spec-writer", "ready-for-critic")
BUILD_STATES = ("ready-for-planner", "planned", "ready-for-parent-verify")
CHECKERS = ("reviewer", "verifier")
# Every role gets these tools; the implementer also gets Edit. Anything else the session offers
# (sub-agents, task lists, notebook edits) is withheld: no role prompt asks for one.
TOOLS = "Read,Grep,Glob,Bash,Write,WebFetch,WebSearch"
ALLOWED = "Read,Grep,Glob,Bash,WebFetch,WebSearch"
PROMPT = ("Your entire input is the file {run}/input.md; read it first and follow it. "
          "Write your complete output to {run}/output.md and return the same text.")
KILL_AFTER_S = 10


def call(*argv: str) -> dict:
    """One store call: `factory.cli.main(argv)` with its output captured. Returns the last stdout
    line that is a JSON object, plus `exit` and `stderr`, normalised as the scripts' clerk() is: a
    non-zero exit is never ok, and a refusal always carries error text in `stderr`."""
    so, se = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
        try:
            code = cli.main(list(argv))
        except SystemExit as e:  # an argparse refusal
            code = e.code if isinstance(e.code, int) else 2
    err = se.getvalue()
    res = None
    for ln in reversed(so.getvalue().splitlines()):
        res = _json_object(ln)
        if res is not None:
            break
    if res is None:
        return {"ok": False, "exit": code, "stderr": err or f"exit {code}, no JSON on stdout",
                "error": "no JSON on stdout"}
    if code != 0:
        res["ok"] = False
    if not res.get("stderr") and err:
        res["stderr"] = err
    if res.get("ok") is False and not res.get("stderr"):
        res["stderr"] = res.get("error") or f"exit {code}, no error text"
    res["exit"] = code
    return res


def _json_object(text: str) -> dict | None:
    try:
        v = json.loads(text)
    except ValueError:
        return None
    return v if isinstance(v, dict) else None


def role_argv(role: str, run: str, model: str, prompt_mode: str, worktree: str | None,
              effort: str | None) -> list[str]:
    """The `claude` argv for one role run. `run` and `worktree` are real absolute paths, so each
    `Edit` rule's path starts with `//`, Claude Code's form for an absolute path."""
    tmp = os.path.realpath(tempfile.gettempdir())
    tools = TOOLS
    allowed = f"{ALLOWED},Edit(/{run}/output.md),Edit(/{run}/scratch/**),Edit(/{tmp}/**)"
    if role == "implementer":
        tools += ",Edit"
        if worktree:
            allowed += f",Edit(/{worktree}/**)"
    sysp = "--append-system-prompt-file" if prompt_mode == "append" else "--system-prompt-file"
    argv = ["-p", PROMPT.format(run=run), "--model", model, "--output-format", "json",
            "--permission-mode", "auto", sysp, f"{run}/system-prompt.txt",
            "--tools", tools, "--allowedTools", allowed]
    if role == "implementer" and worktree:
        argv += ["--add-dir", worktree]
    if effort:
        argv += ["--effort", str(effort)]
    return argv


def _failure_message(reply: dict | None, stderr: str, code: int | None) -> str:
    """Why a role process failed: its reply's `result`, else the last non-blank line of stderr,
    else its exit code."""
    said = (reply or {}).get("result")
    if isinstance(said, str) and said.strip():
        return said.strip()
    lines = [ln for ln in stderr.splitlines() if ln.strip()]
    return lines[-1].strip() if lines else f"exit {code}"


class Driver:
    def __init__(self, a, root: Path, cfg: dict):
        self.ticket = a.ticket
        self.phase = a.phase
        self.parallel = a.parallel
        self.prompt_mode = a.prompt_mode
        self.root = root
        self.effort = cfg.get("effort") or {}
        self.models: dict = {}
        self.max_spec = 2
        self.title = ""
        self.titles: dict[str, str] = {}  # sub-ticket id -> title, read by build_one
        self.running: dict[str, dict] = {}  # run id -> {run, role, ticket, pid}: this driver's runs in flight
        self.procs: dict[str, asyncio.subprocess.Process] = {}
        self.stopped: signal.Signals | None = None
        self.status: dict = {}
        self.status_path = root / "drive" / f"{self.ticket}.yaml"

    # ----- status ---------------------------------------------------------------------

    def write_status(self, **changes) -> None:
        self.status.update(changes, title=self.title, updated=store.now(),
                           running=[dict(r) for r in self.running.values()])
        store.write_yaml(self.status_path, self.status)

    def step(self, text: str, ticket: str | None = None) -> None:
        ticket = ticket or self.ticket
        text = " ".join(ln.strip() for ln in text.strip().splitlines())  # a park reason may end in stderr's newline
        line = f'{ticket} "{self.titles.get(ticket, self.title)}": {text}'
        print(line, flush=True)
        self.write_status(last=line)

    # ----- store calls the routing makes ------------------------------------------------

    def park(self, ticket: str, reason: str, outputs: list[str]) -> None:
        argv = ["ticket", "park", ticket, "--reason=" + reason.replace('"', "'")]
        if outputs:
            argv += ["--outputs", ",".join(outputs)]
        call(*argv)
        self.step(f"parked: {reason}", ticket)

    def transition(self, to: str, round_op: str | None = None, ticket: str | None = None) -> dict:
        ticket = ticket or self.ticket
        argv = ["ticket", "transition", ticket, "--to", to, "--by", "workflow"]
        res = call(*argv, *(["--round", round_op] if round_op else []))
        self.step(f"-> {to}" if res["ok"] else f"-> {to} refused: {res.get('stderr', '').strip()}", ticket)
        return res

    # ----- role runs ----------------------------------------------------------------------

    async def run_role(self, role: str, ticket: str) -> dict | None:
        """runRole: an EMPTY-OUTPUT run is re-dispatched once; a second in a row parks the ticket.
        None means the ticket was parked."""
        first = await self.run_once(role, ticket)
        if not first or first["status"] != "EMPTY-OUTPUT":
            return first
        self.step(f"{role} {first['runId']}: EMPTY-OUTPUT; re-dispatching {role} once", ticket)
        second = await self.run_once(role, ticket)
        if not second or second["status"] != "EMPTY-OUTPUT":
            return second
        self.park(ticket, f"EMPTY-OUTPUT from {role}", [first["runId"], second["runId"]])
        return None

    async def run_once(self, role: str, ticket: str) -> dict | None:
        start = call("run", "start", "--role", role, "--ticket", ticket, "--model", self.models[role])
        if not start["ok"]:
            # A refusal that starts `BLOCKED ` is the harness blocking the run (the sibling-tests
            # check): parked verbatim, so `resolve --ruling` treats it as an implementer's BLOCKED.
            err = start.get("error")
            blocked = isinstance(err, str) and err.startswith("BLOCKED ")
            self.park(ticket, err if blocked else f"harness-bug: run start {role}: {start.get('stderr') or ''}", [])
            return None
        rid = start["run_id"]
        comp = call("run", "compose", rid)
        if not comp["ok"]:
            self.park(ticket, f"harness-bug: run compose {role}: {comp.get('stderr') or ''}", [rid])
            return None
        run = os.path.realpath(self.root / "runs" / rid)
        wt = os.path.realpath(start["worktree"]) if start.get("worktree") else None
        argv = role_argv(role, run, start.get("model") or self.models[role], self.prompt_mode, wt,
                         self.effort.get(role))
        env = {k: v for k, v in os.environ.items() if k != "FACTORY_DISPATCH"}
        self.running[rid] = {"run": rid, "role": role, "ticket": ticket, "pid": None}
        try:
            proc = await asyncio.create_subprocess_exec(
                "claude", *argv, cwd=run, env=env, stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except OSError as e:
            code, out, err = None, b"", f"cannot start claude: {e}"
        else:
            self.procs[rid] = proc
            self.running[rid]["pid"] = proc.pid
            self.step(f"start {role} {rid}", ticket)
            out, errb = await proc.communicate()
            code, err = proc.returncode, errb.decode("utf-8", "replace")
            self.procs.pop(rid, None)
        reply_path = os.path.join(run, "reply.json")
        store.write_text(Path(reply_path), out.decode("utf-8", "replace"))
        reply = _json_object(out.decode("utf-8", "replace"))
        if code != 0 or reply is None:
            # A failed call is treated as a thrown agent() call: the run is recorded KILLED and the
            # ticket parked with the error, so no run is left in flight. No retry.
            call("run", "finish", rid, "--status-override", "KILLED", "--reply", reply_path)
            if role in CHECKERS:
                call("run", "cleanup", rid)
            self.running.pop(rid, None)
            self.step(f"{role} {rid}: KILLED", ticket)
            self.park(ticket, f"agent call failed: {role}: {_failure_message(reply, err, code)}", [rid])
            return None
        # run finish reads the output file for every run: a missing or blank one is EMPTY-OUTPUT.
        fin = call("run", "finish", rid, "--reply", reply_path)
        if role in CHECKERS:
            call("run", "cleanup", rid)
        self.running.pop(rid, None)
        if not fin["ok"]:
            self.park(ticket, f"harness-bug: run finish {role}: {fin.get('stderr') or ''}", [rid])
            return None
        if fin.get("parked"):  # the tripwire saw a listed live file change: do not route on STATUS
            self.step(f"parked: {fin['parked']}", ticket)
            return None
        said = reply.get("result").strip() if isinstance(reply.get("result"), str) else ""
        if fin["status"] == "EMPTY-OUTPUT" and said:
            call("run", "last-message", rid, "--text=" + said[-4000:])
        esc = fin.get("escalations") or []
        self.step(f"{role} {rid}: {fin['status']}" + (f" (+{len(esc)} escalations)" if esc else ""), ticket)
        return {"runId": rid, "status": fin["status"], "escalations": esc, "outputPath": os.path.join(run, "output.md")}

    # ----- intake: factory/workflows/intake.js from `// --- start` ---------------------------

    async def intake(self, state: str, rnd: int) -> dict:
        T = self.ticket
        parked = {"ticket": T, "state": "parked"}
        if state == "ready-for-triage":
            t = await self.run_role("triage", T)
            if not t:
                return parked
            if t["status"] == "ACCEPT":
                self.transition("ready-for-spec-writer")
                state = "ready-for-spec-writer"
                show = call("ticket", "show", T, "--json")  # triage ACCEPT may have retitled it
                if show["ok"]:
                    self.title = show["title"]
            elif t["status"] == "REJECT":
                self.transition("closed")
                return {"ticket": T, "state": "closed", "triage": t}
            elif t["status"] == "NEEDS-HUMAN":
                self.park(T, "NEEDS-HUMAN from triage", [t["runId"]])
                return {**parked, "triage": t}
            elif t["status"] == "CLARIFY":
                self.transition("waiting-requester")
                return {"ticket": T, "state": "waiting-requester", "triage": t}
            else:
                self.park(T, f"harness-bug: unknown STATUS {t['status']} from triage", [t["runId"]])
                return parked
        if state not in ("ready-for-spec-writer", "ready-for-critic"):
            return {"ticket": T, "state": state, "note": "nothing to dispatch from this state"}
        while True:
            if state == "ready-for-spec-writer":
                w = await self.run_role("spec_writer", T)
                if not w:
                    return parked
                if w["status"] == "NEEDS-HUMAN":
                    call("spec", "add", T, "--from-run", w["runId"])
                    self.park(T, "NEEDS-HUMAN from spec writer", [w["runId"]])
                    return parked
                if w["status"] not in ("READY-FOR-CRITIC", "NEEDS-SPLIT"):
                    self.park(T, f"harness-bug: unknown STATUS {w['status']} from spec writer", [w["runId"]])
                    return parked
                added = call("spec", "add", T, "--from-run", w["runId"])
                if not added["ok"]:
                    self.park(T, f"harness-bug: spec add: {added.get('stderr') or ''}", [w["runId"]])
                    return parked
                tr = self.transition("ready-for-critic", "spec:init")
                if not tr["ok"]:
                    self.park(T, f"harness-bug: transition to critic: {tr.get('stderr') or ''}", [w["runId"]])
                    return parked
                rnd = _spec_round(tr, rnd)
                state = "ready-for-critic"
            c = await self.run_role("critic", T)
            if not c:
                return parked
            if c["status"] == "APPROVE":
                self.transition("awaiting-spec-gate")
                self.step(f"spec approved by critic in round {rnd}; awaiting the human gate "
                          f"(bin/factory approve-spec {T})")
                return {"ticket": T, "state": "awaiting-spec-gate", "rounds": rnd}
            if c["status"] == "ESCALATE":
                self.park(T, "ESCALATE from critic", [c["runId"]])
                return {**parked, "rounds": rnd}
            if c["status"] != "REVISE":
                self.park(T, f"harness-bug: unknown STATUS {c['status']} from critic", [c["runId"]])
                return parked
            if rnd < self.max_spec:
                tr = self.transition("ready-for-spec-writer", "spec:+1")
                if not tr["ok"]:
                    self.park(T, f"harness-bug: round increment refused: {tr.get('stderr') or ''}", [c["runId"]])
                    return parked
                rnd = _spec_round(tr, rnd)
                state = "ready-for-spec-writer"
                continue
            self.park(T, "max rounds", [c["runId"]])
            return {**parked, "rounds": rnd, "reason": "max rounds"}

    # ----- build: factory/workflows/build.js from `// --- start` ----------------------------

    async def build(self, state: str) -> dict:
        T = self.ticket
        parked = {"ticket": T, "state": "parked"}
        if state == "ready-for-planner":  # phase 1: Plan
            # A spec that needs one sub-ticket becomes it without a planner run; the harness decides which.
            whole = call("plan", "whole-spec", T)
            if not whole["ok"]:
                self.park(T, f"harness-bug: plan whole-spec: {whole.get('stderr') or ''}", [])
                return parked
            if whole.get("planner") == "skipped":
                self.step(f"planner skipped ({whole.get('reason')}); one sub-ticket from the whole spec")
            else:
                p = await self.run_role("planner", T)
                if not p:
                    return parked
                if p["status"] == "ESCALATE":
                    self.park(T, "ESCALATE from planner", [p["runId"]])
                    return parked
                if p["status"] != "PLANNED":
                    self.park(T, f"harness-bug: unknown STATUS {p['status']} from planner", [p["runId"]])
                    return parked
                for what, argv in (("spec tasks", ("spec", "tasks", T, "--run", p["runId"])),
                                   ("plan add", ("plan", "add", T, "--from-run", p["runId"])),
                                   ("subticket add", ("subticket", "add", T, "--run", p["runId"]))):
                    res = call(*argv)
                    if not res["ok"]:
                        self.park(T, f"harness-bug: {what}: {res.get('stderr') or ''}", [p["runId"]])
                        return parked
            self.transition("planned")
            state = "planned"
        if state == "planned":  # phase 2: Build, while any sub-ticket is not merged, parked or closed
            sem = asyncio.Semaphore(self.parallel)

            async def bounded(st: str) -> None:
                async with sem:
                    await self.build_one(st)

            first = True
            while True:
                ready = call("ticket", "ready-implementers", T)
                if not ready["ok"]:
                    self.park(T, f"harness-bug: ready-implementers: {ready.get('stderr') or ''}", [])
                    return parked
                # A parent planned with no sub-tickets (e.g. by an older intake): create them once from
                # the planner run its recorded plan names, or park the parent saying why.
                if first and ready.get("subtickets") == []:
                    first = False
                    made = call("subticket", "add", T)
                    if not made["ok"]:
                        self.park(T, "no sub-tickets, and none could be created from the recorded plan: "
                                     f"{made.get('stderr') or ''}", [])
                        return parked
                    self.step(f"created {len(made.get('subtickets') or [])} sub-ticket(s) from the recorded plan")
                    continue
                first = False
                # A sub-ticket the human closed parks the parent: amend the spec and re-plan, or close.
                if ready.get("closed"):
                    self.park(T, f"sub-ticket closed by a human: {', '.join(ready['closed'])}", [])
                    return parked
                todo = ready["ready"] + (ready.get("resumable") or [])
                if not todo:
                    if ready["remaining"]:
                        self.step(f"{len(ready['remaining'])} sub-ticket(s) parked or waiting on a human")
                        return {"ticket": T, "state": "planned", "remaining": ready["remaining"]}
                    break
                if ready.get("resumable"):
                    self.step(f"resuming {', '.join(ready['resumable'])} from its stored state")
                await _all(bounded(st) for st in todo)
            pc = call("ticket", "parent-check", T)
            if not pc["ok"]:
                self.park(T, f"parent-check refused: {pc.get('stderr') or ''}", [])
                return parked
            if pc.get("state") != "ready-for-parent-verify":
                return {"ticket": T, "state": pc.get("state") or "planned"}
            state = "ready-for-parent-verify"
        if state == "ready-for-parent-verify":  # phase 3: Close
            # Asked again here: a resumed build may arrive already in ready-for-parent-verify. `reuse`
            # names a single sub-ticket's VERIFIED run that stands for the parent-close run.
            pc = call("ticket", "parent-check", T)
            rid = pc.get("reuse") if pc["ok"] else None
            if rid:
                self.step(f"sub-ticket verifier run {rid} stands for the parent-close run; no new verifier run")
            else:
                v = await self.run_role("verifier", T)
                if not v:
                    return parked
                if v["status"] != "VERIFIED":
                    self.park(T, f"{v['status']} from parent-close verifier", [v["runId"]])
                    return parked
                rid = v["runId"]
            arch = call("archive", T)
            if not arch["ok"]:
                self.park(T, f"archive: {arch.get('stderr') or ''}", [rid])
                return parked
            self.transition("closed")
            return {"ticket": T, "state": "closed", "archived_to": arch.get("archived_to")}
        return {"ticket": T, "state": state, "note": "nothing to dispatch from this state"}

    async def build_one(self, st: str) -> None:
        """buildOne: one sub-ticket through the PR loop. The routing after the checkers is `ticket
        join`'s decision: merge, revise, conflict, wait or park; this only carries it out."""
        while True:
            show = call("ticket", "show", st, "--json")
            if not show["ok"]:
                return
            self.titles[st] = show["title"]
            implemented = show["state"] == "ready-for-implementer"
            if implemented:
                impl = await self.run_role("implementer", st)
                if not impl:
                    return
                if impl["status"] == "BLOCKED":
                    self.park(st, "BLOCKED from implementer", [impl["runId"]])
                    return
                if impl["status"] != "READY-FOR-REVIEW":
                    self.park(st, f"harness-bug: unknown STATUS {impl['status']} from implementer", [impl["runId"]])
                    return
                moved = call("ticket", "head", st)
                if not moved["ok"]:
                    self.park(st, f"harness-bug: ticket head: {moved.get('stderr') or ''}", [impl["runId"]])
                    return
                if moved.get("merge_refused"):
                    # A conflict run that did not merge the integration branch in: no point checking that head.
                    j = call("ticket", "join", st)
                    if j["ok"] and j.get("decision") == "conflict":
                        continue
                    self.park(st, (j.get("reason") or "") if j["ok"] else f"harness-bug: join: {j.get('stderr') or ''}",
                              [impl["runId"]])
                    return
                tr = self.transition("checks-in-flight", "pr:init", st)
                if not tr["ok"]:
                    self.park(st, f"harness-bug: transition to checks: {tr.get('stderr') or ''}", [impl["runId"]])
                    return
            elif show["state"] != "checks-in-flight":
                return  # parked, merged, closed or waiting: nothing for this loop to do
            # The checkers on the same head, at once; each result recorded against that head. After an
            # implementer run both run. Entered at checks-in-flight (a redispatch or a resumed
            # sub-ticket), only the checkers with no row on this head run; the verifier writes the ci row too.
            head_now = call("ticket", "head", st)
            sha = head_now.get("head") if head_now["ok"] else None
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
                self.park(st, f"harness-bug: no head for the checkers: {head_now.get('stderr') or ''}", [])
                return
            roles = list(CHECKERS)
            if not implemented:
                rows = call("results", "show", st)
                if not rows["ok"]:
                    self.park(st, f"harness-bug: results show: {rows.get('stderr') or ''}", [])
                    return
                missing = rows.get("missing") or []
                roles = [r for r in roles if r in missing or (r == "verifier" and "ci" in missing)]

            async def check(role: str) -> dict | None:
                r = await self.run_role(role, st)
                if not r:
                    return None
                rec = call("results", "record", st, "--head", sha, "--role", role, "--output", r["outputPath"],
                           "--run", r["runId"], *(["--killed"] if r["status"] == "KILLED" else []))
                if not rec["ok"]:
                    self.park(st, f"harness-bug: results record {role}: {rec.get('stderr') or ''}", [r["runId"]])
                    return None
                return r

            checked = await _all(check(role) for role in roles)
            if any(r is None for r in checked):
                return
            outs = [r["runId"] for r in checked]
            join = call("ticket", "join", st)
            if not join["ok"]:
                self.park(st, f"harness-bug: join: {join.get('stderr') or ''}", outs)
                return
            decision, reason = join.get("decision"), join.get("reason") or ""
            self.step(f"join: {decision} ({reason})", st)
            if decision == "merge":
                self.transition("ready-for-merge", None, st)
                m = call("merge", st)
                if m["ok"]:
                    self.step(f"merged: {m.get('main_after')}", st)
                    return
                # A refusal that starts `BLOCKED ` is the merge gate blocking the merge (an undeclared
                # protected path): parked verbatim, for `resolve --accept-paths` or `resolve --ruling`.
                if isinstance(m.get("error"), str) and m["error"].startswith("BLOCKED "):
                    self.park(st, m["error"], outs)
                    return
                # The gate refused. Ask the join again: a moved integration branch is a conflict run.
                again = call("ticket", "join", st)
                if again["ok"] and again.get("decision") == "conflict":
                    self.transition("ready-for-implementer", None, st)
                    continue
                self.park(st, (again.get("reason") or "") if again["ok"] and again.get("decision") == "park"
                          else f"harness-bug: merge: {m.get('stderr') or ''}", outs)
                return
            if decision == "revise":
                tr = self.transition("ready-for-implementer", join.get("round_op"), st)
                if not tr["ok"]:
                    self.park(st, f"harness-bug: round increment refused: {tr.get('stderr') or ''}", outs)
                    return
                continue
            if decision == "conflict":
                self.transition("ready-for-implementer", None, st)
                continue
            # 'park', or 'wait' (a row is missing after both checkers reported: a harness bug, not a red round)
            self.park(st, f"harness-bug: {reason}" if decision == "wait" else reason, outs)
            return

    # ----- start, stop, end ------------------------------------------------------------------

    async def run(self, state: str, rnd: int) -> int:
        loop = asyncio.get_running_loop()
        route = asyncio.ensure_future(self.build(state) if self.phase == "build" else self.intake(state, rnd))
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._on_signal, sig, route)
        try:
            result, code = {**await route, "ok": True}, 0
        except asyncio.CancelledError:
            if self.stopped is None:
                raise
            await self.stop()
            result, code = {"ok": False, "ticket": self.ticket, "stopped": self.stopped.name}, 128 + self.stopped
        except Exception as e:  # noqa: BLE001 - a driver bug: end the role processes, park nothing
            await self.stop()
            result, code = {"ok": False, "ticket": self.ticket, "error": f"{type(e).__name__}: {e}"}, 1
        self.end(result)
        return code

    def _on_signal(self, sig: signal.Signals, route: asyncio.Future) -> None:
        if self.stopped is None:
            self.stopped = sig
            route.cancel()

    async def stop(self) -> None:
        """End every role process this driver started (SIGTERM, then SIGKILL after KILL_AFTER_S)
        and record each of its runs in flight KILLED. Parks nothing: a stop is not a failure."""
        procs = [p for p in self.procs.values() if p.returncode is None]
        for p in procs:
            with contextlib.suppress(ProcessLookupError):
                p.terminate()
        if procs:
            waits = [asyncio.ensure_future(p.wait()) for p in procs]
            await asyncio.wait(waits, timeout=KILL_AFTER_S)
            for p in procs:
                if p.returncode is None:
                    with contextlib.suppress(ProcessLookupError):
                        p.kill()
            await asyncio.gather(*waits)
        for rid, r in list(self.running.items()):
            call("run", "finish", rid, "--status-override", "KILLED")
            if r["role"] in CHECKERS:
                call("run", "cleanup", rid)
            self.running.pop(rid)
            self.procs.pop(rid, None)
            self.step(f"{r['role']} {rid}: KILLED", r["ticket"])

    def end(self, result: dict) -> None:
        how = (f"stopped by {result['stopped']}" if "stopped" in result
               else f"failed: {result['error']}" if "error" in result else result.get("state"))
        self.step(f"end: {how}")
        self.write_status(ended=result)
        print(json.dumps(result, ensure_ascii=False), flush=True)


async def _all(aws) -> list:
    """asyncio.gather, as the scripts' parallel(): every awaitable finishes before it returns. If
    one raises, the rest are cancelled and waited for before the error goes on, so no role run is
    still being routed while the stop sequence runs."""
    tasks = [asyncio.ensure_future(a) for a in aws]
    try:
        return await asyncio.gather(*tasks)
    except BaseException:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise


def _spec_round(tr: dict, rnd: int) -> int:
    spec = (tr.get("round") or {}).get("spec")
    return spec if isinstance(spec, int) and not isinstance(spec, bool) else rnd


def drive(a, root: Path, cfg: dict) -> None:
    """`factory drive`, after main() has run the instance refusal, the fence and the harness lock.
    From here on the driver's own store calls carry the dispatcher marker; its role processes never
    inherit it."""
    os.environ["FACTORY_DISPATCH"] = "1"
    d = Driver(a, root, cfg)
    conf = call("config")
    if not conf["ok"]:
        _fail({"ticket": d.ticket, "error": f"no store: factory config failed: {conf.get('stderr') or ''}"})
    d.models, d.max_spec = conf["models"], conf["max_rounds"]["spec"]
    show = call("ticket", "show", d.ticket, "--json")
    if not show["ok"]:
        _fail({"ticket": d.ticket, "error": f"no such ticket: {show.get('stderr') or ''}"})
    state = show["state"]
    d.phase = d.phase or ("intake" if state in INTAKE_STATES else "build" if state in BUILD_STATES else None)
    d.title = show["title"]
    d.status = {"ticket": d.ticket, "title": d.title, "phase": d.phase, "pid": os.getpid(), "started": store.now(),
                "updated": None, "running": [], "last": None, "ended": None}
    d.write_status()
    code = asyncio.run(d.run(state, (show.get("round") or {}).get("spec") or 0))
    if code:
        raise SystemExit(code)


def _fail(result: dict) -> None:
    print(json.dumps({"ok": False, **result}, ensure_ascii=False), flush=True)
    raise SystemExit(1)
