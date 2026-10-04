## Proposed change

Both scripts get the same small helper. The Workflow tool runs a script as one function body with no imports, so the helper is copied into each script, as `clerk()` already is.

A. Title helper (both scripts). Add, next to `stubCount`:
- `TITLES`, an object mapping a ticket id to its short title;
- `shortTitle(t)`, the rule in proposal.md Decisions: collapse whitespace, keep ≤ 60 whole, else cut at the last space at or before index 60 (`lastIndexOf(' ', 60)`; at 60 when there is none), strip trailing `[\s,;:·—-]+`, append `…` (U+2026);
- `tag(id)`, which returns `` `${id} · ${TITLES[id]}` `` (U+00B7) when `TITLES[id]` is non-empty, else `id`.

Fill `TITLES[TICKET] = shortTitle(show.title)` right after the parent's `ticket show --json` (intake.js:128, build.js:200). In build.js `buildOne`, set `TITLES[st] = shortTitle(show.title)` right after `if (!show.ok) return`.

B. Start line (both scripts). Right after A's parent fill, print `log(TITLES[TICKET] ? `${TICKET} · ${TITLES[TICKET]} · ${state}` : `${TICKET} · ${state}`)`. It must come before any phase starts, so that it is the first narrator line.

C. Labels.
- Role rows: `` `${role} ${tag(TICKET)}` `` and `` `${role} (stub) ${tag(TICKET)}` `` in intake.js. Use `tag(ticket)` in build.js.
- Clerk rows: the label becomes `` `clerk ${tag(ticket)}: ${label}` ``. In intake.js the ticket is always `TICKET`. In build.js, give `clerk()` a fourth parameter `ticket = TICKET`. Pass the sub-ticket (`ticket` in `runRole`, `park` and `transition`; `st` in `buildOne`) on every call that acts on one, including the stub-script call at build.js:102. Calls on the parent (`config`, `ticket show`, `ready-implementers`, `spec tasks`, `plan add`, `subticket add`, `parent-check`, `archive`) keep the default.
- Action text: drop the ticket id now carried by the tag: `park ${ticket}` → `park`, `run start ${role} ${ticket}` → `run start ${role}`, `ticket show ${st}` → `ticket show`, `ticket head ${st}` → `ticket head`, `results show ${st}` → `results show`, `join ${st}…` → `join…`, `merge ${st}` → `merge`. build.js's transition label `${ticket} -> ${to}` → `transition -> ${to}`, as intake.js has it. Every other action text stays as it is.

D. Narrator lines.
- `transition()` (both scripts) awaits the clerk reply. When `res.ok`, it prints `` `${tag(ticket)}: → ${to}` `` (U+2192; `TICKET` in intake.js), then returns the reply unchanged. Callers are not edited. Awaiting inside `transition()` changes no command order: every caller already awaits its result before the next clerk call.
- Each existing `log()` call that names a ticket starts with `` `${tag(<that ticket>)}: ` `` and keeps the rest of its text:
  - park: `<tag>: parked: <reason>`;
  - a tripwire park: `<tag>: parked: <fin.parked>`;
  - a role's result: `<tag>: <role> <runId>: <status>` plus intake's escalation count, with build.js's ` (<ticket>)` dropped;
  - join: `<tag>: join: <decision> (<reason>)`;
  - merge: `<tag>: merged: <main_after>`;
  - spec approved, sub-tickets created, sub-tickets parked or waiting, resuming, and reuse lines: tagged with the parent.

E. Nothing else. Add no new clerk call, branch or reordering of calls, so the command order stays the same; the REGRESSION scenario checks it. Make no change to the CLI, prompts, agents, tests, README, design doc or changelog.

## Tests to change

none. No test under `tests/factory/` runs the workflow scripts or reads their labels. `tests/factory/test_shepherd.py:9-11` says they cannot run under pytest.

