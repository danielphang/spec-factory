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
