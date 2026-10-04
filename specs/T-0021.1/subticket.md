## T-0021-S1 / Per-run scratch directory: create, name in the input, preamble rule, ignore, clear on state change, documents
Depends on: none
Parallel-safe: yes (the only sub-ticket; nothing runs beside it)

Parent: T-0021 approved spec v2 (issue #35). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts A, B, C, D, E and F of the parent's design.md, plus the one test edit under its Tests to change. That is the whole parent.

Notes for the implementer, checked on `main` at `a32f90e`:
- Running code. Run the suite, every scenario and every probe through the wrapper, `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`, from the root of your worktree, after `uv sync --frozen`. Run scenario 1 under both bash and zsh, as the parent did.
- Part A. `run_start` is at `factory/cli.py:198`. Today it calls `store.ensure_gitignore(root)` at `:223` (build roles) and `:242` (a tripwire baseline). A third call is at `:856`. The new call must run for every role. Create `scratch/` only after every guard has passed and after `meta.yaml` is written, so that a refused start still writes nothing.
- Part A, `.gitignore`. `STORE_GITIGNORE` and `ensure_gitignore` are at `factory/store.py:49-63`. Today, when any checked line is missing, line 62 appends the whole block again. The parent replaces this: write the full commented block only when the file is absent or empty, and otherwise append only the missing lines. Scenario 5 checks that each line appears exactly once, and that the operator's own `# kept` line survives.
- Part B. The Running code section is built at `factory/compose.py:85-90`. Add the Scratch directory section directly after it, using the text in part B and `root / "runs" / run_id / "scratch"`. Do not add it to `input_sources`.
- Part C. In all three copies, RUNNING CODE begins and GUARDRAIL PATHS follows at these lines: `docs/design.md:208` and `:218`; `docs/prompts/00-preamble.md:40` and `:50`; `factory/prompts/preamble.md:40` and `:50`. Edit `docs/design.md` first and then copy the block to the other two files. Keep the precedence clause `takes precedence over any other instruction to use a session scratchpad` on one line, or scenario 2 prints `0`.
- Part D. `save_ticket` is at `factory/store.py:98`, and `park_ticket` (`:101`) writes through it. The clearing must happen in `save_ticket`, after the write, and only when a stored status existed and changed to something other than `parked`. So `ticket new` (no stored status), `run start` and `run finish` (status unchanged) clear nothing. A run is finished when its `meta.yaml` has a non-null `finished` (set at `factory/cli.py:306`; `run start` writes `finished: None` at `:217`). Remove only directories matching `runs/*/scratch` whose run's `meta.yaml` names this ticket and is finished.
- Part E, design doc. The "Tripwire on live files" paragraph is `docs/design.md:54`. The new "Scratch directory per run" paragraph goes right after it. It is prose, not a prompt block, so no other `docs/prompts/` file changes.
- Part E, changelog. The last numbered entry on `main` is 49 (`docs/changelog.md:53`). Number the new entry 50, or the next free number when you start, and put it before `Declined:`. It must contain `#35`.
- Part E, build spec. The `factory run start` bullet is `dev/build-harness.spec.md:203` and after-run item 6 is `:301`. The text `runs/<run_id>/scratch/` must appear literally.
- Part E, README. The caveat is `README.md:298-300` ("One caveat until #35 lands: …"). The status-header date is on line 9. Read "Maintaining this page" (`README.md:421`) before you edit, and follow its rule for features that have not yet run on a real ticket.
- Part F. Model `tests/factory/test_run_scratch.py` on `tests/factory/test_run_isolation.py`: black-box through `bin/factory` on a throwaway store. The file does not exist yet.
- The store `.gitignore` files of the two instances (`.factory/state/.gitignore` here, and the Nanobot one) are not edited by this PR. The harness rewrites them at the first `run start` after the runtime checkout moves (parent Risk and Operator step 2).

Acceptance (each WHEN verbatim from the parent's `specs/run-scratch/spec.md`, run through the wrapper from the worktree root):
- two runs get separate scratch directories, each named only in its own input. NEW.
  WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; rid(){ sed -E 's/.*"run_id": "([^"]+)".*/\1/'; }; printf '# A\n\nx\n' >$S.a; printf '# B\n\ny\n' >$S.b; bin/factory ticket new --file $S.a >/dev/null; bin/factory ticket new --file $S.b >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | rid); B=$(bin/factory run start --role triage --ticket T-0002 | rid); c(){ bin/factory run compose $1 >/dev/null; echo "$1 dir=$(test -d $S/runs/$1/scratch && echo yes || echo no) heading=$(grep -c '^## Scratch directory$' $S/runs/$1/input.md) own=$(grep -c "$S/runs/$1/scratch" $S/runs/$1/input.md) other=$(grep -c "$S/runs/$2/scratch" $S/runs/$1/input.md)"; }; c $A $B; c $B $A`
  THEN it prints exactly two lines, `run-0001-triage dir=yes heading=1 own=1 other=0` and `run-0002-triage dir=yes heading=1 own=1 other=0`
- a run's system prompt carries the scratch rule. NEW.
  WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | sed -E 's/.*"run_id": "([^"]+)".*/\1/'); grep -c 'takes precedence over any other instruction to use a session scratchpad' $S/runs/$A/system-prompt.txt`
  THEN it prints exactly `1`
- the three copies of the preamble stay identical. REGRESSION.
  WHEN `awk '/^## Shared preamble/{f=1} f&&/^.{3}text$/{p=1;next} p&&/^.{3}$/{exit} p' docs/design.md | diff - docs/prompts/00-preamble.md && diff docs/prompts/00-preamble.md factory/prompts/preamble.md && echo SAME`
  THEN it prints `SAME` and nothing else
- a file in a run's scratch directory is ignored by git. NEW.
  WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | sed -E 's/.*"run_id": "([^"]+)".*/\1/'); mkdir -p $S/runs/$A/scratch; touch $S/runs/$A/scratch/f; git -C $S init -q; echo "untracked_scratch=$(git -C $S status --porcelain --untracked-files=all | grep -c /scratch/)"`
  THEN it prints `untracked_scratch=0`
- an existing store .gitignore gains only the missing line. NEW.
  WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; printf '# kept\nworktrees/\nruns/*/wt/\n' >$S/.gitignore; bin/factory run start --role triage --ticket T-0001 >/dev/null; echo "$(grep -c '^# kept$' $S/.gitignore) $(grep -cxF 'worktrees/' $S/.gitignore) $(grep -cxF 'runs/*/wt/' $S/.gitignore) $(grep -cxF 'runs/*/scratch/' $S/.gitignore)"`
  THEN it prints `1 1 1 1`
- moving a ticket on clears its finished run's scratch and no other ticket's. NEW.
  WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; rid(){ sed -E 's/.*"run_id": "([^"]+)".*/\1/'; }; printf '# A\n\nx\n' >$S.a; printf '# B\n\ny\n' >$S.b; bin/factory ticket new --file $S.a >/dev/null; bin/factory ticket new --file $S.b >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | rid); B=$(bin/factory run start --role triage --ticket T-0002 | rid); for r in $A $B; do mkdir -p $S/runs/$r/scratch; touch $S/runs/$r/scratch/f; done; printf 'Type: bug\nTitle: A\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' >$S.o; bin/factory run finish $A --output-file $S.o >/dev/null; k(){ test -e $S/runs/$1/scratch && echo kept || echo removed; }; echo "after_finish A=$(k $A)"; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; echo "after_move A=$(k $A) B=$(k $B)"`
  THEN it prints `after_finish A=kept` then `after_move A=removed B=kept`
- a parked ticket keeps its run's scratch until a human sends it on. NEW.
  WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | sed -E 's/.*"run_id": "([^"]+)".*/\1/'); mkdir -p $S/runs/$A/scratch; touch $S/runs/$A/scratch/f; printf 'STATUS: NEEDS-HUMAN\nCONFIDENCE: low\nESCALATIONS: none\n' >$S.o; bin/factory run finish $A --output-file $S.o >/dev/null; bin/factory ticket park T-0001 --reason q --outputs $A >/dev/null; k(){ test -e $S/runs/$A/scratch && echo kept || echo removed; }; echo "parked=$(k)"; bin/factory ticket transition T-0001 --to ready-for-triage --by t >/dev/null; echo "resumed=$(k)"`
  THEN it prints `parked=kept` then `resumed=removed`
- the documents carry the change. NEW.
  WHEN `echo "$(grep -c 'One caveat until #35 lands' README.md) $(grep -c '#35' docs/changelog.md) $(grep -c 'runs/<run_id>/scratch/' dev/build-harness.spec.md)"`
  THEN it prints `0 N M` with N of 1 or more and M of 1 or more
- the harness suite passes. REGRESSION.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  THEN it exits 0 and its last line reports no failures
- Intermediate check, a refused `run start` leaves no `runs/` entry. NEW (part F names it; the parent has no scenario for it).
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_run_scratch.py`
  THEN it exits 0, and the file holds a test that makes `run start` refuse (for example a triage run on a ticket not in `ready-for-triage`) and asserts that no new directory appeared under `runs/` and no `scratch/` exists.
- Intermediate check, the edited test keeps its point. REGRESSION.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_tripwire.py -k test_no_tripwire_key_writes_and_prints_what_it_did_before`
  THEN it passes, with the run listing `["meta.yaml", "output.md", "scratch", "system-prompt.txt"]` (still no `tripwire.yaml`) and line 231 asserting that `runs/*/scratch/` is a line of the store's `.gitignore`. No other assertion in that file changes: `git diff main -- tests/factory/test_tripwire.py` touches only lines 230-231.

Tests to change: `tests/factory/test_tripwire.py:230-231`, in `test_no_tripwire_key_writes_and_prints_what_it_did_before`, as the parent lists it.
Protected paths: harness (`factory/cli.py`, `factory/compose.py`, `factory/store.py`, `factory/prompts/preamble.md`); generated (`docs/prompts/00-preamble.md`, re-copied from the design doc block). These are the parent's Risk list. The PR does not edit the infra file `.factory/state/.gitignore` or the reference_harness file `~/dev/nanobot-upstream/.factory/state/.gitignore`.
Out of scope: the build half's worktrees (`worktrees/<ticket>`, `runs/<run id>/wt/`) and where they live; the run-0062 `.venv` case; clearing scratch of runs that never finish; the workflow scripts, routing table, gates and merge rule; setting `TMPDIR` in the running-code wrapper; editing either instance's store `.gitignore`; the operator steps (the prompt acceptance test, committing the regenerated `.gitignore`, the first parallel-intake check).

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v2 of T-0021 (issue #35), in this run's input and at `.factory/state/specs/T-0021.md` with its directory `.factory/state/specs/T-0021/`.

One sub-ticket. The parent sizes the change at about 30 lines of harness code, 30 of prompt text, 30 of documents and 120 of new tests, well under one PR. Splitting would not make review or rollback easier, and some parts cannot land apart without leaving `main` wrong:
- Part A (create `scratch/` and always write the `.gitignore`) breaks the existing test at `tests/factory/test_tripwire.py:230-231` by design. So A and that test edit must land together.
- Parts B and C (the input section and the preamble rule) both tell agents that "the harness clears it when the ticket moves on". Without part D that sentence is false, and scratch would pile up in the store.
- Part E (documents) describes A to D. On its own it would describe behaviour that does not exist, and the README would drop its caveat against parallel intake too early.
Rejected: a separate documents sub-ticket. It would add one more merge for every in-flight sibling to re-verify, for no gain.

I checked the parent's anchors on `main` at `a32f90e`. `git diff --stat d15d833 HEAD -- factory bin tests docs dev README.md` prints nothing, so the parent's line numbers, taken at `d15d833`, still hold.
