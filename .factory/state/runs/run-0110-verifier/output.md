Commit: e703c1bfb1216079f802ba25e3d3a218246f385d (branch `factory/T-0013.1`; verified in `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0110-verifier/wt`, checked out detached at that SHA because the branch is held by the implementer's worktree; `git status --short` empty before and after). Base 0759162e21900c35ecf653e3df7fbe622a30abbd, which equals `main` (`git rev-parse main` and `git merge-base main HEAD` both print it).

How run: every WHEN was pasted verbatim into one scratch script and run from the worktree root on the head, then again with the worktree checked out detached at the base, then the worktree was put back on the head. The verbatim one-liners for preamble-names-the-standard and prompt-copies-verbatim were copied unchanged from the sub-ticket.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | standard-is-one-page-with-a-pair-per-rule | `missing` | `lines=86 rules=8 before=8 after=8` | PASS
- NEW | preamble-names-the-standard | `standard=[] unfilled=0 file=absent` | `standard=[/Users/dphang/dev/spec-factory/.factory/state/runs/run-0110-verifier/wt/docs/writing.md] unfilled=0 file=present` (that path is the checkout it ran in) | PASS
- NEW | preamble-line-in-every-copy | `docs/design.md:0`, `docs/prompts/00-preamble.md:0`, `factory/prompts/preamble.md:0` | `:1` for all three | PASS
- NEW | briefing-template-has-reader-line | `0` | `1` | PASS
- NEW | rubric-6-widened-in-every-copy | first three `:1`, last three `:0` | first three `:0`, last three `:1` | PASS
- NEW | reviewer-check-in-every-copy | `:0` ×3 | `:1` ×3 | PASS
- REGRESSION | prompt-copies-verbatim | `00-preamble verbatim`, `03-spec-critic verbatim`, `06-code-reviewer verbatim`, `preamble copies equal`, `critic-diff=2 reviewer-diff=2` | identical output | PASS
- NEW | records-name-the-standard | `changelog=0 design=0 buildspec=0 stale=1 row=0` | `changelog=1 design=2 buildspec=1 stale=0 row=1` | PASS
- REGRESSION | gates-pass | `check=0`, `121 passed in 92.84s` | `check=0`, `126 passed in 110.68s` | PASS

Every NEW criterion fails on base for the reason the spec's verification.md states. The two REGRESSION criteria pass on both. On base, `git diff --check main...HEAD` is trivially empty because HEAD equals main there.

Gate suite: PASS. From the worktree on the head, `git diff --check main...HEAD` exited 0. `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `126 passed in 110.68s`. It ran in a fresh environment: uv printed `Creating virtual environment at: .venv` and ignored the inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`. The suite covered this tree: `tests/factory/test_writing_standard.py` exists only on the head, and the count rose by its 5 tests (121 on base to 126).

Diff scope: `git diff --stat 0759162...HEAD` lists 15 files. All of them appear in the sub-ticket's declared paths. No file under `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml` or `uv.lock` changed.

Probes:
- Harness copy at a path containing a space (`.../v0110/harness copy`, from `git archive HEAD`), with the preamble-names-the-standard one-liner run from it → `standard=[.../harness copy/docs/writing.md] unfilled=0 file=present` → OK.
- The same harness reached through a symlink (`hlink/bin/factory`), with the run started from a subdirectory of the target (`$T/sub/dir`) → the system prompt's line 53 names the real resolved path (`.../harness copy/docs/writing.md`), and `ls` shows that file exists (5918 bytes). The path follows the running checkout, not the cwd or the invocation path → OK.
- Mutation test in the scratch copy: delete the `text.replace("{writing standard}", …)` line from `fill_preamble` → `test_system_prompt_names_the_running_checkouts_standard` and `test_no_writing_standard_placeholder_is_left_unfilled` fail. The changed `test_instance.py` test, run on a committed copy of the mutation so the dirty-harness refusal does not apply, fails on its new assertion (`tests/factory/test_instance.py:282`, `'person reads...ndard}. Those' == 'person reads...ing.md. Those'`). Separately, removing `docs/writing.md` makes `test_system_prompt_names_the_running_checkouts_standard` fail → OK. The tests catch both a missing fill and a missing file, and nothing is hard-coded to the test inputs. Both mutations were reverted, and the scratch copy was deleted.
- Code-path check: `factory/cli.py:218-219` is the only place a system prompt is built, and it is shared by every role. `grep -rn '{writing standard}' factory/ agents/` finds the placeholder only in `factory/prompts/preamble.md:53` and in `factory/instance.py` (the docstring and the replace call). So no role file carries an unfilled copy → OK.
- Before sources in `docs/writing.md` checked against the store. The rule 5 quote is in `run-0052-spec_writer/output.md:55`, rule 6 in `run-0014-triage/output.md:68`, rule 7 in `run-0062-verifier/output.md:50`, and the rule 4 and rule 8 descriptions match `run-0054-planner/output.md:3-12`. All are real. Rules 1 to 3 cite the operator's overview draft, which is not in the repo, so I could not check them → OK, with one minor CONCERN in the next item.
- Rule 4's After says ".6 merges last". `run-0054-planner/output.md:17-18` says T-0012.5 can run in parallel with .6, and that .6 is the last sub-ticket that may touch harness paths. So ".6 merges last" overstates the source a little. The caption ("Part E (.6) is the last change to harness code") is accurate. This is prose accuracy in an example and outside every acceptance criterion → CONCERN (non-blocking, see ESCALATIONS).

STATUS: VERIFIED
CONFIDENCE: high. All 9 criteria were run verbatim on head and base and gave the stated results, the gates passed in a fresh environment on this tree, and mutation probes show the new and changed tests catch a missing fill and a missing standard file.
ESCALATIONS:
- Minor, non-blocking prose accuracy: the rule 4 After in `docs/writing.md` says sub-ticket ".6 merges last". Its cited source, `run-0054-planner`, lets .5 run in parallel with .6 and says only that .6 is the last sub-ticket to touch harness code. Suggest "…; .6 is the last change to harness code", which matches the caption. This is for the reviewer or operator. It is not a criterion failure.
- Same as the implementer's Known gaps: runs that use the registered `agents/` role templates instead of the inline `system-prompt.txt` do not get the new preamble line. This follows the parent's Decisions and is reported, not a defect of this PR.
- Protected and guardrail paths were touched as declared (harness: `factory/instance.py`, `factory/prompts/{preamble,critic,reviewer}.md`, `factory/context.template.md`; generated: `docs/prompts/{00-preamble,03-spec-critic,06-code-reviewer}.md`; guardrail: three `docs/design.md` blocks and one test in `tests/factory/test_instance.py`). The merge gate needs the human approval for these. No undeclared protected path was touched.
