---
name: classifier-destructive-gate
description: >-
  Gate destructive shell commands through the attached classifier MCP before they
  run. Deterministic deny rules always win; the classifier is a calibrated second
  opinion that can block or escalate the uncertain middle. Backed by the
  plugin's beforeShellExecution hook. Skip when no classifier MCP is attached.
---

# classifier-destructive-gate

Destructive commands are the one place the classifier is a **safety** signal, so
the call must not depend on the agent choosing to make it. That is why this
plugin ships a `beforeShellExecution` hook: the **harness** intercepts the
command and consults the classifier, and the agent cannot skip it. This skill is
the human-readable contract behind that hook.

## Gate

No classifier MCP attached → the hook stays inert (it fails open) and the
deterministic deny rules below carry the load. Do not block work because the
classifier is missing.

## Two layers (order matters)

1. **Deterministic deny rules — always first, always win.** If a command matches
   a hard-deny pattern, deny/ask regardless of any classifier score. The
   classifier never overrides a rule.
2. **Classifier second opinion — the uncertain middle.** For commands that are
   risky-shaped but not an obvious hard deny, ask the classifier whether the
   command destroys state that cannot be trivially recreated.

## Risky-shaped commands (candidates for the classifier)

- `rm -rf` / `rm -fr` / recursive deletes
- `docker compose down -v`, `docker volume rm`, `docker system prune` (volumes)
- `git push --force` / `--force-with-lease` to a shared branch
- `DROP TABLE` / `DROP DATABASE` / destructive migrations
- `kubectl delete` / `terraform destroy` / `proxmox`/`qm` destructive verbs
- `dd of=`, `mkfs`, overwrite-redirects onto a device or mount

Read-only commands (`ls`, `cat`, `git status`, `docker ps`, `kubectl get`) never
need the classifier.

## Decision

Build a typed choice question for the classifier — allow when the command is
read-only or safely reversible, deny when it destroys state that cannot be
trivially recreated — with a short state of the command plus cwd/context. Then:

| Result | Action |
| --- | --- |
| Confidently destructive | **Deny / ask** the user before running |
| Confidently safe | Allow |
| Uncertain middle | **Escalate** — surface the command and ask |

The hook documents this shape in `hooks/classifier-destructive-gate.py`; the
threshold is configurable with `CLASSIFIER_GATE_THRESHOLD` (default `0.5`).

## Hard rules

- Never auto-run a hard-deny pattern because the classifier said "safe".
- Never claim the classifier ran when it did not.
- Never put secret material into the classifier state.
- Fail open on hook error — a broken hook must not wedge the session.