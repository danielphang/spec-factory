Commit: ba3fea8154f74ccd5007fd25d18f8215e0b7f000 (one commit on base 2f7f75f3961d2bd20b2fb106bd587ff94dd7621f)

## How I checked

Read the whole diff against the sub-ticket (every lettered part of T-0033 v2's Proposed change) and the pinned spec. Narrow confirmations run from the worktree, each in the HOME wrapper:
- `git diff --stat 2f7f75f...HEAD`: 12 files, the one new test file and no existing test. Only `tests/factory/test_merge_protected_paths.py` is new; no file under `tests/` is modified or deleted.
- `grep -rn changed_files factory tests bin`: the only callers of `gitops.changed_files` are the two new ones in `factory/cli.py` (lines 693 and 698). The signature change breaks nothing else.
- `sed`/`cmp` of the §6 and §2 design blocks against `docs/prompts/06-code-reviewer.md` and `docs/prompts/02-spec-writer.md`: both print `SAME`, so each `docs/prompts/` file is a byte copy of its block.
- `git diff --check 2f7f75f...HEAD`: exit 0, no whitespace errors.
- `grep -n 'ESCALATE from' factory/cli.py`: the join parks a reviewer ESCALATE with the reason `ESCALATE from reviewer` (line 796), the prefix the new `--ruling` route matches (line 942).
- `specstore.lines_outside_fences` (`factory/specstore.py:77`) yields `(line, in_fence)` and marks the fence lines themselves `True`, so `declared_paths` skips a fence line and every line inside it, as the spec asks.
- `store.new_ticket` (`factory/store.py:201`) always writes `spec: {version: 0, approved_version: None}`, so `undeclared_protected`'s `["spec"]["approved_version"]` read cannot fail on a ticket with no approved spec.
- `build.js` `clerk()` (line 41) returns the parsed JSON of the command's last stdout line with `ok` forced false on a non-zero exit, so `m.error` is the gate's `BLOCKED from merge gate: ...` string and the new `startsWith('BLOCKED ')` test sees it.

## Check results, in the prompt's order

1. Test integrity: no existing test changed, weakened, skipped or deleted. The spec's Tests to change is none. Clean.
2. Correctness: the gate (`factory/cli.py` 674-707, 722-726) does what A.1 and A.2 say. The Risk section bounds are `## Risk` to the next `## ` or `=== ` line outside a fence; the regular expression is the spec's; `none` declares nothing; entries starting `~` or `/` are skipped; both matches go through git's `:(glob)` pathspecs on `integration...head` with `--no-renames`, so a move lists both sides and a brace entry stays literal; `accepted_paths` is an exact-match addition; the refusal is raised before `MergeLock` and after the three result rows, logs `merge.refused` with the sorted paths, and changes no ticket field. `--accept-paths` (lines 877-890) refuses in the spec's order and writes nothing before its last refusal; the set-aside helper (`_set_aside_failed_rows`, 934-954) is the old `--redispatch` block moved verbatim, and `--redispatch` (921) still calls it with the same event and move. The reviewer-ESCALATE route (942-949) sets aside first, logs, then writes the ruling and moves to `checks-in-flight` with `head` and `superseded`. `build.js` (197) parks a `BLOCKED ` refusal verbatim before the second join. Edge cases the spec implies and the new test covers: no parent and no approved spec, fenced line, brace list, head not the branch tip, nothing left to accept. One edge the spec names as out of scope and the implementer reports honestly: an entry git rejects as a pathspec (`../x`) ends as a `harness-bug:` park, not a gate park.
3. Scope: every hunk belongs to parts A to E. `_branch_tip` is an extraction C.1 needs for "merge's wording"; `changed_files` gaining a `globs` parameter is the "helper in `factory/gitops.py`" A allows. Nothing outside the lettered parts.
4. Silent behaviour changes: two, both asked for by the spec and both in the changelog and design: a reviewer ESCALATE ruling now goes to `checks-in-flight` instead of `ready-for-critic`, and `merge` can now refuse on paths. The `--decision` guard (`factory/cli.py:853`) now also blocks `--close` when `--accept-paths` is given, as C.1 asks.
5. Security and data safety: the refusal text carries git's path names into a shell command in `build.js` `park()` (line 62), which wraps it in double quotes and replaces `"`. The spec's Risk section accepts this and states no file in either repository has a backtick or `$` in its name; I confirmed the instance's in-repo protected globs (`.factory/**`, `factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `docs/prompts/**`) cover no such file. No new destructive git operation; the gate only reads.
6. Protected paths touched: `factory/cli.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/06-code-reviewer.md`. All seven are on the pinned spec's `Protected paths:` line (T-0033 v2, Risk). Listed under ESCALATIONS for the record.
7. Coding standard: each new function sits on a rung I can name. `DECLARED_RE`, `declared_paths`, `undeclared_protected` are the minimum code for A.1 and reuse `specstore.lines_outside_fences`, `gitops.changed_files`, `store.load_ticket`; `_branch_tip` and `_set_aside_failed_rows` replace repeated blocks with one call each; `_in_repo` is used twice. The protected-glob flattening repeats the one expression `instance.fill_preamble` uses inline (`factory/instance.py:188`); there is no helper to reuse, and `factory/instance.py` is a protected path the spec does not declare, so leaving it is right. Rule 2: the PR description names every caller of `merge_cmd`, `resolve`, `changed_files` and the redispatch block. Rule 3: no shortcut with a known limit was added; "factory: markers added: none" is stated. Lean already.
8. PR description: readable and specific; findings below.

## Findings

- [SHOULD-FIX] PR description: What changed: the first paragraph uses "merge gate", "reviewer and verifier" and, in part B, "the build parks the sub-ticket" without saying what a merge gate, a sub-ticket, the build or parking is; only "protected path" and "instance" are glossed → the technical reader new to this project, whom the briefing names, cannot follow the first paragraph without the design document. One clause each would do: the merge gate as the harness's last check before a change merges, a sub-ticket as one mergeable piece of a planned ticket, the build as the workflow that runs implementer, checkers and merge, parking as stopping a ticket until a human answers.
- [NIT] README.md:9: the Status row reads `as of 2026-10-09`, unchanged by this change, while E.4 says the status date moves to the merge date and this machine's date is 2026-10-08 → if this merges today the page claims a date one day ahead. The implementer's Known gaps names it; whoever merges should set the date.

No BLOCKING finding.

## Prior findings

none (round 1)

## Out-of-scope observations

- `git diff --name-only` quotes a path with a non-ASCII or control character in C style (`"docs/caf\303\251.md"`) under the default `core.quotePath`. The gate would then compare and store the quoted form; it stays self-consistent across both diffs and `accepted_paths`, but the refusal text would carry a double quote the Decisions section says it never uses. No such file exists in either repository, and the spec fixes the git command, so I did not ask for a change. A later ticket could pass `-c core.quotePath=false`.
- `tests/factory/test_merge_protected_paths.py` adds a stub-clerk driver (`WF_DRIVER`) beside the real-clerk `BUILD_DRIVER` in `tests/factory/test_sibling_tests.py`; they share the prompt-matching lines but differ in what they do with the command. A shared test helper would hold both; that is test hygiene, not this ticket.

STATUS: APPROVE
CONFIDENCE: high, the diff matches every lettered part of the pinned spec, the only test file is new, the prompt copies are byte-identical and every protected path touched is declared on the approved Risk line
ESCALATIONS: for the record, declared protected paths touched (all on T-0033 v2's `Protected paths:` line): `factory/cli.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/06-code-reviewer.md`
