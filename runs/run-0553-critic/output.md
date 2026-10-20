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

STATUS: REVISE
CONFIDENCE: high, every cited path, line and pinned test was checked and two acceptance commands printed what the spec says; the one blocking item is a glossing gap with a one-phrase fix
ESCALATIONS: none
