Sub-ticket: T-0043.1 (ST-1 of T-0043, spec v2). Branch `factory/T-0043.1`, commit `e375b16` on base `5215c5f`, in worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0043.1`.

## What changed

Part A, all in `factory/cost.py`. This is a protected path, and the sub-ticket declares it.

- **Each model call is counted once.** Claude Code writes one transcript record for each streamed block of a reply, and every one of those records carries the whole call's usage. The new `transcript_usage(path) -> (calls, ctx, out)` keeps the last usage seen for each `message.id`. A record with no id counts on its own. `calls` is now the number of message ids kept. `tally()` now gets its numbers from `transcript_usage()`, so the `python -m factory.cost` table has the same header, columns and arguments as before, but each figure counts every call once.
- **Module docstring.** It now explains the once-per-message-id count and names the three new readers.
- **`match_transcripts(dirs, stores) -> {(store, run_id): path}`** searches every `*.jsonl` file at any depth under `dirs`. For each file, the first user message that names `<P>/runs/<R>/` gives the candidate. A message that starts with `[Workflow harness — user request]` is skipped. The file stops being read at that message. A transcript is a candidate for run R of store S when:
  - its first timestamp lies between R's `started` and `finished`, and
  - P is not the path of another store given.

  Among the candidates, one whose P is S's path, or S's path before a `store.migrated` event (`from`/`to` read from S's log), wins. Otherwise a single remaining candidate is taken. Otherwise the run gets no transcript.
- **`gate_failures(transcript, input_md) -> int | None`** reads the gate commands, the check commands listed in the run's input. They are the backticked strings after "Gate commands" on that line of `input.md`. Each command is matched by its own text: what follows the wrapper's last `; `, with the closing `)` removed. A gate counts once when a Bash call containing it returned `is_error: true` and a later call containing it returned no error. The function returns None when the input has no "Gate commands" line.
- **Small refactor in the same file.** The user-text extraction in `_role()` moved into `_user_text()`, which `_opening()` also uses (coding rule 1: reuse the existing pattern).
- **Callers** (coding rule 2), found with `grep -rnE "tally|_role\(|factory\.cost|import cost" factory bin agents tests README.md docs dev`: no caller exists outside `factory/cost.py` (the hits in `factory/drive.py` are its unrelated `run_role`). `tally()`'s only caller is `cost.main()`.

Part D (ST-1's share): the new file `tests/factory/test_cost_once.py`.

## Acceptance results

The fixture's setup block (the GIVEN block of "Runs and verdicts are counted per role and model, ...") was copied verbatim from `input.md` lines 304-374 to `scratch/given.sh`, then run once through the wrapper.

- NEW, "The transcript cost report counts each message once": `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')`
  - Before, on `5215c5f`: `| critic | fable-5 | 1 | 5 | 725 | 33 |`, as the spec says.
  - After, on `e375b16`: `| critic | fable-5 | 1 | 2 | 310 | 17 |`, as expected.
- NEW (intermediate check): `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_cost_once.py`
  - Before the change: `11 failed in 0.10s`. Each failed on a missing attribute, except the table test, which failed on `calls` being 2.
  - After: `11 passed in 2.27s`.
- REGRESSION (intermediate check), which is also the second gate: `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `557 passed in 379.20s (0:06:19)`, exit 0.
- Gate `git diff --check main...HEAD`: exit 0, no output.

Every command ran through the briefing's wrapper. The wrapper gives each command a fresh temporary HOME, so nothing can write the real home directory.

Extra check, not a criterion. `scratch/sanity.py` runs the new functions on the fixture and, read-only, on the two live stores with `~/.claude/projects`:
- **Fixture:** it matches s1 runs 0003 (spec writer), 0004 (critic) and 0008 (implementer), and s2's run-0001-triage, with usages `(1, 100100, 500)`, `(2, 310, 17)`, `(1, 60, 4)` and `(1, 10, 2)`. `gate_failures` on run 0008 gives 1. These are the inputs behind ST-2's section A and D expected rows.
- **Live stores:** matching takes 10.1 s. It places a transcript on 630 of the 631 finished runs started before 2026-10-07T12:00, and `gate_failures` gives 1 for the Nanobot store's `run-0384-implementer`. Both agree with the spec's Evidence.

## Tests added/changed

`tests/factory/test_cost_once.py` is new. It has 11 tests:
- **Counting:** `tally()` and `transcript_usage()` with repeated message ids and with records that have no id; and the `python -m factory.cost` table through `cost.main()`, with the header unchanged and one call per id.
- **Matching:**
  - S's own path wins over another candidate;
  - S's path before a `store.migrated` counts as its own;
  - the relay message is skipped;
  - another given store's path rules a transcript out, while the same transcript with that store alone is the single remaining candidate;
  - a first timestamp before `started` or after `finished` matches nothing;
  - a single remaining candidate is taken, two are not, and the search reaches nested directories.
- **Gate failures:** a failure fixed later counts once; a failure never fixed counts 0, and the worktree path before "Gate commands" is not treated as a gate; an input with no gate line returns None.

The tests load `factory/cost.py` from its file with `importlib`, as `tests/factory/test_subtickets.py` loads `factory/subtickets.py`, because `tests/factory` is itself a package named `factory`. No existing test changed.

## Known gaps and uncertainties

- **Several candidates on S's own path.** Two such transcripts arise when a role spawns a sub-agent whose prompt names its run directory. The earliest first timestamp is taken. The spec does not say how to choose. A `factory:` marker records this at the choice (`factory/cost.py`, in `match_transcripts`).
- **Another store's old path also rules a transcript out.** I treated "the path of another store" as covering that store's path before a `store.migrated`. The spec's wording names only the current path.
- **A run in flight** (`finished` null) has no upper bound on its window. Every ST-2 table leaves such runs out, so this only matters to direct callers.
- **One transcript can be placed on two runs.** A transcript whose P matches no given store can be the single remaining candidate for the same run id in two stores whose runs overlap in time. Nothing in the spec prevents it. The live-store check above shows no sign of it, though it was not checked for directly.
- **Gate lines.** `gate_failures` reads only the first line containing "Gate commands", and returns None, not 0, when that line holds no backticked command. A line saying "none (every gate command is skipped below)" is therefore "not recorded".
- **`cost.py` reads YAML with `yaml.safe_load` directly, not `factory/store.py`'s `read_yaml()`.** Importing `store` would make `cost.py` load only as part of the `factory` package. The tests load it from its file, as above. PyYAML is already a dependency.
- **`tally()` reads each transcript twice:** once in `transcript_usage()` and once in `_model()`. This keeps `transcript_usage()`'s signature exactly as the spec gives it.
- factory: markers added: one, in `match_transcripts` (the earliest-transcript choice above).

## Out-of-scope observations

- `README.md:109` still describes `factory/cost.py` correctly. Documents are ST-3's.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The NEW criterion and the 11 new tests pass, and so does the full suite (557 passed). The new functions reproduce the spec's evidence on the live stores (630 of 631 matched, run-0384's gate fix found).
ESCALATIONS: none
