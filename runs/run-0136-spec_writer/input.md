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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0136-spec_writer/output.md`

## Ticket (Triage output)

Type: feature (harness speed; no change to any verdict)

Title: Build speed: run each check and the test suite only where its result can change the verdict

Summary:
Each sub-ticket build runs the full test suite four or five times, and most of those runs cannot change the outcome. A sub-ticket is one piece of a parent ticket that one implementer agent builds; a verifier agent then checks it, and when all pieces are merged a final "parent-close" verifier run checks the parent. The requester wants three kinds of redundant run removed. First, before-edit runs of checks that are already known to pass. Second, a repeat verifier run at parent close when that run checks the same code as the sub-ticket's verifier. Third, suite runs on a diff the suite cannot see. Every refusal the gate gives today must still happen: a failing NEW check, a failing regression, and a failing suite on a code change. This matters most for the Nanobot v3.5 port, which has about 7,600 tests and 32 tickets ahead, and the operator wants it in place before the port's builds start.

Terms used below. A NEW check is an acceptance check that must fail before the change and pass after it. A REGRESSION check must pass both before and after. Gate commands are the instance's configured check commands (here, `git diff --check main...HEAD` and the harness suite, `.factory/instance.yaml:22-24`). The `ci` row is where the verifier's gate result is recorded in place of a CI service.

Evidence:
- From the request, T-0015 (the coding-standard ticket): the implementer took 431 s. About 103 s of that ran the suite and the acceptance checks before editing, and about 85 s ran them again after. The store records `wall_s: 451` for that run (`.factory/state/runs/run-0131-implementer/meta.yaml`). The 103 s / 85 s split is not in its output, so I could not confirm it. One suite run takes about the stated time: the T-0015.1 verifier recorded `126 passed in 108.52s` on base and `131 passed in 112.14s` on head (`run-0132-verifier/output.md:16`).
- From the request, T-0013 (the writing-standard ticket): the parent-close verifier re-ran the same scenarios and the same suite on an unchanged `main`, taking 5.5 min, 20% of the build. Confirmed: `run-0112-verifier` `wall_s: 330`. The build runs 0108–0112 total 1,754 s, so 330 s is 19%, or 20% if the planner run is left out.
- The suite runs at least three times inside one verifier run today. Specs carry a REGRESSION scenario `gates-pass` that runs the suite, and the verifier runs it on base and on head (`run-0132-verifier/output.md:16`, `run-0112-verifier/output.md:17`). Step 4 then runs the gate suite on head again (`factory/prompts/verifier.md`, steps 3–4).
- Where today's behaviour lives: implementer step 2 runs every acceptance command before editing (`factory/prompts/implementer.md`). Verifier step 3 runs the same commands on base (`factory/prompts/verifier.md`). For parent close, the verifier's head is the integration branch and its base is `parent_base` (`factory/cli.py:246-247`). The parent then closes only on a VERIFIED verifier run on the parent itself (`_parent_close_verified`, `factory/cli.py:860-875`; required by `ticket_transition`, `factory/cli.py:156`, and `archive_cmd`, `factory/cli.py:889`). The workflow script starts that run unconditionally (`factory/workflows/build.js:217-222`).
- From the request: "T-0014 and T-0015 changed only docs and prompts … no test can observe those files." This is partly wrong; see ESCALATIONS. T-0014's merge `fcc8756` touched only `docs/writing.md`. T-0015's merge `530c9ef` also changed `factory/cli.py`, `factory/instance.py` and added `tests/factory/test_coding_standard.py`. The suite also reads documentation: `tests/factory/test_writing_standard.py:65,77` and `tests/factory/test_coding_standard.py:74,86` read `docs/design.md` and compare it to `docs/prompts/*`.
- No reference fix exists. The request names no Nanobot-side commit, and `~/dev/nanobot-upstream` is now on `feat/lionbot-v3.5` with no `factory/` directory.
- Duplicate search: open issues #14 (as-built build half, incl. a baseline-relative gate), #21 (current-state spec) and #24 (token cost) are related but none asks for this. #24 is excluded by the request itself.

Assumptions (mine, not stated by the requester):
1. The proposed parts A–D are the requester's suggestion. The requirement is the evidence plus the stated acceptance: fewer runs that cannot change the verdict, and no refusal lost. The spec writer may reshape A–D within that.
2. "Every refusal still happens" includes failures in what the suite reads, not only in code. So any path list that lets a gate command be skipped (part D) must cover every file that command reads. On this repo that includes `docs/design.md` and `docs/prompts/**`.
3. Dropping the before-edit and base runs of REGRESSION checks (parts A and B) means a REGRESSION check that was already failing on `main` now shows up only as a failure on head. Today the implementer's step 2 would stop and escalate it as a spec mismatch. I assume the requester accepts that routing change, since `main` passed the suite at its last merge.
4. Part C covers only the case the requester names: exactly one sub-ticket, `main` unmoved since its merge, and the sub-ticket's checks include every parent scenario. Every other parent close runs as today.
5. "Measured on the next real build, against T-0015's timings" is a follow-up observation for the operator. It is not a pass/fail acceptance check; the pass/fail checks are the preserved refusals.
6. Suggested priority, for the operator: high. The operator called it blocking for the port.

Reason (ACCEPT): the intent is clear and the requester stated the safety bar. The one defect in the proposal (part D's path list) is settled by that bar, so no product decision is needed. The spec writer must derive D's covered paths from what each gate command actually reads.

Out-of-scope observations:
- On a parent-close run, the gate check `git diff --check main...HEAD` compares `main` with itself and tests nothing (`run-0112-verifier/output.md:44`). Part C would skip that run in its case, but the issue remains for every other parent close.
- Issues #14 and #21 restate the verifier's gate step and the parent-close rule in `docs/design.md`. This ticket edits the same text, so whichever lands second must merge onto the other.

STATUS: ACCEPT
CONFIDENCE: medium. The intent and the main costs are confirmed from run records and code, but part of the evidence is wrong, and part D's real saving on this repo is unmeasured.
ESCALATIONS:
- Part D as proposed would drop a refusal the gate gives today, which breaks the request's own acceptance. The proposal lets the suite cover only `factory/**`, `bin/factory`, `tests/**`, `pyproject.toml` and `uv.lock`. But the suite reads `docs/design.md` and `docs/prompts/*` (`tests/factory/test_writing_standard.py:65,77`; `tests/factory/test_coding_standard.py:74,86`). An edit to a prompt block in `docs/design.md` without re-copying `docs/prompts/` fails the suite today, and under D it would be skipped. The evidence behind D is also partly wrong: T-0015 (`530c9ef`) changed `factory/cli.py` and `factory/instance.py`, so it was not a docs-only ticket. Once `docs/**` is covered, D would not have skipped the suite for T-0014 or T-0015 either. D's saving would come mainly from the Nanobot instance's own path list. Decide at the spec gate whether D stays in this ticket on that basis.

## Request (raw)

---
title: "Build speed: run each test suite only where it can change the verdict"
labels: "harness"
---
**Where:** `factory/prompts/implementer.md` and `verifier.md` (and their `docs/design.md` / `docs/prompts/` copies), the build half's parent-close step (`factory/cli.py` join/close, `factory/workflows/build.js`), and the gate commands' use in the verifier prompt.

**Problem:** one sub-ticket runs the target's full test suite four or five times, and most of those runs cannot change the outcome. For spec-factory that costs a few minutes per ticket. For the Nanobot v3.5 port, about 7,600 tests with every extra installed, it is the largest cost of each build, multiplied by 32 tickets.

**Evidence (spec-factory runs, 2026-10-03):**
- T-0015's implementer took 431 s. About 103 s went to running the suite and the acceptance checks *before* editing, and about 85 s to running them again after. `main` had already passed the same suite at its last merge, so the before-run of a regression check proves nothing. Only checks labelled NEW need a before-run, because they must fail first.
- T-0013: the parent-close verifier re-ran the same scenarios and the same suite on the merge of the one sub-ticket's checked head into an unchanged `main`. That took 5.5 min, 20% of the build.
- T-0014 and T-0015 changed only docs and prompts. The suite ran at every stage, though no test can observe those files.

**Proposed change:**
- A. The implementer runs the checks labelled NEW before and after the edit, and the REGRESSION checks and gate commands after only.
- B. The verifier runs the checks labelled NEW on base and head, and the REGRESSION checks and gate commands on head only.
- C. Parent close reuses the sub-ticket's VERIFIED result, without a new verifier run, when all of these hold: the parent has exactly one sub-ticket; `main` has not moved since that sub-ticket's merge; and the sub-ticket's acceptance list contains every scenario of the parent. Otherwise parent close runs as today.
- D. A gate command can declare the paths it covers. When a branch's diff touches none of them, the command is skipped and the `ci` row records the skip and the reason. Instance B: the suite covers `factory/**`, `bin/factory`, `tests/**`, `pyproject.toml` and `uv.lock`.

**Acceptance:** B and C are measured on the next real build, against T-0015's timings. Every refusal the gate gives today still happens: a failing NEW check, a failing regression, a failing suite on a code diff.

**Out of scope:** the clerk (deferred by the operator, #24); typed role agents (#24 part A).
