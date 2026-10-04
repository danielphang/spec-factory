## Proposed change

Size: about 180 changed lines plus one new test file, so one PR. The planner may split it into two seams: the prompt texts (A, C, D, with their part of E), and the harness check (B, with the rest of E).

**A. Planner: labels per sub-ticket, interim tests, sibling entries.** In the planner block of `docs/design.md` §4 and its verbatim copies `docs/prompts/04-planner.md` and `factory/prompts/planner.md`, replace these four lines:

```text
  Acceptance: the parent's scenarios it covers, each as its WHEN command,
    THEN result and verification.md label, plus any intermediate checks
    it needs, labelled NEW or REGRESSION the same way
  Tests to change: none | the subset of the parent's list this one touches
```

with:

```text
  Acceptance: the parent's scenarios it covers, each as its WHEN command
    and THEN result, plus any intermediate checks it needs. Label each
    NEW or REGRESSION against this sub-ticket's own base: the integration
    branch with its dependencies merged. A check that already passes
    there, as an invariant or because an earlier sibling made it true,
    is REGRESSION, whatever the parent's verification.md label says.
  Interim tests: none | each new test file this one adds that a later
    sibling will break, with that sibling's ID
  Tests to change: none | the subset of the parent's list this one
    touches, plus each test an earlier sibling adds that this one's
    change breaks, one line each:
    - `<file>[::<test>]` (added by <sibling ID>): <reason>
    This one must depend on that sibling. Before each implementer run,
    the harness checks that a merged sibling added the file, and parks
    the sub-ticket if not. A test that existed before the parent's first
    merge goes here only if the parent's list names it.
```

All three files must stay byte-identical in that block.

**B. The sibling-tests check.**

1. `factory/subtickets.py`: add `PLAN_FIELDS`, the planner's field names in lower case: `scope`, `acceptance`, `interim tests`, `tests to change`, `protected paths`, `out of scope`, `depends on`, `parallel-safe`, `coverage map`. Add a function `sibling_tests(text) -> list[str]`. It walks the sub-ticket text line by line. A line that matches `FIELD_RE` with a key in `PLAN_FIELDS`, or a heading line (`_is_heading`), opens a new field. The function reads only lines inside the `tests to change` field, from its own line to the next field or heading. On those lines it finds every `` `<path>` (added by <anything>) `` with ``re.compile(r"`([^`\s]+)`\s*\(added by\s+[^)]+\)")``, drops any `::<test>` suffix, and returns the file paths in order without repeats. A mention anywhere else, such as a Scope or Parallel-safe line, is ignored.
2. `factory/gitops.py`: add `first_added(repo, base, tip, path) -> str | None`. It returns None when `git cat-file -e <base>:<path>` succeeds, because the file existed at the base. Otherwise it returns the first line of `git log --diff-filter=A --reverse --format=%H <base>..<tip> -- <path>`, or None. Add `is_ancestor(repo, a, b) -> bool`, which runs `git merge-base --is-ancestor a b`.
3. `factory/cli.py`: in `run_start`, after the in-flight guards and before `tripwire.baseline(cfg)` (line 212), add: when `a.role == "implementer"` and the ticket has a `parent`, call a new `_check_sibling_tests(root, cfg, t)`. That function reads `specs/<id>/subticket.md` and returns when `sibling_tests` finds nothing. Otherwise it loads the parent's `parent_base`, the integration branch's tip (`gitops.integration_branch` and `gitops.rev`), and the `merge` record of every other sub-ticket of the parent whose status is `merged` and whose `merge.main_after` is set. A path passes when `parent_base` is set, `first_added` returns a commit, and for some sibling that commit is an ancestor of `main_after` and not of `base_before`. The first path that fails raises `Refused`, with a message that starts exactly `BLOCKED from harness: ` and names the path and the parent. The form used in the prototype was `BLOCKED from harness: Tests to change lists <path> as added by a sibling, but no merged sibling of <parent> added it since <base[:9]>; list it in the parent spec's Tests to change, or remove it`. When `parent_base` is unset, it said `(no sibling has merged)` in place of `since …`. Because it raises before `tripwire.baseline` and before the run id is reserved, a refusal writes no run directory, worktree, branch or `in_flight` entry.
4. `factory/workflows/build.js`, `runRole` (line 68): when `start.ok` is false and `start.error` starts with `BLOCKED `, park with `start.error` verbatim as the reason. Every other refusal keeps today's `harness-bug: run start <role>: <stderr>`. `resolve --ruling` (`factory/cli.py:748`) already accepts a park reason that starts with `BLOCKED` and returns the sub-ticket to `ready-for-implementer`. Its next run start checks again, so the human amends the sub-ticket text, or the pinned spec, before ruling.
5. A new test file, `tests/factory/test_sibling_tests.py`, with the cases of the build-dispatch scenarios below. Each case builds a scratch store with `FACTORY_STATE` and a scratch git target, like the existing suite. Add three cases more: a sibling that has not merged (no `parent_base`) refuses; a file a sibling added, deleted later and re-added by another commit is still accepted, because the first add counts; and `sibling_tests` returns nothing for the T-0002.6-style Parallel-safe mention.

**C. Spec writer and critic: tests a decision overturns.**

- In the spec writer block of `docs/design.md` §2, `docs/prompts/02-spec-writer.md` and `factory/prompts/spec_writer.md`, insert this bullet in RULES directly before "- Open questions stay open.":

```text
- Tests a decision overturns: for each Decision that changes existing
  behaviour, search the existing tests for ones that pin the old
  behaviour, and list each under "Tests to change" with the decision it
  follows. One left off blocks the implementer later.
```

- In the critic block of `docs/design.md` §3, `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`, put these lines directly after the rubric line "1. Grounded: cited paths and symbols exist; evidence is real output.":

```text
   For each Decision that changes existing behaviour, search the tests
   for the old behaviour yourself: a test that pins it and is missing
   from "Tests to change" is a finding.
```

**D. Preamble and code reviewer accept a checked sibling entry.**

- Preamble (`docs/design.md` "Shared preamble", `docs/prompts/00-preamble.md`, `factory/prompts/preamble.md`, all three byte-identical): replace `only those listed under "Tests to change" in the human-approved spec).` with these lines:

```text
only those listed under "Tests to change" in the human-approved spec, or
in your sub-ticket as added by an earlier sibling, which the harness
checks).
```

- Code reviewer (`docs/design.md` §6, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`): replace `   are BLOCKING unless the spec lists that test under "Tests to change".` with these lines:

```text
   are BLOCKING unless the spec lists that test under "Tests to change",
   or the sub-ticket lists it there as added by an earlier sibling.
```

**E. Documents.**

1. `docs/design.md`, piece 8 row (line 46), "What it must do": after "is that row for exactly the tests listed", end that sentence there and add: "A test file an earlier sibling sub-ticket of the same parent added is also covered when the sub-ticket lists it as added by that sibling and the sibling-tests check has passed (Tests a sibling added, below);" before "any other guardrail…". In the "GitHub gives you" cell, after `not in the pinned spec's "Tests to change"`, add "or among the sub-ticket's checked sibling entries".
2. `docs/design.md`, the Spec approval row (line 146): replace "which is the only authorization to alter an existing test" with "which is the only authorization to alter a test that existed before the parent's first sub-ticket merged; a test an earlier sibling added needs only the sub-ticket's checked entry (piece 8)".
3. `docs/design.md`, a new paragraph directly before "**Only the dispatcher writes a live store during a run.**", one line, starting `**Tests a sibling added.**`. It says: the entry form; that the planner writes these lines and the spec gate never saw them; the rule of B.3, with "parent's base" glossed as the integration branch before its first sub-ticket merged; the refusal (exit 2, nothing written, a reason that starts `BLOCKED from harness:` and names the file); that the build parks the sub-ticket with that reason and the human resolves it as an implementer's BLOCKED (amend the sub-ticket or pinned spec, then `resolve --ruling`, or close); and that a test that existed before the parent's first merge still needs the pinned spec's list.
4. `docs/changelog.md`: one new numbered entry after the last one, starting `<n>. After issue #40 (2026-10-04), `. It covers the per-sub-ticket labels ("own base"), the `(added by <sibling ID>)` entries and "Interim tests", the check and its `BLOCKED from harness:` park, the preamble and reviewer change, "the spec writer lists the tests each behaviour-changing Decision overturns", and "critic rubric 1". It ends with "Rejected: letting the implementer edit a test on its own judgement." Numbering stays contiguous.
5. `dev/build-harness.spec.md`, kept consistent with the design. Line 203 (`run start` guards): add the sibling-tests refusal after the in-flight guard, citing doc §Harness, "Tests a sibling added". Line 245 (piece 8): an existing test file is also allowed when one of the sub-ticket's `(added by <ID>)` lines that `run start` checked names it. Line 275 (`runRole`): a refusal whose JSON `error` starts `BLOCKED ` parks with that error verbatim, so `resolve --ruling` applies.
6. `README.md`. Under "What is built and what is not", "Built", add a bullet after "Live-store fence" that starts `- **Sibling tests check.**`. It says, in plain words: a planner may let a sub-ticket change a test file that an earlier sub-ticket of the same spec added; before each implementer run the harness checks in git that a merged earlier sub-ticket added it; otherwise the sub-ticket parks as blocked and the human rules on it as on any blocked build; any other existing test still needs the approved spec's list; it is tested and has not yet fired on a real ticket. In "Where a human decides", in the **Unstick** row, change `--ruling F`'s note to "(a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added)". The status date is already 2026-10-04.

## Tests to change

none. With the prototype of A to E, `.venv/bin/python -m pytest -q -p no:cacheprovider tests/factory`, with `TMPDIR` set to a fresh directory under `/tmp`, printed `265 passed`. The tests that compare prompt copies (`tests/factory/test_instance.py`, `test_run_scratch.py`, `test_writing_standard.py`, `test_decision_log.py`) still pass, because every copy changes together. No Decision of this change overturns behaviour that an existing test pins. That suite run is the search part C asks for.

