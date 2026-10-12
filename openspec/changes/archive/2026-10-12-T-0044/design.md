## Proposed change

About 50 changed lines, all in `factory/` plus two test files. One sub-ticket.

A. **Dead definitions.** Delete:
- `run_gates` with its docstring (`factory/gitops.py:202-211`), and the blank lines before it that would then trail the file;
- `STATES` (`factory/store.py:15-21`);
- `OPS` (`factory/specstore.py:20`);
- `load_config` (`factory/store.py:29-32`), with one of the two blank-line pairs around it.

Keep `RESULT_ROLES` and `Refused`. Run `uvx ruff check --select F401,F841 factory tests` afterwards. No import should become unused, but if one does, remove it.

B. **The unread setting.** Delete the line `force_push_allowed: false` from `factory/instance.template.yaml` (line 45) and from `tests/factory/fixtures/instance/instance.yaml` (line 22). In `tests/factory/test_instance.py`, line 109 drops `and cfg["force_push_allowed"] is False`. Line 354's key tuple drops `"force_push_allowed",`, and the tuple is re-wrapped if needed. Leave the `set(cfg) == set(tpl)` assertion at line 113 unchanged: both sides lose the key.

C. **Run start (`factory/cli.py` `run_start`).**
- Replace the two in-flight branches (`:207-208` and `:211-212`) with one, placed where the implementer branch is now, before the reviewer/verifier branch:
  `if a.role in ("triage", "spec_writer", "critic", "planner", "implementer") and t["in_flight"]:`
  `    raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")`
  The reviewer/verifier branch (`:209-210`) and every later check keep their order.
- Delete `prompt_name = a.role` (`:234`). Line 236 reads `(PROMPTS / f"{a.role}.md")`.
- Delete `store.ensure_gitignore(root)` inside `_start_build_run` (`:377`). Keep the call at `:229` and the one in `init` (`:1469`).
- Cut the four blank lines at `:1967-1970` to two.

D. **Stale text.**
- `factory/store.py`: delete line 3 and the blank line 2, so the module docstring is its first line alone.
- `factory/specstore.py:8-9`: end the sentence at "(specs pinned as one text)." by dropping ", so the live pilot store is unaffected". Re-wrap the line if it becomes short.
- `factory/compose.py:420`: change the message to `f"compose: unknown role {role}"`.

E. **`gitops.repo_root`.** Change the signature to `def repo_root() -> Path:`. Replace each `gitops.repo_root(cfg)` with `gitops.repo_root()`: one in `compose.py:110`, eleven in `cli.py`. Where a caller's `cfg` then goes unused, ruff F841 does not fire, because `cfg` is a parameter. Leave such parameters alone.

No change to `README.md`: no command, state, stop or path changes. No change to `docs/` or `dev/` (proposal, Decisions).

## Tests to change

- `tests/factory/test_instance.py` lines 109 and 354: each asserts the `force_push_allowed` key that part B removes from the template and the fixture (Decision: the unread setting is deleted). Remove only the key from each assertion.
- `tests/factory/fixtures/instance/instance.yaml` line 22: the fixture must keep the template's keys, because line 354 compares them. Delete the key line.

