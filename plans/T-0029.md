## ST-1 / Declared protected paths leave the implementer and verifier ESCALATIONS lists
Depends on: none
Parallel-safe: yes

Parent: T-0029, approved spec v2 (issue #49). Read it for context. Do NOT implement parts outside this sub-ticket.

One sub-ticket. The whole change is about 40 added lines of prompt text plus one changelog line, and the spec's prototype was 37 added lines across six files. Splitting it would gain nothing for review or rollback. It would also break things: the existing test that keeps each design block equal to its `docs/prompts/` copy fails if part A lands in `docs/design.md` without the copies, and part B's changelog entry describes part A.

Scope: parts A and B of the parent's design.
- A. Add the new RULES bullet, word for word and with the spec's line breaks, as the last bullet under `RULES` in five places:
  - `factory/prompts/implementer.md`, after the `- On fix rounds: …` bullet (it ends at line 43 on `main` at `7d57998`);
  - `factory/prompts/verifier.md`, after the `- Anti-Goodharting: …` bullet (it ends at line 33);
  - `docs/design.md`, in the fenced blocks under "## 5. Implementer" (anchor at line 585) and "## 7. Verifier" (anchor at line 693);
  - `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, each re-copied in full from its design block.

  Do not change the code reviewer's prompt or the preamble in any copy.
- B. One numbered entry in `docs/changelog.md`, after the last numbered entry and before the "Declined:" line, with the content the design lists. It opens "After issue #49 (2026-10-04)", uses 10 runs and 30 of 205 items, and contains `#49` and `ESCALATIONS`.
  - Numbering note: the spec expected 53, or 54 if #46 landed first. On `main` at `7d57998`, entries 53 (#46) and 54 (#40) already exist (`docs/changelog.md` lines 57-58). So the next free number is 55. The spec's acceptance does not fix the number, only that numbering stays contiguous.

Acceptance (all from the parent; commands run from the repo root after `uv sync --frozen`, under the HOME wrapper, with `TMPDIR` set to the run's scratch directory for the fixture):
- Implementer and verifier run prompts carry the declared-path rule (NEW).
  - GIVEN: write the fixture with the spec's `cat > ${TMPDIR:-/tmp}/t0029-prompt.sh <<'EOF' … EOF` block, verbatim.
  - WHEN: `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer verifier; do P=$(prompt $r); echo "$r declared=$(echo "$P" | grep -c 'A protected path the sub-ticket declares is not an escalation') notunder=$(echo "$P" | grep -c 'but not under ESCALATIONS') undeclared=$(echo "$P" | grep -c 'still goes under ESCALATIONS when the sub-ticket does not declare it')"; done)`
  - THEN: it prints exactly `implementer declared=1 notunder=1 undeclared=1`, then `verifier declared=1 notunder=1 undeclared=1`.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 (REGRESSION).
  - WHEN: `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
  - THEN: it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line.
- The design blocks and their copies carry the rule and stay in step (NEW).
  - WHEN: the spec's command beginning `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" …`, verbatim from `specs/harness-docs/spec.md`.
  - THEN: it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`.
- The code reviewer and preamble copies do not change (REGRESSION).
  - WHEN: `(echo "changed=$(git diff --name-only main...HEAD -- factory/prompts/reviewer.md factory/prompts/preamble.md docs/prompts/06-code-reviewer.md docs/prompts/00-preamble.md | grep -c .)")`
  - THEN: it prints exactly `changed=0`.
- The changelog records the declared-path rule in a contiguous entry (NEW).
  - WHEN: `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
  - THEN: it prints `CONTIGUOUS`, then `1`.
- The declared-path change adds no whitespace errors (REGRESSION).
  - WHEN: `(git diff --check main...HEAD; echo "exit=$?")`
  - THEN: it prints only `exit=0`.
- Intermediate check: the harness suite (REGRESSION). This is not a parent scenario. It guards the existing copy-equality test.
  - WHEN: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, with pytest's temporary directory under `/tmp` as the current-truth suite scenario does.
  - THEN: all tests pass, none skipped or deselected beyond what `main` already does.

Tests to change: none

Protected paths:
- harness (`factory/**`): `factory/prompts/implementer.md` and `factory/prompts/verifier.md`.
- generated (`docs/prompts/**`): `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`.
- Guardrail paths (agent prompts) that the spec's Risk declares: the four files above, plus the "## 5. Implementer" and "## 7. Verifier" blocks in `docs/design.md`.

Out of scope:
- The code reviewer's prompt, including check 6 and its wording "the merge gate will require a human approval". That wording is a separate ticket.
- The shared preamble in every copy.
- Any harness code, routing, or the escalation queue's parser.
- Other noise in implementer and verifier ESCALATIONS lists.
- `README.md`, `dev/build-harness.spec.md`, and anything under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream` or `~/.nanobot/`.
- The operator steps: the runtime upgrade, `--accept-harness`, and checking the queue on the next build.

Coverage map:
- Implementer and verifier run prompts carry the declared-path rule → ST-1
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → ST-1
- The design blocks and their copies carry the rule and stay in step → ST-1
- The code reviewer and preamble copies do not change → ST-1
- The changelog records the declared-path rule in a contiguous entry → ST-1
- The declared-path change adds no whitespace errors → ST-1

Verified for this plan, on `~/dev/spec-factory` at `7d57998`:
- `grep -n` found the anchor bullet endings at `factory/prompts/implementer.md:43`, `docs/prompts/05-implementer.md:42`, `docs/design.md:585`, `factory/prompts/verifier.md:33`, `docs/prompts/07-verifier.md:32` and `docs/design.md:693`.
- `sed -n` showed that each anchor is the last bullet under `RULES`: a blank line and the next section heading (`PR DESCRIPTION` or `OUTPUT`) follow it.
- The headings are at `docs/design.md:541` ("## 5. Implementer") and `:659` ("## 7. Verifier").
- The changelog's last numbered entries are 53 (#46) and 54 (#40), with "Declined:" at line 60.
- I did not run the acceptance scenarios. The spec records their before and after results on its prototype clone.
