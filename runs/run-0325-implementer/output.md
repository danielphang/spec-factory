Sub-ticket: T-0034.1 (parent T-0034, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0034/v2.md`)
Branch: `factory/T-0034.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0034.1`, one commit `f25dffe` on base `2e73dbb`.

## What changed

The spec writer and the critic now carry rules that cut how many turns they take and how much they print. The critic is also told to run no test suite and build nothing. Two agent roles are involved. The spec writer is the agent that investigates a request and writes its spec. The critic is the agent that reviews that spec before a human approves it. Each role prompt exists in three copies: a block in the design document (`docs/design.md`), its documented copy under `docs/prompts/`, and the run copy under `factory/prompts/`, which the harness gives the agent. Every change is added lines only.

- **A. Spec writer.** A new `- Turn economy:` RULES bullet goes directly after `  wrong just to get approved.` in all three copies (`docs/design.md` after line 371; `docs/prompts/02-spec-writer.md` and `factory/prompts/spec_writer.md` after line 58). The text is the spec's seven lines verbatim. In the run copy it sits before the blank line and the run copy's extra "Acceptance items describe behaviour" bullet.
- **B. Critic.** The spec's twelve lines go directly after `Spot-check at least 2 cited paths and 1 acceptance command yourself.` in all three copies (`docs/design.md` after line 468 once A has shifted it; `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md` after line 42). They come before the blank line that precedes `ANTI-GOODHARTING (REVIEWER SIDE)`. The existing minimum spot-check line is kept.
- **C. Nothing else in the prompts.** No other file under `docs/prompts/`, `factory/prompts/` or `agents/` changed, and no existing prompt line changed. The REGRESSION check below confirms both.
- **D.1 `docs/changelog.md`.** Entry 58 is added on one line after entry 57 and before `Declined:`. It uses the spec's text verbatim.
- **D.2 `docs/principles.md`, principle 2.** The "Implemented by" sentence now ends `…(#41, `factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`).` The status line is replaced with the spec's text. Both are rewrapped to the file's width.

The insertions in A and B were made by a script under the run's scratch directory (`scratch/edit.py`). The script asserts that each anchor line appears exactly once and at the expected line number. D was edited by hand.

## Acceptance results

All commands were run from the worktree under a fresh HOME, using `zsh`. The NEW items were run before the change (on `2e73dbb`) and after it (on `f25dffe`).

| Scenario | Kind | Before (`2e73dbb`) | After (`f25dffe`) |
|---|---|---|---|
| Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule | NEW | `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged` / `critic copy=SAME doc=0/6 run=0/6 fill=unchanged` | `spec_writer copy=SAME doc=4/4 run=4/4 fill=unchanged` / `critic copy=SAME doc=6/6 run=6/6 fill=unchanged` |
| Spec writer and critic run prompts carry the new rules | NEW | `spec_writer batch=0 writes=0` / `critic batch=0 suite=0 cap=0` | `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 cap=1` (the same under `sh`) |
| Rubric, round limit, format and every other prompt are unchanged | REGRESSION | not run | `sections_changed=0 removed=0 others=0` |
| The changelog and the principles page record the change | NEW | `CONTIGUOUS` / `0` / `implemented=0 status=0` | `CONTIGUOUS` / `5` / `implemented=1 status=1` |
| The turn-economy change adds no whitespace errors | REGRESSION | not run | `exit=0` |

Every "before" output matched what `verification.md` predicted, so the spec matched reality before the change.

What the "after" outputs show:
- `copy=SAME`: each design block is still byte-identical to its `docs/prompts/` copy.
- `doc=4/4` and `doc=6/6`, with the matching `run=` counts: every rule phrase is present in both the documented copy and the run copy.
- `fill=unchanged`: each run copy differs from its documented copy exactly as it did on `main`.
- `batch=1 writes=1` and `batch=1 suite=1 cap=1`: the system prompt that `run start` writes for a spec writer run, and for a critic run, contains the new rules.
- `sections_changed=0 removed=0 others=0`: the protected sections are byte for byte as on `main`, no line was removed, and no other prompt file changed.
- `CONTIGUOUS` and `5`: the changelog numbering has no gap, and its last entry holds all five required phrases.
- `implemented=1 status=1`: principle 2 names the critic's rule and the new status.

Gate commands, run exactly as written:
- `git diff --check main...HEAD` exited 0 with no output: the diff adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `364 passed in 225.80s`. The tests that keep each design block equal to its `docs/prompts/` copy are part of that run.

## Tests added/changed

None. The spec's "Tests to change" is none. The scenarios check the text of the prompts directly, and the existing block-equality tests already cover the three copies staying in step.

## Known gaps and uncertainties

- Whether the rules actually halve the writer's turns, and keep spec quality, is not checked here. That is the operator's replay in Operator steps 1–2 (run the intake on a few approved tickets with the old and the new prompts, then compare), which needs live model runs.
- In `docs/principles.md`, two rewrapped lines are 102 and 101 columns wide (lines 44 and 46). The file already has lines from 101 to 112 columns (for example lines 12 and 26), and the spec asks for "about 100".
- factory: markers added: none.
- Protected paths touched, all declared in the spec's Risk section: `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`.

## Out-of-scope observations

- The `agents/factory-spec-critic.md` and `agents/factory-spec-writer.md` templates still hold old prompt bodies, as `verification.md` already notes. They are left untouched; T-0030 replaces those bodies.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high — every acceptance scenario printed its expected output on `f25dffe`, every NEW one printed its predicted failure on `2e73dbb`, and both gates passed (`364 passed`).
ESCALATIONS: none
