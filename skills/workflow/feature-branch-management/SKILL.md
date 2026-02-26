---
name: feature-branch-management
description: "Maintain feature branches for work items. Use to create, sync (rebase), and clean up feature branches. Supports: (1) Creating local feature branches, (2) Rebasing on main, (3) Deleting merged branches locally and remotely, (4) Preparing branches for PR submission"
metadata:
  category: workflow
license: MIT
---

# Feature Branch Management

## Overview

Manage feature branches associated with work items: create branches when starting work, keep them synced with main before PR submission, and clean up after merge. Maintains clean branch hygiene and supports work item -> branch -> PR workflow.

## When to Use

Use feature-branch-management when:

- Starting work on a new item (create feature branch)
- Syncing branch before PR submission (rebase on main)
- After PR merge (delete branch locally and remotely)
- Ensuring branch is clean and up-to-date before pushing changes
- Preparing for code review (verify branch state)

## When NOT to Use

Skip feature branch management for:

- Branch creation options (handled automatically by update-work-item)
- Interactive rebase workflows (use terminal directly for complex rebases)
- Exploring alternative branching strategies (feature-branch-management assumes feature branch pattern)

## Operations

### 1. Create Feature Branch

Create a new local feature branch following naming convention `feature/<id>-<slug>`.

**Entry Criteria**:

- Work item ID and slug available
- Not already on target branch

**Example**:

```bash
git checkout -b feature/60-filter-adapter
```

**Usage in Skills**:

- Called by: `update-work-item` when transitioning `not_started` → `in_progress`
- Optional parameters: Base branch (default: main), custom branch name

**Output**:

- Branch created and checked out
- Confirmation of branch name and base

### 2. Sync / Rebase on Main

Rebase feature branch on latest main to ensure clean history and avoid merge conflicts.

**Entry Criteria**:

- Currently on feature branch
- Remote main is accessible
- No uncommitted changes on branch

**Example**:

```bash
git fetch origin
git rebase origin/main
```

**Usage in Skills**:

- Called by: `update-work-item` before submitting PR (in `testing` transition)
- Called by: `handle-pr-feedback` when feedback requires rework
- Safety: Dry-run mode available to preview rebase

**Output**:

- Rebase result (success, conflicts, aborted)
- If conflicts: List of files needing resolution
- Commit history clean and linear after main

**Options**:

- `--dry-run`: Preview rebase without applying
- `--onto <ref>`: Rebase onto specific ref (default: origin/main)
- `--abort`: Abort ongoing rebase if interrupted

### 3. Clean Up / Delete Branch

Remove feature branch after PR is merged.

**Entry Criteria**:

- PR merged to main
- Branch is local and/or remote

**Examples**:

```bash
# Delete local branch
git branch -d feature/60-filter-adapter

# Delete remote branch
git push origin --delete feature/60-filter-adapter

# Prune remote tracking branches
git fetch --prune origin
```

**Usage in Skills**:

- Called by: `merge-pr` after merge confirmation
- Called by: `finalize-work-item` during archival
- Safety: Verify merge before deletion (branch is "safe to delete")

**Output**:

- Deletion result (success, failed, branch not found)
- Confirmation of local and remote cleanup

**Options**:

- `--local-only`: Delete only local branch (keep remote)
- `--remote-only`: Delete only remote branch (keep local)
- `--force`: Force deletion even if not merged (use with caution)

### 4. Prepare for Review

Ensure branch is ready for PR submission (clean, synced, all commits).

**Entry Criteria**:

- Feature branch has commits
- Ready to push to remote

**Workflow**:

1. Verify no uncommitted changes
2. Verify commits are on top of main
3. Optionally rebase on main (sync)
4. Verify branch is pushable (ahead of remote)

**Usage in Skills**:

- Called by: `update-work-item` when status → `testing`
- Called by: Before PR creation as sanity check

**Output**:

- Branch state summary (synced, ahead, conflicts, uncommitted changes)
- Readiness confidence (ready, needs sync, has issues)

**Options**:

- `--auto-sync`: Auto-rebase if behind (default: false, interactive confirmation)
- `--force-push-allowed`: Warn if force push would be needed

## Workflow: Feature Branch Management Lifecycle

### 1. Create Branch (on status: in_progress)

When starting work on a new item:

```bash
# Automatically triggered by update-work-item
# Action: Create and checkout feature branch
git checkout -b feature/60-filter-adapter
# Result: Branch created, ready for development
```

Work item transitions `not_started` → `in_progress`, and feature branch is created with name `feature/<id>-<slug>`.

**Related Fields in Work Item**:

```yaml
status: in_progress
feature_branch: feature/60-filter-adapter  # Track for reference
notes:
  - timestamp: 2024-06-01T12:00:00Z
    user: @john
    note: Started work on feature/60-filter-adapter branch.
```

### 2. Sync Branch (on status: testing)

When implementation is done and ready to submit PR:

```bash
# Automatically triggered before PR creation
git fetch origin
git rebase origin/main
# If dry-run:
git rebase --dry-run origin/main  # Preview without applying
# Result: Branch rebased cleanly on latest main
```

Ensures branch has no conflicts and is in sync with main.

**Dry-Run Verification**:

If rebase conflicts detected, work item can transition to `testing` but with notes on conflict resolution.

### 3. Push to Remote (manual or PR creation)

After branch is synced and tested locally:

```bash
git push origin feature/60-filter-adapter
# PR created, pointing to this branch
```

Handled by `create-pr` skill or manual push.

### 4. Clean Up Branch (on merge)

After PR is merged:

```bash
# Triggered by merge-pr after merge success
git fetch --prune origin
git branch -d feature/60-filter-adapter  # Local
git push origin --delete feature/60-filter-adapter  # Remote
# Result: Branch removed locally and remotely
```

## Common Patterns

### Scenario A: Linear Development (Create → Sync → Push → Merge → Clean)

```text
1. update-work-item (not_started → in_progress)
   └─ feature-branch-management create feature/60-filter-adapter

2. Development work (local commits)
   └─ Developer commits on feature branch

3. update-work-item (in_progress → testing)
   └─ feature-branch-management prepare-for-review + sync
   └─ Optional: resolve-pr-comments if feedback arrives

4. PR created manually or via create-pr skill
   └─ Branch pushed to remote

5. Review + merge
   └─ merge-pr success
   └─ feature-branch-management cleanup (delete branch)

6. finalize-work-item
   └─ Work item archived (branch already deleted)
```

### Scenario B: Feedback Loop (Revert to in_progress → Sync → Push → Re-review → Merge)

```text
1. PR submitted, feedback received

2. handle-pr-feedback decides: Major changes needed
   └─ update-work-item (testing → in_progress)

3. More development work on feature branch

4. update-work-item (in_progress → testing, 2nd time)
   └─ feature-branch-management sync (rebase on main)
   └─ Push updated commits to remote
   └─ PR updated automatically or new PR created

5. Re-review + merge
   └─ merge-pr success
   └─ feature-branch-management cleanup
```

### Scenario C: Conflict During Rebase

```text
1. feature-branch-management prepare-for-review
   └─ Rebase attempt fails: Conflicts detected

2. Output: Conflict files listed, rebase aborted

3. Manual resolution via terminal (outside skill)
   └─ Developer resolves conflicts manually
   └─ Developer completes rebase (git rebase --continue)

4. Retry feature-branch-management prepare-for-review
   └─ Dry-run confirms clean rebase
   └─ Proceed to PR submission
```

## Error Handling

### Branch Already Exists

```yaml
# If creating feature/60 and it exists:
error: "Branch feature/60-filter-adapter already exists. Use --force to recreate, or git switch to use existing."
action: "Switch to existing branch or confirm intent to recreate"
```

### Rebase Conflicts

```yaml
# If rebase fails:
error: "CONFLICT (content): Merge conflict in src/app.ts"
action: "Conflicts detected. Resolve manually with git, then git rebase --continue"
files_needing_resolution: [src/app.ts, docs/README.md]
```

### Branch Not Merged

```yaml
# If deleting unmerged branch:
warning: "Branch feature/60-filter-adapter not fully merged into main"
action: "Use --force to delete anyway, or verify merge is in main"
confirmed: false # Requires confirmation
```

### Cannot Rebase (Uncommitted Changes)

```yaml
# If syncing with dirty working directory:
error: "Working directory has uncommitted changes"
action: "Commit or stash changes before rebasing"
files_dirty: [src/filters.py, tests/test_filters.py]
```

## Related Skills

See the dependency matrix in [docs/SKILL_COMPOSITION.md](docs/SKILL_COMPOSITION.md#skill-dependency-matrix) for the canonical calling relationships.

- **`update-work-item`**: Triggers branch creation and sync at status transitions
- **`create-pr`**: Uses branch name to create PR after branch is synced
- **`handle-pr-feedback`**: Syncs branch when reverting to in_progress for rework
- **`merge-pr`**: Triggers cleanup after merge confirmation
- **`finalize-work-item`**: Ensures branch is cleaned up during archival

## Tips & Best Practices

### 1. Branch Naming Convention

Use `feature/<id>-<slug>` format consistently:

```bash
feature/60-filter-adapter        # Good: ID + slug
feature/filteradapter            # Avoid: No ID, unclear scope
bugfix/issue-123                 # OK: Type + issue
wip/temp-experiment              # OK: WIP prefix for exploratory branches
```

### 2. Rebase vs Merge Strategy

This skill uses **rebase** by default (linear history):

- **Advantage**: Clean, linear history for PR review
- **Disadvantage**: Rewrites history (don't use on shared branches)
- **Safety**: Never rebase once PR is public and under review (merge instead)

### 3. Dry-Run Before Destructive Operations

Always verify before deleting branches:

```bash
# Preview what will be deleted
git branch -d --dry-run feature/60-filter-adapter

# Confirm merge
git log main..feature/60-filter-adapter  # Commits not in main
```

### 4. Keep Branches Short-Lived

Feature branches should have a lifespan of 1-3 weeks:

- Reduces merge conflicts
- Keeps scope manageable
- Easier to understand in PR review
- Easier cleanup

### 5. Sync Frequently

Rebase on main early and often:

```bash
# At start of day or before long dev sessions
git fetch origin
git rebase origin/main
```

Prevents large conflicts later.

## Related Concepts

- **Feature branch workflow**: GitHub Flow, trunk-based development
- **Rebase strategy**: Linear history, clean commit log
- **Branch naming**: Semantic naming for automatic processing
- **Cleanup automation**: Integrated into merge/finalize workflows

## Script Tools (Optional)

For teams using shell automation, consider:

```bash
# Helper: Create and switch in one command
function work-on() {
  local id=$1 slug=$2
  git checkout -b "feature/$id-$slug"
}

# Usage: work-on 60 filter-adapter
```

Equivalent functions can be added to team's `.bash_aliases` or shell config.
