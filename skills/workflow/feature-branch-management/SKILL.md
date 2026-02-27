---
name: feature-branch-management
description: Manage feature branches for work-item lifecycle with safe defaults. Use when creating a branch on `in-progress`, syncing with `main` before `ready-for-review`, preparing PR-ready branch state, or cleaning up merged branches locally/remotely.
metadata:
  category: workflow
license: MIT
---

# Feature Branch Management

## Goal

Manage feature branches end-to-end for work items:

- Create branch at `in-progress`
- Sync branch with `main` at `ready-for-review`
- Verify branch is PR-ready
- Clean up branch after merge

Prioritize correctness and safety first, then minimize steps and token usage.

## Use When

- Starting implementation for a work item
- Refreshing a feature branch before opening/updating a PR
- Validating branch state before PR creation
- Cleaning up merged feature branches

## Do Not Use

- For complex interactive history surgery (manual git workflow)
- To bypass protected-branch rules
- To force-delete unmerged work without explicit approval

## Inputs

- `branch`: optional explicit branch name
- `id`, `slug`: used to derive branch if `branch` is omitted
- `base`: optional base branch name, default `main`
- `sync_mode`: `rebase` (default) or `merge`
- `delete_remote`: cleanup remote branch too (default `true`)
- `force`: explicit override for destructive operations (default `false`)

## Safety Invariants (Efficacy First)

1. Fetch before any create/sync/cleanup decision.
2. Do not sync or cleanup from a dirty worktree.
3. Do not delete unmerged branches unless `force=true` and caller confirms.
4. If history is rewritten, use `--force-with-lease` only, never bare `--force`.
5. Preserve the branch recorded in work-item frontmatter; do not rename midstream.

## Branch Naming

Preferred format:

- `feature/wi-<id>-<slug>`

Accepted existing formats used in current workflows:

- `feature/wi-<id>`
- `feature/<id>-<slug>`

If multiple candidate names exist, reuse the branch already referenced by the work item.

## Operation 1: Create

### Preconditions

- Work item is transitioning to `in-progress`
- Target branch does not conflict with another active work item

### Procedure

```bash
git fetch origin <base>
```

If branch exists locally:

```bash
git switch <branch>
```

Else create from base:

```bash
git switch -c <branch> origin/<base>
```

### Output

- Current branch is `<branch>`
- Branch starts from latest `origin/<base>`

## Operation 2: Sync

### Preconditions

- On feature branch
- Worktree clean: `git status --porcelain` returns empty

### Default strategy: rebase

```bash
git fetch origin <base>
git rebase origin/<base>
```

Use when branch is single-writer and linear history is preferred.

### Alternative strategy: merge

```bash
git fetch origin <base>
git merge --no-edit origin/<base>
```

Use when branch is shared or policy discourages rewriting remote history.

### Push guidance

- If rebase rewrote commits already pushed:

```bash
git push --force-with-lease origin <branch>
```

- Otherwise:

```bash
git push origin <branch>
```

## Operation 3: Prepare for Review

Prepare-for-review is a composed check over branch state.

### Required checks

1. Clean worktree.
2. Branch is synced with `origin/<base>` (run sync if needed).
3. Branch has reviewable delta:

```bash
git rev-list --count origin/<base>..HEAD
```

1. Upstream configured:

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

1. If required by workflow, run guardrails from [guarding-branches](../aspects/guarding-branches/SKILL.md) before PR merge actions.

### Output status

- `ready`: all checks pass
- `blocked`: include blocking reasons and next command

## Operation 4: Cleanup

### Preconditions

- PR merged, or branch is confirmed merged into `origin/<base>`

### Merge verification

```bash
git fetch origin --prune <base>
git merge-base --is-ancestor <branch> origin/<base>
```

If check fails, stop unless `force=true` with explicit caller confirmation.

### Cleanup steps

Local delete:

```bash
git branch -d <branch>
```

Remote delete (default):

```bash
git push origin --delete <branch>
git fetch --prune origin
```

## Decision Rules

- Branch exists locally: switch, do not recreate.
- Dirty worktree on sync/cleanup: block and request commit/stash.
- Rebase conflict: stop, report files, require manual resolution.
- Shared branch or no-force-push policy: use merge sync mode.
- Not merged and cleanup requested: block unless explicit force.

## Integration Points

- `update-work-item`: invoke `create` on `in-progress`, `sync` on `ready-for-review`
- `create-pr`: expects synced branch with upstream
- `handle-pr-feedback`: invoke `sync` after rework
- `merge-pr`: invoke `cleanup` after successful merge
- `finalize-work-item`: verify cleanup completed

## Failure Modes and Fast Recovery

### Branch already exists

- Action: `git switch <branch>` and continue

### Dirty worktree

- Action: commit or stash; retry operation

### Rebase conflicts

- Action: resolve conflicts, `git add <files>`, `git rebase --continue`
- If abandoning: `git rebase --abort`

### Branch not merged on cleanup

- Action: verify merge target/PR status
- Only force-delete with explicit caller approval

## Minimal Examples

Create:

```bash
git fetch origin main
git switch -c feature/wi-060-filter-adapter origin/main
```

Sync (rebase):

```bash
git fetch origin main
git rebase origin/main
git push --force-with-lease origin feature/wi-060-filter-adapter
```

Prepare for review:

```bash
git status --porcelain
git rev-list --count origin/main..HEAD
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

Cleanup:

```bash
git fetch origin --prune main
git merge-base --is-ancestor feature/wi-060-filter-adapter origin/main
git branch -d feature/wi-060-filter-adapter
git push origin --delete feature/wi-060-filter-adapter
```
