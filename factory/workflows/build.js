export const meta = {
  name: 'factory-build',
  description: 'Spec factory build: Planner -> sub-tickets -> Implementer -> Reviewer + Verifier -> merge gate -> parent-close verify -> archive, for one approved parent ticket',
  phases: [
    { title: 'Plan', detail: 'planner decomposes the pinned spec into sub-tickets' },
    { title: 'Build', detail: 'per sub-ticket: implementer, then reviewer and verifier in parallel on the same head, then the merge gate' },
    { title: 'Close', detail: 'one verifier run on the integration branch against the parent spec; VERIFIED archives, then closes' },
  ],
}
// args: { ticket, repo, instance?, state?, target?, integration?, stubs?, inlineRoles? }  — repo/instance/state/stubs/inlineRoles as in intake.js.
// Local-commit stand-in (operator, 2026-10-02): no remote, no CI. The gate suite is run by the
// verifier and recorded as the ci row; the merge is a local --no-ff merge into the integration
// branch. The routing is build spec part H, build.js; the join itself is `factory ticket join`.

const TICKET = args.ticket
const REPO = args.repo
const INSTANCE = args.instance
let STATE = args.state || null  // set from `factory config` below when not given
// target = the repo the implementer works in (default: the instance's repo, the parent of its `.factory/`);
// integration = the branch merged into (default: config integration_branch, else the target's current branch).
const ENV = ['FACTORY_DISPATCH=1', INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : '',
  args.target ? `FACTORY_REPO=${args.target}` : '', args.integration ? `FACTORY_INTEGRATION_BRANCH=${args.integration}` : ''].filter(Boolean).join(' ')
const BIN = `${ENV ? ENV + ' ' : ''}${REPO}/bin/factory`
const PREFIX = args.agentPrefix || 'factory-'
const INLINE = !!args.inlineRoles
const CLERK_RULES = 'You are the store clerk of the spec factory: run the one command you are given, once, unchanged, from the repository root; run nothing else, edit nothing, interpret nothing. '
const AGENT_NAME = { planner: 'planner', implementer: 'implementer', reviewer: 'reviewer', verifier: 'verifier' }
const CLERK_SCHEMA = {
  type: 'object',
  properties: {
    stdout: { type: 'string', description: 'the command\'s stdout, verbatim, unmodified' },
    exit: { type: 'integer', description: 'the command\'s exit code' },
    stderr: { type: 'string', description: 'the command\'s stderr, verbatim' },
  },
  required: ['stdout', 'exit', 'stderr'],
}
let MODELS = { clerk: 'haiku' }
let MAX_PR = 2
const stubCount = {}

async function clerk(cmd, phase, label) {
  const res = await agent(
    (INLINE ? CLERK_RULES : '') + `Run exactly this one shell command from the repository root ${REPO} and nothing else:\n\n${cmd}\n\n` +
    `Report its stdout verbatim (do not reformat, summarize or re-encode it), its exit code, and its stderr verbatim.`,
    { agentType: INLINE ? 'general-purpose' : `${PREFIX}clerk`, model: MODELS.clerk, effort: 'low', phase, label: `clerk: ${label}`, schema: CLERK_SCHEMA })
  if (res === null) return { ok: false, exit: -1, stderr: 'clerk returned nothing' }
  const lines = String(res.stdout || '').trim().split('\n').filter(l => l.trim())
  let parsed = null
  for (let i = lines.length - 1; i >= 0 && parsed === null; i--) {
    try { parsed = JSON.parse(lines[i]) } catch (e) { parsed = null }
  }
  if (parsed === null) return { ok: false, exit: res.exit, stderr: res.stderr || `exit ${res.exit}, no JSON on stdout`, stdout: res.stdout || '', error: 'no JSON on stdout' }
  if (res.exit !== 0 && parsed.ok !== false) parsed.ok = false
  if (!parsed.stderr && res.stderr) parsed.stderr = res.stderr
  // A refusal prints its error as JSON on stdout too: a park reason built from stderr never ends blank.
  if (parsed.ok === false && !parsed.stderr) parsed.stderr = parsed.error || `exit ${res.exit}, no error text`
  return parsed
}

async function park(ticket, reason, outputs, phase) {
  const outs = outputs && outputs.length ? ` --outputs ${outputs.join(',')}` : ''
  await clerk(`${BIN} ticket park ${ticket} --reason "${reason.replace(/"/g, "'")}"${outs}`, phase, `park ${ticket}`)
  log(`${ticket} parked: ${reason}`)
}

// An EMPTY-OUTPUT run is re-dispatched once, same role, same inputs; a second in a row parks the ticket
// with both runs. The agent call reports no reason a run stopped, so neither is a budget kill.
async function runRole(role, ticket, phase) {
  const first = await runOnce(role, ticket, phase)
  if (!first || first.status !== 'EMPTY-OUTPUT') return first
  log(`${role} ${first.runId} (${ticket}): EMPTY-OUTPUT; re-dispatching ${role} once`)
  const second = await runOnce(role, ticket, phase)
  if (!second || second.status !== 'EMPTY-OUTPUT') return second
  await park(ticket, `EMPTY-OUTPUT from ${role}`, [first.runId, second.runId], phase)
  return null
}

async function runOnce(role, ticket, phase) {
  const start = await clerk(`${BIN} run start --role ${role} --ticket ${ticket} --model ${MODELS[role]}`, phase, `run start ${role} ${ticket}`)
  if (!start.ok) {
    // A refusal that starts `BLOCKED ` is the harness blocking the run (the sibling-tests check): park
    // with it verbatim, so `resolve --ruling` treats it as an implementer's BLOCKED.
    const blocked = typeof start.error === 'string' && start.error.startsWith('BLOCKED ')
    await park(ticket, blocked ? start.error : `harness-bug: run start ${role}: ${start.stderr || ''}`, [], phase); return null
  }
  const runId = start.run_id
  const comp = await clerk(`${BIN} run compose ${runId}`, phase, `run compose ${role}`)
  if (!comp.ok) { await park(ticket, `harness-bug: run compose ${role}: ${comp.stderr || ''}`, [runId], phase); return null }
  const outputPath = `${STATE}/runs/${runId}/output.md`
  let out
  try {
    if (args.stubs) {
      stubCount[role] = (stubCount[role] || 0) + 1
      out = await agent(
        `Stub file: ${args.stubs}/${role}-${stubCount[role]}.md\nOutput file: ${outputPath}\n` +
        `If the stub file exists, write its content verbatim to the output file and return that content. ` +
        `If it does not exist, write nothing and return an empty message.` +
        (INLINE ? ' You are a test stub: do exactly this and nothing else; run no other command.' : ''),
        { agentType: INLINE ? 'general-purpose' : `${PREFIX}stub`, model: 'haiku', effort: 'low', phase, label: `${role} (stub) ${ticket}` })
    } else {
      out = await agent(
        (INLINE ? `First read ${STATE}/runs/${runId}/system-prompt.txt: it is your role and your rules for this run; follow it exactly, including the preamble at its top. ` : '') +
        `Your entire input is the file ${STATE}/runs/${runId}/input.md; read it first and follow it. ` +
        `Write your complete output to ${outputPath} and return the same text.`,
        { agentType: INLINE ? 'general-purpose' : `${PREFIX}${AGENT_NAME[role]}`, model: MODELS[role], phase, label: `${role} ${ticket}` })
    }
  } catch (e) {
    // A thrown call (e.g. an agent type that is not installed) gives no result: record the run as
    // killed and park with the error, so no run is left in flight. parallel() would otherwise absorb it.
    await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (agent call failed)`)
    if (role === 'reviewer' || role === 'verifier') await clerk(`${BIN} run cleanup ${runId}`, phase, `run cleanup ${role}`)
    await park(ticket, `agent call failed: ${role}: ${e && e.message ? e.message : e}`, [runId], phase)
    return null
  }
  // Stub seam for the build half: `<role>-<n>.sh` beside the stub, run in the run's worktree, lets a stub
  // implementer make its commit (or merge the integration branch on a conflict run).
  if (args.stubs && role === 'implementer' && start.worktree) {
    const sh = `${args.stubs}/${role}-${stubCount[role]}.sh`
    await clerk(`if [ -f ${sh} ]; then (cd ${start.worktree} && sh ${sh}) >/dev/null 2>&1; fi; echo '{"ok": true}'`, phase, `stub script ${role}-${stubCount[role]}`)
  }
  // run finish reads the output file for every run: a missing or blank one is EMPTY-OUTPUT.
  const fin = await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
  if (role === 'reviewer' || role === 'verifier') await clerk(`${BIN} run cleanup ${runId}`, phase, `run cleanup ${role}`)
  if (!fin.ok) { await park(ticket, `harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
  // run finish parked the ticket (the tripwire saw a listed live file change): stop, do not route on STATUS
  if (fin.parked) { log(`${ticket} parked: ${fin.parked}`); return null }
  // An EMPTY-OUTPUT run keeps the agent's last message, so a human can see why it stopped. A failure
  // here never parks and never changes the route.
  const said = typeof out === 'string' ? out.trim() : ''
  if (fin.status === 'EMPTY-OUTPUT' && said) {
    await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
  }
  log(`${role} ${runId} (${ticket}): ${fin.status}`)
  return { runId, status: fin.status, outputPath }
}

async function transition(ticket, to, roundOp, phase) {
  const r = roundOp ? ` --round ${roundOp}` : ''
  return clerk(`${BIN} ticket transition ${ticket} --to ${to} --by workflow${r}`, phase, `${ticket} -> ${to}`)
}

// --- one sub-ticket through the PR loop (build spec H.3). The routing decision after the checkers
// is `factory ticket join`: the store reads the results table for the current head and says
// merge | revise | conflict | wait | park. This script only carries the decision out.
async function buildOne(st) {
  while (true) {
    const show = await clerk(`${BIN} ticket show ${st} --json`, 'Build', `ticket show ${st}`)
    if (!show.ok) return
    const implemented = show.state === 'ready-for-implementer'
    if (implemented) {
      const impl = await runRole('implementer', st, 'Build')
      if (!impl) return
      if (impl.status === 'BLOCKED') { await park(st, 'BLOCKED from implementer', [impl.runId], 'Build'); return }
      if (impl.status !== 'READY-FOR-REVIEW') { await park(st, `harness-bug: unknown STATUS ${impl.status} from implementer`, [impl.runId], 'Build'); return }
      const moved = await clerk(`${BIN} ticket head ${st}`, 'Build', `ticket head ${st}`)
      if (!moved.ok) { await park(st, `harness-bug: ticket head: ${moved.stderr || ''}`, [impl.runId], 'Build'); return }
      if (moved.merge_refused) {
        // A conflict run that did not merge the integration branch in: no point checking that head.
        const j = await clerk(`${BIN} ticket join ${st}`, 'Build', `join ${st} (conflict run)`)
        if (j.ok && j.decision === 'conflict') continue
        await park(st, j.ok ? j.reason : `harness-bug: join: ${j.stderr || ''}`, [impl.runId], 'Build'); return
      }
      const tr = await transition(st, 'checks-in-flight', 'pr:init', 'Build')
      if (!tr.ok) { await park(st, `harness-bug: transition to checks: ${tr.stderr || ''}`, [impl.runId], 'Build'); return }
    } else if (show.state !== 'checks-in-flight') {
      return  // parked, merged, closed or waiting: nothing for this loop to do
    }
    // The checkers on the same head, fresh contexts, in parallel; each result recorded against that head.
    // After an implementer run both run. Entered at checks-in-flight (a redispatch or a resumed
    // sub-ticket), only the checkers with no row on this head run; the verifier writes the ci row too.
    const headNow = await clerk(`${BIN} ticket head ${st}`, 'Build', `ticket head ${st}`)
    const sha = headNow.ok ? headNow.head : null
    if (!sha || !/^[0-9a-f]{40}$/.test(sha)) { await park(st, `harness-bug: no head for the checkers: ${headNow.stderr || ''}`, [], 'Build'); return }
    let roles = ['reviewer', 'verifier']
    if (!implemented) {
      const rows = await clerk(`${BIN} results show ${st}`, 'Build', `results show ${st}`)
      if (!rows.ok) { await park(st, `harness-bug: results show: ${rows.stderr || ''}`, [], 'Build'); return }
      const missing = rows.missing || []
      roles = roles.filter(role => missing.includes(role) || (role === 'verifier' && missing.includes('ci')))
    }
    const checked = await parallel(roles.map(role => async () => {
      const r = await runRole(role, st, 'Build')
      if (!r) return null
      const rec = await clerk(`${BIN} results record ${st} --head ${sha} --role ${role} --output ${r.outputPath} --run ${r.runId}${r.status === 'KILLED' ? ' --killed' : ''}`, 'Build', `results record ${role}`)
      if (!rec.ok) { await park(st, `harness-bug: results record ${role}: ${rec.stderr || ''}`, [r.runId], 'Build'); return null }
      return r
    }))
    if (checked.some(r => !r)) return
    const outs = checked.map(r => r.runId)
    const join = await clerk(`${BIN} ticket join ${st}`, 'Build', `join ${st}`)
    if (!join.ok) { await park(st, `harness-bug: join: ${join.stderr || ''}`, outs, 'Build'); return }
    log(`${st} join: ${join.decision} (${join.reason})`)
    if (join.decision === 'merge') {
      await transition(st, 'ready-for-merge', null, 'Build')
      const m = await clerk(`${BIN} merge ${st}`, 'Build', `merge ${st}`)
      if (m.ok) { log(`${st} merged: ${m.main_after}`); return }
      // The gate refused. Ask the join again: a moved integration branch is a conflict run, bounded there.
      const again = await clerk(`${BIN} ticket join ${st}`, 'Build', `join ${st} after refusal`)
      if (again.ok && again.decision === 'conflict') { await transition(st, 'ready-for-implementer', null, 'Build'); continue }
      await park(st, again.ok && again.decision === 'park' ? again.reason : `harness-bug: merge: ${m.stderr || ''}`, outs, 'Build'); return
    }
    if (join.decision === 'revise') {
      const tr = await transition(st, 'ready-for-implementer', join.round_op, 'Build')
      if (!tr.ok) { await park(st, `harness-bug: round increment refused: ${tr.stderr || ''}`, outs, 'Build'); return }
      continue
    }
    if (join.decision === 'conflict') { await transition(st, 'ready-for-implementer', null, 'Build'); continue }
    // 'park', or 'wait' (a row is missing after both checkers reported: a harness bug, not a red round)
    await park(st, join.decision === 'wait' ? `harness-bug: ${join.reason}` : join.reason, outs, 'Build')
    return
  }
}

// --- start
const cfg = await clerk(`${BIN} config`, 'Plan', 'config')
if (cfg.ok) { MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr; if (!STATE) STATE = cfg.state_dir }
if (!STATE) return { ticket: TICKET, error: `no store: factory config failed: ${cfg.stderr || cfg.error || ''}` }
const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Plan', 'ticket show')
if (!show.ok) return { ticket: TICKET, error: `no such ticket: ${show.stderr}` }
let state = show.state

// --- phase 1: Plan (only when the parent is ready-for-planner)
if (state === 'ready-for-planner') {
  phase('Plan')
  // A spec that needs one sub-ticket becomes it without a planner run; the harness decides which.
  const whole = await clerk(`${BIN} plan whole-spec ${TICKET}`, 'Plan', 'plan whole-spec')
  if (!whole.ok) { await park(TICKET, `harness-bug: plan whole-spec: ${whole.stderr || ''}`, [], 'Plan'); return { ticket: TICKET, state: 'parked' } }
  if (whole.planner === 'skipped') {
    log(`${TICKET}: planner skipped (${whole.reason}); one sub-ticket from the whole spec`)
  } else {
    const p = await runRole('planner', TICKET, 'Plan')
    if (!p) return { ticket: TICKET, state: 'parked' }
    if (p.status === 'ESCALATE') { await park(TICKET, 'ESCALATE from planner', [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
    if (p.status !== 'PLANNED') { await park(TICKET, `harness-bug: unknown STATUS ${p.status} from planner`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
    const tasks = await clerk(`${BIN} spec tasks ${TICKET} --run ${p.runId}`, 'Plan', 'spec tasks')
    if (!tasks.ok) { await park(TICKET, `harness-bug: spec tasks: ${tasks.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
    const added = await clerk(`${BIN} plan add ${TICKET} --from-run ${p.runId}`, 'Plan', 'plan add')
    if (!added.ok) { await park(TICKET, `harness-bug: plan add: ${added.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
    const subs = await clerk(`${BIN} subticket add ${TICKET} --run ${p.runId}`, 'Plan', 'subticket add')
    if (!subs.ok) { await park(TICKET, `harness-bug: subticket add: ${subs.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
  }
  await transition(TICKET, 'planned', null, 'Plan')
  state = 'planned'
}

// --- phase 2: Build (while any sub-ticket is not merged|parked|closed)
if (state === 'planned') {
  phase('Build')
  let first = true
  while (true) {
    const ready = await clerk(`${BIN} ticket ready-implementers ${TICKET}`, 'Build', 'ready-implementers')
    if (!ready.ok) { await park(TICKET, `harness-bug: ready-implementers: ${ready.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
    // A parent planned with no sub-tickets (e.g. by an older intake): create them once from the planner
    // run its recorded plan names, or park the parent saying why.
    if (first && ready.subtickets && ready.subtickets.length === 0) {
      first = false
      const made = await clerk(`${BIN} subticket add ${TICKET}`, 'Build', 'subticket add (recorded plan)')
      if (!made.ok) { await park(TICKET, `no sub-tickets, and none could be created from the recorded plan: ${made.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
      log(`${TICKET}: created ${(made.subtickets || []).length} sub-ticket(s) from the recorded plan`)
      continue
    }
    first = false
    // A sub-ticket the human closed parks the parent: amend the spec and re-plan, or close (doc §Routing rules).
    if (ready.closed && ready.closed.length) { await park(TICKET, `sub-ticket closed by a human: ${ready.closed.join(', ')}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
    const todo = ready.ready.concat(ready.resumable || [])
    if (todo.length === 0) {
      if (ready.remaining.length) { log(`${TICKET}: ${ready.remaining.length} sub-ticket(s) parked or waiting on a human`); return { ticket: TICKET, state: 'planned', remaining: ready.remaining } }
      break
    }
    if (ready.resumable && ready.resumable.length) log(`${TICKET}: resuming ${ready.resumable.join(', ')} from its stored state`)
    await parallel(todo.map(st => () => buildOne(st)))
  }
  const pc = await clerk(`${BIN} ticket parent-check ${TICKET}`, 'Build', 'parent-check')
  if (!pc.ok) { await park(TICKET, `parent-check refused: ${pc.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
  if (pc.state !== 'ready-for-parent-verify') return { ticket: TICKET, state: pc.state || 'planned' }
  state = 'ready-for-parent-verify'
}

// --- phase 3: Close (one verifier run on the integration branch against the parent spec)
if (state === 'ready-for-parent-verify') {
  phase('Close')
  // Asked again here: a resumed build may arrive already in ready-for-parent-verify. `reuse` names a
  // single sub-ticket's VERIFIED run that stands for the parent-close run (doc routing table, Merge gate row).
  const pc = await clerk(`${BIN} ticket parent-check ${TICKET}`, 'Close', 'parent-check')
  let runId = pc.ok && pc.reuse ? pc.reuse : null
  if (runId) {
    log(`${TICKET}: sub-ticket verifier run ${runId} stands for the parent-close run; no new verifier run`)
  } else {
    const v = await runRole('verifier', TICKET, 'Close')
    if (!v) return { ticket: TICKET, state: 'parked' }
    if (v.status !== 'VERIFIED') { await park(TICKET, `${v.status} from parent-close verifier`, [v.runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
    runId = v.runId
  }
  const arch = await clerk(`${BIN} archive ${TICKET}`, 'Close', 'archive')
  if (!arch.ok) { await park(TICKET, `archive: ${arch.stderr || ''}`, [runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
  await transition(TICKET, 'closed', null, 'Close')
  return { ticket: TICKET, state: 'closed', archived_to: arch.archived_to }
}

return { ticket: TICKET, state, note: 'nothing to dispatch from this state' }
