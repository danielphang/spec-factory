Commit: 3fdcda3e76e891e79e7949c78b78cef051f1dfd2 (branch `factory/T-0057.1`, base 11080b100b31c70c69cc1867960819270d134a23, which is also `main`)

How I ran it. The head is the given worktree `wt/`, clean at `3fdcda3`. For the base, I cloned the repo into `scratch/base`, checked out `11080b1` detached, and pointed its local `main` there, so `git merge-base HEAD main` resolves to the base. I ran `uv sync --frozen` in both. I copied the spec's GIVEN block from `specs/T-0057/v2.md` byte for byte into `scratch/given.sh` and sourced it once, with `TMPDIR=scratch/tmp`. I extracted each WHEN from v2.md with sed into `scratch/w1.sh` … `scratch/w9.sh`, unedited. Every command ran inside the HOME wrapper from the briefing. Outputs are in `scratch/head-1-8.out`, `scratch/base-new.out`, `scratch/head-w9.out`, `scratch/base-w9.out` and `scratch/gate2.out`.

Per criterion:
1. NEW | spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one (`w1`)
   - Base: `wrapped exit=0 versions=1 added=1 err=` / `worded exit=0 versions=2 added=2 err=` / `good exit=0 versions=3 added=3 err=`. This is the failure verification.md predicts.
   - PR: `wrapped exit=2 versions=0 added=0 err=spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md` / `worded exit=2 versions=0 added=0 err=spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md` / `good exit=0 versions=1 added=1 err=`. This is the THEN exactly.
   - PASS
2. REGRESSION | approve-spec still refuses a malformed spec (`w2`)
   - Base: not run.
   - PR: `exit=2 spec not pinned: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`
   - PASS
3. REGRESSION | A store without current truth stores a malformed spec as before (`w3`)
   - Base: not run.
   - PR: `exit=0 versions=1`
   - PASS
4. REGRESSION | A spec writer's NEEDS-HUMAN draft is stored even when malformed (`w4`)
   - Base: not run.
   - PR: `exit=0 versions=1`
   - PASS
5. NEW | A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script (`w5`)
   - Base: `awaiting-spec-gate spec=1 versions=1 writer=1 critic=1 reason=`, twice. This is as predicted.
   - PR: `awaiting-spec-gate spec=2 versions=1 writer=2 critic=1 reason=`, twice.
   - PASS
6. NEW | A refusal in the last round parks with the refusal, quoted safely, in the driver and the script (`w6`)
   - Base: `parked spec=1 versions=1 writer=1 critic=1 reason=harness-bug: unknown STATUS UNKNOWN from critic`, twice, then `parked spec=2 versions=2 writer=2 critic=2 reason=max rounds`, twice. This is as predicted.
   - PR: `parked spec=2 versions=0 writer=2 critic=0 reason=max rounds: spec not added: scenario 'the 'echo hi' thing works' has no NEW/REGRESSION label in verification.md`, twice, then `parked spec=2 versions=1 writer=2 critic=1 reason=max rounds: spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`, twice.
   - PASS
7. NEW | The spec writer's next run receives the refusal and its refused output (`w7`)
   - Base: `first=0 heading= message= output= source=`. This is as predicted.
   - PR: `first=0 heading=1 message=1 output=1 source=1`
   - PASS
8. NEW | README, the design doc and the changelog describe the refusal route (`w8`)
   - Base: `formed=no truth=no round=no edge=no row=no design=no growth=` / `CONTIGUOUS` / `entries=0 terms=0`. This is as predicted.
   - PR: `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok` / `CONTIGUOUS` / `entries=1 terms=3`
   - PASS
9. NEW | The suite passes, only the two listed test files change, and every added test file fails on the base (`w9`)
   - Base: `647 passed in 127.29s (0:02:07)` / `changed= added=0`, and no per-file lines. Since n=0, the THEN fails, as predicted.
   - PR: `652 passed in 107.19s (0:01:47)` / `changed=tests/factory/test_shepherd.py,tests/factory/test_spec_store.py added=1` / `tests/factory/test_spec_add_refusal.py on the base: 5 failed`
   - PASS

Every NEW criterion fails on the base for the reason verification.md gives, and passes on the PR. No SPEC-DEFECT.

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `652 passed in 110.24s (0:01:50)`, exit 0.

The human ruling (2026-10-25) set two conditions, and both hold:
- T-0056's `tests/factory/test_transcript_record.py` and `tests/factory/test_scorecard.py` are not in the diff. `git diff --stat 11080b1 HEAD` lists only the two allowed existing test files and one added file. Both T-0056 files pass within the 652, and alone they give `20 passed`. I ran that last command with a fresh `HOME=$(mktemp -d)`, not the full wrapper.
- Every `run finish` call keeps `--transcripts`. There are 4 such calls in `factory/drive.py` (lines 235, 242, 600; the same 4 as on the base) and 3 in `factory/workflows/intake.js` (lines 128, 133; the same 3 as on the base). The other matching lines are comments or park strings.

Probes (on the head, store with an `openspec/` tree):
- **A delta that does not apply** (`MODIFIED 'No such req'`). This is a different kind of failure from the tested label errors. `spec add` exits 2 with `spec not added: MODIFIED 'No such req' is not in current truth (thing)` and stores no version. `approve-spec --edit` of the same file prints the identical text after `spec not pinned: `. → OK. The check is the general one, not a label special case.
- **An empty spec file.** `spec add` exits 2 with ``spec not added: no `=== <path>` part lines`` and stores no version. `approve-spec --edit` gives the same text. → OK.
- **A spec with no `proposal.md` and a wrapped label whose scenario name contains `$HOME` and `\`.** `spec add` exits 2, stores nothing, and reports only the label error. `approve-spec --edit` reports exactly the same, so the two are at parity. The missing `proposal.md` is not flagged by either command; that is the check's existing behaviour on the base, outside this ticket. → OK.
- **A last-round refusal whose scenario name holds `$HOME`, `\` and a backtick-quoted `` `id` ``, through both runners** (an untested fixture, run with the spec's own `t0057-intake.sh`). Both lines read `parked spec=2 versions=0 writer=2 critic=0 reason=max rounds: spec not added: scenario 'a 'HOME '' 'id' b' has no NEW/REGRESSION label in verification.md`. The driver and the script record the same reason. No `$`, `\` or backtick survives, and nothing was expanded. → OK.

I also read the code diff (`scratch/code.diff`). The refusal route keys on the `spec not added: ` prefix and on `max(round, 1)` against the instance's `max_spec`, and no fixture text appears in the harness code. `cli.py` is 899 lines, under the 900 cap. The implementer disclosed that it has no headroom left.

Protected paths: the change touches `factory/cli.py`, `factory/compose.py`, `factory/drive.py` and `factory/workflows/intake.js`. The parent spec's Risk section declares all four. It touches no other protected path.

STATUS: VERIFIED
CONFIDENCE: high. All nine acceptance commands ran as written: each NEW one fails on the base as predicted and passes on the head, both gates pass, and the probes show the check and the route are general.
ESCALATIONS: none
