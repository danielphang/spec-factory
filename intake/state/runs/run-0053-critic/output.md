Round 2 review of T-0012 (harness home, issue #19), spec v2.

Scope of this round, per Convergence: (a) whether the four round-1 findings are resolved, (b) the text that changed between v1 and v2. I diffed the two versions mechanically (`diff` of the v1 and v2 blocks extracted from the input): the changes are confined to Problem paragraphs 1–2 (split and reworded), two new Evidence bullets (`repo_root` callers; `request_dir`), two new Decisions, the Risk "Lock behaviour after close" paragraph, design.md B.2, B.9 (conftest), E.1 (`request_dir` dropped), E.3 (lock rewrite rule), the verification "Round 2" line and the new Responses section. No acceptance scenario changed.

What I checked myself (from `~/dev/spec-factory`, `main` = `f082708` = HEAD; green read-only, HEAD `7c0a035` = G, `git log G..feat/lionbot-v3 -- factory/prompts .claude/agents` empty):

- New Evidence claim "`factory/compose.py` and five places in `factory/cli.py` call `gitops.repo_root`": `git grep` on green gives `cli.py:205,236,404,474,759` and `compose.py:49`. Exactly five plus one. Holds.
- New Evidence claim on `request_dir`: `git grep request_dir` over green's `factory/*.py` and `factory/workflows/*` exits 1 (no match); the key is at `intake/instance/config.yaml:6` with value `../../issues` (my round-1 "line 3" was wrong; the writer's correction is right). From `REPO_ROOT = intake/harness` that resolves to `issues/`, whose only tracked file (`issues/README.md`) part D moves to `dev/issues.md`. Holds.
- B.9's conftest reasoning: `FACTORY_REPO` appears in the imported tests only at `test_shepherd.py:627`, written into a per-subprocess env dict; every other test relies on `gitops.repo_root`'s default (`gitops.py:18-22`). The tests build their env at call time (`test_p0_cli.py:21`, `env = {**os.environ, "FACTORY_STATE": …}` inside `run()`), and `test_killed_checker.py` drives the CLI through `built_to_implementer` imported from `test_shepherd`, so an import-time `conftest.py` is seen by all six test modules. Green has no `tests/factory/conftest.py`, and `tests/factory/fixtures/` holds only `stubs/`, so the new `fixtures/instance/` collides with nothing. Holds.
- Acceptance commands re-run verbatim today: intake-holds-only-live-store → `left=167`; harness-history-carried → `24`; no-old-paths-in-live-files → matches on `README.md` lines 5, 6, 9, 11, `exit=0`. All match the spec's "today" outputs.

Prior findings (round 1):

- [BLOCKING] 6 proposal.md, Problem, first paragraph → RESOLVED. The new second paragraph states the defect ("the harness can serve only the repository it lives in") and both victims (the operator keeping a drifting hand copy; every new adopting project) in two sentences, with no inference and no ungloss'd term. Read as the gate operator, I can say what is wrong and for whom after six sentences. See the NIT below on where those sentences sit.
- [SHOULD-FIX] 6 design.md B.2, repo root under `FACTORY_INSTANCE` → RESOLVED. B.2 now defines the repo root as the parent of the instance directory, whatever its name, with `FACTORY_REPO` overriding. The writer also traced the consequence I had not: with the fixture at `tests/factory/fixtures/instance/` that rule would make the imported tests' repo root `tests/factory/fixtures/`, so B.9's conftest now sets `FACTORY_REPO` to the harness checkout when unset. I verified that this reproduces today's default for every imported test and that the shepherd tests' per-subprocess override still wins. The Decisions entry matches.
- [NIT] 4 design.md E.1, `request_dir` carried → RESOLVED. E.1 drops the key with the reason; Decisions and Evidence record it; the line number is corrected.
- [NIT] 2 specs/self-instance/spec.md, lock at parent close → RESOLVED. E.3 now requires any sub-ticket touching harness paths that merges after E branches to rewrite `.factory/harness.lock`, and Risk repeats it for the planner.

Findings on changed text:

[NIT] 6 proposal.md, Problem, paragraphs 1–2
Problem: The rubric's letter asks that the *first* paragraph say what is wrong and for whom; v2 puts that in a two-sentence second paragraph directly after a first paragraph that still only describes the system.
Evidence: Paragraph 1 ends "It finds three things by looking next to its own code: …"; paragraph 2 opens "So the harness can serve only the repository it lives in." The operator needs no translator and no inference, only one more paragraph break. This technically fails rubric 6 in a way that does not matter for the gate reader, so I do not block on it.
Suggested fix: Join paragraph 2 onto the end of paragraph 1 (the "So …" sentence already reads as its conclusion), leaving "Concretely, …" as the new paragraph 2.

No other findings. The new Evidence bullets, Decisions and Risk text are accurate against green and this checkout; the B.9 conftest rule is the correct fix and is stated precisely enough to implement without a question; E.1 and E.3 are now consistent with B.5's template and the lock design in C.

Out-of-scope observations:
- Unchanged from round 1: `intake/requests/19_harness_home.md` and the T-0012 store files are untracked; the design doc's piece-8 and role-context lines are each one physical line, which design-text-kept's two `grep -v` exclusions rely on.
- The writer's own out-of-scope note that `factory init` now carries a third meaning in the build spec (part A bare-repo seeding) is correct and is rightly left to a later build-spec pass; it does not affect this ticket's acceptance.

STATUS: APPROVE
CONFIDENCE: high — the v1→v2 diff is confined to the four findings plus their supporting evidence; every new factual claim (six `repo_root` callers, `request_dir` unread and at line 6, shepherd-only `FACTORY_REPO`, call-time env construction, no fixture collision) checked true on green and on this checkout; three acceptance commands re-run match the spec's today outputs; the one remaining nit is a paragraph break.
ESCALATIONS: none
