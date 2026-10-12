Commit: 608a62ced66a5f32cb0e3e090d43ef75dd2a6618 (branch `factory/T-0043.3`, base `ebc5773ef696d25c58159c61a7531e7ee3b61b3f`, which is `main`)

## What I checked, in the prescribed order

1. Test integrity. `git diff --stat ebc5773...608a62c` lists five files: `README.md`, `dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md`, `docs/principles.md`. `git diff --name-only ... -- docs/prompts factory/prompts tests factory bin agents` prints nothing. No test, prompt copy or code changed.

2. Correctness against part E. Every item of part E is present where the spec puts it, read in the worktree:
   - README: the read-only list sentence is inside "## Where a human decides" (heading at line 830, sentence at 836-837); the lock sentence is inside "### Accepting a harness revision" (548); `### Counting what each role catches and costs` (885) follows `### What you read at each stop` (872) and precedes `## What is built and what is not` (928); the "What depends on Claude Code" row (110); the **Built** bullet; the status header already reads 2026-10-11, which is today, so "bump" leaves it as is (the PR description says so).
   - design.md: fence paragraph, role-context lock clause and model-per-role paragraph changed; the §8 block untouched (prompt copies unchanged, so the §8 block it mirrors must be too).
   - principles.md §4: "3 BLOCKING findings in total"; "Implemented by:" names `factory stats` and no longer says "double-counts"; "Planned:" keeps only #79.
   - build spec: the `**`factory stats`**` paragraph follows `**`factory drive`**`. Its two code claims hold on this head: `("stats", None)` is in `READ_ONLY` (`factory/cli.py:1976`) and `main()` handles `stats` with `init` and `paths` before the instance lookup (`factory/cli.py:2011`). Its `FACTORY_STATE`-before-instance order matches `stats_cmd` (`factory/cli.py:1640-1641`), and README's `--store` row says the same.
   - changelog: entry 70 in the "After issue #N (date), where ...:" form; the acceptance `awk` prints `CONTIGUOUS`.
   - The figures. The spec says the design paragraph must quote what `factory stats` prints and compare with Evidence. I re-ran the quoted command on this head, after `uv sync --frozen` in the worktree, through the wrapper, with the transcripts directory as an absolute path: `bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 --transcripts /Users/dphang/.claude/projects` exited 0. Section D printed `| critic | fable | 84 | 22755 | 66027675 | ...`, `| implementer | opus | 114 | 55980 | 372507821 | ...`, `| reviewer | fable | 99 | 29455 | 94860442 | ...`, `| verifier | fable | 5 | 2647 | 5189563 | ...`, `| verifier | opus | 108 | 45342 | 232945610 | ...`; section A printed `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 111 read, 0 not recorded |`. All six token figures, the run counts (99, 84, 114, 108, 5), the changed-outcome counts (4 of 94, 19 of 84, 18 of 111, 8 of 108, 1 of 5), "3 BLOCKING findings" and "no gate failure found fixed" in the design paragraph are what the command prints, and the four that Evidence lists (94,860,442 over 99; 372,507,821 over 114; 232,945,610 over 108; 3 BLOCKING) agree with Evidence. The critic's and the Fable verifier's token figures are not in Evidence; the command is their source, and it prints them.
   - The acceptance grep "The documents record factory stats", run verbatim from the worktree through the wrapper, printed `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, `CONTIGUOUS`, `4`, `clean`. (A cheap, read-only check; the verifier owns the gates.)

3. Scope. One edit is outside part E's list: a sentence in README's "Related work and history" (lines 1127-1128) giving the issue numbers #70, #61 and #42. README's "Maintaining this page" rule sends every issue number to that section rather than the body, so the sentence is what the README's own contract asks for once the **Built** bullet exists. I take it as in scope.

4. Silent behaviour changes. None possible: no code changed.

5. Security and data safety. None: documents only.

6. Protected paths. None touched. `docs/prompts/**` is unchanged (`prompts=0`).

7. Coding standard. Not applicable; no code.

8. PR description. "What changed" says in words what the change is, glosses "store" and "`factory stats`" at first use, and states where each figure came from. "Known gaps" is honest: the unchanged status date, the absolute transcripts path, the dependence on transcripts Claude Code still keeps, the gate-column limit, and the one-off suite failure in `test_drive_build.py`, which it correctly leaves alone since no code changed. No finding.

Findings: none.

Prior findings: not applicable (round 1).

Out-of-scope observations:
- README's how-to says reading `~/.claude/projects` "takes about 12 seconds on this machine". A README reader is not on this machine; "on the author's machine" or a count of files would travel better. Prose only, below NIT.
- The design paragraph packs five roles' figures into one sentence. The spec asked for "one or two sentences", so the implementer followed it; the writing standard's §12 (parallel facts go in a table) would be the later improvement, by amending the design, not this ticket.

STATUS: APPROVE
CONFIDENCE: high. No code or test changed; every part E item is present and I re-derived the design doc's quoted figures by running the quoted command on this head.
ESCALATIONS: none
