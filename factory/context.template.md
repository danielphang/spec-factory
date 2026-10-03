## Context for this run (composed by the harness, not part of the request)

TODO: replace this stub with the briefing for this repository. `factory run compose` puts this file,
`.factory/context.md`, at the top of every role's input, so every agent, author and checker alike,
reads it first. A wrong briefing misleads all of them at once. State, in a few short paragraphs:

- Which repository this is: its name, where the checkout lives, the integration branch, and what it
  holds (code, documents, both).
- How to run things here: the install step, the test command, the lint command, and anything that
  must not be used. Acceptance commands must be runnable as written from the repo root.
- Any reference implementation or other checkout an agent may read, and what it must never write
  (credentials, live config, other repositories).
- What kind of request to expect, and what counts as requirement versus suggestion in it.
- How the build half works here: remote or local commits, what the gate commands are for, and
  files a gate run creates that must never be committed.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.
