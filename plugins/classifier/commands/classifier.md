---
name: classifier
description: >-
  Consult the classifier MCP for destructive gating and discrete decisions
  (coding-primary: tier/subagent/scope; also generic route/approve/rank).
---

# classifier

1. Load `classifier`. Follow the skill gate and load map. If no classifier MCP
   is attached to the session, stop — use the deterministic rules instead.
2. Discover the classifier namespace once (do not hardcode a host). Prefer
   `*_gate` / `*_choose` / `*_score` over raw `*_ask`.
3. Destructive **shell**: the `beforeShellExecution` hook gates automatically;
   deterministic rules always win. Destructive **non-shell**: call `*_gate`
   before acting when the MCP is attached.
4. Discrete decisions: narrow options first, then consult for the ambiguous
   middle (`classifier-decisions`). Report choice + confidence — never
   fabricate one.
