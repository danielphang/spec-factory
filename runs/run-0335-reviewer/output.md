Commit: 9a87c3e3983a8dd04c7e21f9dd6fdfe99dfe5a41 (branch `factory/T-0035.1`, base `49ea4c7646475a00adee963e1e806302a3eed18c`, one commit)

## What I checked

1. Test integrity: no file under `tests/` is in the diff (`git diff --stat 49ea4c7..9a87c3e` lists only `docs/changelog.md`, `docs/design.md`, `docs/principles.md`, `docs/prompts/03-spec-critic.md`, `factory/prompts/critic.md`). No test weakened, skipped or deleted.
2. Correctness, part A: I extracted the spec's eight-line block from `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0035/v2.md` and compared it with `sed -n '/^Spot-check at least 2 cited paths/,/^what you could not check\.$/p'` on each of the three files; `cmp` reported SAME for `docs/design.md`, `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`. The design block extracted from `docs/design.md` is byte-identical to `docs/prompts/03-spec-critic.md`. `diff docs/prompts/03-spec-critic.md factory/prompts/critic.md` shows only the `round {2}` / `round 2` line, the same one difference as on `main` (line 74 there, 75 now: the block grew by one line). The diff hunks touch only the PROCESS lines; the `Turn economy:` paragraph, everything before PROCESS and everything from ANTI-GOODHARTING on are untouched.
3. Correctness, parts B, C, D: principle 2 now reads `suite (#73, kept by #74, \`factory/prompts/critic.md\`).` once and `builds nothing` zero times in `docs/principles.md`. The Spiking paragraph (everything after the `## Spiking` heading and its blank line) is byte-identical to the spec's block C, and the file ends with a single newline. Changelog entry 59 is byte-identical to the spec's block D, follows entry 58, and the `Declined:` line follows it. `git diff --check 49ea4c7..9a87c3e` exits 0.
4. Scope: five files, all named by the spec's parts A to D; no file under `agents/`, no writer prompt, no code. `git rev-parse main` in the worktree is `49ea4c7`, so the acceptance commands that use `main` compare against the spec's base.
5. Silent behaviour changes: none beyond what the spec asks. The critic's prompt is the only runtime-visible text changed, and it changes as specified.
6. Security and data safety: text-only change; nothing to flag.
7. Protected paths: `factory/prompts/critic.md` (harness) and `docs/prompts/03-spec-critic.md` (generated), both declared in the spec's Risk list. Listed under ESCALATIONS below as the role requires; the merge gate needs a human approval.
8. Coding standard: no code added; no `reuse:`, `stdlib:`, `native:`, `yagni:` or `delete:` finding applies. Lean already.
9. PR description: What changed says in words what was removed, what was kept and why, and glosses "critic". Known gaps lists the `factory:` markers (none), the unrun replay, and the runtime's state. I confirmed the runtime claim: `.factory/harness.lock` holds `ef9a74b`, and `git merge-base --is-ancestor 05cf8f9 ef9a74b` fails, so the runtime predates #73 as the description says. The "no `AGENTS.md`" observation is also true (`git ls-tree main` lists none).

## Findings

- [SHOULD-FIX] PR description: What changed: two terms specific to the factory are not glossed at first use (writing standard rule 2). "three past intakes" does not say what an intake is (a ticket the factory took from request to approved spec; the spec's Problem section glosses it). Part A says "as the s1 output `fill=unchanged` shows" and nothing defines `s1` → the operator at the gate reading the description without the spec has to guess what an intake is and which output "s1" names. Suggested wording: "three past intakes, tickets the factory had already taken from request to approved spec" and "as the first acceptance scenario's `fill=unchanged` shows". Prose only; the code is correct and merges as is.

No BLOCKING findings. No NIT beyond the above.

## Prior findings

None: round 1.

## Out-of-scope observations

- None.

STATUS: APPROVE
CONFIDENCE: high. Every changed region is byte-identical to the spec's blocks by `cmp`, the three critic copies agree with each other exactly as they did on `main`, and no file outside the spec's five is touched.
ESCALATIONS: Protected paths touched, both declared in the approved spec's Risk section: `factory/prompts/critic.md` (harness: the prompt the critic runs under) and `docs/prompts/03-spec-critic.md` (generated: a verbatim copy of the design doc's critic block, re-copied here from that block and matching it byte for byte). The merge gate requires a human approval for them; nothing else to escalate.
