Sub-ticket: T-0030.1 (ST-1 / A registered agent definition for every role, a file-tool fence on the reviewer and verifier, and `run start --inline`). Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md

What changed: nothing. The branch `factory/T-0030.1` is still at its base, `d226a4d03ca94bab45bd4221972285a4d16ee0bb`, with a clean tree (`git status`: "nothing to commit, working tree clean"). No commits were made and no PR is ready. This retry was blocked at step 2 of the implementer process, the same point as run-0312. The operator's ruling says to stop in that case, so I stopped.

What I did before the block (read only, plus one scratch file):
- Read the role prompt, the input with its Human ruling, and the coding standard (`~/dev/spec-factory-harness/docs/coding.md`). The worktree has no `AGENTS.md`: `find . -name AGENTS.md` printed nothing.
- Read the worktree's `agents/` directory. It holds six files, `factory-clerk.md factory-planner.md factory-spec-critic.md factory-spec-writer.md factory-stub.md factory-triage.md`. None is for the implementer, reviewer or verifier, which matches the spec. Each of the four role files still carries a `ROLE:` copy after its pointer line.
- Found the code part A changes:
  - `run_start` is at `factory/cli.py:197`. The `run start` parser is at `factory/cli.py:1441-1445`, with `--model` and no `--inline`.
  - Each workflow sends `run start` from one line: `factory/workflows/intake.js:88` and `factory/workflows/build.js:79`.
  - The `inlineRoles` comments are at `intake.js:17` and `intake.js:29-31`, and at `build.js:10`.
- Copied the spec's GIVEN block, lines 306-500 of `input.md`, unchanged into `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0318-implementer/scratch/given.sh` (195 lines). Running it was refused; see ESCALATIONS.

Acceptance results: none run. Every NEW and REGRESSION command in this sub-ticket needs the GIVEN fixture files, which were never written because running the block was refused. The gate commands were not run either.

Tests added/changed: none.

Known gaps and uncertainties:
- All of part A (A1 to A5) is still to do. factory: markers added: none.
- The GIVEN block does nothing but write files: eight `cat > ${TMPDIR:-/tmp}/t0030-* <<'EOF'` heredocs, run with `TMPDIR` set to this run's scratch directory. The scripts it writes run later, from acceptance commands. When they run, they use stub agents and work on scratch stores and scratch target repos. I read the block and found nothing in it that writes outside a temporary directory, but I did not run it.

Out-of-scope observations:
- The input asks the implementer to read `AGENTS.md`, but this repository has none. The README's "Maintaining this page" section seems to be the nearest equivalent.

STATUS: BLOCKED
CONFIDENCE: high, because nothing in the repository changed and both refusals are quoted below.
ESCALATIONS:
- Claude Code's auto-mode permission check refused this run again with the reason "Code from External". The operator's ruling of 2026-10-07 covers this case: stop, change nothing further, and report the refused command. The refused commands:
  1. Writing the spec's fixture files by running the GIVEN block from the scratch directory. The exact command: `S=/Users/dphang/dev/spec-factory/.factory/store/runs/run-0318-implementer/scratch; (export HOME="$(cd "$(mktemp -d)" && pwd -P)"; export TMPDIR=$S/tmp; sh $S/given.sh) && ls $S/tmp`. The reason given was "[Code from External]".
  2. Sent in the same batch and refused with the same reason: a read-only check in the worktree, `ls -d .venv; which node uv python3`.
  Without the first command, the role's process cannot start: every acceptance command runs the fixtures that block writes. To unblock this run, the operator can add a permission rule that allows the following:
  - running `sh` on a script under `/Users/dphang/dev/spec-factory/.factory/store/runs/*/scratch/`;
  - running `node` and `.venv/bin/python` on the fixtures that script writes;
  - running the gate suite, `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, in the worktree.
  The operator can then send T-0030.1 back to the implementer unchanged. The base, branch and sub-ticket are all still valid.
