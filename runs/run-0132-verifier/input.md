## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
  `intake/state/` until an operator step moves it.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
it only to observe what a fix does there today; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0132-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0132-verifier/wt` (branch `factory/T-0015.1`, base `61d92bef32d05c89bb9187f8455f4eb298b2a99f`, head `27d6d63fcb2f5c03d64696f6769abf871e4f2bc0`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0015.1

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

## Parent spec (v2, pinned)

=== proposal.md
## Problem

The factory has no rule that stops its coding agents from building more than a ticket needs. Two
agents write and judge code. The implementer writes the code for one piece of a ticket. Its prompt
says to make "the smallest change" that passes the tests, and nothing about how to find that
change. The code reviewer judges that code before it merges. Its last check says only
"Maintainability, only where it will cause real problems", which gives the reviewer no kind of
finding to look for, so a reviewer either pads its review or says nothing. Coding agents are known
to over-build. They add a new helper beside one that already exists, hand-write something the
standard library ships, or add an interface with one implementation. Nothing in the factory
catches this. The operator pays at the gate, where they approve specs and merges, in bigger diffs.
After the merge they own the duplicate code.

This change adds one page, `docs/coding.md`, the coding counterpart of the writing standard. The
writing standard is `docs/writing.md`, the page every agent follows when it writes something a
person reads. The new page has five rules. Each rule can be checked by the agent in its own
output, has an example with its rewrite, and names the code-design principle it applies:
- reuse before writing;
- find every caller before fixing a shared function, then fix it once;
- mark each deliberate shortcut with a `factory:` comment;
- tag each over-building review finding;
- use one name per concept from spec to code.

The page opens with a precedence rule: a target repository's own instructions win where they
disagree with it. The implementer and reviewer prompts each gain one line pointing to the page.

Two smaller pieces ride with it:
- The spec writer is told to cut any part the ticket does not need, and the spec critic treats
  such a part as a finding.
- The retro is the planned agent that proposes prompt changes from pipeline outcomes. Its design
  now lists, as one of its inputs, every `factory:` comment in the code. The code that builds that
  list waits for the ticket that builds the retro.

## Evidence

- The page does not exist. `ls docs/coding.md` fails with "No such file or directory". The format
  it copies is `docs/writing.md`: one numbered rule per heading, a `Check:` line saying how to
  verify the rule in your own output, a sourced `Before (` example and an `After:` rewrite.
- The text this ticket replaces is still in place, in all three copies of each prompt. The copies
  are the design document `docs/design.md`, its verbatim copy under `docs/prompts/`, and the
  copy the harness runs, under `factory/prompts/`, which has some placeholders already filled in.
  The harness is the code that starts each agent run and keeps its records.
  - Implementer step 4: `docs/design.md:493`, `docs/prompts/05-implementer.md:10`,
    `factory/prompts/implementer.md:10`: "Make the smallest change that makes them pass for the
    right reason."
  - Code reviewer check 7: `docs/design.md:555`, `docs/prompts/06-code-reviewer.md:21`,
    `factory/prompts/reviewer.md:21`: "Maintainability, only where it will cause real problems.
    Not style."
- Today an implementer or reviewer run is not pointed at any coding standard. I started one of
  each in a throwaway target repository, using a throwaway store (scenario
  implementer-and-reviewer-prompts-name-the-page below), and searched each system prompt for the
  page's path. The output was `implementer standard=[] unfilled=0`, `reviewer standard=[]
  unfilled=0`, `file=absent`. Neither prompt names the page, neither has a placeholder for it,
  and the file is absent.
- The harness fills placeholders only in the shared preamble, the text at the top of every
  agent's prompt. `fill_preamble` in `factory/instance.py` (lines 160–172) fills
  `{writing standard}` with the absolute path of `docs/writing.md` in the running checkout.
  `run_start` in `factory/cli.py` then appends the role's prompt unchanged (line 219). So a
  placeholder written into the implementer or reviewer prompt would reach the agent unfilled
  unless the harness is changed.
- The spec writer has no rule about cutting unneeded parts. Its RULES, at `docs/design.md`
  lines 286–320, cover size, runnable acceptance, open questions, the Problem section and
  revisions. Critic rubric 3 (`docs/design.md:379`) checks size, out-of-scope and "Tests to
  change", but not whether each part is needed.
- The retro's inputs do not mention markers. Its INPUT block is at `docs/design.md:640–648` and
  is copied in `docs/prompts/08-retro.md`. Its Routing table row is at `docs/design.md:127`. The
  build spec's retro input composer is at `dev/build-harness.spec.md:323`, with its acceptance
  item 66 at line 435. `grep -c 'marker ledger'` on those three files prints 0 for each. No retro
  is built: `factory/workflows/` holds only `build.js` and `intake.js`, so the list has no reader
  yet. That is why the operator deferred building it (the operator's first answer, option b).
- The rule 1 example is real code. `ensure_gitignore` in `factory/store.py` creates the store
  directory and writes `.gitignore` itself (lines 59–60). That repeats `write_text`, defined
  just after it in the same module (line 63), which does the same two steps.
- The precedence example is real. `~/dev/nanobot/.agent/design.md:15` is the heading "Prefer
  duplication over premature abstraction". Its text limits the heading to Nanobot's channel and
  provider files.
- The proposed change works as specified. I applied it to a scratch clone of this repository at
  `b33e593`, without the new test file. Every scenario below printed its expected after-state
  there. `git diff --check main...HEAD` exited 0, and the harness suite printed `126 passed`, the
  same count as on `main`. The change came to 149 added and 15 removed lines in 16 files.

## Root cause

No coding standard was ever written. The writing standard (changelog entry 43) gave every role a
page for its prose, with one pointer line in the preamble. No page covers code, and the two
coding prompts carry only the step 4 and check 7 sentences quoted above. The harness fills
`{writing standard}` only in the preamble (`fill_preamble`, `factory/instance.py`), so a role
prompt has no way to name a page by path. The spec-stage cut rule and the retro's list of
`factory:` comments were proposed in the original issue and never made.

## Out of scope

- The verifier prompt, the triage and planner prompts, and the shared preamble.
- Any new role or checker seat. That includes the simplifier from the closed issue that this one
  replaced.
- The code that builds the list of `factory:` comments, and the retro itself (`retro-input`,
  `retro.js`). Both wait for the ticket that builds the retro.
- The `agents/` role-agent templates. They are already out of date with `factory/prompts/`, as
  noted under Out-of-scope observations.
- Fixing the duplication in `ensure_gitignore` that rule 1 uses as its example.
- Rewriting existing code to the new rules.
- Checks 1–6 and 8 of the code reviewer, and its OUTPUT format.
- A behaviour benchmark of the new rules in the shape of ponytail's agentic runs. It is an
  optional Operator step, not acceptance.
- Green (`~/dev/nanobot-upstream`), which runs its own copy of the harness.

## Open questions

none

## Decisions

- **The page has five rules, in the request's order.** Each has `Check:`, `Principle:`, `Before (`
  and `After:` lines. The twin of the writing standard's "Code counterpart:" line is
  `Principle:`, because these rules are already about code. The precedence rule comes before rule
  1, as the operator asked.
- **The page's path reaches the two prompts through a placeholder, `{coding standard}`.** The
  harness fills it when a run starts, with the path of `docs/coding.md` in the running checkout,
  the same way it fills `{writing standard}`. One helper fills both placeholders. The preamble
  uses it, and so does the role prompt, which the harness does not fill today. Two alternatives
  were rejected:
  - Naming the page in the preamble. The preamble is out of scope, and the rescope asks for the
    pointer in the implementer and reviewer prompts only.
  - A repository-relative path. The implementer works in the target repository, which has no
    `docs/coding.md`.
- **Check 7's text is replaced by the pointer, not kept beside it.** Keeping "Maintainability,
  only where it will cause real problems" would leave two checks that overlap. It is also the
  vague check the request says reviewers pad or skip. The cost: the reviewer loses a general
  maintainability check that is not about over-building. Correctness (check 2) and scope (check
  3) still apply.
- **The PR description line for markers lives in rule 3, not in the implementer's PR template.**
  The rescope gives each coding prompt one line only. The implementer's rules already require
  "Disclose every shortcut … in the PR description". Rule 3 says the shortcuts go under Known
  gaps.
- **Tag severities come from the request's part C.** `reuse:` is BLOCKING; `stdlib:`, `native:`,
  `yagni:` and `delete:` are SHOULD-FIX. A finding against rules 2, 3 or 5 takes no tag, and its
  severity is that of a correctness or scope finding. The tag goes after the severity, so the
  reviewer's Findings line keeps its shape. Ponytail's sixth tag, `shrink:`, is not adopted
  (request).
- **The spec-stage cut rule ships in this ticket**, in the spec writer's RULES and as a probe in
  critic rubric 3. The rescope keeps it among the spec writer's rules, not in `docs/coding.md`.
  The probe is reworded from the request's "a part no acceptance item needs is a finding" to "a
  lettered part the ticket's intent does not need is a finding". Read literally, the original
  would push spec writers to add acceptance items for bookkeeping parts such as a changelog
  entry. That is padding, which the anti-Goodharting rules forbid.
- **The list of markers, called the marker ledger, is named as design only (the operator's first answer, option b).**
  The harness builds it from the code on the integration branch when the retro runs. It is not
  appended to the audit log (the append-only record of every run). Markers live in the code, so a
  marker removed since the last retro should drop out. The ledger reads code comments, not
  documents, so the example markers in `docs/coding.md` are not rows.
- **Three of the five examples are labelled "illustration".** The rule 1 example is live code in
  this repository. The rule 2 example comes from ponytail's benchmark, as reported in the
  request. No real factory output matched rules 3, 4 or 5, so their examples are written for the
  page and say so.
- **The `agents/` templates are not changed**, as the writing-standard ticket decided before. Runs
  that read `system-prompt.txt` get the new text.
- **`README.md` gains one row in its files table.** The retro bullet under "Where this can go" is
  unchanged, because it already describes the retro at that level.

## Risk

Blast radius:
- Every implementer and code-reviewer run gains one line and one absolute path. Every spec-writer
  and critic run gains the cut rule.
- Reviewers will raise more findings. A `reuse:` finding blocks the merge, so expect more PR
  rounds at first.
- Critics may return more specs for revision under the rubric 3 probe.
- The change touches `factory/**`, so the harness revision moves. This instance refuses its store
  until the operator accepts the new revision. Nothing reaches a running role before the runtime
  moves (Operator steps).
- Green runs its own copy of the harness and is not affected.

Protected and guardrail paths this change touches:
- **harness (`factory/**`):** `factory/instance.py` (one helper fills both standards' paths),
  `factory/cli.py` (the role prompt is filled), `factory/prompts/implementer.md`,
  `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`.
- **generated (`docs/prompts/**`):** `02-spec-writer.md`, `03-spec-critic.md`,
  `05-implementer.md`, `06-code-reviewer.md`, `08-retro.md`. Each is re-copied from its changed
  design block.
- **Guardrail, agent prompts:** the spec writer, spec critic, implementer, code reviewer and retro
  blocks in `docs/design.md`, plus the copies above.

Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, existing
tests, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Also changed, unprotected: `docs/coding.md` (new), `docs/design.md` (the role-context paragraph at
line 54 and the Routing table's Retro row), `docs/changelog.md` (entry 44),
`dev/build-harness.spec.md` (three sentences), `README.md` (one row), and one new test file under
`tests/factory/`.

## Operator steps

0. **Before step 1: the operator's acceptance test (operator, pre-approved gate, 2026-10-03).** The merge changes nothing until the runtime moves, so the acceptance happens here, not in the merge checks.
   - **Sample.** Two real implementer diffs from this store (for example T-0012.3 and T-0013.1), each with its sub-ticket text.
   - **Review.** A fresh reviewer agent reviews each diff once under the pre-merge reviewer prompt, and once under the merged prompt with `docs/coding.md`. The two finding lists go side by side.
   - **Rewrite.** For one sub-ticket, a fresh implementer re-implements it in a scratch checkout with and without `docs/coding.md`. Both must pass that sub-ticket's acceptance. The diffs are compared on size and on the page's rules.
   - **Operator.** The operator reads a side-by-side page and approves. That approval is this ticket's acceptance. Only then does step 1 run. A rejection goes back as a new ticket; it does not revert the merge, which is inert until the runtime moves.
1. **Upgrade, then accept.** After merge, between tickets, move the runtime to the merge commit
   and accept it on this instance, as the README's "Upgrading the runtime" describes. The runtime
   is the pinned checkout at `~/dev/spec-factory-harness` that runs every ticket. This change
   touches harness code, so `--accept-harness` is required. Until then, no agent sees the change.
2. **Optional: judge the first review.** Read the findings of the first code-reviewer run after
   step 1. Pass: each over-building finding carries a tag after its severity and names what
   replaces the code, and the review ends with `net: -N lines possible` or `Lean already.`.
   A failure goes into a follow-up issue; it does not revert this change. A deeper check is a
   seeded repository in the shape of ponytail's benchmark: a shared `_debit()` and a ticket that
   names one caller, built with and without the page, on Opus or Sonnet. That is the operator's
   call and not part of this ticket.

=== design.md
## Proposed change

The parts are listed in dependency order. B needs A's file, C needs B's placeholder, and every
part's acceptance is listed in `verification.md`. Wrap prose at no more than 100 characters, as
the documents do now. The prompt blocks keep their narrower wrap, and table rows in
`docs/coding.md` may run past 100.

**A. `docs/coding.md` (new).** This exact text. Rewrapping is allowed; the gate fixes the wording.

```markdown
# Coding standard

A coding agent tends to build more than its ticket needs: a new helper beside one that already
exists, hand-rolled code for something the standard library ships, an interface with one
implementation. The operator pays for each at the gate, in a bigger diff, and later owns the
duplicate code. This page is how the spec factory's implementer (the role that writes the code for
one sub-ticket) and its code reviewer (the role that judges that code before it merges) keep a
change as small as the ticket allows. It is the twin of the writing standard, `docs/writing.md`:
the same format, and where both pages name a principle, they name the same one.

**Precedence.** A target repository's own instructions win where they disagree with this page.
They are in its `AGENTS.md` and the documents that file points to. Example: Nanobot's
`.agent/design.md` says "Prefer duplication over premature abstraction" for its channel and
provider files. In those files DRY (rule 1) gives way, and a repeated block is not a `reuse:`
finding (rule 4).

Each rule below is one you can check in your own output before you hand it in: the implementer
in its diff and PR description, the reviewer in its findings. Each names its code-design
principle and has an example and its rewrite. An example marked "illustration" was written for
this page; the others are sourced.

## 1. Reuse before writing: take the first rung that holds.
Check: for each function, class, type or dependency your diff adds, you can name the rung it sits
on and say why no earlier rung held.
1. A helper, util, type or pattern already in this repo.
2. The standard library.
3. A native platform feature: a database constraint over app code, an atomic file-system call
   over a lock.
4. A dependency already installed.
5. One line.
6. The minimum code that works.
Whether the thing should exist at all is the spec's question, not the implementer's: the spec
writer cuts any part the ticket does not need.
Principle: DRY, don't repeat yourself (Hunt and Thomas, The Pragmatic Programmer).
Before (`factory/store.py`, `ensure_gitignore`, as of 2026-10-03): it creates the store directory
and writes `.gitignore` with its own two lines, which repeat `write_text` in the same module.
After: it calls `write_text`, so a later change to how the store writes files, such as its
encoding or an atomic replace, reaches `.gitignore` too.

## 2. Fix the shared function once: grep every caller before you edit.
Check: for each existing function your diff changes, your PR description names its callers, found
by a grep of the repo, and says why the fix sits where it does.
Principle: single responsibility, and root cause over symptom: a ticket names a symptom, and the
fix goes where the cause is, once.
Before (ponytail's comprehension benchmark, 2026-06-22: a seeded `bank.py` where `transfer()` and
`withdraw()` share `_debit()`, and the bug report names only transfers): told to "trace the flow
end to end", Opus scored 0 of 3. Patching only `transfer()` leaves `withdraw()` broken.
After: told to "grep every caller of the function you touch; fix the shared function once",
Sonnet 4.6 and Opus 4.8 scored 6 of 6, against a baseline of 1 of 6. One guard in `_debit()` is a
smaller diff than one per caller.

## 3. A deliberate shortcut carries a `factory:` comment naming its limit and upgrade trigger.
Check: each simplification in your diff with a known limit (a global lock, an O(n²) scan, a naive
heuristic) has a comment starting `factory:` that names the limit and when to upgrade. Your PR
description's Known gaps lists each marker you added, or says "factory: markers added: none".
Principle: technical-debt bookkeeping; debt taken on purpose is recorded where it lives
(Cunningham's debt metaphor).
Before (illustration): `with ACCOUNTS_LOCK:` around every account update, with no comment, so
the next reader cannot tell a choice from an oversight.
After: `# factory: one global lock; per-account locks if transfers contend` above it. The marker
is greppable: `grep -rnE '(#|//|/\*) ?factory:'` lists every one in the code.

## 4. A reviewer's over-building finding carries one tag and names what replaces the code.
Check: each over-building finding (code the change could have reused, or did not need) starts,
after its severity, with one tag from the table (`[BLOCKING] reuse: file:line: problem →
consequence`), names what the table says to name, and has the table's severity. A finding against
rule 2, 3 or 5 takes no tag; it earns its severity as a correctness or scope finding. The pass ends
with `net: -N lines possible`, where N is the lines the tagged findings would remove, or with
`Lean already.`
Principle: per tag, in the table.

| Tag | Flags | Names | Severity | Principle |
|---|---|---|---|---|
| `reuse:` | a helper, type or pattern this repo already has | its path | BLOCKING | DRY |
| `stdlib:` | code the standard library ships | the function | SHOULD-FIX | don't reinvent |
| `native:` | code or a dependency doing the platform's job | the feature | SHOULD-FIX | don't reinvent |
| `yagni:` | an abstraction, setting or layer with one use | what it folds into | SHOULD-FIX | YAGNI |
| `delete:` | dead code, unused flexibility, a speculative feature | nothing | SHOULD-FIX | dead code |

Before (illustration): "Maintainability: some duplication in the store module; consider
refactoring."
After: "[BLOCKING] reuse: factory/store.py:59: `ensure_gitignore` repeats `write_text` → a change
to how the store writes files misses `.gitignore`; call `write_text`." Then "net: -1 lines
possible".

## 5. One name per concept, from spec to code.
Check: each term your spec defines (in its Problem section; for the factory itself, in the
README's terms table) is the identifier your code uses for that concept, and no identifier you add
is a synonym for one the repo already has.
Principle: ubiquitous language (Evans, Domain-Driven Design), the same principle as the writing
standard's rule 9.
Before (illustration): the README's terms table defines a "parked" ticket, and a change adds the
state `on_hold` and a function `hold_ticket()` for the same thing.
After: the state stays `parked` and the command stays `ticket park`, the names the store and the
README already use.

The check order (rule 1) and the tag vocabulary (rule 4) are adapted from ponytail
(DietrichGebert/ponytail, MIT), as the design document's changelog records.
```

**B. Pointer lines (implementer and code reviewer).** Make the same edit in `docs/design.md`
(§5 Implementer, §6 Code reviewer), `docs/prompts/05-implementer.md`,
`docs/prompts/06-code-reviewer.md`, `factory/prompts/implementer.md` and
`factory/prompts/reviewer.md`.
- Implementer PROCESS step 4: keep its line, and add one line under it:
  ```
  4. Make the smallest change that makes them pass for the right reason.
     Follow the coding standard at {coding standard}.
  ```
- Code reviewer CHECK 7: replace `7. Maintainability, only where it will cause real problems. Not
  style.` with:
  ```
  7. The coding standard at {coding standard}: a finding against it
     carries the tag and severity the standard gives it. Not style.
  ```

**C. The harness fills `{coding standard}`.**
- In `factory/instance.py`, add `fill_standards(text)` next to `fill_preamble`. It replaces
  `{writing standard}` with `HARNESS / "docs" / "writing.md"` and `{coding standard}` with
  `HARNESS / "docs" / "coding.md"`, both as absolute paths. `fill_preamble` calls it in place of
  its own `{writing standard}` line, and its docstring points there.
- In `factory/cli.py` `run_start`, pass the role prompt through `instance.fill_standards` before
  appending it to the preamble.
- Rejected: a second, separate `.replace` in `cli.py`. It would repeat the path logic, against
  rule 1 of the new page.

**D. Spec-stage cut.** Make the same edit in `docs/design.md`, `docs/prompts/02-spec-writer.md`
and `factory/prompts/spec_writer.md` for the writer, and in `docs/design.md`,
`docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md` for the critic.
- Spec writer RULES: directly after the Size rule (the one ending "seams as lettered parts under
  Proposed change."), add:
  ```
  - Cut before you specify: for each part, ask first whether the ticket's
    intent needs it at all. A speculative part is cut, and named in one
    line under Out of scope.
  ```
- Critic rubric 3: its last line `   breaks, with a reason each.` becomes:
  ```
     breaks, with a reason each; a lettered part the ticket's intent does
     not need is a finding.
  ```

**E. The retro's input names the marker ledger.** Text only; no code.
- Retro INPUT, in `docs/design.md` §8 and re-copied to `docs/prompts/08-retro.md`. After the line
  `is how you propose a model change.`, add:
  ```
  Also the marker ledger: one row per `factory:` comment in the code on
  the integration branch (a shortcut its author marked, per the coding
  standard), with its file:line, the limit it names and its upgrade
  trigger, flagged no-trigger where it names none.
  ```
- The Routing table's Retro row (`docs/design.md:127`). Its Receives cell ends "…for the period
  and for each prior proposal's window". Append: `, and the marker ledger: one row per `factory:`
  comment in the code on the integration branch, with file:line, limit and upgrade trigger,
  flagged `no-trigger` where it names none, composed by the harness when the retro runs`.
- `dev/build-harness.spec.md:323`, the `retro-input` sentence. Replace "and run and outcome counts
  per `(role, model)` from `runs/*/meta.yaml` and `log/`;" with "run and outcome counts per
  `(role, model)` from `runs/*/meta.yaml` and `log/`, and the marker ledger (one row per
  `factory:` comment in the code on `main`: file:line, limit, upgrade trigger, and `no-trigger`
  where the comment names none);".
- `dev/build-harness.spec.md` item 66 (line 435). After "`counts per role` (one line per `(role,
  model)`, item 72)", add ", `marker ledger` (one row per `factory:` code comment on `main`; a
  comment naming no upgrade trigger carries `no-trigger`)".

**F. Records and a test.**
- `docs/design.md:54`, the role-context paragraph. After its last sentence, which ends "…and
  `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it.",
  add: "`{coding standard}`, in the implementer and code reviewer prompts, is filled the same way
  with the path of `docs/coding.md` in that checkout."
- `dev/build-harness.spec.md:158`. After "with the absolute path of its `docs/writing.md`", add ",
  and `{coding standard}`, in the implementer and code-reviewer prompts, with the absolute path of
  its `docs/coding.md`".
- `docs/changelog.md`: entry 44, after entry 43 and before the "Declined:" line. It says what
  the page holds (five rules, the precedence rule, the tags and their severities), the two
  pointer lines and the `{coding standard}` fill, that check 7's old text is replaced, the spec
  writer's cut rule and the critic's probe, and that the marker ledger is design whose producer
  waits for the retro. It credits ponytail (DietrichGebert/ponytail, MIT) for the check order
  and the tag vocabulary.
- `README.md`, "Where things live". After the `docs/writing.md` row, add:
  `| `docs/coding.md` | The coding standard for the implementer and code reviewer; their prompts
  name the runtime's copy |`.
- One new test file, `tests/factory/test_coding_standard.py`, driven through `bin/factory` as
  `tests/factory/test_writing_standard.py` is. It checks:
  - an implementer run's and a reviewer run's system prompt name the running checkout's
    `docs/coding.md`, with no `{coding standard}` left unfilled;
  - the spec writer, implementer and retro design blocks equal their `docs/prompts/` copies.

## Tests to change

none. The two existing tests that read prompt text still pass unchanged. The scratch-clone trial
ran the suite with every part except the new test file applied, and it printed `126 passed`:
- `test_design_block_equals_its_prompt_copy` covers the critic and reviewer blocks, and both
  copies change together.
- `test_system_prompt_is_the_design_preamble_filled_from_the_instance` uses the triage role,
  whose prompt has no placeholder.

=== specs/coding-standard/spec.md
## ADDED Requirements

### Requirement: coding-standard-page-of-checkable-rules
The repository SHALL have `docs/coding.md`, which states a precedence rule before its first rule
and holds five numbered rules, each with one `Check:`, one `Principle:`, one `Before (` and one
`After:` line.

#### Scenario: coding-page-has-five-checkable-rules
- WHEN (bash, from `~/dev/spec-factory`) `if [ -f docs/coding.md ]; then f=docs/coding.md; echo "rules=$(grep -o '^## [0-9]*\.' $f | tr -dc '0-9\n' | paste -sd, -) check=$(grep -c '^Check: ' $f) principle=$(grep -c '^Principle: ' $f) before=$(grep -c '^Before (' $f) after=$(grep -c '^After: ' $f) precedence=$(awk '/^\*\*Precedence\.\*\*/ {p=NR} /^## 1\./ {r=NR} END {print (p && p < r) ? "first" : "absent"}' $f)"; else echo missing; fi`
- THEN it prints `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first`

### Requirement: coding-standard-carries-the-requested-rules
`docs/coding.md` MUST contain the precedence example, the grep-every-caller rule, the `factory:`
marker, the five reviewer tags, both closing lines of a review pass, and the principles DRY,
YAGNI and ubiquitous language.

#### Scenario: coding-page-has-every-requested-phrase
- WHEN (bash, from `~/dev/spec-factory`) `b=$(printf '\140'); n=0; for h in 'Prefer duplication over premature abstraction' 'grep every caller' "${b}factory:${b}" "${b}reuse:${b}" "${b}stdlib:${b}" "${b}native:${b}" "${b}yagni:${b}" "${b}delete:${b}" 'net: -N lines possible' 'Lean already.' 'ubiquitous language' 'DRY' 'YAGNI'; do if cat docs/coding.md 2>/dev/null | tr '\n' ' ' | grep -qF "$h"; then n=$((n+1)); else echo "missing: $h"; fi; done; echo "found=$n of 13"`
- THEN it prints only `found=13 of 13`

### Requirement: reviewer-tag-severities
The tag table in `docs/coding.md` SHALL give `reuse:` the severity BLOCKING and `stdlib:`,
`native:`, `yagni:` and `delete:` the severity SHOULD-FIX.

#### Scenario: tag-table-severities
- WHEN (bash, from `~/dev/spec-factory`) `b=$(printf '\140'); for t in reuse stdlib native yagni delete; do printf '%s=%s ' "$t" "$(grep -E "^\| ${b}$t:${b} \|" docs/coding.md 2>/dev/null | grep -oE 'BLOCKING|SHOULD-FIX' | paste -sd+ -)"; done; echo`
- THEN it prints `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX` (a trailing space is allowed)

### Requirement: implementer-and-reviewer-point-to-the-page
The implementer's PROCESS step 4 and the code reviewer's CHECK 7 SHALL each name the coding
standard through `{coding standard}`, in all three copies of each prompt, and check 7's old
"Maintainability, only where" text MUST be gone.

#### Scenario: pointer-line-in-every-copy
- WHEN (bash, from `~/dev/spec-factory`) `grep -cF 'Follow the coding standard at {coding standard}.' docs/design.md docs/prompts/05-implementer.md factory/prompts/implementer.md; grep -cF '7. The coding standard at {coding standard}' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; grep -cF 'Maintainability, only where' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md`
- THEN the first six lines each end `:1` and the last three each end `:0`

### Requirement: run-prompts-name-the-running-checkouts-page
When an implementer or code-reviewer run starts, its system prompt MUST name the absolute path of
`docs/coding.md` in the running harness checkout, with no `{coding standard}` placeholder left.

#### Scenario: implementer-and-reviewer-prompts-name-the-page
- GIVEN a scratch target repository with an instance and a throwaway store, with the ticket's status set by `ticket set` so that each role can start
- WHEN (bash, from `~/dev/spec-factory`) `H=$(pwd -P); T=$(mktemp -d); git -C "$T" init -q -b main; git -C "$T" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init; printf '# demo\n\nDo the thing.\n' > "$T/r.md"; F() { (cd "$T" && env -u FACTORY_INSTANCE -u FACTORY_REPO -u FACTORY_INTEGRATION_BRANCH "$@"); }; F env -u FACTORY_STATE "$H/bin/factory" init --repo-name demo >/dev/null 2>&1; S="$T/s"; X() { F env FACTORY_STATE="$S" "$H/bin/factory" "$@" >/dev/null; }; X ticket new --file "$T/r.md"; X ticket set T-0001 status=ready-for-implementer; X run start --role implementer --ticket T-0001 --model opus; X ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git -C "$T" rev-parse HEAD); X run start --role reviewer --ticket T-0001 --model opus; for r in implementer reviewer; do P=$(ls "$S"/runs/*-$r/system-prompt.txt); echo "$r standard=[$(grep -oF "$H/docs/coding.md" "$P" | head -1)] unfilled=$(grep -c '{coding standard}' "$P")"; done; echo "file=$(test -s "$H/docs/coding.md" && echo present || echo absent)"; rm -rf "$T"`
- THEN it prints `implementer standard=[<checkout>/docs/coding.md] unfilled=0`, `reviewer standard=[<checkout>/docs/coding.md] unfilled=0` and `file=present`, where `<checkout>` is the absolute path of the checkout it ran in

=== specs/spec-writer/spec.md
## ADDED Requirements

### Requirement: spec-stage-cut
The spec writer's RULES SHALL tell it to cut any part the ticket's intent does not need, and
critic rubric 3 SHALL make such a part a finding, in all three copies of each prompt.

#### Scenario: cut-rule-and-probe-in-every-copy
- WHEN (bash, from `~/dev/spec-factory`) `grep -cF -- '- Cut before you specify: for each part' docs/design.md docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; grep -cF 'a lettered part the ticket' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`
- THEN it prints six lines, each ending `:1`

=== specs/retro/spec.md
## ADDED Requirements

### Requirement: retro-input-names-the-marker-ledger
The retro's INPUT block, its Routing table row and the build spec's retro input composer SHALL
name the marker ledger, one row per `factory:` comment in the code on the integration branch.

#### Scenario: marker-ledger-named-in-design-and-build-spec
- WHEN (bash, from `~/dev/spec-factory`) `echo "design=$(grep -c 'marker ledger' docs/design.md) retro=$(grep -c 'marker ledger' docs/prompts/08-retro.md) buildspec=$(grep -c 'marker ledger' dev/build-harness.spec.md) row=$(grep '^| Weekly audit done' docs/design.md | grep -c 'marker ledger')"`
- THEN it prints `design=2 retro=1 buildspec=2 row=1`

=== specs/design-doc/spec.md
## ADDED Requirements

### Requirement: prompt-copies-stay-verbatim
Every changed prompt block in `docs/design.md` MUST equal its `docs/prompts/` copy byte for
byte. The harness copies under `factory/prompts/` MUST differ from those copies only in the
placeholders they already fill.

#### Scenario: changed-blocks-verbatim-and-harness-copies-in-step
- WHEN (bash, from `~/dev/spec-factory`) `q=$(printf '\140\140\140'); for s in "2. Spec writer:02-spec-writer" "3. Spec critic:03-spec-critic" "5. Implementer:05-implementer" "6. Code reviewer:06-code-reviewer" "8. Retro:08-retro"; do f=${s##*:}; sed -n "/^## ${s%%:*}\$/,/^$q\$/p" docs/design.md | sed "1,/^${q}text\$/d;\$d" | cmp -s - docs/prompts/$f.md && echo "$f verbatim" || echo "$f differs"; done; for p in "02-spec-writer spec_writer" "03-spec-critic critic" "05-implementer implementer" "06-code-reviewer reviewer"; do set -- $p; printf '%s-diff=%s ' "$2" "$(diff docs/prompts/$1.md factory/prompts/$2.md | grep -c '^[<>]')"; done; echo`
- THEN it prints five `verbatim` lines, then `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2` (a trailing space is allowed)

### Requirement: design-records-follow-the-change
The changelog SHALL have an entry naming `docs/coding.md`. The design doc and the build spec
SHALL say how `{coding standard}` is filled. `README.md`'s files table SHALL list
`docs/coding.md`.

#### Scenario: records-name-the-coding-standard
- WHEN (bash, from `~/dev/spec-factory`) `echo "changelog=$(grep -E '^[0-9]+\. ' docs/changelog.md | grep -c 'docs/coding.md') design=$(grep -c '{coding standard}' docs/design.md) buildspec=$(grep -c '{coding standard}' dev/build-harness.spec.md) row=$(grep -c '^| .docs/coding.md. |' README.md)"`
- THEN it prints `changelog=1 design=3 buildspec=1 row=1`

### Requirement: harness-gates-still-pass
The instance's gate commands MUST pass on the change.

#### Scenario: gates-pass
- WHEN (bash, from `~/dev/spec-factory`) `git diff --check main...HEAD; echo "check=$?"; uv run --frozen pytest -q -p no:cacheprovider tests/factory`
- THEN it prints `check=0`, and pytest ends with `N passed` and no failures or errors

=== verification.md
## Acceptance

- coding-page-has-five-checkable-rules → NEW. Today it prints `missing`, because
  `docs/coding.md` does not exist.
- coding-page-has-every-requested-phrase → NEW. Today it prints thirteen `missing: …` lines and
  `found=0 of 13`, because the file does not exist.
- tag-table-severities → NEW. Today it prints `reuse= stdlib= native= yagni= delete=`: there is no
  tag table to read.
- pointer-line-in-every-copy → NEW. Today the first six lines end `:0`, because no prompt names a
  coding standard. The last three end `:1`, because check 7 still says "Maintainability, only
  where".
- implementer-and-reviewer-prompts-name-the-page → NEW. Today it prints `implementer
  standard=[] unfilled=0`, `reviewer standard=[] unfilled=0` and `file=absent`.
  - Both runs do start; the failure is the missing path and file, not the setup.
  - `unfilled=0` today is not a pass: there is no placeholder yet.
  - A wrong fix fails here. One that adds the placeholder without the harness fill (part C)
    prints `standard=[] unfilled=1`. One that fills the path from somewhere other than the
    running checkout prints a different path.
  - It uses a throwaway store, so the harness lock does not apply.
- cut-rule-and-probe-in-every-copy → NEW. Today all six lines end `:0`.
- marker-ledger-named-in-design-and-build-spec → NEW. Today it prints `design=0 retro=0
  buildspec=0 row=0`.
- changed-blocks-verbatim-and-harness-copies-in-step → REGRESSION. Today it prints the five
  `verbatim` lines and `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2`. It
  must print the same after the change. That means every changed block is re-copied to
  `docs/prompts/`, and each `factory/prompts/` copy takes the same edit and still differs only in
  the placeholders it fills (`{400}`, `{2}`, `{gate commands}`, `{force-push allowed}`).
- records-name-the-coding-standard → NEW. Today it prints `changelog=0 design=0 buildspec=0
  row=0`.
- gates-pass → REGRESSION. Today it prints `check=0` and `126 passed`. After the change the count
  rises by the new test file's tests.

How verified:
- Base: I ran every WHEN above verbatim in `~/dev/spec-factory` at `b33e593` and copied the
  "today" results above from that output.
- After-state: I made the change in a scratch clone of the same commit. The edits were `docs/coding.md`
  as in part A and parts B–F, without the new test file. I ran every WHEN there, and each printed
  the THEN given above:
  - `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first`;
  - `found=13 of 13`;
  - the five severities;
  - `:1` ×6 then `:0` ×3;
  - both runs naming `<clone>/docs/coding.md` with `unfilled=0`, and `file=present`;
  - `:1` ×6;
  - `design=2 retro=1 buildspec=2 row=1`;
  - five `verbatim` lines and unchanged diff counts;
  - `changelog=1 design=3 buildspec=1 row=1`;
  - `check=0`, and the suite at `126 passed`.
- The clone was outside the repository. Nothing in `~/dev/spec-factory` changed except this output
  file.

Not an acceptance item: whether a live reviewer actually tags its findings, or whether an
implementer actually guards a shared function. Both need model runs on the upgraded runtime. The
operator judges them (Operator step 2).

Out-of-scope observations:
- The `agents/` templates have drifted further from `factory/prompts/`. They lack the critic's
  rubric 2 and 6 text, and the spec writer's Problem-section and acceptance-item rules. This
  change adds two more differences: the spec writer's cut rule and the critic's probe. The fix noted after the writing
  standard still applies: regenerate the templates from `factory/prompts/`, or make each one a
  pointer only.
- `dev/build-harness.spec.md:158` describes `factory render` and `render --check` as if built.
  This harness has no `render` command (`factory/cli.py` registers none), and the README lists it
  under "Not built".
- `ensure_gitignore` in `factory/store.py` repeats `write_text` (rule 1's example). It is a
  one-line cleanup for its own ticket.
- Changelog entry 43 still says the writing standard "holds eight rules"; it has twelve since rules
  9–12 merged.

## PR description (the implementer's output)

Sub-ticket: T-0015.1, "Add the coding standard and point the implementer, reviewer, spec writer, critic and retro at it" (parent T-0015, issue #20, approved spec v2). Branch `factory/T-0015.1`, head `27d6d63fcb2f5c03d64696f6769abf871e4f2bc0`, base `61d92bef32d05c89bb9187f8455f4eb298b2a99f`, one commit. Worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0015.1`.

## What changed

The factory's two coding roles now get a coding standard, a page that tells them how to keep a change as small as the ticket allows. The implementer is the agent that writes the code for one sub-ticket. The code reviewer is the agent that judges that code before it merges. Before this change, neither role's prompt named any coding standard. A smaller rule tells the spec writer to cut parts the ticket does not need. The retro is the planned agent that proposes prompt changes. Its design now lists `factory:` comments as one of its inputs. 17 files, 235 lines added and 15 removed (`git diff --stat main...HEAD`).

- **A. The page.** `docs/coding.md` is new. Its text is byte-identical to the block in the parent's part A: `diff` of the spec block against the file printed nothing. It opens with a precedence rule: a target repository's own instructions win where they disagree with the page. It then has five rules, each with a `Check:`, `Principle:`, `Before (` and `After:` line. The five rules are reuse before writing, grep every caller, `factory:` shortcut markers, tagged review findings, and one name per concept.
- **B. Pointer lines.** Implementer step 4 keeps its sentence and gains `Follow the coding standard at {coding standard}.` Code reviewer check 7, "Maintainability, only where it will cause real problems. Not style.", is replaced by a check against the coding standard, with the tag and severity the page gives. Each edit is in all three copies: `docs/design.md`, `docs/prompts/` and `factory/prompts/`.
- **C. The harness fills the path.** `{coding standard}` is a placeholder that the harness must replace with a real path when a run starts. `factory/instance.py` gains `fill_standards(text)`. It replaces `{writing standard}` and `{coding standard}` with the absolute paths of `docs/writing.md` and `docs/coding.md` in the running harness checkout. `fill_preamble` now calls it in place of its own `{writing standard}` line. `run_start` in `factory/cli.py` now passes the role prompt through it before appending it to the preamble. Before this change, the role prompt was appended unfilled. `fill_preamble` has one caller, `factory/cli.py:218` (`grep -rn fill_preamble --include='*.py' --include='*.js' .`). After the change the only placeholders in `factory/prompts/` are the two coding-standard lines and the preamble's writing-standard line.
- **D. Spec-stage cut.** The spec writer's RULES gain "Cut before you specify…" directly after the Size rule. Critic rubric 3 ends "…; a lettered part the ticket's intent does not need is a finding." Each edit is in all three copies.
- **E. The marker ledger, text only.** The marker ledger is the retro's planned list of every `factory:` comment in the code. It is now named in three places: the retro's INPUT block (`docs/design.md` §8, re-copied to `docs/prompts/08-retro.md`), the Routing table's Retro row, and the build spec's `retro-input` sentence and item 66. No code builds the ledger yet.
- **F. Records and test.** Three records now say how `{coding standard}` is filled: `docs/design.md`'s role-context paragraph, `dev/build-harness.spec.md`'s placeholder sentence and changelog entry 44. Entry 44 sits after 43 and before "Declined:", and it credits ponytail. `README.md` gains one row after the `docs/writing.md` row. The new test file is `tests/factory/test_coding_standard.py`.

The edits were applied by a script that refused to change a file unless its anchor text occurred exactly once. No edit was placed by line number.

## Acceptance results

The commands were run verbatim from the worktree on its branch. The "before" results come from the worktree at `61d92be`, before any edit, and match the spec's "today" results. The "after" results come from committed head `27d6d63`.

| # | Scenario | Before | After |
|---|---|---|---|
| 1 | coding-page-has-five-checkable-rules (NEW) | `missing` | `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first` |
| 2 | coding-page-has-every-requested-phrase (NEW) | 13 `missing: …` lines, `found=0 of 13` | only `found=13 of 13` |
| 3 | tag-table-severities (NEW) | `reuse= stdlib= native= yagni= delete= ` | `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX ` |
| 4 | pointer-line-in-every-copy (NEW) | six lines end `:0`, the last three `:1` | six lines end `:1`, the last three `:0` |
| 5 | implementer-and-reviewer-prompts-name-the-page (NEW) | `implementer standard=[] unfilled=0`, `reviewer standard=[] unfilled=0`, `file=absent` | `implementer standard=[/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0015.1/docs/coding.md] unfilled=0`, the same path for `reviewer`, `file=present` |
| 6 | cut-rule-and-probe-in-every-copy (NEW) | six lines `:0` | six lines `:1` |
| 7 | marker-ledger-named-in-design-and-build-spec (NEW) | `design=0 retro=0 buildspec=0 row=0` | `design=2 retro=1 buildspec=2 row=1` |
| 8 | changed-blocks-verbatim-and-harness-copies-in-step (REGRESSION) | five `verbatim` lines, then `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2` | the same |
| 9 | records-name-the-coding-standard (NEW) | `changelog=0 design=0 buildspec=0 row=0` | `changelog=1 design=3 buildspec=1 row=1` |
| 10 | gates-pass (REGRESSION) | `check=0`, `126 passed in 101.27s` | `check=0`, `131 passed in 83.81s` |
| 11 | the new test file on its own (NEW) | see below | `5 passed in 0.36s` |

What each result means:
- Row 5 shows that both live prompts carry the absolute path of the checkout they ran from, with no placeholder left.
- Row 8 shows that every changed design block still equals its `docs/prompts/` copy byte for byte. Each `factory/prompts/` copy still differs from it only in the placeholders the harness already fills.
- Row 10: the suite count rose from 126 to 131, which is exactly the five new tests.

Criterion 11 also asks that the new tests fail where the change is missing. I ran them in two states:
- **Pages and pointer lines in place, harness fill not yet written** (parts A and B, without C). This was the real red step of this ticket, and the failure is the one the spec names. The two prompt-path tests failed because the prompt still held `{coding standard}`, so `Follow the coding standard at <checkout>/docs/coding.md.` was not in the implementer's prompt (`2 failed, 3 passed`).
- **`main`'s files.** I made a scratch clone of `main` at `61d92be` in my scratchpad, outside the repo, and copied in only the new test file. The two prompt-path tests failed on `assert (True and False)`, because `docs/coding.md` does not exist there (`2 failed, 3 passed`). I deleted the clone afterwards.

Both gate commands, run exactly as written from the worktree: `git diff --check main...HEAD` exited 0, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `131 passed`.

## Tests added/changed

- Added `tests/factory/test_coding_standard.py`, a new file. It drives `bin/factory` in a scratch target repository on a throwaway store, as `test_writing_standard.py` does.
  - `test_run_prompt_names_the_running_checkouts_coding_standard[implementer|reviewer]` (2 tests). These check the spec's first bullet. Each run's system prompt contains the filled pointer line with the absolute path of the running checkout's `docs/coding.md`, the file exists and is not empty, and no `{coding standard}` is left. The ticket's status is set with `ticket set` so that each role can start, as in scenario 5.
  - `test_changed_design_block_equals_its_prompt_copy[2. Spec writer|5. Implementer|8. Retro]` (3 tests). These check the spec's second bullet: the three changed design blocks that `test_writing_standard.py` does not already cover equal their `docs/prompts/` copies.
- Changed: none. No existing test file was touched (`git diff --stat main...HEAD -- tests/` lists only the new file). `test_design_block_equals_its_prompt_copy` and `test_system_prompt_is_the_design_preamble_filled_from_the_instance` pass unchanged.

## Known gaps and uncertainties

- **The three block-equality tests pass on `main`.** They are regression guards, like the existing `test_design_block_equals_its_prompt_copy`. Each one fails only if a future edit changes a design block without re-copying it. Criterion 11 requires only the prompt-path tests to fail on `main`, and they do. A strict reading of "a test that passes on `main` checks nothing" would flag these three. The spec's part F asks for them anyway, so I kept them and am saying so here.
- **The new README row describes the system before it runs.** The row says the two prompts "name the runtime's copy". The runtime is the pinned checkout that runs every ticket, and that statement holds only after the operator moves it to this merge and accepts it (the parent's Operator step 1). The README's "Ground truth only" rule says a thing appears above "Where this can go" only after it has run on a real ticket. The existing `docs/writing.md` row has the same timing. The spec asks for this row in this ticket, so I added it as specified. The README's status date is already 2026-10-03, so no date bump was needed.
- **Backticks in the Routing table's Retro row.** The spec quoted the appended text inside backticks that also contain backticked `factory:` and `no-trigger`. I read the outer backticks as quotation marks and kept the inner ones as code formatting. Scenario 7 does not depend on this choice.
- **Changelog entry 44's wording is mine.** The spec lists what the entry must say, not its text. It names `docs/coding.md`, the precedence rule, the five rules, the tags and their severities, both pointer lines, the `{coding standard}` fill, the removal of check 7's old text, the cut rule and the critic's probe, the marker ledger as design only, and ponytail (DietrichGebert/ponytail, MIT).
- **Not verified here: live behaviour.** The parent leaves two questions to the operator: whether a live reviewer tags its findings, and whether a live implementer guards a shared function (Operator steps 0 and 2). No running agent sees this change until the runtime moves (Operator step 1).
- factory: markers added: none.

## Out-of-scope observations

- None beyond the parent's own list: the drifted `agents/` templates, the unbuilt `render` command described at `dev/build-harness.spec.md:158`, the `ensure_gitignore` duplication in `factory/store.py`, and changelog entry 43's "eight rules". This change adds the two further `agents/` drifts the parent predicted: the spec writer's cut rule and the critic's probe.
- This repository has no `AGENTS.md` at its root, so step 1 of my process had none to read. That is consistent with the briefing, which names `README.md` as the current-state page.

## Responses to findings

Round 1: none.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 11 acceptance criteria and both gates were run on the committed head and printed the expected results. The new prompt-path tests were seen to fail both without the harness fill and on `main`.
ESCALATIONS: none

## Diff `61d92bef32d05c89bb9187f8455f4eb298b2a99f...27d6d63fcb2f5c03d64696f6769abf871e4f2bc0`

diff --git a/README.md b/README.md
index e27e121..c4cfdf4 100644
--- a/README.md
+++ b/README.md
@@ -347,6 +347,7 @@ from `docs/design.md` and changes only when the design does.*
 | `docs/changelog.md` | The design document's changelog |
 | `docs/prompts/` | Each role's prompt block, copied verbatim from the design doc by hand; `00-preamble.md` goes at the top of every role |
 | `docs/writing.md` | The writing standard for every section a person reads; the preamble names the runtime's copy |
+| `docs/coding.md` | The coding standard for the implementer and code reviewer; their prompts name the runtime's copy |
 | `dev/` | Working documents from building the factory: the build spec, its plan, the P0 walking skeleton, the issue index (`dev/issues.md`) |
 | `factory/` | The harness package: the store CLI, its role prompts and its two workflow scripts (`factory/workflows/`) |
 | `bin/factory` | The harness entry point |
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 2f1fa1d..bf9c79c 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -155,7 +155,7 @@ State on branch `tickets` of the bare repo (the ticket store, doc §Harness tabl
 
 - `pyproject.toml`: console script `factory = factory.cli:main`; dependency `pyyaml`; dev `pytest`, `ruff`, `mypy`.
 - `factory/cli.py`: subcommands per part; exit 0 success, 2 refused precondition, 1 error; one audit event (C) per state change.
-- `factory render`: reads `docs/design.md`, which is in the same repo as the harness (`render` reads no other path and still has no `--doc` option), and writes `docs/prompts/` and the `agents/` templates from its prompt blocks, plus **one added rule in the Triage and Spec-writer definitions** (addendum 2): "Acceptance items describe behaviour (a command a user or operator could run, or Given/When/Then) and never name a test function, class, or internal symbol; symbols belong under Root cause and Proposed change." The placeholders (`{repo name}`, protected paths, `{2}`, `{400}`, `{gate commands}`, `{3}`, `{5}`, `{force-push allowed}`) are filled per instance from `.factory/instance.yaml` when a run starts; `{writing standard}` is filled at the same time from the running harness checkout, not from `instance.yaml`, with the absolute path of its `docs/writing.md`. The doc text itself is copied verbatim and otherwise never edited by this ticket; `factory render --check` diffs the rendered bodies back against `docs/design.md` (the verbatim check the plan's BH-4 cites; item 82).
+- `factory render`: reads `docs/design.md`, which is in the same repo as the harness (`render` reads no other path and still has no `--doc` option), and writes `docs/prompts/` and the `agents/` templates from its prompt blocks, plus **one added rule in the Triage and Spec-writer definitions** (addendum 2): "Acceptance items describe behaviour (a command a user or operator could run, or Given/When/Then) and never name a test function, class, or internal symbol; symbols belong under Root cause and Proposed change." The placeholders (`{repo name}`, protected paths, `{2}`, `{400}`, `{gate commands}`, `{3}`, `{5}`, `{force-push allowed}`) are filled per instance from `.factory/instance.yaml` when a run starts; `{writing standard}` is filled at the same time from the running harness checkout, not from `instance.yaml`, with the absolute path of its `docs/writing.md`, and `{coding standard}`, in the implementer and code-reviewer prompts, with the absolute path of its `docs/coding.md`. The doc text itself is copied verbatim and otherwise never edited by this ticket; `factory render --check` diffs the rendered bodies back against `docs/design.md` (the verbatim check the plan's BH-4 cites; item 82).
 - `.claude/skills/factory/SKILL.md`: how to run `factory intake`, then `Workflow({scriptPath: 'factory/workflows/intake.js', args: {ticket: ID, stubs?: dir}})`, approve at the gate, then `Workflow({scriptPath: 'factory/workflows/build.js', args: {ticket: ID}})`; the human commands (`queue`, `approve-*`, `request-changes`, `resolve`, `merge`, `gate-run`, `audit-sample`, `retro`), all run with `FACTORY_KEY` set (B). Not verified: whether the Workflow registry can address these as named workflows; `scriptPath` is what the reference documents, so that is what the skill uses.
 - `factory init`: creates `~/factory-remote/nanobot.git` (bare), seeds `main` from `feat/lionbot-v3`, creates the `tickets` branch and its checkout, mints keys (E), installs the hook (`factory install-hook`: copies the installed package to `~/factory-remote/hook-env/`, writes the shim with an absolute `FACTORY_HOOK_PYTHON`, so a pushed edit to `factory/hook.py` changes nothing until a human reinstalls). It never touches `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md`, `webui/package-lock.json`, `port_state.json`, or `scripts/` (E9).
 - `AGENTS.md`: the layout, the gates, and that `.claude/agents/factory-*`, `.claude/skills/factory*` and `factory/prompts/**` are guardrail paths.
@@ -320,7 +320,7 @@ No separate CI service. For sub-ticket PRs, `results record --role verifier` wri
 
 ### M. Audit sample and retro entry
 
-`factory audit-sample [--since 7d] [--n 5]` → `audits/<date>.yaml`. `factory retro-input [--since <last>]` composes the retro input per doc §Routing table (Retro row) to stdout: incidents, instruction files, previous proposals read from `retros/*.yaml`, and run and outcome counts per `(role, model)` from `runs/*/meta.yaml` and `log/`; `retro.js` feeds it to `runRole('retro')` (retro key); `PROPOSED` → clerk `factory ticket new --type retro --branch retro/<date> --output <run output>` (writes `retros/<date>.yaml`, records the head, runs `gate-run`, L), queue.md "Guardrail gate"; `NO-CHANGES` → `run.finished` only.
+`factory audit-sample [--since 7d] [--n 5]` → `audits/<date>.yaml`. `factory retro-input [--since <last>]` composes the retro input per doc §Routing table (Retro row) to stdout: incidents, instruction files, previous proposals read from `retros/*.yaml`, run and outcome counts per `(role, model)` from `runs/*/meta.yaml` and `log/`, and the marker ledger (one row per `factory:` comment in the code on `main`: file:line, limit, upgrade trigger, and `no-trigger` where the comment names none); `retro.js` feeds it to `runRole('retro')` (retro key); `PROPOSED` → clerk `factory ticket new --type retro --branch retro/<date> --output <run output>` (writes `retros/<date>.yaml`, records the head, runs `gate-run`, L), queue.md "Guardrail gate"; `NO-CHANGES` → `run.finished` only.
 
 ### Size and seams (NEEDS-SPLIT)
 
@@ -432,7 +432,7 @@ Driver: `claude -p … "/factory run build T-0001 --stubs tests/factory/fixtures
 ### Audit and retro (S5)
 
 65. `factory audit-sample --since 7d --n 5` with 3 merged → prints 3 IDs and `note: only 3 merged in period`; `audits/<date>.yaml` written [NEW]
-66. `factory retro-input` → sections `incidents`, `instruction files`, `previous proposals` (read from `retros/*.yaml`; item 53's file appears here), `counts per role` (one line per `(role, model)`, item 72) [NEW]
+66. `factory retro-input` → sections `incidents`, `instruction files`, `previous proposals` (read from `retros/*.yaml`; item 53's file appears here), `counts per role` (one line per `(role, model)`, item 72), `marker ledger` (one row per `factory:` code comment on `main`; a comment naming no upgrade trigger carries `no-trigger`) [NEW]
 
 ### CLI guards (S1)
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 09cd4f0..6fe5e03 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -45,5 +45,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 41. After the T-0010 spec gate (2026-10-02), where the operator could not read an approved Problem section without a translation: the spec writer writes the Problem section in plain words for the operator who approves the spec at the gate, a deeply technical reader new to this system's internals, with each term of art specific to this system glossed on first use and the detail left to Evidence and Root cause; critic rubric 6 reads the Problem as that operator, and a first paragraph that does not say what is wrong and for whom, or uses an unglossed term specific to this system (even one a careful reader could infer), is BLOCKING.
 42. After issue #19 (2026-10-02): the harness lives in this repo and each target repo carries a `.factory/` instance: `instance.yaml`, `context.md` (the role-context block, prepended by the composer), `harness.lock` (the accepted harness revision; any other revision is refused until a human accepts it) and the store. The harness finds the instance by walking up from the working directory, and its own code is a protected path in the repo that holds it. The design doc splits into `docs/design.md` and this changelog, the prompt copies move to `docs/prompts/`, and the working documents for building the factory move to `dev/`.
 43. After issue #23 (2026-10-03), where the operator's review of the overview draft found the same three failures the factory's own outputs show (an unglossed term, a parenthetical holding a second idea, a page that assumed its reader knew the project): a one-page writing standard, `docs/writing.md`, holds eight rules an agent can check in its own output, each with a before-and-after example from the factory's own writing. The shared preamble's OUTPUT block gains one line: every section a person reads follows the standard at `{writing standard}`, a placeholder the harness fills when a run starts with the path of `docs/writing.md` in the harness checkout that runs it; the role-context block also names who reads what the roles write. Critic rubric 6 widens from the Problem section to every human-facing section of a spec (Problem, Evidence, Open questions, Decisions, Operator steps), still BLOCKING on a Problem that does not say what is wrong and for whom or a first paragraph with an unglossed term specific to this system; other departures from the standard are SHOULD-FIX or NIT. The code reviewer gains check 8, whether the operator could read the PR description's What changed and Known gaps, which is SHOULD-FIX, never BLOCKING. The briefing template gains a line naming the reader of the repo's documents.
+44. After issue #20 (2026-10-03), because nothing stopped a coding agent from building more than its ticket needs: a coding standard, `docs/coding.md`, the twin of the writing standard. It opens with a precedence rule (a target repository's own instructions win where they disagree with it) and holds five rules an agent can check in its own output, each with a `Check:` line, the code-design principle it applies and a before-and-after example: reuse before writing, taking the first rung of a check order that holds; grep every caller and fix a shared function once; mark each deliberate shortcut with a `factory:` comment naming its limit and upgrade trigger; tag each over-building review finding; and one name per concept from spec to code. The review tags are `reuse:` (BLOCKING) and `stdlib:`, `native:`, `yagni:` and `delete:` (SHOULD-FIX), and a review pass ends with `net: -N lines possible` or `Lean already.` The implementer's step 4 gains a line pointing to the standard at `{coding standard}`, and the code reviewer's check 7 is replaced by one: its old "Maintainability, only where it will cause real problems" text is gone. The harness fills `{coding standard}` when a run starts, with the path of `docs/coding.md` in the harness checkout that runs it, through the same helper that fills `{writing standard}`, now applied to the role prompt as well as the preamble. The spec writer gains a rule to cut any part the ticket's intent does not need, naming it under Out of scope, and critic rubric 3 makes such a part a finding. The retro's input names the marker ledger, one row per `factory:` comment in the code on the integration branch; this is design only, and the harness code that builds the ledger waits for the ticket that builds the retro. The check order and the tag vocabulary are adapted from ponytail (DietrichGebert/ponytail, MIT).
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/coding.md b/docs/coding.md
new file mode 100644
index 0000000..cc27e2d
--- /dev/null
+++ b/docs/coding.md
@@ -0,0 +1,98 @@
+# Coding standard
+
+A coding agent tends to build more than its ticket needs: a new helper beside one that already
+exists, hand-rolled code for something the standard library ships, an interface with one
+implementation. The operator pays for each at the gate, in a bigger diff, and later owns the
+duplicate code. This page is how the spec factory's implementer (the role that writes the code for
+one sub-ticket) and its code reviewer (the role that judges that code before it merges) keep a
+change as small as the ticket allows. It is the twin of the writing standard, `docs/writing.md`:
+the same format, and where both pages name a principle, they name the same one.
+
+**Precedence.** A target repository's own instructions win where they disagree with this page.
+They are in its `AGENTS.md` and the documents that file points to. Example: Nanobot's
+`.agent/design.md` says "Prefer duplication over premature abstraction" for its channel and
+provider files. In those files DRY (rule 1) gives way, and a repeated block is not a `reuse:`
+finding (rule 4).
+
+Each rule below is one you can check in your own output before you hand it in: the implementer
+in its diff and PR description, the reviewer in its findings. Each names its code-design
+principle and has an example and its rewrite. An example marked "illustration" was written for
+this page; the others are sourced.
+
+## 1. Reuse before writing: take the first rung that holds.
+Check: for each function, class, type or dependency your diff adds, you can name the rung it sits
+on and say why no earlier rung held.
+1. A helper, util, type or pattern already in this repo.
+2. The standard library.
+3. A native platform feature: a database constraint over app code, an atomic file-system call
+   over a lock.
+4. A dependency already installed.
+5. One line.
+6. The minimum code that works.
+Whether the thing should exist at all is the spec's question, not the implementer's: the spec
+writer cuts any part the ticket does not need.
+Principle: DRY, don't repeat yourself (Hunt and Thomas, The Pragmatic Programmer).
+Before (`factory/store.py`, `ensure_gitignore`, as of 2026-10-03): it creates the store directory
+and writes `.gitignore` with its own two lines, which repeat `write_text` in the same module.
+After: it calls `write_text`, so a later change to how the store writes files, such as its
+encoding or an atomic replace, reaches `.gitignore` too.
+
+## 2. Fix the shared function once: grep every caller before you edit.
+Check: for each existing function your diff changes, your PR description names its callers, found
+by a grep of the repo, and says why the fix sits where it does.
+Principle: single responsibility, and root cause over symptom: a ticket names a symptom, and the
+fix goes where the cause is, once.
+Before (ponytail's comprehension benchmark, 2026-06-22: a seeded `bank.py` where `transfer()` and
+`withdraw()` share `_debit()`, and the bug report names only transfers): told to "trace the flow
+end to end", Opus scored 0 of 3. Patching only `transfer()` leaves `withdraw()` broken.
+After: told to "grep every caller of the function you touch; fix the shared function once",
+Sonnet 4.6 and Opus 4.8 scored 6 of 6, against a baseline of 1 of 6. One guard in `_debit()` is a
+smaller diff than one per caller.
+
+## 3. A deliberate shortcut carries a `factory:` comment naming its limit and upgrade trigger.
+Check: each simplification in your diff with a known limit (a global lock, an O(n²) scan, a naive
+heuristic) has a comment starting `factory:` that names the limit and when to upgrade. Your PR
+description's Known gaps lists each marker you added, or says "factory: markers added: none".
+Principle: technical-debt bookkeeping; debt taken on purpose is recorded where it lives
+(Cunningham's debt metaphor).
+Before (illustration): `with ACCOUNTS_LOCK:` around every account update, with no comment, so
+the next reader cannot tell a choice from an oversight.
+After: `# factory: one global lock; per-account locks if transfers contend` above it. The marker
+is greppable: `grep -rnE '(#|//|/\*) ?factory:'` lists every one in the code.
+
+## 4. A reviewer's over-building finding carries one tag and names what replaces the code.
+Check: each over-building finding (code the change could have reused, or did not need) starts,
+after its severity, with one tag from the table (`[BLOCKING] reuse: file:line: problem →
+consequence`), names what the table says to name, and has the table's severity. A finding against
+rule 2, 3 or 5 takes no tag; it earns its severity as a correctness or scope finding. The pass ends
+with `net: -N lines possible`, where N is the lines the tagged findings would remove, or with
+`Lean already.`
+Principle: per tag, in the table.
+
+| Tag | Flags | Names | Severity | Principle |
+|---|---|---|---|---|
+| `reuse:` | a helper, type or pattern this repo already has | its path | BLOCKING | DRY |
+| `stdlib:` | code the standard library ships | the function | SHOULD-FIX | don't reinvent |
+| `native:` | code or a dependency doing the platform's job | the feature | SHOULD-FIX | don't reinvent |
+| `yagni:` | an abstraction, setting or layer with one use | what it folds into | SHOULD-FIX | YAGNI |
+| `delete:` | dead code, unused flexibility, a speculative feature | nothing | SHOULD-FIX | dead code |
+
+Before (illustration): "Maintainability: some duplication in the store module; consider
+refactoring."
+After: "[BLOCKING] reuse: factory/store.py:59: `ensure_gitignore` repeats `write_text` → a change
+to how the store writes files misses `.gitignore`; call `write_text`." Then "net: -1 lines
+possible".
+
+## 5. One name per concept, from spec to code.
+Check: each term your spec defines (in its Problem section; for the factory itself, in the
+README's terms table) is the identifier your code uses for that concept, and no identifier you add
+is a synonym for one the repo already has.
+Principle: ubiquitous language (Evans, Domain-Driven Design), the same principle as the writing
+standard's rule 9.
+Before (illustration): the README's terms table defines a "parked" ticket, and a change adds the
+state `on_hold` and a function `hold_ticket()` for the same thing.
+After: the state stays `parked` and the command stays `ticket park`, the names the store and the
+README already use.
+
+The check order (rule 1) and the tag vocabulary (rule 4) are adapted from ponytail
+(DietrichGebert/ponytail, MIT), as the design document's changelog records.
diff --git a/docs/design.md b/docs/design.md
index a72f32b..2575e23 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -51,7 +51,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **What the harness itself owns** (no platform provides these): the routing table, the round counter and the max-round cutoff, composing each role's input from *only* its declared sources, choosing the model per role, and the escalation queue view for the daily human pass.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception.
 
@@ -124,7 +124,7 @@ Rules the table relies on:
 | Verifier | SPEC-DEFECT | Human queue | Verifier output |
 | Merge gate | Head does not contain current main | Implementer (same round, conflict run): merge main into the branch, or rebase where {force-push allowed} | Conflict output; the new head re-runs CI and both checkers |
 | Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main + piece-8 approvals | Merge; then dispatch sub-tickets that depended on this one. When all sub-tickets have merged, one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label): VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue | Parent-close run: pinned parent spec; head = current main; base = the main SHA recorded before the parent's first sub-ticket merged; `{gate commands}` |
-| Weekly audit done, or on demand | — | Retro | Full outputs behind every outcome signal since the last retro (piece 10), current instruction files, every proposal still under evaluation with its metric, and per-role run and outcome counts, broken down by model, for the period and for each prior proposal's window |
+| Weekly audit done, or on demand | — | Retro | Full outputs behind every outcome signal since the last retro (piece 10), current instruction files, every proposal still under evaluation with its metric, and per-role run and outcome counts, broken down by model, for the period and for each prior proposal's window, and the marker ledger: one row per `factory:` comment in the code on the integration branch, with file:line, limit and upgrade trigger, flagged `no-trigger` where it names none, composed by the harness when the retro runs |
 | Retro | PROPOSED | Guardrail-changes gate (human); on approval, the no-sub-ticket merge row | PR |
 | Retro | NO-CHANGES | Log only | — |
 | Retro or revert PR (no sub-ticket) | Guardrail-gate human approval on current head | Gate runner on the head; then merge on CI green + head contains main + that approval; no checkers (piece 7 exception). Fails the exception test: closed, logged to the human queue | — |
@@ -287,6 +287,9 @@ RULES
 - Size: one spec must fit in one reviewable PR (roughly under
   {400} changed lines). If it can't, mark it NEEDS-SPLIT and name the
   seams as lettered parts under Proposed change.
+- Cut before you specify: for each part, ask first whether the ticket's
+  intent needs it at all. A speculative part is cut, and named in one
+  line under Out of scope.
 - Acceptance criteria must be runnable. Label each NEW (must fail today)
   or REGRESSION (must pass today and after the change). A NEW criterion
   that already passes proves nothing. State how each NEW item fails
@@ -379,7 +382,8 @@ RUBRIC (judge intent, not wording)
 3. Scoped: fits one PR, or is marked NEEDS-SPLIT with natural seams
    named (the planner splits it); out-of-scope list is present and sensible;
    "Tests to change" names only tests the intended change genuinely
-   breaks, with a reason each.
+   breaks, with a reason each; a lettered part the ticket's intent does
+   not need is a finding.
 4. No hidden decisions: no product or design choice is made silently;
    every protected path the change will touch is declared under Risk.
 5. Consistent: doesn't conflict with open tickets or stated architecture.
@@ -491,6 +495,7 @@ PROCESS
 3. Write or extend tests that capture the intended behavior. Watch them
    fail.
 4. Make the smallest change that makes them pass for the right reason.
+   Follow the coding standard at {coding standard}.
 5. Run the full local gates: {gate commands}.
 6. Open a PR using the format below. On a fix round: check out the
    existing branch, push fix commits to it, and replace the PR
@@ -552,7 +557,8 @@ CHECK, IN THIS ORDER
    ESCALATE. If it does, list them under ESCALATIONS, finish the review,
    and give the STATUS the code earns; the merge gate will require a
    human approval.
-7. Maintainability, only where it will cause real problems. Not style.
+7. The coding standard at {coding standard}: a finding against it
+   carries the tag and severity the standard gives it. Not style.
 8. PR description: could the operator at the gate read its What changed
    and Known gaps, held to the writing standard? They say in words what
    changed and what is uncertain, not as a file list, and gloss each
@@ -646,6 +652,10 @@ evaluation with the metric it was meant to move, and per-role run and outcome
 counts for the period, broken down by model, so every rate has a
 denominator. The model-per-role table is harness config: a diff to it
 is how you propose a model change.
+Also the marker ledger: one row per `factory:` comment in the code on
+the integration branch (a shortcut its author marked, per the coding
+standard), with its file:line, the limit it names and its upgrade
+trigger, flagged no-trigger where it names none.
 
 PROCESS
 1. For each incident, write the causal chain:
diff --git a/docs/prompts/02-spec-writer.md b/docs/prompts/02-spec-writer.md
index 023653b..080e7ea 100644
--- a/docs/prompts/02-spec-writer.md
+++ b/docs/prompts/02-spec-writer.md
@@ -16,6 +16,9 @@ RULES
 - Size: one spec must fit in one reviewable PR (roughly under
   {400} changed lines). If it can't, mark it NEEDS-SPLIT and name the
   seams as lettered parts under Proposed change.
+- Cut before you specify: for each part, ask first whether the ticket's
+  intent needs it at all. A speculative part is cut, and named in one
+  line under Out of scope.
 - Acceptance criteria must be runnable. Label each NEW (must fail today)
   or REGRESSION (must pass today and after the change). A NEW criterion
   that already passes proves nothing. State how each NEW item fails
diff --git a/docs/prompts/03-spec-critic.md b/docs/prompts/03-spec-critic.md
index c77934d..a72de2e 100644
--- a/docs/prompts/03-spec-critic.md
+++ b/docs/prompts/03-spec-critic.md
@@ -11,7 +11,8 @@ RUBRIC (judge intent, not wording)
 3. Scoped: fits one PR, or is marked NEEDS-SPLIT with natural seams
    named (the planner splits it); out-of-scope list is present and sensible;
    "Tests to change" names only tests the intended change genuinely
-   breaks, with a reason each.
+   breaks, with a reason each; a lettered part the ticket's intent does
+   not need is a finding.
 4. No hidden decisions: no product or design choice is made silently;
    every protected path the change will touch is declared under Risk.
 5. Consistent: doesn't conflict with open tickets or stated architecture.
diff --git a/docs/prompts/05-implementer.md b/docs/prompts/05-implementer.md
index 4119a3d..efe4204 100644
--- a/docs/prompts/05-implementer.md
+++ b/docs/prompts/05-implementer.md
@@ -8,6 +8,7 @@ PROCESS
 3. Write or extend tests that capture the intended behavior. Watch them
    fail.
 4. Make the smallest change that makes them pass for the right reason.
+   Follow the coding standard at {coding standard}.
 5. Run the full local gates: {gate commands}.
 6. Open a PR using the format below. On a fix round: check out the
    existing branch, push fix commits to it, and replace the PR
diff --git a/docs/prompts/06-code-reviewer.md b/docs/prompts/06-code-reviewer.md
index 05f0532..5ab0419 100644
--- a/docs/prompts/06-code-reviewer.md
+++ b/docs/prompts/06-code-reviewer.md
@@ -18,7 +18,8 @@ CHECK, IN THIS ORDER
    ESCALATE. If it does, list them under ESCALATIONS, finish the review,
    and give the STATUS the code earns; the merge gate will require a
    human approval.
-7. Maintainability, only where it will cause real problems. Not style.
+7. The coding standard at {coding standard}: a finding against it
+   carries the tag and severity the standard gives it. Not style.
 8. PR description: could the operator at the gate read its What changed
    and Known gaps, held to the writing standard? They say in words what
    changed and what is uncertain, not as a file list, and gloss each
diff --git a/docs/prompts/08-retro.md b/docs/prompts/08-retro.md
index d25ddc6..da63f6c 100644
--- a/docs/prompts/08-retro.md
+++ b/docs/prompts/08-retro.md
@@ -12,6 +12,10 @@ evaluation with the metric it was meant to move, and per-role run and outcome
 counts for the period, broken down by model, so every rate has a
 denominator. The model-per-role table is harness config: a diff to it
 is how you propose a model change.
+Also the marker ledger: one row per `factory:` comment in the code on
+the integration branch (a shortcut its author marked, per the coding
+standard), with its file:line, the limit it names and its upgrade
+trigger, flagged no-trigger where it names none.
 
 PROCESS
 1. For each incident, write the causal chain:
diff --git a/factory/cli.py b/factory/cli.py
index 852c458..d8bfade 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -216,7 +216,8 @@ def run_start(a, root, cfg):
     store.write_yaml(d / "meta.yaml", meta)
     prompt_name = a.role
     preamble = instance.fill_preamble((PROMPTS / "preamble.md").read_text(encoding="utf-8"), cfg)
-    sysp = preamble.rstrip() + "\n\n" + (PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8")
+    role_prompt = instance.fill_standards((PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8"))
+    sysp = preamble.rstrip() + "\n\n" + role_prompt
     store.write_text(d / "system-prompt.txt", sysp)
     t["in_flight"].append(rid)
     store.save_ticket(root, t)
diff --git a/factory/instance.py b/factory/instance.py
index 264b86a..9af711f 100644
--- a/factory/instance.py
+++ b/factory/instance.py
@@ -157,13 +157,20 @@ def guard(inst: Path, cfg: dict, root: Path, accept: str | None) -> None:
 PROTECTED_PLACEHOLDER = "  {auth, payments, migrations, infra, public API, dependencies}"
 
 
+def fill_standards(text: str) -> str:
+    """`{writing standard}` and `{coding standard}` filled from the running harness checkout, not
+    the instance: the absolute paths of its `docs/writing.md` and `docs/coding.md`, which ship in
+    the same checkout as this code. Applied to the preamble and to each role prompt."""
+    text = text.replace("{writing standard}", str(HARNESS / "docs" / "writing.md"))
+    return text.replace("{coding standard}", str(HARNESS / "docs" / "coding.md"))
+
+
 def fill_preamble(text: str, cfg: dict) -> str:
     """The design doc's preamble block with `{repo name}` and the protected-path line filled from
     the instance (B.4). The line becomes `  <class> (<glob>, <glob>)` per class, joined by `, `.
-    `{writing standard}` is filled from the running harness checkout, not the instance: the
-    absolute path of its `docs/writing.md`, which ships in the same checkout as this code."""
+    The standards' paths are filled by `fill_standards`."""
     text = text.replace("{repo name}", str(cfg["repo_name"]))
-    text = text.replace("{writing standard}", str(HARNESS / "docs" / "writing.md"))
+    text = fill_standards(text)
     classes = []
     for cls, globs in (cfg.get("protected_paths") or {}).items():
         globs = [globs] if isinstance(globs, str) else list(globs or [])
diff --git a/factory/prompts/critic.md b/factory/prompts/critic.md
index 8ec25e7..a22c9f0 100644
--- a/factory/prompts/critic.md
+++ b/factory/prompts/critic.md
@@ -11,7 +11,8 @@ RUBRIC (judge intent, not wording)
 3. Scoped: fits one PR, or is marked NEEDS-SPLIT with natural seams
    named (the planner splits it); out-of-scope list is present and sensible;
    "Tests to change" names only tests the intended change genuinely
-   breaks, with a reason each.
+   breaks, with a reason each; a lettered part the ticket's intent does
+   not need is a finding.
 4. No hidden decisions: no product or design choice is made silently;
    every protected path the change will touch is declared under Risk.
 5. Consistent: doesn't conflict with open tickets or stated architecture.
diff --git a/factory/prompts/implementer.md b/factory/prompts/implementer.md
index 63fdd71..2d1d573 100644
--- a/factory/prompts/implementer.md
+++ b/factory/prompts/implementer.md
@@ -8,6 +8,7 @@ PROCESS
 3. Write or extend tests that capture the intended behavior. Watch them
    fail.
 4. Make the smallest change that makes them pass for the right reason.
+   Follow the coding standard at {coding standard}.
 5. Run the full local gates: the gate commands listed in your input
    under "Where you work", each exactly as written.
 6. Open a PR using the format below. On a fix round: check out the
diff --git a/factory/prompts/reviewer.md b/factory/prompts/reviewer.md
index 4c8b1f3..2f2c615 100644
--- a/factory/prompts/reviewer.md
+++ b/factory/prompts/reviewer.md
@@ -18,7 +18,8 @@ CHECK, IN THIS ORDER
    ESCALATE. If it does, list them under ESCALATIONS, finish the review,
    and give the STATUS the code earns; the merge gate will require a
    human approval.
-7. Maintainability, only where it will cause real problems. Not style.
+7. The coding standard at {coding standard}: a finding against it
+   carries the tag and severity the standard gives it. Not style.
 8. PR description: could the operator at the gate read its What changed
    and Known gaps, held to the writing standard? They say in words what
    changed and what is uncertain, not as a file list, and gloss each
diff --git a/factory/prompts/spec_writer.md b/factory/prompts/spec_writer.md
index 8a81f85..a3b0dec 100644
--- a/factory/prompts/spec_writer.md
+++ b/factory/prompts/spec_writer.md
@@ -16,6 +16,9 @@ RULES
 - Size: one spec must fit in one reviewable PR (roughly under
   400 changed lines). If it can't, mark it NEEDS-SPLIT and name the
   seams as lettered parts under Proposed change.
+- Cut before you specify: for each part, ask first whether the ticket's
+  intent needs it at all. A speculative part is cut, and named in one
+  line under Out of scope.
 - Acceptance criteria must be runnable. Label each NEW (must fail today)
   or REGRESSION (must pass today and after the change). A NEW criterion
   that already passes proves nothing. State how each NEW item fails
diff --git a/tests/factory/test_coding_standard.py b/tests/factory/test_coding_standard.py
new file mode 100644
index 0000000..f063b93
--- /dev/null
+++ b/tests/factory/test_coding_standard.py
@@ -0,0 +1,86 @@
+"""The coding standard (issue #20): an implementer run's and a code-reviewer run's system prompt
+name the running checkout's `docs/coding.md`, with `{coding standard}` filled; and the design
+blocks this change edits that test_writing_standard.py does not cover (spec writer, implementer,
+retro) stay verbatim copies of their `docs/prompts/` files.
+
+Black-box through `bin/factory` in a scratch target repo, as test_writing_standard.py drives it.
+"""
+from __future__ import annotations
+
+import json
+import os
+import re
+import subprocess
+from pathlib import Path
+
+import pytest
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+STANDARD = REPO.resolve() / "docs" / "coding.md"
+STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
+FENCE = "`" * 3
+
+
+def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
+    env = {k: v for k, v in os.environ.items() if k not in STRIP}
+    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
+    cp = subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=cwd)
+    assert cp.returncode == 0, (argv, cp.stderr)
+    return cp
+
+
+@pytest.fixture(scope="module")
+def system_prompts(tmp_path_factory) -> dict[str, str]:
+    """The system prompts of one implementer run and one reviewer run on the same ticket, started
+    in a fresh scratch target on a throwaway store (FACTORY_STATE), as in the spec's scenario. The
+    ticket's status is set by `ticket set` so that each role can start."""
+    tmp = tmp_path_factory.mktemp("coding")
+    t = tmp / "target"
+    t.mkdir()
+    for argv in (["init", "-q", "-b", "main"],
+                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
+        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
+    req = tmp / "r.md"
+    req.write_text("# demo\n\nDo the thing.\n")
+    store = {"FACTORY_STATE": str(tmp / "s")}
+    cli(t, "init", "--repo-name", "demo")
+    cli(t, "ticket", "new", "--file", str(req), **store)
+    head = subprocess.run(["git", "-C", str(t), "rev-parse", "HEAD"], check=True, capture_output=True,
+                          text=True).stdout.strip()
+    prompts = {}
+    for role, status in (("implementer", ["status=ready-for-implementer"]),
+                         ("reviewer", ["status=checks-in-flight", "in_flight=[]", f"head={head}"])):
+        cli(t, "ticket", "set", "T-0001", *status, **store)
+        cp = cli(t, "run", "start", "--role", role, "--ticket", "T-0001", "--model", "opus", **store)
+        run_id = json.loads(cp.stdout.strip().splitlines()[-1])["run_id"]
+        prompts[role] = (tmp / "s" / "runs" / run_id / "system-prompt.txt").read_text()
+    return prompts
+
+
+@pytest.mark.parametrize("role, line", [
+    ("implementer", "   Follow the coding standard at {path}."),
+    ("reviewer", "7. The coding standard at {path}: a finding against it"),
+])
+def test_run_prompt_names_the_running_checkouts_coding_standard(system_prompts, role, line):
+    assert STANDARD.is_absolute() and STANDARD.is_file() and STANDARD.stat().st_size > 0
+    prompt = system_prompts[role]
+    assert line.format(path=STANDARD) in prompt.split("\n")
+    assert "{coding standard}" not in prompt
+
+
+def _design_block(heading: str) -> str:
+    """The text inside the first fenced `text` block under `## <heading>` in docs/design.md."""
+    design = (REPO / "docs" / "design.md").read_text()
+    m = re.search(rf"^## {re.escape(heading)}\n.*?^{FENCE}text\n(.*?)^{FENCE}$", design, re.M | re.S)
+    assert m, heading
+    return m.group(1)
+
+
+@pytest.mark.parametrize("heading, copy", [
+    ("2. Spec writer", "02-spec-writer.md"),
+    ("5. Implementer", "05-implementer.md"),
+    ("8. Retro", "08-retro.md"),
+])
+def test_changed_design_block_equals_its_prompt_copy(heading, copy):
+    assert _design_block(heading) == (REPO / "docs" / "prompts" / copy).read_text()
