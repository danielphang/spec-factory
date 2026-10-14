Commit: 8d07f458b674f9041c6c2b861e626dc08121f053 (branch `factory/T-0052.1`). Base given: 43a289e000c971ecc22d5303d387e3669bf5d987 (`main`).

The branch was not cut from the base I was given. `git merge-base HEAD main` is `525d73f`. Since then `main` has gained T-0053.1 (merge `af439c4`), which added its own changelog entry `73. After issue #110`. This PR also numbers its entry 73. On its own the branch passes every acceptance command. Merged onto `main`, it breaks the changelog criterion. The spec planned for this case: "If another ticket takes the next number first, take the next free one: the entries must stay numbered without a gap." Details are under the changelog criterion below.

How I ran things: every command went through the running-code wrapper (a fresh temporary HOME each time), after `uv sync --frozen`. For the PR I ran in the worktree at `8d07f45`. For the base I ran in a clone at `43a289e` under my scratch directory. To check the merge, I made a second scratch clone at `43a289e` and ran `git merge --no-ff 8d07f45`. Each scenario command was saved to `scratch/sc/s<n>.sh`. I grep-checked each saved command against the input to confirm it matches the spec text exactly.

Per criterion:
- NEW | Every role agent template's frontmatter parses and carries name, description, model and tools | base: clerk and stub `keys=ok`; planner, spec-critic, spec-writer and triage `keys=unparsed` | PR: all six `keys=ok` | PASS
- NEW | The four fixed templates keep their description's words and every other line | base: each of the four `text=changed rest=same`, then `others=same` | PR: `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, `others=same` | PASS
- NEW | The suite fails on a template with broken frontmatter and names it | base: `suite=passed clerk=0 stub=0` | PR: `suite=failed clerk=1 stub=1` | PASS
- NEW | init reports an edited agent copy and leaves it as it is | base: `exit=0 stale=absent kept=yes named=0 others=0` | PR: `exit=0 stale=factory-planner.md kept=yes named=1 others=0` | PASS
- REGRESSION | init still creates a missing agent copy and lists no matching copy | base: not run (I ran it anyway: `exit=0 created=factory-triage.md stale=0 same=6 differs=0`) | PR: `exit=0 created=factory-triage.md stale=0 same=6 differs=0` | PASS
- NEW | README describes init's report of a differing agent copy | base: `row=0 step=0 missing=1` | PR: `row=1 step=1 missing=1` | PASS. On the trial merge it also gives `row=1 step=1 missing=1`.
- NEW | The changelog records issue 108 in one entry without a numbering gap | base: `CONTIGUOUS`, `0`, `0` | PR head alone: `CONTIGUOUS`, `1`, `3` | FAIL against the given base. On the trial merge of `8d07f45` into `43a289e` (no conflict; git auto-merged `docs/changelog.md`), the same command prints `GAPPED`, `1`, `3`. `grep -n '^7[0-9]\. ' docs/changelog.md` on the merge shows line 78 `73. After issue #108` followed by line 80 `73. After issue #110`. That is two entries numbered 73, with #108's entry placed before #110's. The command passes on the head only because the head does not contain `main`'s entry 73. The fix the spec asks for is to rebase onto `43a289e` and renumber the entry to 74, after #110's entry.
- REGRESSION | README stays within its line budget and both documents pass the whitespace check | base: not run (I ran it anyway: `readme=within`, `check=0`) | PR: `readme=within`, `check=0` | PASS. On the trial merge, README is 1,108 lines and the command prints `readme=within`, `check=0`.

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0. Note that this compares the merge-base `525d73f` to HEAD, so it does not see the entry-73 collision.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `593 passed in 95.18s`.
  Extra, not a gate: the full suite on the trial merge (`bd9583a`) gave `593 passed in 114.76s`. The code side merges cleanly.

Probes:
- Two edited copies (planner, triage) and one deleted copy (clerk) in one init → exit 0, `agents=factory-clerk.md`, `stale=factory-planner.md,factory-triage.md`, one stderr line naming each copy and its template, and the "restart the session" line, because a copy was created → OK. The report is not special-cased to the planner.
- A copy truncated to 0 bytes (`factory-stub.md`) → exit 0, listed under `stale_agents`, and still 0 bytes afterwards → OK.
- `FACTORY_STATE` set to a throwaway store, with an edited planner copy → exit 0, `stale_agents= []`. This matches the spec's decision that init run against another store does not read `.claude/agents/` → OK.
- The frontmatter test on a scratch copy of the tree with three extra templates added and no edit to the test. One template had no closing `---`, one had a list as its frontmatter, and one had a quoted description containing `: `. Result: `2 failed, 7 passed`. The failures were `[factory-extra.md]` "frontmatter has no closing ---" and `[factory-list.md]` "frontmatter is not a mapping"; the quoted-colon template passed. → OK. The glob picks up new templates and each failure names its template.
- `.claude/agents/factory-stub.md` replaced by a directory → init exits 1 with `factory: IsADirectoryError`. Before this change, the `exists()` check would have skipped the directory silently. → CONCERN, outside the criteria. The input is unusual and no criterion covers it, so this does not count toward FAILED.

Protected paths this change touches: `agents/**` and `factory/**`. Both are declared in the spec's Risk section.

STATUS: FAILED
CONFIDENCE: high. All eight commands and both gates ran in full on the head. The failure is reproduced by a real merge onto the given base, where the changelog command prints `GAPPED`.
ESCALATIONS:
- The harness gave me base `43a289e` (current `main`), but the implementer's branch was cut from `525d73f`, and T-0053.1 merged in between. Unless this branch is rebased or the entry renumbered before merge, `docs/changelog.md` on `main` will have two entries numbered 73. Neither the gate (`git diff --check main...HEAD` only checks merge-base to HEAD) nor the head-only acceptance command catches this. A human should decide whether the harness rebases a branch onto the current base before review, or whether the implementer reruns on the new base.
- Outside the criteria: `factory init` now crashes (exit 1, `IsADirectoryError`) when a directory sits where an agent copy belongs. Before this change it skipped the directory without error. This is a minor robustness regression, noted for the operator.
