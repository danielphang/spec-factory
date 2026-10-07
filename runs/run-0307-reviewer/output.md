Commit: c01e7c2cf8bdef4f73fd8443744906b9ea89db74

Reviewed by reading the diff `97becfd...c01e7c2` (14 files, +204/-28) against the pinned T-0032 spec v1, the sub-ticket and the two human rulings. I ran no suite and no gate command. Narrow commands I ran from the worktree, each cited where it supports a check:
- `git rev-parse HEAD` → `c01e7c2cf8bdef4f73fd8443744906b9ea89db74`: the head the sub-ticket names.
- `cmp docs/prompts/00-preamble.md factory/prompts/preamble.md` → `same`: the two preamble files are byte-identical (part A).
- `grep -c 'KILLED condition\|KILLED seam' dev/build-harness.spec.md` → `0`: part D.2's last requirement holds.
- `grep -n 'def checker' tests/factory/test_gate_paths.py:93` → `def checker(self, role: str = "verifier")`: the ruling's `t.checker()` composes a verifier input, as the ruling says.

## Check 1. Test integrity
One existing test file changed: `tests/factory/test_gate_paths.py:123`, `t.checker("reviewer")` → `t.checker()`. The human ruling of 2026-10-06, item 1, names this test as a test to change and prescribes exactly this edit and nothing else in the file; the diff shows one changed line. The assertions are unchanged. Not blocking. New file `tests/factory/test_empty_output.py` adds 6 tests; none is skipped or weakened, and each asserts the spec's value (`EMPTY-OUTPUT`, `KILLED`, the exact JSON, exit 2 with nothing written).

## Check 2. Correctness
- C.1 `factory/cli.py:343-346`: no override and blank text → `EMPTY-OUTPUT` with `error: empty output`. Line 367 chooses `run.killed` only for `KILLED`, so the new status logs `run.finished`, as the spec and the new test require. The override branch (line 341) is untouched.
- C.2 `factory/cli.py:302-309` `run_last_message`: reads `meta.yaml`, refuses with `Refused` (exit 2 via `main`, `cli.py:1604-1607`) unless status is `EMPTY-OUTPUT`, writes `last-message.md` with one trailing newline through `store.write_text`, prints the spec's JSON. `_run_dir` (`cli.py:191-195`) refuses an unknown run before anything is written. `("run","last-message")` is not in `READ_ONLY` (`cli.py:1563`), so the fence treats it as a write, as the spec asks; the dispatcher already passes the fence for `run finish`, so this call passes it the same way.
- C.3 `factory/workflows/build.js:68-77` and `intake.js:75-84`: `runRole` calls `runOnce`, returns any non-EMPTY-OUTPUT result (including `null` from a park or harness-bug), re-dispatches once, and parks `EMPTY-OUTPUT from <role>` with both run ids. The `killed` condition is gone (`build.js:118-119`, `intake.js:118-119`), so `run finish` decides in one place. The quoting `said.slice(-4000).replace(/'/g, "'\\''")` yields `'\''` for each apostrophe inside a single-quoted word: correct for `sh`. A `null` return gives `said === ''` and keeps nothing (scenario 2). The thrown-call `catch` is unchanged. `build.js:153` (the `budget kill: implementer` park) is deleted; it was unreachable after C.1.
- Re-dispatch preconditions I checked in the CLI: `run start` reuses an existing implementer worktree (`cli.py:281-282`, `if not wt.exists()`), and `run finish` clears `in_flight` (`cli.py:359-360`), so a second start of the same role on the same ticket is accepted. For a checker, `runOnce` still runs `run cleanup` before the second start.
- Join interaction: a reviewer that parks returns `null`, `build.js:183` returns `null` for it, and `build.js:188` returns before the join, so no reviewer row is recorded and the verifier's rows stand. `resolve --redispatch` (`cli.py:889-890`) accepts a park from `checks-in-flight`, which is where this park comes from, and re-runs only the role with no row. Scenario 1's `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` is what this code produces.
- B.2 `factory/compose.py:221-233`: the non-reviewer text is the old f-string split at the same characters; the verifier's and implementer's paragraphs are byte-for-byte what they were. The reviewer gets the ruling's sentence, then the SKIPPED lines for every role (ruling item 3).
- A and B.1: the three preamble copies and the three reviewer copies gain the spec's exact text at the spec's exact places; no existing line of the reviewer prompt is removed (the diff has no `-` line in either reviewer file).
- D: every edit the spec lists is in the diff (design.md:99, 100, 106, 136-137, 224-227, 622-627; build spec lines 205-206, 276, 301, 411; README lines 9, 173-176, 217, 565, 860-866; changelog entry 57).

## Check 3. Scope
Nothing outside parts A to D and the ruling's two edits.

## Check 4. Silent behavior changes
`run finish` now returns `EMPTY-OUTPUT` where it returned `KILLED` for a blank output without override. The spec asks for this; the join's `KILLED` handling (`cli.py:715-722`) and `results record --killed` stay for hand-recorded rows, as the spec's Out of scope says. `build.js:184` still appends `--killed` for a `KILLED` status that the workflow can no longer produce: dead but harmless, and the spec keeps it.

## Check 5. Security and data safety
The last message is a role's own output embedded, single-quoted, in a clerk command. The quoting is correct for the shell. The clerk is an agent, not a shell, so the text also reaches a model prompt; see Out-of-scope observations. No secrets, no destructive operation, no authz change.

## Check 6. Protected paths
All eight touched protected paths are declared in the parent's Risk list (harness: `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`; generated: `docs/prompts/00-preamble.md`, `docs/prompts/06-code-reviewer.md`). Listed under ESCALATIONS as the role requires. No undeclared protected path is touched.

## Check 7. Coding standard
- Rule 1: `run_last_message` uses the repo's `_run_dir`, `store.read_yaml`, `store.write_text`, `Refused`, `out`, `_rel`. The test file's `Store` helper repeats the per-file `cli`/`ok` pattern that 8 existing test files use and no conftest provides, so it is the repo's convention, not a `reuse:` finding.
- Rule 2: the PR description names the callers of `runRole` and `compose.compose`, found by grep.
- Rule 3: the description states "factory: markers added: none"; the diff adds none.
- Rule 5: `EMPTY-OUTPUT`, `last-message`, `runOnce` are used with one meaning from spec to code to documents.
- Rule 6: the test's store lives under `tmp_path` via `FACTORY_STATE`; it adds no path outside the repository.
Lean already.

## Check 8. PR description
What changed says in words what each part does, and glosses preamble, clerk, fence and SKIPPED lines at first use. Known gaps names the untested reviewer-SKIPPED case, the unreachable `--killed` suffix and the clerk quoting risk, and says what happens if each fires. Readable at the gate.

## Findings
- [NIT] factory/workflows/build.js:124-128 (and intake.js:122-126): the `fin.parked` return at line 124 comes before the `run last-message` call, so an `EMPTY-OUTPUT` run that the tripwire also parked keeps no last message → the one case where a human most wants to know why the run stopped loses the message. The spec's wording ("when `run finish` succeeds with status EMPTY-OUTPUT") covers a parked-but-ok finish, so moving the keep above the `fin.parked` check would match it exactly. Rare; not blocking.

Prior findings: none. This is the first review round on this sub-ticket; run-0304 ended BLOCKED from the implementer before any review ran.

## Out-of-scope observations
- The last message reaches the clerk as part of a prompt ("Run exactly this one shell command … `--text='…'`"). A role's final message can contain lines that look like instructions or a second command, so the clerk may alter or refuse the call. The spec decided this route and its failure is ignored, so only the kept message is lost; a `--text-file` form would remove the surface if it ever bites. Recorded in the PR's Known gaps already.
- `factory/workflows/build.js:184` keeps `${r.status === 'KILLED' ? ' --killed' : ''}` for a status the workflow no longer produces; the spec keeps it.
- T-0030 will edit the same reviewer paragraph in `factory/compose.py` and the §6 block; whichever merges second conflicts there, as the PR description notes.

STATUS: APPROVE
CONFIDENCE: high. Every lettered part is in the diff at the spec's exact text and place, the one existing-test edit is the ruling's own, and the retry, park and redispatch paths were traced through the CLI guards they depend on; the suite and gates are the verifier's to confirm.
ESCALATIONS:
- Declared protected paths touched (parent Risk list; listed once, as check 6 requires): harness `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`; generated `docs/prompts/00-preamble.md`, `docs/prompts/06-code-reviewer.md`. Each change is the one the spec describes.
