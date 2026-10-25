# Review of T-0056.1: record every run's tokens with `run finish --transcripts`

Commit: 6991572ee604bbf88e7b71af43e9233279029fdb (base 3e4705ae6af33c83e680a479beef42d58721511b)

## How I checked

I read the whole diff (7 files, 241 insertions, 24 deletions) against the sub-ticket's parts A1 to A4, D, E1 and E3 and the parent spec's Decisions. I did not run the suite or the gate commands; the verifier runs them on this head. Narrow checks I ran in the worktree, with their output:

- `git diff --stat 3e4705a HEAD`: the only test file touched is the new `tests/factory/test_transcript_record.py`. No existing test, CI config or prompt changed.
- `wc -l README.md factory/cli.py`: `1189` and `885`. README is 5 lines over the base's 1,184, inside the 30-line allowance and the raised 1,225 cap. `cli.py` grew 5 of its 19 allowed lines, as the PR description states.
- `grep -n 'match_transcripts(\|transcript_usage(' factory/stats.py tests/factory/*.py`: every existing caller passes positional arguments only, so the new optional `modified_since` parameter and the `_usages` split change nothing for them.
- `grep -n -A1 '^def now' factory/store.py`: `started` is written as an aware UTC timestamp with microseconds dropped, so the modification-time floor in `factory/cost.py:181` compares epoch seconds correctly and can only be earlier than the true start, never later.

## Correctness against the spec

- **A1** `factory/cost.py:205-216`: `transcript_record` calls `match_transcripts` for the one store with the floor, takes the run's entry, and sums the four usage fields over `_usages`, which keeps each message id once with its last record. At finish time the on-disk `meta.yaml` has no `finished` yet, so `_window` (`cost.py:153-163`) leaves the upper bound open, which is the "no upper time bound because the run is finishing" the spec asks for. The record shape matches the Decision exactly. `cost.py` still imports nothing from `factory`.
- **A2** `factory/cli.py:342-344`: the transcript is consulted only when a directory was given and the recorded `claude` value has no `usage` mapping. A reply with usage keeps its shape; an unusable reply with no transcript stays `claude: null` because `_claude_record` already set `None`; no reply and no transcript leaves the key absent, as before. The parser flag at `cli.py:705-706` is `append` with default `[]`.
- **A3** `intake.js:33`, `build.js:29`: the constant is a single-quoted literal, so JavaScript passes `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` through for the clerk's shell. Both `run finish` commands in each script carry it. The new test asserts the literal text at the end of each printed command.
- **A4** `factory/drive.py:85-89`: `_transcripts()` treats an empty `CLAUDE_CONFIG_DIR` as unset, as the spec says. All three `run finish` calls pass it (`drive.py:235`, `242`, `584`).
- **E1, E3**: the README row and paragraph match the spec's text word for word, and the row sits after the `Catch and cost per role` row. The status-header date bump follows README's "Update with the change" rule.
- **Tests (D, A's share)**: the new file covers the record and its two decoys, the mtime floor, a reply winning, an unusable reply with and without a transcript, and build.js under node on both `run finish` paths. The build.js tests check the literal argument and that each implementer run records its own agent's transcript, so a `${…}` interpolation mistake, the risk the spec names, would fail them.

## Findings

- [SHOULD-FIX] PR description: What changed: "clerk" (the sub-agent that runs one store command for a Workflow script) and "the Workflow scripts" (the original way of running the factory inside a Claude Code session) are used without a gloss at first use → the operator at the gate, held to docs/writing.md rule 2, has to know the factory's names to follow A3. One clause each fixes it.
- [NIT] factory/workflows/intake.js:32, factory/workflows/build.js:28: one comment line above `TRANSCRIPTS` in each script, beyond the sub-ticket's "Nothing else in either script changes" → no behavioural effect; the implementer disclosed it. Acceptable as is or dropped, either way.
- [NIT] factory/drive.py:85: A4 adds a path outside the repository (`~/.claude/projects`) with no autouse guard, which docs/coding.md rule 6 asks for → a suite run outside the briefing's wrapper, with `CLAUDE_CONFIG_DIR` pointing at the operator's real directory, would scan it read-only during the drive tests. The spec's Decision chose explicit passing plus a throwaway HOME as the guard, the access is read-only, and the guard would live in `tests/factory/conftest.py`, an existing test file this sub-ticket may not edit. Disclosed in Known gaps. Not actionable here; worth a line in a later ticket.

Over-building pass (coding standard rule 4): Lean already. `_usages` is the reuse the spec asked for; `_transcripts()` has three callers; no helper duplicates one the repo has.

## Silent behaviour changes

Every `run finish` given `--transcripts` now reads the store's event log once (for `store.migrated`) and stats every `*.jsonl` under the transcript directory, opening only those modified since the run started. The spec accepts this and names its cost as unmeasured; the PR description says so under Known gaps. Nothing else a caller or user would notice changed: `stats` output without `--scorecard` is untouched, and the `claude:` record from a reply keeps its exact shape.

## Security and data safety

Read-only access to the transcript directory, which the scripts and driver pass explicitly; `run finish` never defaults it, so a throwaway HOME reads nothing real. The transcript path is stored in `meta.yaml`, which the spec's Risk section accepts. No secrets, no destructive operations.

## Protected paths

`factory/cost.py`, `factory/cli.py`, `factory/drive.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`: all under `factory/**`, which the sub-ticket and the spec's Risk section declare. Listed under ESCALATIONS for the record.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high, the diff implements A1 to A4, E1 and E3 as the spec words them, no existing test changed, and the two risks the spec names (template-string interpolation and the throwaway-HOME rule) are covered by the new node-driven tests and by explicit passing of the directory
ESCALATIONS: protected path `factory/**` touched (cost.py, cli.py, drive.py, workflows/intake.js, workflows/build.js); declared by the sub-ticket and the approved spec's Risk section, so the merge gate may proceed without further approval
