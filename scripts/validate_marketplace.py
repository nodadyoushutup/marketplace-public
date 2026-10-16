#!/usr/bin/env python3
"""Validate marketplace-public catalogs, manifests, prefixes, and quality bar.

Exit 0 when clean; print failures and exit 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"

CATALOGS = {
    "cursor": ROOT / ".cursor-plugin" / "marketplace.json",
    "claude": ROOT / ".claude-plugin" / "marketplace.json",
    "copilot": ROOT / ".github" / "plugin" / "marketplace.json",
    "codex": ROOT / ".agents" / "plugins" / "marketplace.json",
}

# Commands allowed without the plugin prefix (short slash UX).
SHORT_COMMANDS: dict[str, frozenset[str]] = {}

# Plugins that do not need a docs/*-workflow.drawio (standing posture only).
WORKFLOW_EXEMPT: frozenset[str] = frozenset()

FRONTMATTER_NAME = re.compile(
    r"(?m)^---\s*\n(?:.*\n)*?^name:\s*['\"]?([^\n'\"]+)['\"]?\s*$",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_names(path: Path) -> list[str]:
    data = load_json(path)
    return [p["name"] for p in data.get("plugins", [])]


def plugin_dirs() -> list[Path]:
    return sorted(p for p in PLUGINS.iterdir() if p.is_dir() and not p.name.startswith("."))


def frontmatter_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_NAME.search(text)
    return m.group(1).strip() if m else None


def allowed_asset(short: str, stem: str) -> bool:
    if stem == short:
        return True
    if stem.startswith(f"{short}-"):
        return True
    if stem in SHORT_COMMANDS.get(short, frozenset()):
        return True
    return False


def check_catalogs(errors: list[str]) -> set[str]:
    by_host: dict[str, list[str]] = {}
    for host, path in CATALOGS.items():
        if not path.is_file():
            errors.append(f"missing catalog: {path.relative_to(ROOT)}")
            continue
        names = catalog_names(path)
        by_host[host] = names
        if len(names) != len(set(names)):
            errors.append(f"{host}: duplicate plugin names in catalog")

    if len(by_host) < len(CATALOGS):
        return set()

    ref = set(by_host["cursor"])
    for host, names in by_host.items():
        if set(names) != ref:
            missing = sorted(ref - set(names))
            extra = sorted(set(names) - ref)
            errors.append(
                f"{host}: catalog set differs from cursor "
                f"(missing={missing or '-'} extra={extra or '-'})"
            )
        # Cursor catalog order is canonical for human diffs; warn only on set.
    return ref


def check_plugin_folder_vs_catalog(catalog: set[str], errors: list[str]) -> None:
    dirs = {p.name for p in plugin_dirs()}
    expected = {n.removeprefix("nodadyoushutup-") for n in catalog}
    if dirs != expected:
        errors.append(
            f"plugins/ folders vs catalogs: "
            f"only_dirs={sorted(dirs - expected) or '-'} "
            f"only_catalog={sorted(expected - dirs) or '-'}"
        )


def check_manifests(short: str, errors: list[str]) -> None:
    expected_name = f"nodadyoushutup-{short}"
    for rel in (
        ".cursor-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
    ):
        path = PLUGINS / short / rel
        if not path.is_file():
            errors.append(f"{short}: missing {rel}")
            continue
        data = load_json(path)
        if data.get("name") != expected_name:
            errors.append(
                f"{short}: {rel} name={data.get('name')!r} want {expected_name!r}"
            )


def check_prefixes(short: str, errors: list[str]) -> None:
    root = PLUGINS / short

    for rule in sorted((root / "rules").glob("*.mdc")) if (root / "rules").is_dir() else []:
        if not allowed_asset(short, rule.stem):
            errors.append(f"{short}: bad rule prefix {rule.name}")

    skills_root = root / "skills"
    if skills_root.is_dir():
        for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            stem = skill_dir.name
            if not allowed_asset(short, stem):
                errors.append(f"{short}: bad skill dir {stem}")
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                errors.append(f"{short}: missing {skill_dir.name}/SKILL.md")
                continue
            name = frontmatter_name(skill_md)
            if name != stem:
                errors.append(
                    f"{short}: skill frontmatter name={name!r} != dir {stem!r}"
                )

    agents_root = root / "agents"
    if agents_root.is_dir():
        for agent in sorted(agents_root.glob("*.md")):
            if not allowed_asset(short, agent.stem):
                errors.append(f"{short}: bad agent prefix {agent.name}")
            name = frontmatter_name(agent)
            if name != agent.stem:
                errors.append(
                    f"{short}: agent frontmatter name={name!r} != {agent.stem!r}"
                )

    commands_root = root / "commands"
    if commands_root.is_dir():
        for cmd in sorted(commands_root.glob("*.md")):
            if not allowed_asset(short, cmd.stem):
                errors.append(f"{short}: bad command prefix {cmd.name}")
            name = frontmatter_name(cmd)
            if name != cmd.stem:
                errors.append(
                    f"{short}: command frontmatter name={name!r} != {cmd.stem!r}"
                )


def check_quality_bar(short: str, errors: list[str]) -> None:
    root = PLUGINS / short
    readme = root / "README.md"
    if not readme.is_file():
        errors.append(f"{short}: missing README.md")

    skills_root = root / "skills"
    if not skills_root.is_dir() or not any(skills_root.glob("*/SKILL.md")):
        errors.append(f"{short}: need ≥1 skill (skills/*/SKILL.md)")

    if short in WORKFLOW_EXEMPT:
        return

    docs = root / "docs"
    workflows = list(docs.glob("*-workflow.drawio")) if docs.is_dir() else []
    if not workflows:
        errors.append(
            f"{short}: quality bar — missing docs/*-workflow.drawio "
            f"(expected at least docs/{short}-workflow.drawio)"
        )


def check_private_leak(errors: list[str]) -> None:
    # Homelab site overlays stay in marketplace-private only.
    if (PLUGINS / "homelab").exists():
        errors.append("private plugin leaked into public: plugins/homelab/")


def main() -> int:
    errors: list[str] = []
    catalog = check_catalogs(errors)
    if catalog:
        check_plugin_folder_vs_catalog(catalog, errors)
        for short in sorted(p.name for p in plugin_dirs()):
            check_manifests(short, errors)
            check_prefixes(short, errors)
            check_quality_bar(short, errors)
    check_private_leak(errors)

    if errors:
        print(f"validate_marketplace: {len(errors)} failure(s)")
        for e in errors:
            print(f"  - {e}")
        return 1

    n = len(plugin_dirs())
    print(f"validate_marketplace: OK ({n} plugins, 4 catalogs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
