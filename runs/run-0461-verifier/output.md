Commit: 3478d1fddf4b207fdf0a04ba34ae5459ec11968c (branch `factory/T-0045.1`; base 2b9baf506852d6f74124b1f5eadbdd84f6bad52b, which is also `main`)

Where things ran: the PR runs were in the verifier worktree `wt/`, at HEAD 3478d1f. The base runs were in `scratch/base`, a `--no-checkout` clone of the worktree, detached at 2b9baf5, with a local `main` at 2b9baf5 and `.venv` symlinked to the worktree's. Every command went through the fresh-HOME wrapper. The worktree had no `.venv` at the start. The `uv run --frozen` suite gate created it, and the acceptance commands' `.venv/bin/python` then used it. The plan says to run the checks "from `~/dev/spec-factory`", but there HEAD is `main`, so the merge-base pair is empty and nothing would be compared. I ran them from the worktree, whose HEAD is the PR, as the implementer did.

Per criterion:
- NEW | "Only the duplicate test and its assertions are gone" (parent spec command, as written) | base: `pair: 0`, `removed: 0`, `added: 0`, `missing: 0` | PR: `pair: 1`, `removed: 1`, then exactly `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`, `added: 0`, `missing: 2`, then `missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert cp.returncode == 0 and js(cp)['status'] == 'KILLED'` and `missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert yaml.safe_load((store / 'runs' / rid / 'meta.yaml').read_text())['status'`. tar printed `Failed to set default locale` twice on stderr, as the spec expects. | PASS
- NEW | "The suite is shorter" | base: `pairs: 0; test lines before: 0, after: 0, change: 0` | PR: `pairs: 1; test lines before: 9710, after: 9583, change: -127` | PASS
- NEW | "A suite run in a fresh clone passes and adds nothing to the checkout" | base: `577 passed in 408.16s (0:06:48)`, then `paths changed: 13`, which are `./factory/__pycache__` and 12 `.pyc` files in it (`__init__`, `cli`, `compose`, `cost`, `drive`, `gitops`, `instance`, `specstore`, `status`, `store`, `subtickets`, `tripwire`) | PR: `576 passed in 496.20s (0:08:16)`, then `paths changed: 0`, with nothing after it. 576 is the expected count: no other ticket has added tests since 2b9baf5. | PASS
- NEW (intermediate) | "The shared constants and wrappers are defined once" | base: `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1` | PR: `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=2 approved_parent=1`, the interim value the sub-ticket expects | PASS

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 608.65s (0:10:08)`, exit 0. Afterwards, `git status --short --ignored` in the worktree showed only `.venv/` and `tests/factory/__pycache__/`. There was no `factory/__pycache__`.

Probes:
- Did every changed file keep its old helper behaviour? I compared ASTs over every function and class in `tests/factory/*.py`, base against PR, with docstrings stripped. The result was 0 changed bodies. The only definitions gone are the 30 helper copies (`run`, `js`, `ticket`, `cli`, `tree`) and `test_run_finish_without_output_is_killed`. The only new ones are in `_cli.py`. This covers the four design-block tests and T-0044's two lines in `test_instance.py`. → OK
- Was each file's form of `js` and `run` matched to its old copy? Every base copy of `js` that asserted exit 0 is now imported as `js_ok as js`: `test_redispatch_rows`, `test_replan`, `test_resolve_rulings`, `test_store_setup`, `test_subtickets` and `test_superseded_plan`. Every copy that did not assert imports plain `js`. The two environment-dict `run` copies import `run_env as run`. `test_p0_cli`'s `stdin` form maps to the shared `run`, which has `stdin=None`. → OK
- Was the bytecode guard fixed only for the full-suite path? I ran `test_cost_once.py`, `test_subtickets.py` and `test_role_inputs.py` alone, in a fresh `git archive` of each revision. These are the in-process `importlib` loads and the `without_evidence` subprocess. Both revisions had `21 passed`. On base they wrote 7 `.pyc` files under `factory/__pycache__`. On the PR they wrote none outside `tests/factory/__pycache__`. → OK
- How do the shared helpers handle edge inputs? Called in-process from `tests.factory._cli`:
  - `js` takes the last non-blank line, even with noise and a trailing blank line;
  - `js` on a non-zero exit parses without asserting;
  - `js_ok` on exit 2 raises `AssertionError('boom')`, with stderr as the message;
  - `js` on empty stdout raises `IndexError`, as the old copies did;
  - `ticket(d)` reads T-0001, and `ticket(d, "T-0002")` reads T-0002;
  - `run` and `run_env` both reach `bin/factory` (`--help` exits 0).
  
  → OK
- `STRIP` is wider in five files: `test_coding_standard`, `test_harness_lock`, `test_store_setup`, `test_turn_economy` and `test_writing_standard`. They now also strip `FACTORY_DISPATCH`, the dispatcher's marker that lets a write through while runs are in flight. None of the five sets or reads it. The suite passes, and the PR description discloses the change. → OK. This is a small change to those tests' environment, not a broken criterion.

Out-of-scope observations:
- The suite gate took 608.65s, longer than a 10-minute foreground tool timeout. My foreground call timed out at 600s, and I collected the run's result from its log after it finished with exit 0. The two fresh-clone runs took 6:48 on base and 8:16 on the PR. As the implementer noted, the runtime is close to that limit on this machine (load average 6 to 10 during the run).
- The plan's "run every command below from `~/dev/spec-factory`" does not suit the two comparison scenarios before merge. There HEAD is `main`, so they compare nothing. They give the intended result only from the PR branch's checkout.

STATUS: VERIFIED
CONFIDENCE: high. All four NEW criteria failed on base and passed on the PR as specified, both gates passed on 3478d1f, and the probes found no special-casing and no changed test or helper bodies.
ESCALATIONS: none
