Sub-ticket: T-0052.1 (parent T-0052, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0052/v2.md`)
Branch: `factory/T-0052.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0052.1`, one commit `8d07f45` on base `525d73f`.

## What changed

Claude Code could not load four of the factory's six role agent templates. A role agent template is a Claude Code agent definition in `agents/`, and `factory init` copies it into a target repository's `.claude/agents/`. The four templates now parse. The harness suite now fails if any template's header stops parsing. `factory init` now names an installed copy that differs from its template, so a target holding an old broken copy finds out.

- **A. Templates.** In `agents/factory-planner.md`, `factory-spec-critic.md`, `factory-spec-writer.md` and `factory-triage.md`, the `description:` value is now wrapped in double quotes. The words are unchanged, and no other line changed. `factory-clerk.md` and `factory-stub.md` are untouched.
- **B. Suite test.** New file `tests/factory/test_agent_templates.py`. The test `test_template_frontmatter_parses_and_carries_the_agent_keys` runs once for each `agents/*.md` file found by a glob, with the file name as the case id, so a seventh template is checked with no edit to the test. Each case checks four things: line 1 is `---`, a closing `---` exists, the lines between them parse with `yaml.safe_load` into a dict, and that dict has `name`, `description`, `model` and `tools`. Every assertion message names the template. A YAML error is not caught, so the case fails under its own id.
- **C. `factory init` report** (`factory/setup.py` `init_cmd`). The copy loop gained an `elif` branch for a copy that already exists. If the copy's bytes differ from the template's, init appends the copy's path to `stale` and prints one stderr line: `factory init: <copy> differs from its template <template>; left as it is`. The copy is never written. `"stale_agents": stale` sits beside `"agents"` in the JSON output. The `store.initialised` log condition and the "restart the session" line are unchanged. So a run of init that only reports differing copies logs nothing and asks for no restart, and the new test checks that. The only caller is `factory/cli.py:783` (`p.set_defaults(fn=init_cmd)`), found with `grep -rn init_cmd factory`. The same new test file has three init tests: an edited copy is listed and kept, a deleted copy is created and not listed, and matching copies give `stale_agents == []`. They build each target with `git_repo`, `cli` and `js` from `tests/factory/_cli.py`.
- **D. Documents.**
  - `README.md` line 463: the `.claude/agents/factory-*.md` row's "Written by" cell keeps "`factory init`, when they are missing" and adds "it reports a copy that differs from its template and leaves it as it is".
  - Step 1 of "Adopting the factory in a repo" gained one sentence. It says init never overwrites an agent copy, and that a copy differing from its template is listed under `stale_agents` and named on stderr. README grows from 1,106 to 1,108 lines, inside the four-line allowance. The status-header date stays 2026-10-13, which is today.
  - `docs/changelog.md`: new entry 73, `73. After issue #108 (2026-10-13), …`, placed after entry 72 and before the "Declined:" line.

## Acceptance results

Each command ran from the worktree inside the running-code wrapper, which gives every run a throwaway HOME.

- **Every role agent template's frontmatter parses and carries name, description, model and tools** (NEW). Before: `factory-clerk.md keys=ok`, `factory-planner.md keys=unparsed`, `factory-spec-critic.md keys=unparsed`, `factory-spec-writer.md keys=unparsed`, `factory-stub.md keys=ok`, `factory-triage.md keys=unparsed`. After: all six print `keys=ok`. All six headers now parse and carry the four keys.
- **The four fixed templates keep their description's words and every other line** (NEW). Before: each of the four printed `text=changed rest=same`, then `others=same`. After: `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, `others=same`. The parsed description equals the old raw text, and no other line moved.
- **The suite fails on a template with broken frontmatter and names it** (NEW). Before: `suite=passed clerk=0 stub=0`. After: `suite=failed clerk=1 stub=1`. I re-ran the scenario with its pytest log kept, to check that the failures come from the new test and nothing else: `FAILED …test_template_frontmatter_parses_and_carries_the_agent_keys[factory-clerk.md]`, `FAILED …[factory-stub.md]`, `2 failed, 591 passed`. Both runs also printed `tar: Failed to set default locale`, which is noise from `tar` and does not affect the result.
- **init reports an edited agent copy and leaves it as it is** (NEW). Before: `exit=0 stale=absent kept=yes named=0 others=0`. After: `exit=0 stale=factory-planner.md kept=yes named=1 others=0`. The edited copy is listed, named once on stderr and kept byte for byte, and init exits 0.
- **init still creates a missing agent copy and lists no matching copy** (REGRESSION). After: `exit=0 created=factory-triage.md stale=0 same=6 differs=0`.
- **README describes init's report of a differing agent copy** (NEW). Before: `row=0 step=0 missing=1`. After: `row=1 step=1 missing=1`.
- **The changelog records issue 108 in one entry without a numbering gap** (NEW). Before: `CONTIGUOUS`, `0`, `0`. After: `CONTIGUOUS`, `1`, `3`. There is one #108 entry, it names `frontmatter`, `stale_agents` and `Nanobot`, and the numbering has no gap.
- **README stays within its line budget and both documents pass the whitespace check** (REGRESSION). After: `readme=within`, `check=0`.
- **Gate `git diff --check main...HEAD`**: no output, exit 0.
- **Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`**: `593 passed in 88.12s`. The 593 include the 9 new tests: six template cases and three init cases.

Red step: before the fix, the new test file gave `7 failed, 2 passed`. The four broken templates failed, the three init tests failed on the missing `stale_agents` key, and clerk and stub passed. After the fix it gave `9 passed`.

## Tests added/changed

- Added `tests/factory/test_agent_templates.py`, a new file with 6 parametrized template cases and 3 init tests, as part B and part C ask.
- Changed: none. No existing test file was touched. `test_init_is_idempotent_and_creates_only_what_is_missing` in `test_instance.py` is left as it is, as the spec asks.

## Known gaps and uncertainties

- The spec says the description is on "line 2". It is on line 3 of each template: line 1 is `---` and line 2 is `name:`. I edited the `description:` line, which is the spec's intent, and the "keep every other line" scenario confirms nothing else changed.
- The frontmatter test checks one thing the spec does not list: that a closing `---` exists. Without that check, a missing close would fail with a bare `ValueError` that does not name the template.
- The stderr line prints the template's path as `instance.AGENTS / <name>`, which is the harness checkout's `agents/` directory. In a target run from the runtime checkout, that path is under `~/dev/spec-factory-harness/agents/`, not the dev checkout.
- factory: markers added: none.

## Out-of-scope observations

- Nanobot's `.claude/agents/` copies are still the broken ones. The Driver refreshes them after the merge and the runtime upgrade, as the spec's Operator steps say. Nothing outside the worktree was written.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN exactly. The broken-template scenario fails only on the new cases. The full suite passed on the commit (593 passed).
ESCALATIONS: none
