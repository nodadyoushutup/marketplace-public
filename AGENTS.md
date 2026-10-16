# AGENTS.md — marketplace-public

Public Claude Code / Cursor / GitHub Copilot / OpenAI Codex plugin marketplace.
Root catalogs:

- `.cursor-plugin/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.github/plugin/marketplace.json` (Copilot)
- `.agents/plugins/marketplace.json` (Codex)

Plugins live under `plugins/<short>/` (for example `plugins/jenkins/`).

Marketplace / `plugin.json` **`name`** is `nodadyoushutup-<short>` (for example
`nodadyoushutup-jenkins`). Claude/Cursor catalog `source` stays the short folder
name; Copilot/Codex catalogs use `./plugins/<short>`.

Homelab **homelab** infra craft ships from the sibling
[`marketplace-private`](https://github.com/nodadyoushutup/marketplace-private)
repo — do not re-add `plugins/homelab/` here. Core posture, coding, planning,
Atlassian, GitHub, and draw.io craft (`global`, `code`, `business-analyst`,
`atlassian`, `github`, `drawio`) and the framework plugin live in
[`archentic/marketplace`](https://github.com/archentic/marketplace) — do not
re-add them here.

## Plugin prefix rule (required)

Asset basenames use the **short** plugin key (folder stem), not the full
marketplace id. Every rule, skill, and agent basename **must** use that short
prefix (kebab-case), or — for a single primary skill — the exact short name.
Commands follow the same rule; plugin-named commands (`/jenkins`, `/vault`)
match the short key.

| Short key (folder) | Marketplace id | Allowed basenames |
| --- | --- | --- |
| `agentmemory` | `nodadyoushutup-agentmemory` | `agentmemory` or `agentmemory-*` |
| `jenkins` | `nodadyoushutup-jenkins` | `jenkins` or `jenkins-*` |
| `browser` | `nodadyoushutup-browser` | `browser-*` |
| `lucidchart` | `nodadyoushutup-lucidchart` | `lucidchart-*` |
| `google-workspace` | `nodadyoushutup-google-workspace` | `google-workspace` or `google-workspace-*` |
| `google-cloud` | `nodadyoushutup-google-cloud` | `google-cloud` or `google-cloud-*` |
| `freshservice` | `nodadyoushutup-freshservice` | `freshservice` or `freshservice-*` |
| `vault` | `nodadyoushutup-vault` | `vault` or `vault-*` |
| `grafana` | `nodadyoushutup-grafana` | `grafana` or `grafana-*` |
| `cloudflare` | `nodadyoushutup-cloudflare` | `cloudflare` or `cloudflare-*` |
| `compose` | `nodadyoushutup-compose` | `compose` or `compose-*` |
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

- `plugins/jenkins/rules/jenkins-ci-from-main.mdc`
- `plugins/agentmemory/skills/agentmemory/SKILL.md` with frontmatter `name: agentmemory`
- `plugins/browser/skills/browser-automation/SKILL.md` with frontmatter `name: browser-automation`
- `plugins/jenkins/skills/jenkins/SKILL.md` with frontmatter `name: jenkins`
- `plugins/jenkins/commands/jenkins.md` with frontmatter `name: jenkins` → `/jenkins`
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
- `plugins/kubernetes/commands/kubernetes.md` → `/kubernetes`


### Slash command names

Skills, rules, and agents stay plugin-prefixed (`jenkins-ci-from-main`,
`vault-secrets`). Plugin-named **commands** use the short key as frontmatter
`name:` and filename (`jenkins` → `/jenkins`, `vault` → `/vault`), live under
the owning plugin, and invoke that plugin's prefixed skill.

### Hard requirements

1. **Directory / file stem matches frontmatter `name:`** for skills and agents.
2. **Do not leave another plugin's prefixed assets inside a plugin** (no
   `global-*` or `code-*` files here; those plugins live in `archentic/marketplace`).
3. **Do not invent a second prefix** inside a plugin (no `jenkins-global-*`, no
   bare `builds.mdc` under `plugins/jenkins/rules/`).
4. When moving an asset between plugins, **rename it** and update all
   cross-references in the same change.
5. Cross-plugin references use the **full prefixed name** (for example
   `browser-automation`, `jenkins-ci-from-main`), including references to
   `archentic/marketplace` plugins (`code-technical-lead`, `business-analyst-planner`).

### What goes where

| Short key | Owns |
| --- | --- |
| `agentmemory` | AgentMemory MCP recall/capture (always) + on-demand ops (optional) |
| `jenkins` | Agnostic Jenkins builds + pipeline CI craft (optional) |
| `browser` | Browser QA skill (optional) |
| `lucidchart` | Lucidchart Standard Import author/repair + `.lucid` packaging (optional) |
| `google-workspace` | Gmail + Drive + Calendar + Docs/Sheets (optional) |
| `google-cloud` | GCP projects + Compute/GKE + GCS with safety gates (optional) |
| `freshservice` | Freshservice ITSM create gates + ticket shape (optional) |
| `vault` | Vault secrets/PKI + leak refuse (optional) |
| `grafana` | Dashboards, Explore, incidents, alerting (optional) |
| `cloudflare` | DNS record craft with destructive gates (optional) |
| `compose` | Docker Compose layout/ops with destructive gates (optional) |
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

Every plugin under `plugins/` must ship:

1. **Primary skill** with Gate + Load map + Defaults (skip when unauthorized).
2. **`docs/<short>-workflow.drawio`** (or `<short>-*-workflow.drawio` for
   multi-surface plugins) mapping the gate → act → end path.
3. **`README.md`** listing rules, skills, commands, and the workflow diagram.
4. **Manifests:** `.cursor-plugin/plugin.json`, `.claude-plugin/plugin.json`,
   `.codex-plugin/plugin.json`, and entries in all four root catalogs.

## Commits

Use Conventional Commits (`code-commit-messages` from `archentic/marketplace`).

**Expectation for this repo:** after every change, commit and push to `origin`
on the current branch. Do not wait for the user to ask. Skip only when the user
explicitly says not to commit or push.

## Validation checklist (before commit)

- [ ] New/renamed skills/rules/agents use the owning plugin’s prefix
- [ ] Commands use the plugin prefix or the plugin-named short key that
      invokes the prefixed skill (`jenkins` → `jenkins`, `vault` → `vault`)
- [ ] Skill/agent/command `name:` frontmatter matches the directory or file stem
- [ ] All four marketplace JSON files list the plugin (if new)
- [ ] New plugins also ship `.codex-plugin/plugin.json` (Codex)
- [ ] Craft plugins meet the quality bar (skill gate + workflow drawio + README)
- [ ] `python3 scripts/validate_marketplace.py` passes
- [ ] READMEs for touched plugins list the new names
- [ ] No references to old unprefixed or wrong-plugin names remain
- [ ] Homelab private assets are not reintroduced under this public marketplace
