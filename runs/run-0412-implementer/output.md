Sub-ticket: T-0040.3 (T-0040.C / Documents), parent T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md`)
Branch: `factory/T-0040.3`, base `18fbe88ba88be7f2ae2dbebca09586bd25caf50d`
Commit: 0e99ddad7eb10387369fac62286f8520fd6a1a67

## What changed

This change brings the documents up to date with `factory drive`. Parts A and B of this ticket built `factory drive`, a command that does the job of the Workflow-tool scripts. It decides which AI agent role runs next, and it starts each role as its own `claude -p` process. Until this commit the documents did not mention it, and the README still listed per-role effort as not built. Only documents change here. Nothing under `factory/`, `bin/`, `tests/`, `agents/`, `docs/prompts/` or `.factory/` is touched.

Part C, item 1, `README.md`:
- **"Starting a run"** has a new how-to subsection, "Driving a ticket from a shell with `factory drive`". It covers what to run and how the phase follows the stored state. It covers `FACTORY_DISPATCH=1` when another run is in flight, `--parallel`, what the driver prints, the status file `drive/<ticket>.yaml`, and stopping and resuming. It ends with `reply.json`, the `effort:` map and `--prompt-mode`. It also says the Workflow tool remains the tested route until the driver has run a real ticket.
- **"What depends on Claude Code"** gains a row for the driver's role processes: `claude -p`, `--output-format json`, `--permission-mode auto`, the prompt file, the model, an optional `--effort`, `--tools` and `--allowedTools`. The intro count went from "Four pieces" to "Five pieces" because that table now has five "yes" rows.
- **Built** gains two bullets. The driver bullet ends "It is tested, and has not yet run a real ticket." The second bullet, "Per-role effort, for driver runs only", replaces the removed Not built bullet "Per-role effort settings". The Built bullet on the live-store fence now says that the driver also marks its own commands, and that its role processes are never marked.
- **The store's file table** gains a `drive/<ticket>.yaml` row. Its columns say: on no branch because git ignores it, written by `factory drive`, never committed, rewritten at each step and kept until the next drive of that ticket. The "Store records" row now reads "through the workflows' clerk or `factory drive`, and the operator's commands".
- **The status date** went from 2026-10-09 to 2026-10-10.

Part C, item 2, `docs/design.md`. No prompt block changed: the three edits are at lines 44, 64 and 874, and all three are outside every ```` ```text ```` block.
- In the harness table, piece 2 (the event dispatcher) now names `factory drive` as the external dispatcher. It has no clerk, so v0 limit (1) does not apply to it. Limits (2) and (3) still hold. "Clerk" is the agent the scripts start only to run one store command.
- The fence paragraph says the driver goes through the fence and the lock when it starts, then marks its own store calls. It also says the driver removes the marker from every role process's environment.
- "Running on another agent host" names `factory drive` as the Claude Code form of the adapter that section describes.

Part C, item 3, `dev/build-harness.spec.md`:
- R3 names the driver beside the Workflow scripts.
- R6 keeps "Never `bypassPermissions` (nor `dontAsk`)". It adds that under the driver, roles run under `auto` with the `--tools` and `--allowedTools` lists and the four `Edit` rule scopes, and that Bash is not restricted.
- Part H gains one paragraph pointing to `factory drive` for the same routing.
- I.4 says that under the driver, the tool restriction is `--tools` and `--allowedTools`.

Part C, item 4, `docs/changelog.md`: entry 67, "After issue #65 (2026-10-05), where …", placed before "Declined:". It cites the clerk figures and the T-0027.2 failure, and lists #22, #28, #47 and #24 part A as absorbed.

## Acceptance results

The fixtures ran under the running-code wrapper with `TMPDIR` set to this run's scratch directory (`…/run-0412-implementer/scratch/tmp`). The GIVEN blocks were taken verbatim from current truth (`human-resolution`, `live-store-guard`) and from the parent spec (`build-dispatch`). The WHEN commands were taken verbatim from the sub-ticket's input. Full log: `scratch/regress.log`.

- **NEW, "The documents describe the driver."**
  - Before (on base `18fbe88`): `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean`. This matches the spec's "today" line.
  - After (on `0e99dda`): `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`. That is exactly the expected line. It means every required section names the driver, no "none has an effort level" text remains, the build spec still forbids `dontAsk`, and there are no whitespace errors.
- **REGRESSION, the ten driver and script scenarios of `specs/build-dispatch/spec.md`, run after the change.** All ten printed exactly their THEN lines:
  - intake parity: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`
  - build parity: `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`
  - role argv: `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`
  - reply record: `triage=ok spec_writer=ok critic=ok`
  - concurrency: `parallel=1: calls=4 max=2 parked parked`, `parallel=default: calls=4 max=4 parked parked`
  - intake step lines: `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`
  - build step lines: `untagged=0 sub=yes last=1`
  - stop and resume: `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, `resumed: exit=0 closed calls=2`
  - marker and effort: `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`
  - Workflow scripts: `T-0001.1 merged T-0001 parked`, `T-0001 awaiting-spec-gate`

  The sub-ticket says "nine" scenarios, but the ten it names are the ten WHENs in the spec, so all ten ran.
- **Gate `git diff --check main...HEAD`**, wrapped exactly as given: no output, exit 0. The change adds no whitespace errors.
- **Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`**, wrapped exactly as given: `520 passed in 348.70s`, exit 0. This also covers the sub-ticket's intermediate check.

## Tests added/changed

None. The sub-ticket lists no tests to change and no interim tests. The change is documents only.

## Known gaps and uncertainties

- **README edits beyond the sub-ticket's list.** I made four small README edits that the sub-ticket does not list. Without them, sentences this change made stale would have stayed wrong, and "Maintaining this page" counts a stale sentence as a reviewer finding. A reviewer may judge any of them out of scope:
  1. The directory tree in "What the factory keeps in a target" gains a `drive/<T>.yaml` line, and the `runs/` line now mentions `reply.json`.
  2. The Built "Live-store fence" bullet now names the driver as marking its own commands.
  3. The README's "Running on another agent host" gains one sentence pointing to `factory drive`. That section mirrors the design doc, and the design doc's matching section changed here.
  4. "Related work and history" no longer lists per-role effort (#22) as open work, and gains one sentence on #65 and the issues it absorbs.
- **Re-derived figures.** In "Related work and history", the store counts went from "32 tickets and 26 sub-tickets" to 40 tickets and 47 sub-tickets. I counted `^T-[0-9]*\.yaml$` and `^T-[0-9]*\.[0-9]*\.yaml$` in `/Users/dphang/dev/spec-factory/.factory/store/tickets`. The runtime commit (`639fcb5`, from `git -C ~/dev/spec-factory-harness rev-parse --short HEAD`) and the harness revision (`da50576…`, from `.factory/harness.lock`) still match what the page quotes, so they are unchanged. The ticket counts will go stale as soon as more tickets are filed.
- **"Ground truth only" rule.** "Maintaining this page" says a thing appears above "Where this can go" only after it has run on a real ticket. The approved spec puts the driver under "Starting a run" and Built anyway. I followed the spec: both places say plainly that the driver is tested and has not yet run a real ticket, as several existing Built bullets already do.
- **Changelog figures are the requester's, not re-derived.** The figures are 2,236 clerk agents, 4,476 calls and 143M of 866M tokens. The parent spec's Evidence also marks them "Not re-derived here".
- **Claims about the driver.** I checked the driver behaviour these documents describe against `factory/drive.py` and the `drive` subparser in `factory/cli.py`. That covers the argv, the `Edit` rule scopes, the dropped marker, the states for each phase, the stop sequence, the status file keys and the absence of any time limit. I did not run the driver with a real `claude`. The Operator steps cover that.

## Out-of-scope observations

- **The sub-ticket says "nine" scenarios, but the spec has ten.** It names ten, and the parent spec holds ten WHENs. This is a counting slip in the plan, and it changes nothing.
- **The README's "Running on another agent host" table** still shows only the Workflow tool in the "Claude Code (today)" column. So does the design doc's. The new sentence below each covers this. Changing the table cells was more than C.2 asked for.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command, all ten regression scenarios and both gates were run on this head and printed exactly what the spec expects; the remaining risk is reviewer judgement on the four unlisted README edits
ESCALATIONS: none
