export const meta = {
  name: 'factory-intake',
  description: 'Spec factory intake: Triage -> Spec writer <-> Spec critic (max 2 rounds) -> human gate -> Planner, for one ticket',
  phases: [
    { title: 'Triage', detail: 'classify the request; ACCEPT routes to the spec writer' },
    { title: 'Spec', detail: 'writer and critic alternate, fresh context each, until APPROVE or the round cutoff' },
    { title: 'Plan', detail: 'after the human gate: planner decomposes the approved spec' },
  ],
}
// args: { ticket, repo, state, stubs?, agentPrefix? }
//   repo  = absolute path of the checkout (bin/factory lives under it)
//   state = absolute path of the store (knowledge_vault/spec_factory)
//   stubs = directory of <role>-<n>.md fixture outputs; when set, every role is the factory-stub agent
//   inlineRoles = true when the factory-* agent types are not registered in this session
// The script holds routing, the join and the round counter as code and nothing else decides
// them; the CLI's guards are authoritative (an exit 2 from transition parks the ticket as a
// harness bug). The script never reads a file: every store read or write is a clerk call.

const TICKET = args.ticket
const REPO = args.repo
const STATE = args.state
const BIN = `FACTORY_STATE=${STATE} ${REPO}/bin/factory`
const PREFIX = args.agentPrefix || 'factory-'
// inlineRoles: the .claude/agents/factory-* definitions are not registered in this session (the
// directory did not exist at session start), so every role runs as general-purpose and reads its
// role prompt from runs/<id>/system-prompt.txt. Model per role is unchanged; tool fences are not.
const INLINE = !!args.inlineRoles
const CLERK_RULES = 'You are the store clerk of the spec factory: run the one command you are given, once, unchanged, from the repository root; run nothing else, edit nothing, interpret nothing. '
const AGENT_NAME = { triage: 'triage', spec_writer: 'spec-writer', critic: 'spec-critic', planner: 'planner' }

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
let MAX = 2
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

async function park(reason, outputs, phase) {
  const outs = outputs && outputs.length ? ` --outputs ${outputs.join(',')}` : ''
  await clerk(`${BIN} ticket park ${TICKET} --reason "${reason.replace(/"/g, "'")}"${outs}`, phase, 'park')
  log(`${TICKET} parked: ${reason}`)
}

async function runRole(role, phase) {
  const start = await clerk(`${BIN} run start --role ${role} --ticket ${TICKET} --model ${MODELS[role]}`, phase, `run start ${role}`)
  if (!start.ok) { await park(`harness-bug: run start ${role}: ${start.stderr || ''}`, [], phase); return null }
  const runId = start.run_id
  const comp = await clerk(`${BIN} run compose ${runId}`, phase, `run compose ${role}`)
  if (!comp.ok) { await park(`harness-bug: run compose ${role}: ${comp.stderr || ''}`, [runId], phase); return null }
  const outputPath = `${STATE}/runs/${runId}/output.md`
  let out
  if (args.stubs) {
    stubCount[role] = (stubCount[role] || 0) + 1
    out = await agent(
      `Stub file: ${args.stubs}/${role}-${stubCount[role]}.md\nOutput file: ${outputPath}\n` +
      `If the stub file exists, write its content verbatim to the output file and return that content. ` +
      `If it does not exist, write nothing and return an empty message.` +
      (INLINE ? ' You are a test stub: do exactly this and nothing else; run no other command.' : ''),
      { agentType: INLINE ? 'general-purpose' : `${PREFIX}stub`, model: 'haiku', effort: 'low', phase, label: `${role} (stub) ${TICKET}` })
  } else {
    out = await agent(
      (INLINE ? `First read ${STATE}/runs/${runId}/system-prompt.txt: it is your role and your rules for this run; follow it exactly, including the preamble at its top. ` : '') +
      `Your entire input is the file ${STATE}/runs/${runId}/input.md; read it first and follow it. ` +
      `Write your complete output to ${outputPath} and return the same text.`,
      { agentType: INLINE ? 'general-purpose' : `${PREFIX}${AGENT_NAME[role]}`, model: MODELS[role], phase, label: `${role} ${TICKET}` })
  }
  const killed = out === null || (typeof out === 'string' && out.trim() === '')
  const fin = killed
    ? await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (killed)`)
    : await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
  if (!fin.ok) { await park(`harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
  log(`${role} ${runId}: ${fin.status}${fin.escalations && fin.escalations.length ? ` (+${fin.escalations.length} escalations)` : ''}`)
  return { runId, status: fin.status, escalations: fin.escalations || [] }
}

async function transition(to, roundOp, phase) {
  const r = roundOp ? ` --round ${roundOp}` : ''
  return clerk(`${BIN} ticket transition ${TICKET} --to ${to} --by workflow${r}`, phase, `transition -> ${to}`)
}

// --- start: read config and the ticket's stored state (resumption starts from what the store holds)
const cfg = await clerk(`${BIN} config`, 'Triage', 'config')
if (cfg.ok) { MODELS = cfg.models; MAX = cfg.max_rounds.spec }
const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Triage', 'ticket show')
if (!show.ok) return { ticket: TICKET, error: `no such ticket: ${show.stderr}` }
let state = show.state
let round = (show.round && show.round.spec) || 0

// --- phase 1: Triage
if (state === 'ready-for-triage') {
  phase('Triage')
  const t = await runRole('triage', 'Triage')
  if (!t) return { ticket: TICKET, state: 'parked' }
  if (t.status === 'ACCEPT') { await transition('ready-for-spec-writer', null, 'Triage'); state = 'ready-for-spec-writer' }
  else if (t.status === 'REJECT') { await transition('closed', null, 'Triage'); return { ticket: TICKET, state: 'closed', triage: t } }
  else if (t.status === 'NEEDS-HUMAN') { await park(`NEEDS-HUMAN from triage`, [t.runId], 'Triage'); return { ticket: TICKET, state: 'parked', triage: t } }
  else if (t.status === 'CLARIFY') { await transition('waiting-requester', null, 'Triage'); return { ticket: TICKET, state: 'waiting-requester', triage: t } }
  else { await park(`harness-bug: unknown STATUS ${t.status} from triage`, [t.runId], 'Triage'); return { ticket: TICKET, state: 'parked' } }
}

// --- phase 2: Spec loop (writer <-> critic)
if (state === 'ready-for-spec-writer' || state === 'ready-for-critic') {
  phase('Spec')
  while (true) {
    if (state === 'ready-for-spec-writer') {
      const w = await runRole('spec_writer', 'Spec')
      if (!w) return { ticket: TICKET, state: 'parked' }
      if (w.status === 'NEEDS-HUMAN') {
        await clerk(`${BIN} spec add ${TICKET} --from-run ${w.runId}`, 'Spec', 'spec add (draft with open questions)')
        await park('NEEDS-HUMAN from spec writer', [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' }
      }
      if (w.status !== 'READY-FOR-CRITIC' && w.status !== 'NEEDS-SPLIT') { await park(`harness-bug: unknown STATUS ${w.status} from spec writer`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
      const added = await clerk(`${BIN} spec add ${TICKET} --from-run ${w.runId}`, 'Spec', 'spec add')
      if (!added.ok) { await park(`harness-bug: spec add: ${added.stderr || ''}`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
      const tr = await transition('ready-for-critic', 'spec:init', 'Spec')
      if (!tr.ok) { await park(`harness-bug: transition to critic: ${tr.stderr || ''}`, [w.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
      round = (tr.round && typeof tr.round.spec === 'number') ? tr.round.spec : round
      state = 'ready-for-critic'
    }
    const c = await runRole('critic', 'Spec')
    if (!c) return { ticket: TICKET, state: 'parked' }
    if (c.status === 'APPROVE') {
      await transition('awaiting-spec-gate', null, 'Spec')
      log(`${TICKET}: spec approved by critic in round ${round}; awaiting the human gate (bin/factory approve-spec ${TICKET})`)
      return { ticket: TICKET, state: 'awaiting-spec-gate', rounds: round }
    }
    if (c.status === 'ESCALATE') { await park('ESCALATE from critic', [c.runId], 'Spec'); return { ticket: TICKET, state: 'parked', rounds: round } }
    if (c.status !== 'REVISE') { await park(`harness-bug: unknown STATUS ${c.status} from critic`, [c.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
    if (round < MAX) {
      const tr = await transition('ready-for-spec-writer', 'spec:+1', 'Spec')
      if (!tr.ok) { await park(`harness-bug: round increment refused: ${tr.stderr || ''}`, [c.runId], 'Spec'); return { ticket: TICKET, state: 'parked' } }
      round = (tr.round && typeof tr.round.spec === 'number') ? tr.round.spec : round
      state = 'ready-for-spec-writer'
      continue
    }
    await park('max rounds', [c.runId], 'Spec')
    return { ticket: TICKET, state: 'parked', rounds: round, reason: 'max rounds' }
  }
}

// --- phase 3: Plan (only after the human gate moved the ticket to ready-for-planner)
if (state === 'ready-for-planner') {
  phase('Plan')
  const p = await runRole('planner', 'Plan')
  if (!p) return { ticket: TICKET, state: 'parked' }
  if (p.status === 'PLANNED') {
    const added = await clerk(`${BIN} plan add ${TICKET} --from-run ${p.runId}`, 'Plan', 'plan add')
    if (!added.ok) { await park(`harness-bug: plan add: ${added.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
    await transition('planned', null, 'Plan')
    return { ticket: TICKET, state: 'planned' }
  }
  if (p.status === 'ESCALATE') { await park('ESCALATE from planner', [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
  await park(`harness-bug: unknown STATUS ${p.status} from planner`, [p.runId], 'Plan')
  return { ticket: TICKET, state: 'parked' }
}

return { ticket: TICKET, state, note: 'nothing to dispatch from this state' }
