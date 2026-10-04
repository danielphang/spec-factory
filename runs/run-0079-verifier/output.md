Commit: 7090d9d21f17688df45fd3701dc5ee26f01452c4

Environment: PR = the given worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0079-verifier/wt` (branch `factory/T-0012.5`, HEAD `7090d9d`, `git status --short` empty before and after). Base = a fresh scratch `git clone` of `~/dev/spec-factory`, detached at the given base `68e89456939ac7939ef659975dfbb37812bd6f83` with a local `main` at the same SHA. Parent scenarios ran with `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, which is `parent_base` in `intake/state/tickets/T-0012.yaml`. Every WHEN was copied verbatim: the parent scenarios from `specs/repo-layout`, the intermediates from the sub-ticket, and no-old-paths "documents only" from `intake/state/specs/T-0012.2/subticket.md:19`. The whitespace intermediate ran as `git diff --check main...HEAD; echo "exit=$?"`.

The PR description names base `bed7e28`. The given base is `68e8945`. `git diff --name-only bed7e28 68e8945 | grep -v '^intake/state/' | wc -l` → `0`, so main moved only in store records and the document comparisons are unaffected. `main...HEAD` resolves to merge-base `bed7e28`.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | design-doc-instance-text | `kept=0 open=1 piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` | PASS
- NEW | build-spec-render-paths | `stale=3 new=0 d8=0` | `stale=0 new=3 d8=1` (N=3 ≥ 3) | PASS
- NEW | changelog-entry-appended | `0` | `1` | PASS
- REGRESSION | responses-unchanged | `exit=0` | `exit=0` | PASS
- REGRESSION | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- REGRESSION | design-text-kept | `0` | `0` | PASS
- REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` | PASS
- REGRESSION | no-old-paths, documents only | `exit=1` | `exit=1` | PASS
- REGRESSION | whitespace (sub-ticket diff) | `exit=0` (empty range at base) | `exit=0` | PASS

Each NEW criterion fails on base for the reason the spec gives. At base, the build spec's stale hits before `## Responses` (line 523) are lines 145, 158 and 456, as the sub-ticket says, plus 537, which is inside Responses.

Gate suite: PASS
- `git diff --check main...HEAD` printed nothing, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `92 passed in 100.51s`. A second run, which captured the exit code, gave `92 passed in 109.31s`, `pytest_exit=0`. uv warned that the inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` would be ignored, so both runs used the worktree's own `.venv`, which is gitignored.

Probes: input → result → OK / CONCERN
- Exact parent text. I extracted F.1, F.2, F.3 and the D8 value from `intake/state/specs/T-0012/v3.md` §F and compared each to the PR text. The "Role-context block" paragraph ends with the F.1 text: True. Its old text minus the removed sentence is a prefix of the new one: True. Piece 8 cell 3 ends with the F.2 text: True. The other cells of that row are unchanged: True. `\n42. <F.3 text>\n` is in `docs/changelog.md`: True. The D8 Value cell equals F.4's value exactly: True. The layout row at line 145 equals F.4's text. → OK. The fix is the specified prose, not text shaped to pass the greps.
- Diff scope. The PR touches 3 files (`dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md`), 7 insertions and 6 deletions. `diff main:docs/design.md docs/design.md` gives 4 changed lines, which are the two excluded lines out and in. The changelog diff against main is one added line, entry 42, placed after 41 and before `Declined:`. The `--word-diff` of the build spec shows changes only in the D8 cell, the layout row, the render bullet, and item 82, where each `factory/prompts/design-doc.md` became `docs/design.md`. → OK
- Stale paths in the whole build spec, not only above Responses. `grep -n 'factory/prompts/design-doc\.md'` finds only line 537, inside `## Responses`, which F.4 says to leave alone. → OK
- The F.2 full stop. The implementer added "." after "on the PR itself" before appending the F.2 sentence. That change is on the line design-text-kept excludes, and every other cell of the row is byte-identical. → OK. It is a readability change the gate may want to see. It does not break any criterion.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran verbatim on both base and PR with the expected results, both gates passed with exit codes captured, and the probes confirm the text is the parent's F.1–F.4 wording in only the 3 permitted files.
ESCALATIONS: none
