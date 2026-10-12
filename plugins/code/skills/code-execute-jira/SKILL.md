---
name: code-execute-jira
description: >-
  Execute a named Jira issue through an isolated worktree to an open GitHub
  PR. Stop when the PR is ready — never merge, never mark the issue Done.
  Use when the user runs /code-execute-jira or asks to execute a Jira key
  through PR.
---

# Execute Jira issue (worktree → PR)

Own one named Jira issue from read through an open pull request. Hand the
merge decision back to the operator.

## Gate

- **Issue key required** this turn (slash argument or explicit key in the
  message). No key → ask once; if still missing, stop.
- Prefer a ready **Jira / Atlassian MCP** to read the issue and a ready
  **GitHub MCP** to open the PR (`global-mcp-first`). Fall back to CLI only
  after MCP fails or is absent.
- Skip when the ask is create-only filing (that stays `/jira` /
  `business-analyst`) or ordinary coding with no key.

## This command authorizes

| Allowed | Forbidden |
| --- | --- |
| Rename chat/session title to the issue key | Merge the PR |
| Worktree isolation (`code-worktrees`) | Force-push / rewrite shared history |
| Commits + push on the issue-key branch | Mark the issue **Done** |
| Open one PR against the default remote branch | Auto-pick a different issue |
| Transition toward **In Progress** when board/status craft applies | Invent project, board, or epic ids |

Host overlays may add multi-remote or live-refresh steps. Follow them when
present. Do not invent product-addon identity in portable guidance.

## Steps

1. **Resolve the key** — normalize the argument (trim whitespace). Use that
   exact key everywhere (branch name, chat title, PR link text).
2. **Read the issue** — description, acceptance criteria, comments, links,
   attachments. Treat Requirements + AC as the success bar.
3. **Hard blocker gate** — before any other work, inspect inbound **Blocks**
   links (`is blocked by`). Follow `atlassian-jira-status` blocker rules:
   - Open inbound blocker → hard-stop. Report the blocking key(s). Do not
     rename, branch, or implement.
   - Outbound `blocks` links do not gate this run.
   - API field map on Blocks links (other issue’s role): `outward_issue` =
     UI `is blocked by` (gate); `inward_issue` = UI `blocks` (ignore).
4. **Rename chat** — set the session title to **exactly** the issue key
   (Cursor: `rename_chat`). This command is the operator’s explicit rename
   request for this chat only.
5. **Status** — load `atlassian-jira-status`. Move backlog → board only when
   the operator named a board id (never invent). Then transition to
   `In Progress`. Never jump to In Progress from backlog alone when board
   moves apply.
6. **Isolate** — If the host overlay forbids git worktrees, branch in the
   open checkout with the issue-key name and do not create a worktree.
   Otherwise load `code-worktrees`. Branch and worktree name = the issue
   key. Record the live checkout path. Do not call `move_agent_to_root`.
   Stay on the open checkout only when isolation is off or creation fails
   with no host fallback.
7. **Implement** — load `code-workflow`. Satisfy Requirements and AC with
   the smallest reversible change. Stay in Agent mode.
8. **Verify** — load `code-verification-before-completion`. Prefer owner /
   unit tests the repo already runs. Do not start Docker/Compose unless the
   issue text explicitly requires a visual/GUI check.
9. **Ship to PR (not merge)**
   - Conventional Commits (`code-commit-messages`).
   - Push the issue-key branch.
   - Open a PR against the repo’s default remote branch.
   - Title: Conventional Commits shape.
   - Body: short what/why bullets; add a tracker browse link only when the
     host already provides a site URL. No Test plan unless this turn asks.
   - Assign per host GitHub assignee pref when set; otherwise author / `@me`.
   - Prefer GitHub MCP (`github` skill) when ready.
10. **Handoff and stop**
    - Final reply: one–three sentence plain-English summary of what changed,
      plus the **PR URL** and that merge is **manual**.
    - Optional: Jira comment with the same summary and the PR URL (not Done).
    - Leave the worktree on disk. Do not merge. Do not mark Done.

## Done when

All of:

- Blocker gate passed (or hard-stopped with blocker keys)
- Chat title is the issue key
- Requirements and AC satisfied with verify evidence
- Issue-key branch pushed and PR opened
- Operator has the PR URL and a clear “ready to merge” handoff

Not Done: PR merged, live refresh after merge, or tracker **Done**. Those
wait for an explicit later ask after the operator merges.
