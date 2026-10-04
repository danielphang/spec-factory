Commit: 3bf45779ddee6e0874ba3b1eda5170235ededfc1 (branch `factory/T-0023.4`, base `cf6e2bc6aa19a748648e159c37204dba418b1df8`, which is also `main`)

How I ran it. The PR head is the worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0216-verifier/wt`. For the base I added a detached worktree at `cf6e2bc` under this run's scratch directory, and removed it when I was done. I ran `uv sync --frozen` in both, with `node` on `PATH`. I wrote the parent's GIVEN block to `scratch/given.sh` and diffed it against input.md lines 354-406: identical. I ran it once with `TMPDIR` set to `scratch/tmp`, and it wrote `t0023-parent.sh`, `t0023-closed.sh` and `t0023-wf.mjs` there. I took each WHEN from the sub-ticket into `scratch/cmds.txt` byte for byte, then ran it through the wrapper from the tree's root with that `TMPDIR`: `bash -c "(export HOME=\"\$(cd \"\$(mktemp -d)\" && pwd -P)\"; <WHEN>)"`.

Per criterion:
- NEW | Run records in a store pass whitespace checks and other store files do not | base: `runs=2`, `other=2` | PR: `runs=0`, `other=2` | PASS
- NEW | A run start adds the whitespace rule to an existing store (`t0023-parent.sh`, then `run start --role planner`) | base: `rule=0` | PR: `rule=1` | PASS
- NEW | init refuses to create an instance on a throwaway store and writes nothing | base: `exit=0 instance=written store=written names_state=0` | PR: `exit=2 instance=none store=none names_state=1` | PASS
- NEW | A missing briefing refuses the compose with exit 2 | base: `exit=1 input=none names_context=1` (the uncaught `FileNotFoundError` the spec describes) | PR: `exit=2 input=none names_context=1` | PASS
- NEW | Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory | base: `state=0 instance=0 repo=0` | PR: `state=1 instance=1 repo=1` | PASS
- REGRESSION | An absolute FACTORY_STATE is used as given | base: `absolute=1` (run anyway) | PR: `absolute=1` | PASS
- NEW | The README says relative paths resolve from the caller's directory | base: `0` | PR: `1` | PASS
- NEW | The changelog records the change in order | base: `51 CONTIGUOUS`, `6` (entry 51 already held the three earlier seams' clauses, so 6 is the expected base count for this last seam) | PR: `51 CONTIGUOUS`, `9` | PASS
- NEW | Intermediate check, the new test file passes (`uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_store_setup.py`) | base: `ERROR: file or directory not found: tests/factory/test_store_setup.py`, `no tests ran`, exit 4. That is the expected base failure for a check about a new file, and sibling verifiers on T-0023.2 and T-0023.3 recorded it the same way. To show the tests detect the change, I copied the PR's file into the base worktree and ran it there: `11 failed, 2 passed in 3.24s`. The two that pass are `test_an_existing_rule_is_not_duplicated` and `test_an_absolute_factory_state_is_used_as_given`. Both guard behaviour that base already has. I removed the copy afterwards. | PR: `13 passed in 1.34s`, exit 0 | PASS
- REGRESSION | The harness suite passes with an uncommitted harness edit | base: not run | PR: `254 passed in 244.31s (0:04:04)`. Its own `/tmp/t0023-suite.*` directory was gone afterwards. `/tmp/t0023-suite.g5G5PW` was there before the run and is still there, which matches the implementer's out-of-scope note. | PASS
- REGRESSION | The change adds no whitespace errors (`git diff --check main...HEAD; echo "exit=$?"`) | base: `exit=0` (empty range) | PR: `exit=0` only | PASS

Gate suite: PASS
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `254 passed in 213.48s (0:03:33)`, no failures or errors. The run printed a `uv` warning that the inherited `VIRTUAL_ENV` was ignored in favour of the project's `.venv`, which is harmless.

Probes (each through the wrapper, from the PR worktree, against throwaway directories):
- `FACTORY_STATE=../../st`, run from `$T/a/b` → `"state": ".../$T/st"`. `..` resolves against the caller's directory → OK
- `FACTORY_STATE='~/st'` → `$HOME/st`, under the throwaway HOME. `expanduser` still applies → OK
- `FACTORY_STATE=` (empty) → the fixture instance's own store, the same as unset → OK
- `FACTORY_CWD=$T/a` set by hand, run from `$T` → resolves to `$T/rel`. `bin/factory` line 9 always overwrites it (`export FACTORY_CWD="$PWD"`), so the caller's directory is `$PWD`. This was already true before the change, and it matches the spec → OK
- `init --repo-name demo` with the relative `FACTORY_STATE=.factory/state`, which names the instance's own store → exit 0, `instance.yaml` and `context.md` written, the store's `.gitattributes` holds the rule. The own-store check is not tied to an absolute spelling → OK
- `init --repo-name demo` run from a subdirectory of the target with the relative `FACTORY_STATE=../../elsewhere` → exit 2, neither `.factory` nor the store written. The message names `FACTORY_STATE` and the resolved store → OK
- Whitespace rule scope: a run record nested three levels under `runs/` → `deep_runs=0`. `store/runs.md`, `store/tickets/runs-note.md` and a `runs/` directory at the repo root, outside the store, are all still reported (exit 2). The rule exempts only the store's `runs/` tree, not files with similar names → OK
- `context.md` present as a directory, not a file → compose exit 2 with the refusal, and no `input.md` → OK
- I followed the refusal's advice: deleted `context.md`, then ran `factory init` with `FACTORY_STATE` unset → exit 0, and `context.md` came back from the template. The advice in the message works → OK

Nothing suggests special-casing. The relative-path fix is in the shared resolvers (`instance.env_path`, used by `find`, `repo_root`, `state_root`, `store.state_root` and `init_cmd`), not in `paths`. Inputs I chose myself (`..`, `~`, subdirectories, relative own store) behave the same as the tested ones.

STATUS: VERIFIED
CONFIDENCE: high, every acceptance command and both gates ran verbatim on 3bf4577 and printed the expected output, the NEW ones failed on base for the reasons the spec states, and nine probes beyond the tested inputs behaved correctly.
ESCALATIONS: none
