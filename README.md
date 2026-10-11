# nodadyoushutup-marketplace-public

Public marketplace of portable Agent **rules**, **skills**, and **agents** for
**Claude Code**, **Cursor**, **GitHub Copilot**, and **OpenAI Codex**.

## Install — Claude Code

```shell
/plugin marketplace add nodadyoushutup/marketplace-public
/plugin install nodadyoushutup-global@nodadyoushutup-marketplace-public
/plugin install nodadyoushutup-code@nodadyoushutup-marketplace-public
# optional plugins use the same @nodadyoushutup-marketplace-public form
/reload-plugins
```

## Install — Cursor

1. Open **Dashboard → Settings → Plugins**.
2. Import: `https://github.com/nodadyoushutup/marketplace-public`
3. Install **nodadyoushutup-global** + **nodadyoushutup-code**, plus optional
   plugins as needed.

## Install — GitHub Copilot CLI

```shell
copilot plugin marketplace add nodadyoushutup/marketplace-public
copilot plugin install nodadyoushutup-global@nodadyoushutup-marketplace-public
copilot plugin install nodadyoushutup-code@nodadyoushutup-marketplace-public
# optional plugins use the same @nodadyoushutup-marketplace-public form
```

## Install — OpenAI Codex

```shell
codex plugin marketplace add nodadyoushutup/marketplace-public
```

## Plugins

Marketplace `name` is `nodadyoushutup-<short>`; folders and asset prefixes stay
short (`code-*`, `global-*`, …).

| Marketplace id | Folder | What it is |
| --- | --- | --- |
| **nodadyoushutup-global** | `plugins/global/` | Standing posture, writing/policy craft |
| **nodadyoushutup-code** | `plugins/code/` | Language + framework standards (React/Next/Flask/FastAPI, YAML/K8s), secure coding, Conventional Commits, coding workflow, agents |
| **nodadyoushutup-business-analyst** | `plugins/business-analyst/` | Business analysis, planner, external researcher |
| **nodadyoushutup-agentmemory** | `plugins/agentmemory/` | Gated AgentMemory recall/capture (+ on-demand ops) |
| **nodadyoushutup-atlassian** | `plugins/atlassian/` | Unified Jira + Confluence craft |
| **nodadyoushutup-github** | `plugins/github/` | Agnostic GitHub PR checks/comments + Actions CI craft |
| **nodadyoushutup-jenkins** | `plugins/jenkins/` | Agnostic Jenkins builds + pipeline CI craft |
| **nodadyoushutup-browser** | `plugins/browser/` | Browser QA (IDE browser → CLI) |
| **nodadyoushutup-drawio** | `plugins/drawio/` | `.drawio` author/repair + editor triage |
| **nodadyoushutup-lucidchart** | `plugins/lucidchart/` | Lucidchart Standard Import author/repair |
| **nodadyoushutup-google-workspace** | `plugins/google-workspace/` | Gmail + Drive + Calendar + Docs/Sheets |
| **nodadyoushutup-google-cloud** | `plugins/google-cloud/` | GCP projects + Compute/GKE + GCS |
| **nodadyoushutup-freshservice** | `plugins/freshservice/` | Freshservice ITSM create gates + ticket shape |
| **nodadyoushutup-vault** | `plugins/vault/` | Vault secrets/PKI + leak refuse |
| **nodadyoushutup-grafana** | `plugins/grafana/` | Dashboards, Explore, incidents, alerting |
| **nodadyoushutup-cloudflare** | `plugins/cloudflare/` | DNS record craft with destructive gates |
| **nodadyoushutup-compose** | `plugins/compose/` | Docker Compose layout/ops + destructive gates |
| **nodadyoushutup-framework** | `plugins/framework/` | Framework monorepo craft (addons, Docker ops, parity, ceremony hooks) |
| **nodadyoushutup-kubernetes** | `plugins/kubernetes/` | Agnostic pod/event/log triage |
| **nodadyoushutup-proxmox** | `plugins/proxmox/` | Proxmox VE inventory + gated VM ops |
| **nodadyoushutup-argocd** | `plugins/argocd/` | Argo CD apps + gated sync |
| **nodadyoushutup-prometheus** | `plugins/prometheus/` | PromQL discover/query |
| **nodadyoushutup-graylog** | `plugins/graylog/` | Log search + redaction |
| **nodadyoushutup-minio** | `plugins/minio/` | MinIO/S3 buckets/objects |
| **nodadyoushutup-velero** | `plugins/velero/` | Velero backups/restores |
| **nodadyoushutup-fortigate** | `plugins/fortigate/` | FortiGate inventory + gated policies |
| **nodadyoushutup-yarr** | `plugins/yarr/` | *arr / Plex / qBit / Seerr fleet |

Plugins may also ship **commands** under `plugins/<short>/commands/` (`/deslop`,
`/refactor`, `/business-analyst`, `/atlassian`, `/jira`, `/confluence`,
`/github`, `/jenkins`, `/google-workspace`, `/google-cloud`, `/freshservice`,
`/vault`, `/grafana`, `/cloudflare`, `/compose`, `/framework`, `/kubernetes`, `/proxmox`,
`/argocd`, `/prometheus`, `/graylog`, `/minio`, `/velero`, `/fortigate`, `/yarr`, …).

## Catalog paths

| Host | Marketplace catalog | Per-plugin manifest |
| --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `.claude-plugin/plugin.json` |
| Cursor | `.cursor-plugin/marketplace.json` | `.cursor-plugin/plugin.json` |
| GitHub Copilot | `.github/plugin/marketplace.json` | `.claude-plugin/plugin.json` (Copilot also accepts this path) |
| OpenAI Codex | `.agents/plugins/marketplace.json` | `.codex-plugin/plugin.json` |

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Asset basenames must use the owning plugin’s prefix. See [AGENTS.md](AGENTS.md).

Before commit:

```shell
python3 scripts/validate_marketplace.py
```

CI runs the same check on push/PR (`.github/workflows/validate-marketplace.yml`).

To scaffold a compact gate→act workflow diagram for a craft plugin:

```shell
python3 scripts/generate_workflow_drawios.py
```
