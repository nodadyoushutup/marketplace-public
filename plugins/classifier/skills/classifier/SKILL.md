---
name: classifier
description: >-
  Decision-model craft for an attached classifier MCP (kev/jev). Primary use is
  coding (destructive gate, intensity tier, subagent pick, scope, rerank); also
  covers generic route/approve/rank decisions. Skip entirely when no classifier
  MCP is attached.
---

# classifier

The **classifier** is a tiny decision model reached through an MCP attached to
this session. It does not chat, write code, or call tools. It takes a short
**state** plus typed **questions** and returns a probability per answer in one
pass. Everything before the call is packaging; everything after is your policy.

Primary workload is **coding agents**. The same tools work for **generic**
route / approve / rank decisions when the marketplace plugin is used outside a
coding repo. Coding examples are defaults, not a hard scope limit.

The MCP namespace differs per host (`mcp_kev`, `mcp-jev`, `mcp-classifier`, a
bespoke `mcp_systemone`, …). **Discover it; never assume a name.**

## Gate

If no classifier MCP is attached to the session → **skip this plugin
entirely**. Use the deterministic rules that already live in `code-workflow`,
`global-execute-first`, and host policy. Do not invent a classifier call, do not
block work waiting for one, and do not treat a missing classifier as a failure.

## Load map

| Need | Load |
| --- | --- |
| Shell gate (hook + contract) | `classifier-destructive-gate` |
| Discrete decisions + thresholds | `classifier-decisions` |
| Always-on default | `classifier-consult` |

## Discover the MCP (once per session)

1. List the session's MCP tools (`GetDynamicTools` / the attached tool list).
2. Find the namespace whose tools build a state+question decision call — prefer
   opinionated names ending in `_gate`, `_choose`, `_score`, plus `_ask` /
   `_status` or a raw `/systemone` passthrough.
3. Cache that namespace for the session. Do **not** hardcode a host, port, URL,
   or key — the endpoint is the operator's, supplied by the MCP.

## Tool map (prefer opinionated tools)

| Job | Call | Avoid |
| --- | --- | --- |
| May this action run? | `*_gate(command, context?, threshold?)` | Hand-rolling allow/deny via `*_ask` |
| Pick 1 of N options | `*_choose(prompt, options, instructions?)` | Argmax over a huge unfiltered list |
| Score / rerank criteria | `*_score(prompt, criteria, instructions?)` | One mega-prompt with no criteria |
| Exotic typed question | `*_ask(state, questions)` | Everyday gate/choose/score |
| Liveness | `*_status()` | Treating status as a decision |

Shell destructive gating is owned by the `beforeShellExecution` hook (HTTP to
`CLASSIFIER_ENDPOINT`). Agents still call `*_gate` for **non-shell**
irreversible actions (MCP mutates, data wipes, force-pushes invoked outside the
shell hook path).

## Defaults

1. **Rules narrow, the classifier decides the ambiguous middle.** Deterministic
   guards always win. Only send genuinely ambiguous decisions.
2. **Short state only.** A command line, a one-line ask, a diff hunk, or a
   3–5 option list — not a whole document. Long states degrade confidence.
3. **Confidence, not argmax.** Act only when a confident answer clears the
   per-type threshold; otherwise take the deterministic default or escalate.
4. **Fail open, then fall back.** Unreachable, slow, or ambiguous →
   deterministic default and continue. Never wedge work.
5. **Never invent decisions.** Do not fabricate probabilities or an MCP that
   is not attached.

## Pairing

- `code-workflow` — tiers and phases the classifier helps select when coding.
- `global-execute-first` — deterministic default when no classifier is attached.
- `global-mcp-first` — prefer the attached MCP over CLI/side paths to the same
  decision endpoint.
