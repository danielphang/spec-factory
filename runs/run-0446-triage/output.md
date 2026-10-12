Type: chore

Title: De-bloat A: delete dead code, redundant lines and stale docstrings in the harness

Summary: The 2026-10-11 de-bloat sweep found harness code that nothing calls, a config key that nothing reads, a few redundant lines in `factory/cli.py`, and docstrings that are no longer true. The requester wants all of it removed, with no change to any refusal, verdict or routing. The named items are: `gitops.run_gates`, `store.STATES`, `specstore.OPS`, `store.load_config`, the `force_push_allowed` key (in the template, the test fixture and the test's key lists), the `prompt_name` alias, the two duplicate in-flight refusal branches in run start, the second `store.ensure_gitignore` call for build roles, the extra blank lines, three stale docstrings, and the unused `cfg` parameter of `gitops.repo_root`. Done means each named symbol is gone from `factory/`, `grep -rn force_push_allowed factory tests` prints nothing, ruff F401/F841 stays clean, the full harness suite passes, and the three in-flight refusal tests pass unchanged.

Evidence: (I checked each claim on this checkout at `0ba4e4f`, using grep across `factory/ bin/ tests/ docs/design.md README.md dev/` and reading the cited line ranges)
- `gitops.run_gates` is defined at `factory/gitops.py:202`. Nothing calls it: the only hit is the definition.
- `store.STATES` is at `factory/store.py:15-21` and nothing reads it. The other `*STATES` hits are different names (`drive.INTAKE_STATES`/`BUILD_STATES`, `subtickets.IN_FLIGHT_STATES`).
- `specstore.OPS` is at `factory/specstore.py:20` and nothing reads it. `parse_delta` hardcodes `(ADDED|MODIFIED|REMOVED)` at `:130`.
- `store.load_config` is at `factory/store.py:29-32` and nothing calls it. Every caller uses `instance.load_config`, including `store.py:42`.
- `force_push_allowed` appears at `factory/instance.template.yaml:45`, `tests/factory/fixtures/instance/instance.yaml:22` and `tests/factory/test_instance.py:109` and `:354`. Nothing in `factory/*.py` reads it. `factory/prompts/implementer.md:23` hardcodes "never rebase: force-push is not allowed here". The live `.factory/instance.yaml:34` also has the key. `factory/instance.py` has no unknown-key check, so a leftover key in an instance does nothing.
- `factory/cli.py:234` has `prompt_name = a.role`, and `:236` is its only use.
- The in-flight refusals are at `cli.py:207-208` (implementer) and `:211-212` (triage, spec_writer, critic, planner). Both raise `f"{t['id']} already has run {t['in_flight'][0]} in flight"`. The role sets do not overlap. The three tests the request names assert this text: `test_p0_cli.py:97`, `test_shepherd.py:533` and `test_whole_spec_plan.py:200`.
- `store.ensure_gitignore` runs at `cli.py:229` for every role. For build roles it also runs at `:377`, inside `_start_build_run`, which `:227` calls first. So build roles run it twice.
- `cli.py:1966-1970` has four blank lines in a row before the live-store fence comment.
- Stale docstrings: `store.py:3` says "so a later sub-ticket can add commit-and-push in one place". `specstore.py:8-9` says "so the live pilot store is unaffected".
- `compose.py:420` is not a docstring. It is the message of a refusal: `raise store.Refused(f"compose: role {role} not supported yet")`. Every role in `cli.ROLES` (`cli.py:25`) has a branch in `compose` (`compose.py:278-350`), so I believe the refusal can never be reached. Nothing in `tests/` or the docs contains the text.
- `gitops.repo_root(cfg)` at `gitops.py:18-19` ignores `cfg` and returns `instance.repo_root()`. I counted 14 `gitops.repo_root(` callers: 1 in `compose.py`, 13 in `cli.py`.
- Issue: https://github.com/danielphang/spec-factory/issues/97 (#96 row 2a).

Capabilities: none

Assumptions:
- (inference) No capability changes because the change is meant to keep every behaviour. The closest one is build-dispatch: the in-flight refusals run when a role run starts. The refusal text stays the same, so no requirement changes.
- (inference) Rewording the `compose.py:420` message counts as fixing a stale message, not as a refusal change, because the refusal cannot be reached. The spec writer should confirm it cannot be reached, or leave the text alone.
- (inference) `tests/factory/test_instance.py` (`:109`, `:354`) and `tests/factory/fixtures/instance/instance.yaml` are existing tests and fixtures. The spec must list them under "Tests to change", or the guardrail will block the implementer.
- (inference) The design doc still describes the `{force-push allowed}` placeholder at `docs/design.md:144` and `:623`. `dev/build-harness.spec.md` D9 and item 80 name `force_push_allowed` as the key that fills it. The request does not say whether these documents change. With the key gone, the design doc describes a setting that no longer exists. In practice nothing changes, because the shipped prompt already hardcodes the answer. The spec writer should either record this as a known gap or add a design-doc line with its changelog entry. If the design doc changes, the `docs/prompts/` copy must be re-copied, and prompts are out of scope here. That makes a known gap the cheaper route.
- (inference) T-0047 (#100, split `cli.py` into modules) moves the code at these `cli.py` line numbers. The request for T-0047 says it runs after the helper ticket. This ticket's `cli.py` edits should merge before T-0047 is planned, or T-0047 should be planned against the post-merge tree. T-0046 (#99, shared helpers) also edits `cli.py`. I found no overlap between them in the named lines.
- Suggestion (priority is a human call): low priority, and worth landing first in the de-bloat round because it is small and only removes code.

Question for human / Missing info / Reason: n/a (ACCEPT). Duplicate search: this request is T-0044 itself. Its siblings, T-0045 to T-0048 (#98 to #101), cover different items. No open or closed ticket names these symbols, apart from T-0024's earlier note on `run_gates`, which the request cites.

STATUS: ACCEPT
CONFIDENCE: high. I checked every evidence item on this checkout with grep and by reading the lines. The scope only removes code and the requester spelled it out.
ESCALATIONS: none
