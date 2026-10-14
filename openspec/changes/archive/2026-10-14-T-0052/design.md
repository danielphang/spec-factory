## Proposed change

A. Templates. In `agents/factory-planner.md`, `agents/factory-spec-critic.md`, `agents/factory-spec-writer.md` and `agents/factory-triage.md`, change line 2 from `description: <text>` to `description: "<text>"`. The text stays character for character the same. None of the four contains a `"` or a `\`, so no escaping is needed. Change nothing else in these files, and do not touch `factory-clerk.md` or `factory-stub.md`.

B. Suite test. Add a new file, `tests/factory/test_agent_templates.py`. Add one test, parametrized over `sorted((REPO / "agents").glob("*.md"))` with the file name as the case id (`REPO` from `tests/factory/_cli.py`). Each case:
   1. asserts line 1 is `---`;
   2. takes the lines up to the next `---` and parses them with `yaml.safe_load`;
   3. asserts the result is a dict containing `name`, `description`, `model` and `tools`.

   Each assertion message names the template. A YAML error is left to fail the case (pytest shows it under the case id), not caught. Do not hard-code the list of templates: a seventh template must be checked without editing the test.

C. `factory init` report, in `factory/setup.py` `init_cmd`.
   1. Next to `agents: list[str] = []`, add `stale: list[str] = []`.
   2. In the copy loop (lines 180-184), add an `elif` for an existing copy. When `(dest / src.name).read_bytes() != src.read_bytes()`, append `str(dest / src.name)` to `stale` and print one line to stderr: `factory init: <copy path> differs from its template <template path>; left as it is`.
   3. Never write the copy. Add `"stale_agents": stale` to the final `out({...})` beside `"agents"`. Leave the `store.initialised` event condition and the "restart the session" line as they are.

   In the same new test file, add suite tests for this: an edited copy is listed and kept; a deleted copy is created and not listed; matching copies give `stale_agents == []`. Build each target with the shared helpers in `tests/factory/_cli.py` (`git_repo`, `cli`, `js`), the way `tests/factory/test_instance.py`'s `target` fixture does, and add no new setup code. `_cli.py` says a test file imports helpers from there, never from another test file, so do not import that fixture. Do not add these tests to `test_instance.py`: they overlap `test_init_is_idempotent_and_creates_only_what_is_missing` there, but leave that test as it is.

D. Documents.
   1. `README.md` line 463, the `.claude/agents/factory-*.md` row's "Written by" cell: keep "`factory init`, when they are missing" and add that init reports a copy that differs from its template and leaves it. The row must contain the words `differs from its template`.
   2. Step 1 of "Adopting the factory in a repo" (README lines 579-587): add one sentence saying a copy that differs from its template is listed under `stale_agents` and named on stderr, and is never overwritten.
   3. Net README growth: at most four lines. README's "Maintaining this page" asks a change to a command to bump the date in the status header (line 9, now "Current state as of 2026-10-13"): set it to the merge date if that differs. This changes no line count.
   4. `docs/changelog.md`: append one entry, the next number after the last, starting `<n>. After issue #108 (2026-10-13), `. It says the four headers did not parse and are now quoted, that the suite now parses every template's frontmatter, and that init reports a differing copy in `stale_agents` without overwriting it. It also says Nanobot's copies are refreshed by its Driver. The entry must contain the words `frontmatter`, `stale_agents` and `Nanobot`. If another ticket takes the next number first, take the next free one: the entries must stay numbered without a gap.

Size: about 4 template lines, about 7 lines in `setup.py`, a new test file of about 50 lines, 2 README lines and 1 changelog line.

## Tests to change

none. No existing test pins the old behaviour. `tests/factory/test_instance.py:123` and `:135` assert `agents` on runs where every copy matches or one was deleted, and `tests/factory/test_store_branch.py:269` reads named keys only. On the prototype the full suite passed unchanged (590 passed).

