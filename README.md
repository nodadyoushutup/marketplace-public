<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/mark-white.svg">
    <img src="docs/assets/mark-black.svg" alt="Marketplace Public" width="96" height="96">
  </picture>
</p>

<h1 align="center">Marketplace Public</h1>

Public marketplace of portable Agent **rules**, **skills**, and **agents** for
**Claude Code**, **Cursor**, **GitHub Copilot**, and **OpenAI Codex**.

Core posture, coding, planning, Atlassian, GitHub, and draw.io craft moved to
[`archentic/marketplace`](https://github.com/archentic/marketplace). This repo
keeps the optional infra and service stacks; pair it with that marketplace.

## Install — Claude Code

```shell
/plugin marketplace add nodadyoushutup/marketplace-public
/plugin install nodadyoushutup-<short>@nodadyoushutup-marketplace-public
/reload-plugins
```

## Install — Cursor

1. Open **Dashboard → Settings → Plugins**.
2. Import: `https://github.com/nodadyoushutup/marketplace-public`
3. Install the plugins you need.

## Install — GitHub Copilot CLI

```shell
copilot plugin marketplace add nodadyoushutup/marketplace-public
copilot plugin install nodadyoushutup-<short>@nodadyoushutup-marketplace-public
```

## Install — OpenAI Codex

```shell
codex plugin marketplace add nodadyoushutup/marketplace-public
```

## Plugins

Marketplace `name` is `nodadyoushutup-<short>`; folders and asset prefixes stay
short (`jenkins-*`, `vault-*`, …).

| Marketplace id | Folder | What it is |
| --- | --- | --- |
| **nodadyoushutup-agentmemory** | `plugins/agentmemory/` | Gated AgentMemory recall/capture (+ on-demand ops) |
| **nodadyoushutup-jenkins** | `plugins/jenkins/` | Agnostic Jenkins builds + pipeline CI craft |
| **nodadyoushutup-browser** | `plugins/browser/` | Browser QA (IDE browser → CLI) |
| **nodadyoushutup-lucidchart** | `plugins/lucidchart/` | Lucidchart Standard Import author/repair |
| **nodadyoushutup-google-workspace** | `plugins/google-workspace/` | Gmail + Drive + Calendar + Docs/Sheets |
| **nodadyoushutup-google-cloud** | `plugins/google-cloud/` | GCP projects + Compute/GKE + GCS |
| **nodadyoushutup-freshservice** | `plugins/freshservice/` | Freshservice ITSM create gates + ticket shape |
| **nodadyoushutup-vault** | `plugins/vault/` | Vault secrets/PKI + leak refuse |
| **nodadyoushutup-grafana** | `plugins/grafana/` | Dashboards, Explore, incidents, alerting |
| **nodadyoushutup-cloudflare** | `plugins/cloudflare/` | DNS record craft with destructive gates |
| **nodadyoushutup-compose** | `plugins/compose/` | Docker Compose layout/ops + destructive gates |
| **nodadyoushutup-kubernetes** | `plugins/kubernetes/` | Agnostic pod/event/log triage |
| **nodadyoushutup-proxmox** | `plugins/proxmox/` | Proxmox VE inventory + gated VM ops |
| **nodadyoushutup-argocd** | `plugins/argocd/` | Argo CD apps + gated sync |
| **nodadyoushutup-prometheus** | `plugins/prometheus/` | PromQL discover/query |
| **nodadyoushutup-graylog** | `plugins/graylog/` | Log search + redaction |
| **nodadyoushutup-minio** | `plugins/minio/` | MinIO/S3 buckets/objects |
| **nodadyoushutup-velero** | `plugins/velero/` | Velero backups/restores |
| **nodadyoushutup-fortigate** | `plugins/fortigate/` | FortiGate inventory + gated policies |
| **nodadyoushutup-yarr** | `plugins/yarr/` | *arr / Plex / qBit / Seerr fleet |

Plugins may also ship **commands** under `plugins/<short>/commands/`
(`/jenkins`, `/google-workspace`, `/google-cloud`, `/freshservice`, `/vault`,
`/grafana`, `/cloudflare`, `/compose`, `/kubernetes`, `/proxmox`, `/argocd`,
`/prometheus`, `/graylog`, `/minio`, `/velero`, `/fortigate`, `/yarr`, …).

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
