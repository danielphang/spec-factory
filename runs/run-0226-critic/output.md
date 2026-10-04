## Critic review: T-0025 spec v2 (store on its own branch, `factory-store`), round 2

### What I checked

Round 2 scope: my round-1 findings and the text that changed. All from `~/dev/spec-factory` on `main` at `3a3f58c` (unchanged since round 1; `git status` shows only uncommitted store files), with a throwaway HOME and `TMPDIR` set to this run's scratch directory.

- README scenario, as rewritten: prints `store_branch=0 migrate=0 old_cost=1 old_refs=4` today, matching verification.md. The four `old_refs` hits are README lines 403, 418, 457 and 462, the places design.md D now lists. The retired clause is wrapped across lines 306-307, so the writer's point against my suggested single-line grep stands; the `tr '\n' ' '` join is the right fix. The "Where it runs" diagram holds exactly two `state/` labels (lines 186, 191), as D says.
- Operator steps, step 1: the two upgrade commands match README "Upgrading the runtime" (`git -C ~/dev/spec-factory-harness checkout --detach <sha>`, `uv sync --frozen`). Read cold, the paragraph now says what the runtime is, why a merge does not change it, and what `--accept-harness` does. Step 3 glosses "Driver session" and names T-0001.1 as a sub-ticket.
- Risk bullet on T-0024: `run-0224-spec_writer/meta.yaml` is T-0024's second spec round; run-0220's output (its v1 spec) refuses unmarked writes to a live store while a run is in flight there and exempts only a fixed read-only list, so `init` and `store migrate` would fall under it as the bullet says. The standing decisions in `decisions.md` (the `FACTORY_DISPATCH=1` marker) agree.
- Acceptance commands re-run as written: "init refuses a once-tracked store path" prints `exit=0 instance=written names_path=0`; "init on a clone restores the store" prints `exit=1 branch=main restored=1`. Both match verification.md.
- Evidence prototypes, now inlined: I re-ran the orphan-worktree and `git clean -fdxq` claims in this run's scratch. `git worktree add --orphan -b factory-store` with no identity exits 0 and the excluded path leaves `git status --porcelain` empty; after `git clean -fdxq` the B1 store keeps `decisions.md` and the B2 directory is gone. Both match the Evidence paragraphs.

### Prior findings

- [BLOCKING] 6, Operator steps step 1, "the runtime" and `--accept-harness` unglossed → RESOLVED.
- [SHOULD-FIX] 2, README scenario `old_cost` forbids a phrase the new how-to needs → RESOLVED. The writer's evidence against my suggested grep is right (the clause is wrapped), and the join fixes it properly.
- [SHOULD-FIX] 2, changelog bullet in D lacks the literal words "never tracked" → RESOLVED.
- [NIT] 2, README scenario `old_path=0` forbids the old path anywhere → RESOLVED by narrowing to `old_refs`.

### Findings

[NIT] 2 specs/harness-docs/spec.md, scenario "The README describes the store branch and the move", `old_refs`
Problem: The alternative `at `.factory/state/`` still forbids the most natural phrasing in the new how-to and its rollback ("the store back at `.factory/state/`"), which D permits to name the old path.
Evidence: D's how-to bullet says it "may name the old path it moves from"; the regex matches that phrase wherever it appears; today's four hits do not include the how-to because it does not yet exist.
Suggested fix: Add one clause to D's how-to bullet saying the how-to writes the old path without a preceding "at", or names it as `.factory/state` with no trailing slash.

### Notes, not findings

- The relayed operator note calls this issue "45" and frames the choice as "worktree and/or branch". The spec's Responses already record that this request is GitHub #46 and #45 is T-0024's. The spec's B1 (worktree checkout of the branch) and B2 (branch with no working copy) are the operator's two readings of "worktree and/or branch", and B1 is left for the operator to confirm at the gate; option A is recorded as rejected for the operator's stated reason.
- No new issue on unchanged text.

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding is fixed as described, the rewritten scenario and both re-run acceptance commands print what verification.md says, and the inlined prototype claims reproduce.
ESCALATIONS: none
