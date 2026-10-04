Commit: 302f70bb99f5c4518ddb94de12db22653aa57385 (branch `factory/T-0012.6`). Base: f4be7ec826121021c2c247fba9ae56db68e658e9, which is also `main`.

How I ran it:
- **PR:** in the given worktree (`.../run-0092-verifier/wt`). `git status --porcelain` was empty before and after every run.
- **Base:** in a scratch `git clone --no-local` of `~/dev/spec-factory`, detached at f4be7ec. In that clone `main` is also f4be7ec.
- **Commands:** I put every acceptance command into one bash script, pasted verbatim from the sub-ticket and the parent spec. Each section starts with `uv sync --frozen`.
- **Environment:** `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `VIRTUAL_ENV` unset.
- **BASE:** `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, the `parent_base` at `intake/state/tickets/T-0012.yaml:74`, for the parent scenarios.
- **Subshell:** records-moved-as-pure-renames reassigns `BASE=$(git merge-base main HEAD)`, so I ran it verbatim inside a subshell. That kept the reassignment from leaking into the parent scenarios that run after it.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | intake-holds-only-live-store | `left=168` | `left=0` | PASS
- NEW | pilot-store-and-answers-kept-byte-identical | `kept=0 of 135` | `kept=135 of 135` | PASS. The two numbers are equal, which is the THEN's condition. The spec says 134, but that count was taken at `f082708`. `git diff --name-status f082708 cdb1c67 -- intake/green-pilot intake/answers` shows one added file, `A intake/answers/T-0012-gate-edit.md`. Distinct contents: f082708 = 134, cdb1c67 = 135. So the count drifted; it is not a defect.
- NEW | instance-b-opens-every-ticket | `tickets=0 failed=0` | `tickets=18 failed=0` | PASS
- NEW | instance-b-config | `no instance config` / `context=` | `True True True` / `context=3` | PASS
- NEW | readme-has-install-and-layout | 5 lines (`missing: git clone`, `uv sync`, `factory init`, `factory paths`, `.factory/`), then `checked` | `checked` | PASS
- NEW | no-old-paths-in-live-files | `exit=1` | `exit=1` | **SPEC-DEFECT**. This NEW criterion passes on both base and PR. At this base, T-0012.2 and T-0012.5 have already cleaned `README.md`, `docs/` and `dev/`, and `.factory/instance.yaml` and `.factory/context.md` do not exist yet. Over those two new files the check is therefore vacuous on base. It is a guard on this sub-ticket, and should have been labelled REGRESSION, as live-store-untouched was. Probe 1 shows the guard is substantive on the PR.
- NEW | lock-is-base-revision | `head: .factory/harness.lock: No such file or directory` / `lock=stale` / `harness_paths_changed=0` | `lock=current` / `harness_paths_changed=0` | PASS
- NEW | instance-b-keys | `FileNotFoundError: … '.factory/instance.yaml'`, then `TypeError: expected str … not NoneType` (paths gives `instance: null`) | `False [] intake/state True` / `True True` | PASS
- NEW | records-moved-as-pure-renames | `0` / `pilot=0 of 148 answers=0 of 14` | `0` / `pilot=148 of 148 answers=14 of 14` | PASS
- REGRESSION | live-store-untouched | `0` | `0` | PASS
- REGRESSION | role-prompt-text-unchanged | `changed=0 of 14` | `changed=0 of 14` | PASS
- REGRESSION | harness-files-in-repo | `agents=6 green_only=0` | `agents=6 green_only=0` | PASS
- REGRESSION | harness-history-carried | `0` | `0` | PASS
- REGRESSION | docs-moved-and-split | `old_tracked=0` | `old_tracked=0` | PASS
- REGRESSION | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | same | PASS
- REGRESSION | design-text-kept | `0` | `0` | PASS
- REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | same | PASS
- REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `116 passed in 82.15s` | `sync=0` / `116 passed in 88.65s` | PASS
- REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS
- REGRESSION | whitespace (sub-ticket diff) `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS

Gate suite: PASS. Both commands were run from the worktree, exactly as written.
- `git diff --check main...HEAD` exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` exited 0, with `116 passed in 80.65s`.
- `git status --porcelain` was empty afterwards. The suite did not touch `.factory/` or `intake/state/`.

Probes (in a scratch clone of 302f70b, after `uv sync --frozen`):
- **Guard bites on the new files.** I replaced `.factory/instance.yaml` with `main:intake/instance/config.yaml` and re-ran the no-old-paths grep. It printed `exit=0` and matched `.factory/instance.yaml:2` (`intake/setup.sh`), `:3` (`HARNESS_PIN`) and `:9` (`generated: ["prompts/**"]`). Appending `` see `prompts/` `` to `.factory/context.md` also matched (`exit=0`). → OK. The check works on the PR; only its NEW label is wrong.
- **Walk-up from a subdirectory.** `cd docs && ../bin/factory ticket show T-0012` exited 0. `bin/factory paths` from `docs/prompts` gives `instance=<clone>/.factory`, `state=<clone>/intake/state` and `harness_revision=010d1b00c5835c7022a72771c63f63f8b6ab3707`, which equals `.factory/harness.lock` (40 hex plus `\n`, 1 line). → OK. The instance is found by the walk-up, so the result does not depend on running from the repo root.
- **The lock is enforced on instance B's own store.**
  - An all-zero `.factory/harness.lock` makes `bin/factory ticket show T-0012` exit 2: `harness 010d1b0… is not the revision this instance accepted (0000…); rerun with --accept-harness 010d1b0… to accept it`.
  - The lock with no trailing newline exits 0.
  - With `# local edit` appended to `factory/__init__.py`, `bin/factory --accept-harness <rev> ticket show T-0012` exits 2: `harness <clone> has uncommitted changes:` / `factory/__init__.py`.
  - → OK. So `tickets=18 failed=0` passed a real lock check.
- **Instance B's config drives the run.** I added a probe ticket (`ticket new` → T-0013 in the clone's store), then ran `run start --role triage`. The resulting `system-prompt.txt` starts with line 1 `You are one agent in a software pipeline: spec-factory (the design repo at ~/dev/spec-factory, branch main). Other agents check`. Its line 38 is `infra (.factory/**, intake/**), harness (factory/**, bin/factory, agents/**, pyproject.toml, uv.lock), generated (docs/prompts/**), reference_harness (~/dev/nanobot-upstream/**), credentials (~/.nanobot/**)`, and it has 0 placeholders left. `run compose` produced an `input.md` whose opening bytes equal `.factory/context.md` byte for byte. → OK.
- **The moves are byte-identical renames.**
  - `git diff -M100% --name-status main...HEAD` over the moved directories gives 162 × `R100`.
  - `git ls-tree -r main -- intake/green-pilot intake/answers`, with the prefix stripped, is identical to `git ls-tree -r HEAD -- .factory/green-pilot .factory/answers` (mode, blob and path).
  - The rest of the diff is 3 A (`.factory/README.md`, `context.md`, `harness.lock`), 5 D (`intake/HARNESS_PIN`, `README.md`, `instance/context.md`, `instance/preamble.md`, `setup.sh`), 1 M (`README.md`), and 1 R062 (`intake/instance/config.yaml` → `.factory/instance.yaml`).
  - → OK. Nothing outside the sub-ticket's file list changed.
- **instance.yaml key diff against the old config** (yaml parsed). Only these keys changed: `repo_name`, `harness` (added), `state_dir` (`../state` → `intake/state`), `protected_paths`, `gate_commands` (the pytest line added), and `request_dir` (removed). `environment_files` was already `[]`. Key order is otherwise preserved. → OK, matches E.1.

STATUS: SPEC-DEFECT
CONFIDENCE: high. I ran every acceptance and gate command on both base and PR myself, and the probes show the change works beyond the tested inputs. The only problem is that one NEW criterion is mislabelled.
ESCALATIONS:
- **SPEC-DEFECT: no-old-paths-in-live-files is labelled NEW but prints `exit=1` on base f4be7ec and on the PR.** Base is clean because the files it guards were cleaned by T-0012.2 and T-0012.5 or did not exist yet. Suggested fix: relabel it REGRESSION, as the operator did for live-store-untouched. Probe 1 shows the substance holds on the PR. Apart from this label, every criterion behaves as specified, and both gates pass.
- **Parent close will fail whitespace-clean, but not because of this branch.** `git diff --check cdb1c67 HEAD` exits 2 on the PR, and it exits 2 on f4be7ec too. All 29 flagged files are under `intake/state/` (store run records such as `runs/run-0057-verifier/`). None is outside the store. This needs an operator or spec decision before parent close.
- **Note on README wording.** `README.md`, under "How updates work", says each target "refuses uncommitted edits to the harness's code, until you run a command with `--accept-harness <sha>`". The harness correctly refuses a dirty runtime even with `--accept-harness` (probe 3, per C.4). The sentence mirrors E.6's own phrasing. Its meaning is still wrong: `--accept-harness` does not clear the dirty refusal. This does not affect any criterion.
