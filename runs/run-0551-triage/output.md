Type: bug

Title: Four small harness defects: the escalation parser counts Claude Code's attribution footer as escalations, a build-dispatch scenario fails under macOS /bin/sh, `factory init` exits 1 on an unreadable agent copy, and `--accept-harness` is silently ignored by `init`, `paths` and `stats` (#88, #113, #114, #115)

Summary:
The operator wants four small harness defects fixed together. None of them changes routing. Each one leaves either a misleading record or a failed command that a person has to notice and work around.
- **#88.** When a role's `output.md` ends with Claude Code's attribution line after the STATUS trailer, the run is recorded with escalations it never raised: the trailer's `none` plus the footer line. The run then logs a false `escalation.queued` event. (The STATUS trailer is the closing STATUS / CONFIDENCE / ESCALATIONS block every role writes.)
- **#113.** One current-truth scenario in `build-dispatch` uses an unparenthesised `case` pattern inside `$( )`. macOS's `/bin/sh` (bash 3.2) cannot parse that, so the scenario fails whatever the code does. (Current truth is the store's `openspec/specs/`, the accepted behaviour of each capability.) The fix is to rewrite that scenario. The request asks for no code change here.
- **#114.** `factory init` should list an agent copy it cannot read under `stale_agents`, with a note on stderr, and exit 0. It should never overwrite the copy. Today it exits 1.
- **#115.** `factory --accept-harness <sha>` with `init`, `paths` or `stats` should be refused with exit 2, and the message should name a command that does accept the flag. Today the flag is silently ignored. README's "Accepting a harness revision" should say which commands accept the flag.

Evidence:
I checked every item on `main` (`788a201`). The runtime is at `1058db5`, and the harness lock (the accepted harness revision in `.factory/harness.lock`) is `e12ca71`.
- **#88, Nanobot target.** `~/dev/nanobot-upstream/.factory/store/runs/run-0418-implementer/output.md` ends with `ESCALATIONS: none`, a blank line, then `🤖 Generated with [Claude Code](https://claude.com/claude-code)`. Its `meta.yaml:25-27` records `escalations: [none, 🤖 Generated with …]`. It is the only Nanobot output with the footer (count from `grep -l`: 1).
- **#88, this repo too.** `.factory/store/runs/run-0538-implementer` (T-0054.1, 2026-10-19) has the same tail and the same two-item `escalations` list (`meta.yaml:23-25`). `log/2026-10.jsonl:2861` has the false event: `"event": "escalation.queued", "ticket": "T-0054.1", "run": "run-0538-implementer", "items": ["none", "🤖 Generated with …"]`. A third run is relevant. `run-0544-implementer` has `escalations: []`; its output does contain the footer string, but not after the trailer.
- **#88, cause in the parser.** `factory/status.py:43-49`: when lines follow the ESCALATIONS head, every line from the head on becomes an item, including a `none` head. This follows the operator's rule (b) of 2026-10-01.
- **#88, cause in the role process.** `factory/drive.py:105-112` builds the `claude -p` argv with no `--settings` argument. Claude Code's settings reference lists `attribution.pr` ("Change or hide the attribution line in pull request descriptions"), and `--settings` takes a JSON value for one session (https://code.claude.com/docs/en/settings, https://code.claude.com/docs/en/settings-reference). Both footer runs are implementers, whose output is a PR description.
- **#113.** The scenario is at `.factory/store/openspec/specs/build-dispatch/spec.md:694`: `where=$(case "$C" in $T/tmp/factory-launch-*/$s.js) echo own-dir;; *) echo none;; esac)`. I reproduced the failure with a minimal script of the same shape, kept in scratch at `scratch/case.sh`:
  - `/bin/sh` (GNU bash 3.2.57) prints `syntax error near unexpected token 'newline'` and `where= echo own-dir;; *) echo none;; esac)`.
  - `/bin/sh -n` exits 0, so a syntax check does not catch it.
  - zsh and Homebrew bash print `where=own-dir`.
  - With leading parentheses, `($T/a.js)` and `(*)`, `/bin/sh` prints `where=own-dir`.
- **#114.** `factory/setup.py:186` calls `(dest / src.name).read_bytes()` with no handling of a read error. The generic handler at `factory/cli.py:870-873` then exits 1. T-0052's verifier (`.factory/store/runs/run-0532*/output.md:30,37`) recorded the regression: on the base the same setup exits 0, and the verifier left treating the copy like the directory case to the operator. This request is that call.
- **#115.** `factory/cli.py:851-855`: the comment says `init`, `paths` and `stats` "skip the fence and the harness lock and ignore --accept-harness", and `main()` returns before `instance.guard(…, a.accept_harness)` at `:863`. `Refused` exits 2 (`:866-869`). The README section is at `README.md:596`. I did not re-run the Nanobot reproduction from 2026-10-19.

Capabilities: build-dispatch, store-setup, live-store-guard, harness-docs, harness-suite

Assumptions:
- **Inference: the footer's source.** I infer that the footer appears because the implementer's output is a PR description and Claude Code adds its PR attribution line. I have not verified that `attribution.pr` suppresses it in a `claude -p` reply. The request says to look the setting up before relying on it.
- **Inference: #88 fix choice.** The request leaves the fix to the spec: the drive setting, a parser change, or both. I treat that as a design choice to approve at the spec gate, not a product decision needed now. Either way, rule (b) must still hold for real item lines.
- **Inference: a parser fix also covers the Workflow-script path.** A drive-only setting would not cover the Workflow-script path (the older way of running the roles, beside the drive), so only a parser fix covers both. The request does not say whether that path needs covering.
- **Inference: #113 goes through a spec delta.** The #113 edit is to current truth in the store, which a ticket changes only through its spec delta and archive. I assume that is the intended route. The optional check that no current-truth scenario has an unparenthesised `case` inside `$( )` is the requester's suggestion, not a requirement.
- **Discrepancy: #114 output.** run-0532 says the unreadable-copy case printed "no JSON output", but the generic handler at `cli.py:870-873` prints an `ok: false` JSON object. The spec should reproduce the case and not rely on either description.
- **Suggestion: priority.** I suggest p1, because T-0059 (#120) is queued to run after this ticket's #113 fix (`dev/issues.md:122`, `requests/T-0059.md:23`). Priority is the operator's call.

Reason: The intent is clear for all four items. The request names what must not change: rule (b) for real item lines, the lock guard for other commands, and that init never overwrites a copy. The one choice it leaves open (#88's fix) is a design choice inside the spec. No open or recent ticket duplicates it: T-0058 is this ticket. T-0059 depends on it and does not cover it. No other ticket mentions #88, #113, #114 or #115.

STATUS: ACCEPT
CONFIDENCE: high. I reproduced #113 under `/bin/sh` and checked every code location and both stores' records on `main`. The one point I did not verify is whether `attribution.pr` suppresses the footer in a `claude -p` reply.
ESCALATIONS: none
