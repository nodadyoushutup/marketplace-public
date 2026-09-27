---
name: classifier-decisions
description: >-
  Resolve discrete decisions via the attached classifier MCP — coding (intensity
  tier, subagent, scope, rerank) and generic (route, approve, rank). Rules narrow
  options first; the classifier breaks genuine ambiguity. Skip when unattached.
---

# classifier-decisions

Consult the classifier as a **quality signal**, not a safety hook. A missed call
here is suboptimal, not catastrophic — call it as an MCP tool from the agent.
Destructive **shell** gating belongs in `classifier-destructive-gate` (hook).

## Gate

No classifier MCP attached → skip. Resolve with deterministic rules
(`code-workflow`, host policy) and act. Do not block on the classifier.

## When to consult (auto)

Call when **all** of these hold:

1. The decision is **discrete** (pick one option, or score a short criterion list).
2. Written rules do **not** already force a single answer.
3. You can hand the model **2–5** real candidates (or a short criterion list).

Do **not** call for trivia (typo, rename, known verify-failure → `code-debugger`).

### Coding (primary)

| Decision | Tool | Options / criteria (examples) |
| --- | --- | --- |
| Intensity tier | `*_choose` | `L0`, `L1`, `L2`, `L3` |
| Subagent pick | `*_choose` | short candidate agent names only |
| Approach fork | `*_choose` | 2–4 concrete approaches already narrowed |
| Scope / boundary | `*_score` or `*_choose` | e.g. `stays_in_slice`, `expands_scope` |
| Search / snippet rerank | `*_score` or `*_choose` | top snippets or paths only |

### Generic (marketplace / non-coding)

| Decision | Tool | Options / criteria (examples) |
| --- | --- | --- |
| Route to a handler | `*_choose` | queue / team / playbook names |
| Approve vs reject | `*_choose` or `*_gate` | `approve` / `reject`, or gate an action |
| Rank candidates | `*_score` | one criterion list, or choose among short labels |
| Policy yes/no | `*_score` | named policy checks scored independently |

## Method

1. **Narrow first.** Drop obviously wrong options with written rules. Hand the
   model 2–5 real candidates — never every possibility.
2. **Package a short state.** One line of ask + the candidate list (or command +
   cwd). Never the whole file or doc. Never secrets.
3. **Prefer opinionated tools.** `*_choose` / `*_score` / `*_gate` before raw
   `*_ask`. Discover the namespace once per the `classifier` skill.
4. **Apply policy.** Map probability through the per-type threshold below.
   Above → act; below → deterministic default or escalate to the user.
5. **One line of evidence.** When the classifier changed the outcome, mention
   choice + confidence (or denyProbability) in one short line. Do not dump raw
   distributions unless asked.

### Worked shapes

```text
*_choose
  prompt: "User ask: extract shared addon name validation into framework substrate vs keep duplicated in two custom addons. Repo uses framework-custom-addon-isolation."
  options: ["extract_base_substrate", "keep_duplicated", "shared_helper_outside_addons"]
  instructions: "Prefer substrate only when the capability is agnostic and removability stays intact."

*_score
  prompt: "Edit touches framework/addons/manifest.py and addons/example/hooks.py for the same validator."
  criteria: ["stays_framework_agnostic", "leaks_custom_addon_identity", "worth_base_extraction"]

*_gate
  command: "kubectl delete namespace ephemeral-test"
  context: "namespace is a disposable CI scratch; no PVCs"
  threshold: 0.5
```

## Thresholds (starting points — tune to the workload)

| Type | Act above | Below → |
| --- | --- | --- |
| Intensity tier | 0.6 | default to the lighter tier |
| Subagent / approach pick | 0.6 | default to the rule's first candidate |
| Scope check | 0.5 | keep scope tight; do not expand |
| Rerank / generic rank | 0.4 | keep the original order |
| Approve / policy | 0.6 | reject or escalate |

When the tool returns a precomputed `confidence`, prefer that over re-deriving
from raw probabilities. Otherwise for `choice` over \(K\) options use
\((p_{\max} - 1/K) / (1 - 1/K)\).

For `*_gate`, branch on the boolean `allowed` (denyProbability < threshold) and
still surface `denyProbability` when you escalate.

## Fail open

Classifier unavailable, errored, or slow → use the deterministic default and
continue. Mention the fallback in one line only when it changed the outcome.
