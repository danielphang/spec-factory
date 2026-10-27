Commit: 37c867e6881221552f4b86efe47fcbb04fabd929 (branch `factory/T-0060.1`, base 9e8f4d3c14d352bf058b1532814d5ff83b6dd14e)

Environment: the PR is the given worktree, which was clean at the head. The base is a `git archive` of 9e8f4d3 unpacked into `scratch/base` and given a one-commit git repo. Both ran `uv sync --frozen` through the wrapper. I extracted the spec's GIVEN block verbatim from input.md lines 239–264 into `scratch/given.sh` and ran it once, which wrote `$TMPDIR/t0060-fixture.sh`. I copied each WHEN verbatim into `scratch/whens.sh` and ran it from each checkout's root through the briefing's wrapper, under both bash and zsh. Within each checkout the bash and zsh outputs were identical (`diff` reported no difference). Outputs are in `scratch/acc-{pr,base}-{bash,zsh}.txt`.

Per criterion:

| Kind | Scenario (command) | Base 9e8f4d3 | PR 37c867e | Result |
|---|---|---|---|---|
| NEW | A plain session's transcript gives its operator messages, operator time, elapsed time and tokens | `…/scratch/base/.venv/bin/python: No module named factory.benchmark`, `exit=1` (the spec's "Today", apart from the venv path) | `\| measure \| value \|`, `\|---\|---\|`, `\| operator messages \| 3 \|`, `\| gate and ruling events \| 0 \|`, `\| operator time, minutes \| 17.0 (2 sittings) \|`, `\| elapsed, hours \| 0.68 \|`, `\| session tokens \| 3150 context, 60 output \|`, `exit=0`, which is exactly the THEN | PASS |
| NEW | A factory arm's store events and runner session give one operator time | `No module named factory.benchmark`, `exit=1` | the two header lines, then `\| operator messages \| 2 \|`, `\| gate and ruling events \| 2 \|`, `\| operator time, minutes \| 3.5 (3 sittings) \|`, `\| elapsed, hours \| 3.08 \|`, `\| session tokens \| 1130 context, 12 output \|`, `exit=0`, which is exactly the THEN | PASS |
| NEW | The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing | `none=1+msg missing=1+msg nolog=1+msg store=unchanged` | `none=2+msg missing=2+msg nolog=2+msg store=unchanged` | PASS |
| REGRESSION | The suite passes and no existing test file is modified or deleted | not run (it passed on the PR) | `669 passed in 153.80s (0:02:33)`, and nothing after it | PASS, with one deviation, below |
| NEW | The benchmark page has its eight sections in order | `exit=2` | the eight headings in the spec's order, then `exit=0` | PASS |
| NEW | The benchmark page states its selection, blinding, setup, measures, review and spend rules | `caveat=no selection=no blind=no arms=no measures=no review=no spend=no` | `caveat=yes selection=yes blind=yes arms=yes measures=yes review=yes spend=yes` | PASS |
| NEW | No relative link in the benchmark page is broken | `docs/benchmark.md missing` | `relative=some broken=0` | PASS |
| NEW | README names the benchmark page and puts its report in the cost row | `where=0 depends=0 shared=0` | `where=1 depends=1 shared=1` | PASS |

Each NEW criterion fails on base for the reason verification.md gives and passes on the PR. So none is a SPEC-DEFECT.

The suite scenario could not run exactly as written. Claude Code's built-in safety check refused its `rm -rf "$P"`, because `P` comes from a command substitution. Following the check's own advice, I ran `mktemp -d /tmp/t0060-suite.XXXXXX` on its own, which printed `/tmp/t0060-suite.9SetU7`. I then ran the WHEN with `P=/tmp/t0060-suite.9SetU7` in place of the substitution and without the `rm`, and removed that literal directory afterwards. Everything else in the WHEN ran verbatim: `TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1`, then `git diff --name-only --diff-filter=MD main...HEAD -- tests`. The `git diff` printed nothing, so no existing test file was modified or deleted. Only the cleanup step changed, and cleanup cannot affect what the scenario checks.

Gate suite: PASS
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `669 passed in 124.91s (0:02:04)` and exited 0.
- `/Users/dphang/dev/spec-factory/bin/factory truth check --store … --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'` printed `347 scenarios: 306 passed, 0 failed, 41 skipped; wall time 141 s` and exited 0. That run includes `PASS harness-docs: README is at most 1,225 lines`, and `wc -l README.md` gives 1225. The README diff is exactly design part D: one row added after the `STATUS.md`, `docs/reviews/` row, and the `factory/cost.py` row reworded in place, both verbatim.

Probes (fixtures in `scratch/probe/`, each run through the wrapper as `.venv/bin/python -m factory.benchmark …`):
- A store-only run, plus a mixed run with a `suggestion_accepted` message at 10:00:00Z. The store holds a zoneless `ts` 10:15:00 (exactly 900 s later), a decision at 10:30:01+00:00 (901 s after that) and an unparseable line. Results: mixed → `17.0 (2 sittings)`, elapsed `0.50`, `gate and ruling events | 2`. Store only → `2.0 (2 sittings)`. Both are correct by hand: 15+1 and 1 minutes, and the 900/901 s boundary holds across session and store. A zoneless store timestamp is read as UTC. The garbage line is skipped. → OK
- A transcript with no timestamps at all (`0.0 (0 sittings)`, elapsed `-`), and a store with an empty `log/` (same output, exit 0). A directory given as SESSION → `factory.benchmark: not a file: …`, exit 2. → OK
- A 20,000-record transcript runs in 0.11 s and gives a hand-checked `1439.0 (1 sittings)`. A user record with empty text and no `promptSource` counts as an operator message, which is literally what the rule says. → OK
- A `user` record with no `message` key, or with `"message": null`, crashes the report: `KeyError: 'message'` and `TypeError: 'NoneType' object is not subscriptable`, both at `factory/benchmark.py:35` (`content = o["message"]["content"]`), with exit 1 and a traceback. `factory.cost._user_text` tolerates such a record; `_operator_message` then indexes it directly. → CONCERN. No stated criterion covers it, and Claude Code's real user records carry `message`, so this is not a FAIL.
- Passing the same transcript twice double-counts. `base.jsonl base.jsonl` gives tokens `6300 context, 120 output`, because `transcript_usage` deduplicates message ids within one file and the report sums across files. Operator time is unchanged (`17.0 (2 sittings)`). This follows design part A ("the sum of `transcript_usage` over the sessions"). It is an operator-error case, not a criterion breach. → CONCERN, minor

Nothing in the code is special-cased to the fixture's inputs. The counting rule, the 900 s gap and the 60 s addition are constants applied generally (`factory/benchmark.py:26-53`), and the probes above with new inputs gave hand-checkable answers. The page's caveat text (`docs/benchmark.md:173-178`) names the three gaps of Answer 2 that design C.6 requires.

STATUS: VERIFIED
CONFIDENCE: high. All eight acceptance commands and all three gates were run on the head and printed their THEN lines, and every NEW command failed on base as verification.md states. The one deviation is the suite scenario's `rm` cleanup, which a safety check blocked, and it does not affect what that scenario checks.
ESCALATIONS:
- `python -m factory.benchmark` exits 1 with a traceback on a `user` record whose `message` is missing or null (`factory/benchmark.py:35`). This is outside the criteria and harmless on real Claude Code transcripts, but it is not a clean refusal. It may be worth a later fix: guard with `(o.get("message") or {}).get("content")`.
- The suite scenario's WHEN ends with `rm -rf "$P"` on a command-substitution variable. Claude Code's safety check blocks that line, so an agent cannot run the scenario verbatim. The gate's own replay skips this scenario, so the gate is unaffected. A later spec that reuses the T-0023 pattern may want a form that agents can run, such as removing a fixed directory under `/tmp`.
