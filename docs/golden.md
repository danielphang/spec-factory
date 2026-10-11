# Golden set

The fixed set of past tickets that every replay runs. A replay is how a change to how roles think is
accepted (north star, rule 8; procedure in #80). This set replaces a fresh pick per ticket: the
three replays so far (#73/#74, #75, #76) each chose their own tickets, so their figures cannot be
compared. Chosen 2026-10-11, while the runtime was at `a4f90b6`, before any #96 prompt ticket.

## Rules

- Every replay runs every entry, with the same request, base and inputs. No fresh pick.
- A ticket joins or leaves the set only with a dated row under Changes to the set, giving the reason.
- An entry passes when the replay reproduces its known catch, as the entry states it. It must also
  not lose a verdict the original run reached.
- The baseline below is the current prompts and needs no blinding. Every later replay follows the
  blinding rules in #80.
- Replays run in a throwaway store (`FACTORY_STATE`), never in the live stores.

## Stores

- **SF:** spec-factory. Store `.factory/store` on branch `factory-store`; target repo
  `~/dev/spec-factory`, branch `main`.
- **NB:** Nanobot. Store `~/dev/nanobot-upstream/.factory/store`; target repo
  `~/dev/nanobot-upstream`, branch `feat/lionbot-v3.5`.

Neither store records an integration head per spec version. An intake's base is the SHA its spec v1
or critic cites, checked against `git rev-list -1 --first-parent --before=<triage time>`. A build's
base is the run's own `base` in `meta.yaml`.

A request that gained a `## Answer N` section after triage is replayed with that section cut, so
triage sees what the original triage saw.

## Entries

| # | Ticket | Store | Base | Request | Roles | Known catch to reproduce | Why it is here |
|---|---|---|---|---|---|---|---|
| 1 | T-0029 (#49), intake v1 | SF | `0b1abad474cb` | `requests/T-0029.md` | triage, spec writer, critic | run-0258-critic: `[BLOCKING] 6`, the unglossed "runtime", "instance" and `--accept-harness`; `[SHOULD-FIX] 1`, the retro's two counts (26 vs 38) | Replayed twice (#73, #74). Part of the only set where a prompt change is known to have stopped the critic verifying |
| 2 | T-0031 (#51), intake v1 | SF | `c2750bf9c18c` | `requests/T-0031.md` | triage, spec writer, critic | run-0279-critic `[SHOULD-FIX] 4`: Instance A's gate commands pin `UV_PYTHON_INSTALL_DIR` as well as `UV_CACHE_DIR`. Missed under #73's capped critic (`docs/changelog.md`) | A real environment risk, caught only by a critic that reads the instance |
| 3 | T-0033 (#57), intake v1 | SF | `d226a4d03ca9` | `requests/T-0033.md`, cut `## Answer 1` | triage, spec writer, critic | run-0316-critic `[SHOULD-FIX] 4`: a brace list such as `factory/prompts/{preamble,planner}.md` is not expanded by git. Proven by a scratch git test. Missed under #73 | A finding proven by experiment, not judgement |
| 4 | T-0032, intake | NB | `bab0dede7dca` | `requests/T-0032.md`, cut `## Answer 1` | triage, spec writer, critic | The spec keeps standing decision T-0003 (`decisions.md:5`): the sweep goes in `nanobot/agent/lionbot.py`, not a new module under `nanobot/cron/` (v2 D11, `specs/T-0032/v2.md:76`). The #75 replay broke it | The only recorded case of a cross-cutting decision lost to input filtering |
| 5 | T-0038 (#77), intake | SF | `51e2af7f1737` | `requests/T-0038.md` | triage, spec writer, critic | run-0350-critic, its only BLOCKING: `[BLOCKING] 6`, "the Nanobot target's T-0024" and "Nanobot's `factory-store`" unglossed, though `README.md:135,137` define them | The cleanest single rubric-6 case. Exercises #93 |
| 6 | T-0009, triage | NB | `e91864691b81` | `requests/T-0009.md` lines 1–219 (cut `## Answer 1` at 220) | triage | run-0059-triage NEEDS-HUMAN: under D23 a read-only sender could `read_file` other groups' raw logs in `workspace/chats/`. "Where should the log live on v3.5?" Options A, B (recommended), C. Operator chose B | A product and privacy choice the request never raised. Exercises #91 |
| 7 | T-0036.1 (#75.1), build | SF | `9a258097a5eb` (verifier head `15c9d2f6`) | `requests/T-0036.md` + its plan | implementer, verifier | run-0343-verifier VERIFIED, with the edge case: a triage `Capabilities:` line written `(beta, alpha)` or ending in `;` names no capability. Implementer yardstick: run-0341 wrote 20 tests | Half of the only implementer/verifier pair with a recorded replay (#76) |
| 8 | T-0038.1 (#77.1), build | SF | `f4ea04193e82` (verifier head `9aa97bf4`) | `requests/T-0038.md` + its plan | implementer, verifier | run-0359-verifier VERIFIED, with the edge case: a `planned_from` that is not an integer makes every plan-splitting command fail with a TypeError | The other half of that pair |
| 9 | T-0009.1, build | NB | implementer `67ad0cdd402c`; verifier base `931dde232680`, head `742e06ae3026` | `requests/T-0009.md`, spec v2 | verifier (implementer if the build is replayed) | run-0247-verifier FAILED: a neonize-scale timestamp `int(time.time()*1000)` gives `entries written: 0` and "year 58729 is out of range". The spec never names milliseconds | A verifier probing outside the spec's scenarios and catching a defect that would have broken production. Not `merge.base_before` (`cf0131ecb0f0`), which is after three rounds |

SHAs are abbreviated to 12 characters. Each resolves with `git cat-file -t` in its repo (checked
2026-10-11).

## Baseline

The set run once with the runtime prompts at `a4f90b6`, before #93 (#96 row 5) moves the runtime.
Measures per entry and role:
- calls and turns;
- tokens (input, cache read, output);
- suite runs;
- the verdict, and whether it changed an outcome;
- operator decisions asked for;
- whether the known catch was reproduced.

Not yet run.

| # | Role | Calls | Turns | Tokens | Suite runs | Verdict | Catch reproduced |
|---|---|---|---|---|---|---|---|

## Changes to the set

| Date | Change | Reason |
|---|---|---|
| 2026-10-11 | Set created: entries 1–9 | Operator instruction (via the Reviewer). Candidates from the retrospective. Entry 5 replaces "one rubric-6 REVISE ticket" with T-0038 because entries 1 and 4 already carry rubric 6. Entry 6 is NB T-0009 rather than NB T-0032 run-0267, because that request hands its choice to a human itself |
