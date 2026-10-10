Commit: 0e99ddad7eb10387369fac62286f8520fd6a1a67

## What I checked

Diff `18fbe88..0e99dda`, read in full. `git diff --stat` shows exactly the four files the sub-ticket names: `README.md` (+87/-?), `dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md`; 85 insertions, 17 deletions. `git diff --name-only` filtered to `docs/prompts tests factory bin agents .factory AGENTS.md pyproject.toml uv.lock` returns 0 paths.

1. Test integrity: no test file is touched. Nothing under `tests/`. Pass.
2. Correctness, claim by claim against the code and the store (the documents describe part A and B's build, so each as-built statement was checked):
   - The three `docs/design.md` edits are at lines 44, 64 and 874. An awk fence counter over the file reports all three `outside fence`, so no prompt block changed and `docs/prompts/` needs no re-copy (confirmed: no `docs/prompts/` path in the diff).
   - Acceptance line run in the worktree: `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`. Exactly the THEN line.
   - "Five pieces assume Claude Code": the table under "What depends on Claude Code" has 5 rows with `yes` (`grep -c '^| [^|]* | yes |'`). Correct.
   - "40 tickets and 47 sub-tickets": `ls .factory/store/tickets` counts 40 `T-NNNN.yaml` and 47 `T-NNNN.k.yaml`. Correct today. Runtime `639fcb5` (`git -C ~/dev/spec-factory-harness rev-parse --short HEAD`) and lock `da50576…` (`cat .factory/harness.lock`) match what the page quotes.
   - Changelog figures (2,236 agents, 4,476 calls, 143M of 866M) match the parent spec's Evidence line 14 (`specs/T-0040/v4.md`), which marks them "Not re-derived here". Entry 67 matches the acceptance regex and sits before "Declined:".
   - Edit rule scopes stated in R6, the README Built bullet and the changelog match `factory/drive.py:88-94`: `Edit(/<run>/output.md)`, `Edit(/<run>/scratch/**)`, `Edit(/<tmp>/**)`, plus `Edit(/<worktree>/**)` for the implementer. `--prompt-mode replace` → `--system-prompt-file` matches `drive.py:95`; `--effort` matches `drive.py:102`; the marker stripped from role processes matches `drive.py:197`; the status path `drive/<ticket>.yaml` matches `drive.py:132`; exit `128 + signal` matches `drive.py:539`.
   - design.md piece 2 says "no role process has a time limit": the only `timeout` in `drive.py` is `asyncio.wait(waits, timeout=KILL_AFTER_S)` at line 560, inside the stop sequence. Correct.
   - "nothing to dispatch from this state" matches `drive.py:271` and `:417`.
   - The Built bullet ends "It is tested, and has not yet run a real ticket." as the spec requires. R6 keeps "Never `bypassPermissions` (nor `dontAsk`)". Part H has one new paragraph. I.4 has the driver sentence. R3 names the driver.
3. Scope: the four unlisted README edits the implementer declares (directory tree lines, the fence bullet, the "Running on another agent host" sentence, "Related work and history") are each a sentence the change made stale, and C.1 says to follow "Maintaining this page", which requires exactly that ("updates the sentence that describes it"). In scope. No code, prompt or `.factory/` change.
4. Silent behaviour changes: none possible; documents only.
5. Security and data safety: nothing applicable.
6. Protected paths: none touched (0 paths in the filtered name list).
7. Coding standard: not applicable to prose.
8. PR description: What changed says in words what changed and why, glosses "clerk" and the Workflow-tool scripts at first use, and Known gaps names each judgement call with its reason. Readable at the gate.

## Findings

- [NIT] dev/build-harness.spec.md:118 (R6): "plus `Edit` rules, which also cover Write" is a claim about Claude Code's permission system that neither the parent spec's Decisions nor any evidence in the ticket states. I could not verify it in this run. It is also a parenthetical second idea in the sentence (writing standard rule 3). If it is wrong, a reader believes the checkers' `Write` tool is limited to the four scopes when it is not. Suggest dropping the aside, or stating it as its own sentence once verified. Not blocking: the spec itself relies on the same assumption ("The checkers therefore cannot use a file tool on the checkout").
- [NIT] README.md:1057-1058 ("Related work and history"): the new sentence was appended onto an existing wrapped line, making one ~190-character line in a paragraph otherwise wrapped at ~100. Harmless to render; mildly harder to diff. Re-wrap when the paragraph is next touched.

No BLOCKING or SHOULD-FIX findings. I would merge this into documents I own.

Prior findings: none (round 1).

Out-of-scope observations:
- The sub-ticket's "nine" scenarios versus the spec's ten is a count slip in the plan, as the implementer notes; nothing to change here.
- "Terms used on this page" does not define "driver"; the term is glossed at first use in "Starting a run" and in the Built bullet, so the page's own rule is met, but a one-line Terms entry would help a reader who lands on the Built list first. Not asked for by the spec.

STATUS: APPROVE
CONFIDENCE: high, the diff touches only the four named documents, every as-built claim I checked matches `factory/drive.py`, the store and the runtime, and the acceptance command printed its exact THEN line on this head
ESCALATIONS: none
