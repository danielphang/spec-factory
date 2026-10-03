Commit: c367bef72e2ed70a4417e98de907c91dbbe31320 (branch `factory/T-0012.2`, one commit over base/`main` `cdb1c6769ecc39208e62edc65578f62f5a23908f`; `git status --porcelain` empty in the worktree)

How I ran it: every WHEN below verbatim, with bash, from the root of the worktree `intake/state/runs/run-0057-verifier/wt` (head) and from a detached scratch worktree of the same repo at `cdb1c67` (base), with `BASE=$(git rev-parse main)` = `cdb1c67…` in both. The scratch worktree was removed afterwards. Nothing was written under `~/dev/nanobot-upstream` or `~/.nanobot`.

Per criterion:
- docs-moved-and-split | NEW | [specs/repo-layout] WHEN | base: seven `missing …` lines (docs/design.md, docs/changelog.md, docs/prompts/00-preamble.md, dev/build-harness.spec.md, dev/build-harness.plan.md, dev/P0-intake-skeleton.md, dev/issues.md) then `old_tracked=15` | PR: only `old_tracked=0` | PASS
- changelog-moved-verbatim | NEW | [specs/repo-layout] WHEN | base: `DIFFERENT` then `declined= numbering=NONE in_design=` | PR: `SAME` then `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- design-text-kept | NEW | [specs/repo-layout] WHEN | base: `570` (docs/design.md absent, the reason verification.md states) | PR: `0` | PASS
- prompt-copies-moved-unchanged | NEW | [specs/repo-layout] WHEN | base: `changed=10 of 10 DRIFT` | PR: `changed=0 of 10 VERBATIM` | PASS
- no-old-paths, documents only | NEW (intermediate) | `git grep -n … -- README.md docs dev >/dev/null; echo "exit=$?"` | base: `exit=0` (matches) | PR: `exit=1` | PASS
- how-to-use-names-new-homes | NEW (intermediate) | `awk '/^## How to use this/…' docs/design.md | grep 'docs/changelog\.md' | grep -c 'docs/prompts/'` | base: `awk: can't open file docs/design.md` then `0` | PR: `1` | PASS
- records-untouched | NEW (intermediate) | `git diff --name-only main...HEAD -- intake/state intake/answers intake/green-pilot intake/.gitignore | wc -l | tr -d ' '` | base: `0` | PR: `0` | SPEC-DEFECT (label). The check is sound and the PR satisfies it, but it passes on base too. It cannot do otherwise: on base `main...HEAD` is empty, so this criterion is an invariant, not a NEW behaviour. Under the verifier rule "a NEW criterion that passes on both is a SPEC-DEFECT", I report it as such. The fix is to relabel it REGRESSION (or an invariant) in the sub-ticket; the PR needs no change for it.
- green-harness-still-present | REGRESSION | [specs/self-instance] WHEN | base: `green keeps its harness` | PR: `green keeps its harness` | PASS
- whitespace (sub-ticket diff) | REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | base: `exit=0` | PR: only `exit=0` | PASS

Gate suite: PASS. `git diff --check main...HEAD` from the worktree printed nothing, exit 0.

Probes (all on the head, against `$BASE:docs/spec-factory.md` and the base files):
- Whole changelog body, not only the numbered lines: `diff <(base Changelog section body, heading and trailing blank dropped) <(tail -n +2 docs/changelog.md)` → no output, identical; file is 47 lines, ends in a single `\n`, last line is the `Declined:` line → OK
- Whole `docs/design.md` against base-minus-Changelog (`awk '!f'` cut), ordered diff rather than `sort -u`: the only difference is `30a31,32`: the added sentence "This document's changelog is `docs/changelog.md`, and `docs/prompts/` holds a verbatim copy …" plus one blank line; 759 − 48 + 2 = 713 lines. The sentence occurs once (line 31) and `## Harness: functional pieces` is line 33 → OK (no reordering, duplicate loss or stray edit; the reverted line-29 mishap the PR description mentions left no trace)
- `dev/P0-intake-skeleton.md` vs base with `specs/build-harness.md→dev/build-harness.spec.md` and `plans/build-harness.md→dev/build-harness.plan.md` substituted: identical. `dev/build-harness.plan.md` vs base with the first substitution: identical; 9 `Parent:` lines before and after → OK (renames are pure path swaps)
- Old-path grep widened to the two `intake/` files D.4 edits (`intake/README.md`, `intake/instance/context.md`): exit 1, no match; `specs/`, `plans/`, `issues/` tokens in `README.md`: none → OK
- Change set: `git diff --name-status -M main...HEAD` is 11 × R100 (`prompts/*`→`docs/prompts/*`, `specs/build-harness.md`, `issues/README.md`), R096/R097/R085 for the three edited renames, A `docs/changelog.md`, M `README.md`, `intake/README.md`, `intake/instance/context.md`. Nothing under `intake/state`, `intake/answers`, `intake/green-pilot`, `intake/.gitignore`, `intake/setup.sh`, `intake/HARNESS_PIN`, `intake/instance/{config.yaml,preamble.md}` → OK (file list matches the sub-ticket's and the infra allowance)
- The 15 old tracked paths at base are exactly `docs/spec-factory.md`, `specs/build-harness.md`, `plans/{build-harness,P0-intake-skeleton}.md`, `issues/README.md` and the 10 `prompts/*` files, so `old_tracked=0` means every one moved, none deleted → OK

Out-of-scope observations:
- `README.md` lines 7–8 are reworded, not token-swapped (the PR description flags this); within D.4's intent since the `specs/<ticket>.md` / `plans/<ticket>.md` directories no longer exist, and E.6 rewrites README.
- `README.md:11` still claims `docs/prompts/` "is regenerated" from the design doc; parent Evidence says nothing regenerates it. Left for E.6, as the PR description says.
- `intake/instance/config.yaml:9` and `intake/instance/preamble.md:38` still name `prompts/**`; outside this sub-ticket's file list, removed by E.5.

STATUS: SPEC-DEFECT
CONFIDENCE: high. Every acceptance command and the gate were run verbatim on the committed head and on the base; all substantive checks pass and the byte-level probes confirm the moves are exact. The SPEC-DEFECT is confined to the NEW label on records-untouched, which is structurally unable to fail on base; relabel it and this head verifies as-is.
ESCALATIONS: none
