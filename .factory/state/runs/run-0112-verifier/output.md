Commit: 01f7524f35d3939caa31f56e35cd9de5884b6034 (the merge of factory/T-0013.1 into `main`. `main` in `~/dev/spec-factory` points at this SHA, so this parent-close run verifies `main`.)
Base: 0759162e21900c35ecf653e3df7fbe622a30abbd (the operator's gate approval, which comes before the first merge for T-0013)

How I ran it. Head was the given worktree `.factory/state/runs/run-0112-verifier/wt`, at HEAD = 01f7524 with a clean tree. For the base I made a `git clone --shared` of the repo in my scratchpad, checked out 0759162, and set a local `main` there. I ran `uv sync --frozen` in each tree. I then ran every WHEN command verbatim on both trees from one script and copied the results below from its output. I have since deleted the scratch clones. The worktree's `git status --porcelain` is empty.

Per criterion:
| Kind | Scenario (command as written in the spec) | Base 0759162 | Head 01f7524 | Result |
|---|---|---|---|---|
| NEW | standard-is-one-page-with-a-pair-per-rule | `missing` | `lines=86 rules=8 before=8 after=8` | PASS |
| NEW | preamble-names-the-standard | `standard=[] unfilled=0 file=absent` | `standard=[/Users/dphang/dev/spec-factory/.factory/state/runs/run-0112-verifier/wt/docs/writing.md] unfilled=0 file=present` | PASS |
| NEW | preamble-line-in-every-copy | `:0` ×3 | `:1` ×3 (design.md, 00-preamble.md, factory/prompts/preamble.md) | PASS |
| NEW | briefing-template-has-reader-line | `0` | `1` | PASS |
| NEW | rubric-6-widened-in-every-copy | first three `:1`, last three `:0` | first three `:0`, last three `:1` | PASS |
| NEW | reviewer-check-in-every-copy | `:0` ×3 | `:1` ×3 | PASS |
| REGRESSION | prompt-copies-verbatim | 3× `verbatim`, `preamble copies equal`, `critic-diff=2 reviewer-diff=2` | same output | PASS |
| NEW | records-name-the-standard | `changelog=0 design=0 buildspec=0 stale=1 row=0` | `changelog=1 design=2 buildspec=1 stale=0 row=1` | PASS |
| REGRESSION | gates-pass | `check=0`, `121 passed` | `check=0`, `126 passed` | PASS |

Every base result matches what `verification.md` predicts. Each NEW criterion fails on base for the reason the spec states: the file, line or text is missing. None fails because of its setup. The preamble-names-the-standard run started on base too and printed the stated `standard=[] … file=absent`.

Gate suite: PASS. I ran both commands from the worktree exactly as written:
- `git diff --check main...HEAD` exited 0. On this run that check is empty: HEAD equals `main`, so `main...HEAD` holds no commits. For evidence that covers the change, I also ran `git diff --check 0759162 HEAD`, which exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `126 passed in 87.26s`. The count rose by 5 from base's 121: the new file adds 2 tests plus 1 test run on 3 inputs.

Spec conformance beyond the commands. I read the diff 0759162..01f7524 (15 files) and checked it against `design.md` parts A to F:
- The OUTPUT lines of the preamble, rubric 6, reviewer check 8 and the briefing bullet match the spec's text exactly. So do both edits at `docs/design.md:54` and the one-sentence change to `dev/build-harness.spec.md`.
- `fill_preamble` (`factory/instance.py:166`) adds one line: `text.replace("{writing standard}", str(HARNESS / "docs" / "writing.md"))`, with the docstring updated. `HARNESS_PATHS` (`factory/instance.py:31`) is unchanged, as the Decisions require.
- The edit to `tests/factory/test_instance.py` is the one listed under Tests to change. It adds the excluded index `w` and asserts the content of the filled line. It extends the final check to `{writing standard}`. No assertion is removed or loosened.
- The README has only the two specified edits. Its status-header date is already 2026-10-03.
- Changelog entry 43 was added. The diff touches nothing under `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml` or `uv.lock`.
- `docs/writing.md` follows part A: a reader model, a scope sentence, then 8 rules in the requested order, each with a "Check:" line, a sourced Before and an After. It closes with one line naming the README.
- I confirmed that the run-output Befores are real text. `Order and parallelism:` appears in run-0054-planner/output.md, `old_tracked=0` in run-0052-spec_writer/output.md, the A3 "whole word `none` (word boundary)" escalation in run-0014-triage/output.md (line 68) and "Stale branch base, which is a harness/process issue" in run-0062-verifier/output.md (line 50). As the spec allows, rules 1–3 use the operator's review findings as their Befores. I could not check those against a file, because the overview draft is not in this repository.

Probes:
- Run the harness through a symlinked path that contains a space: a head clone at `/tmp/…/scratchpad/head copy`, where `/tmp` links to `/private/tmp`, started with a triage run as in the scenario. Result: the prompt names `/private/tmp/…/head copy/docs/writing.md`, that file exists, `unfilled=0`, and no other `{…}` placeholder is left. So the path is the resolved path of the checkout that actually ran, not a fixed or worktree-specific value. → OK
- Call `fill_preamble` directly with three configs: no `protected_paths`, a `protected_paths` map, and a `repo_name` that is literally `{writing standard}`. Result: none leaves the placeholder unfilled, and filling twice gives the same text. → OK. Filling `{repo name}` first means a repo with that literal name would also get the path, which is harmless.
- Build the system prompt for every role (triage, spec_writer, critic, planner, implementer, reviewer, verifier) by the same steps `factory/cli.py:218-219` uses. Result: each names the standard's absolute path once, with 0 unfilled. Only triage could go through `run start` here; for the other roles the ticket's state refused the start, as designed. → OK

Not verified (by design): whether a live critic flags an unglossed term in an Evidence paragraph. That is Operator step 3, after the upgrade.

STATUS: VERIFIED
CONFIDENCE: high. All 9 scenarios ran verbatim on base and head with the predicted results, both gate commands passed, and the probes show the fill follows the running checkout and is not tied to the tested path.
ESCALATIONS:
- Gate check `git diff --check main...HEAD` (the whitespace check over the change) is always empty on a parent-close run. The verifier runs on `main` itself, so `main...HEAD` holds no commits and the check passes without testing anything. Here I covered it with `git diff --check 0759162 HEAD`, which exited 0. Decide whether the parent-close gate should use the pre-merge base instead of `main`.
