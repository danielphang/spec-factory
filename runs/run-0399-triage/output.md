Type: feature (harness)

Title: `factory drive TICKET`: a Python driver runs intake and build, with each role as a headless `claude -p` process; the clerk agent and the Workflow scripts retire

Summary:
Today every store command a workflow issues goes through a clerk agent, because a Workflow-tool script (`factory/workflows/intake.js`, `build.js`) cannot run a command itself. The requester measured the cost on 2026-10-05 across 97 workflow runs: 2,236 clerk agents, 4,476 calls and 143M of 866M workflow context tokens (17%). The clerk is also most of the wall-clock time between steps and the source of its own failures. The operator chose an external driver in place of batching inside the Workflow tool. The requester wants a `factory drive TICKET [--phase intake|build]` command. It runs today's routing in Python and calls the store functions directly. Each role runs as a headless `claude -p` process from its run's directory, with that role's prompt file, model, effort, tool allowlist and a non-interactive permission mode. The JSON reply (`result`, `session_id`, `total_cost_usd`) goes into the run's `meta.yaml`. The two checkers run as two concurrent processes, and independent sub-tickets run concurrently up to a configured limit. The driver prints one line per step and writes a status file in the store. The Workflow scripts keep working until the driver has taken one real ticket end to end through intake and one through build; after that they retire and the README is updated. Routing, round limits, refusals and the live-store fence (#45) must not change.

Evidence:
- Request body, issue https://github.com/danielphang/spec-factory/issues/65: "the clerk was 2,236 agents and 4,476 calls, and 143M of 866M workflow context tokens (17%)", measured 2026-10-05. I could not re-derive these figures; they are the requester's.
- A further clerk failure, from a comment dated 2026-10-09 on T-0027.2: the reviewer's `run finish` succeeded (log `run.finished APPROVE`). The clerk then returned the JSON pretty-printed across several lines, the workflow read that as a failure, and it parked the piece as "harness-bug: run finish reviewer:" with empty stderr.
- Scope added by comments. They take precedence over the body where the two disagree:
  - 2026-10-07: #24 part A (an agent definition per role, with file tools withheld from the checkers) moved here. The driver passes each role its prompt with `--system-prompt-file` or `--append-system-prompt-file` and sets its tools with `--tools`/`--allowedTools` and a permission mode. That replaces the body's `--agent factory-<role>` and its "after #24 A+C" sequencing. Part C is merged (T-0030.3).
  - 2026-10-09 backlog review: absorbs #22 (per-role effort becomes `--effort`; T-0030.2 withdrawn). Absorbs #28 (the chat relay goes away with the Workflow scripts). Absorbs #47 (the per-step title moves to the driver's status output; T-0026 withdrawn).
- Checked on this checkout:
  - `factory/workflows/intake.js` and `build.js` exist and contain 18 and 35 "clerk" lines.
  - `agents/factory-clerk.md` exists.
  - The README has "What depends on Claude Code" (line 97) and "Starting a run" (line 690).
  - Routing is enforced in `factory/cli.py` (line 153: `if to not in cfg["routing"].get(frm, [])`).
- `claude --help`, run under a throwaway HOME (output in `scratch/help.txt`), lists `--agent`, `--tools`, `--allowedTools`, `--effort`, `--output-format`, `--resume`, `--bare` and `--system-prompt[-file]`/`--append-system-prompt[-file]`. `--permission-mode` accepts `dontAsk`. I did not check the billing claim about `--bare`.
- Duplicate search: T-0040 is this ticket. T-0030 (#24) is closed, with parts A and B and per-role effort moved here. T-0026 (#47) and T-0030.2 (#22) are closed as withdrawn into #65. No open ticket covers the driver.

Capabilities: build-dispatch, live-store-guard, run-environment, role-inputs, harness-docs

Assumptions:
- (inference) The 2026-10-07 comment replaces the body's `--agent factory-<role>`: the driver delivers prompts and tool fences through CLI flags, and it does not wait on #24 A. Whether to use `--system-prompt-file` or `--append-system-prompt-file` is for the spec to decide by measurement (body item D, with a baseline of 44k start-up tokens per call).
- (inference) The persistent per-role conversation (`--resume`) is an option to measure after the driver exists, not a requirement here. If the spec takes it up, the 2026-10-07 caution applies: only the writer and implementer keep a conversation; checkers start fresh every round.
- (inference) "No clerk run appears" means that `factory drive` never dispatches the clerk role. Whether `agents/factory-clerk.md` and the clerk prompt are deleted when the scripts retire (part F) is left to the spec.
- (inference) The harness suite runs under a fresh HOME with no Claude login, so the parity acceptance (the same fixture through `factory drive` and through the Workflow script reaches the same states and records) needs a stubbed role runner. The real end-to-end runs and the per-ticket token totals "beside the 2026-10-05 figures" are operator steps on real tickets.
- (inference) The spec decides the open points the request names: whether concurrent `claude -p` runs conflict (test it), how a running driver is stopped and resumed (tied to #53's recorded stop), and whether the driver runs as its own process or in the background of a runner session.
- Suggested priority (a suggestion only; priority is a human call): high. The operator chose this approach, and #59, #66, #70 and #76's hook are listed as following it.

Reason: ACCEPT. The intent is clear and the operator has already made the design call (external driver, not in-Workflow batching), so no product decision is left for triage. The remaining open points are ones the requester explicitly hands to the spec.

Out-of-scope observations:
- T-0030.1 was refused twice by the session's auto-mode permission check ("Code from External") because its fixtures generated and ran Claude Code agent files. Fixtures that launch `claude -p` may meet the same refusal. The spec's Risk section should plan for a stub runner in the suite.
- The change touches protected `harness` paths (`factory/**`, `bin/factory`, `agents/**`). The approved spec's Risk section must declare them, or the merge gate will refuse.
- `dev/issues.md` line 81 links #76's PreToolUse hook to #65 ("hook with #65"), but the request and its comments do not mention it, so I left it out of scope.

STATUS: ACCEPT
CONFIDENCE: medium. The intent and the operator's choice are clear, but the request has grown through four absorbed issues and one superseded mechanism, so the spec must state which version it builds.
ESCALATIONS: none
