Commit: 67b61a587546e8a45349e91c13c00c3daa8346fe (branch `factory/T-0030.3`, base `d226a4d03ca94bab45bd4221972285a4d16ee0bb`)

## Review

Round 1. I read the full diff (`factory/compose.py`, 45 lines changed; `tests/factory/test_role_inputs.py`, new, 197 lines), the sub-ticket, the parent spec v2, and the surrounding code in the worktree. I did not run the suite or the gate commands.

**1. Test integrity.** No existing test file is changed (`git diff --stat d226a4d...67b61a5` lists only `factory/compose.py` and the new `tests/factory/test_role_inputs.py`). The four new tests assert specific headings, marker lines, label lines, context-line counts and `input_sources`; none is weakened or hard-coded to output. Clean.

**2. Correctness.**
- C1, `without_evidence` (`factory/compose.py:94-104`): walks `specstore.lines_outside_fences`, starts cutting at an unfenced line whose `rstrip()` is `## Evidence` or `## Responses`, stops at the next unfenced line starting `## ` or `=== `. I probed it in the worktree under a throwaway HOME (`PYTHONPATH=. uv run --frozen python ../scratch/probe.py`): a `## Responses` section ending at `=== specs/x.md` keeps the part line and everything after (`'## Acceptance\nA\n=== specs/x.md\n## ADDED\nS\n'`); a `### ` sub-heading inside Evidence stays cut (covered by the unit test); a fenced `## Evidence` is text. Matches C1 and the design's rule.
- C2 (`compose.py:157-160`, call sites `228`, `267`, `282`, `285`): all four places the sub-ticket names now go through `add_spec`. The heading keeps its words, including `verify every scenario on main`, and appends `. Its Evidence and Responses sections are left out; the full spec is \`<root/rel>\``. `root` is the store root from `store.state_root` (`FACTORY_STATE` or the instance's `state_dir`), the same path the acceptance scenario greps. `input_sources` is unchanged because `add()` still appends `rel` (`compose.py:156`). `subticket.md` stays on plain `add()` (`compose.py:266`, `284`).
- C3 (`compose.py:211-221`): `difflib.unified_diff(prev.splitlines(), cur.splitlines(), prev_rel, cur_rel, n=3, lineterm="")`, byte comparison `len(diff.encode()) < len(prev.encode())`, heading names which one the input holds, `input_sources` still records `v<n-1>`. When `v<n-1>` does not exist, the diff of `""` is never shorter than 0 bytes, so it falls to the whole-version branch, whose `add()` finds no file and adds nothing: today's behaviour.
- C4: the critic's `Spec under review` (`compose.py:203`), triage, spec writer and every other `add()` call pass two arguments and take the identity `edit`. Unchanged.
- Edge the spec implies: an unclosed fence inside Evidence hides every later line from the four roles (probe: `'## Problem\nP\n'` from a text whose Evidence opens a fence that never closes). The implementer declares this under Known gaps, it is the shared fence reader's rule, and the spec store has the same exposure. Not a finding against this change; see Out-of-scope observations.

**3. Scope.** Only `factory/compose.py` and one new test file. The `edit` parameter on `add()` is the means to C2, not new behaviour. In scope.

**4. Silent behaviour changes.** The four downstream inputs lose two sections and gain a heading suffix, as the spec asks. Round-2 critic headings change wording in both branches; `tests/factory/test_p0_cli.py:170` and `test_shepherd.py:123-124` assert content and sources, not the heading, so they stay valid (the implementer reports 364 passed; the verifier confirms). One small one below (NIT).

**5. Security and data safety.** Reads store files it already read; no new paths, no shell, no secrets.

**6. Protected paths.** `factory/compose.py` is harness, declared in the sub-ticket and the parent spec's Risk. Listed under ESCALATIONS; the merge gate needs a human approval.

**7. Coding standard.** `without_evidence` sits on rung 1: it reuses `specstore.lines_outside_fences` instead of a second fence parser. `add_spec` has four uses; `edit` has two distinct values. The test's subprocess helper mirrors `test_store_migrate.py`, which also reaches the harness package by subprocess because `tests/factory` imports as a top-level `factory` package. No `factory:` marker needed. Lean already.

**8. PR description.** What changed leads with who stops receiving what and why, glosses critic, round 2, parent-close verifier and `input_sources` at first use, and names `compose()`'s single caller for rule 2. Known gaps are honest and specific. Acceptance results give each printed line and what it shows. No finding.

## Findings

- [NIT] factory/compose.py:217: when `v<n>` is byte-identical to `v<n-1>` (`spec add` does not refuse a repeat; grep of `factory/cli.py` and `factory/specstore.py` finds no such check), the diff is empty, 0 bytes is less than the version, and the critic gets the heading `Previous spec version (v<n-1>), as a unified diff to v<n>` over an empty body → the critic may read it as a composition fault rather than "nothing changed". A one-line body such as `(no differences)` when `diff` is empty would say so. Not required by the spec.

net: Lean already.

Prior findings: none (round 1).

## Out-of-scope observations

- An unclosed code fence inside any spec section makes `specstore.lines_outside_fences` treat the rest of the file as fenced. The spec store's part and requirement parsing already has that exposure, and this change inherits it for the section cut. A fence-balance check at `spec add` would close both at once. Not this sub-ticket's.
- `v1.md`/`v2.md` are compared with `splitlines()`, so a CRLF spec would reach the four roles with LF endings. No stored spec has CRLF; noting it only because it is a byte-level difference from today's raw `add()`.
- A mis-nested heredoc in my own probe ran `uv run` once in the worktree and created its `.venv`. It is gitignored (`git status --short` is empty) and the verifier's `uv sync --frozen` uses it; no tracked file changed.

STATUS: APPROVE
CONFIDENCE: high, every lettered part is at the named call sites, the helper behaves as the design states on the edges I probed, no existing test is touched, and the one finding is cosmetic.
ESCALATIONS: protected path touched, declared in the sub-ticket: harness `factory/compose.py`. The merge gate needs a human approval for it; the code earns APPROVE.
