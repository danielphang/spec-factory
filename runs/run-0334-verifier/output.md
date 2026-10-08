Commit: 9a87c3e3983a8dd04c7e21f9dd6fdfe99dfe5a41

Verified in the worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0334-verifier/wt` (branch `factory/T-0035.1`, clean, one commit over base). Base runs used a fresh clone of the repo checked out at `49ea4c7646475a00adee963e1e806302a3eed18c` under this run's scratch directory (`scratch/base`), with `main` also at `49ea4c7`. Every command ran through the throwaway-HOME wrapper, with bash, after `uv sync --frozen` in each checkout. The seven WHEN commands were extracted with sed from the pinned spec `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0035/v2.md` (lines 122-170, the `specs/harness-docs/spec.md` section), not from the PR description.

Per criterion:

- NEW | Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules | base: `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` then `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged` (fails as verification.md states) | PR: `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` then `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged` | PASS
- NEW | A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban | base: `spec_writer batch=1 writes=1` then `critic batch=1 suite=1 scratch=0 cap=1 build=1` (fails as stated) | PR: `spec_writer batch=1 writes=1` then `critic batch=1 suite=1 scratch=1 cap=0 build=0` | PASS
- REGRESSION | The writer prompt is as #73 left it, and only the critic's PROCESS changes | base: not run (passed on the PR) | PR: `sections_changed=0 writer=0 others=0` | PASS
- NEW | Principle 2 names the critic's no-suite rule and no longer its build ban | base: `CONTIGUOUS` then `entries73=1 implemented=0 builds=1 status=1` (fails as stated) | PR: `CONTIGUOUS` then `entries73=1 implemented=1 builds=0 status=1` | PASS
- NEW | The changelog records the revert as its last entry | base: `CONTIGUOUS` then `1` (fails as stated) | PR: `CONTIGUOUS` then `7` | PASS
- NEW | The Spiking section allows a small scratch check and records the replay | base: `bound=1 nobuild=1 scratch=0 whole=0 replay=0` (fails as stated) | PR: `bound=0 nobuild=0 scratch=1 whole=1 replay=1` | PASS
- REGRESSION | The critic revert adds no whitespace errors | base: not run (passed on the PR) | PR: `exit=0` | PASS

Every NEW command fails on base for exactly the reason verification.md gives and prints its THEN line exactly on the PR. Every command exited 0 on both checkouts.

Gate suite: PASS
- `(export HOME=...; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `364 passed in 218.74s (0:03:38)`, exit 0 (run twice; the first run also printed `364 passed in 229.98s`, its exit code was lost to a shell quirk in my capture, so I re-ran it with a direct capture).

Probes (the scenarios count phrases; these check the actual text):

- The PROCESS block (from the line after `PROCESS` to the line before `Turn economy:`) in `docs/design.md`'s "## 3. Spec critic" block, `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`, compared byte for byte with the spec's eight-line part A fence → all three `EQUAL`; the three files' `main...HEAD` hunks have the same md5 → OK
- The Spiking paragraph (after its heading and blank line, to end of file) compared byte for byte with the spec's part C fence → `EQUAL`; file ends with a newline (`0a`) → OK
- Changelog entry 59 compared byte for byte with the spec's part D line → `EQUAL`; it is line 63, after entry 58 (line 62), with `Declined:` still after it (line 65) → OK
- The `Turn economy:` paragraph in both prompt copies, compared with `main` → `EQUAL` in both; `diff factory/prompts/critic.md docs/prompts/03-spec-critic.md` shows only the pre-existing line 75 `round 2` / `round {2}` difference → OK
- `git grep -nE "build nothing|builds nothing|Ground any one claim|no clone, worktree|two paths, one command|at most 2 paths|does not build" -- . ':!docs/changelog.md'` → no match (exit 1) → OK
- `git diff --stat 05cf8f9 main -- docs/design.md docs/prompts factory/prompts` → empty, so "unchanged from #73" and "unchanged from main" are the same check for the writer; `git diff --name-only main...HEAD` → exactly the five files the spec names; no `agents/`, `README.md` or test file in the diff → OK

The change is a text replacement, so there is no input-space to probe beyond the text itself; none of the above shows the change fitted to the scenario's phrase lists rather than to the spec's wording.

Protected paths touched, both declared in the spec's Risk list: `factory/prompts/critic.md` (harness), `docs/prompts/03-spec-critic.md` (generated; the diff shows it equal to the design block, which is how it is meant to change).

Out-of-scope observations:
- None beyond the PR description's own note that the worktree has no `AGENTS.md`.

STATUS: VERIFIED
CONFIDENCE: high. All seven acceptance commands print their THEN lines on the PR head and the five NEW ones fail on base exactly as the spec predicts; both gates pass with exit 0; the replaced text is byte-identical to the spec in every copy.
ESCALATIONS: none
