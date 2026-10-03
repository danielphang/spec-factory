Commit: f5d820346e2ed3edd2b8d160f280dc02d74d57f1 (branch `factory/T-0012.3`; base 51ea76c94740462b299941d40bf8a431d07ee9ba)

How run:
- PR: in the given worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0067-verifier/wt` (HEAD = f5d8203, `main` = 51ea76c), after `uv sync --frozen` (exit 0).
- Base: a fresh scratch clone of `~/dev/spec-factory`, checked out at 51ea76c with `main` = 51ea76c, after `uv sync --frozen` (exit 0). I used a clone so the old harness, which puts its store next to its own code, could not write into the worktree or the live store. It did write into the clone's `intake/state` (T-0013, log, index, openspec/, decisions.md). That is the "harness_changes=4" failure mode the spec describes.
- Commands: the parent scenarios' WHEN lines and the sub-ticket's intermediate WHEN lines were pulled from the input file by a script, not retyped. Each ran with `bash` from the checkout root, with `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f` (the parent's `parent_base` in `intake/state/tickets/T-0012.yaml`).
- The "no-old-paths, documents and harness" command is the T-0012.2 intermediate grep from `intake/state/specs/T-0012.2/subticket.md:19`, with the pathspec changed to `-- README.md docs dev agents factory`.
- Whitespace: `git diff --check main...HEAD; echo "exit=$?"`, as in the T-0012.2 sub-ticket.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | harness-files-in-repo | `agents=6 green_only=2` | `agents=6 green_only=0` | PASS
- NEW | role-prompt-text-unchanged | `changed=1 of 14` | `changed=0 of 14` | PASS
- NEW | init-creates-instance-in-throwaway-target | `init=2` / `instance=[] agents=0 restart=0` | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` | PASS
- NEW | store-command-from-subdirectory-uses-target-instance | `init=2` / `new=0 tickets=[] harness_changes=4` | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` | PASS
- NEW | command-outside-any-instance-refused | `exit=0 created=0 names_instance=0` | `exit=2 created=0 names_instance=1` | PASS
- NEW | factory-instance-override-from-elsewhere | `init=2` / `found=0` | `init=0` / `found=1` | PASS
- NEW | composed-input-opens-with-instance-context | `init=2` / `first=[]` | `init=0` / `first=[CTX-MARKER for demo]` | PASS
- NEW | run-system-prompt-names-instance | `init=2` / `line1=[] placeholders= protects_instance=` | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` | PASS
- NEW | paths-name-harness-workflows-and-instance | `init=2` / `no paths` | `init=0` / `True True True True` | PASS
- NEW | init-refusals-and-idempotence | `outside_git=2` / `no_name=0` / `again=0 same=yes`, plus four `find: .factory|.claude: No such file or directory` lines | `outside_git=2` / `no_name=2` / `again=0 same=yes` | PASS
  - The criterion as a whole fails on base, through `no_name=0`, so it is not a SPEC-DEFECT. Two of its three parts pass on base for other reasons:
    - `outside_git=2` on base is argparse rejecting `--repo-name`. Confirmed: base prints `factory: error: unrecognized arguments: --repo-name x`, exit 2.
    - `same=yes` is vacuous on base, because nothing was created.
  - I probed the outside-git refusal on the PR directly (probe 1).
- NEW | agent-pointer-replaced | four lines `old=1 new=0` | four lines `old=0 new=1` | PASS
- NEW | workflows-take-instance | `intake 0` / `build 0` | `intake 2` / `build 1` | PASS
  - This check is structural only, as the sub-ticket says. The workflows are not run end to end here; operator step 3 does that after close.
- NEW | no-old-paths, documents and harness | `exit=0` | `exit=1` | PASS
- REGRESSION | harness-history-carried | `0` | `0` | PASS
- REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `70 passed in 75.80s (0:01:15)` | `sync=0` / `92 passed in 74.37s (0:01:14)` | PASS
- REGRESSION | docs-moved-and-split | `old_tracked=0` | `old_tracked=0` | PASS
- REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` | PASS
- REGRESSION | green-harness-still-present | `green keeps its harness` | `green keeps its harness` | PASS
- REGRESSION | whitespace (sub-ticket diff) | `exit=0` | `exit=0` | PASS

Other sub-ticket constraints checked:
- Existing tests are untouched. `git diff --name-status --no-renames 51ea76c HEAD` lists only `A` entries under `tests/`: `conftest.py`, `fixtures/instance/{context.md,instance.yaml}` and `test_instance.py`.
- The imported tests use throwaway stores. `FACTORY_STATE` appears in `test_p0_cli.py` (2), `test_results_commit.py` (2), `test_spec_store.py`, `test_shepherd.py` and `test_subtickets.py` (1 each). `test_killed_checker.py` imports `built_to_implementer` from `.test_shepherd`.
- `cmp factory/prompts/preamble.md docs/prompts/00-preamble.md` reports them identical.
- The diff touches nothing under `docs/`. Under `factory/prompts/`, only `context.md` (deleted) and `preamble.md` change, so the seven role prompts are unchanged.
- No lock enforcement (C.2–C.5) is present. `main()` exempts only `init` and `paths` from the instance refusal, and has no lock comparison.
- `git status --porcelain` in the worktree was empty after all acceptance runs, gates and probes.

Gate suite: PASS
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `92 passed in 72.42s (0:01:12)` and exited 0.

Probes (all on the PR head, in temporary targets):
1. `init --repo-name x` in a non-git temp directory → exit 2. Stderr: `factory init: /private/var/folders/.../tmp.7YbYlClvGG is not inside a git work tree`. The directory stays empty. → OK
2. `init` from a 3-deep subdirectory `a/b/c`, with repo name `odd: "name" #1 {x}`. I then rewrote `protected_paths` to `{infra: [.factory/**], auth: "src/auth/**" (a bare string), dependencies: [uv.lock, pyproject.toml]}` and ran `ticket new` and `run start --role triage`. → OK
   - `instance.yaml` reads back `repo_name` exactly, and `harness` is the worktree's absolute path.
   - `harness.lock` = `f5d820346e2ed3edd2b8d160f280dc02d74d57f1`, which equals `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`.
   - `diff docs/prompts/00-preamble.md <head of system-prompt.txt>` differs only on line 1 (`... pipeline: odd: "name" #1 {x}. Other agents check`) and line 38 (`  infra (.factory/**), auth (src/auth/**), dependencies (uv.lock, pyproject.toml)`).
   - The triage role prompt follows. `run compose` opened `input.md` with that instance's `context.md` (`CTX-ODD`).
   - Nothing is special-cased to `demo`.
3. Edge cases of the override and walk-up. → OK
   - `paths` outside any instance → exit 0, `"instance": null, "state": null`, nothing written.
   - `FACTORY_INSTANCE` pointing at a directory named `other` (not `.factory`) → `state` resolves under the parent of `other`, following the B.2 rule.
   - `FACTORY_INSTANCE` naming a directory with no `instance.yaml` → `ticket show` exits 2 with `... holds no instance.yaml; run factory init --repo-name NAME there, or fix FACTORY_INSTANCE`, and nothing is written.
   - Empty `protected_paths: {}` → the protected-path line renders as `  none`.
   - A second target T2 does not see T1's tickets (`ticket show T-0001` → exit 2 from T2), while T1 still finds its own.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command and both gates ran as written on f5d8203 and gave the expected output. Every NEW criterion failed on base, and probes with non-test inputs (odd repo name, several classes, a bare-string glob, deep subdirectory, a renamed instance directory) behave by the rule, not by the test values.
ESCALATIONS:
- The implementer's own `init` reading (PR gap 1) is not in the spec and needs a human decision. Instance pieces (`context.md`, `harness.lock`, `.claude/agents/`) are written only when the store in use is the instance's own. So `factory init` run with `FACTORY_STATE` exported elsewhere creates only `instance.yaml` and that store. B.5 does not state this. It is not covered by any acceptance criterion, but a human should confirm it at review.
- The B.8 workflows are verified only structurally, as the sub-ticket allows. I read the diff: with `instance` given and no `state`, `STATE` comes from `factory config`'s absolute `state_dir`, and `BIN` carries `FACTORY_INSTANCE`. I did not run them, and their end-to-end behaviour is unproven until operator step 3.
- The implementer's PR discloses that its first baseline run wrote into the worktree's tracked `intake/state` (infra) and then reverted it. The worktree is clean now (`git status --porcelain` is empty), and the live store's tickets end at `T-0012.yaml` with no T-0013. Recorded for the human audit only.
- I did not run `node --check` or any stub run of the workflows. The PR's claim that both pass is unverified by me.
