## Acceptance

Every command was run on `main` at `788a201` from `~/dev/spec-factory`, under the running-code wrapper, with both `/bin/sh` (bash 3.2.57) and zsh. Both shells gave the same output.

- A none trailer followed by the attribution footer finishes with no escalation and queues nothing → NEW. Today it prints `finish=["none", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]` and `queued=1 meta=1`.
- A real item above the attribution footer stays, and the footer is dropped → NEW. Today it prints `["none", "the auth path needs review", "🤖 Generated with [Claude Code](https://claude.ai/code)"]`.
- Real item lines, and a line that only mentions Claude Code, are still read by rule (b) → REGRESSION. Today it prints the THEN exactly.
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance → REGRESSION.
  - Under zsh and bash 5, the old text and the restated text both print the THEN. Under `/bin/sh` only the restated text does.
  - #113 is an edit to scenario text, applied at archive, so no item can fail on the base code and pass on the PR. To check the restated text under the shell #113 concerns, run `(F=.factory/store/openspec/changes/T-0058/specs/build-dispatch/spec.md; T=$(mktemp -d); B=$(printf '\140'); sed -n '/^#### Scenario: Each launch copy is a one-line change/,/^- WHEN/p' $F | sed -n "s/^- WHEN $B\(.*\)$B\$/\1/p" > $T/w.sh; /bin/sh $T/w.sh)`. It must print the THEN.
  - With `F` set to current truth, `.factory/store/openspec/specs/build-dispatch/spec.md`, the same command prints `syntax error near unexpected token 'newline'` and `intake: where= echo own-dir;; *) echo none;; esac) …`. I ran both forms, with my restated text standing in for the change file.
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy → REGRESSION. It is restated word for word.
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy → REGRESSION. It is restated word for word.
- init reports an edited agent copy and leaves it as it is → REGRESSION. It is restated word for word.
- init still creates a missing agent copy and lists no matching copy → REGRESSION. It is restated word for word.
- init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is → NEW. Today it prints `exit=1 stale=absent kept=yes named=1 unread=0 others=0`. The `named=1` comes from the PermissionError line, which names the copy.
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance → NEW. Today it prints `init: exit=0 named=0 hint=0 json=0`, `paths: exit=0 named=0 hint=0 json=0`, `stats: exit=0 named=0 hint=0 json=0`, `target=unchanged`, `fresh: exit=0 files=16`.
- Without the flag paths and stats still run under another lock, and config still accepts a revision → REGRESSION. Today it prints `paths=0 stats=0 config=2 accept=0 lock=accepted`.
- README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy → NEW. Today it prints `accepting=0 upgrade=0 stats=0 row=0`.
- The design doc states the footer rule and the refusal in the lock clause → NEW. Today it prints `footer=0 lock=0`.
- The changelog records the four issues in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, `0`, `0`.
- The harness suite passes → REGRESSION. On `main` at `788a201`, under the wrapper, it printed `615 passed in 79.30s`.
- The only existing test file changed is the stats test → REGRESSION. On the base it prints nothing.
- Current truth also checked, not part of this delta: the harness-docs scenarios "README is at most 1,185 lines" and "The maintained documents pass git's whitespace check in full". "The documents record factory stats" also still passes, because the README "Accepting" section and design line 68 still name `stats`; I ran it today and it printed its THEN. So does "The design doc states the EMPTY-OUTPUT rule, its rows and its park".

## Responses

- [BLOCKING] Decisions, first bullet: `rule (b)` and `parse()` not glossed → FIXED. Problem item 1 now ends the sentence about the 2026-10-01 rule with "(the code calls it rule (b))". The Decisions bullet now reads "the trailer parser, `parse()` in `factory/status.py`, drops…". While there, I also glossed `factory drive` and the Workflow-script path where the rejected-option bullet first uses them.
- [SHOULD-FIX] `stale_agents` used as a known name → FIXED. Problem item 3 now says "It lists a copy that differs under `stale_agents` in its JSON output, and leaves it alone."
- [NIT] the mode-`000` scenario assumes a user other than root → FIXED. The scenario now has the GIVEN line "the shell runs as a user other than root, since root reads a file at mode `000`". Its WHEN and THEN are unchanged.
- Not a finding, but new evidence: v1 said I had not run the suite. I have now run it on `main` at `788a201` under the wrapper: `615 passed in 79.30s`. The suite item under Acceptance records this.

## Critic rounds

round 1 · spec v1 · run-0553-critic · REVISE

# Critic review: T-0058 spec v1 (round 1)

What I checked, on `main` at `788a201`:
- Cited code: `factory/status.py` `parse()` lines 37-49 build `tail` from every non-blank line below ESCALATIONS and make `[esc_head, *tail]` the item list; `factory/setup.py:187` calls `read_bytes()` with no handler; `factory/cli.py:851-855` returns for `init`, `paths` and `stats` before the lock at line 863, with the comment "ignore --accept-harness"; `Refused` is imported at line 25. All as the spec says.
- Evidence: `run-0538-implementer/output.md` ends `ESCALATIONS: none`, blank, footer; its `meta.yaml` line 25 holds the footer as an item; `log/2026-10.jsonl:2861` is the false `escalation.queued` event. It is the only `meta.yaml` in this store that mentions the footer.
- Current truth `build-dispatch/spec.md:694` has `case "$C" in $T/tmp/factory-launch-*/$s.js) echo own-dir;;`, the unparenthesised pattern.
- Tests pinning old behaviour: the only test that passes `--accept-harness` to `init`, `paths` or `stats` is `tests/factory/test_stats.py:419-423`, which "Tests to change" lists. No test or workflow script mentions `Generated with` or `Co-Authored`. Neither workflow script passes `--accept-harness`.
- Ran two acceptance commands under the wrapper from `~/dev/spec-factory`: "The design doc states the footer rule and the refusal in the lock clause" printed `footer=0 lock=0` (NEW, fails today as stated); "Without the flag paths and stats still run under another lock, and config still accepts a revision" printed `paths=0 stats=0 config=2 accept=0 lock=accepted` (REGRESSION, passes today).
- README line 611 and design line 68 and 105 hold the text the spec cites. The "Accepting a harness revision" section has no sentence today that the new `accepting=` count would match, so the count can only be 1 after the edit. README is 1,174 lines against the 1,185 budget. The last changelog entry is 75.
- Open tickets T-0055 to T-0060: none changes the trailer parser, `init`, or the `--accept-harness` handling. T-0059 (#120, the gate replays current-truth scenarios) depends on the #113 fix, which the spec notes. Approved changes not yet archived: none.

Not checked: the suite scenario, and that the `attribution.pr` setting does or does not change a `claude -p` reply. The spec says the same.

## Findings

[BLOCKING] 6 Decisions, first bullet
Problem: The first paragraph of Decisions uses two terms of art, `rule (b)` and `parse()`, that no human-facing section has glossed; the Problem describes the 2026-10-01 rule but never attaches the label "(b)" to it, and `parse()` is named only under Root cause.
Evidence: Problem item 1 says "The operator chose that rule on 2026-10-01" with no "(b)"; the first mention of "rule (b)" and of `parse()` outside Root cause is the Decisions bullet "#88 is fixed in the parser. Before rule (b) is applied, `parse()` drops…".
Suggested fix: In Problem item 1, end the sentence about the rule with "(the code calls it rule (b))", and in the Decisions bullet write "the trailer parser, `parse()` in `factory/status.py`, drops…" so both terms are glossed where the operator first meets them.

[SHOULD-FIX] 6 Decisions, #114 bullet
Problem: `stale_agents` is used as a known name, but the Problem only says init "lists a copy that differs" and never names the JSON field.
Evidence: First mention of `stale_agents` in a human-facing section is Evidence's last bullet, as a decision title, with no gloss.
Suggested fix: In Problem item 3, say "It lists a copy that differs under `stale_agents` in its JSON output, and leaves it alone."

[NIT] 2 store-setup scenario "init lists an agent copy it cannot read"
Problem: The scenario relies on mode 000 blocking a read, which is false when the shell runs as root, so a root runner would print `stale=absent`.
Evidence: `chmod 000` then `$B init`; root bypasses file permissions.
Suggested fix: Leave as is, since the suite and the gate run as the operator, or add one GIVEN line saying the scenario assumes a non-root user.

No other findings. Scope fits one PR, each lettered part serves one of the four issues, "Tests to change" names the one test the #115 decision breaks, the three protected paths are declared under Risk, and the overturned T-0043 decision is named with a standing replacement.

round 2 · spec v2 · run-0555-critic · APPROVE

# Critic review: T-0058 spec v2 (round 2)

Round 2, so this review covers whether the round-1 findings were resolved and the text that changed between v1 and v2. The v1-to-v2 diff touches Problem items 1 and 3, the first two Decisions bullets, one GIVEN line in the store-setup scenario, the suite line under Acceptance, and the new Responses section. Nothing else moved.

What I checked, on `main` at `788a201`, from `~/dev/spec-factory`:
- `factory/status.py` lines 37-49 still build `tail` from every non-blank line below ESCALATIONS and make `[esc_head, *tail]` the item list, with the comment naming "option (b)" and the 2026-10-01 decision. The spec's gloss "the code calls it rule (b)" matches the comment.
- `factory/cli.py` lines 851-855 still return for `init`, `paths` and `stats` before `instance.guard` at line 863, with the comment "ignore --accept-harness". `factory/setup.py:187` still calls `read_bytes()` with no handler.
- Ran the acceptance command "The design doc states the footer rule and the refusal in the lock clause" under the running-code wrapper. It printed `footer=0 lock=0`, so the item is NEW and fails today as the spec says.
- `- GIVEN` lines are an established scenario form: ten current-truth capabilities use them, build-dispatch five times, so the new GIVEN line follows the store's own convention.
- Approved changes not yet archived: none, so no cross-ticket setup conflict to check.

Not checked: the suite scenario (the writer reports `615 passed in 79.30s` on the base, which I did not rerun), and whether `attribution.pr` changes a `claude -p` reply; the spec says the same and rejects that route for stated reasons.

## Prior findings (round 1)

- [BLOCKING] 6 Decisions, first bullet, `rule (b)` and `parse()` unglossed → RESOLVED. Problem item 1 now attaches "(the code calls it rule (b))" to the 2026-10-01 rule, and the Decisions bullet reads "the trailer parser, `parse()` in `factory/status.py`, drops…". The second bullet also now glosses `factory drive` and the Workflow-script path at first use. Read as the operator new to the system, the first paragraph of each human-facing section now stands on its own.
- [SHOULD-FIX] 6 Decisions, #114 bullet, `stale_agents` used as a known name → RESOLVED. Problem item 3 now introduces it as the JSON field init lists a differing copy under.
- [NIT] 2 store-setup scenario, mode-000 read assumes a non-root user → RESOLVED. The scenario carries a GIVEN line saying so; WHEN and THEN are unchanged.

## Findings

No new findings. The changed text introduces no new term of art without a gloss, no new decision, and no change to any scenario's WHEN or THEN. The round-1 assessment stands: scope fits one PR, each lettered part serves one of the four issues, "Tests to change" names the one test the #115 decision breaks, the three protected paths are declared under Risk, and the overturned T-0043 decision is named with a standing replacement.

## Verifier results

6f4d8658252556ed62bd19e130b09634f119f454 · T-0058.1 · VERIFIED · run-0564-verifier
