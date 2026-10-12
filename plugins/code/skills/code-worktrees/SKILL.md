---
name: code-worktrees
description: >-
  Isolate feature work in a git worktree under ~/.cursor/worktrees (Cursor-
  discoverable). Prefer Cursor-native remount when already in a worktree or
  when the user starts with /worktree; otherwise git worktree add and edit
  only under that path. Detect the repo default branch. Prune only on ask.
  Use when starting issue-keyed or isolation-required work.
---

# Git worktrees

Isolate when required. Stay on the open checkout when not. Do **not** call
`move_agent_to_root` / `move_agent_to_cloned_root`.

Announce only when you create, reuse, remount into, or prune an isolated tree.

## When isolation applies

Isolation is **on** when **any** of:

1. The user asked for a worktree / isolated checkout.
2. The host repo’s rules say this task is isolated (for example issue-keyed
   implement work) **and** the user did not opt out.

Isolation is **off** (stay put) when:

- No host/user isolation signal, or
- The user said work **on main**, **on live**, **in the open checkout**, or
  **skip the worktree**.

Create-only tracker asks (file a ticket, no implement verb) never open a
worktree — see `global-execute-first` / host Jira rules.

## Remount lanes (pick one)

| Lane | When | What to do |
| --- | --- | --- |
| **A — Already remounted** | Session root is already this task’s worktree (Agents Window, `/worktree`, or prior remount) | Stay. Reuse. Do not create a second tree for the same branch. |
| **B — Cursor native** | Isolation just turned on in Cursor and the user can remount | Prefer they start/continue via Agents Window or `/worktree` so the agent runs *inside* the checkout. Mention once if still on live after create — do not block waiting. |
| **C — `git worktree add`** | Claude Code, scripts, or Cursor when native remount did not happen | Create/reuse under `~/.cursor/worktrees/...` (below). Edit **only** under that path. |

Hard rule for lanes B/C when isolation is on: before every write, confirm the
target path is under the worktree root (or Shell `working_directory` is that
root). Never edit, branch, or commit issue work in the live checkout while
isolation is on.

Do **not** ask the user to type `/worktree` as a blocker. One-line mention of
native remount is fine; then proceed with lane C if still on live.

## Default branch

Resolve the start point once per create (do not hardcode `main`):

```bash
git symbolic-ref --quiet refs/remotes/origin/HEAD \
  | sed 's#^refs/remotes/origin/##'
```

Fallback order if that is empty: `main`, then `master`, then `HEAD`. Call the
result `<default-remote-branch>` (for example `origin/main`).

## Unexpected tree content — do not auto-revert

Before `git restore`, `git checkout --`, `git reset`, or any silent revert:

1. Confirm which checkout `git status` belongs to (live vs worktree).
2. Separate uncommitted dirt from content already in `HEAD`.
3. If clean or already committed: `git log` for that path. Report the commit.
   Do not discard it because this chat did not author it.

Discard only on an explicit operator ask, or when the dirt is uncommitted, you
created it this session, and undoing it *is* the task.

## Step 0 — Reuse

```bash
git worktree list
git rev-parse --show-toplevel
```

Record the open checkout path (live) before creating a tree — finish/refresh
steps need it.

| Result | Action |
| --- | --- |
| Session root is already the target worktree | Lane A — stay |
| List already has this branch or path | Use that path (lane C edits if root stayed live) |
| Otherwise | Step 1 |

## Step 1 — `git worktree add`

`<repo-directory-name>` = basename of live `git rev-parse --show-toplevel`.
`<name>` = branch the task requires (often the issue key).

```bash
git fetch origin
git worktree add -b "<name>" \
  "$HOME/.cursor/worktrees/<repo-directory-name>/<name>" \
  "origin/<default-remote-branch>"
```

If the branch already exists, omit `-b` and pass the branch as the start
point. Use `HEAD` only when no suitable `origin/<branch>` exists.

Cursor’s manager scans only
`~/.cursor/worktrees/<repo-directory-name>/<name>`. Trees elsewhere are
invisible to that scan. Do not nest the worktree inside the open checkout.

If the session root moves into the new tree on its own → lane A. If it stays
on live → lane C (absolute paths / `working_directory`). A stayed root is not
a creation failure.

**Creation failed** only when `git worktree add` fails or the path is not a
checkout of this repo. Then Step 2 — do not retry a different directory.

## Step 2 — Emergency fallback

1. If the host overlay forbids git worktrees, stop. Edit the open checkout
   on the current branch. Do not invent a directory.
2. If `git worktree add` failed and the host overlay names an emergency clone
   parent, follow that overlay. Edit by absolute path. Still no
   `move_agent_to_root`.
3. Otherwise edit the open checkout on the current branch. Say so in one
   sentence. Do not invent a directory.

## Step 3 — Setup and finish

Bootstrap the checkout you actually created (host scripts when the repo has
them). Commit from that checkout when the user asks. After required merges,
refresh the **original** live checkout from Step 0 when the host provides a
refresh helper; otherwise `git -C <live> pull` only if the user asked to
update live.

## Cleanup (never automatic on session end)

Do **not** delete a worktree because a chat ended or a hook fired.

Remove only when:

1. The user asked to delete / prune / clean worktrees, or the host runbook
   says to after merge, or
2. You are pruning **stale** trees on an explicit prune ask: branch is merged
   on the default remote branch (or deleted on origin), the tree is clean, and
   the path is under `~/.cursor/worktrees/`.

Prefer Cursor `/delete-worktree` for trees the IDE manages. Otherwise:

```bash
git worktree remove "<path>"    # fails if dirty — good
git worktree prune
```

Never `git worktree remove --force` unless the user explicitly asked to discard
that tree’s uncommitted work.
