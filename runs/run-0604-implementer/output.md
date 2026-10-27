Sub-ticket: T-0060.1, `/Users/dphang/dev/spec-factory/.factory/store/tickets/T-0060.1.yaml`. Parent: T-0060, spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0060/v2.md`.
Branch: `factory/T-0060.1`. Head: `37c867e6881221552f4b86efe47fcbb04fabd929`, one commit on base `9e8f4d3`.

## What changed

This change adds the method for the upstream benchmark and a command that computes one of its measures. The upstream benchmark gives the same real Nanobot bug reports to the factory and to one plain Claude Code session, then scores each fix by that pull request's own tests. Before this change nothing wrote down how to run it fairly. Nothing could compute operator time either: the operator's attention, derived from timestamps.

**A. `factory/benchmark.py`, run as `python -m factory.benchmark [--store PATH] [SESSION.jsonl]...`.** A new module of 107 lines. It reads the session transcripts and the store's event log it is given, and writes nothing. It prints a seven-row Markdown table:
- operator messages;
- gate and ruling events, meaning the store's `approval.recorded` and `human.resolved` events;
- operator time in sittings;
- elapsed hours;
- session tokens.

It reuses `factory.cost`'s `_records`, `_log_records`, `_user_text`, `_when` and `transcript_usage`, and takes the decision events from `factory.stats.DECISIONS`. It copies none of them. Refusals exit 2 with one stderr line starting `factory.benchmark: ` and nothing on stdout. Each refusal is checked before anything is printed:
- no `--store` and no session;
- a session that is not a file, named in the message;
- a store with no `log/` directory, named in the message.

**B. `tests/factory/test_benchmark.py`, a new file with 11 tests.** These parts of the operator-message rule are covered: `typed`, `queued` and `suggestion_accepted` count, as do a text-block prompt and an older record with no `promptSource`. A `tool_result` does not count, with or without `promptSource`. Nor do `isMeta`, `isSidechain`, `system`, `sdk`, a no-source record starting with `<`, or an unparseable line. The tests also cover these:
- the 900 s boundary: exactly 900 s stays in one sitting, and 901 s starts a new one;
- the one-minute addition;
- store events outside `DECISIONS`, which are not interactions but count for elapsed time;
- a session message and a store decision sharing one sitting;
- a message id repeated across records, counted once;
- `-` for elapsed time when nothing has a timestamp;
- the three refusals.

The tests run the module as a subprocess from the checkout root. `tests/factory` is itself a package named `factory`, so `factory.benchmark` cannot be imported by name in-process.

**C. `docs/benchmark.md`, a new page.** It has the eight `##` sections the spec names, in order. Each quoted phrase that acceptance reads sits on one line. It links `north-star.md`, `reviews/TEMPLATE.md` and `../README.md`.

**D. README.** It grows by one net line, from 1,224 to 1,225, filling its budget. "Where things live" gains the spec's `docs/benchmark.md` row, verbatim, after the `STATUS.md`, `docs/reviews/` row. In "What depends on Claude Code", the `factory/cost.py` row is reworded in place to the spec's text, verbatim. The status header's date is already 2026-10-26, today's date, so it is unchanged. If the merge happens on a later day, that date needs bumping at merge.

## Acceptance results

Each WHEN ran verbatim under `bash`, through the briefing's wrapper, from the worktree, after the spec's GIVEN block and `uv sync --frozen`. Scratch copies: `scratch/given.sh`, `scratch/whens.txt`, `scratch/run_acc.sh`. Outputs are in `scratch/before.txt` and `scratch/after.txt`.

| Scenario | Kind | Before (base `9e8f4d3`) | After (`37c867e`) |
|---|---|---|---|
| A plain session's transcript gives its operator messages, operator time, elapsed time and tokens | NEW | `…/.venv/bin/python: No module named factory.benchmark`, `exit=1` | `\| measure \| value \|`, `\|---\|---\|`, `\| operator messages \| 3 \|`, `\| gate and ruling events \| 0 \|`, `\| operator time, minutes \| 17.0 (2 sittings) \|`, `\| elapsed, hours \| 0.68 \|`, `\| session tokens \| 3150 context, 60 output \|`, `exit=0`: matches the THEN exactly |
| A factory arm's store events and runner session give one operator time | NEW | `No module named factory.benchmark`, `exit=1` | `operator messages \| 2`, `gate and ruling events \| 2`, `operator time, minutes \| 3.5 (3 sittings)`, `elapsed, hours \| 3.08`, `session tokens \| 1130 context, 12 output`, `exit=0`, under the same two header lines: matches the THEN exactly |
| The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing | NEW | `none=1+msg missing=1+msg nolog=1+msg store=unchanged` | `none=2+msg missing=2+msg nolog=2+msg store=unchanged`: matches |
| The suite passes and no existing test file is modified or deleted | REGRESSION | not run before, per the process | `669 passed in 115.95s (0:01:55)`, with nothing after it, so the `git diff --diff-filter=MD … -- tests` lists no file: matches |
| The benchmark page has its eight sections in order | NEW | `exit=2` | the eight headings in order, then `exit=0`: matches |
| The benchmark page states its selection, blinding, setup, measures, review and spend rules | NEW | `caveat=no selection=no blind=no arms=no measures=no review=no spend=no` | `caveat=yes selection=yes blind=yes arms=yes measures=yes review=yes spend=yes`: matches |
| No relative link in the benchmark page is broken | NEW | `docs/benchmark.md missing` | `relative=some broken=0`: matches |
| README names the benchmark page and puts its report in the cost row | NEW | `where=0 depends=0 shared=0` | `where=1 depends=1 shared=1`: matches |

Every "before" output matched verification.md's "Today" line. The first two differ only in the checkout path that the venv's Python prints.

The gates ran on `37c867e`, each exactly as written:
- `git diff --check main...HEAD` printed nothing and exited 0, so no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `669 passed in 119.01s (0:01:59)` and exited 0.
- `bin/factory truth check --store … --skip-when-contains '…'` printed `347 scenarios: 306 passed, 0 failed, 41 skipped; wall time 128 s` and exited 0. That includes `PASS harness-docs: README is at most 1,225 lines` at 1,225 lines, and `PASS harness-docs: Where things live has a row for each new file`. This change's own seven scenarios were SKIPPED there, "in the approved delta of T-0060, which that ticket's verifier checks". That is why I ran them myself, as the table above shows.

## Tests added/changed

- Added: `tests/factory/test_benchmark.py`, 11 tests, which cover design part B as listed under "What changed". Before the module existed, all 11 failed, because the subprocess could not find `factory.benchmark`. After, all 11 pass.
- Changed: none. The parent's "Tests to change" is none.

## Known gaps and uncertainties

- **The baseline's operator decisions need one hand subtraction.** The page takes this measure as "the operator messages after the first", as design part C.6 specifies. The report prints all operator messages, so a reviewer must subtract one by hand. That sits uneasily with the page's rule that "No number is typed or adjusted". I followed the spec and did not add a row the spec does not define. A reviewer could fix it with a later row such as "operator messages after the first", or by pasting the raw count and stating the rule.
- **`factory.cli` is imported indirectly.** `benchmark.py` does not import `factory.cli`, as the spec requires. But `from factory.stats import DECISIONS` loads `factory.stats`, which imports `factory.cli` for `ROLES` (`factory/stats.py:25`). So the module still loads `cli` at import. I followed the spec's instruction to take `DECISIONS` from `factory.stats` rather than copy it.
- **The module is 107 lines, not "about 90".** The docstring states the full counting rule, and the refusals and table rows are written one per line.
- **A bad timestamp is not caught.** A record or event with a timestamp that `datetime.fromisoformat` cannot parse raises `ValueError`, giving a traceback and exit 1. I left this uncaught rather than skip the record silently. Claude Code and the store both write ISO timestamps.
- **Sittings are always plural.** The output prints `1 sittings`, keeping the spec's `<s> sittings` format literally.
- **Upstream's URL and test command are not verified or named.** The page names upstream as `https://github.com/HKUDS/nanobot`, from the spec's `gh pr list --repo HKUDS/nanobot`. I did not fetch it. The page defines "upstream's test command" as the one upstream's CI configuration runs at that commit, without naming a command. I did not read upstream's CI.
- **The factory arm's procedure is untried.** Following the spec's Risk, its first trial is the first benchmark task.
- **Only `bash` was used.** I ran every scenario under bash, the shell the truth check replays with. I did not re-run under zsh, which the spec writer also did.
- **`factory:` markers added:** none.

## Out-of-scope observations

- The process says to read `AGENTS.md`, but this repository has none, at the worktree root or at `~/dev/spec-factory`. I worked from the briefing, the spec, `docs/coding.md` and `docs/writing.md`.
- Gate 3 printed `folded: T-0060` when run from this worktree, yet skipped T-0060's scenarios as "in the approved delta". That is consistent with how the gate treats an open ticket's delta. It does mean the gate itself never checks this change's scenarios before the ticket's verifier runs.

## Protected paths

`factory/benchmark.py`, declared in the parent's Risk. The change also adds `tests/factory/test_benchmark.py` as a new file, as part B specifies. No existing test file changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All eight acceptance commands print their THEN lines exactly, and the suite and the truth check pass on the commit. The one design tension, the hand subtraction for the baseline's decisions, comes from the spec and is disclosed above.
ESCALATIONS: none
