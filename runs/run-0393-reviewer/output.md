Commit: d9c8a4d40544b62dd11214a9fc41887b28c3e778

Round 1. Branch `factory/T-0027.4`, base `bfc764cd4f533b6909678da16564f5f8e2359bc0`. One commit; `git diff --stat` shows four files: `README.md` (+19/-4), `dev/build-harness.spec.md` (2 lines rewritten), `docs/changelog.md` (+1), `docs/design.md` (+5/-3). `git diff --check` on the range exits 0.

## Checks, in order

1. **Test integrity.** No file under `tests/` is in the diff. No code or prompt file is in the diff. The critic block of `docs/design.md` and `docs/prompts/03-spec-critic.md` are untouched (the design.md hunks are at lines 59, 91, 110 and 119, none inside the prompt appendix).

2. **Correctness against the spec and the merged code.** I read the documents against `factory/cli.py` (`_check_drift` 275, `_sibling_drift` 293, `_test_drift` 315, `_add_spec_version` 496, `_restart_note` 515, `spec_amend` 531) and `factory/compose.py` (`add_approved_changes` 234), and the changelog's incidents against the parent spec's Evidence table.
   - `docs/design.md` Spec drift paragraph: the `integration_head` record in `v<n>.yaml` with null when the repo or branch does not resolve (`_integration_head`, `_add_spec_version:500`); the check runs before the sibling-tests check (`cli.py:214-215`); it skips when a finished implementer run exists (`_runs_for` filters on `finished`, `compose.py:24`) or a `ruling-*` file exists (`cli.py:282`); the sibling rule's whole-token match and dependency closure (`cli.py:297-310`); the test rule's skip on no record, null head or a non-commit (`cli.py:319-325`), the named-file filter excluding test files and `.md` (`cli.py:330-331`), the two Tests to change lists (`cli.py:334-335`), the refusal text (`cli.py:290`). Each sentence matches the code.
   - `docs/design.md` Spec store sentences: every refusal named exists in `spec_amend` (sub-ticket, at the gate, no approved version, closed, in-flight runs, `--intent changed`, intent changes, archived, validator). The `tasks.md` keep (`cli.py:573-577`), the sub-ticket version move with `planned_from` untouched (`cli.py:580-583`), the record contents and `spec.amended` event (`cli.py:596-606`) match. "No workflow script or role prompt names it" matches the parent's Decisions; a grep of `factory/workflows/` and `factory/prompts/` for `spec amend` is left to the verifier, since the sub-ticket forbids touching those files and this diff does not.
   - `docs/design.md` line 113 and the routing row: the exact text part E items 4 and 5 ask for.
   - `docs/changelog.md` entry 65: numbered after 64, before `Declined:`. The three incidents (Nanobot T-0008's two scenarios with no policy file; this repo's T-0012 edited in place; T-0032.1 blocked by a test merged after its spec was written) are the Evidence table's rows 2, 1 and 3. "9 of 10 known breaks" is Evidence's 2 of 2 plus 7 of 8; "about half" is Evidence's own phrasing for 17 of 36 and 29 of 43. The four rejected alternatives are the ones the Decisions list. The six phrases the acceptance greps for are present.
   - `dev/build-harness.spec.md`: the `factory resolve` bullet says `resolve` has no `--amend-spec` and names the built command; the Spec store paragraph describes the critic section's inclusion rule (matches `compose.py:243-247`, including the `none` body and the left-out case), the `v<N>.yaml` record and the drift check.
   - `README.md`: the Amend row names the three triggers, the amend-or-restart rule and what `--intent changed` prints; the Unstick row gains the drift park; the Built bullet starts `**Spec amendment and drift.**`, glosses "spec drift" at first use and ends with the required sentence. The status date is already 2026-10-09 (`README.md:9`), today's UTC date, so there was nothing to bump.

3. **Scope.** Two README hunks fall outside the four listed items: the Spec critic row of the role table (`README.md:86`) and the store layout tree (`README.md:431-432`, `441-442`). Both document paths and inputs that ST-1 to ST-3 added, and README's "Maintaining this page" says a change to a path updates its sentence in the same ticket; this is that ticket's documents sub-ticket. The implementer disclosed both under Known gaps. I accept them. The second `--amend-spec` mention in the `resolve` bullet and the "`approve-spec` or `spec amend` pins" wording are inside the two passages the sub-ticket names and are needed for those passages not to contradict themselves.

4. **Silent behaviour changes.** None possible: no code, prompt, workflow or test file changed.

5. **Security and data safety.** Nothing applicable. No secrets, paths or commands beyond those the parent spec already documents.

6. **Protected paths.** None touched. The four changed files are not in the protected list, and `docs/prompts/**` is not in the diff.

7. **Coding standard.** No code in the diff. Lean already.

8. **PR description.** What changed opens by saying in words what T-0027 adds and glosses the factory, the spec gate, a sub-ticket and the critic at first use. The item list is organised by file, but each item states the content, not a path. Known gaps lists every edit beyond the listed items, the unbumped date and the figures it did not re-measure, and says where each came from. Readable at the gate.

## Findings

none

## Prior findings

none (round 1)

## Out-of-scope observations

- `docs/design.md:60`, the Tests a sibling added paragraph, still says "amend the sub-ticket or the pinned spec" without the `factory spec amend` pointer that line 113 now carries. Part E item 4 names only line 113, so this is not a defect of this sub-ticket; a later editor may want the same parenthetical there.
- `dev/build-harness.spec.md` still names `--amend-spec` in build cases 48, 77, 83 and 84 and in the round-4 responses, as the implementer noted. Those are historical records of the build, not the current signature, and the sub-ticket names only lines 193 and 315.

STATUS: APPROVE
CONFIDENCE: high. Every sentence the documents add was read against the merged code or the parent spec's Evidence and matched; the diff touches only the four documents the sub-ticket names and no test, code, prompt or protected path.
ESCALATIONS: none
