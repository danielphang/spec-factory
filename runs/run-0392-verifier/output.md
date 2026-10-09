Commit: d9c8a4d40544b62dd11214a9fc41887b28c3e778 (branch `factory/T-0027.4`; base bfc764cd4f533b6909678da16564f5f8e2359bc0, which is also the current `main`, so `main...HEAD` is the sub-ticket's own diff)

Environment: worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0392-verifier/wt`, clean at the head. Every command ran inside the fresh-HOME wrapper. The base tree was extracted with `git archive bfc764c | tar -x` into `scratch/base`. The acceptance commands, copied verbatim from the parent spec v3 (`specs/harness-docs/spec.md`), are in `scratch/acc.sh`. The diff touches 4 files: `README.md`, `dev/build-harness.spec.md`, `docs/changelog.md` and `docs/design.md`. No code, prompt or `docs/prompts/` file changed.

Per criterion:
- NEW | changelog contiguous entry (`awk ... CONTIGUOUS; grep 'factory spec amend' | grep -c .; grep -oF six phrases | sort -u | grep -c .`) | base: `CONTIGUOUS`, `0`, `0` | PR: `CONTIGUOUS`, `1`, `6` | PASS
- NEW | design doc and build spec (`echo "amend=... build_drift=..."`) | base: `amend=0 intent=0 drift=0 row=0 build=0 build_drift=0` | PR: `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1` | PASS
- NEW | README lists the amend command and the drift check (`H=$(sed -n '/^## Where a human decides/,...'); B=...`) | base: `amend=0 intent=0 built=0` | PR: `amend=1 intent=1 built=1` | PASS
- REGRESSION | `(git diff --check main...HEAD; echo "exit=$?")` | base: not run | PR: `exit=0` only | PASS
- REGRESSION (intermediate) | `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)` | base: not run (it printed `copies=same` there as well) | PR: `copies=same` | PASS
- REGRESSION (intermediate) | harness suite, the second gate command below | base: not run | PR: `486 passed in 409.25s` | PASS

Each NEW criterion fails on the base for the reason the spec gives (the text is absent) and passes on the PR. These results match the "fails today" outputs in the spec's verification.md.

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0, no output.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `486 passed in 409.25s (0:06:49)` (log at `scratch/suite.log`).

Probes. These are documents, so I checked the text against the merged code that ST-1 to ST-3 built, and checked that the checks did not pass on wording alone.
- Spec drift paragraph (`docs/design.md:62`) against `factory/cli.py` `_check_drift` (275), `_sibling_drift` (293) and `_test_drift` (315) → every claim matches:
  - the check runs before `_check_sibling_tests` (cli.py:214-215);
  - it skips when there is a finished implementer run, which `compose._runs_for` counts only when `meta.finished` is set, or a `ruling-*` file;
  - it uses the whole-token regex and the dependency closure;
  - the test rule's base is `v<n>.yaml` `integration_head`, and the rule is skipped when the record is missing or null or the head is not a commit;
  - named files exclude test files and `.md` files, and listed files are cut at `::`;
  - the refusal prefix is `BLOCKED from harness: spec drift:`;
  - `_add_spec_version` writes `v<n>.yaml` for all three callers.
  → OK
- Spec store sentences and changelog entry 65 against `spec_amend` (cli.py:531) and `_restart_note` (515) → match. Both cover the refusals (sub-ticket, awaiting-spec-gate, no approved version, closed, reason, in flight, `--intent changed`, intent changes, archived, validate and applies), the `tasks.md` kept across the re-pin, the sub-ticket version moves with `planned_from` untouched, the `amendment-<k>.md` record and the `spec.amended` event. The restart routes are named too. → OK
- `dev/build-harness.spec.md:315`, the rewritten parked-parent route ("`--to spec-gate` and `approve-spec ID --edit FILE`, which moves the parent to `ready-for-planner`") → `approve_spec` refuses unless the ticket is `awaiting-spec-gate` (cli.py:1052) and sets `ready-for-planner` (cli.py:1062). The new text is accurate, and the old `--amend-spec` text it replaced was not. → OK
- README "Where a human decides" table → the new Amend row has the same 5 `|` fields as its neighbours (lines 795-802), so the table still renders. The `**Built**` and `**Not built**` anchors that the README check slices on each occur once. → OK
- Copies of changed design text → `grep` finds none of the changed passages in `docs/prompts/` or `factory/prompts/`, so no prompt file needed re-copying. → OK
- Status date → it reads 2026-10-09 on both the base and the PR. Today is 2026-10-09, so leaving it unchanged is correct. → OK
- Wording of the figures → the design paragraph and the changelog say the test rule "parks about half of all sub-tickets". The spec's Risk section gives 17 of 36 and 29 of 43, which is 46 of 79 or about 58%, so "about half" is fair. Its Evidence line 41 says "about half the sub-tickets that had no problem", a slightly different denominator. No criterion depends on this. → OK (minor)

Out-of-scope observations:
- README's "Maintaining this page" rule says a thing appears above "Where this can go" only after it has run on a real ticket. The spec nonetheless asks for an Amend row under "Where a human decides". The implementer also added a critic-input mention to "What each role reads and writes" and `v<n>.yaml` and `amendment-<n>.md` to the store tree, for features that have not yet fired on a real ticket. The Built bullet says so. The approved spec directs the Amend row, so this is not a failure here.
- The two README edits beyond the four listed items (the critic row and the store tree) are accurate against `compose.py:259` and `cli.py:501`/`:550+`, and the PR description discloses them.

STATUS: VERIFIED
CONFIDENCE: high. All six criteria and both gates ran on d9c8a4d, the NEW ones fail on base bfc764c as the spec states, and I checked every documented behaviour against the merged code.
ESCALATIONS: none
