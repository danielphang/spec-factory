Sub-ticket: T-0052.1 (parent T-0052, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0052/v2.md`)
Branch: `factory/T-0052.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0052.1`. Head `3809245`, a fix-round commit on top of `1d0a1c7`. `1d0a1c7` is a merge of `main` (`43a289e`) into the round-1 commit `8d07f45`. The merge-base with `main` is now `43a289e`, the base the harness gave.

## What changed

Claude Code could not load four of the factory's six role agent templates. A role agent template is a Claude Code agent definition in `agents/`; `factory init`, the command that sets a repository up to use the factory, copies each one into that repository's `.claude/agents/`. After this change the four templates parse, the harness suite fails if any template's header stops parsing, and `factory init` names any installed copy that differs from its template. A target that still holds an old broken copy now gets told about it.

Parts A to D are unchanged from round 1 except where noted.

- **A. Templates.** In `agents/factory-planner.md`, `factory-spec-critic.md`, `factory-spec-writer.md` and `factory-triage.md`, the `description:` value is wrapped in double quotes. The words are unchanged and no other line changed. `factory-clerk.md` and `factory-stub.md` are untouched.
- **B. Suite test.** This is the new file `tests/factory/test_agent_templates.py`. `test_template_frontmatter_parses_and_carries_the_agent_keys` runs once for each `agents/*.md` found by a glob, with the file name as the case id, so a seventh template gets checked with no edit to the test. Each case checks four things: line 1 is `---`; there is a closing `---`; the lines between them parse with `yaml.safe_load` into a dict; and the dict has `name`, `description`, `model` and `tools`. Every assertion message names the template. A YAML error is not caught, so the case fails under its own id.
- **C. `factory init` report** (`factory/setup.py` `init_cmd`). The copy loop has an `elif` for a copy that already exists. When the copy differs from its template, init adds the copy's path to `stale_agents` in its JSON output and prints one line to stderr: `factory init: <copy> differs from its template <template>; left as it is`. Init never writes the copy. The `store.initialised` log condition and the "restart the session" line are unchanged.
  - **New this round:** a path that exists but is not a regular file, such as a directory, now also counts as differing from its template. It is listed and left alone. In round 1, a directory in place of a copy made init crash with `IsADirectoryError` (exit 1). Before round 1, the `exists()` check skipped such a path silently. The fix is one condition, `not (dest / src.name).is_file() or …`, and a fourth init test covers it.
  - The init tests in the new file: an edited copy is listed and kept; a deleted copy is created and not listed; matching copies give `stale_agents == []`; a directory in place of a copy is listed and left as it is. Each builds its target with `git_repo`, `cli` and `js` from `tests/factory/_cli.py`.
- **D. Documents.**
  - `README.md`: the `.claude/agents/factory-*.md` row's "Written by" cell keeps "`factory init`, when they are missing" and adds that init reports a copy that differs from its template and leaves it as it is.
  - `README.md`, step 1 of "Adopting the factory in a repo": one new sentence says init never overwrites an agent copy, and that a copy that differs from its template is listed under `stale_agents` and named on stderr.
  - README is 1,108 lines after the merge of `main`, within the 1,110 budget. The status date stays 2026-10-13, which is today.
  - `docs/changelog.md`, **changed this round:** the #108 entry is now **74**, after `main`'s entry `73. After issue #110`, with a blank line between them in the file's style. Its text is unchanged. In round 1 it was also numbered 73, so merging into `main` would have left two entries numbered 73.

## Acceptance results

I ran every command from the worktree at `3809245`, inside the running-code wrapper (a fresh temporary HOME each time), after `uv sync --frozen` (exit 0). I saved each command to `scratch/sc/s<n>.sh` and checked with `grep -F` that each one matches the spec text in my input exactly. The output is in `scratch/acceptance.log`. The "Before" values are from round 1, measured on `525d73f`.

- **Every role agent template's frontmatter parses and carries name, description, model and tools** (NEW).
  - Before: clerk and stub `keys=ok`; planner, spec-critic, spec-writer and triage `keys=unparsed`.
  - After: `factory-clerk.md keys=ok`, `factory-planner.md keys=ok`, `factory-spec-critic.md keys=ok`, `factory-spec-writer.md keys=ok`, `factory-stub.md keys=ok`, `factory-triage.md keys=ok`.
- **The four fixed templates keep their description's words and every other line** (NEW).
  - Before: each of the four `text=changed rest=same`, then `others=same`.
  - After: `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, `others=same`.
- **The suite fails on a template with broken frontmatter and names it** (NEW).
  - Before: `suite=passed clerk=0 stub=0`.
  - After: `suite=failed clerk=1 stub=1`.
  - I re-ran the scenario with its pytest log kept (`scratch/s3.log`). Only the two new cases fail: `FAILED …test_template_frontmatter_parses_and_carries_the_agent_keys[factory-clerk.md]` and `…[factory-stub.md]`, with `2 failed, 592 passed`.
- **init reports an edited agent copy and leaves it as it is** (NEW).
  - Before: `exit=0 stale=absent kept=yes named=0 others=0`.
  - After: `exit=0 stale=factory-planner.md kept=yes named=1 others=0`.
- **init still creates a missing agent copy and lists no matching copy** (REGRESSION). After: `exit=0 created=factory-triage.md stale=0 same=6 differs=0`.
- **README describes init's report of a differing agent copy** (NEW).
  - Before: `row=0 step=0 missing=1`.
  - After: `row=1 step=1 missing=1`.
- **The changelog records issue 108 in one entry without a numbering gap** (NEW).
  - Before: `CONTIGUOUS`, `0`, `0`.
  - After: `CONTIGUOUS`, `1`, `3`.
  - This now holds with `main`'s entry 73 in the tree. `grep -n '^7[0-9]\. ' docs/changelog.md` lists 70, 71, 72, `73. After issue #110` and `74. After issue #108`.
- **README stays within its line budget and both documents pass the whitespace check** (REGRESSION). After: `readme=within`, `check=0`.
- **Gate `git diff --check main...HEAD`**: no output, exit 0. The merge-base is now `43a289e`, so this covers the whole change against current `main`.
- **Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`**: exit 0, `594 passed in 96.55s`. That is 593 from round 1 plus the new directory test.

Red step for the new test: before the `setup.py` fix, `tests/factory/test_agent_templates.py` gave `1 failed, 9 passed`. The failure was `test_init_lists_a_directory_in_place_of_a_copy_and_leaves_it`, where init exited 1 with `IsADirectoryError`. After the fix: `10 passed`.

## Tests added/changed

- Added `tests/factory/test_agent_templates.py`. It is a new file with 6 parametrized template cases and 4 init tests. The fourth init test, `test_init_lists_a_directory_in_place_of_a_copy_and_leaves_it`, is new this round and covers the verifier's `IsADirectoryError` finding.
- Changed: none. No existing test file is in the diff (`git diff --stat main..HEAD`).

## Known gaps and uncertainties

- **Decision taken without the spec:** how init treats a directory where an agent copy belongs. I chose to list it under `stale_agents` and leave it. The other option was to skip it silently, as init did before this ticket. I chose listing because a directory is not the template, and the spec's intent is that the operator hears about any copy that is not the template. The stderr line for this case still says "differs from its template", which is accurate but does not say the path is a directory. A reviewer may prefer the silent skip.
- Other unreadable cases (for example a copy with no read permission) still raise and exit 1. I did not handle them, because no criterion or finding covers them.
- The spec says the description is on "line 2". It is on line 3 of each template: line 1 is `---` and line 2 is `name:`. I edited the `description:` line, as the spec intends.
- The frontmatter test also checks that a closing `---` exists, which the spec does not list. Without it, a missing close would fail with a bare `ValueError` that does not name the template.
- The stderr line gives the template's path as `instance.AGENTS / <name>`. In a target run from the runtime checkout, that path is under `~/dev/spec-factory-harness/agents/`, not the dev checkout.
- The merge commit `1d0a1c7` came in with a wrong author email (`noreply@anthropic.com`), set by a `-c user.email` override on the merge command. I amended it to the repo's configured identity before making any other commit. There is no remote, so nothing was pushed with the wrong email.
- factory: markers added: none.

## Out-of-scope observations

- Nanobot's `.claude/agents/` copies are still the broken ones. Its Driver (the session that runs the Nanobot target) refreshes them after the merge and the runtime upgrade, as the spec's Operator steps say. I wrote nothing outside the worktree and my scratch directory.
- The verifier's process point still stands for the harness. `git diff --check main...HEAD` and the head-only acceptance commands could not see the changelog number collision while the branch's merge-base was older than the given base. This round's merge of `main` resolves it for this branch only.

## Responses to findings

- Verifier, changelog criterion (on the trial merge with `main`, two entries were numbered 73 and the command printed `GAPPED`): **FIXED** in `1d0a1c7` (merge of `main`) and `3809245` (entry renumbered to 74 and placed after #110's). The verifier suggested a rebase. I merged instead, because my role forbids rebasing (force-push is not allowed). The result is the same: the command now prints `CONTIGUOUS`, `1`, `3` on a tree that contains `main`'s entry 73.
- Verifier, concern outside the criteria (`factory init` exits 1 with `IsADirectoryError` when a directory sits where an agent copy belongs): **FIXED** in `3809245`. Init now lists that path under `stale_agents`, leaves it alone and exits 0. The new test above covers it.
- Code reviewer: no findings (APPROVE).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All eight acceptance commands printed their THEN exactly on `3809245`, with `main`'s changelog entry 73 in the tree. Both gates passed (594 passed). The broken-template scenario fails only on the two new cases.
ESCALATIONS: none
