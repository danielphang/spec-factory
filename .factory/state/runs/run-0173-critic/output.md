## Review of T-0020 spec v1 (live-file tripwire + coding rule 6), round 1

What I checked myself, on `main` at `9853737` (the checkout has moved since the spec's `1c5f6a7`: the T-0019.1 merge landed on top of it):

- Cited paths and lines. `factory/cli.py`: `ticket_set` at 109-121, `ticket_park` at 173-185 (writes the park record, logs `ticket.parked` and `escalation.queued`), `run_start` 197-228 with the `in_flight` append at 225, `run_finish` 281-320 with the remove at 306-307. `grep -n in_flight factory/*.py` shows no other writer (`subtickets.py` and `cli.py:438-442` only read). `factory/instance.py` `fill_preamble` is the only reader of `protected_paths`. `factory/store.py`: `Refused` (exit 2), `STORE_GITIGNORE` with two lines, `ensure_gitignore` checking exactly those two, `next_run_id` reserving by mkdir. `docs/coding.md`: `## 5.` at line 86, "rule 2, 3 or 5" at 67, closing "The check order" paragraph at 97. `docs/design.md` line 52 opens `**What the harness itself owns**`. `factory/instance.template.yaml`: `protected_paths` at 12-13, `parked:` row at 58 allowing nine exits. `intake.js` line 153 is the `ready-for-critic` transition; both `runRole` functions have the `if (!fin.ok)` line (intake 36, build 44 within the function) and every caller returns on `null` (intake 131, 145, 159; build 149, 192, 249). README: "Instances and the harness lock" bullet at 343, "returns it." at 322, status header date at line 9.
- Nanobot evidence. `~/dev/nanobot-upstream/.factory/state/runs/run-0080-implementer/output.md` lines 91-93 say what the spec quotes (overwrite of `policies.json` and `.bak`, the `FileExistsError`, the collection-time import as cause). `git log --all -i --grep=tripwire` there finds no factory commit; the one hit is a SPEC-22 docs commit about "regression tripwires", unrelated. Read only.
- Acceptance commands. I wrote both fixture scripts and ran every scenario except the full suite: park, escalate, dropped-by-`ticket set`, killed, substitute `HOME`, directory refusal, baseline, no-key, the coding awk, the docs grep, the changelog awk and the workflow awk. Each printed exactly the "today" output verification.md records (`state=ready-for-triage reason=None`, `items=None`, `exit=0 named=no runs=1`, `held=0`/`committed=0`, `design=0 template=0 built=0 resume=0`, `contiguous=yes last_names_tripwire=no`, `intake.js 0`/`build.js 0`, `heading` line absent and all six `=no`). So every NEW item fails today for the stated reason, and the REGRESSION items pass. The substitute-`HOME` scenario would also catch a `HOME`-based expansion, as its verification note says, since `~/.t0020-probe` under the real home does not exist on this machine.
- Tests to change: `test_instance.py` 89 and `test_shepherd.py` 200-201 are subset checks on `.gitignore`; `test_instance.py` 94-106 compares keys with the template, and a comment adds no key; the fixture instance has no `tripwire`. "none" is correct.

Rubric 4 and 5: the baseline-in-gitignored-file, pwd-based `~`, compare-once-on-leaving-in-flight and "during not by" choices are all written down under Decisions; the six harness files are declared under Risk; nothing here conflicts with T-0019 (which is the complementary prevention half) or the routing table. Rubric 6: the Problem's first paragraph says what is wrong (nothing notices a live-file write) and for whom (the operator), and glosses role, role run, harness and store before using them. Decisions and Operator steps read cleanly to a newcomer.

## Findings

[SHOULD-FIX] 1, 5 — Evidence first line and Risk "Ordering"
Problem: the spec is checked against `1c5f6a7`, but `main` is now `9853737` with T-0019.1 (the throwaway-`HOME` wrapper, changelog entry 48, and its template/README/design edits) already merged, so "build this after T-0019 merges" names a half-merged thing.
Evidence: `git log --oneline 1c5f6a7..HEAD` lists `5f43cba T-0019.1` and its merge `9853737`; `docs/changelog.md` line 52 is entry 48 "After issue #36"; `.factory/state/tickets/T-0019.2.yaml` is still `ready-for-implementer` and its plan says S2 also edits `docs/design.md` and `docs/changelog.md`. I re-ran every scenario on `9853737` and the "today" outputs are unchanged, so nothing else in the spec is stale.
Suggested fix: re-date the Evidence line to `9853737` and make the ordering note say T-0019.1 is merged and only T-0019.2 (plan field lines; edits the design doc and changelog) is still ahead of this one.

[SHOULD-FIX] 6 — Problem paragraph 2 "intake roles", Evidence bullet 1 "sub-ticket worktree", Operator step 1 "the Driver's lists"
Problem: three factory-specific terms appear in human-facing sections without a gloss; none is in a first paragraph, so this is not blocking.
Evidence: writing standard rule 2. "Intake" (the half of the chain that ends at the spec gate), "sub-ticket" (a part of a split change that gets its own worktree) and "Driver" (the operator session that runs the Nanobot instance) are not defined anywhere in the spec.
Suggested fix: one clause each at first use, e.g. "intake roles (the triage, spec writer and critic runs before a human approves)", "that run's worktree (the checkout the implementer edits)", and "the lists the Nanobot instance's operator asked for".

[NIT] 2 — design.md A1/A3 "expanded path"
Problem: the scenarios compare the as-written `$T20/...` path in the park reason, and on macOS `mktemp -d` returns `/var/folders/...`, a symlink to `/private/var/...`, so an implementer who normalises with `Path.resolve()` or `realpath` passes A1 as written yet fails every fixture scenario on a path string.
Evidence: `mktemp -d` here printed `/var/folders/1t/.../T/tmp.1OHwOIcmNc`; A1 only says "a leading `~/` becomes … plus `/`" and never says whether anything else is normalised.
Suggested fix: add one sentence to A1: "No other normalisation: no symlink resolution, no `..` collapsing; the path is kept as written after the `~/` replacement."

[NIT] 6 — Risk, "stops the workflow before the role's output is recorded"
Problem: `run finish` has already written `output.md` and `meta.yaml` by the time the tripwire parks; what is skipped is the routing step after it (for example `spec add`), so the sentence slightly misstates where the stop falls.
Evidence: `run_finish` writes `output.md` at line 288-289 and `meta.yaml` at 304 before any point where A5 would compare; part C stops the script after `run finish` returns.
Suggested fix: "stops the workflow after the run is recorded but before its result is acted on (for example, a spec is not added), so resuming re-runs that role."

Not findings, said for the record: the "Both scripts check run finish for a park" scenario ends in a reading step; it is declared structural and the awk count is the runnable part, which is the honest shape for code that needs the Workflow runtime. Part E (the coding rule) belongs here: the T-0019 approval commit message says the tripwire and the import-patching rule were split together into this ticket.

## Prior findings
none (round 1)

STATUS: APPROVE
CONFIDENCE: high — I ran every non-suite acceptance command and every cited line on the current `main`; the two SHOULD-FIX items are wording and a stale commit reference, and an implementer could start from this spec without a question.
ESCALATIONS: none
