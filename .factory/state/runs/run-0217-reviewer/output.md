Commit: 3bf45779ddee6e0874ba3b1eda5170235ededfc1 (branch `factory/T-0023.4`, base `cf6e2bc6aa19a748648e159c37204dba418b1df8`, one commit)

## Checks, in order

1. Test integrity: `git diff cf6e2bc6 HEAD --name-only | grep ^tests/` lists only the new file `tests/factory/test_store_setup.py` (187 lines added). No existing test changed, skipped, weakened or deleted. The new file's assertions are specific (exact file contents, exact `written` order, exact exit codes and message fragments, `Traceback` absent). Sub-ticket says "Tests to change: none"; honoured.
2. Correctness, part by part, read against the parent's design.md steps:
   - C1 (`factory/store.py:63-77`): `STORE_GITATTRIBUTES` is one `#` comment plus `runs/** -whitespace`; `ensure_gitattributes` goes through `_ensure_block`, which is the old body of `ensure_gitignore` parametrised on path and block. Absent/empty file gets the block; an existing file keeps its lines and gains only missing non-comment lines. Semantics of `ensure_gitignore` unchanged (same code, same `STORE_GITIGNORE`).
   - C2 (`factory/cli.py:222`, `:889`): called beside the `run_start` `ensure_gitignore` at `:221`, which is after every refusal in `run_start` (refusals end at `:210`, `next_run_id` at `:211`). In `init_cmd`, `.gitattributes` is inserted at index 0 after `.gitignore` is, so `written` reads `[".gitattributes", ".gitignore", ...]` when both were absent, as the test asserts. `_start_build_run:243` still calls only `ensure_gitignore`; the spec asks for the `:222` site only, and the `run_start` call runs after `_start_build_run` on the same `root`, so every started run gets the rule.
   - E1 (`factory/cli.py:862-868`): the refusal sits before `_revision()` and before the first `store.write_text`, so nothing is written. It builds the config in memory from `_new_instance_yaml`, computes the store with the same `instance.state_root` the rest of the command uses, and tests it with the existing `instance.is_own_store` (`factory/instance.py:105`). Message matches the spec text; `CONFIG_NAME` is `instance.yaml` (`instance.py:38`). When `instance.yaml` already exists the branch is skipped, so `test_instance.py:166-176` keeps passing (suite confirms).
   - E2 (`factory/compose.py:85-88`): `store.Refused` raised before `parts` is built; `run_compose` writes `input.md` only on return, so no input is written (scenario confirms `input=none`). Exit 2 is `Refused`'s code.
   - F1/F2 (`factory/instance.py:45-52`, `:57`, `:82`, `:99`; `factory/store.py:38`; `factory/cli.py:857`): `env_path` returns None for unset or empty, `expanduser()` first, joins a relative path onto `caller_cwd()`, `.resolve()`. The five raw reads named in the sub-ticket notes are all replaced; `grep -rn "os\." factory/cli.py factory/store.py` finds no remaining `os.environ` read, so the dropped `import os` in both files is correct. `not_found_message` is untouched. Absolute values take the same `.resolve()` path as before (REGRESSION scenario passes).
   - Edge cases: `FACTORY_REPO` set with `FACTORY_STATE` unset at `init` makes own store `FACTORY_REPO/.factory/state` on both sides of `is_own_store`, so the instance is created, as before. `FACTORY_CWD` unset with a relative value falls back to `os.getcwd()`, which is what the spec says ("`FACTORY_CWD`, else the working directory").
3. Scope: `README.md:204-205` adds one sentence beyond J3's verbatim text ("`FACTORY_STATE` names a store to use instead, and `FACTORY_REPO` a repo root."). It is in the same paragraph J3 edits, is accurate (the README's only earlier `FACTORY_STATE` mention is at `:222`, further down), glosses two names J3's sentence uses, and the PR description declares it. Not a finding. Status-header date at `README.md:9` already reads 2026-10-04 (J4). Changelog edit is the S3 clause appended to line 51 only. Nothing else outside parts C, E, F, J1, J3, J4.
4. Silent behavior changes: an existing store's first `init` or `run start` after the runtime moves gains a `.gitattributes` and, for `init`, one more `store.initialised` log event listing it. Both are what the parent asks for (Risk, part C). No other caller-visible change found; `tests/factory/test_spec_store.py:151` (second `init` writes nothing) still holds in the suite.
5. Security and data safety: no new destructive op, no secrets, no injection surface. `_ensure_block` only appends to a file inside the store. The refusal paths write nothing. Tests write only under `tmp_path`, the fixture instance (read-only), and the worktree's own `bin/factory`.
6. Protected paths: `factory/cli.py`, `factory/store.py`, `factory/instance.py`, `factory/compose.py`, all four declared in the sub-ticket's "Protected paths" line. Listed under ESCALATIONS; merge gate needs a human approval.
7. Coding standard: rule 1 honoured by `_ensure_block` (rung 1, an existing pattern reused rather than copied) and by reusing `is_own_store`, `caller_cwd`, `state_root` and `Refused`. Rule 2: the PR description names every caller of the five changed functions and the fix sits in the shared resolvers. Rule 3: no shortcut with a known limit; "factory: markers added: none" stated. Rule 5: `.gitattributes`, store, instance, briefing keep the names the README uses. Rule 6 not applicable (no path patched, no new outside path). Lean already.
8. PR description: What changed says in words what each part does and glosses store, instance and run record on first use; Known gaps name the two judgment calls and the one state left as before (a refused compose leaves the run `running`, same as the old crash). Readable by the operator at the gate. No finding.

## What I ran (all from the worktree root, through the wrapper, HOME fresh; GIVEN block written once with `TMPDIR` set to this run's scratch directory)

| Scenario | Printed | Expected |
|---|---|---|
| Run records in a store pass whitespace checks and other store files do not | `runs=0`, `other=2` | same |
| A run start adds the whitespace rule to an existing store | `rule=1` | same |
| init refuses to create an instance on a throwaway store and writes nothing | `exit=2 instance=none store=none names_state=1` | same |
| A missing briefing refuses the compose with exit 2 | `exit=2 input=none names_context=1` | same |
| Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory | `state=1 instance=1 repo=1` | same |
| An absolute FACTORY_STATE is used as given | `absolute=1` | same |
| The README says relative paths resolve from the caller's directory | `1` | same |
| The changelog records the change in order | `51 CONTIGUOUS`, `9` | same |
| Intermediate check, the new test file passes | `13 passed in 3.28s`, exit 0 | exit 0 |
| The harness suite passes with an uncommitted harness edit | `254 passed in 228.69s (0:03:48)` | passed, no failed/error |
| The change adds no whitespace errors | `exit=0`, no other output | same |

Gates: `git diff --check main...HEAD` printed nothing, exit 0 (`main` is at the base `cf6e2bc6`). `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `254 passed in 219.44s (0:03:39)`: the full suite, including the 13 new cases, passes on this head.

The refusal texts I saw on stderr: `factory init: <tgt>/.factory has no instance.yaml, and FACTORY_STATE names another store (<s>); create the instance with FACTORY_STATE unset, then init that store` and `<tgt>/.factory/context.md is missing: it is the role-context block every role reads first; run factory init with FACTORY_STATE unset to create it from the template`. Both match the spec's wording in E1 and E2.

I could not run `ruff` (no `.venv/bin/ruff` in the worktree); the PR's `All checks passed!` claim is unverified by me. Ruff is not a gate here.

## Findings

None.

Prior findings: none (round 1).

## Out-of-scope observations

- `tests/factory/test_store_setup.py:101` `test_a_relative_factory_instance_resolves_from_the_callers_directory` takes `tmp_path` and does not use it. Harmless.
- The PR's own out-of-scope note stands: relative `--file`/`--output`/`--answer` arguments still resolve against the harness checkout (`factory/cli.py:60` and the sites it lists). Same class as H7, not in this ticket.

STATUS: APPROVE
CONFIDENCE: high, every acceptance scenario, both gates and the uncommitted-edit suite scenario were run by me on `3bf4577` and printed the expected output; the diff was read line by line against parts C, E and F.
ESCALATIONS: protected harness paths touched, all declared by the sub-ticket: `factory/cli.py`, `factory/store.py`, `factory/instance.py`, `factory/compose.py`. The merge gate needs a human approval for them; the code itself earns APPROVE.
