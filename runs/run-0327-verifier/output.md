Commit: f25dffed5f970142f9da01b0ed24f8e8deaac40a (branch `factory/T-0034.1`; base and `main` both at 2e73dbb8c997a4284649dcc25f5e9fbba8b65fea)

The change does what T-0034 asks. All five prompt-text copies carry the new rules word for word. The system prompts the harness writes for a spec writer run and for a critic run contain them. Nothing else in the prompts changed. Both gates pass.

Every command ran exactly as written, under the fresh-HOME wrapper, from the PR worktree after `uv sync --frozen`. Base results come from a detached worktree at 2e73dbb in this run's scratch directory, also after `uv sync --frozen`. In both checkouts `main` resolves to 2e73dbb.

Per criterion:
- NEW | Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule | base: `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged` / `critic copy=SAME doc=0/6 run=0/6 fill=unchanged` | PR: `spec_writer copy=SAME doc=4/4 run=4/4 fill=unchanged` / `critic copy=SAME doc=6/6 run=6/6 fill=unchanged` | PASS (fails on base for the reason the spec gives: no copy has the rules)
- NEW | Spec writer and critic run prompts carry the new rules | base: `spec_writer batch=0 writes=0` / `critic batch=0 suite=0 cap=0` (no stderr, so both system-prompt.txt files existed) | PR: `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 cap=1` | PASS
- REGRESSION | Rubric, round limit, format and every other prompt are unchanged | base: not run | PR: `sections_changed=0 removed=0 others=0` | PASS
- NEW | The changelog and the principles page record the change | base: `CONTIGUOUS` / `0` / `implemented=0 status=0` | PR: `CONTIGUOUS` / `5` / `implemented=1 status=1` | PASS (fails on base for the reason the spec gives)
- REGRESSION | The turn-economy change adds no whitespace errors | base: not run | PR: `exit=0` | PASS

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `364 passed in 222.50s (0:03:42)`, exit 0. The full log is `scratch/pytest.log`.

Probes:
- Is the inserted text the spec's text, or just text that holds the grep phrases? I took the added lines of each file from `git diff main...HEAD` and compared them byte for byte (`cmp`) with the spec's code blocks in `specs/T-0034/v2.md`. `docs/prompts/02-spec-writer.md` and `factory/prompts/spec_writer.md` match block A (7 lines). `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md` match block B (12 lines). The lines added to `docs/design.md` are exactly A followed by B. Changelog entry 58 matches the spec's quoted text byte for byte, and there is exactly one entry 58. → OK
- Does each rule land where the spec says, in the prompt a real run receives? I composed a spec writer run and a critic run in a throwaway store. The writer's system-prompt.txt contains block A whole. In the critic's, block B sits whole between `Spot-check at least 2 cited paths and 1 acceptance command yourself.` and the blank line before `ANTI-GOODHARTING`. The writer-only rule is not in the critic prompt, and the critic's cap is not in the writer prompt. → OK
- Would scenario 1's check catch a broken copy? This tests whether the check is meaningful, not whether it is special-cased. In a throwaway worktree at HEAD I deleted one critic line from `docs/design.md` and changed one character in `factory/prompts/critic.md`. The check then printed `critic copy=DIFF doc=6/6 run=6/6 fill=changed`. The phrase counts stay at 6/6 because neither edit touched a counted phrase, but `copy` and `fill` both flag the drift. The worktree was then discarded. → OK
- `docs/principles.md` principle 2, joined into one line: it holds the full required "Implemented by" ending and the full required status sentence, each found once with `grep -F`, and the old `done by #41. ` wording is gone. Lines 44 and 46 are 102 and 101 columns wide. The spec asks for "about 100", and the file had 26 lines over 100 columns on `main`. The PR description reports both lines. → OK
- Files changed (`git diff --stat`): 7 files, 63 insertions, 3 deletions. All 3 deletions are the rewrapped principles lines. No file under `agents/` changed, and neither did `README.md` or `dev/build-harness.spec.md`, which the spec puts out of scope. → OK

Protected paths changed, all declared in the spec's Risk section: `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`. Each change adds the lines the spec describes and nothing else.

Not verified: whether the rules really cut the spec writer's turns, or whether spec quality holds. Checking that needs live model runs. It is Operator steps 1 and 2 (the replay before the runtime upgrade), not this check.

STATUS: VERIFIED
CONFIDENCE: high. All five scenarios produced their expected output on f25dffe. The three NEW ones produced the predicted failures on 2e73dbb. Both gates passed. Byte-for-byte comparisons show the inserted text is exactly the spec's.
ESCALATIONS: none
