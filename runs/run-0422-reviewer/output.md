Commit: 654f523b997af69c9896cb06bdd9ac36fc04469c (branch `factory/T-0041.1`, base `cce3d6f43a2126c54141f67c377ac92b908880d6`)

## Checks, in the prescribed order

1. **Test integrity.** One existing test file changed: `tests/factory/test_resolve_rulings.py`, lines 126-127. Only the refusal-text assertion changed, to Decision 4's text; the exit code, state and "no ruling written" assertions and the parametrized cases stay. The parent's Tests to change lists exactly this test. No test weakened, skipped or deleted. `tests/factory/test_drift_siblings.py` is new. Not blocking.
2. **Correctness.**
   - Part A (`factory/cli.py:341-347`): the skip set is `merge.main_after` of every `status == merged` sub-ticket from `store.subtickets_of`, which globs `tickets/<parent>.*.yaml` (`factory/store.py:230-237`), so sub-tickets of earlier plans are included (Decision 1). The walk skips only a commit equal to one of those ids, before diffing it; merge commits in general are still diffed (Decision 2). `factory merge` records `main_after` from `gitops.merge_no_ff`, which returns `rev(repo, into)`, a full `rev-parse` id (`factory/gitops.py`), so the exact-match comparison against `rev-list` output holds for every harness-made merge. The set comprehension's condition runs before its expression, so `s["merge"]["main_after"]` is reached only when `merge` and `main_after` exist. A later direct commit to the sibling's own test is still found and named: `last[f] = c` is written for every non-skipped commit, so the refusal names the later commit, as the `greet` case pins.
   - Part B (`factory/cli.py:1189-1207`): `start_bug` requires both the `harness-bug: run start implementer:` prefix and `parked["from"] == "ready-for-implementer"`. `store.park` records `from` as the state at the time of the park (`factory/store.py:154`); `factory/drive.py:186` and `factory/workflows/build.js:84` park with that prefix from the implementer's ready state, so a real start failure matches. A `start_bug` park takes the `BLOCKED` route (`to = "ready-for-implementer"`, ruling file written, round untouched by `move`). `run compose` failures and checkers' start failures have a different prefix or `from`, so they stay refused, as the parametrized refusal test pins. The `use --answer` refusal is checked before the new text and is unchanged.
   - Part D: the design doc, build spec, README and changelog edits say what the code does, and nothing more. Changelog entry 68 is contiguous after 67. `git diff --name-only cce3d6f...654f523 -- docs/prompts factory/prompts` prints 0 lines: no prompt copy changed.
3. **Scope.** Seven files, all within parts A-D. No change to `factory/drive.py`, the Workflow scripts, prompts or `_check_sibling_tests`.
4. **Silent behaviour changes.** One, intended and spec'd: the `--ruling` refusal text changes for every refused park, which is why `test_resolve_rulings.py` is on the Tests to change list. Nothing else a caller would notice.
5. **Security and data safety.** None: no new paths, no shell, no destructive operation. The ruling route widens a human-only command on a park the human has already read.
6. **Protected paths.** `factory/cli.py` changed; the parent's Risk section declares it. Listed under ESCALATIONS for the record.
7. **Coding standard.** Rule 1: nothing new beyond one set and one `continue`; the test file reuses `test_spec_amend`'s fixture and `test_spec_drift`'s helpers rather than its own. Rule 2: `_test_drift` has one caller, `_check_drift`; `resolve` is the CLI entry. Rule 5: names (`main_after`, `ruling`, `parked`) are the store's existing names. Rule 6: no path outside the repository. Lean already.
8. **PR description.** What changed and Known gaps are in words, gloss "sibling" and the park at first use, and the acceptance outputs are each followed by what they mean. Two rule-3 and rule-2 formalities are missing; see the NITs.

I ran `git diff --check cce3d6f...654f523` in the worktree: exit 0, no output.

## Findings

- [NIT] PR description: Known gaps: coding rule 3 asks the Known gaps to say "factory: markers added: none" when the diff adds no `factory:` marker; it says nothing → a gate reader cannot tell "none added" from "not checked". One line fixes it.
- [NIT] PR description: What changed: coding rule 2 asks the description to name the callers of each existing function the diff changes; `_test_drift`'s one caller (`_check_drift`) and `resolve`'s entry point are not named → the reader re-derives them. Not a correctness concern: I confirmed the callers by grep.
- [NIT] factory/cli.py:341-342: the condition guards `merge` with `(s.get("merge") or {})` while the expression indexes `s["merge"]["main_after"]` directly → correct today because the condition runs first, but a reader has to work that out; `(s.get("merge") or {})["main_after"]` or a plain `s["merge"]["main_after"]` in both places reads as one rule.

No BLOCKING or SHOULD-FIX findings.

## Prior findings

None: round 1.

## Out-of-scope observations

- README's Built section now describes the sibling-merge exception in the present tense while saying it "has not yet run on a real ticket". The spec's part D requires the sentence and the implementer flagged the tension in Known gaps; "Maintaining this page" would otherwise place untried behaviour under "Where this can go". A one-line note at the next README edit, once the exception has run live, closes it.
- The implementer's own observation stands: the preceding README bullet, on tests a sibling added, still says "has not yet fired on a real ticket", unchecked by this ticket.

STATUS: APPROVE
CONFIDENCE: high. I read every hunk against the spec's Decisions 1-4, confirmed by grep in the worktree that `park` records `from`, that `merge_no_ff` returns full commit ids, that `subtickets_of` spans every plan, and that no prompt copy changed; the one existing test changed is the one the spec lists.
ESCALATIONS: protected path `factory/cli.py` changed, declared in the parent spec's Risk section (for the record; no action needed).
