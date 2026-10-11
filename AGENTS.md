# AGENTS.md — marketplace-public

Public Claude Code / Cursor / GitHub Copilot / OpenAI Codex plugin marketplace.
Root catalogs:

- `.cursor-plugin/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.github/plugin/marketplace.json` (Copilot)
- `.agents/plugins/marketplace.json` (Codex)

Plugins live under `plugins/<short>/` (for example `plugins/code/`).

Marketplace / `plugin.json` **`name`** is `nodadyoushutup-<short>` (for example
`nodadyoushutup-code`). Claude/Cursor catalog `source` stays the short folder
name; Copilot/Codex catalogs use `./plugins/<short>`.

Homelab **homelab** infra craft ships from the sibling
[`marketplace-private`](https://github.com/nodadyoushutup/marketplace-private)
repo — do not re-add `plugins/homelab/` here. Framework monorepo craft lives
in this public marketplace as `plugins/framework/`.

## Plugin prefix rule (required)

Asset basenames use the **short** plugin key (folder stem), not the full
marketplace id. Every rule, skill, and agent basename **must** use that short
prefix (kebab-case), or — for a single primary skill — the exact short name.
Commands follow the same rule **except** short slash UX names documented below
(`/deslop`, `/refactor`, `/jira`, `/confluence`).

| Short key (folder) | Marketplace id | Allowed basenames |
| --- | --- | --- |
| `global` | `nodadyoushutup-global` | `global-*` |
| `code` | `nodadyoushutup-code` | `code-*` |
| `business-analyst` | `nodadyoushutup-business-analyst` | `business-analyst` or `business-analyst-*` |
| `agentmemory` | `nodadyoushutup-agentmemory` | `agentmemory` or `agentmemory-*` |
| `atlassian` | `nodadyoushutup-atlassian` | `atlassian` or `atlassian-*` |
| `github` | `nodadyoushutup-github` | `github` or `github-*` |
| `jenkins` | `nodadyoushutup-jenkins` | `jenkins` or `jenkins-*` |
| `browser` | `nodadyoushutup-browser` | `browser-*` |
| `drawio` | `nodadyoushutup-drawio` | `drawio-*` |
| `lucidchart` | `nodadyoushutup-lucidchart` | `lucidchart-*` |
| `google-workspace` | `nodadyoushutup-google-workspace` | `google-workspace` or `google-workspace-*` |
| `google-cloud` | `nodadyoushutup-google-cloud` | `google-cloud` or `google-cloud-*` |
| `freshservice` | `nodadyoushutup-freshservice` | `freshservice` or `freshservice-*` |
| `vault` | `nodadyoushutup-vault` | `vault` or `vault-*` |
| `grafana` | `nodadyoushutup-grafana` | `grafana` or `grafana-*` |
| `cloudflare` | `nodadyoushutup-cloudflare` | `cloudflare` or `cloudflare-*` |
| `compose` | `nodadyoushutup-compose` | `compose` or `compose-*` |
| `framework` | `nodadyoushutup-framework` | `framework` or `framework-*` |
| `kubernetes` | `nodadyoushutup-kubernetes` | `kubernetes` or `kubernetes-*` |
| `proxmox` | `nodadyoushutup-proxmox` | `proxmox` or `proxmox-*` |
| `argocd` | `nodadyoushutup-argocd` | `argocd` or `argocd-*` |
| `prometheus` | `nodadyoushutup-prometheus` | `prometheus` or `prometheus-*` |
| `graylog` | `nodadyoushutup-graylog` | `graylog` or `graylog-*` |
| `minio` | `nodadyoushutup-minio` | `minio` or `minio-*` |
| `velero` | `nodadyoushutup-velero` | `velero` or `velero-*` |
| `fortigate` | `nodadyoushutup-fortigate` | `fortigate` or `fortigate-*` |
| `yarr` | `nodadyoushutup-yarr` | `yarr` or `yarr-*` |

Homelab (`homelab` / `homelab-*`) lives only in **marketplace-private**.

### Examples

- `plugins/code/rules/code-python.mdc`
- `plugins/code/skills/code-workflow/SKILL.md` with frontmatter `name: code-workflow`
- `plugins/code/skills/code-security/SKILL.md` with frontmatter `name: code-security`
- `plugins/code/agents/code-reviewer.md` with frontmatter `name: code-reviewer`
- `plugins/agentmemory/skills/agentmemory/SKILL.md` with frontmatter `name: agentmemory`
- `plugins/atlassian/skills/atlassian/SKILL.md` with frontmatter `name: atlassian`
- `plugins/atlassian/commands/atlassian.md` with frontmatter `name: atlassian` → `/atlassian`
- `plugins/atlassian/commands/jira.md` with frontmatter `name: jira` → `/jira`
- `plugins/atlassian/commands/confluence.md` with frontmatter `name: confluence` → `/confluence`
- `plugins/github/skills/github/SKILL.md` with frontmatter `name: github`
- `plugins/github/commands/github.md` with frontmatter `name: github` → `/github`
- `plugins/jenkins/skills/jenkins/SKILL.md` with frontmatter `name: jenkins`
- `plugins/jenkins/commands/jenkins.md` with frontmatter `name: jenkins` → `/jenkins`
- `plugins/code/commands/code-worktree.md` with frontmatter `name: code-worktree`
- `plugins/code/commands/code-execute-jira.md` with frontmatter
  `name: code-execute-jira` → `/code-execute-jira <ISSUE-KEY>`
- `plugins/code/commands/deslop.md` with frontmatter `name: deslop` → `/deslop`
- `plugins/code/commands/refactor.md` with frontmatter `name: refactor` → `/refactor`
- `plugins/business-analyst/commands/business-analyst.md` with frontmatter `name: business-analyst` → `/business-analyst`
- `plugins/code/commands/code-review.md` with frontmatter `name: code-review`
- `plugins/google-workspace/skills/google-workspace/SKILL.md` with frontmatter `name: google-workspace`
- `plugins/google-workspace/commands/google-workspace.md` with frontmatter `name: google-workspace` → `/google-workspace`
- `plugins/google-cloud/skills/google-cloud/SKILL.md` with frontmatter `name: google-cloud`
- `plugins/google-cloud/commands/google-cloud.md` with frontmatter `name: google-cloud` → `/google-cloud`
- `plugins/freshservice/commands/freshservice.md` → `/freshservice`
- `plugins/vault/commands/vault.md` → `/vault`
- `plugins/grafana/commands/grafana.md` → `/grafana`
- `plugins/cloudflare/commands/cloudflare.md` → `/cloudflare`
- `plugins/compose/skills/compose/SKILL.md` with frontmatter `name: compose`
- `plugins/compose/commands/compose.md` with frontmatter `name: compose` → `/compose`
- `plugins/framework/skills/framework/SKILL.md` with frontmatter `name: framework`
- `plugins/framework/commands/framework.md` with frontmatter `name: framework` → `/framework`
- `plugins/kubernetes/commands/kubernetes.md` → `/kubernetes`


### Slash command names

Skills, rules, and agents stay plugin-prefixed (`code-deslop`, `code-refactor`).

**Commands** that are meant to be typed as short slash UX may use the short
name as frontmatter `name:` and filename (for example `deslop`, `refactor` →
`/deslop`, `/refactor`; `jira`, `confluence` under `plugins/atlassian/` →
`/jira`, `/confluence`). Those commands must still live under the owning
plugin and invoke the prefixed skill (`atlassian` / `atlassian-jira-*` /
`atlassian-confluence-*`). Plugin-named commands (for example
`business-analyst` → `/business-analyst`) follow the same stem/`name:` match
rule.

### Hard requirements

1. **Directory / file stem matches frontmatter `name:`** for skills and agents.
2. **Do not leave `global-*` assets inside non-`global` plugins.**
3. **Do not invent a second prefix** inside a plugin (no `code-global-*`, no
   bare `python.mdc` under `plugins/code/rules/`).
4. When moving an asset between plugins, **rename it** and update all
   cross-references in the same change.
5. Cross-plugin references use the **full prefixed name** (for example
   `code-technical-lead`, `business-analyst-planner`, `browser-automation`).

### What goes where

| Short key | Owns |
| --- | --- |
| `global` | Standing posture, writing/policy craft (not SDLC tiers, not commit format) |
| `code` | Language/file-type + popular framework standards (React, Next.js, Flask, FastAPI), secure coding, Conventional Commits, coding workflow, worktrees/merge, coding agents |
| `business-analyst` | Business analysis, multi-step planner, external researcher (optional) |
| `agentmemory` | AgentMemory MCP recall/capture (always) + on-demand ops (optional) |
| `atlassian` | Unified Jira + Confluence craft (optional) |
| `github` | Agnostic GitHub PR checks/comments + Actions CI craft (optional) |
| `jenkins` | Agnostic Jenkins builds + pipeline CI craft (optional) |
| `browser` | Browser QA skill (optional) |
| `drawio` | `.drawio` author/repair craft + editor triage (optional) |
| `lucidchart` | Lucidchart Standard Import author/repair + `.lucid` packaging (optional) |
| `google-workspace` | Gmail + Drive + Calendar + Docs/Sheets (optional) |
| `google-cloud` | GCP projects + Compute/GKE + GCS with safety gates (optional) |
| `freshservice` | Freshservice ITSM create gates + ticket shape (optional) |
| `vault` | Vault secrets/PKI + leak refuse (optional) |
| `grafana` | Dashboards, Explore, incidents, alerting (optional) |
| `cloudflare` | DNS record craft with destructive gates (optional) |
| `compose` | Docker Compose layout/ops with destructive gates (optional) |
| `framework` | Framework monorepo craft: addon isolation/substrate, Docker ops, parity, ceremony hooks, thin host overlays (optional) |
| `kubernetes` | Agnostic pod/event/log triage (optional; site overlays stay in private `homelab`) |
| `proxmox` | Proxmox VE inventory + gated VM/LXC ops (optional) |
| `argocd` | Argo CD app status + gated sync (optional) |
| `prometheus` | PromQL discover/query via MCP (optional) |
| `graylog` | Log search via MCP with redaction (optional) |
| `minio` | MinIO/S3 buckets/objects with delete gates (optional) |
| `velero` | Velero backup/restore inventory + gated mutate (optional) |
| `fortigate` | FortiGate inventory + gated policy changes (optional) |
| `yarr` | *arr / Plex / qBit / Seerr fleet via yarr MCP (optional) |

## Plugin quality bar (required for craft plugins)

Every plugin under `plugins/` except `global` must ship:

1. **Primary skill** with Gate + Load map + Defaults (skip when unauthorized).
2. **`docs/<short>-workflow.drawio`** (or `<short>-*-workflow.drawio` for
   multi-surface plugins like `atlassian`) mapping the gate → act → end path.
3. **`README.md`** listing rules, skills, commands, and the workflow diagram.
4. **Manifests:** `.cursor-plugin/plugin.json`, `.claude-plugin/plugin.json`,
   `.codex-plugin/plugin.json`, and entries in all four root catalogs.

`global` is exempt from the workflow drawio (standing posture, not a gated
product surface).

## Commits

Use Conventional Commits (`code-commit-messages`).

**Expectation for this repo:** after every change, commit and push to `origin`
on the current branch. Do not wait for the user to ask. Skip only when the user
explicitly says not to commit or push.

## Validation checklist (before commit)

- [ ] New/renamed skills/rules/agents use the owning plugin’s prefix
- [ ] Commands use the plugin prefix **or** an allowed short slash name that
      invokes the prefixed skill (`deslop` → `code-deslop`, `refactor` →
      `code-refactor`, `jira` / `confluence` → `atlassian`, `github` /
      `jenkins` → matching plugin skill)
- [ ] Skill/agent/command `name:` frontmatter matches the directory or file stem
- [ ] All four marketplace JSON files list the plugin (if new)
- [ ] New plugins also ship `.codex-plugin/plugin.json` (Codex)
- [ ] Craft plugins meet the quality bar (skill gate + workflow drawio + README)
- [ ] `python3 scripts/validate_marketplace.py` passes
- [ ] READMEs for touched plugins list the new names
- [ ] No references to old unprefixed or wrong-plugin names remain
- [ ] Homelab private assets are not reintroduced under this public marketplace
