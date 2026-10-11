=== proposal.md
## Problem

The harness wrongly stops part of a planned change because an earlier part of the same change has merged. Twice in the last multi-part build, the operator had to step in by hand to restart work the plan expected to go ahead. The second time, no command could restart it, so the operator edited the ticket's record by hand.

Some background. A large approved request (a parent ticket) is split by a planner into parts (sub-tickets). Each part is built, checked and merged on its own into the integration branch, which is the target repository's main line. One part may depend on an earlier one and build on what it added. The parts of one parent are siblings. Before the first coding run of a part (its implementer run), the harness runs a spec drift check. That check looks for changes on the integration branch, made since the parent's spec was approved, that the spec did not plan for. One of its rules flags a test file that changed in the same commit as a file the spec's design names, because such a test may pin behaviour the spec is about to change. When the check finds drift, the harness parks the part, which means it stops and waits in the operator's queue. The operator then amends the spec or writes a ruling (`factory resolve <part> --ruling F`, a note that returns the part to its implementer and also stops the check from repeating).

Two problems, both for the operator:

1. **A sibling's merge counts as drift.** The test rule looks at every commit on the integration branch since the spec was approved, including the merges of the parent's own earlier parts. When part A adds a test and changes a file the design names, part B is parked as soon as A merges, although the plan said A would add that test. Today the operator must rule on every such false park. The fix keeps flagging commits that come from anywhere else.
2. **One kind of park has no way back.** When the harness fails to start an implementer run for any reason other than a refusal it reports as blocked, the build parks the part as a harness bug (`harness-bug: run start implementer: …`). No `resolve` option accepts that park, so even after the cause is understood, the part cannot be returned to its implementer. In the second case below, the Workflow script recorded a spec drift refusal in that harness-bug form, and the operator had to edit the stored park reason by hand before `--ruling` would accept it. The newer driver records drift refusals as plain blocked parks. It still parks every other start failure, such as a failed environment sync, as a harness bug.

## Evidence

- **First false park.** The parent T-0040 (issue #65, the driver) was planned in three parts. Part A, T-0040.1, merged as `2ad4d8c52`. `git show --stat 2ad4d8c52` prints the subject "Merge factory/T-0040.1: The driver core and the intake phase (T-0040.1)" and shows that it changed `factory/cli.py`, a file the design names, and added `tests/factory/test_drive.py` (303 lines). The store's log then records part B, T-0040.2, parked from `ready-for-implementer` (`ticket.parked`, 2026-10-10T06:37:15) with the reason `BLOCKED from harness: spec drift: tests/factory/test_drive.py changed by 2ad4d8c52 since spec v4 was written at 37848dbb0`. That commit is the merge of B's own sibling, and `.factory/store/tickets/T-0040.1.yaml:53-55` records it as `merge.main_after: 2ad4d8c5288474b823d4571ba03de82a706eabdf`.
- **Second false park, and no route back.** `.factory/store/tickets/T-0040.3.yaml:26-33` records part C parked with `harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/factory/test_drive.py changed by 2ad4d8c52 …; tests/factory/test_drive_build.py changed by 18fbe88ba …`. Both blamed commits are sibling merges: `18fbe88ba` is "Merge factory/T-0040.2: The build phase (T-0040.2)", which added `tests/factory/test_drive_build.py`, and `T-0040.2.yaml:60-62` records it as that part's `merge.main_after`. The log holds a `park.corrected` event by the operator at 2026-10-10T17:18:37 whose `previous` field is that harness-bug reason. The ruling that followed in the same second (history entry `resolve: ruling`) is the workaround.
- **Cause in code.** `factory/cli.py:316-347` (`_test_drift`) walks `git rev-list --first-parent --reverse <recorded head>..<tip>` and flags each test file changed by a commit that also changed a design-named file. It never reads the parent's merged sub-tickets. The sibling-tests check beside it, `_check_sibling_tests` (`factory/cli.py:245-269`), already reads each merged sibling's `merge.main_after` and `merge.base_before`.
- **No resolve route.** `factory/cli.py:1183-1185`: `--ruling` refuses unless the park reason starts with `ESCALATE` or `BLOCKED`. `factory/cli.py:1223-1225`: `--redispatch` refuses unless the park came from `checks-in-flight` or `ready-for-merge`. `factory/drive.py:179-186` and `factory/workflows/build.js:79-84` park every run-start refusal that does not start `BLOCKED ` as `harness-bug: run start <role>: <stderr>`, from `ready-for-implementer` for the implementer.
- **Reproduced on this checkout (`f3a85bc`)** with the acceptance scenarios below, run through the running-code wrapper:
  - "A merged sibling's merge is not drift…" printed `none: drift=1 greet=1 named=0 runs=0`. That is: part B, after only its sibling's merge, is refused for spec drift naming the sibling's test, and no implementer run starts. In the `other` line, the refusal names both the sibling's test and the other commit's test (`greet=1`).
  - "A ruling returns a sub-ticket whose implementer run failed to start…" printed `ruling=2 parked kept=no drift=1`, then `start=2 runs=0`. That is: `--ruling` refuses the harness-bug park, writes no ruling, and the part stays parked.
- **Proposed fix prototyped** in a throwaway clone (scratch, not committed): skipping a merged sub-ticket's `main_after` in `_test_drift`, and accepting the harness-bug park in `--ruling`. With it, the two scenarios above print their expected output. The three existing drift scenarios of build-dispatch print their current-truth output unchanged, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` prints `520 passed`. That prototype kept the old refusal text; Decision 4 changes it, which is why one test is listed under Tests to change.
- Capabilities read: `openspec/specs/build-dispatch/spec.md`, `openspec/specs/human-resolution/spec.md`, `openspec/specs/harness-docs/spec.md`, and `openspec/specs/spec-amendment/spec.md` for the `t0027-amend.sh` fixture.
- The request cites no Nanobot-side harness fix, and none was checked.

## Root cause

- `factory/cli.py` `_test_drift`: the first-parent walk does not exclude the recorded merge commits (`merge.main_after`) of the parent's merged sub-tickets. A sibling's merge is a first-parent commit whose diff against its first parent holds everything the sibling changed, so any sibling that adds a test and touches a design-named file trips the rule for every later sibling.
- `factory/cli.py` `resolve`, `--ruling` branch: accepts only `ESCALATE…` and `BLOCKED…` reasons. A `harness-bug: run start implementer:` park from `ready-for-implementer` matches no mode, so it can only be cleared by editing the ticket file.

## Out of scope

- The other drift rule (an Acceptance field naming an unmerged sibling), the named-file and test-file patterns, and the "no implementer run and no ruling on file" condition are unchanged.
- `_check_sibling_tests` (the sibling-tests check) is unchanged.
- The Workflow scripts' clerk re-encoding a JSON refusal as a harness-bug reason is not fixed here. The driver does not do it, and issue #89 retires the scripts.
- `--redispatch`, `--accept-paths` and every other `resolve` route keep their current rules. Harness-bug parks other than an implementer's failed run start (for example `harness-bug: run compose implementer:`, or any checker's) stay refused by `--ruling`.
- No change to `factory/drive.py`, `factory/workflows/*.js`, any role prompt, `docs/prompts/` or `factory/prompts/`.

## Open questions

none

## Decisions

- 1 (which commits are not drift): the test rule skips a first-parent commit that is the recorded merge (`merge.main_after`) of any merged sub-ticket of the same parent, from the current plan or an earlier one. Rejected: only the current plan's siblings. An earlier plan's merged sub-ticket is also this parent's own work, and the sibling-tests check already counts it the same way.
- 2 (later commits still count): only the sibling's merge commit is skipped. A later commit from anywhere else that changes the same test file beside a design-named file is still drift, and the refusal names that commit.
- 3 (the resolve route): `resolve <id> --ruling F` also accepts a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer`. It writes F as the next ruling and returns the sub-ticket to `ready-for-implementer` at the same round, as a ruling on a `BLOCKED` park does. As with any ruling on file, the drift check does not run again for that sub-ticket. Rejected: widening `--redispatch` to this park. `--redispatch` re-runs the checkers today, and with no ruling on file a drift refusal would park the sub-ticket again. Rejected: accepting every harness-bug park from `ready-for-implementer`. A failed `run compose` leaves its run in flight, so the next run start would be refused again.
- 4 (refusal text): `--ruling` on any other park is refused with `--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an implementer's run start; <id> is <state> (<reason or 'no park'>)`, so the operator sees the new case.

## Risk

Blast radius: the drift check at an implementer's run start and one `resolve --ruling` branch. If the sibling skip were too broad, a real drift commit could go unflagged. The skip matches exact recorded merge commits of the same parent only, and the `other` and `greet` cases of the new build-dispatch scenario pin that other commits still park. The ruling widening touches one prefix from one state. Every other park keeps today's refusal, which the second human-resolution scenario pins.
Protected paths: `factory/cli.py`

## Operator steps

1. After merge, move the runtime checkout to the new harness revision and accept it on each instance (`--accept-harness`). Until then the running factory still parks on sibling merges.

=== design.md
## Proposed change

**A. The test rule skips merged siblings' merges** (`factory/cli.py`, `_test_drift`). Before the first-parent walk, collect the `merge.main_after` of every sub-ticket of the parent (`store.subtickets_of(root, parent["id"])`) whose status is `merged` and whose `main_after` is set. In the walk, `continue` past any commit in that set before diffing it. Nothing else in the rule changes: a later commit that changes the same test file is still found, and the refusal still names the last such commit. Update the function's docstring and `_check_drift`'s docstring to say a merged sibling's merge is not drift.

**B. A ruling returns an implementer whose run failed to start** (`factory/cli.py`, `resolve`, the `--ruling` branch). Let `start_bug` be true when the park reason starts with `harness-bug: run start implementer:` and `parked["from"]` is `ready-for-implementer`. Accept the park when it starts with `ESCALATE` or `BLOCKED`, or when `start_bug` is true. Route `start_bug` exactly as `BLOCKED`: write F as the next `approvals/<id>/ruling-<n>.md` and `move("ready-for-implementer", "ruling", …)`, round unchanged. Change the refusal text to Decision 4's. The `use --answer` refusal for question parks stays as it is.

**C. Suite cases** in a new file, `tests/factory/test_drift_siblings.py`, built like `tests/factory/test_spec_drift.py`'s fixtures:
- A two-part plan where part A's recorded `--no-ff` merge adds a test file and changes a design-named file: part B's implementer run starts.
- The same, plus a later direct commit on the integration branch that changes a test beside a design-named file: refused, naming only that commit's test. A later direct commit that changes A's test file again: refused, naming the later commit.
- A merged sub-ticket of an earlier, superseded plan whose merge adds a test beside a design-named file is not drift.
- `--ruling` on a `harness-bug: run start implementer:` park from `ready-for-implementer` returns the sub-ticket to `ready-for-implementer` with the ruling file written. `--ruling` stays refused, writing nothing, on `harness-bug: run start reviewer:` from `checks-in-flight` and on `harness-bug: run compose implementer:`.

**D. Documents.**
- `docs/design.md`, the **Spec drift** paragraph: add that a first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans, is not counted, because the plan expects its siblings' changes.
- `docs/design.md`, the routing rules' resolution list (the bullet beginning "BLOCKED, a critic ESCALATE, and a planner ESCALATE"): add that a sub-ticket parked `harness-bug: run start implementer:` from `ready-for-implementer` returns to its implementer with the ruling, same round.
- `dev/build-harness.spec.md`: in the `factory resolve` CLI entry, add the same `--ruling` case. In the spec-store paragraph's drift sentence, add that a merged sibling's merge is not drift.
- `README.md`: in "Where a human decides", the **Unstick** row's `--ruling F` list gains "the harness failed to start an implementer run (a `harness-bug: run start implementer:` park)". In the **Spec amendment and drift** bullet under Built, add a sentence saying that a merge of another sub-ticket of the same spec is not drift. Replace that bullet's "It is tested, and has not yet fired on a real ticket", which is now false: the check has fired on real sub-tickets. Bump the status date.
- `docs/changelog.md`: one new entry, the last numbered, contiguous, "After issue #85 (2026-10-10), …", naming the two false parks, the `main_after` skip and the `harness-bug: run start implementer:` ruling route.
- No `docs/prompts/` or `factory/prompts/` file changes: no prompt block is edited.

## Tests to change

- `tests/factory/test_resolve_rulings.py::test_a_ruling_on_any_other_state_is_refused_and_names_both_park_kinds`: it asserts the old refusal text, `--ruling applies to an ESCALATE or BLOCKED park; T-0001 is …`. Decision 4 changes that text, so the assertion changes to the new text. The cases it parametrizes (a `budget kill: reviewer` park and no park) stay refused, and the test's other assertions stay.

=== specs/build-dispatch/spec.md
## MODIFIED Requirements

### Requirement: A sub-ticket whose spec drifted parks before its first implementer run
`factory run start --role implementer` on a sub-ticket with no implementer run and no ruling on file MUST refuse with exit 2, writing no run, with an error that starts `BLOCKED from harness: spec drift: `, when its Acceptance field names a sibling of the current plan that has not merged and is not among its dependencies, or when a test file changed on the integration branch since the parent's approved version was written, in a first-parent commit that changed a file that version's design names and that is not the recorded merge of a merged sub-ticket of the same parent, and no Tests to change list names it; the build SHALL park it with that error, and a ruling SHALL let the next run start.

#### Scenario: A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\nAcceptance:\n- REGRESSION: ST-1 scenarios still pass\n' && J=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1); echo "unmerged: blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: spec drift: ') names=$(echo "$J" | grep -c 'T-0001.1') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"; bin/factory ticket set T-0001.1 status=merged >/dev/null; bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "merged: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `unmerged: blocked=1 names=1 runs=0 ready-for-implementer`, then `merged: exit=0 runs=1`

#### Scenario: A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start
Needs the GIVEN blocks of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" and of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" (current truth, build-dispatch) run once. In `t0022-build.mjs` every role run returns an empty string.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && land src/other.py tests/test_other.py && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(spec drift:\).*/\1/'; R=$(bin/factory ticket show T-0001.1 --json | tail -1); echo "greet=$(echo "$R" | grep -c 'tests/test_greet.py') other=$(echo "$R" | grep -c 'tests/test_other.py') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"; printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "ruled: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `park T-0001.1: BLOCKED from harness: spec drift:`, then `greet=1 other=0 runs=0`, then `ruled: exit=0 runs=1`

#### Scenario: A merged sibling's merge is not drift, and a later commit from elsewhere still is
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell. Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" (current truth, spec-amendment) run once. In each case, part ST-1's branch adds `tests/test_greet.py` and changes `src/greet.py`, which the spec's design names, and is merged with `--no-ff` and recorded as T-0001.1's merge; T-0001.2 depends on it. Case `none` adds nothing more; `other` then commits `src/greet.py` with `tests/test_other.py` directly on main; `greet` then commits `src/greet.py` with `tests/test_greet.py` directly on main.
- WHEN `(for c in none other greet; do (. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' && A=$(git -C $T27/t rev-parse HEAD) && git -C $T27/t checkout -qb st1 && land src/greet.py tests/test_greet.py && git -C $T27/t checkout -q main && git -C $T27/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' st1 && bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$(git -C $T27/t rev-parse HEAD)'" >/dev/null && bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null && { [ $c = none ] || land src/greet.py tests/test_$c.py; } && J=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1); echo "$c: drift=$(echo "$J" | grep -c '"error": "BLOCKED from harness: spec drift: ') greet=$(echo "$J" | grep -c 'tests/test_greet.py changed') named=$(echo "$J" | grep -c "tests/test_$c.py changed by $(git -C $T27/t rev-parse --short=9 HEAD)") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"); done)`
- THEN it prints exactly `none: drift=0 greet=0 named=0 runs=1`, then `other: drift=1 greet=0 named=1 runs=0`, then `greet: drift=1 greet=1 named=1 runs=0`

=== specs/human-resolution/spec.md
## ADDED Requirements

### Requirement: A ruling returns a sub-ticket whose implementer run failed to start
`factory resolve <id> --ruling F` on a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer` MUST write F as the ticket's next ruling and return it to `ready-for-implementer` at the same round; on a harness-bug park of any other kind it MUST still refuse with exit 2, writing nothing.

#### Scenario: A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" (current truth, spec-amendment) run once. The park reason is the spec drift refusal wrapped as the Workflow script's clerk wrapped it for the sub-ticket that showed this problem.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && E=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p') && bin/factory ticket park T-0001.1 --reason "harness-bug: run start implementer: $E" >/dev/null && printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') kept=$(cmp -s $T27/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo yes || echo no) drift=$(echo "$E" | grep -c '^BLOCKED from harness: spec drift: ')"; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "start=$? runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)")`
- THEN it prints exactly `ruling=0 ready-for-implementer kept=yes drift=1`, then `start=0 runs=1`

#### Scenario: A ruling on a checker's or a compose step's harness-bug park is still refused
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(for r in 'harness-bug: run start reviewer: x' 'harness-bug: run compose implementer: x'; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && { case "$r" in *reviewer*) bin/factory ticket set T-0001.1 status=checks-in-flight >/dev/null;; esac; } && bin/factory ticket park T-0001.1 --reason "$r" >/dev/null && printf 'Ruling: x\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>$T23/err; echo "exit=$? refused=$(grep -c -- '--ruling applies to' $T23/err) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)"); done)`
- THEN it prints two lines, each exactly `exit=2 refused=1 parked rulings=0`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the sibling-merge exception and the start-failure ruling
`docs/design.md`'s Spec drift paragraph SHALL name `main_after` as not drift and its routing rules SHALL name the `harness-bug: run start implementer` ruling; `dev/build-harness.spec.md` SHALL name that ruling; README's Unstick row SHALL name it, and its "Spec amendment and drift" bullet SHALL say a sibling's merge is not drift and SHALL no longer say the check has not yet fired; `docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; no prompt copy SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The design doc, build spec, README and changelog record both changes, and no prompt copy changes
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; B=$(sed -n '/^- \*\*Spec amendment and drift\.\*\*/,/^- \*\*Re-plan after a re-spec\.\*\*/p' README.md); echo "design-drift=$(y $(grep '^\*\*Spec drift\.\*\*' docs/design.md | grep -c main_after)) design-ruling=$(y $(grep -c 'harness-bug: run start implementer' docs/design.md)) buildspec=$(y $(grep -c 'harness-bug: run start implementer' dev/build-harness.spec.md)) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c 'harness-bug: run start implementer')) bullet-sibling=$(y $(echo "$B" | grep -c 'not drift')) bullet-stale=$(y $(echo "$B" | grep -c 'has not yet fired')) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#85' -e main_after -e 'harness-bug: run start implementer' | sort -u | grep -c .)`
- THEN it prints exactly `design-drift=yes design-ruling=yes buildspec=yes unstick=yes bullet-sibling=yes bullet-stale=no prompts=0`, then `CONTIGUOUS`, then `3`

#### Scenario: The sibling-merge change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

- A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges → REGRESSION
- A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start → REGRESSION
- A merged sibling's merge is not drift, and a later commit from elsewhere still is → NEW. Today it prints `none: drift=1 greet=1 named=0 runs=0`, then `other: drift=1 greet=1 named=1 runs=0`, then `greet: drift=1 greet=1 named=1 runs=0`. Part B is refused for its sibling's test, and the `other` refusal names the sibling's test too.
- A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts → NEW. Today it prints `ruling=2 parked kept=no drift=1`, then `start=2 runs=0`: `--ruling` refuses the park, and the sub-ticket stays parked.
- A ruling on a checker's or a compose step's harness-bug park is still refused → REGRESSION
- The design doc, build spec, README and changelog record both changes, and no prompt copy changes → NEW. Today it prints `design-drift=no design-ruling=no buildspec=no unstick=no bullet-sibling=no bullet-stale=yes prompts=0`, then `CONTIGUOUS`, then `0`.
- The sibling-merge change adds no whitespace errors → REGRESSION

STATUS: READY-FOR-CRITIC
CONFIDENCE: high. Both failures reproduce on this checkout, and a prototype of the fix passes the new scenarios, the three existing drift scenarios and the full suite (520 passed).
ESCALATIONS: none
