Sub-ticket: T-0029.1 (ST-1, "Declared protected paths leave the implementer and verifier ESCALATIONS lists"), parent T-0029, approved spec v2 (issue #49). Branch `factory/T-0029.1`, head `090939d6428bff085890aa5d1b9d384bb8915c78`, base `7d57998169bf08563fe33fcd098729fae200c4b9`.

## What changed

After this change, the implementer and verifier prompts tell those roles not to list a declared protected path under ESCALATIONS. A protected path is a repository path that needs a human's approval before a change to it merges. A declared one is a path the sub-ticket says it will touch. ESCALATIONS is the list at the end of each role's output, and the harness copies every item on it into the operator's escalation queue. The code reviewer is now the only role told to list declared paths. It keeps doing so once for each head (each commit put up for review), through its check 6, which is unchanged. Every role still escalates an undeclared protected path. The change is prompt text and one changelog line: 37 added lines across six files, with no deletions and no code.

- A. The spec's RULES bullet, word for word and with its line breaks, is now the last bullet under `RULES` in five places:
  - `factory/prompts/implementer.md`, after the `- On fix rounds: …` bullet;
  - `factory/prompts/verifier.md`, after the `- Anti-Goodharting: …` bullet;
  - `docs/design.md`, inside the fenced blocks under "## 5. Implementer" and "## 7. Verifier", at the same two places;
  - `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. I re-copied each in full from its design block, using the same awk extraction the acceptance command uses. Each copy's diff is only the six added lines.
  - The bullet went in through a script that matched the anchor line, and the script checked that each anchor occurs exactly once in its file. The code reviewer's prompt and the preamble are untouched in every copy.
- B. A new entry 55 in `docs/changelog.md`, after entry 54 (#40) and before the "Declined:" line.
  - It opens "After issue #49 (2026-10-04)" and gives the re-derived count: 10 runs, 30 of 205 queued items.
  - It then states the rule in the five points the design lists, and records that the retro's figure of 26 of 139 was rejected.
  - The number is 55, not the spec's 53, because entries 53 (#46) and 54 (#40) were already on `main` at `7d57998`. The ticket's numbering note says the same.

## Acceptance results

Every command ran from the worktree root under the HOME wrapper, after `uv sync --frozen`. `TMPDIR` was set to this run's scratch directory, and the fixture was written there with the spec's block, verbatim.

| Check | Label | Before (base `7d57998`) | After (`090939d`) |
|---|---|---|---|
| 1. Implementer and verifier run prompts carry the declared-path rule | NEW | `implementer declared=0 notunder=0 undeclared=0`, `verifier declared=0 notunder=0 undeclared=0` | `implementer declared=1 notunder=1 undeclared=1`, `verifier declared=1 notunder=1 undeclared=1` |
| 2. All three run prompts keep the undeclared-path rule; reviewer keeps check 6 | REGRESSION | not run | `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` |
| 3. Design blocks and copies carry the rule and stay in step | NEW | `implementer copy=SAME rule=0 fill=unchanged`, `verifier copy=SAME rule=0 fill=unchanged` | `implementer copy=SAME rule=1 fill=unchanged`, `verifier copy=SAME rule=1 fill=unchanged` |
| 4. Code reviewer and preamble copies do not change | REGRESSION | not run | `changed=0` |
| 5. Changelog records the rule in a contiguous entry | NEW | `CONTIGUOUS`, `0` | `CONTIGUOUS`, `1` |
| 6. No whitespace errors (`git diff --check main...HEAD; echo "exit=$?"`) | REGRESSION | not run | `exit=0` |

Each NEW command failed on the base exactly as the spec's verification section predicted. Each command printed its THEN lines after the change. Neither REGRESSION command failed, so neither needed a run on the base.

Gates, each run once on `090939d`, from the worktree, exactly as written:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `310 passed in 379.56s (0:06:19)`, with nothing skipped or deselected. This also covers the existing test that keeps each design block equal to its `docs/prompts/` copy.

## Tests added/changed

None. The design says no suite test is required: the acceptance commands check the composed run prompts and the document copies from outside, and the existing copy-equality test already guards the design blocks. "Tests to change" is none, and no existing test file was touched.

## Known gaps and uncertainties

- The checks prove only that the rule text reaches the composed implementer and verifier prompts. They cannot prove that a model will follow it. The spec keeps that check as operator step 2: on the next build, read the escalation queue.
- The ticket asks for the suite to run with pytest's temporary directory under `/tmp`. I ran the gate exactly as written, in a shell whose `TMPDIR` was the macOS default, `/var/folders/1t/.../T/`. That directory is not `/tmp`, but like `/tmp` it lies outside the repository and the store. I believe this is the condition the ticket means, but I have not verified that the suite behaves the same under `/tmp` itself.
- The ticket gave the design-doc anchors as lines 585 and 693. On `7d57998`, the two bullets end at lines 585 and 693, and the headings are at lines 541 and 659. The inserts are at the bullet ends, as the ticket intends.
- factory: markers added: none.

## Out-of-scope observations

- This change touches no harness code. The rule reaches runs only after the operator upgrades the runtime (the checkout at `~/dev/spec-factory-harness` that runs execute from) and accepts the new commit with `--accept-harness <commit>` in each instance, as the spec's Operator steps say.
- The spec's own out-of-scope note still stands. Check 6's wording "the merge gate will require a human approval" does not match local mode, where no merge check reads the declaration. That wording is for a separate ticket.

## Responses to findings

Not applicable: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates ran on the committed head and printed exactly the expected output, and the diff is the spec's 37 lines.
ESCALATIONS: none
