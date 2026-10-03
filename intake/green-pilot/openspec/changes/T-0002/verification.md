## Acceptance
- killed-verifier-without-output-file-parks-as-budget-kill → NEW. Today it prints `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci`: recording the killed verifier exits 1 with `FileNotFoundError`, which `build.js:140` turns into a `harness-bug: results record verifier: …` park. Same output on a simulation of #16 merged.
- killed-reviewer-without-output-file-parks-as-budget-kill → NEW. Today it prints `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer`. Same on the #16 simulation.
- killed-record-without-output-flag-still-records-killed → REGRESSION. Today it prints `exit=0 rows=[verifier.yaml ] status=KILLED`. This is the call shape the test fixture uses, the second caller the fix must keep working.
- killed-output-naming-another-commit-records-killed → NEW. Today it prints `exit=2 rows=[] status=` (refused by the `Commit:` check, which runs on a killed run's output). Same on the #16 simulation, since #16 keeps the killed check.
- unkilled-record-with-missing-output-file-still-fails → REGRESSION. Today it prints `exit=1 rows=[] events=0`. This guards against the fix skipping the read for every run instead of only killed ones.
- factory-suite-passes-with-killed-checker-change → REGRESSION. Today `55 passed in 70.71s` on this checkout. When this ticket is built, the count also includes #16's new tests and this change's new test file.

How verified: I ran every WHEN above verbatim, under bash and zsh, on this checkout (HEAD `f8f40e0c5`) for the "today" results. All of them were run from the repo root of each copy. I also ran them in three scratch copies of `factory/`, `bin/` and `tests/factory/` outside this checkout:
- this checkout with design part A;
- a simulation of #16's change without part A;
- that simulation with part A.
On the #16 simulation without A, the results matched "today" above. With A, on either base, every THEN line held, and `tests/factory` plus a sketch of part B gave `57 passed`. Without A, the sketch failed in both roles with `FileNotFoundError`. The #16 simulation is my reading of #16's approved design part A and its part B fixture edit, not #16's actual implementation (not merged yet; its worktree `factory/T-0001.1` is still at `f8f40e0c5`).

Out-of-scope observations:
- `tests/factory/test_shepherd.py:642-645`: the shepherd's killed path records without `--output`, which is not how `build.js:139` calls `results record`. That divergence is why the suite never caught this bug. Making the fixture mirror `build.js` would be an edit to an existing test, so this spec adds a new test with the build loop's call shape instead.
- The working tree of this checkout shows `M webui/package-lock.json` (a protected dependency path). It was there before this run started and was not touched by it.

## Critic rounds

round 1 · spec v1 · run-0010-critic · APPROVE

Round 1 review of T-0002 v1 (killed checker parks as `harness-bug` instead of `budget kill`).

Spot-checks (this checkout, `feat/lionbot-v3` at `f8f40e0c5`; working tree carries only the pre-existing `M webui/package-lock.json`):
- Cited paths, all confirmed at the stated lines: `factory/workflows/build.js:91` (`const killed = out === null || ...`), `:93` (`run finish ... --status-override KILLED`), `:139` (`results record ... --output ${r.outputPath} --run ...${' --killed'}`), `:140` (`harness-bug: results record ${role}` park); `factory/cli.py:255` (`run finish` writes `output.md` only under `--output-file`), `:425` (`text = Path(a.output).read_text(...) if a.output else ""`), `:426` (`if a.killed:`), `:431-433` (`Commit:` check), `:436` (`if a.role == "verifier" and not a.killed`), `:467-470` (merge gate wants `ci PASS`, `APPROVE`, `VERIFIED`), `:524-525` (killed verifier excused from the `ci` row), `:532-533` (`budget kill:` park), `:929` (`except Exception` in `main`); `tests/factory/test_shepherd.py:642-645` (killed path records without `--output`), `:389` `built_to_implementer`, `:581` `ok`, `:713` `act_on_join`. `tests/factory/__init__.py` exists, so design B's `from .test_shepherd import built_to_implementer` is sound. `tests/factory/test_killed_checker.py` does not exist yet.
- Acceptance commands run verbatim from the repo root (zsh), four of five:
  - killed-verifier-without-output-file → `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci`; stderr of the killed record is `factory: FileNotFoundError: [Errno 2] No such file or directory: '.../runs/R2/output.md'`. Matches the spec's "today".
  - killed-record-without-output-flag → `exit=0 rows=[verifier.yaml ] status=KILLED`. Matches.
  - killed-output-naming-another-commit → `exit=2 rows=[] status=`. Matches.
  - unkilled-record-with-missing-output-file → `exit=1 rows=[] events=0`. Matches.
- The five scenarios together pin the fix: scenario 4 fails a fix that only tolerates a missing file, scenario 5 fails a fix that skips the read for every run, scenario 3 fails a fix that requires `--output`. The NEW items fail today for the reason stated.
- Consistency with #16 (`specs/T-0001/v1.md`): its requirement `killed-run-recording-is-unchanged` (no `--output`; `--output` with no `Commit:` line) still holds under this change; only #16's design-level sentence "keep today's check unchanged" for killed runs is superseded, and the Decisions section says so and why. The merge-gate argument (a KILLED row can never merge) is correct per `cli.py:467-470` and `:532-533`.

Findings:

[SHOULD-FIX] 6 proposal.md, Problem, first paragraph
Problem: The first paragraph is entirely glossary (factory, checkers, build loop, `results record`, park) and does not say what is wrong or for whom; that lands in paragraphs 2 and 3.
Evidence: Read as the gate operator. The defect ("the recording command crashes ... parks with `harness-bug: results record <role>` ... hides the real cause") and the victim ("the operator ... investigates the factory instead of re-dispatching") are stated plainly in the next two paragraphs with every term glossed, so no translation or inference is needed; this fails the rubric's first-paragraph letter but not its intent, and I am deliberately not blocking on it.
Suggested fix: Open the first paragraph with one sentence such as "When a checker agent's run is killed by a budget limit, the factory reports it to the operator as a factory bug instead of a budget kill", then keep the gloss.

[SHOULD-FIX] 1 verification.md, "How verified", last sentence (and Decisions "Sequencing", Risk "Merge-order risk")
Problem: The claim that #16's worktree `factory/T-0001.1` "is still at `f8f40e0c5`" is stale: it is at `e28db6a25` (`T-0001.1: results record refuses output whose Commit: lines do not all name the head`), and the store's `tickets/T-0001.1.yaml` is `status: checks-in-flight` with that head.
Evidence: `git worktree list` in this checkout; `git diff f8f40e0c5 e28db6a25 -- factory/cli.py` shows line 425 unchanged and the `Commit:` check split into `if a.killed:` (first-hex-line check) / `else:` (strict per-line check) at lines 431-444, which is exactly the shape the spec simulated. I ran the killed-verifier and killed-output-naming-another-commit WHEN lines from that worktree's root: `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci` and `exit=2 rows=[] status=`, the same "today" results the spec gives for its simulation. Nothing in design A changes; the implementer should just be pointed at the real base.
Suggested fix: Replace the simulation sentence with "#16's implementation exists at commit `e28db6a25` on branch `factory/T-0001.1` (checks in flight); the killed-only `Commit:` branch to remove is its `if a.killed:` block in `results_record`", and drop "my reading of #16's approved design".

[NIT] 6 design.md, part A, first sentence
Problem: "Today that is line 425: `text = ... if a.output and not a.killed else ""`" quotes the replacement line as if it were today's code (today's line has no `and not a.killed`).
Evidence: `factory/cli.py:425` reads `text = Path(a.output).read_text(encoding="utf-8") if a.output else ""`.
Suggested fix: Word it as "Today line 425 reads `... if a.output else ""`; change it to `... if a.output and not a.killed else ""`."

Not verified, not blocking: the request's GitHub reference `danielphang/spec-factory#18` (no network used in this review). Everything else in Evidence that is checkable on disk checked out.

No BLOCKING findings. The spec is grounded, each acceptance item is runnable and discriminating, the one design decision (a killed run's output is never read) is explicit and justified, no protected or guardrail path is touched, and an implementer could start from design A and B without a question. I would bet on it producing a correct PR.
