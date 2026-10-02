export const meta = {
  name: 'factory-build',
  description: 'Spec factory build: Planner -> sub-tickets -> Implementer -> Reviewer + Verifier -> merge gate -> parent-close verify -> archive, for one approved parent ticket',
  phases: [
    { title: 'Plan', detail: 'planner decomposes the pinned spec into sub-tickets' },
    { title: 'Build', detail: 'per sub-ticket: implementer, then reviewer and verifier in parallel on the same head, then the merge gate' },
    { title: 'Close', detail: 'one verifier run on the integration branch against the parent spec; VERIFIED archives, then closes' },
  ],
}
// args: { ticket, repo, state, target?, integration?, stubs?, inlineRoles? }  — repo/state/stubs/inlineRoles as in intake.js.
// Local-commit stand-in (operator, 2026-10-02): no remote, no CI. The gate suite is run by the
// verifier and recorded as the ci row; the merge is a local --no-ff merge into the integration
// branch. The routing is build spec part H, build.js; the join itself is `factory ticket join`.

const TICKET = args.ticket
const REPO = args.repo
const STATE = args.state
// target = the repo the implementer works in (default: the checkout bin/factory lives in);
// integration = the branch merged into (default: config integration_branch, else the target's current branch).
const ENV = `FACTORY_STATE=${STATE}` + (args.target ? ` FACTORY_REPO=${args.target}` : '') + (args.integration ? ` FACTORY_INTEGRATION_BRANCH=${args.integration}` : '')
const BIN = `${ENV} ${REPO}/bin/factory`
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
  if (parsed === null) return { ok: false, exit: res.exit, stderr: res.stderr || '', stdout: res.stdout || '', error: 'no JSON on stdout' }
  if (res.exit !== 0 && parsed.ok !== false) parsed.ok = false
  if (!parsed.stderr && res.stderr) parsed.stderr = res.stderr
  return parsed
}

async function park(ticket, reason, outputs, phase) {
  const outs = outputs && outputs.length ? ` --outputs ${outputs.join(',')}` : ''
  await clerk(`${BIN} ticket park ${ticket} --reason "${reason.replace(/"/g, "'")}"${outs}`, phase, `park ${ticket}`)
  log(`${ticket} parked: ${reason}`)
}

async function runRole(role, ticket, phase) {
  const start = await clerk(`${BIN} run start --role ${role} --ticket ${ticket} --model ${MODELS[role]}`, phase, `run start ${role} ${ticket}`)
  if (!start.ok) { await park(ticket, `harness-bug: run start ${role}: ${start.stderr || ''}`, [], phase); return null }
  const runId = start.run_id
  const comp = await clerk(`${BIN} run compose ${runId}`, phase, `run compose ${role}`)
  if (!comp.ok) { await park(ticket, `harness-bug: run compose ${role}: ${comp.stderr || ''}`, [runId], phase); return null }
  const outputPath = `${STATE}/runs/${runId}/output.md`
  let out
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
  const killed = out === null || (typeof out === 'string' && out.trim() === '')
  const fin = killed
    ? await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (killed)`)
    : await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
  if (role === 'reviewer' || role === 'verifier') await clerk(`${BIN} run cleanup ${runId}`, phase, `run cleanup ${role}`)
  if (!fin.ok) { await park(ticket, `harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
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
    if (show.state === 'ready-for-implementer') {
      const impl = await runRole('implementer', st, 'Build')
      if (!impl) return
      if (impl.status === 'KILLED') { await park(st, 'budget kill: implementer', [impl.runId], 'Build'); return }
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
    // Both checkers on the same head, fresh contexts, in parallel; each result recorded against that head.
    const headNow = await clerk(`${BIN} ticket head ${st}`, 'Build', `ticket head ${st}`)
    const sha = headNow.ok ? headNow.head : null
    if (!sha || !/^[0-9a-f]{40}$/.test(sha)) { await park(st, `harness-bug: no head for the checkers: ${headNow.stderr || ''}`, [], 'Build'); return }
    const checked = await parallel(['reviewer', 'verifier'].map(role => async () => {
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
if (cfg.ok) { MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr }
const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Plan', 'ticket show')
if (!show.ok) return { ticket: TICKET, error: `no such ticket: ${show.stderr}` }
let state = show.state

// --- phase 1: Plan (only when the parent is ready-for-planner)
if (state === 'ready-for-planner') {
  phase('Plan')
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
  await transition(TICKET, 'planned', null, 'Plan')
  state = 'planned'
}

// --- phase 2: Build (while any sub-ticket is not merged|parked|closed)
if (state === 'planned') {
  phase('Build')
  while (true) {
    const ready = await clerk(`${BIN} ticket ready-implementers ${TICKET}`, 'Build', 'ready-implementers')
    if (!ready.ok) { await park(TICKET, `harness-bug: ready-implementers: ${ready.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
    // A sub-ticket the human closed parks the parent: amend the spec and re-plan, or close (doc §Routing rules).
    if (ready.closed && ready.closed.length) { await park(TICKET, `sub-ticket closed by a human: ${ready.closed.join(', ')}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
    if (ready.ready.length === 0) {
      if (ready.remaining.length) { log(`${TICKET}: ${ready.remaining.length} sub-ticket(s) parked or waiting on a human`); return { ticket: TICKET, state: 'planned', remaining: ready.remaining } }
      break
    }
    await parallel(ready.ready.map(st => () => buildOne(st)))
  }
  const pc = await clerk(`${BIN} ticket parent-check ${TICKET}`, 'Build', 'parent-check')
  if (!pc.ok || pc.state !== 'ready-for-parent-verify') return { ticket: TICKET, state: pc.state || 'planned' }
  state = 'ready-for-parent-verify'
}

// --- phase 3: Close (one verifier run on the integration branch against the parent spec)
if (state === 'ready-for-parent-verify') {
  phase('Close')
  const v = await runRole('verifier', TICKET, 'Close')
  if (!v) return { ticket: TICKET, state: 'parked' }
  if (v.status !== 'VERIFIED') { await park(TICKET, `${v.status} from parent-close verifier`, [v.runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
  const arch = await clerk(`${BIN} archive ${TICKET}`, 'Close', 'archive')
  if (!arch.ok) { await park(TICKET, `archive: ${arch.stderr || ''}`, [v.runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
  await transition(TICKET, 'closed', null, 'Close')
  return { ticket: TICKET, state: 'closed', archived_to: arch.archived_to }
}

return { ticket: TICKET, state, note: 'nothing to dispatch from this state' }
