Sub-ticket: T-0013.1 (parent `.factory/state/specs/T-0013/v1.md`, issue #23). Branch `factory/T-0013.1`, one commit `e703c1b` on base `0759162`, in worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0013.1`.

What changed:
The factory's agents now get one shared rule: write every section a person reads to a one-page writing standard. Two of the checking agents now apply that rule. Each part:
- **A. The standard.** New `docs/writing.md`, 86 lines. It opens by saying who the reader is: technical, but new to this system. Next comes the list of sections the rule covers. Then the eight rules, in the request's order. Each rule has one line on how a writer checks it, one sourced Before and one After. Rules 1 to 3 use the operator's three findings from the 2026-10-03 overview review. Rules 4 to 8 use real run outputs, each named: run-0054-planner (twice), run-0052-spec_writer, run-0014-triage and run-0062-verifier. The request's `checks-in-flight` escalation could not be found, as the spec's Evidence says. Rule 7 uses a real escalation from run-0062-verifier in its place, and names that run. The page ends by naming `README.md` as a worked example.
- **B. How the rule reaches every role.** Every role's system prompt starts with a shared preamble. Its OUTPUT block gains the spec's five lines, which carry the placeholder `{writing standard}`. The block changed in `docs/design.md` and was re-copied by hand to `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md`, which remain byte-identical. When a run starts, `fill_preamble` in `factory/instance.py` replaces the placeholder with `str(HARNESS / "docs" / "writing.md")`. `HARNESS` is the harness checkout that is running. Its docstring now says this value comes from the checkout, not from `instance.yaml`. It does not refuse when the file is missing, as the spec says. Two more edits: the role-context paragraph in `docs/design.md` (line 54) gets both of the spec's additions, and the placeholder sentence in `dev/build-harness.spec.md` (line 158) now names `{writing standard}`.
- **C. Critic rubric 6.** The critic's readability item now covers five sections, not just Problem: Problem, Evidence, Open questions, Decisions and Operator steps. The item was replaced in `docs/design.md` with the spec's exact text and re-copied to `docs/prompts/03-spec-critic.md`. The same text went into `factory/prompts/critic.md`, which keeps its literal `2` round limit.
- **D. Code-reviewer check 8.** New item 8 after item 7: can the operator read the PR description's What changed and Known gaps? A problem there is SHOULD-FIX, never BLOCKING. It is in `docs/design.md`, `docs/prompts/06-code-reviewer.md` and `factory/prompts/reviewer.md`. The reviewer copy keeps its literal `2`.
- **E. Briefing template.** The briefing is the text every role reads first. Its template, `factory/context.template.md`, gains the spec's four-line bullet asking who reads what the roles write. The bullet goes after "What kind of request to expect".
- **F. Records and tests.** New changelog entry 43 in `docs/changelog.md`; 43 was the next free number. In `README.md`, the "once it exists (#23)" sentence is replaced with the spec's text. A `docs/writing.md` row is added after `docs/prompts/` in "Where things live". The status-header date was already 2026-10-03, today's date, so it is unchanged. The one listed test changed, and there is one new test file (see below).

Acceptance results (each run from the worktree, which equals `~/dev/spec-factory` `main` at `0759162` before the commit; the long one-liners were copied verbatim into a scratch script):
| Criterion | Before (`0759162`) | After (`e703c1b`) |
|---|---|---|
| standard-is-one-page-with-a-pair-per-rule | `missing` | `lines=86 rules=8 before=8 after=8` |
| preamble-names-the-standard | `standard=[] unfilled=0 file=absent` | `standard=[/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0013.1/docs/writing.md] unfilled=0 file=present` (the worktree is the checkout it ran in; `pwd -P` is the same path) |
| preamble-line-in-every-copy | `:0` ×3 | `docs/design.md:1`, `docs/prompts/00-preamble.md:1`, `factory/prompts/preamble.md:1` |
| briefing-template-has-reader-line | `0` | `1` |
| rubric-6-widened-in-every-copy | `:1 :1 :1` then `:0 :0 :0` | `:0 :0 :0` then `:1 :1 :1` |
| reviewer-check-in-every-copy | `:0` ×3 | `:1` ×3 |
| prompt-copies-verbatim (REGRESSION) | `00-preamble verbatim`, `03-spec-critic verbatim`, `06-code-reviewer verbatim`, `preamble copies equal`, `critic-diff=2 reviewer-diff=2` | identical |
| records-name-the-standard | `changelog=0 design=0 buildspec=0 stale=1 row=0` | `changelog=1 design=2 buildspec=1 stale=0 row=1` |
| gates-pass (REGRESSION) | `check=0`, `121 passed in 107.12s` | `check=0`, `126 passed in 86.99s` |

Both gate commands were run from the worktree exactly as written: `git diff --check main...HEAD` exited 0, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `126 passed`. 126 is the baseline of 121 plus the new file's 5 tests. Not a gate, but `ruff check` on the two changed Python files printed `All checks passed!`.

Tests added/changed:
- Changed: `tests/factory/test_instance.py::test_system_prompt_is_the_design_preamble_filled_from_the_instance`. This is the one test under "Tests to change". Part B adds a third filled line, so the unchanged-lines comparison failed as written. The change finds the index of the `{writing standard}` line and leaves it out of that comparison, alongside the first line and the protected-path line. It asserts that the filled line equals the design line with the placeholder replaced by the absolute path of the checkout's `docs/writing.md`. That is an exact-line check, stricter than "contains the path". It adds `"{writing standard}" not in` to the final check. No assertion was removed or loosened.
- New: `tests/factory/test_writing_standard.py`, 5 tests. Each test drives `bin/factory` in a scratch git repo. Like the spec's scenario, it runs `init` and then a triage run on a throwaway store (`FACTORY_STATE`), so it does not need a clean harness checkout.
  - The standard file exists and is non-empty, and the run's system prompt holds the line `person reads to the writing standard at <checkout>/docs/writing.md. Those`.
  - No `{writing standard}` is left in the system prompt.
  - Parametrized ×3: the preamble, spec critic and code reviewer design blocks equal their `docs/prompts/` copies byte for byte.
- Watched them fail first. The prompt edits were in place and `fill_preamble` and `docs/writing.md` were not. The new file gave `2 failed, 3 passed`: the missing standard file, and an unfilled `{writing standard}`. The changed test could not be watched failing on its own assertions. From a dirty checkout it is refused earlier, with "harness … has uncommitted changes", because it uses the instance's own store. It passes in the committed tree.

Known gaps and uncertainties:
- Agents that use the registered role agents do not see the new rule. Those agents come from the `agents/` templates, which this change does not touch, as the spec's Decisions require; their copy of the preamble lacks the line. Only runs that read their role from `system-prompt.txt` get it. The current intake runs work that way.
- No agent sees any of this until the operator moves the runtime to a revision that contains this commit and accepts it (Operator step 1). Until then, the running harness at `~/dev/spec-factory-harness` still has the old preamble. It also has no `docs/writing.md`.
- Whether a live critic actually blocks on an unglossed term in an Evidence paragraph was not tested. That needs a model run on the upgraded runtime (Operator step 3).
- Some Befores in `docs/writing.md` are descriptions or trimmed excerpts, which the spec allows ("short real excerpt or a one-line description"). All 3 operator findings and the run-0054-planner examples for rules 4 and 8 are paraphrased; the overview draft is not in this repo, so findings 1 and 3 are written from the request's account of them. Rules 5, 6 and 7 quote their runs, trimmed with "…" where long. Every After is my own rewrite. Rule 6's After follows the form run-0015-spec_writer later used for the same item. A reviewer should check that each After is still true to the system. For example, rule 4's After says sub-ticket .6 merged last; run-0054 line 18 says so.
- Rule 7's example replaces the request's `checks-in-flight` escalation, which could not be found. The page names the replacement's source (run-0062-verifier). It does not say that it stands in for the request's example. That note is here instead.
- The changelog entry starts "After issue #23". That matches the style of entries 41 and 42, but it is an internal reference the new rule 6 would ask to be introduced. I followed the changelog's existing style.
- I re-copied the three blocks with the same `sed` extraction the prompt-copies-verbatim criterion uses, not with `factory render`. As built, this checkout has no `render` command: `grep -n render factory/cli.py` finds nothing.

Out-of-scope observations:
- `README.md` "Related work and history" still describes #23 as "the documentation standard this page was rewritten to". That is still true. I left it unchanged, because the ticket allows no README edits beyond the two named.
- `dev/build-harness.spec.md:158` describes a `factory render` (and `render --check`) that `factory/cli.py` does not implement in this checkout. That sentence was already there; this ticket only extended its placeholder list.
- `uv run` printed a warning that `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` does not match the project's `.venv` and was ignored. The gate used the worktree's own `.venv`, which is gitignored and was not committed.

Responses to findings (round 2+): n/a, round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run on the committed head and gave the spec's expected output. The one judgment-heavy part is the wording of the standard's Before/After examples.
ESCALATIONS:
- Protected and guardrail paths touched. Each is declared in the parent's Risk section and the sub-ticket, so the merge gate needs the human approval it provides for:
  - harness: `factory/instance.py`, `factory/prompts/preamble.md`, `factory/prompts/critic.md`, `factory/prompts/reviewer.md`, `factory/context.template.md`.
  - generated: `docs/prompts/00-preamble.md`, `docs/prompts/03-spec-critic.md`, `docs/prompts/06-code-reviewer.md`, each re-copied from its design block.
  - guardrail, agent prompts: the preamble, critic and code-reviewer blocks in `docs/design.md`.
  - guardrail, existing tests: the one listed test in `tests/factory/test_instance.py`.
- No undeclared protected path was touched. In particular: `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, green and `~/.nanobot/`.
- No prompt-injection attempt found in the input.
