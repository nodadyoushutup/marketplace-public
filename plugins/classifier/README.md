# classifier

Decision-model craft for the coding workflow. When the session attaches a
**classifier** MCP (a small "kev/jev" decision model that returns a probability
per typed question), this plugin teaches the agent when to consult it — gating
destructive commands and resolving discrete coding decisions — and ships the
hook that makes destructive gating unskippable.

The classifier is **optional infrastructure**: no classifier MCP attached →
the plugin skips and the deterministic rules already in `code-workflow` and
`global-execute-first` carry the load. No host, port, URL, or key is hardcoded;
the MCP namespace is discovered per session.

## Rules (Cursor)

| Rule | Purpose |
| --- | --- |
| `classifier-consult` | Default: consult the classifier for the ambiguous middle; skip when unattached |

## Skills

| Skill | Purpose |
| --- | --- |
| `classifier` | Index / gate; discover the classifier MCP namespace |
| `classifier-destructive-gate` | Destructive-command contract behind the hook |
| `classifier-decisions` | Tier, subagent pick, scope, rerank with thresholds |

## Hooks

| Hook | Event | Purpose |
| --- | --- | --- |
| `classifier-destructive-gate.py` | `beforeShellExecution` | Deterministic deny rules first, then classifier second opinion; fail open |

Configure the endpoint the hook calls (never hardcoded):

| Env | Meaning |
| --- | --- |
| `CLASSIFIER_ENDPOINT` | Base URL of the classifier decision endpoint (unset → rules only) |
| `CLASSIFIER_API_KEY` | Optional bearer token |
| `CLASSIFIER_GATE_THRESHOLD` | Act/deny boundary, default `0.5` |

## Commands

- `/classifier` → classifier consult craft

## Pairing

- `code-workflow` — tiers and phases the classifier helps select
- `global-execute-first` — deterministic default when no classifier is attached
- `global-mcp-first` — prefer the attached MCP over CLI/side paths

## Diagrams

- [`docs/classifier-workflow.drawio`](docs/classifier-workflow.drawio) — gate → act → evidence