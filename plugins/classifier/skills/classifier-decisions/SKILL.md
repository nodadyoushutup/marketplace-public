---
name: classifier-decisions
description: >-
  Use the attached classifier MCP to resolve discrete coding decisions —
  intensity tier, subagent selection, scope/boundary checks, and search rerank.
  Rules narrow the options first; the classifier only breaks genuine ambiguity.
  Skip when no classifier MCP is attached.
---

# classifier-decisions

Consult the classifier as a **quality signal**, not a gate. A missed call here
is merely suboptimal, so it is fine to call it as an MCP tool from the agent —
unlike destructive gating, which belongs in a hook (`classifier-destructive-gate`).

## Gate

No classifier MCP attached → skip. Resolve the decision with the deterministic
rules in `code-workflow` and act. Do not block on the classifier.

## When to consult

Use the classifier only where a **discrete** decision is genuinely ambiguous
and the option set is small (3–5). Prefer the deterministic rule when one fits.

| Decision | Question shape | Suggested type |
| --- | --- | --- |
| Intensity tier (L0/L1/L2/L3) | pick one tier for this ask | `choice` |
| Subagent selection | pick one agent from a short candidate list | `choice` |
| Scope / boundary | does this edit stay inside the named slice? | `noul` |
| Search rerank | which snippet is most relevant? | `score` / `choice` |

## Method

1. **Narrow first.** Apply the written rules to drop obviously wrong options.
   The model degrades as the option count grows, so hand it 3–5 real candidates,
   not every possibility. "Verify failure → `code-debugger`" is a rule, not a
   decision.
2. **Package a short state.** One line of ask, the command or diff hunk, the
   candidate list. Never the whole file or doc.
3. **Call the classifier.** Use the session's classifier MCP tool (discover the
   namespace per the `classifier` skill). Send the typed question; read the
   probability per option.
4. **Apply policy.** Map the probability through a per-type threshold. Above it,
   act on the answer; below it, take the deterministic default or escalate.
5. **Record nothing sensitive.** Never put secrets, tokens, credentials, or
   private payloads into classifier state.

## Thresholds (starting points — tune to the workload)

| Type | Act above | Below → |
| --- | --- | --- |
| Intensity tier | 0.6 | default to the lighter tier |
| Subagent pick | 0.6 | default to the rule's first candidate |
| Scope check | 0.5 | keep scope tight; do not expand |
| Rerank | 0.4 | keep the original order |

Confidence is normalized for option count: for `choice` over \(K\) options,
\((p_{\max} - 1/K) / (1 - 1/K)\).

## Fail open

Classifier unavailable, errored, or slow → use the deterministic default and
continue. Mention the fallback in one line only when it changed the outcome.