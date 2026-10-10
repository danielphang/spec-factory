"""`factory drive TICKET`: the dispatcher as an ordinary process, with no clerk (T-0040).

It does the Workflow scripts' job without the Workflow tool. Every store call goes through the
CLI's own entry point, `factory.cli.main`, in this process, one at a time, so every guard, the
fence and the harness lock run as they do for `bin/factory`. Every role runs as one headless
`claude -p` process from its run directory, with its role's prompt, model, effort and tool limits;
its reply is kept as `runs/<id>/reply.json` and its cost recorded by `run finish --reply`.

The routing is a port of factory/workflows/intake.js from `// --- start`, branch for branch: the
same commands, transitions, round operations and park reasons, so a ticket driven here leaves the
same records the script leaves. Like the script, the driver stops at the spec gate.

One stdout line per step, `<ticket id> "<title>": <step>`, then the result as one JSON object. The
store's `drive/<ticket>.yaml` is a live view of this process (git ignores it). SIGINT or SIGTERM
ends the role processes, records their runs KILLED and parks nothing: running `factory drive`
again resumes from the stored state.

Part A of T-0040 builds the intake phase only: the build phase (build.js) is refused.
"""
from __future__ import annotations

import asyncio
import contextlib
import io
import json
import os
import signal
import tempfile
from pathlib import Path

from factory import cli, store
from factory.store import Refused

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
        self.prompt_mode = a.prompt_mode
        self.root = root
        self.effort = cfg.get("effort") or {}
        self.models: dict = {}
        self.max_spec = 2
        self.title = ""
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
        line = f'{ticket or self.ticket} "{self.title}": {text}'
        print(line, flush=True)
        self.write_status(last=line)

    # ----- store calls the routing makes ------------------------------------------------

    def park(self, ticket: str, reason: str, outputs: list[str]) -> None:
        argv = ["ticket", "park", ticket, "--reason=" + reason.replace('"', "'")]
        if outputs:
            argv += ["--outputs", ",".join(outputs)]
        call(*argv)
        self.step(f"parked: {reason}", ticket)

    def transition(self, to: str, round_op: str | None = None) -> dict:
        argv = ["ticket", "transition", self.ticket, "--to", to, "--by", "workflow"]
        res = call(*argv, *(["--round", round_op] if round_op else []))
        self.step(f"-> {to}" if res["ok"] else f"-> {to} refused: {res.get('stderr', '').strip()}")
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
        return {"runId": rid, "status": fin["status"], "escalations": esc}

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

    # ----- start, stop, end ------------------------------------------------------------------

    async def run(self, state: str, rnd: int) -> int:
        loop = asyncio.get_running_loop()
        route = asyncio.ensure_future(self.intake(state, rnd))
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
    phase = d.phase or ("intake" if state in INTAKE_STATES else "build" if state in BUILD_STATES else None)
    if phase == "build":
        # factory: interim until T-0040 part B ports build.js; refused before anything is written.
        raise Refused(f"{d.ticket} is {state}: the build phase of factory drive is not built yet; "
                      "run the build Workflow script")
    d.title = show["title"]
    d.status = {"ticket": d.ticket, "title": d.title, "phase": phase, "pid": os.getpid(), "started": store.now(),
                "updated": None, "running": [], "last": None, "ended": None}
    d.write_status()
    code = asyncio.run(d.run(state, (show.get("round") or {}).get("spec") or 0))
    if code:
        raise SystemExit(code)


def _fail(result: dict) -> None:
    print(json.dumps({"ok": False, **result}, ensure_ascii=False), flush=True)
    raise SystemExit(1)
