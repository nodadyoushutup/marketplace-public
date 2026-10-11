#!/usr/bin/env python3
"""Generate compact docs/<short>-workflow.drawio files for craft plugins.

Idempotent: skips when the target already exists unless --force.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"

# Ambient + spine copy per plugin. Keep short — diagram is a map, not a novel.
SPECS: dict[str, dict[str, str]] = {
    "browser": {
        "title": "Browser QA Workflow",
        "ambient": (
            "AMBIENT — GUI QA&#10;&#10;"
            "Priority&#10;1 IDE browser MCP&#10;2 agent-browser CLI&#10;3 WebFetch/curl (read-only)&#10;&#10;"
            "Refuse&#10;no localhost URLs to user&#10;no private headless when MCP ready&#10;&#10;"
            "Pair: global-host-url · global-mcp-first"
        ),
        "gate": "gate · browser QA?&#10;explicit open / click / form /&#10;screenshot / scrape ask",
        "skip": "skip — no GUI work&#10;ordinary coding; do not&#10;open a browser for sport",
        "act": "drive browser&#10;IDE MCP tools first;&#10;CLI only if MCP unusable",
        "end_ok": "END — URL + assertion&#10;(+ screenshot path if taken)",
    },
    "github": {
        "title": "GitHub Workflow",
        "ambient": (
            "AMBIENT — agnostic SCM&#10;&#10;"
            "Never invent&#10;owner/repo · PR · workflow id&#10;&#10;"
            "MCP first when ready&#10;Pair: code-workflow · code-yaml"
        ),
        "gate": "gate · GitHub work?&#10;PR / checks / comments /&#10;Actions ask or named PR",
        "skip": "skip — no GitHub&#10;ordinary coding; do not&#10;open PRs to cover work",
        "act": "act via MCP&#10;checks · comments ·&#10;workflow YAML hygiene",
        "end_ok": "END — evidence&#10;(check conclusion / URL)",
    },
    "jenkins": {
        "title": "Jenkins Workflow",
        "ambient": (
            "AMBIENT — agnostic CI&#10;&#10;"
            "Never invent&#10;job name · node · queue id&#10;&#10;"
            "MCP first when ready&#10;Pair: code-workflow"
        ),
        "gate": "gate · Jenkins work?&#10;build / job / pipeline ask&#10;or named job",
        "skip": "skip — no Jenkins&#10;ordinary coding; do not&#10;trigger builds for sport",
        "act": "act via MCP&#10;build · console ·&#10;pipeline craft",
        "end_ok": "END — build result&#10;+ console evidence",
    },
    "google-workspace": {
        "title": "Google Workspace Workflow",
        "ambient": (
            "AMBIENT — Workspace&#10;&#10;"
            "Never invent&#10;ids · emails · tokens&#10;&#10;"
            "Outbound needs verb&#10;draft-before-send&#10;&#10;"
            "MCP first when ready&#10;Pair: google-cloud (GCP)"
        ),
        "gate": "gate · Workspace?&#10;Gmail / Drive / Calendar /&#10;Docs / Sheets ask",
        "skip": "skip — no Workspace&#10;ordinary coding; do not&#10;touch mailbox for sport",
        "act": "route + act&#10;gmail · drive · calendar ·&#10;docs/sheets rules",
        "end_ok": "END — id / link&#10;no secrets in chat",
    },
    "google-cloud": {
        "title": "Google Cloud Workflow",
        "ambient": (
            "AMBIENT — GCP&#10;&#10;"
            "Never invent&#10;project · zone · bucket&#10;&#10;"
            "Read-only default&#10;delete/IAM need verb&#10;&#10;"
            "MCP first; else gcloud&#10;Pair: kubernetes · vault"
        ),
        "gate": "gate · GCP work?&#10;project / compute / GKE /&#10;GCS ask or named id",
        "skip": "skip — no GCP&#10;ordinary coding; do not&#10;gcloud for sport",
        "act": "inventory → act&#10;compute · storage;&#10;safety on delete/IAM",
        "end_ok": "END — project +&#10;resource (no keys)",
    },
    "freshservice": {
        "title": "Freshservice Workflow",
        "ambient": (
            "AMBIENT — ITSM&#10;&#10;"
            "Never invent&#10;workspace · group · requester&#10;&#10;"
            "Create-only default&#10;honest status&#10;&#10;"
            "Pair: business-analyst"
        ),
        "gate": "gate · ITSM work?&#10;ticket / incident ask&#10;or named ticket id",
        "skip": "skip — ticketless&#10;ordinary coding; do not&#10;ask to file",
        "act": "create / update&#10;shape body; status honest;&#10;MCP when ready",
        "end_ok": "END — ticket id&#10;create-only stops here",
    },
    "vault": {
        "title": "Vault Workflow",
        "ambient": (
            "AMBIENT — secrets&#10;&#10;"
            "Never invent&#10;mount · path · role&#10;&#10;"
            "Land in Vault&#10;not in chat / commits&#10;&#10;"
            "Always: vault-refuse-leak"
        ),
        "gate": "gate · Vault work?&#10;secret / mount / PKI ask&#10;or named path",
        "skip": "skip — no Vault&#10;ordinary coding; do not&#10;open Vault for sport",
        "act": "read / write / PKI&#10;via MCP; refuse leaks;&#10;delete needs verb",
        "end_ok": "END — path only&#10;(no secret material)",
    },
    "grafana": {
        "title": "Grafana Workflow",
        "ambient": (
            "AMBIENT — observability&#10;&#10;"
            "Never invent&#10;uid · datasource · folder&#10;&#10;"
            "MCP first when ready&#10;Pair: kubernetes · prometheus"
        ),
        "gate": "gate · Grafana?&#10;dashboard / explore /&#10;alert / incident ask",
        "skip": "skip — no Grafana&#10;ordinary coding; do not&#10;open Explore for sport",
        "act": "query / edit&#10;dashboards · explore ·&#10;alerting · incidents",
        "end_ok": "END — uid / link&#10;+ what changed",
    },
    "cloudflare": {
        "title": "Cloudflare DNS Workflow",
        "ambient": (
            "AMBIENT — DNS&#10;&#10;"
            "Never invent&#10;zone id · record id&#10;&#10;"
            "Prefer update&#10;over delete+create&#10;&#10;"
            "Deletes need verb"
        ),
        "gate": "gate · DNS work?&#10;Cloudflare / record ask&#10;or named FQDN",
        "skip": "skip — no DNS&#10;ordinary coding; do not&#10;touch zones for sport",
        "act": "list → change&#10;create/update via MCP;&#10;safety on delete/bulk",
        "end_ok": "END — FQDN + type&#10;+ content (no tokens)",
    },
    "compose": {
        "title": "Compose Workflow",
        "ambient": (
            "AMBIENT — Compose&#10;&#10;"
            "First COMPOSE_FILE&#10;= project directory&#10;&#10;"
            "Anchor at root&#10;then overlays&#10;&#10;"
            "down -v needs verb&#10;No .env dumps in chat"
        ),
        "gate": "gate · Compose work?&#10;docker compose / stack /&#10;overlay / profile ask",
        "skip": "skip — no Compose&#10;ordinary coding; do not&#10;touch stacks for sport",
        "act": "resolve dir → config&#10;ops via compose CLI;&#10;safety on down -v",
        "end_ok": "END — project +&#10;services (no secrets)",
    },
    "framework": {
        "title": "Framework Workflow",
        "ambient": (
            "AMBIENT — monorepo&#10;&#10;"
            "Addon isolation&#10;substrate · modularity&#10;&#10;"
            "Pair public plugins&#10;global · code · atlassian&#10;&#10;"
            "Ceremony hooks floor&#10;No secret dumps in chat"
        ),
        "gate": "gate · framework?&#10;addon / docker / parity /&#10;ceremony / monorepo ask",
        "skip": "skip — not framework&#10;use other public plugins;&#10;do not invent overlays",
        "act": "route via load map&#10;isolation · docker ·&#10;parity · host overlays",
        "end_ok": "END — change +&#10;ceremony evidence",
    },
    "kubernetes": {
        "title": "Kubernetes Triage Workflow",
        "ambient": (
            "AMBIENT — cluster&#10;&#10;"
            "Never invent&#10;context · ns · pod&#10;&#10;"
            "Read-only default&#10;destructive needs verb&#10;&#10;"
            "Site overlays: private homelab"
        ),
        "gate": "gate · k8s work?&#10;pod / ns / cluster ask&#10;or named workload",
        "skip": "skip — no cluster&#10;ordinary coding; do not&#10;kubectl for sport",
        "act": "triage via MCP&#10;status · events · logs;&#10;safety for delete/exec",
        "end_ok": "END — diagnosis&#10;+ next action",
    },
    "drawio": {
        "title": "Drawio Craft Workflow",
        "ambient": (
            "AMBIENT — .drawio&#10;&#10;"
            "Layout contract first&#10;no overlap · bus edges&#10;&#10;"
            "Author vs repair&#10;editor triage ≠ rewrite"
        ),
        "gate": "gate · diagram work?&#10;new / redesign / repair&#10;or named .drawio",
        "skip": "skip — no diagram&#10;ordinary coding",
        "act": "author or repair&#10;drawio-layout + recipes;&#10;triage editor false alarms",
        "end_ok": "END — readable graph&#10;AABB-verified edges",
    },
    "lucidchart": {
        "title": "Lucidchart SI Workflow",
        "ambient": (
            "AMBIENT — Lucid SI&#10;&#10;"
            "Source: *.lucid.json&#10;Package → .lucid zip&#10;&#10;"
            "New doc on import&#10;SI cannot patch live"
        ),
        "gate": "gate · Lucid work?&#10;author / repair / package&#10;or named *.lucid.json",
        "skip": "skip — no Lucid&#10;ordinary coding",
        "act": "author / repair SI&#10;then package_lucid.py;&#10;create new Lucid doc",
        "end_ok": "END — .lucid +&#10;import evidence",
    },
    "agentmemory": {
        "title": "AgentMemory Workflow",
        "ambient": (
            "AMBIENT — memory MCP&#10;&#10;"
            "Gate: skip if disconnected&#10;&#10;"
            "Everyday&#10;lesson_recall · smart_search&#10;lesson_save · memory_save&#10;&#10;"
            "No secrets in memory"
        ),
        "gate": "gate · memory connected?&#10;and task needs recall/save",
        "skip": "skip — disconnected&#10;or routine rename/typo&#10;with no architecture risk",
        "act": "recall → verify → act&#10;capture only durable&#10;verified insights",
        "end_ok": "END — used leads&#10;and/or saved entry",
    },
    "proxmox": {
        "title": "Proxmox Workflow",
        "ambient": (
            "AMBIENT — hypervisor&#10;&#10;"
            "Never invent&#10;node · VMID · storage&#10;&#10;"
            "Read-only default&#10;Respect sacred VMs&#10;&#10;"
            "MCP first when ready"
        ),
        "gate": "gate · Proxmox?&#10;VM / LXC / node ask&#10;or named VMID",
        "skip": "skip — no hypervisor&#10;ordinary coding",
        "act": "inventory / gated ops&#10;status first; power/clone&#10;only with explicit verb",
        "end_ok": "END — VMID + status&#10;(no credentials)",
    },
    "argocd": {
        "title": "Argo CD Workflow",
        "ambient": (
            "AMBIENT — GitOps&#10;&#10;"
            "Never invent&#10;app · project · ns&#10;&#10;"
            "Status before sync&#10;Pair: kubernetes"
        ),
        "gate": "gate · Argo CD?&#10;Application / sync ask&#10;or named app",
        "skip": "skip — no GitOps&#10;ordinary coding",
        "act": "get / tree / events&#10;sync only with explicit&#10;verb naming the app",
        "end_ok": "END — app health&#10;+ sync result",
    },
    "prometheus": {
        "title": "Prometheus Workflow",
        "ambient": (
            "AMBIENT — metrics&#10;&#10;"
            "Discover first&#10;labels · series · targets&#10;&#10;"
            "rate then sum&#10;Pair: grafana"
        ),
        "gate": "gate · Prometheus?&#10;PromQL / metrics /&#10;targets ask",
        "skip": "skip — no metrics&#10;ordinary coding",
        "act": "discover → query&#10;instant/range via MCP;&#10;bound cardinality",
        "end_ok": "END — query +&#10;short finding",
    },
    "graylog": {
        "title": "Graylog Workflow",
        "ambient": (
            "AMBIENT — logs&#10;&#10;"
            "Never invent&#10;stream id&#10;&#10;"
            "Narrow time range&#10;Redact secrets"
        ),
        "gate": "gate · Graylog?&#10;log search ask",
        "skip": "skip — no Graylog&#10;ordinary coding",
        "act": "search / aggregate&#10;via MCP; summarize;&#10;no secret dumps",
        "end_ok": "END — finding&#10;+ query used",
    },
    "minio": {
        "title": "MinIO Workflow",
        "ambient": (
            "AMBIENT — object store&#10;&#10;"
            "Never invent&#10;bucket · object key&#10;&#10;"
            "No access keys in chat&#10;Deletes need verb"
        ),
        "gate": "gate · MinIO/S3?&#10;bucket / object ask",
        "skip": "skip — no object store&#10;ordinary coding",
        "act": "list → read/write&#10;via MCP; safety on&#10;delete / public ACL",
        "end_ok": "END — bucket/key&#10;(no credentials)",
    },
    "velero": {
        "title": "Velero Workflow",
        "ambient": (
            "AMBIENT — backups&#10;&#10;"
            "Never invent&#10;backup · schedule name&#10;&#10;"
            "Restore = data risk&#10;Pair: kubernetes · argocd"
        ),
        "gate": "gate · Velero?&#10;backup / restore ask",
        "skip": "skip — no Velero&#10;ordinary coding",
        "act": "inventory first&#10;create/restore only&#10;with explicit verb",
        "end_ok": "END — backup name&#10;+ phase",
    },
    "fortigate": {
        "title": "FortiGate Workflow",
        "ambient": (
            "AMBIENT — firewall&#10;&#10;"
            "Never invent&#10;policy · address · VDOM&#10;&#10;"
            "Read-only default&#10;ACL changes need verb"
        ),
        "gate": "gate · FortiGate?&#10;firewall / policy ask",
        "skip": "skip — no firewall&#10;ordinary coding",
        "act": "inventory / health&#10;mutate only with&#10;explicit verb + risk",
        "end_ok": "END — policy id&#10;+ change summary",
    },
    "yarr": {
        "title": "Yarr Media Fleet Workflow",
        "ambient": (
            "AMBIENT — *arr / Plex&#10;&#10;"
            "Never invent&#10;ids · torrent hashes&#10;&#10;"
            "Read/search default&#10;Site libraries: private homelab"
        ),
        "gate": "gate · media fleet?&#10;*arr / Plex / qBit /&#10;Seerr / Tautulli ask",
        "skip": "skip — no media ops&#10;ordinary coding",
        "act": "search / status&#10;via yarr MCP; mutate&#10;only with explicit verb",
        "end_ok": "END — title/id&#10;+ action taken",
    },
}


def render(short: str, spec: dict[str, str]) -> str:
    title = escape(spec["title"])
    ambient = spec["ambient"]  # already uses &#10;
    gate = spec["gate"].replace("\n", "&#10;")
    skip = spec["skip"].replace("\n", "&#10;")
    act = spec["act"].replace("\n", "&#10;")
    end_ok = spec["end_ok"].replace("\n", "&#10;")
    diagram_id = f"{short}-workflow"

    return f"""<!-- LAYOUT CONTRACT
     LEGEND    x=40..300
     AMBIENT   x=40..300 (below legend)
     LEFT      x=400..720 — skip / END skip
     SPINE     x=780..1160 — gate → act → END
     BUSES: x=350 skip drain
-->
<mxfile host="app.diagrams.net" agent="cursor" version="24.0.0">
  <diagram id="{diagram_id}" name="{title}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="legend" value="Legend&#10;&#10;Boxes&#10;blue = work phase&#10;green = finish&#10;gray = START / END / skip&#10;&#10;Lines&#10;black = next step&#10;green = skip / finish" style="rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=14;spacingRight=14;spacingTop=12;spacingBottom=12;fontSize=11;fillColor=#f5f5f5;strokeColor=#bbbbbb;fontColor=#222222" parent="1" vertex="1">
          <mxGeometry x="40" y="40" width="260" height="220" as="geometry"/>
        </mxCell>
        <mxCell id="ambient" value="{ambient}" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 8;align=left;verticalAlign=top;spacingLeft=14;spacingRight=14;spacingTop=12;spacingBottom=12;fontSize=11;fontStyle=1;fillColor=#eeeeee;strokeColor=#999999;strokeWidth=2;fontColor=#333333" parent="1" vertex="1">
          <mxGeometry x="40" y="300" width="260" height="320" as="geometry"/>
        </mxCell>

        <mxCell id="start" value="START — user ask" style="ellipse;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=13;fontStyle=1;fillColor=#e0e0e0;strokeColor=#666666;fontColor=#222222" parent="1" vertex="1">
          <mxGeometry x="780" y="40" width="380" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="gate" value="{gate}" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacingLeft=12;spacingRight=12;fontSize=12;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#12305B" parent="1" vertex="1">
          <mxGeometry x="780" y="160" width="380" height="110" as="geometry"/>
        </mxCell>
        <mxCell id="skip" value="{skip}" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacingLeft=12;spacingRight=12;fontSize=12;fillColor=#e0e0e0;strokeColor=#666666;fontColor=#222222" parent="1" vertex="1">
          <mxGeometry x="400" y="160" width="320" height="110" as="geometry"/>
        </mxCell>
        <mxCell id="act" value="{act}" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacingLeft=12;spacingRight=12;fontSize=12;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#12305B" parent="1" vertex="1">
          <mxGeometry x="780" y="320" width="380" height="120" as="geometry"/>
        </mxCell>
        <mxCell id="end_ok" value="{end_ok}" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacingLeft=12;spacingRight=12;fontSize=12;fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#12401A" parent="1" vertex="1">
          <mxGeometry x="780" y="490" width="380" height="100" as="geometry"/>
        </mxCell>
        <mxCell id="end_skip" value="END — stay out" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacingLeft=12;spacingRight=12;fontSize=12;fillColor=#e0e0e0;strokeColor=#666666;fontColor=#222222" parent="1" vertex="1">
          <mxGeometry x="400" y="490" width="320" height="100" as="geometry"/>
        </mxCell>

        <mxCell id="e_start_gate" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;jumpStyle=arc;jumpSize=10;exitX=0.5;exitY=1;entryX=0.5;entryY=0" parent="1" source="start" target="gate" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_gate_skip" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;jumpStyle=arc;jumpSize=10;strokeColor=#82b366;exitX=0;exitY=0.5;entryX=1;entryY=0.5" parent="1" source="gate" target="skip" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="chip_skip" value="no" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=10;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#333333" parent="1" vertex="1">
          <mxGeometry x="730" y="195" width="40" height="22" as="geometry"/>
        </mxCell>
        <mxCell id="e_gate_act" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;jumpStyle=arc;jumpSize=10;exitX=0.5;exitY=1;entryX=0.5;entryY=0" parent="1" source="gate" target="act" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="chip_yes" value="yes" style="rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=10;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#333333" parent="1" vertex="1">
          <mxGeometry x="920" y="278" width="40" height="22" as="geometry"/>
        </mxCell>
        <mxCell id="e_act_end" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;jumpStyle=arc;jumpSize=10;strokeColor=#82b366;exitX=0.5;exitY=1;entryX=0.5;entryY=0" parent="1" source="act" target="end_ok" edge="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e_skip_end" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;jumpStyle=arc;jumpSize=10;strokeColor=#82b366;exitX=0.5;exitY=1;entryX=0.5;entryY=0" parent="1" source="skip" target="end_skip" edge="1">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="350" y="215"/>
              <mxPoint x="350" y="540"/>
            </Array>
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    wrote = 0
    for short, spec in sorted(SPECS.items()):
        docs = PLUGINS / short / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        target = docs / f"{short}-workflow.drawio"
        if target.exists() and not args.force:
            print(f"skip existing {target.relative_to(ROOT)}")
            continue
        target.write_text(render(short, spec), encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")
        wrote += 1
    print(f"done ({wrote} written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
