# classifier

Decision-model craft for an attached **classifier** MCP (a small "kev/jev"
model that returns calibrated probabilities for typed questions).

**Primary workload:** coding agents — destructive gating, intensity tier,
subagent/approach pick, scope checks, search rerank.

**Also generic:** route / approve / rank / policy score when the plugin is used
from the marketplace outside a coding repo. Same tools; different option labels.

The classifier is **optional infrastructure**: no classifier MCP attached →
the plugin skips and the deterministic rules already in `code-workflow` and
`global-execute-first` carry the load. No host, port, URL, or key is hardcoded;
the MCP namespace is discovered per session.

## Two paths to the model

| Path | Who calls | Transport | When |
| --- | --- | --- | --- |
| Agent tools | the agent | classifier MCP (`*_gate` / `*_choose` / `*_score` / …) | discrete decisions + non-shell irreversible actions |
| Shell hook | Cursor harness | HTTP `CLASSIFIER_ENDPOINT` + `/v1/systemone` | `beforeShellExecution` — agents cannot skip it |

The hook cannot call MCP tools. Point `CLASSIFIER_ENDPOINT` at the **System One
HTTP base** (the API the MCP fronts), not at the MCP `/mcp` URL. When the env
is unset, the hook still applies deterministic deny rules and **asks** on
risky-shaped commands.

## Rules (Cursor)

| Rule | Purpose |
| --- | --- |
| `classifier-consult` | Auto-consult for the ambiguous middle; skip when unattached |

## Skills

| Skill | Purpose |
| --- | --- |
| `classifier` | Index / gate; discover namespace; tool map |
| `classifier-destructive-gate` | Shell hook + non-shell `*_gate` contract |
| `classifier-decisions` | Coding + generic decisions with thresholds |

## Hooks

| Hook | Event | Purpose |
| --- | --- | --- |
| `classifier-destructive-gate.py` | `beforeShellExecution` | Deterministic deny first, classifier second opinion; fail open |

| Env | Meaning |
| --- | --- |
| `CLASSIFIER_ENDPOINT` | System One HTTP base URL (unset → rules + ask only) |
| `CLASSIFIER_API_KEY` | Optional bearer token |
| `CLASSIFIER_GATE_THRESHOLD` | Deny-probability ask/block boundary, default `0.5` |

## Commands

- `/classifier` → classifier consult craft

## Pairing

- `code-workflow` — tiers and phases the classifier helps select when coding
- `global-execute-first` — deterministic default when no classifier is attached
- `global-mcp-first` — prefer the attached MCP over CLI/side paths

## Diagrams

- [`docs/classifier-workflow.drawio`](docs/classifier-workflow.drawio) — gate → act → evidence
