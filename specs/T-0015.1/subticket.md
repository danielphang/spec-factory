## T-0015.1 / Add the coding standard and point the implementer, reviewer, spec writer, critic and retro at it

Parent: T-0015, approved spec v2 (`proposal.md`, `design.md`, `specs/*/spec.md`,
`verification.md` in the change folder). Read it for context. Do NOT implement parts outside
this sub-ticket.

Depends on: none
Parallel-safe: yes. It is the only sub-ticket in this plan.

Scope: parts A, B, C, D, E and F of the parent's Proposed change, all of it:
- A. `docs/coding.md` (new), the exact text in the parent's part A. Rewrapping is allowed; the
  wording is fixed by the gate.
- B. The implementer's step 4 pointer line and the code reviewer's new check 7, in all three
  copies of each prompt (`docs/design.md`, `docs/prompts/`, `factory/prompts/`).
- C. `fill_standards(text)` in `factory/instance.py`, called by `fill_preamble` and by `run_start`
  in `factory/cli.py` on the role prompt.
- D. The spec writer's cut rule and critic rubric 3's probe, in all three copies of each.
- E. The marker ledger named in the retro's INPUT block (`docs/design.md` §8 and
  `docs/prompts/08-retro.md`), the Retro routing row (`docs/design.md:127`) and
  `dev/build-harness.spec.md` (the `retro-input` sentence at line 323 and item 66 at line 435).
  Text only.
- F. `docs/design.md:54`, `dev/build-harness.spec.md:158`, changelog entry 44 (after 43, before
  `Declined:`), one `README.md` row after the `docs/writing.md` row, and the new test file
  `tests/factory/test_coding_standard.py`, driven through `bin/factory` as
  `tests/factory/test_writing_standard.py` is.

Acceptance: every parent scenario, verbatim from the parent's `specs/*/spec.md`, run from
`~/dev/spec-factory` (in the implementer's worktree, on its branch):
  1. coding-page-has-five-checkable-rules: NEW. Today it prints `missing`.
     WHEN (bash, from `~/dev/spec-factory`) `if [ -f docs/coding.md ]; then f=docs/coding.md; echo "rules=$(grep -o '^## [0-9]*\.' $f | tr -dc '0-9\n' | paste -sd, -) check=$(grep -c '^Check: ' $f) principle=$(grep -c '^Principle: ' $f) before=$(grep -c '^Before (' $f) after=$(grep -c '^After: ' $f) precedence=$(awk '/^\*\*Precedence\.\*\*/ {p=NR} /^## 1\./ {r=NR} END {print (p && p < r) ? "first" : "absent"}' $f)"; else echo missing; fi`
     THEN it prints `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first`
  2. coding-page-has-every-requested-phrase: NEW. Today it prints `found=0 of 13`.
     WHEN (bash, from `~/dev/spec-factory`) `b=$(printf '\140'); n=0; for h in 'Prefer duplication over premature abstraction' 'grep every caller' "${b}factory:${b}" "${b}reuse:${b}" "${b}stdlib:${b}" "${b}native:${b}" "${b}yagni:${b}" "${b}delete:${b}" 'net: -N lines possible' 'Lean already.' 'ubiquitous language' 'DRY' 'YAGNI'; do if cat docs/coding.md 2>/dev/null | tr '\n' ' ' | grep -qF "$h"; then n=$((n+1)); else echo "missing: $h"; fi; done; echo "found=$n of 13"`
     THEN it prints only `found=13 of 13`
  3. tag-table-severities: NEW. Today it prints `reuse= stdlib= native= yagni= delete=`.
     WHEN (bash, from `~/dev/spec-factory`) `b=$(printf '\140'); for t in reuse stdlib native yagni delete; do printf '%s=%s ' "$t" "$(grep -E "^\| ${b}$t:${b} \|" docs/coding.md 2>/dev/null | grep -oE 'BLOCKING|SHOULD-FIX' | paste -sd+ -)"; done; echo`
     THEN it prints `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX` (a trailing space is allowed)
  4. pointer-line-in-every-copy: NEW. Today the first six lines end `:0` and the last three `:1`.
     WHEN (bash, from `~/dev/spec-factory`) `grep -cF 'Follow the coding standard at {coding standard}.' docs/design.md docs/prompts/05-implementer.md factory/prompts/implementer.md; grep -cF '7. The coding standard at {coding standard}' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; grep -cF 'Maintainability, only where' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md`
     THEN the first six lines each end `:1` and the last three each end `:0`
  5. implementer-and-reviewer-prompts-name-the-page: NEW. Today `standard=[]` for both roles and `file=absent`. GIVEN: a scratch target repository with an instance and a throwaway store, with the ticket's status set by `ticket set` so that each role can start
     WHEN (bash, from `~/dev/spec-factory`) `H=$(pwd -P); T=$(mktemp -d); git -C "$T" init -q -b main; git -C "$T" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init; printf '# demo\n\nDo the thing.\n' > "$T/r.md"; F() { (cd "$T" && env -u FACTORY_INSTANCE -u FACTORY_REPO -u FACTORY_INTEGRATION_BRANCH "$@"); }; F env -u FACTORY_STATE "$H/bin/factory" init --repo-name demo >/dev/null 2>&1; S="$T/s"; X() { F env FACTORY_STATE="$S" "$H/bin/factory" "$@" >/dev/null; }; X ticket new --file "$T/r.md"; X ticket set T-0001 status=ready-for-implementer; X run start --role implementer --ticket T-0001 --model opus; X ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git -C "$T" rev-parse HEAD); X run start --role reviewer --ticket T-0001 --model opus; for r in implementer reviewer; do P=$(ls "$S"/runs/*-$r/system-prompt.txt); echo "$r standard=[$(grep -oF "$H/docs/coding.md" "$P" | head -1)] unfilled=$(grep -c '{coding standard}' "$P")"; done; echo "file=$(test -s "$H/docs/coding.md" && echo present || echo absent)"; rm -rf "$T"`
     THEN it prints `implementer standard=[<checkout>/docs/coding.md] unfilled=0`, `reviewer standard=[<checkout>/docs/coding.md] unfilled=0` and `file=present`, where `<checkout>` is the absolute path of the checkout it ran in
  6. cut-rule-and-probe-in-every-copy: NEW. Today all six lines end `:0`.
     WHEN (bash, from `~/dev/spec-factory`) `grep -cF -- '- Cut before you specify: for each part' docs/design.md docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; grep -cF 'a lettered part the ticket' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`
     THEN it prints six lines, each ending `:1`
  7. marker-ledger-named-in-design-and-build-spec: NEW. Today `design=0 retro=0 buildspec=0 row=0`.
     WHEN (bash, from `~/dev/spec-factory`) `echo "design=$(grep -c 'marker ledger' docs/design.md) retro=$(grep -c 'marker ledger' docs/prompts/08-retro.md) buildspec=$(grep -c 'marker ledger' dev/build-harness.spec.md) row=$(grep '^| Weekly audit done' docs/design.md | grep -c 'marker ledger')"`
     THEN it prints `design=2 retro=1 buildspec=2 row=1`
  8. changed-blocks-verbatim-and-harness-copies-in-step: REGRESSION. Prints the same today; it must still print it after.
     WHEN (bash, from `~/dev/spec-factory`) `q=$(printf '\140\140\140'); for s in "2. Spec writer:02-spec-writer" "3. Spec critic:03-spec-critic" "5. Implementer:05-implementer" "6. Code reviewer:06-code-reviewer" "8. Retro:08-retro"; do f=${s##*:}; sed -n "/^## ${s%%:*}\$/,/^$q\$/p" docs/design.md | sed "1,/^${q}text\$/d;\$d" | cmp -s - docs/prompts/$f.md && echo "$f verbatim" || echo "$f differs"; done; for p in "02-spec-writer spec_writer" "03-spec-critic critic" "05-implementer implementer" "06-code-reviewer reviewer"; do set -- $p; printf '%s-diff=%s ' "$2" "$(diff docs/prompts/$1.md factory/prompts/$2.md | grep -c '^[<>]')"; done; echo`
     THEN it prints five `verbatim` lines, then `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2` (a trailing space is allowed)
  9. records-name-the-coding-standard: NEW. Today `changelog=0 design=0 buildspec=0 row=0`.
     WHEN (bash, from `~/dev/spec-factory`) `echo "changelog=$(grep -E '^[0-9]+\. ' docs/changelog.md | grep -c 'docs/coding.md') design=$(grep -c '{coding standard}' docs/design.md) buildspec=$(grep -c '{coding standard}' dev/build-harness.spec.md) row=$(grep -c '^| .docs/coding.md. |' README.md)"`
     THEN it prints `changelog=1 design=3 buildspec=1 row=1`
  10. gates-pass: REGRESSION. Today `check=0` and `126 passed`; after, the count rises by the new test file's tests.
     WHEN (bash, from `~/dev/spec-factory`) `git diff --check main...HEAD; echo "check=$?"; uv run --frozen pytest -q -p no:cacheprovider tests/factory`
     THEN it prints `check=0`, and pytest ends with `N passed` and no failures or errors
  11. Intermediate check, NEW: the new test file passes on its own and fails on `main`.
     WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_coding_standard.py`
     THEN it ends with `N passed` (N at least 2, one per bullet in part F) and no failures; run
     against `main`'s files (no `docs/coding.md`, no fill) its prompt-path test fails. A test
     that passes on `main` checks nothing, and is a finding.

Tests to change: none. The parent lists none: `test_design_block_equals_its_prompt_copy` and
`test_system_prompt_is_the_design_preamble_filled_from_the_instance` must pass unchanged.

Protected paths (all from the parent's Risk list):
- harness: `factory/instance.py`, `factory/cli.py`, `factory/prompts/implementer.md`,
  `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`.
- generated: `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`,
  `docs/prompts/05-implementer.md`, `docs/prompts/06-code-reviewer.md`, `docs/prompts/08-retro.md`,
  each re-copied from its changed design block, never edited by hand apart from it.
- guardrail (agent prompts): the spec writer, spec critic, implementer, code reviewer and retro
  blocks in `docs/design.md`.
Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, any
existing test, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Out of scope:
- Everything under the parent's Out of scope: the verifier, triage and planner prompts, the
  shared preamble, any new role, the code that builds the marker ledger, the retro itself
  (`retro-input`, `retro.js`), the `agents/` templates, fixing `ensure_gitignore` in
  `factory/store.py`, rewriting existing code to the new rules, reviewer checks 1 to 6 and 8 and
  its OUTPUT format, a ponytail-style benchmark, and Green (`~/dev/nanobot-upstream`).
- The parent's Operator steps. Step 0, the operator's side-by-side acceptance test, and step 1,
  moving the runtime (the pinned checkout at `~/dev/spec-factory-harness` that runs every ticket)
  and `--accept-harness`, are the operator's. This sub-ticket merges into `main` only; no running
  agent sees the change until step 1.
- The parent's Out-of-scope observations (the drifted `agents/` templates, the unbuilt `render`
  command described at `dev/build-harness.spec.md:158`, changelog entry 43's "eight rules").

---

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The approved spec already fits one PR, and splitting it would make review and
rollback harder, not easier.

Why not split (checked against the spec, not assumed):
- Size. The spec's own trial came to 149 added and 15 removed lines in 16 files, plus one new test
  file. The per-sub-ticket budget is `{400}` changed lines (`docs/design.md:288`, filled from
  `.factory/instance.yaml:25`, `spec_lines: 400`). It fits.
- Parts A, B and C cannot land apart without breaking what the spec asks. B without C puts an
  unfilled `{coding standard}` into every live implementer and reviewer prompt (the spec's
  verification.md names that exact failure: `standard=[] unfilled=1`). B without A points each
  run at a file that does not exist. C alone is a helper with no placeholder to fill.
- Parts D (the spec writer's cut rule) and E (the marker ledger in the retro's input) are
  independent of A to C in logic, but not in files. All of A to F edit `docs/design.md`, and part F
  asks for one changelog entry, 44, that describes every part. Separate sub-tickets would need
  either three changelog entries or one entry describing parts not yet merged. Either changes
  what the spec asks, and none of these sub-tickets could run in parallel anyway, because they
  share files.

Drift check: since the spec's base commit `b33e593`, the only change under `docs/`, `factory/`,
`dev/`, `tests/` and `README.md` is `dev/issues.md` (`git diff --stat b33e593 HEAD`, one file,
2 insertions and 1 deletion). The spec's line numbers still hold on `main` at `61d92be`. Spot
checks: implementer step 4 at `docs/design.md:493`, check 7 at `:555`, the retro's
`is how you propose a model change.` at `:648`, the Retro routing row at `:127`, the size rule's
`seams as lettered parts under Proposed change.` at `:289`, rubric 3's `breaks, with a reason
each.` at `:382`, and `fill_preamble` at `factory/instance.py:160-172`. Anchor each edit on its
quoted text, not on its line number.

---
