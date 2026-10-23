## Problem

This ticket fixes four small defects in the harness. The harness is the code that runs the factory's AI roles and keeps their records. None of the defects changes where a ticket goes next. Each one leaves a record that is wrong, or a command that fails or silently does nothing, and a person has to notice it and work around it.

1. **A false escalation in the run record.** Every role ends its output with a three-line trailer: STATUS (its verdict), CONFIDENCE and ESCALATIONS (the items it wants a human to see). The harness reads that trailer when the run finishes. If the ESCALATIONS line says `none` and further lines follow it, the harness treats the whole block as a real list of items. The operator chose that rule on 2026-10-01 (the code calls it rule (b)). Claude Code sometimes appends its own attribution line, `🤖 Generated with [Claude Code](…)`, after the trailer. When it does, the harness records two escalations the role never raised, `none` and the footer, and logs a false "escalation queued" event. This has happened once on each of the two repositories the factory runs on.
2. **A scenario that fails under macOS's `/bin/sh`.** Current truth is the store's record of each capability's accepted behaviour. Each requirement in it carries scenarios, which are shell commands with the output they must print. One scenario puts a `case` statement inside `$( )` without a leading parenthesis on its patterns. The bash 3.2 that macOS ships as `/bin/sh` cannot parse that, so the scenario fails whatever the code does. A check that runs current truth under that shell would report a regression the code did not cause. Such a check is queued as the next ticket (#120).
3. **`factory init` fails on an agent copy it cannot read.** `factory init` sets a repository up for the factory. Since the fix for #108, it also compares each copy of an agent definition in the repository (`.claude/agents/factory-*.md`) with the harness's template. It lists a copy that differs under `stale_agents` in its JSON output, and leaves it alone. If a copy exists but cannot be read, init crashes with exit 1 instead. Before #108 it exited 0.
4. **`--accept-harness` is silently ignored by three commands.** Each repository records which harness revision it has agreed to run, in a lock file, and the harness refuses to touch that repository's store under any other revision. The operator agrees to a new revision by adding `--accept-harness <sha>` to a command. Three commands, `init`, `paths` and `stats`, never check the lock, so they drop the flag without a word. On 2026-10-19 the operator ran `--accept-harness … paths` on the Nanobot target. The command looked as if it had worked, and the lock was left unchanged.

## Evidence

All reproductions ran on `main` at `788a201`, from `~/dev/spec-factory`, under a throwaway HOME and a throwaway store or target. The scratch scripts are in this run's `scratch/` directory.

**#88, false escalations.**
- The record shows the defect on both repositories, and nowhere else. Across both stores (554 runs here, 436 on Nanobot), the only `meta.yaml` files that mention `Generated with [Claude` or `Co-Authored-By` are those of `.factory/store/runs/run-0538-implementer` and `~/dev/nanobot-upstream/.factory/store/runs/run-0418-implementer`. Each `output.md` ends with `ESCALATIONS: none`, a blank line, then `🤖 Generated with [Claude Code](https://claude.com/claude-code)` (line 151 and line 83). `.factory/store/log/2026-10.jsonl:2861` is the false `escalation.queued` event for run-0538.
- Reproduced end to end: a throwaway store, one triage run, an output ending in the same three lines, then `run finish`. It printed `finish=["none", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]` and `queued=1 meta=1`.
- With a real item above the footer, `status parse` returned `["none", "the auth path needs review", "🤖 Generated with [Claude Code](https://claude.ai/code)"]`.
- I looked up the Claude Code setting. The settings reference (https://code.claude.com/docs/en/settings-reference) lists `attribution.pr`, "Change or hide the attribution line in pull request descriptions", and `includeCoAuthoredBy` as deprecated. I did not verify that setting it changes what a `claude -p` reply contains.

**#113, the `/bin/sh` scenario.** The scenario "Each launch copy is a one-line change to its script, …" is at `.factory/store/openspec/specs/build-dispatch/spec.md:694`. I extracted its WHEN line and ran it from `~/dev/spec-factory`:
- `/bin/sh` (GNU bash 3.2.57) printed `command substitution: line 1: syntax error near unexpected token 'newline'`, then `intake: where= echo own-dir;; *) echo none;; esac) changed=2 …`.
- The same command with `($T/tmp/factory-launch-*/$s.js)` and `(*)` printed exactly the scenario's THEN under `/bin/sh`, zsh and Homebrew bash 5.

**#114, the unreadable agent copy.** I made a target with `init`, ran `chmod 000 .claude/agents/factory-planner.md`, then ran `init` again. It exited 1. Stdout was `{"ok": false, "error": "PermissionError: [Errno 13] Permission denied: '…/factory-planner.md'"}` and stderr was `factory: PermissionError: …`. So JSON is printed, contrary to run-0532's "no JSON output", which triage flagged. The cause is `factory/setup.py:187`, which calls `read_bytes()` with no error handling.

**#115, `--accept-harness` ignored.** In a target made by `init`, `--accept-harness 0123…4567` with each of `init`, `paths` and `stats` exited 0 and left `harness.lock` unchanged. On a fresh repository, `--accept-harness … init --repo-name demo` exited 0 and created 16 files.

**Current truth and decisions read:**
- `openspec/specs/build-dispatch/spec.md`, `openspec/specs/store-setup/spec.md`, `openspec/specs/live-store-guard/spec.md` and `openspec/specs/harness-docs/spec.md` (the README and design scenarios at its lines 152 and 332).
- The decision log entries 2026-10-12 T-0043 (stats ignores `--accept-harness`) and 2026-10-14 T-0052 (the `stale_agents` shape; init never overwrites a copy).

## Root cause

- **#88.** `factory/status.py` `parse()`, lines 37-49. Every non-blank line below the ESCALATIONS line goes into `tail`. A non-empty `tail` makes `[esc_head, *tail]` the item list, as the 2026-10-01 rule (b) says. Nothing tells the attribution footer apart from an item line. `run finish` uses this parser for both the drive and the Workflow-script path (`factory/workflows/intake.js:143` logs `fin.escalations` from `run finish`).
- **#113.** The scenario text in current truth. Bash before 4.0 ends a command substitution at the first `)`, and an unparenthesised case pattern has one. This is not a code defect.
- **#114.** `factory/setup.py:187`: `(dest / src.name).read_bytes()` raises `PermissionError`. The generic handler in `factory/cli.py` `main()` turns that into exit 1.
- **#115.** `factory/cli.py:851-855`: `main()` runs `init`, `paths` and `stats` and returns before `instance.guard(…, a.accept_harness)` at line 863, so nothing reads the flag for those three. The comment at line 852 says "ignore --accept-harness".

## Out of scope

- Setting `attribution.pr` (or any `--settings`) on the role processes `factory drive` starts. See Decisions.
- Any other footer or trailer form, such as `Co-Authored-By:` lines. None appears in either store's escalation records.
- A check that no current-truth scenario has an unparenthesised `case` inside `$( )`, which #113 suggests as optional.
- Every other scenario in current truth, and any code change for #113.
- What the harness lock and the live-store fence do for every command other than `init`, `paths` and `stats`. The live-store fence is the guard that keeps writes out of a store while a role run is in flight.
- The shape of `stale_agents` (a list of paths), and creating missing copies. Init never overwrites, repairs or changes the permissions of an existing copy.
- Rule (b) for real item lines below a `none` head.
- Past run records. The false items in run-0418 and run-0538 stay as they are.

## Open questions

none

## Decisions

- #88 is fixed in the parser. Before rule (b) is applied, the trailer parser, `parse()` in `factory/status.py`, drops each line below the ESCALATIONS line that, after its list marker is stripped, is exactly `🤖 Generated with [Claude Code](<link>)`, with any link and nothing else on the line. Rule (b) applies unchanged to the lines that are left.
- Rejected for #88: passing `attribution.pr` through `--settings` to the role processes that `factory drive` (the command that runs each role as a headless `claude -p` process) starts. The key exists, but its effect on a `claude -p` reply is unverified. The footer appeared in 2 of 990 runs, so no acceptance check could show the setting works. It would also not cover the Workflow-script path (the older way of running the roles, beside the drive), which goes through the same parser.
- Rejected for #88: ignoring everything after a blank line below the trailer. That would break rule (b) for real items separated by blank lines.
- Standing decision for later tickets: the trailer parser drops only the exact Claude Code attribution footer. Any other text below the ESCALATIONS line stays an item under rule (b). Recognising a new footer form needs its own ticket.
- #113 changes only the two patterns of that one `case`, to `($T/tmp/factory-launch-*/$s.js)` and `(*)`. The rest of the requirement is restated word for word. This is a spec delta, so current truth changes when the ticket is archived.
- #114: an existing copy whose read raises any `OSError` is listed under `stale_agents` by its path, as a differing copy is. Stderr gets one line that names the copy and says it `could not be read`, with the error. Init exits 0 and leaves the copy as it is. The JSON shape does not change, which keeps T-0052's decision that `stale_agents` is a list of paths.
- #115: `factory --accept-harness <sha>` with `init`, `paths` or `stats` is refused with exit 2 before anything else runs, on any store, whether or not a run is in flight, and writes nothing. The message names the command and gives `factory --accept-harness <sha> config`, with the sha the operator passed, as the command to run instead. `config` reads nothing it could break and reaches the lock.
- That overturns the 2026-10-12 T-0043 decision that `stats` ignores `--accept-harness`, and the same behaviour in `init` and `paths`. Standing decision for later tickets: a command that skips the harness lock refuses `--accept-harness` and never ignores it.
- README's "Upgrading the runtime" step 2 names `factory --accept-harness <sha> config` as the command to run. It no longer says "any store command", which would now include three that refuse the flag.

## Risk

Blast radius:
- The parser change touches every `run finish`, for every role, on both instances, once the runtime moves to the merge. The match is one exact line form, so the only result that changes is a trailer followed by that footer.
- The `init` change affects only a copy that cannot be read, which today crashes.
- The `--accept-harness` refusal turns a silent no-op into exit 2 for three commands. A script that passes the flag to them would now stop. None does in the harness, in either workflow script or in the tests, apart from the one test listed under "Tests to change".
- The #113 edit reaches current truth only at archive. Until then current truth keeps the scenario that breaks under `/bin/sh`.

Protected paths: `factory/status.py`, `factory/setup.py`, `factory/cli.py`

