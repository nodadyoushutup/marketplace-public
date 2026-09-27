#!/usr/bin/env python3
"""beforeShellExecution gate: consult the classifier before destructive commands.

The classifier is a small decision model reached through the MCP that this
session attaches. A shell hook cannot call an MCP tool, so this gate talks to the
same classifier endpoint the MCP fronts over HTTP, configurable by the operator:

    CLASSIFIER_ENDPOINT    base URL of the classifier decision endpoint
    CLASSIFIER_API_KEY     optional bearer token
    CLASSIFIER_GATE_THRESHOLD  act/deny boundary (default 0.5)

**No endpoint is hardcoded and no server is assumed.** When ``CLASSIFIER_ENDPOINT``
is unset the gate still runs its deterministic rules and simply asks the user
for risky-shaped commands; it never invents a classifier result.

Two layers, in order:

1. Deterministic rules (always first, always win). A tiny catastrophic set is
   denied outright; a broader risky-shaped set is escalated.
2. Classifier second opinion for the risky middle, when configured.

Fails open: any internal error emits ``{"permission": "allow"}`` so a broken
hook can never wedge a session. Never exits ``2``.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

DEFAULT_THRESHOLD = 0.5
CLASSIFIER_TIMEOUT_SECONDS = 2.0

# Catastrophic patterns: deny outright, independent of the classifier.
CATASTROPHIC_PATTERNS = (
    r"rm\s+-[a-z]*r[a-z]*f?[a-z]*\s+(--no-preserve-root|/\s*$|/\*)",
    r"--no-preserve-root",
    r"\bmkfs(\.\w+)?\b",
    r"\bdd\b[^\n]*\bof=/dev/(sd|nvme|vd|hd)",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",  # fork bomb
    r"\b(shred|wipefs)\b[^\n]*\/dev\/(sd|nvme|vd|hd)",
)

# Risky-shaped: escalate (ask) or send to the classifier for a second opinion.
RISKY_PATTERNS = (
    r"\brm\s+-[a-z]*r[a-z]*f?[a-z]*\b",
    r"\brm\s+-[a-z]*f[a-z]*r[a-z]*\b",
    r"\bgit\s+push\b[^\n]*--force(-with-lease)?\b",
    r"\bgit\s+push\b[^\n]*\s-f\b",
    r"\bdocker\s+compose\b[^\n]*\bdown\b[^\n]*(-v|--volumes)",
    r"\bdocker\s+volume\s+(rm|prune)\b",
    r"\bdocker\s+system\s+prune\b",
    r"\bdocker\s+image\s+prune\b[^\n]*-a\b",
    r"\bdrop\s+(table|database|schema)\b",
    r"\bterraform\s+destroy\b",
    r"\bkubectl\s+delete\b",
    r"\b(qm|pct)\s+(destroy|stop|reset)\b",
    r"\btruncate\b[^\n]*-s\s*0\b",
    r"\bdd\b[^\n]*\bof=",
    r">\s*/dev/(sd|nvme|vd|hd)",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\b[^\n]*-[a-z]*f",
)

# Read-only commands never need the gate.
SAFE_PATTERNS = (
    r"^\s*(ls|cat|head|tail|less|more|grep|rg|find|stat|file|wc|echo|pwd|which|"
    r"command\s+-v|type|env|printenv|date|whoami|id|hostname|uname|df|du|free|ps|"
    r"top|htop|tree|diff|jq|awk|sed\s+-n)\b",
    r"^\s*git\s+(status|log|show|diff|branch|remote|tag|blame|describe|rev-parse|"
    r"ls-files|config\s+--get|stash\s+list)\b",
    r"^\s*(docker|podman)\s+(ps|images|inspect|logs|version|info|volume\s+ls|"
    r"network\s+ls|compose\s+(ps|logs|config|top))\b",
    r"^\s*kubectl\s+(get|describe|logs|events|top|config\s+view)\b",
)


def read_event() -> dict:
    """Parse the Cursor hook payload from stdin, or ``{}`` when invalid."""
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def emit(permission: str, user_message: str = "", agent_message: str = "") -> None:
    """Print a ``beforeShellExecution`` result and exit 0."""
    payload: dict[str, str] = {"permission": permission}
    if user_message:
        payload["user_message"] = user_message
    if agent_message:
        payload["agent_message"] = agent_message
    print(json.dumps(payload))


def catastrophic(command: str) -> str | None:
    """Return the catastrophic pattern matched, if any."""
    for pattern in CATASTROPHIC_PATTERNS:
        if re.search(pattern, command):
            return pattern
    return None


def risky(command: str) -> bool:
    """True when the command is destructive-shaped and worth a second opinion."""
    if any(re.search(pattern, command) for pattern in SAFE_PATTERNS):
        return False
    return any(re.search(pattern, command) for pattern in RISKY_PATTERNS)


def build_state(command: str, event: dict) -> str:
    """Compose a short classifier state: the command plus optional cwd/context."""
    parts = [command.strip()]
    cwd = event.get("cwd") or event.get("working_directory")
    if isinstance(cwd, str) and cwd:
        parts.append(f"cwd: {cwd}")
    return "\n".join(parts)


def classify(command: str, event: dict) -> float | None:
    """Ask the classifier how likely the command is destructive.

    Returns the destructive probability, or ``None`` when the classifier is not
    configured or cannot be reached/parsed. Never raises.
    """
    endpoint = os.environ.get("CLASSIFIER_ENDPOINT", "").strip()
    if not endpoint:
        return None

    url = endpoint.rstrip("/") + "/v1/systemone"
    body = {
        "state": build_state(command, event),
        "questions": {
            "gate": {
                "type": "choice",
                "instructions": (
                    "Decide whether this shell command may be executed. "
                    "Choose allow when it is read-only, additive, or safely "
                    "reversible. Choose deny when it destroys data, is "
                    "irreversible, or cannot be undone without a restore."
                ),
                "criteria": {
                    "allow": "read-only, additive, or safely reversible",
                    "deny": (
                        "destructive, irreversible, or unrecoverable "
                        "without a restore"
                    ),
                },
            }
        },
    }
    headers = {"content-type": "application/json"}
    api_key = os.environ.get("CLASSIFIER_API_KEY", "").strip()
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            request, timeout=CLASSIFIER_TIMEOUT_SECONDS
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, OSError, TimeoutError):
        return None

    return destructive_probability(payload)


def destructive_probability(payload: object) -> float | None:
    """Extract the probability of the ``deny`` label from a classifier response.

    Canonical System One / Kev shape is
    ``answers.<question>.probabilities.deny``. Also tolerates flatter
    ``{deny: p}`` maps under ``answers`` or the response root. Returns
    ``None`` when no numeric deny probability can be found.
    """
    if not isinstance(payload, dict):
        return None

    candidates: list[object] = []
    answers = payload.get("answers")
    if isinstance(answers, dict):
        candidates.extend(answers.values())
    candidates.append(payload)

    label_keys = ("deny", "destructive", "unrecoverable", "unsafe")

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        probabilities = candidate.get("probabilities")
        if isinstance(probabilities, dict):
            for key in label_keys:
                value = probabilities.get(key)
                if isinstance(value, (int, float)):
                    return float(value)
        for key in label_keys:
            value = candidate.get(key)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, dict):
                for inner in value.values():
                    if isinstance(inner, (int, float)):
                        return float(inner)
    return None


def threshold() -> float:
    """Return the classifier act/deny boundary, clamped to ``[0, 1]``."""
    raw = os.environ.get("CLASSIFIER_GATE_THRESHOLD", "").strip()
    if not raw:
        return DEFAULT_THRESHOLD
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_THRESHOLD
    return min(max(value, 0.0), 1.0)


def decide(command: str, event: dict) -> tuple[str, str, str]:
    """Return ``(permission, user_message, agent_message)`` for a command.

    Pure policy: deterministic rules first, classifier second opinion for the
    risky middle. Never raises.
    """
    if not isinstance(command, str) or not command.strip():
        return "allow", "", ""

    if catastrophic(command) is not None:
        return (
            "deny",
            "Blocked: this command is on the unrecoverable list "
            "(device overwrite / filesystem format / root wipe).",
            "classifier-destructive-gate: catastrophic pattern denied.",
        )

    if not risky(command):
        return "allow", "", ""

    probability = classify(command, event)
    if probability is None:
        return (
            "ask",
            "This command looks destructive and the classifier could not be "
            "consulted. Review it before running.",
            "classifier-destructive-gate: risky command escalated (no classifier).",
        )

    if probability > threshold():
        return (
            "ask",
            f"The classifier rates this command {probability:.0%} likely to "
            "destroy state that cannot be trivially recreated. Review before "
            "running.",
            "classifier-destructive-gate: classifier flagged destructive.",
        )

    return (
        "allow",
        "",
        f"classifier-destructive-gate: classifier rated it {probability:.0%} "
        "destructive (below threshold).",
    )


def main() -> int:
    """Run the gate and emit a permission decision."""
    event = read_event()
    command = event.get("command")
    permission, user_message, agent_message = decide(command, event)
    emit(permission, user_message, agent_message)
    return 0


if __name__ == "__main__":
    try:
        status = main()
    except Exception:  # noqa: BLE001 - the gate must never wedge a session
        emit("allow")
        status = 0
    raise SystemExit(status)