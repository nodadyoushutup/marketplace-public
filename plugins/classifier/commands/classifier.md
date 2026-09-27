---
name: classifier
description: >-
  Consult the classifier MCP for destructive-command gating and discrete coding
  decisions.
---

# classifier

1. Load `classifier`. Follow the skill gate and load map. If no classifier MCP
   is attached to the session, stop — use the deterministic rules instead.
2. Discover the classifier namespace once (do not hardcode a host).
3. Destructive commands: the `beforeShellExecution` hook gates them
   automatically; deterministic rules always win.
4. Discrete decisions: narrow options first, then consult the classifier for the
   ambiguous middle. Report the decision and the confidence — never fabricate one.