## Critic review — T-0010 spec v2 (round 2)

Spot-checks run from `~/dev/spec-factory` at `555c119` (branch `main`; working tree carries only `intake/state/**` run files) and, read only, `~/dev/nanobot-upstream` (`feat/lionbot-v3`, now at `e00561071`, one more commit past round 1; `factory/cli.py` `archive_cmd` is unchanged in content).

Scope of this round: (a) whether the four round-1 findings were resolved, (b) the text that changed (item 91, D.1, E, F's anchor, the new Evidence bullets, Risk, Tests to change, the two new out-of-scope observations, the item-91 acceptance grep).

Grounding verified on changed text:
- New Evidence citations: line 160 is the `factory init` bullet and says "creates the `tickets` branch and its checkout"; line 202 defines `factory ticket park ID --reason R --outputs RUN,RUN [--question PATH]`; line 458 is item 84 and exercises `AS daniel factory resolve T-0001 --close` on a parked parent; line 474 is item 88 and pins `specs/T-0001/v1.md` with `AS daniel factory approve-spec T-0001 --version 1`; line 152 lists `openspec/` among the state checked out at `~/factory/state` on branch `tickets`.
- `grep -c 'factory init' docs/spec-factory.md` → `0`; `grep -c 'openspec/' docs/spec-factory.md` → `3`. The design doc never names the CLI command, so the D.1 / E wording ("before the repo had an `openspec/` tree") is the right call and the new REGRESSION item holds today.
- `grep -l archive prompts/*` → exit 1; `git diff --check main...HEAD` → exit 0. `## Risk` is at `plans/P0-intake-skeleton.md` line 100 with a blank line 99 before it, so F's anchor is unambiguous.
- Acceptance "today" values re-run for the changed and the resolution items: the item-91 grep (`… | grep -F 'no spec store (factory init not run)' | grep -F 'T-0001 has no change folder to archive' | grep -c 'git rm -r'`) → `0`; the K refusal grep → `0`; the resolution-bullet grep → `0`; the verbatim line-94 REGRESSION grep → `1`. All as stated.
- Reference harness: `archive_cmd` (`factory/cli.py` 436–447) refuses in the order `is_active` → `change_dir(...).exists()` → `applies`, messages `no spec store (factory init not run)` and `<ID> has no change folder to archive`, exactly as A and item 91 quote; `specstore.is_active` is `root / "openspec"` `.is_dir()`, so `mv openspec ../openspec.aside` does produce the no-spec-store refusal in (b). The two new out-of-scope observations are real: `factory spec tasks` refuses `… has no change folder (no pinned version)` (`cli.py` 415) and `ticket_park` refuses status `planned` (`cli.py` 137).
- `intake/answers/T-0010.md` chooses (a) and names SPEC-21/26/27 as the cohort; the spec follows it.

Findings:

[SHOULD-FIX] 2, 6 — Proposed change C, item 91 (a) setup
Problem: `git rm -r -q openspec/changes/T-0001 && git commit -q -m setup` only works if `approve-spec` left the change folder tracked and committed on the `tickets` checkout, and the build spec says this only indirectly (line 309: for `approve-*` "the CLI commits the row and pushes it"; line 152: `openspec/` is state on branch `tickets`), while the reference harness has no git integration at all (`grep -rn 'subprocess\|"git"' factory/*.py` outside `hook.py` → nothing), so `git rm` would fail there with "pathspec did not match".
Evidence: Lines 152 and 309 as quoted; `factory/store.py` `write_text` is a plain `path.write_text`; `specstore.pin` writes files and nothing else. I rate this SHOULD-FIX, not BLOCKING, because a harness built from the build spec does commit `approve-spec`'s writes (line 309), and the item's before/after check (`git rev-parse HEAD`, `git status --porcelain`) is correct either way.
Suggested fix: Make the setup independent of the commit question — `rm -rf openspec/changes/T-0001` on the `tickets` checkout, no commit — and change the item-91 acceptance grep's last stage from `grep -c 'git rm -r'` to `grep -c 'rm -rf openspec/changes/T-0001'`; the before/after `git rev-parse HEAD` and `git status --porcelain` comparison stays as written.

Rubric items not flagged this round: the resolution text in A and D.3 matches the operator's answer (a) word for word in substance; part H and the "does not apply" resolution are untouched and guarded by REGRESSION items; no reference SHA, test name or line number remains in the spec; Risk declares no protected path and A–F touch none; `prompts/` untouched is proven by grep, not asserted.

Prior findings (round 1):
- [BLOCKING] item 91 (b) setup depended on unstated `approve-spec` behaviour without `openspec/` — RESOLVED. Both refusals now come from mechanical setups on item 88's T-0001 (`git rm`/commit, then `mv openspec`), the "pinned before `factory init`" parenthetical is gone from the item, and the stderr messages are quoted exactly as the reference emits them. The residual setup question is the SHOULD-FIX above, which is a different and smaller point (tracked vs. untracked), not the one I raised.
- [SHOULD-FIX] D.1 wording garbled — RESOLVED, with different words than I suggested. The writer's reason (`grep -c 'factory init' docs/spec-factory.md` → `0`; the design doc names the tree, not the command) is correct and I accept it; the new REGRESSION item pins it.
- [NIT] reference SHAs in Evidence — RESOLVED. No reference SHA remains; `555c119` is this repo's own HEAD, which is fine.
- [NIT] item 91 (c) tested only the existing `--close` — RESOLVED by removing (c); the resolution is stated in K (A) and the doc (D.3) and checked by the K greps.

STATUS: APPROVE
CONFIDENCE: high — every changed citation, the reference refusal order and messages, and the changed acceptance "today" values were verified by command; the one remaining finding is a setup robustness point that does not change what the spec decides.
ESCALATIONS: none
