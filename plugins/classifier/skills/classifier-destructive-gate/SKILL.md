---
name: classifier-destructive-gate
description: >-
  Gate destructive actions through the classifier: shell via beforeShellExecution
  hook (HTTP CLASSIFIER_ENDPOINT), non-shell via attached *_gate MCP tool.
  Deterministic deny rules always win. Skip when no classifier is available.
---

# classifier-destructive-gate

Destructive actions are the one place the classifier is a **safety** signal.

- **Shell:** the plugin ships a `beforeShellExecution` hook so the harness
  intercepts the command. The agent cannot skip it. Hooks cannot call MCP
  tools, so the hook talks HTTP to `CLASSIFIER_ENDPOINT` (the same System One
  API the MCP fronts).
- **Non-shell:** MCP mutates, data wipes, and other irreversible tools are
  **not** covered by the shell hook. Before those, the agent must call the
  session's `*_gate` tool when a classifier MCP is attached.

This skill is the human-readable contract behind both paths.

## Gate

- No `CLASSIFIER_ENDPOINT` → hook still runs deterministic rules and **asks**
  on risky-shaped shell commands (never invents a classifier score).
- No classifier MCP attached → agent skips `*_gate` and uses host safety rules
  only. Do not block work because the classifier is missing.

## Two layers (order matters)

1. **Deterministic deny rules — always first, always win.** If a command matches
   a hard-deny pattern, deny/ask regardless of any classifier score. The
   classifier never overrides a rule.
2. **Classifier second opinion — the uncertain middle.** For actions that are
   risky-shaped but not an obvious hard deny, ask whether the action destroys
   state that cannot be trivially recreated.

## Risky-shaped (candidates for the classifier)

Shell (hook patterns — non-exhaustive):

- `rm -rf` / `rm -fr` / recursive deletes
- `docker compose down -v`, `docker volume rm`, `docker system prune`
- `git push --force` / `--force-with-lease` to a shared branch
- `DROP TABLE` / `DROP DATABASE` / destructive migrations
- `kubectl delete` / `terraform destroy` / `qm`/`pct` destructive verbs
- `dd of=`, `mkfs`, overwrite-redirects onto a device or mount
- `git reset --hard`, `git clean -f…`

Non-shell (agent must call `*_gate` when MCP is attached):

- Irreversible MCP tools (delete bucket/object, delete VM, restore overwrite,
  force-merge, purge queues) when host plugin safety already requires an
  explicit verb — classifier is a second opinion, not a bypass.
- Any action you would not run without a restore path.

Read-only commands (`ls`, `cat`, `git status`, `docker ps`, `kubectl get`) never
need the classifier.

## Decision

| Result | Action |
| --- | --- |
| Confidently destructive | **Deny / ask** the user before running |
| Confidently safe | Allow |
| Uncertain middle | **Escalate** — surface the action and ask |

Hook threshold: `CLASSIFIER_GATE_THRESHOLD` (default `0.5`), comparing the
**deny** probability from System One (`answers.gate.probabilities.deny`).

MCP path: call `*_gate(command, context?, threshold?)` and branch on `allowed`
(and surface `denyProbability` when asking the user).

## Operator env (hook only)

| Env | Meaning |
| --- | --- |
| `CLASSIFIER_ENDPOINT` | Base URL of the System One HTTP API (not the MCP URL). Unset → rules + ask only |
| `CLASSIFIER_API_KEY` | Optional bearer token for that HTTP API |
| `CLASSIFIER_GATE_THRESHOLD` | Deny probability needed to ask/block (default `0.5`) |

Example: if Kev serves System One at `http://192.168.1.27:8008`, set
`CLASSIFIER_ENDPOINT` to that base. The MCP URL (`…/mcp`) is for agent tools,
not this hook.

## Hard rules

- Never auto-run a hard-deny pattern because the classifier said "safe".
- Never claim the classifier ran when it did not.
- Never put secret material into the classifier state.
- Fail open on hook error — a broken hook must not wedge the session.
- Never use the classifier to bypass an explicit user/host safety gate.
