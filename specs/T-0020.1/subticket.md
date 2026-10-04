## T-0020-S1 / Tripwire on listed live files (baseline, compare, park or escalate), workflow stop, documents and coding rule 6
Depends on: none
Parallel-safe: yes (the only sub-ticket; nothing runs beside it)

Parent: T-0020 approved spec v1 (issue #38). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts A (A1 to A5), B, C, D (D1 to D4), E and F of the parent's design.md. The whole parent.

Notes for the implementer, checked on `main` at `02465fa`:
- Fixtures. Most scenarios need the two fixture scripts that the GIVEN block of the parent's first scenario writes ("A changed park-listed file parks the ticket", in `specs/live-file-tripwire/spec.md`). Run that block once, verbatim, at column 0, before running any scenario. Run every command from the root of your worktree, after `uv sync --frozen`.
- Running tests. Run the suite and every probe under a throwaway `HOME`: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Never list a path under the real home that exists in a test or a probe.
- Part A1 resolves `~/` with `pwd.getpwuid(os.getuid()).pw_dir`, never `HOME`. The scenario "A file under a substitute HOME is not watched" fails if `HOME` is used.
- Part A3, `.gitignore`. `ensure_gitignore` (`factory/store.py` lines 52-60) appends the whole `STORE_GITIGNORE` block when any checked line is missing. With a third line in the list, an existing store `.gitignore` that has only the first two lines gets the two lines again, plus the new one. That is harmless. Appending only the missing lines is also within A3. Do not change what the two existing lines are.
- Part A4, the shared park helper. `ticket_park` is at `factory/cli.py` lines 173-185. Move its body into the helper and call the helper from both places, as A4 says. Keep `ticket_park`'s own refusal for a `closed` or `parked` ticket.
- Part C. The `if (!fin.ok) …` line is `factory/workflows/intake.js` line 108 and `factory/workflows/build.js` line 107. The ticket variable is `TICKET` in intake.js and `ticket` in build.js.
- Part D1. The commented `tripwire` example goes right after the `protected_paths:` block (template lines 12-13), before the `gate_commands` comment. Since T-0019, a real key, `run_env: {}`, sits at line 30. Leave it as it is.
- Part D2. The **What the harness itself owns** paragraph is still at `docs/design.md` line 52. It is prose, not a prompt block, so no `docs/prompts/` file changes.
- Part D3. The README anchors are on `main`: the "Instances and the harness lock" bullet (line 343), and the sentence ending "returns it." on lines 321-322 of the "Gap, as of today" paragraph.
- Part D4. Number the entry after the last numbered entry on `main` when you start. T-0019 added one. The entry goes before `Declined:`.
- Part E. Rule 4's sentence wraps: "A finding against" ends line 66 and "rule 2, 3 or 5 takes no tag" starts line 67. After the edit, keep `rule 2, 3, 5 or 6` on one line, or the rule-6 scenario's `grep -c 'rule 2, 3, 5 or 6'` prints `0`. `docs/coding.md` must still end with the two-line "The check order (rule 1) and …" paragraph.

Acceptance (each WHEN verbatim from the parent; run the fixture GIVEN block first):
- A changed park-listed file parks the ticket. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"token": "T20-SECRET-C"}\n' > $T20/live/policies.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; secrets)`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`, then `secrets=0`
- A park-listed file deleted or created during a run counts as changed. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && rm $T20/live/policies.json && echo '{}' > $T20/live/new.json && bin/factory run finish $R --output-file $T20/out.md >/dev/null 2>&1; show)`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage`
- A killed run is still compared. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; show)`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`
- A changed escalate-listed file is queued and the ticket still moves. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"chat": "T20-SECRET-D"}\n' > $T20/live/pairing.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; bin/factory log tail -n 1 --event escalation.queued > $T20/esc.out; python3 -c 'import json,sys; t=sys.stdin.read().strip(); print("items=%s" % (json.loads(t)["items"] if t else None))' < $T20/esc.out | sed "s|$T20|\$T20|g"; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null && echo moved=yes; secrets)`
  THEN it prints exactly `state=ready-for-triage reason=None`, then `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']`, then `moved=yes`, then `secrets=0`
- Unchanged listed files neither park nor escalate. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print("status=" + json.load(sys.stdin)["status"])'; show; echo "escalations=$(bin/factory log tail -n 100 --event escalation.queued | wc -l | tr -d ' ')")`
  THEN it prints exactly `status=ACCEPT`, then `state=ready-for-triage reason=None`, then `escalations=0`
- Clearing an abandoned run compares it; an unrelated set does not. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory ticket set T-0001 title=Renamed >/dev/null 2>&1; show; bin/factory ticket set T-0001 'in_flight=[]' >/dev/null 2>&1; show)`
  THEN it prints exactly `state=ready-for-triage reason=None`, then `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`
- A file under a substitute HOME is not watched. NEW.
  WHEN `(T20=$(mktemp -d); mkdir -p $T20/home; echo a > $T20/home/.t0020-probe; echo a > $T20/live.json; TRIPWIRE="tripwire: {park: [\"~/.t0020-probe\", $T20/live.json]}"; export HOME=$T20/home; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && echo b > $T20/home/.t0020-probe && echo b > $T20/live.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; bin/factory ticket show T-0001 --json | tail -1 | python3 -c 'import json,sys; t=json.load(sys.stdin); print("state=%s reason=%s" % (t["state"], (t["parked"] or {}).get("reason")))' | sed "s|$T20|\$T20|g")`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage`
- A directory in the list refuses run start. NEW.
  WHEN `(T20=$(mktemp -d); mkdir -p $T20/live; TRIPWIRE="tripwire: {park: [$T20/live]}"; . ${TMPDIR:-/tmp}/t0020-bare.sh && bin/factory run start --role triage --ticket T-0001 > $T20/start.out 2>&1; echo "exit=$? named=$(grep -q "$T20/live" $T20/start.out && echo yes || echo no) runs=$(ls $T20/store/runs 2>/dev/null | wc -l | tr -d ' ')")`
  THEN it prints exactly `exit=2 named=yes runs=0`
- The baseline digest is kept but not committable. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && H=$(printf '{"token": "T20-SECRET-A"}\n' | python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())') && echo "held=$(grep -rl $H $T20/store | wc -l | tr -d ' ')" && git -C $T20/store init -q && git -C $T20/store add -A && echo "committed=$(git -C $T20/store grep --cached -l $H | wc -l | tr -d ' ')")`
  THEN it prints exactly `held=1`, then `committed=0`
- No tripwire key, no new output or file. REGRESSION.
  WHEN `(TRIPWIRE=; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && printf 'Type: bug\nTitle: F\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' > $T20/out.md && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin)))'; ls $FACTORY_STATE/runs/$R | tr '\n' ' '; echo)`
  THEN it prints exactly `['confidence', 'escalations', 'ok', 'run_id', 'status']`, then `meta.yaml output.md system-prompt.txt ` (with the trailing space)
- The harness suite passes under a throwaway HOME. REGRESSION.
  WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
  THEN it exits 0 with no failures, including the new `tests/factory/test_tripwire.py`
- Both scripts check run finish for a park. NEW. This check is structural: the workflow scripts need the Claude Code Workflow runtime and cannot run in the verifier.
  WHEN `for f in factory/workflows/intake.js factory/workflows/build.js; do echo "$f $(awk '/^async function runRole/{f=1} f&&/^}/{f=0} f' $f | grep -c '\.parked')"; done`
  THEN each of the two lines ends in a number of 1 or more, and reading those lines shows a `return null` taken when the `run finish` answer carries `parked`
- Rule 6 is in the page's format and rule 4 names it. NEW.
  WHEN `awk '/^## 6\. /{f=1;print "heading=yes";next} /^## |^The check order/{f=0} f&&/^Check: /{c=1} f&&/^Principle: /{p=1} f&&/^Before /{b=1} f&&/^After: /{a=1} f&&/tmp_path/{t=1} f&&/store\.policy_store_path/{m=1} END{print "check="(c?"yes":"no"), "principle="(p?"yes":"no"), "before="(b?"yes":"no"), "after="(a?"yes":"no"), "tmp_path="(t?"yes":"no"), "module_attr="(m?"yes":"no")}' docs/coding.md; grep -c 'rule 2, 3, 5 or 6' docs/coding.md; tail -2 docs/coding.md | head -1 | cut -c1-28`
  THEN it prints exactly `heading=yes`, then `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes`, then `1`, then `The check order (rule 1) and`
- Design doc, template and README name the tripwire. NEW.
  WHEN `echo "design=$(grep -c '^\*\*Tripwire on live files\.\*\*' docs/design.md) template=$(grep -c 'tripwire' factory/instance.template.yaml) built=$(awk '/^\*\*Built\*\*/{f=1} /^\*\*Not built\*\*/{f=0} f' README.md | grep -ci 'tripwire') resume=$(grep -c 'A ticket the tripwire parked' README.md)"`
  THEN it prints `design=1`, `template=` a number of 1 or more, `built=` a number of 1 or more, and `resume=1`
- The changelog records the change in order. NEW.
  WHEN `awk '/^[0-9]+\. /{n++; split($0,a,"."); if (a[1]+0!=n) bad=1; last=$0} END{print "contiguous=" (bad?"no":"yes"), "last_names_tripwire=" (last ~ /tripwire/ ? "yes":"no")}' docs/changelog.md`
  THEN it prints exactly `contiguous=yes last_names_tripwire=yes`
- The change adds no whitespace errors. REGRESSION.
  WHEN `git diff --check main...HEAD`
  THEN it exits 0 with no output
- Intermediate check: only the files the parent declares change, and no existing test changes. NEW.
  WHEN `git diff --name-only main...HEAD | sort`
  THEN it prints exactly these 11 lines: `README.md`, `docs/changelog.md`, `docs/coding.md`, `docs/design.md`, `factory/cli.py`, `factory/instance.template.yaml`, `factory/store.py`, `factory/tripwire.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `tests/factory/test_tripwire.py`

Tests to change: none. New tests go in the new file `tests/factory/test_tripwire.py` (part F).

Protected paths: harness: `factory/tripwire.py` (new), `factory/cli.py`, `factory/store.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/instance.template.yaml`. That is the parent's whole Risk list. Guardrail path: `docs/coding.md` (part E asks for it).

Out of scope:
- Everything in the parent's Out of scope section. That includes watching directories, naming changed JSON keys, a new `resolve` mode, `dev/build-harness.spec.md`, the prompt blocks and `docs/prompts/**`.
- Either instance's own files: `.factory/**` here, and anything under `~/dev/nanobot-upstream`. Adding Nanobot's lists is the parent's Operator step 1, after merge.
- `~/.nanobot/**`: never read or write it, not even to test.
- A guard on leaving `parked` for every park, and documenting how to recover a run left in flight. Both are in the parent's out-of-scope observations.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v1 of T-0020 (issue #38), in this run's input and the T-0020 spec store.

One sub-ticket. The parent decides this itself ("One change, not split: about 300 lines, half of them the new test file"), and the parts cannot land apart without leaving `main` wrong. The workflow-script stop (part C) on its own reads a `parked` field that nothing writes. The baseline and comparison (parts A and B) on their own would park tickets that the workflow scripts then route out of `parked`, which is the silent undo the parent's Evidence describes. Rejected: a separate documents-and-rule-6 sub-ticket (parts D and E). It would describe a tripwire that does not exist yet, and splitting would make one more merge for the other in-flight work to re-verify, with no gain for review or rollback.

The parent's ordering condition holds. It asks for this to be built after T-0019 merges. T-0019 is the approved change that runs every role under a throwaway `HOME`. Both of its sub-tickets are merged on `main` (`02465fa`: T-0019.1 at `9853737`, T-0019.2 at `3d23560`). They changed `docs/design.md`, `docs/changelog.md`, `README.md` and `factory/instance.template.yaml`. I re-checked every anchor this change edits against `main` at `02465fa` (below). `factory/cli.py`, `factory/store.py` and both workflow scripts are unchanged since the spec's base `1c5f6a7`, so the parent's line numbers for them still hold.
