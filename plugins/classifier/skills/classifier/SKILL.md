---
name: classifier
description: >-
  Decision-model craft ("kev/jev") for the coding workflow: consult the attached
  classifier MCP to gate destructive commands and to resolve discrete coding
  decisions (intensity tier, subagent pick, scope, rerank). Skip entirely when no
  classifier MCP is attached.
---

# classifier

The **classifier** is a tiny decision model reached through an MCP that is
attached to this agent session. It does not chat, does not write code, and does
not call tools. It takes a short **state** plus a few typed **questions** and
returns a probability per answer in one pass. Everything before the call is
packaging; everything after is your policy.

The MCP server is whatever classifier endpoint this session exposes — the exact
namespace differs per host (`mcp-kev`, `mcp-jev`, `mcp-classifier`, a bespoke
`mcp_systemone`, …). **Discover it; never assume a name.**

## Gate

If no classifier MCP is attached to the session → **skip this plugin
entirely**. Use the deterministic rules that already live in `code-workflow`,
`global-execute-first`, and host policy. Do not invent a classifier call, do not
block work waiting for one, and do not treat a missing classifier as a failure.

## Load map

| Need | Load |
| --- | --- |
| Gate a shell command before it runs | `classifier-destructive-gate` (hook + skill) |
| Intensity tier, subagent pick, scope, rerank | `classifier-decisions` |
| Rule-level default | `classifier-consult` |

## Discover the MCP (once per session)

1. List the session's MCP tools (`GetDynamicTools` / the attached tool list).
2. Find the namespace whose tools build a state+question decision call — look
   for names like `kev_gate`, `*_choose`, `*_score`, `*_ask`, `*_status`, or a
   raw `/systemone` passthrough.
3. Cache that namespace for the session. Do **not** hardcode a host, port, URL,
   or key anywhere in this plugin — the endpoint is the operator's, supplied by
   the MCP.

## Defaults

1. **Rules narrow, the classifier decides the ambiguous middle.** Run
   deterministic guards first; they always win. Only send genuinely ambiguous
   decisions to the classifier.
2. **Short state only.** Classifiers trained for gating want a command line, a
   diff hunk, or a one-line ask — not a whole document. Long states degrade
   confidence.
3. **Confidence, not argmax.** Act only when a confident answer clears the
   per-type threshold; otherwise escalate to the user. The uncertain middle is
   the whole point.
4. **Fail open, then fall back.** Classifier unreachable, slow, or ambiguous →
   fall back to the deterministic default and continue. Never wedge work.
5. **Never invent decisions.** Do not fabricate probabilities, answers, or an
   MCP that is not attached. Report the classifier was unavailable instead.

## Pairing

- `code-workflow` — tiers and phases the classifier helps select.
- `global-execute-first` — the deterministic default when no classifier is
  attached.
- `global-mcp-first` — prefer the attached MCP over CLI/side paths.