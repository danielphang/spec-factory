## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0052-spec_writer/output.md`

## Ticket (Triage output)

Type: chore (structural refactor of both repos' layout; it also closes a functional gap: the factory cannot target a second repo without a hand copy)

Title: Move the harness into spec-factory and give each target repo a `.factory/` instance (instance B first; carries #7's harness side)

Summary:
The spec factory cannot be pointed at a second repository without copying its code out of the first one by hand: the harness lives inside the Nanobot fork (green, `feat/lionbot-v3`), and the only other install (this repo's `intake/`) is a `git archive` snapshot of it with three files overwritten, pinned by a hand-kept `HARNESS_PIN`. The requester wants the harness to live in the repo that owns its design (`~/dev/spec-factory`), with each target carrying a small `.factory/` instance that names the harness checkout, records the harness revision it has accepted, and holds its own config, role-context block and store. They also want the four concerns now mixed together (harness code, design doc + prompt copies, the working docs for building the factory, how it is installed) split into directories whose names say which is which. Scope ends when the installed harness runs this repo's own `.factory/` end to end and `factory init` produces a working instance in a throwaway target; moving green (instance A) over is a separate, paired ticket on instance A. The requester marks it NEEDS-SPLIT, with proposed parts A-F as the planner's seams.

Evidence:
- Duplicate search: `issues/README.md` and `intake/state/tickets/*.yaml` (T-0001..T-0011 all `status: closed`). #7 ("Harness instance is single-target", T-0007, closed, `b9379ec`, changelog 38) applied the doc side only; this request carries its open harness side, so it is not a duplicate. #13/#14 (open, not in intake) touch the same files (design doc §Harness/routing, build spec parts B, D, G, H, L) but ask for different changes. Those are sequencing overlaps, not duplicates. #19 in `issues/README.md` is this request ("not in intake yet"); this run is its intake as T-0012.
- I checked these quotes and facts on this checkout (`main` at `239ef5f`):
  - `README.md:11`: "Fill in `{braces}` per repo. The design doc is the source of truth; `prompts/` is regenerated from it." The request says line 13; it is actually line 11.
  - `docs/spec-factory.md:52`: "Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here." The file is 759 lines (`wc -l`). The Changelog (from line 678) has 41 numbered items, and item 38 says "where the block is kept stays open".
  - `intake/README.md:1-6`: "# intake/ — SCRATCH … Delete the whole directory once the issues are filed and closed".
  - `intake/setup.sh` runs `git -C "$SRC" archive "$PIN" factory bin/factory`, then copies `instance/preamble.md`, `instance/context.md` and `instance/config.yaml` over the copy. `intake/HARNESS_PIN` is `7c0a0353d…` today. The body's `2986a2f` is superseded, as the operator's intake note says.
  - Five files reference the paths that would move (grep for `docs/spec-factory.md|specs/build-harness.md|plans/build-harness.md|plans/P0-intake-skeleton.md|issues/README`): `README.md`, `plans/build-harness.md`, `plans/P0-intake-skeleton.md`, `intake/README.md`, `intake/instance/context.md`. This matches the request's list.
- Reference harness (read only), `~/dev/nanobot-upstream` on `feat/lionbot-v3`, HEAD `7c0a0353d` ("Merge factory/T-0002.1 …"):
  - `.claude/agents/` holds six `factory-*.md` files (clerk, planner, spec-critic, spec-writer, stub, triage).
  - `factory/config.yaml:8` protects `infra: ["factory/workflows/**", "factory/config.yaml", …]`. `factory/prompts/**` is not listed, which matches the request's claim.
  - `factory/` has no `render.py`, so `factory render` is still unbuilt.
  - Grepping `tests/factory` for `knowledge_vault|nanobot/` returns nothing.
  - `grep -E "^\s*(async )?def test_"` over `tests/factory` counts 69 test functions. The operator says 70 tests (parametrization may explain the difference; I did not run pytest).
  - `factory/workflows/intake.js` lines 14 and 24-27 hold the `inlineRoles` fallback comment and flag the request cites.
  - The body's "green tip `f8f40e0c5`" is now an ancestor of HEAD.
- Requester's operator ruling: "highest priority once the first end-to-end pilot finishes". Operator note at intake: #16 and #18 are merged into green and closed; the latest pilot merge is `7c0a0353d`; #13 and #14 are still open.
- Side-by-side review linked by the requester: https://claude.ai/artifact/GbquRqWRR6y3ZR2pY1dXaK (operator-reviewed; I did not open it).

Assumptions (my inferences, labeled as such):
- ACCEPT, not NEEDS-HUMAN. The requester has already made the product and design calls: the design doc stays the prompt source and `render --check` stays; the harness is a pinned git checkout with an advisory lock and an explicit accept step; instance A's cutover is a separate ticket. The open choices are explicitly given to the planner: whether `intake/green-pilot/` becomes a second instance directory or is folded in, and which sub-ticket adds `uv run pytest tests` to this instance's gate.
- The operator's intake note amends part E: E moves everything except the live store, and the move of `intake/state/` → `.factory/state/` (plus removal of `intake/harness/`) becomes a scripted post-close step with its own check ("the store opens from `.factory/state/`, and `ticket show` on every ticket still works"). I read that recommendation as the requester's intent, because the harness cannot move the store it runs from in the middle of a ticket.
- The operator's facts replace the body's stale numbers. The history cut for part A goes at or after green `7c0a0353d`, and the moved test suite is about 70 tests, not 55.
- Part A extracts history with `git filter-repo`. I assume this must run on a fresh clone of green, never inside `~/dev/nanobot-upstream`, because filter-repo rewrites the repo it runs in and that path is read only for this instance (`reference harness` protected class). The request does not say this, but it follows from the protected-path rule.
- Green-specific files stay on green as instance A's overlay and are not moved here: `factory/config.yaml`, `factory/prompts/{context,preamble}.md`, `scripts/full_suite_gate.py` (operator note).
- Out of scope, as the requester listed: the simplifier role (#15), role-prompt wording, the routing table, the store schema, the OpenSpec tree. Role prompts move but their wording must not change.
- Suggested priority (a suggestion only; priority is a human call): p0, matching the request's label and the operator's ruling, now that its precondition (#16 and #18 closed) is met.

Question for human / Missing info / Reason: none blocking. For the Spec writer and Planner:
- Protected paths on instance B that this work touches: `intake/**` (`infra`, deleted or moved) and `prompts/**` (`generated`, moved and from then on written by `render`). The request's Risk section declares both, and the approved spec's Risk section must carry them forward.
- Sequencing against #13 and #14: either their doc edits land first, or part D carries them. The planner states which, per sub-ticket.

STATUS: ACCEPT
CONFIDENCE: medium. The intent, scope boundary and decisions are explicit, and the cited facts check out on both checkouts. But this is a large multi-part refactor whose body has stale numbers (corrected by the intake note), and I did not run green's test suite or open the linked review.
ESCALATIONS: none. This run wrote only its output file. The protected-path touches (`intake/**`, `prompts/**`) are declared in the request's Risk section and flagged above for the gate.

## Request (raw)

---
title: Repo layout: the harness moves home, each target carries a .factory/ instance
labels: p0, design-doc, harness
---
**Where:** the layout of both repos. `README.md` ("Fill in `{braces}` per repo"; "`prompts/` is regenerated from it"); `docs/spec-factory.md` §Harness (role-context block: "where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here"; piece 8 guardrail paths); `specs/build-harness.md` D8 and parts A/K (`factory render`); `intake/README.md` ("scratch, delete once the issues are closed"); on Nanobot green, `factory/**`, `bin/factory`, `.claude/agents/factory-*.md`, `tests/factory/**`, `knowledge_vault/spec_factory/`. Carries the harness side of #7 (closed; its doc side applied in `b9379ec`, changelog 38; "where the block is kept" was left open).

**Problem, for the gate:** the spec factory cannot be pointed at a second repository without copying its code out of the first one by hand. Anyone who adopts it for another project repeats that copy; the operator, who already runs it against two targets, keeps two copies that drift. The factory's code lives inside the first project it was built for (the Nanobot fork, branch `feat/lionbot-v3` in `~/dev/nanobot-upstream`, called "green" below), and the only second install, the factory working on its own design repo, is a snapshot of that code with three files overwritten.

**What happened (2026-10-02, both installs; the side-by-side review is at <https://claude.ai/artifact/GbquRqWRR6y3ZR2pY1dXaK>, operator-reviewed):** four concerns are interleaved and the directory names do not say which is which.

1. *The factory's code* lives inside its first target. `factory/` is versioned by green's commits and protected there only under `infra` (`factory/workflows/**`, `factory/config.yaml`); `factory/prompts/**` is unprotected on green today. The only way to run it against a second target, including this repo, is `intake/setup.sh`: `git archive <HARNESS_PIN> factory bin/factory` out of green into a gitignored copy, then overwrite three files (`preamble.md`, `context.md`, `config.yaml`). `HARNESS_PIN` (`2986a2f`, 3 commits behind green tip `f8f40e0c5` at filing) is a hand-kept lockfile into another repo's history.
2. *The documentation* is one 759-line file holding the design, the prompt blocks, the routing table and a 41-item changelog; `prompts/` is a second copy of the blocks, green's `factory/prompts/` a third with placeholders filled. The README says `prompts/` is regenerated from the doc; nothing in either repo does so (`factory render`, build spec A/K, is unbuilt).
3. *The working docs for building the factory* (`specs/build-harness.md`, `plans/build-harness.md`, `plans/P0-intake-skeleton.md`) sit in directories whose names the design reserves for pipeline **output** (`specs/<ticket>.md`, `plans/<ticket>.md`). A reader cannot tell a spec the factory produced from the spec for the factory.
4. *How it is installed* is written nowhere as a procedure. `intake/` calls itself scratch and says to delete it, while being the only self-hosting mechanism, with eleven tickets and 48 runs of committed state. It is the second install ("instance B" below), not scratch.

**Why it matters:** every new target repeats the copy-and-overwrite by hand, drifts from the harness it was copied from, and inherits a wrong role-context block silently (the block is the per-repo facts every role reads first; the checkers read the same one, so they share the error). Operator ruling: highest priority once the first end-to-end pilot finishes; a refactor, and also what makes the factory a thing other projects can adopt.

**Proposed change (NEEDS-SPLIT; the seams are the planner's sub-tickets):** one principle, #7's: **the target is a property of an instance, not of the harness.** The harness moves to the repo that owns its design; each target carries a small instance directory that pins a harness revision and holds its overlay and store.

```
~/dev/spec-factory/                     the factory: design + code, one repo, one history
  README.md                             what it is · install · 5-minute use · where things live
  docs/
    design.md                           today's docs/spec-factory.md: design, routing, gates, and the prompt blocks (still the source)
    changelog.md                        the 41 items, split out of the design
    prompts/                            RENDERED from design.md by `factory render`; `render --check` diffs them back (build spec A/K, paths updated)
  factory/                              the harness package (from nanobot-upstream/factory/, history carried)
    cli.py compose.py store.py gitops.py …  workflows/intake.js build.js  render.py
  bin/factory
  tests/                                today's tests/factory/ (55 tests; none references knowledge_vault or nanobot/)
  agents/                               factory-*.md templates; `factory init` copies them into a target's .claude/agents/
  dev/                                  working docs for building the factory itself
    build-harness.spec.md  build-harness.plan.md  P0-intake-skeleton.md  issues.md
  .factory/                             instance B: the factory on itself
    instance.yaml                       repo name, repo path, protected paths, gate commands, models, routing, harness path
    context.md                          the role-context block for this repo
    harness.lock                        the harness commit this instance was last run with (replaces intake/HARNESS_PIN)
    state/                              today's intake/state/

~/dev/nanobot-upstream/                 target A (instance A), cut over by its own ticket after B lands
  .factory/                             instance.yaml  context.md  harness.lock  state/ (today's knowledge_vault/spec_factory/)
  .claude/agents/factory-*.md           written by `factory init`, committed
  knowledge_vault/specs/                requests stay put (request_dir in instance.yaml)
```

A. **Harness extraction.** Move `factory/`, `bin/factory`, `tests/factory/` and the six `.claude/agents/factory-*.md` (as `agents/` templates) into this repo with history (`git filter-repo --path …` over the four prefixes; `git subtree split` takes one prefix, so it would be four splits and a merge). A creates `pyproject.toml` here (the `factory` package, `pyyaml` as a dependency, `pytest` as a dev dependency; green supplies both through nanobot's `pyproject.toml` today) and commits `uv.lock`, so `uv sync` gives `bin/factory` its interpreter as on green.
B. **Instance discovery.** `factory` finds `.factory/instance.yaml` by walking up from the cwd; `FACTORY_STATE` / `FACTORY_REPO` / `FACTORY_INTEGRATION_BRANCH` stay as overrides. `store.REPO_ROOT` and `gitops.repo_root` come from the instance (`repo path`), not from where the package lives. `factory init --repo-name <name>` writes `.factory/` (from a template) and the agent files, and prints "restart the session so the agents register". `factory paths` prints the harness checkout, `bin/factory` and the two workflow scripts, so a dispatcher (the Workflow tool's `scriptPath`) can be pointed at them from any target. `run compose` prepends the instance's `context.md` (fixes the design doc's open "where the block is kept").
C. **Harness revision and lock.** The harness is a git checkout, not a tool-venv install: "install" is `git clone` + `uv sync` once, and a target's `instance.yaml` names the checkout path. `harness.lock` records the harness commit the instance last ran with; `factory` refuses to run when the checkout's HEAD differs from the lock unless `--accept-harness <sha>` rewrites it (an advisory lock with an explicit step, recorded in the log). One checkout, many targets, each target saying which revision it has accepted.
D. **Docs re-layout.** `docs/spec-factory.md` → `docs/design.md` + `docs/changelog.md`; `docs/prompts/` becomes render output; `specs/build-harness.md`, `plans/*.md` → `dev/`; `issues/README.md` → `dev/issues.md`. Every cross-reference in `README.md`, `docs/`, `specs/`, `plans/`, `issues/`, `intake/README.md`, `intake/instance/*` is updated (five files reference the moved paths today: `README.md`, `plans/P0-intake-skeleton.md`, `plans/build-harness.md`, `intake/README.md`, `intake/instance/context.md`; `README.md` line 13 is where `prompts/` is said to be regenerated).
E. **Instance B cutover.** `intake/setup.sh`, `intake/HARNESS_PIN`, `intake/harness/` removed; `intake/state/` → `.factory/state/`; `intake/instance/*` → `.factory/instance.yaml` + `context.md`; `intake/README.md` rewritten as "this repo's own instance". `intake/green-pilot/` (the live pilot store) moves the same way once the pilot closes, or stays as a second instance directory; the planner decides from the pilot's state.
F. **Design-doc text.** §Harness: the role-context block is kept at `.factory/context.md` and prepended by the composer from the instance that owns the run; a harness serving several repos picks the instance by the cwd walk-up. Piece 8: the harness code is itself a protected path in the repo that holds it. Build spec D8 and A/K: `render` reads `docs/design.md` and the instance; `render --check` is kept; paths updated.

**Instance A cutover is not this ticket.** Instance B's own config protects `~/dev/nanobot-upstream/**` as read-only (`reference_harness`), and a sub-ticket merges into one integration branch of one repo (#14). After A–F land, a **paired ticket on instance A, driven by the Driver session** (the Claude Code session that owns green's store and gate decisions), removes `factory/`, `bin/factory`, `tests/factory/` from green, moves `knowledge_vault/spec_factory/` to `.factory/state/`, rewrites `factory/config.yaml` as `instance.yaml`, and re-creates the agent files with `factory init`. Until that lands, green keeps running its in-tree copy. This ticket's scope ends at: the installed harness runs this repo's own `.factory/` end to end, and `factory init` produces a working instance in a throwaway target.

**Decisions:**
- The design doc stays the source of truth for prompts; `docs/prompts/` is rendered output and `render --check` stays (build spec A/K keep their direction, paths change).
- The harness is a pinned checkout, not a tool-venv install; the lock is advisory with an explicit accept step.
- Instance A's cutover is a separate ticket on instance A.

**Out of scope:** the simplifier role (#15); any change to role prompts' wording; the routing table; the store schema; the OpenSpec tree.

**Risk, protected and guardrail paths touched:** on this repo, `intake/**` (B's `infra` class: deleted or moved) and `prompts/**` (B's `generated` class: moved and from then on written by `render`); the design doc and build spec are not protected on B today; listed for the gate's information. Guardrail paths: the role prompts move but do not change in wording. On green, nothing in this ticket; the paired ticket touches `factory/workflows/**`, `factory/config.yaml` (`infra`) and `.claude/agents/**` (guardrail).

**Sequencing:**
- After the first end-to-end pilot (#16 as `intake/green-pilot` T-0001, then #18, both merging into green's `factory/`); the history extraction (A) is cut after those merges, or it misses them.
- #13 and #14 propose text in design doc §Harness / routing and build spec parts B, D, G, H, L, the same files D splits and renames. Their doc edits land first, or D carries them; the planner states which per sub-ticket.
- Enters as a ticket on instance B (the factory's own rule), not as a hand edit.

**Known behaviour, not documented:** `.claude/agents/` registers only if the directory existed at session start, and a directory under `--add-dir` is not watched: observed on 2026-10-01 (#4), not stated in Claude Code's docs. `factory init`'s "restart the session" output and the `inlineRoles` fallback (`intake.js:14,24,27`) are the mitigations.

**Fix as implemented on the Nanobot side:** none. #7's harness side (instance.yaml + context.md in the store root) is also unimplemented.


---

**Operator context at intake (2026-10-02, from the Green session; facts re-derived today):**
- The pilots this issue waits on are done: #16 (green-pilot T-0001) and #18 (T-0002) are merged into green and closed. The latest pilot merge is `7c0a0353d`, so part A's history cut goes at or after it. Green's harness now has 70 tests, not the 55 the body says.
- This instance now runs harness pin `7c0a0353d` with the build half's config (spec-factory `239ef5f`). Its gate is `git diff --check main...HEAD` because this repo has no test suite until part A lands. Once A lands, this instance's gate commands must also run the moved tests (`uv run pytest tests`); a sub-ticket says which one adds that.
- #13 and #14 are still open and not in intake.
- **The live store moves last.** This ticket's own store is `intake/state/`, and part E moves it to `.factory/state/`. The harness cannot move the store it is running from mid-ticket. Recommendation: E does everything but the store move, and the store move (plus `intake/harness/` removal) is a scripted post-close step. The plan names that step and its check (the store opens from `.factory/state/`, and `ticket show` on every ticket still works).
- `intake/green-pilot/` is closed (both tickets), so E moves it too, as a second instance directory or folded in; the planner decides.
- Green's own `factory/config.yaml`, `factory/prompts/{context,preamble}.md` and `scripts/full_suite_gate.py` are nanobot-specific. They stay on green and become instance A's overlay in the paired ticket; they are not moved here.

## Critic findings on your previous version

Round 1 review of T-0012 (harness home, issue #19), spec v1.

What I checked myself (all from `~/dev/spec-factory` on `main` = `f082708`, green read-only at `7c0a035`, which is both green's HEAD and the `Merge factory/T-0002.1` commit the spec calls G):

- Cited paths and symbols on green: `factory/store.py:15-16,36-41` (`REPO_ROOT`, `CONFIG_PATH`, `state_root` with `FACTORY_STATE`), `factory/gitops.py:18-19` (`repo_root`, `FACTORY_REPO`), `factory/compose.py:11,57` (`PROMPTS`, `context.md` first), `factory/cli.py:193-194,198` (`preamble.md` + role prompt written to `system-prompt.txt`; `run start` prints `"run_id": …` JSON), `cli.py:716-719` (`init` = `specstore.init`), `bin/factory` (`cd "$HERE"`, `.venv/bin/python` or `python3`). Six `.claude/agents/factory-*.md`; the pointer line is at line 8 of exactly the four named files. Seven test `.py` files, 1,801 lines; every test sets `FACTORY_STATE` and uses `cwd=REPO` with `REPO = Path(__file__).resolve().parents[2]`. `ticket show` without `--json` dumps YAML (`title: demo` matches), `ticket new --file` takes the title from the first `#` line and starts at `ready-for-triage`, so the B and C scenarios are consistent with the CLI they build on.
- Cited facts here: `README.md:11` text, `docs/spec-factory.md` 759 lines, `## Changelog` at 678, `## Appendix` at 726, 41 numbered entries, `Declined: a dedicated merge agent` at 724, `**Role-context block.**` at 52 ending with "are not fixed here", piece-8 row at 44 starts `| 8 | Guardrail and protected paths`; `prompts/` has 10 files; `prompts/00-preamble.md` lines 1 and 38 carry the two placeholders; `intake/README.md:1`, `intake/HARNESS_PIN` = G, `intake/setup.sh:10-12` archive + three `cp`s; `git ls-files intake | grep -v '^intake/state/'` = 168; tickets T-0001..T-0012.
- Acceptance commands run verbatim today: harness-history-carried → `24`; design-text-kept → `570`; no-old-paths-in-live-files → matches on `README.md` lines 5, 6, 9, 11 (plus the `plans/` lines D.4 rewrites); the `prompt-copies-moved-unchanged` awk range over today's doc → `VERBATIM`; pilot blob count → `134`. `issues/README.md`, `specs/build-harness.md`, `docs/spec-factory.md` and green's `factory/`, `bin/factory`, agent files have no match for any no-stale-references pattern, so moving them unchanged keeps that scenario green. The 7 whitespace errors under `intake/green-pilot/` (blank line at EOF) do not trip `whitespace-clean`: a scratch clone with `git mv` of `intake/green-pilot` and `intake/answers` into `.factory/` gives `git diff --check main~1 HEAD` exit 0 (renames add no lines).
- `issues/README.md` on `main` says #20 and #21 come after #19 and #13/#14 fold into #21, as the spec states.

Findings:

[BLOCKING] 6 proposal.md, Problem, first paragraph
Problem: The first paragraph describes what the harness is and where it lives, but does not say what is wrong or for whom; "wired to that project" and "finds three things next to its own code" leave the reader to infer the defect, and the affected people appear only in the fourth paragraph.
Evidence: Read as the gate operator, new to the system: after paragraph 1 I can say "the harness is bound to the repo it lives in" but not that this is the problem, nor who pays for it (the operator keeping two drifting copies; anyone adopting the factory). The glosses themselves (harness, ticket, store, role-context block, green) are good.
Suggested fix: End paragraph 1 with one sentence of the form "So it can serve only the repo it lives in: the operator who runs it on a second repo (this one) keeps a hand-made copy that drifts, and every new project would have to do the same."

[SHOULD-FIX] 6 design.md, B.2 "The repo root is the directory holding `.factory/`"
Problem: With `FACTORY_INSTANCE` the instance directory need not be named `.factory/` (the test fixture is `tests/factory/fixtures/instance/`), so the rule does not say what the repo root is in that case.
Evidence: B.9 points `FACTORY_INSTANCE` at `tests/factory/fixtures/instance/`; `gitops.repo_root` is read by every build command; the imported tests set `FACTORY_REPO` only in `test_shepherd.py` (line 627), the others rely on the default.
Suggested fix: Say "the parent of the instance directory, whatever it is named; `FACTORY_REPO` still overrides it".

[NIT] 4 design.md, E.1 "Every other key is unchanged"
Problem: That carries `request_dir: ../../issues` into `.factory/instance.yaml`, a key no harness code reads (`grep request_dir factory/*.py` on green: nothing) whose value is relative to the old `intake/harness/` location and names a directory D removes.
Evidence: `intake/instance/config.yaml` line 3; B.5's template key list omits `request_dir`.
Suggested fix: Drop the key in E.1 (and from the template, which already omits it), or say so under Decisions.

[NIT] 2 specs/self-instance/spec.md, instance-b-opens-every-ticket
Problem: Passing the lock at parent close depends on `harness.lock` equalling the harness revision on `main` after the final merge, which E.3 sets "at E's base"; this holds only if no sub-ticket that touches `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock` merges after E branches.
Evidence: Dependencies say A→B→C→E and F touches only `docs/` and `dev/`; D is renames. So the sequence is sound, but the planner must not let a fix-up sub-ticket on harness paths land after E without re-pinning the lock.
Suggested fix: One sentence in E.3 or Risk: "if any later sub-ticket touches harness paths, it also rewrites `harness.lock`".

Not blocking, noted for the record: the spec's Decisions make real design choices (lock on last-touching commit, no fallback instance, generated protected-path line, `init` idempotent) and states each with its reason, so rubric 4 is met; Part A is well above the size guideline but is a verbatim import verified mechanically and is marked NEEDS-SPLIT with six seams; "Tests to change" is correctly `none` (no tests exist here, and the imported suite arrives byte-identical). Every NEW scenario fails today for the stated reason (the files do not exist), and the B/C scenarios would fail against a stub because they check behaviour (`exit=2`, nothing written, the lock bytes, the first line of `input.md`, the filled first line of `system-prompt.txt`), not the presence of code.

Out-of-scope observations:
- `intake/requests/19_harness_home.md` and the T-0012 store files are untracked in the working tree today (`git status intake`); the spec's operator step 2 already covers the request file.
- The design doc's piece-8 and role-context lines are each one physical line, which is what design-text-kept's two `grep -v` exclusions rely on; a later reflow of the doc would need those exclusions revisited.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high — every cited path and symbol checked exists as described; four acceptance commands run verbatim gave the spec's "today" outputs; the one BLOCKING finding is a one-sentence fix to the Problem paragraph, not a design defect.
ESCALATIONS: none

## Your previous spec (v1)

=== proposal.md
## Problem

The spec factory is a set of AI agents (triage, spec writer, critic, planner, implementer, checkers) plus a small program, the **harness**, that moves each piece of work (a **ticket**) from agent to agent, keeps the records, and enforces the rules no prompt can enforce. The harness's code lives inside the first project it was built for, a fork of the Nanobot app (`~/dev/nanobot-upstream`, branch `feat/lionbot-v3`, called "green" below). It is also wired to that project. It finds three things by looking next to its own code: its configuration, its **store** (the folder of ticket records and agent run outputs), and the **role-context block**, a short per-repository briefing that every agent reads first (which repository, how to run its tests, what kind of request to expect).

As a result, the only way to point the factory at a second repository is to copy the code out by hand and overwrite those files. That is how it runs against this design repository today. A script copies a pinned revision of green's harness into an ignored folder and overwrites three files. The pin is a commit id that someone updates by hand. Every project that adopts the factory would repeat that copy. Each copy drifts from the original, and a wrong briefing misleads every agent at once. The checking agents read the same briefing as the authors, so they share the error instead of catching it.

This repository's own layout makes it worse. Four things are mixed together, and the folder names do not say which is which:
- the design (one 759-line document that also holds the 41-item changelog);
- copies of the agents' instructions. The README says they are regenerated from the design document, but nothing regenerates them;
- the working documents for building the factory itself. They sit in `specs/` and `plans/`, the names the design reserves for the factory's own output;
- the install that actually runs the factory on this repository, `intake/`. It calls itself scratch and says to delete it, but it holds twelve tickets of records.

This affects two groups:
- The operator, who runs the factory against two repositories and keeps two drifting copies.
- Anyone who adopts the factory for a new project.

The change has two parts:
- Move the harness code into this repository, with its history, and give each target repository a small `.factory/` folder. That folder holds the repository's configuration, its briefing, the harness revision it has accepted, and its records, so one harness checkout serves many repositories.
- Rename this repository's documents so each folder says what it holds.

Moving green itself onto the new layout is a separate, later ticket.

## Evidence

All commands were run from `~/dev/spec-factory`, branch `main`. During this run, `main` moved from `239ef5f` to `f082708`, but only `issues/README.md` changed. Green (read-only reference) is at its latest pilot merge, subject `Merge factory/T-0002.1: …`. Below that commit is called **G**: `git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3`, which today is green's HEAD.

**The harness locates everything relative to its own code** (green, read with `grep`/`sed`):
- `factory/store.py`: `REPO_ROOT = Path(__file__).resolve().parent.parent` and `CONFIG_PATH = …/"config.yaml"` next to the package. `state_root()` is `FACTORY_STATE` or `REPO_ROOT / cfg["state_dir"]`.
- `factory/gitops.py`: `repo_root()` is `FACTORY_REPO` or `store.REPO_ROOT`.
- `factory/compose.py`: `PROMPTS = Path(__file__).resolve().parent / "prompts"`. The composed input starts with `(PROMPTS / "context.md")`.
- `factory/cli.py`, `run start`: the system prompt is `PROMPTS/preamble.md` + `PROMPTS/<role>.md`.
- `bin/factory`: `cd "$HERE"` (the harness checkout), then `exec "$PY" -m factory`. So a cwd-based lookup inside the package sees the harness directory, not the caller's.
- The four role agent definitions (`.claude/agents/factory-{triage,spec-writer,spec-critic,planner}.md`) each say ``Read `factory/prompts/preamble.md` before anything else``. That is a path relative to the target repo.
- `factory init` exists on green and does something else: it creates the spec-store tree inside the store (`specstore.init`).
- Green's per-repo text is only in `factory/config.yaml`, `factory/prompts/context.md`, and two lines of `factory/prompts/preamble.md`. The first is line 1 (`{repo name}` filled). The second is the protected-paths line (`diff ~/dev/nanobot-upstream/factory/prompts/preamble.md intake/instance/preamble.md` differs only on lines 1 and 38). The seven role prompts in `factory/prompts/` have no repo-specific text: `grep -i 'nanobot\|knowledge_vault\|lionbot'` over them, excluding preamble and context, prints nothing. Gate commands reach the implementer and verifier through their input, not their prompt.

**The second install is a hand copy.** `intake/setup.sh` runs `git -C "$SRC" archive "$PIN" factory bin/factory | tar -x`, then copies `instance/preamble.md`, `instance/context.md` and `instance/config.yaml` over the result. `intake/HARNESS_PIN` holds green's pilot-merge commit. `intake/README.md:1` is `# intake/ — SCRATCH`, and it says "Delete the whole directory once the issues are filed and closed". `git ls-files intake | grep -v '^intake/state/'` lists 168 files (167 without `intake/.gitignore`). The live store, `intake/state/tickets/`, holds T-0001 to T-0012.

**The documents.** `README.md:11`: "The design doc is the source of truth; `prompts/` is regenerated from it." Nothing regenerates them: this repo has no code, and green has no `factory/render.py`. `docs/spec-factory.md` is 759 lines. Its Changelog runs from line 678 and has 41 numbered entries. Line 52 ends "Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here." References to the paths that would move (`git grep` outside the stores) are in `README.md`, `plans/build-harness.md` (9 "Parent:" lines), `plans/P0-intake-skeleton.md:3`, `intake/README.md`, `intake/instance/context.md`, and historical operator answers under `intake/answers/`.

**Green's suite and its config dependence** (trials in a scratch copy: `git archive` of `factory bin/factory tests/factory` from green, run with green's venv, `PYTHONDONTWRITEBYTECODE=1 … pytest -q -p no:cacheprovider tests/factory`; nothing was written in green):
- With green's own config: `70 passed in 92.22s`.
- With this repo's instance config (`intake/instance/config.yaml`): `1 failed, 69 passed`. The failing test checks that an untracked lockfile named in the config's `environment_files` is copied into each worktree. Green lists `uv.lock` there; this repo lists none.
- With this repo's config plus `environment_files: ["uv.lock"]`: `70 passed in 93.51s`.

Every test drives `bin/factory` as a subprocess with `cwd` set to the harness checkout, which it finds as `Path(__file__).resolve().parents[2]`. Moving the tests out of `tests/factory/` would change that root, and running them from a checkout that has its own `.factory/` would give them that instance's config.

**History extraction works** (trial in scratch, green untouched): `git clone --no-local --single-branch --branch feat/lionbot-v3 ~/dev/nanobot-upstream g`, then `git filter-repo --path factory/ --path bin/factory --path tests/factory/ --path-glob '.claude/agents/factory-*' --path-rename .claude/agents/:agents/`, gave 31 commits. `git pull --no-rebase --allow-unrelated-histories` of that into a scratch clone of this repo merged without conflict. Afterwards, acceptance item harness-history-carried printed `0` (`24` on `main` today), and role-prompt-text-unchanged printed `changed=1 of 14`. The one difference is the preamble, which part B replaces.

**The document split works** (trial in the same scratch clone: `git mv` plus an `awk` cut of the Changelog section): docs-moved-and-split printed `old_tracked=0`; changelog-moved-verbatim printed `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`; design-text-kept printed `0`; prompt-copies-moved-unchanged printed `changed=0 of 10 VERBATIM`.

**Sequencing facts.** Green's harness tickets #16 and #18 are merged and closed. `issues/README.md` on `main` (`f082708`) now says #20 and #21 come "after #19", and that "#13, #14 fold in" to #21. Both are "not in intake yet". `uv sync --frozen` here today prints `error: No \`pyproject.toml\` found in current directory or any parent directory`.

## Root cause

The harness treats "the repo I serve" as "the repo I live in":
- `store.REPO_ROOT` and `store.CONFIG_PATH` (config), `store.state_root` (store), `gitops.repo_root` (target repo), `compose.PROMPTS/context.md` (role-context block), and `cli` `run start` (preamble with the repo name and protected paths filled) all resolve from the package's own location.
- `bin/factory` also changes into the harness directory before the package runs, so the caller's location is lost.

The only per-repo seams are the three environment overrides (`FACTORY_STATE`, `FACTORY_REPO`, `FACTORY_INTEGRATION_BRANCH`). They cannot supply config, briefing or preamble. Hence `intake/setup.sh`'s copy and overwrite.

The document confusion is historical. The design doc grew its changelog in place, `prompts/` was copied by hand, the factory's own build spec and plan were filed under the output directory names, and `intake/` started as scratch and became the self-hosting install.

## Out of scope

- **Instance A (green) cutover.** This change does not remove `factory/`, `bin/factory`, `tests/factory/` or the agent files from green, move `knowledge_vault/spec_factory/`, write green's `.factory/`, or run `factory init` there. Nothing is written under `~/dev/nanobot-upstream/`. Green keeps running its in-tree copy until its own paired ticket, driven by the Driver session.
- **Building `factory render` / `render --check`.** Only the build spec's text about them changes (part F). `docs/prompts/` stays a set of verbatim copies, re-copied by hand.
- **Role-prompt wording** (the seven role prompts and the agent definitions' role text stay byte-identical), the routing table, the store's record format, the OpenSpec tree (instance B gets no `openspec/`; `factory init` keeps creating it only where it already did, or in a new instance), and the simplifier role (#15).
- **The text of #13 and #14.** They fold into #21, which comes after #19.
- **Agent files for instance B.** This repo keeps dispatching with inline roles; no `.claude/agents/` is added here.
- **Rewriting records.** Store files, `intake/answers/*` and the green-pilot store move byte-identical, and old paths quoted inside them stay as written.
- **Moving the live store** (`intake/state/` to `.factory/state/`) and deleting `intake/harness/`. This happens after close, as an operator step (below).
- **Detecting uncommitted edits in the harness checkout.** The lock compares committed revisions only.

## Open questions

none. The choices the request left to the planner stay with the planner: where `intake/green-pilot/` goes (subject to it moving byte-identical out of `intake/`), the order of the sub-tickets within the dependencies under design.md, and which sub-ticket puts the moved suite into this instance's gate. The design calls this spec makes are under Decisions, and the gate can override any of them.

## Decisions

- **The lock pins the harness's own code, not the checkout's HEAD.** The harness revision is the last commit that touched `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock`. A HEAD lock would refuse after every store or document commit in this repo, which is both the harness and instance B.
- **The lock guards the instance's own store only.** A run against any other store (`FACTORY_STATE` pointing elsewhere, as every test does) is not checked.
- **`FACTORY_INSTANCE` is added as an override** (the path of a `.factory/` directory), beside the walk-up. The workflows' clerk runs from the harness checkout, where the walk-up would find the harness repo's own instance, and the tests need a fixed instance.
- **No fallback.** When no instance is found, the command is refused and nothing is written. The harness never uses an instance of its own by default.
- **No per-instance preamble file.** The harness keeps the design doc's preamble block verbatim and, at run start, fills `{repo name}` and the protected-path line from `instance.yaml`. The protected-path line is generated from the globs as `class (glob, glob), …`. Instances B and A lose their hand-written prose on that line (for example "never read or written by any role"); such notes belong in `context.md`.
- **The agent definitions' preamble pointer** changes to the run directory's `system-prompt.txt`, which `run start` already writes with the filled preamble. The role text below it is unchanged.
- **One `factory init` verb.** It is idempotent and creates whatever is missing: the instance, the briefing stub, the lock, the store with today's spec-store tree, and the agent files. `--repo-name` is required only when `instance.yaml` is missing.
- **The tests stay at `tests/factory/`**, not `tests/`, because they locate the checkout two levels up. A new `tests/factory/conftest.py` points them at a fixed test instance (one test needs `environment_files: ["uv.lock"]`; see Evidence). No existing test file changes.
- **Instance B's harness is this repo's own checkout** (`harness: .`), installed with `uv sync`. No separate clone is required.
- **Instance B's gate adds the moved suite**: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, next to `git diff --check main...HEAD`. Instance B's protected paths add a `harness` class (`factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`) and `.factory/**` under `infra`, and `generated` follows the copies to `docs/prompts/**`.
- **#13 and #14 are not carried.** No #13/#14 text merges while this parent is in flight. `main` already folds them into #21, after #19.
- **Part A runs `git filter-repo` only on a fresh clone of green in a scratch directory**, never in `~/dev/nanobot-upstream`.
- **Green-only files are not in this repo's tree at close:** `factory/config.yaml`, `factory/prompts/{context,preamble}.md` as green has them, and `scripts/full_suite_gate.py`. They may appear in the imported history.
- **The live store moves after close** (operator note at intake). Until then `.factory/instance.yaml` names `intake/state` as its store.

## Risk

**Blast radius.** This repo's whole layout, and every instance B run after close, which then reads a new config location and runs the in-repo harness. The history grows by about 31 imported commits. Green is unaffected until its own ticket.

**Lock behaviour after close.** Any later merge that touches harness code makes instance B refuse store commands until the operator runs `--accept-harness`. A build workflow in flight at that moment parks the ticket as a harness bug, by design. This ticket's own build runs on the old copy in `intake/harness/`, which has no lock, so it is not affected.

**Part A size.** Part A is about 4,400 imported lines plus `uv.lock`: 2,557 lines of package, workflows and `bin/factory`, and 1,801 lines across 7 test `.py` files plus fixtures. That is far above the 400-line guideline, but it is a verbatim import. It is verified mechanically (history subjects, byte comparison of the role prompts, the suite) rather than by reading. Part A's own non-import diff is small: `pyproject.toml`, `.gitignore`, and the interim overlay.

**Fragile acceptance anchor.** Items harness-history-carried and role-prompt-text-unchanged find green's pilot merge by its subject. If part A cuts later than G and green changes a role prompt in between, role-prompt-text-unchanged compares against the wrong revision. Check `git -C ~/dev/nanobot-upstream log G..feat/lionbot-v3 -- factory/prompts .claude/agents` (empty today, since G is green's HEAD).

**Protected paths touched** (instance B's current classes, declared for the gate):
- **infra `intake/**`**: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed. `intake/answers/` and `intake/green-pilot/` move out, byte-identical. `intake/state/**` and `intake/.gitignore` are not changed by the PRs; the post-close operator step moves them.
- **generated `prompts/**`**: moved to `docs/prompts/`, byte-identical.
- **reference_harness `~/dev/nanobot-upstream/**`**: read only. Part A clones it into a scratch directory; acceptance reads it with `git log`, `git show` and `git cat-file`.
- **credentials `~/.nanobot/**`**: not read or written.

**Guardrail paths touched:**
- **Agent prompts.** The six agent definitions move to `agents/`, and four of them get the new pointer line. The seven role prompts move to `factory/prompts/` byte-identical. The preamble becomes the design doc's block verbatim. The `prompts/` copies move to `docs/prompts/`.
- **Tests.** There are no existing tests in this repo. `tests/factory/**` arrives as new files, byte-identical to green's. New test files and the new `conftest.py` with its fixture instance are added. The conftest changes which config every imported test runs with: the fixed fixture instead of whatever instance surrounds the checkout.
- No CI config, `AGENTS.md` or skills exist here.

## Operator steps

1. **Optional, during the build, after part A merges.** Run `uv sync` in `~/dev/spec-factory`. Then append `uv run --frozen pytest -q -p no:cacheprovider tests/factory` to `gate_commands` in the running copy's `intake/harness/factory/config.yaml`, so that later sub-tickets are gated by the moved suite. That file is live, gitignored infra.
2. **After the parent closes**, with the store committed and no run in flight, move the live store:
   - `git mv intake/state .factory/state`.
   - In `.factory/instance.yaml`, set `state_dir: .factory/state` and drop `intake/**` from `protected_paths.infra`.
   - `git rm -q intake/.gitignore && rm -rf intake/harness`.
   - Move or delete anything still under `intake/` (untracked; today `intake/requests/19_harness_home.md`).
   - Check: `bin/factory paths` shows `state` ending in `/.factory/state`, and the command of scenario instance-b-opens-every-ticket prints `tickets=N failed=0` with N ≥ 12.
   - Commit.
3. **End-to-end run.** Run the next ticket (#20 or #21) through the moved harness: take `intake_workflow` from `bin/factory paths`, and call the Workflow tool with `{ticket, repo: <abs ~/dev/spec-factory>, instance: <abs ~/dev/spec-factory/.factory>, inlineRoles: true}`. This is the request's "the installed harness runs this repo's own `.factory/` end to end". It needs agent runs, so it is not an acceptance command.
4. **Bookkeeping.** Update the #19 row in `dev/issues.md` and close GitHub #19. Then open the paired instance-A ticket for the Driver session.

=== design.md
## Proposed change

There are six parts, A to F; this is the NEEDS-SPLIT seam list. Dependencies: A before B before C before E. D can land at any point. F comes after D. E comes after B, C and D. All paths are relative to `~/dev/spec-factory` unless they start with `~/`.

**A. Harness import, with history.** Part A's tip has the harness in this repo and its suite green. It makes no behaviour change.
1. Make a fresh scratch clone: `git clone --no-local --single-branch --branch feat/lionbot-v3 ~/dev/nanobot-upstream <scratch>/g`. Its tip must be at or after G. Never run `filter-repo` in `~/dev/nanobot-upstream`.
2. In the clone: `git filter-repo --path factory/ --path bin/factory --path tests/factory/ --path-glob '.claude/agents/factory-*' --path-rename .claude/agents/:agents/`.
3. On the sub-ticket branch: `git pull --no-rebase --allow-unrelated-histories --no-edit <scratch>/g HEAD`. No paths overlap.
4. Remove the three green-only files from the tree and replace them with an **interim overlay**, which is this repo's current instance files. Part B deletes it.
   - `factory/config.yaml` becomes `intake/instance/config.yaml`, with `state_dir: intake/state` (now relative to this repo's root) and `environment_files: ["uv.lock"]`. The suite needs the latter (Evidence).
   - `factory/prompts/context.md` becomes `intake/instance/context.md`.
   - `factory/prompts/preamble.md` becomes `intake/instance/preamble.md`.
   - Every other imported file stays byte-identical to green at the cut.
5. Add `pyproject.toml` with:
   - `[project] name = "spec-factory"`, `version = "0.0.0"`, `requires-python = ">=3.11"`, `dependencies = ["pyyaml>=6"]`;
   - `[dependency-groups] dev = ["pytest>=8"]`;
   - `[tool.uv] package = false`.
   `bin/factory` runs `python -m factory` from the checkout, so no build backend is needed. Run `uv lock` and commit `uv.lock`. Add a root `.gitignore` with `.venv/`, `__pycache__/` and `.pytest_cache/`.
6. Check: `uv sync --frozen && PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` reports 70 passed.

**B. Instances: discovery, config, briefing, preamble, `init`, `paths`.**
1. **One instance resolver**, used by `store`, `gitops`, `compose` and `cli`:
   - If `FACTORY_INSTANCE` is set, it names the instance's `.factory/` directory.
   - Otherwise, walk up from the caller's working directory to the nearest directory that contains `.factory/instance.yaml`. `bin/factory` must hand the package the caller's working directory, since it changes into the harness checkout before running.
   - If nothing is found, exit 2 with stderr `no .factory/instance.yaml found from <cwd>; run factory init --repo-name NAME, or set FACTORY_INSTANCE`, and write nothing. There is no fallback to the harness checkout.
   - `init` and `paths` are exempt.
2. **Where things come from:**
   - Config is `<instance>/instance.yaml`. This replaces `store.CONFIG_PATH`; the keys are today's config keys plus `harness`.
   - The repo root is the directory holding `.factory/`. `FACTORY_REPO` still overrides it.
   - `state_dir` is relative to the repo root. `FACTORY_STATE` still overrides it.
   - `FACTORY_INTEGRATION_BRANCH` is unchanged.
3. **Role-context block.** `run compose` opens `input.md` with `<instance>/context.md`. Delete `factory/prompts/context.md`.
4. **Preamble.** `factory/prompts/preamble.md` becomes the design doc's preamble block verbatim, byte-identical to `prompts/00-preamble.md` (later `docs/prompts/00-preamble.md`). `run start` writes `system-prompt.txt` with two substitutions:
   - `{repo name}` becomes the instance's `repo_name`.
   - The line `  {auth, payments, migrations, infra, public API, dependencies}` becomes two spaces followed by `<class> (<glob>, <glob>)` for each `protected_paths` entry, joined by `, `.
   The seven role prompt files do not change.
5. **`factory init [--repo-name NAME]`** works at the git top level of the working directory, and exits 2 outside a git work tree. It is idempotent and creates only what is missing:
   - `.factory/instance.yaml`, from a new `factory/instance.template.yaml`. It sets `repo_name`, `harness` (the absolute path of the running harness checkout), `state_dir: .factory/state`, `protected_paths: {infra: [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]}` and `gate_commands: []`. Today's generic values come with it: placeholders, `max_rounds`, `integration_branch: null`, `environment_files: []`, `force_push_allowed: false`, `models`, `ready_state`, `routing`. It needs `--repo-name`; without one, it exits 2.
   - `.factory/context.md`, from a new `factory/context.template.md`: a stub that says what the briefing must state.
   - `.factory/harness.lock`: the current harness revision (C).
   - The store at `state_dir`, with today's `init` content (the spec-store tree, `decisions.md`) and the store `.gitignore`.
   - `.claude/agents/factory-*.md`, copied from `agents/` for each missing file. When it writes any agent file, it prints `restart the session so the agents register`.
   After a fresh `init`, `.factory/` holds exactly `context.md`, `harness.lock`, `instance.yaml` and `state`. With an instance present and `--repo-name` omitted, it does today's `init` plus any missing pieces.
6. **`factory paths`** prints one JSON object with absolute paths: `harness`, `bin`, `intake_workflow`, `build_workflow`, `harness_revision` (C), `instance` and `state`. The last two are `null` when no instance is found. It runs no lock check and writes nothing.
7. **Agent templates.** In `agents/factory-{triage,spec-writer,spec-critic,planner}.md`, replace the line ``Read `factory/prompts/preamble.md` before anything else; it is the top of your system prompt.`` with ``Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.`` Nothing else in `agents/` changes.
8. **Workflows.** `factory/workflows/intake.js` and `build.js` accept `instance`, the absolute path of the target's `.factory/`. When it is given, every store command is prefixed with `FACTORY_INSTANCE=<instance>`. `state` becomes optional (it still sets `FACTORY_STATE`), and `repo` stays the harness checkout. Update the header comments.
9. **Tests.**
   - Add a new `tests/factory/conftest.py` that sets `os.environ["FACTORY_INSTANCE"]` at import to a new fixture, `tests/factory/fixtures/instance/`. The fixture has `instance.yaml` with the template values plus `environment_files: ["uv.lock"]` and `gate_commands: ["git diff --check main...HEAD"]`, and a `context.md`. Every existing test already builds its subprocess environment from `os.environ`.
   - Add new test files for B's behaviours.
   - Delete A's interim `factory/config.yaml`. Its `prompts/context.md` was deleted in item 3.

**C. Harness revision and lock.**
1. The **harness revision** is `git -C <harness> log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`.
2. **When the store in use is the instance's own store** (`FACTORY_STATE` is unset or resolves to the instance's `state_dir`), every command except `init` and `paths` first compares the stripped first line of `<instance>/harness.lock` with the revision. If they differ, or the lock is missing, the command exits 2 with stderr `harness <rev> is not the revision this instance accepted (<lock>|none); rerun with --accept-harness <rev> to accept it`, and writes nothing. Other stores are not checked.
3. **`--accept-harness SHA`** is a global option, written before the subcommand.
   - The SHA must equal the current revision, as 40 hex characters. Otherwise the command exits 2 and leaves the lock unchanged.
   - If it matches, the harness writes the SHA to `harness.lock` and appends a log event to the instance's store recording the old and new revisions, then runs the command.
4. Add new test files for C.

**D. Document re-layout.** Content is unchanged apart from the path updates.
1. `git mv docs/spec-factory.md docs/design.md`. Then move its `## Changelog` section, from the heading to the line before `## Appendix`, into a new `docs/changelog.md`: a `# Changelog` title, then that text verbatim (intro paragraph, numbered entries, `Declined:` line). At the end of "How to use this" in `docs/design.md`, add one line naming `docs/changelog.md` and `docs/prompts/`.
2. `git mv prompts docs/prompts`. The bytes do not change.
3. `git mv specs/build-harness.md dev/build-harness.spec.md`, `git mv plans/build-harness.md dev/build-harness.plan.md`, `git mv plans/P0-intake-skeleton.md dev/P0-intake-skeleton.md`, `git mv issues/README.md dev/issues.md`.
4. Update the references in:
   - `README.md` (until E rewrites it);
   - `dev/build-harness.plan.md` (the nine `Parent:` lines);
   - `dev/P0-intake-skeleton.md:3`;
   - `intake/README.md` and `intake/instance/context.md` (while they still exist).
   Records are left as written: `intake/answers/`, the stores, and changelog entries.

**E. Instance B cutover.** The live store does not move in this part.
1. `.factory/instance.yaml` starts from `intake/instance/config.yaml`, with these changes:
   - `repo_name: "spec-factory (the design repo at ~/dev/spec-factory, branch main)"`, `harness: .` and `state_dir: intake/state`.
   - `protected_paths`: `infra: [".factory/**", "intake/**"]`, `harness: ["factory/**", "bin/factory", "agents/**", "pyproject.toml", "uv.lock"]`, `generated: ["docs/prompts/**"]`, `reference_harness: ["~/dev/nanobot-upstream/**"]`, `credentials: ["~/.nanobot/**"]`.
   - `gate_commands: ["git diff --check main...HEAD", "uv run --frozen pytest -q -p no:cacheprovider tests/factory"]` and `environment_files: []`. `uv.lock` is tracked here, and copying it in would mask a branch's own lock.
   - Every other key is unchanged.
2. `.factory/context.md` is `intake/instance/context.md` rewritten for the new layout. It names:
   - `docs/design.md` (source of truth) and `docs/changelog.md`;
   - `docs/prompts/` (verbatim copies, changed only by re-copying);
   - `dev/` (working documents for building the factory);
   - the harness as code in this repo (`factory/`, `bin/factory`, `agents/`, `tests/factory/`, run with `uv run --frozen pytest -q -p no:cacheprovider tests/factory`);
   - green as instance A, read only.
   It keeps the existing rules on acceptance commands and design-doc conventions, with the paths updated.
3. `.factory/harness.lock` holds the harness revision (C.1) at E's base.
4. `.factory/README.md` carries the still-true parts of `intake/README.md`: the ticket to GitHub-issue table, how to run, and scope, written as "this repo's own instance".
5. Remove `intake/README.md`, `intake/setup.sh`, `intake/HARNESS_PIN` and `intake/instance/*`. Move `intake/answers/` to `.factory/answers/`, byte-identical. Move `intake/green-pilot/` out of `intake/`, byte-identical, to a place the planner chooses: a second instance directory or a folded-in archive. Keep `intake/state/` and `intake/.gitignore`.
6. Rewrite `README.md`:
   - what the factory is;
   - install (`git clone`, `uv sync`);
   - five-minute use: `factory init --repo-name`, restart the session, fill in `.factory/context.md` and `gate_commands`, `factory paths`, the Workflow call with `scriptPath` and `{ticket, repo, instance}`, and `approve-spec`;
   - where things live: `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, `dev/`, `factory/`, `bin/factory`, `agents/`, `tests/factory/`, `.factory/`.

**F. Design-doc and build-spec text.**
1. **`docs/design.md`, §Harness, "Role-context block" paragraph.** Replace its last sentence ("Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here.") with:
   "The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`."
2. **`docs/design.md`, piece 8 row ("Guardrail and protected paths"), "What it must do" cell.** Append: "The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it."
3. **`docs/changelog.md`.** Append one entry, numbered one past the last entry at merge time (42 today):
   "After issue #19 (2026-10-02): the harness lives in this repo and each target repo carries a `.factory/` instance: `instance.yaml`, `context.md` (the role-context block, prepended by the composer), `harness.lock` (the accepted harness revision; any other revision is refused until a human accepts it) and the store. The harness finds the instance by walking up from the working directory, and its own code is a protected path in the repo that holds it. The design doc splits into `docs/design.md` and this changelog, the prompt copies move to `docs/prompts/`, and the working documents for building the factory move to `dev/`."
4. **`dev/build-harness.spec.md`.**
   - D8 row, Value column: "per instance: `repo_name` and `protected_paths` in the target repo's `.factory/instance.yaml` (doc §Harness, role-context block); for nanobot: `nanobot`; protected: `infra`, `dependencies`, `credentials`, `public API` (globs in F)".
   - Layout row `factory/prompts/design-doc.md`: becomes `docs/design.md (spec-factory, beside the harness)  the design doc; the only doc `factory render` reads (A)`.
   - Part A's `factory render` bullet: it reads `docs/design.md`, which is in the same repo as the harness, and still has no `--doc` option. It writes `docs/prompts/` and the `agents/` templates from the blocks. The placeholders are filled per instance from `.factory/instance.yaml` when a run starts, and `render --check` diffs against `docs/design.md`.
   - Item 82: every `factory/prompts/design-doc.md` becomes `docs/design.md`.
   - Leave the `## Responses` history as written.

Size per part:
- A: import plus about 40 lines of its own.
- B: about 300 lines including new tests.
- C: about 120.
- D: renames plus about 30.
- E: about 150 plus renames.
- F: about 15.

## Tests to change

none. This repo has no existing tests. `tests/factory/**` arrives byte-identical. The new `conftest.py`, the fixture instance and the new test files are new files. See Risk for the conftest's effect on the imported tests.

=== specs/harness-home/spec.md
## ADDED Requirements

### Requirement: harness-code-lives-in-design-repo
The harness package, its entry point, its two workflow scripts, its test suite and the six agent definition templates MUST be tracked in this repository, and green's repo-specific config and briefing MUST NOT be.

#### Scenario: harness-files-in-repo
- WHEN `for p in factory/cli.py factory/store.py factory/compose.py factory/gitops.py factory/workflows/intake.js factory/workflows/build.js bin/factory pyproject.toml uv.lock tests/factory/test_p0_cli.py; do test -e "$p" || echo "missing $p"; done; echo "agents=$(ls agents/factory-*.md 2>/dev/null | wc -l | tr -d ' ') green_only=$(ls factory/config.yaml factory/prompts/context.md 2>/dev/null | wc -l | tr -d ' ')"`
- THEN it prints only `agents=6 green_only=0`

### Requirement: harness-history-carried
Every non-merge commit of green, up to its latest pilot merge, that touched the harness package code, workflows, entry point, tests or factory agent definitions SHALL appear in this repository's history with the same subject.

#### Scenario: harness-history-carried
- WHEN `G=$(git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3); comm -23 <(git -C ~/dev/nanobot-upstream log --no-merges --format=%s "$G" -- 'factory/*.py' factory/workflows bin/factory tests/factory '.claude/agents/factory-*' | sort -u) <(git log --no-merges --format=%s -- 'factory/*.py' factory/workflows bin/factory tests/factory 'agents/factory-*' | sort -u) | wc -l | tr -d ' '`
- THEN it prints `0`

### Requirement: harness-installs-with-uv
`uv sync` in a checkout of this repository SHALL give the harness its interpreter and dependencies, and the moved test suite MUST pass there.

#### Scenario: harness-suite-passes-after-uv-sync
- WHEN `uv sync --frozen -q >/dev/null 2>&1; echo "sync=$?"; PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1`
- THEN it prints `sync=0`, then a line `N passed in …` with N ≥ 70 and no `failed` or `error`

### Requirement: role-prompt-text-unchanged
The role prompts and agent definitions MUST move without any change to their wording: the agent templates differ from green's only in the preamble pointer line, the seven role prompts are byte-identical to green's, and the harness's preamble is byte-identical to the design doc's copy.

#### Scenario: role-prompt-text-unchanged
- WHEN `G=$(git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3); c=0; n=0; for f in factory-clerk factory-planner factory-spec-critic factory-spec-writer factory-stub factory-triage; do n=$((n+1)); cmp -s <(git -C ~/dev/nanobot-upstream show "$G:.claude/agents/$f.md" | grep -v 'before anything else') <(grep -v 'before anything else' "agents/$f.md" 2>/dev/null) || c=$((c+1)); done; for f in triage spec_writer critic planner implementer reviewer verifier; do n=$((n+1)); cmp -s <(git -C ~/dev/nanobot-upstream show "$G:factory/prompts/$f.md") "factory/prompts/$f.md" || c=$((c+1)); done; n=$((n+1)); cmp -s factory/prompts/preamble.md docs/prompts/00-preamble.md || c=$((c+1)); echo "changed=$c of $n"`
- THEN it prints `changed=0 of 14`

=== specs/factory-instance/spec.md
## ADDED Requirements

### Requirement: instance-created-by-init
`factory init --repo-name NAME`, run anywhere inside a git work tree with no instance, SHALL create `.factory/` at that tree's top level holding `instance.yaml`, `context.md`, `harness.lock` and the store, SHALL copy the six agent definitions into `.claude/agents/`, and SHALL tell the operator to restart the session.

#### Scenario: init-creates-instance-in-throwaway-target
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; echo "instance=[$(ls -A $T/.factory 2>/dev/null | tr '\n' ' ')] agents=$(ls $T/.claude/agents/factory-*.md 2>/dev/null | wc -l | tr -d ' ') restart=$(grep -c 'restart the session' $T/init.out)"`
- THEN it prints `init=0` then `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1`

### Requirement: instance-found-from-working-directory
Every store command SHALL use the instance found by walking up from the caller's working directory, and MUST NOT write into the harness checkout.

#### Scenario: store-command-from-subdirectory-uses-target-instance
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; before=$(git -C $H status --porcelain | wc -l); $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; echo "new=$? tickets=[$(ls $T/.factory/state/tickets 2>/dev/null)] harness_changes=$(( $(git -C $H status --porcelain | wc -l) - before ))"`
- THEN it prints `init=0` then `new=0 tickets=[T-0001.yaml] harness_changes=0`

### Requirement: no-instance-refused
A store command run where no instance is found and no override is set MUST be refused with exit 2, an error naming `instance.yaml`, and nothing written.

#### Scenario: command-outside-any-instance-refused
- WHEN `H=$PWD; D=$(mktemp -d); cd $D && $H/bin/factory ticket show T-0001 >$D/out 2>$D/err; echo "exit=$? created=$(ls -A $D | grep -v -x -e out -e err | wc -l | tr -d ' ') names_instance=$(grep -c 'instance.yaml' $D/err)"`
- THEN it prints `exit=2 created=0 names_instance=1`

### Requirement: instance-override
`FACTORY_INSTANCE` SHALL select the instance regardless of the working directory.

#### Scenario: factory-instance-override-from-elsewhere
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; D=$(mktemp -d); cd $D && echo "found=$(FACTORY_INSTANCE=$T/.factory $H/bin/factory ticket show T-0001 2>/dev/null | grep -c '^title: demo$')"`
- THEN it prints `init=0` then `found=1`

### Requirement: compose-prepends-instance-context
Every composed role input SHALL begin with the `context.md` of the instance that owns the run.

#### Scenario: composed-input-opens-with-instance-context
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf 'CTX-MARKER for demo\n' 2>/dev/null > $T/.factory/context.md; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; R=$($H/bin/factory run start --role triage --ticket T-0001 --model opus 2>/dev/null | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); $H/bin/factory run compose "$R" >/dev/null 2>&1; echo "first=[$(head -1 $T/.factory/state/runs/$R/input.md 2>/dev/null)]"`
- THEN it prints `init=0` then `first=[CTX-MARKER for demo]`

### Requirement: preamble-filled-from-instance
The system prompt written at run start SHALL carry the preamble with the instance's repo name and protected paths filled in and no placeholder left.

#### Scenario: run-system-prompt-names-instance
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; R=$($H/bin/factory run start --role triage --ticket T-0001 --model opus 2>/dev/null | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); P=$T/.factory/state/runs/$R/system-prompt.txt; echo "line1=[$(head -1 $P 2>/dev/null)] placeholders=$(grep -c -e '{repo name}' -e '{auth, payments' $P 2>/dev/null) protects_instance=$(grep -c '\.factory/instance\.yaml' $P 2>/dev/null)"`
- THEN it prints `init=0` then `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1`

### Requirement: paths-printed
`factory paths` SHALL print, as JSON, the harness checkout, its entry point, both workflow scripts, the harness revision and the instance in use, so a dispatcher in any target can be pointed at them.

#### Scenario: paths-name-harness-workflows-and-instance
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; $H/bin/factory paths >$T/p.json 2>/dev/null; python3 -c 'import json,os,sys; p=json.load(open(sys.argv[1])); r=os.path.realpath; print(r(p["harness"])==r(sys.argv[2]), all(os.path.isfile(p[k]) for k in ("bin","intake_workflow","build_workflow")), r(p["instance"])==r(sys.argv[3]+"/.factory"), len(p["harness_revision"])==40)' $T/p.json $H $T 2>/dev/null || echo "no paths"`
- THEN it prints `init=0` then `True True True True`

=== specs/harness-lock/spec.md
## ADDED Requirements

### Requirement: unaccepted-harness-refused
When the store in use is the instance's own store, every command except `init` and `paths` MUST be refused (exit 2, nothing written, a hint naming `--accept-harness`) if the instance's `harness.lock` does not name the running harness revision.

#### Scenario: lock-mismatch-refused
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>$T/err; echo "exit=$? tickets=$(ls $T/.factory/state/tickets 2>/dev/null | wc -l | tr -d ' ') hint=$(grep -c 'accept-harness' $T/err)"`
- THEN it prints `init=0` then `exit=2 tickets=0 hint=1`

### Requirement: accept-harness-is-explicit-and-logged
`--accept-harness SHA` SHALL rewrite the lock and log the acceptance only when SHA is the running harness revision, and MUST leave the lock unchanged and refuse otherwise.

#### Scenario: accept-current-revision-rewrites-lock
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; REV=$($H/bin/factory paths 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["harness_revision"])' 2>/dev/null); $H/bin/factory --accept-harness "$REV" ticket new --file $T/r.md >/dev/null 2>&1; echo "exit=$? lock_is_rev=$([ -n "$REV" ] && [ "$(cat $T/.factory/harness.lock 2>/dev/null)" = "$REV" ] && echo yes || echo no) logged=$(cat $T/.factory/state/log/*.jsonl 2>/dev/null | grep "$REV" | grep -c harness)"`
- THEN it prints `init=0` then `exit=0 lock_is_rev=yes logged=N` with N ≥ 1

#### Scenario: accept-other-revision-refused
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; $H/bin/factory --accept-harness 1234567 ticket new --file $T/r.md >/dev/null 2>&1; echo "exit=$? lock=$(cat $T/.factory/harness.lock 2>/dev/null) tickets=$(ls $T/.factory/state/tickets 2>/dev/null | wc -l | tr -d ' ')"`
- THEN it prints `init=0` then `exit=2 lock=0000000000000000000000000000000000000000 tickets=0`

### Requirement: throwaway-store-not-locked
A command whose store is not the instance's own store (`FACTORY_STATE` pointing elsewhere) SHALL run whatever the lock says.

#### Scenario: throwaway-store-ignores-lock
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; S=$(mktemp -d); FACTORY_STATE=$S $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; echo "exit=$? ticket=[$(ls $S/tickets 2>/dev/null)]"`
- THEN it prints `init=0` then `exit=0 ticket=[T-0001.yaml]`

=== specs/repo-layout/spec.md
## ADDED Requirements

### Requirement: documents-say-what-they-are
The design doc SHALL be `docs/design.md` with its changelog split out verbatim into `docs/changelog.md`, the prompt copies SHALL be under `docs/prompts/` byte-identical, and the working documents for building the factory SHALL be under `dev/`; the old paths MUST NOT be tracked.

#### Scenario: docs-moved-and-split
- WHEN `for p in docs/design.md docs/changelog.md docs/prompts/00-preamble.md dev/build-harness.spec.md dev/build-harness.plan.md dev/P0-intake-skeleton.md dev/issues.md; do git ls-files --error-unmatch "$p" >/dev/null 2>&1 || echo "missing $p"; done; echo "old_tracked=$(git ls-files docs/spec-factory.md specs plans issues prompts | wc -l | tr -d ' ')"`
- THEN it prints only `old_tracked=0`

#### Scenario: changelog-moved-verbatim
- GIVEN `BASE` is the parent's recorded base commit (the parent-close input `base`); on today's checkout, `export BASE=$(git rev-parse main)`
- WHEN `old() { git show "$BASE:docs/spec-factory.md" | awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' | grep '^[0-9][0-9]*\. '; }; diff <(old) <(grep '^[0-9][0-9]*\. ' docs/changelog.md 2>/dev/null | head -n "$(old | wc -l)") >/dev/null && echo SAME || echo DIFFERENT; echo "declined=$(grep -c '^Declined: a dedicated merge agent' docs/changelog.md 2>/dev/null) numbering=$(grep '^[0-9][0-9]*\. ' docs/changelog.md 2>/dev/null | awk -F. '$1!=NR{g=1} END{print (NR==0?"NONE":(g?"GAP":"CONTIGUOUS"))}') in_design=$(grep -c '^## Changelog' docs/design.md 2>/dev/null)"`
- THEN it prints `SAME` then `declined=1 numbering=CONTIGUOUS in_design=0`

#### Scenario: design-text-kept
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `comm -23 <(git show "$BASE:docs/spec-factory.md" | awk '/^## Changelog/{f=1} /^## Appendix/{f=0} !f' | sort -u) <(sort -u docs/design.md 2>/dev/null) | grep -v -e '^\*\*Role-context block\.\*\*' -e '^| 8 | Guardrail and protected paths' | wc -l | tr -d ' '`
- THEN it prints `0`: every line of the old doc outside its Changelog is still in `docs/design.md`, except the two lines part F rewrites

#### Scenario: prompt-copies-moved-unchanged
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `c=0; n=0; for f in $(git ls-tree --name-only "$BASE" prompts/); do n=$((n+1)); git show "$BASE:$f" | cmp -s - "docs/$f" || c=$((c+1)); done; v=$(awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/design.md 2>/dev/null | cmp -s - docs/prompts/02-spec-writer.md && echo VERBATIM || echo DRIFT); echo "changed=$c of $n $v"`
- THEN it prints `changed=0 of 10 VERBATIM`

### Requirement: no-stale-references
The live documents, the instance's config and briefing, the agent templates and the harness code MUST NOT name a moved or removed path.

#### Scenario: no-old-paths-in-live-files
- WHEN `git grep -n -e 'docs/spec-factory\.md' -e 'specs/build-harness\.md' -e 'plans/build-harness\.md' -e 'plans/P0-intake-skeleton\.md' -e 'issues/README\.md' -e 'HARNESS_PIN' -e 'intake/setup\.sh' -e '[^/a-z_]prompts/' -e '^prompts/' -- README.md docs dev .factory/instance.yaml .factory/context.md agents factory >/dev/null; echo "exit=$?"`
- THEN it prints `exit=1` (no match)

### Requirement: install-documented
`README.md` SHALL state how to install the harness and start an instance, and where each kind of file lives.

#### Scenario: readme-has-install-and-layout
- WHEN `for s in 'git clone' 'uv sync' 'factory init' 'factory paths' '.factory/' 'dev/' 'docs/prompts/'; do grep -qF -- "$s" README.md || echo "missing: $s"; done; echo checked`
- THEN it prints only `checked`

### Requirement: design-doc-names-the-instance
The design doc SHALL say where the role-context block is kept and how a multi-repo harness picks the instance, SHALL make the harness code a protected path in its own repo, and its changelog SHALL record the change.

#### Scenario: design-doc-instance-text
- WHEN `echo "kept=$(grep '^\*\*Role-context block\.\*\*' docs/design.md 2>/dev/null | grep -c '\.factory/context\.md') open=$(grep -c 'are not fixed here' docs/design.md 2>/dev/null) piece8=$(grep '^| 8 |' docs/design.md 2>/dev/null | grep -c 'harness code') logged=$(grep '^[0-9][0-9]*\. ' docs/changelog.md 2>/dev/null | grep -c 'harness\.lock')"`
- THEN it prints `kept=1 open=0 piece8=1 logged=1`

### Requirement: build-spec-render-reads-design-doc
The build spec SHALL say that `factory render` reads `docs/design.md` and that the repo name and protected paths come from each instance's `instance.yaml`, outside its historical Responses.

#### Scenario: build-spec-render-paths
- WHEN `echo "stale=$(awk '/^## Responses/{exit} {print}' dev/build-harness.spec.md 2>/dev/null | grep -c 'factory/prompts/design-doc\.md') new=$(grep -c 'docs/design\.md' dev/build-harness.spec.md 2>/dev/null) d8=$(grep '^| D8 |' dev/build-harness.spec.md 2>/dev/null | grep -c 'instance\.yaml')"`
- THEN it prints `stale=0 new=N d8=1` with N ≥ 3

=== specs/self-instance/spec.md
## ADDED Requirements

### Requirement: intake-reduced-to-live-store
At parent close, nothing SHALL remain tracked under `intake/` except the live store `intake/state/` and `intake/.gitignore`, which the post-close operator step moves.

#### Scenario: intake-holds-only-live-store
- WHEN `echo "left=$(git ls-files intake | grep -v -e '^intake/state/' -e '^intake/\.gitignore$' | wc -l | tr -d ' ')"`
- THEN it prints `left=0`

### Requirement: closed-records-kept
Every file of the closed green-pilot store and of the operator answers MUST still be tracked, byte-identical, outside `intake/`.

#### Scenario: pilot-store-and-answers-kept-byte-identical
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `A=$(mktemp); B=$(mktemp); git ls-tree -r "$BASE" -- intake/green-pilot intake/answers | awk '{print $3}' | sort -u >$A; git ls-tree -r HEAD | awk -F'\t' '$2 !~ /^intake\//{print $1}' | awk '{print $3}' | sort -u >$B; echo "kept=$(( $(wc -l <$A) - $(comm -23 $A $B | wc -l) )) of $(wc -l <$A | tr -d ' ')"`
- THEN it prints `kept=134 of 134` (both numbers equal; 134 distinct contents on `main` today)

### Requirement: instance-b-runs-on-moved-harness
This repository SHALL be its own instance: `bin/factory`, run from its root, MUST find `.factory/`, pass the lock and open every ticket in its store.

#### Scenario: instance-b-opens-every-ticket
- WHEN `S=$(bin/factory paths 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["state"])' 2>/dev/null); n=0; bad=0; for f in "$S"/tickets/T-*.yaml; do [ -f "$f" ] || continue; n=$((n+1)); bin/factory ticket show "$(basename "$f" .yaml)" >/dev/null 2>&1 || bad=$((bad+1)); done; echo "tickets=$n failed=$bad"`
- THEN it prints `tickets=N failed=0` with N ≥ 12

### Requirement: instance-b-gates-and-protects-harness
This instance's gate SHALL run the moved suite as well as the whitespace check, its protected paths SHALL include the harness code and the prompt copies, and its briefing SHALL describe the new layout.

#### Scenario: instance-b-config
- WHEN `uv run --frozen python -c "import yaml; c=yaml.safe_load(open('.factory/instance.yaml')); g=c['gate_commands']; p=[x for v in c['protected_paths'].values() for x in v]; print(any('pytest' in x and 'tests/factory' in x for x in g), 'git diff --check main...HEAD' in g, all(x in p for x in ('factory/**', 'bin/factory', 'agents/**', 'docs/prompts/**')))" 2>/dev/null || echo "no instance config"; echo "context=$(grep -c -e 'docs/design\.md' -e 'tests/factory' .factory/context.md 2>/dev/null)"`
- THEN it prints `True True True` then `context=N` with N ≥ 2

### Requirement: green-keeps-its-harness
This change MUST NOT remove green's in-tree harness, which keeps running until instance A's own ticket.

#### Scenario: green-harness-still-present
- WHEN `git -C ~/dev/nanobot-upstream cat-file -e feat/lionbot-v3:factory/cli.py && git -C ~/dev/nanobot-upstream cat-file -e feat/lionbot-v3:.claude/agents/factory-triage.md && echo "green keeps its harness"`
- THEN it prints `green keeps its harness`

### Requirement: no-whitespace-errors
The parent's combined change MUST add no whitespace errors.

#### Scenario: whitespace-clean
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `git diff --check "$BASE" HEAD; echo "exit=$?"`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Run every command with bash from the root of the `~/dev/spec-factory` checkout under test, which at parent close is `main`. `~/dev/nanobot-upstream` and `uv` must be on the machine. "Today" means `main` at `f082708`, with `BASE=$(git rev-parse main)`. Every today output below was observed on this checkout. The expected results for B and C are design targets; no code for them exists yet.

- harness-files-in-repo → NEW. Today it prints ten `missing …` lines (from `factory/cli.py` to `tests/factory/test_p0_cli.py`), then `agents=0 green_only=0`.
- harness-history-carried → NEW. Today it prints `24`, because none of green's harness commits are here. In the scratch import trial it printed `0`.
- harness-suite-passes-after-uv-sync → NEW. Today `uv sync` fails (`No pyproject.toml found`) and it prints `sync=2`, then `no tests ran in 0.00s`. Green's suite gave `70 passed` in a scratch copy.
- role-prompt-text-unchanged → NEW. Today it prints `changed=14 of 14`, because none of the files exist here. After the import trial it printed `changed=1 of 14`; the one is the preamble, which part B replaces.
- init-creates-instance-in-throwaway-target → NEW. Today it prints `init=127` (`bin/factory` does not exist), then `instance=[] agents=0 restart=0`.
- store-command-from-subdirectory-uses-target-instance → NEW. Today it prints `init=127`, then `new=127 tickets=[] harness_changes=0`.
- command-outside-any-instance-refused → NEW. Today it prints `exit=127 created=0 names_instance=0`.
- factory-instance-override-from-elsewhere → NEW. Today it prints `init=127`, then `found=0`.
- composed-input-opens-with-instance-context → NEW. Today it prints `init=127`, then `first=[]`.
- run-system-prompt-names-instance → NEW. Today it prints `init=127`, then `line1=[] placeholders= protects_instance=`.
- paths-name-harness-workflows-and-instance → NEW. Today it prints `init=127`, then `no paths`.
- lock-mismatch-refused → NEW. Today it prints `init=127`, then `exit=127 tickets=0 hint=0`.
- accept-current-revision-rewrites-lock → NEW. Today it prints `init=127`, then `exit=127 lock_is_rev=no logged=0`.
- accept-other-revision-refused → NEW. Today it prints `init=127`, then `exit=127 lock= tickets=0`.
- throwaway-store-ignores-lock → NEW. Today it prints `init=127`, then `exit=127 ticket=[]`.
- docs-moved-and-split → NEW. Today it prints seven `missing …` lines, then `old_tracked=15`. In the scratch split trial it printed `old_tracked=0`.
- changelog-moved-verbatim → NEW. Today it prints `DIFFERENT`, then `declined= numbering=NONE in_design=`. In the trial it printed `SAME`, then `declined=1 numbering=CONTIGUOUS in_design=0`.
- design-text-kept → NEW. Today it prints `570`, because `docs/design.md` does not exist. In the trial it printed `0`.
- prompt-copies-moved-unchanged → NEW. Today it prints `changed=10 of 10 DRIFT`. In the trial it printed `changed=0 of 10 VERBATIM`.
- no-old-paths-in-live-files → NEW. Today it prints `exit=0`: `README.md` lines 5, 6, 9 and 11 match.
- readme-has-install-and-layout → NEW. Today it prints seven `missing: …` lines, then `checked`.
- design-doc-instance-text → NEW. Today it prints `kept=0 open= piece8=0 logged=0`.
- build-spec-render-paths → NEW. Today it prints `stale=0 new= d8=0`, because the file is not at `dev/`. The `stale=0` there is vacuous: `awk` read no file.
- intake-holds-only-live-store → NEW. Today it prints `left=167`.
- pilot-store-and-answers-kept-byte-identical → NEW. Today it prints `kept=0 of 134`, because every one of those files is tracked only under `intake/`.
- instance-b-opens-every-ticket → NEW. Today it prints `tickets=0 failed=0`, because `bin/factory` does not exist here and no store is found. The same tickets open today through the old copy: `FACTORY_STATE=$PWD/intake/state intake/harness/bin/factory ticket show T-000N` succeeds for all twelve.
- instance-b-config → NEW. Today it prints `no instance config`, then `context=`.
- green-harness-still-present → REGRESSION. It prints `green keeps its harness` today and must still do so after the change.
- whitespace-clean → REGRESSION. It prints `exit=0` today (an empty range) and must still do so over the whole parent.

How verified:
- I ran every WHEN above verbatim on this checkout for the "today" results.
- The A and D results marked "trial" came from a scratch clone of this repo:
  - for A, with green's harness imported by `git filter-repo` from a scratch clone of green;
  - for D, with the document moves done by `git mv` plus an `awk` split of the Changelog.
- Green's suite was run in a scratch `git archive` copy with green's venv, three times: with green's config, with this repo's config, and with this repo's config plus `environment_files: ["uv.lock"]`.
- Nothing was written in `~/dev/nanobot-upstream`.
- I did not build B, C, E or F. Their scenarios are checked against today's failure only, and their expected results are the design above.

Out-of-scope observations:
- `main` moved twice during this run, to `b722abd` (#20 filed, "after #19") and then `f082708` (#13 and #14 "fold in" to #21, "after #19"). Neither touched the files this spec changes, except `issues/README.md` gaining rows. Part D moves that file as-is.
- `intake/requests/19_harness_home.md` (this request's file) is untracked. The post-close operator step has to move or delete it.
- The store's run records (`meta.yaml`, `input.md`) hold absolute `intake/state/...` paths. After the post-close move they stay as historical text and no command reads them back.
- `factory init` now has a third meaning in the build spec: part A's bare-repo seeding (`dev/build-harness.spec.md`, "factory init: creates ~/factory-remote/nanobot.git"). Part F does not reconcile it. A later build-spec pass should.
- Even after this change there are three prompt texts: `docs/design.md`, `docs/prompts/` (verbatim), and `factory/prompts/<role>.md` (placeholders filled, plus the spec-writer and triage addendum). With all three in one repo a `render --check` becomes possible, but it is not built here.
