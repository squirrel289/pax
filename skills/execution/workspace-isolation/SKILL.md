---
name: workspace-isolation
description: 'Use git worktrees to maintain isolated workspaces for multiple parallel work items. Ensures atomic commits, prevents state conflicts, and enables true parallelism with clean git history. Use when executing multiple work items simultaneously with complete workspace separation.'
metadata:
  category: project-management
  pattern: git-worktree, workspace-isolation
license: MIT
---

# Workspace Isolation with Git Worktrees

## Overview

Execute multiple independent work items with complete workspace isolation using git worktrees. Each work item gets its own independent working directory checked out to a feature branch, enabling true parallelism without state conflicts or lock contention.

**Key Principle**: One git worktree per active work item, shared git repository.

## When to Use

Use this pattern when:

- Multiple independent work items ($N \geq 2$) are being executed simultaneously
- Work items touch different files or subsystems
- You want guaranteed isolation and conflict-free merges
- Timeline pressure requires true parallelism

## Architecture

### Worktree Structure

```
repo/
├── .git/                    # Shared git database
├── src/
├── backlog/
├── wt_wi_001/               # Worktree 1
│   ├── .git -> ../.git/worktrees/wt_wi_001/
│   ├── src/
│   └── backlog/001_*.md
├── wt_wi_002/               # Worktree 2
│   ├── .git -> ../.git/worktrees/wt_wi_002/
│   ├── src/
│   └── backlog/002_*.md
└── wt_wi_003/               # Worktree 3
    ├── .git -> ../.git/worktrees/wt_wi_003/
    ├── src/
    └── backlog/003_*.md
```

**Key properties**:
- Each worktree is a complete, independent working directory
- All worktrees share the same `.git/` database
- Working tree state (files, uncommitted changes) is isolated per worktree
- Git refs are shared; commits from any worktree are immediately visible to all
- No lock contention; operations in one worktree don't affect others

## Setup Phase (Main Agent)

### Step 1: Validate Prerequisites

```bash
# Check git version (2.10+ required)
git worktree --version

# Verify tooling
pnpm --version
gh --version
git --version

# Confirm no blocking dependencies for any WI
for wi_file in backlog/001_*.md backlog/002_*.md backlog/003_*.md; do
  # Parse links.depends_on from YAML frontmatter
  # Verify all referenced items have status: closed
done
```

### Step 2: Create Worktrees

Create one worktree per active work item, each checked out to its feature branch:

```bash
# Create worktree for WI-001 on feature/wi-001 branch
git worktree add wt_wi_001 feature/wi-001

# Create worktree for WI-002 on feature/wi-002 branch
git worktree add wt_wi_002 feature/wi-002

# Create worktree for WI-003 on feature/wi-003 branch
git worktree add wt_wi_003 feature/wi-003

# Verify all worktrees
git worktree list
git worktree prune
```

**Expected output**:

```
repo                          abc1234 [main]
wt_wi_001                     def5678 [feature/wi-001]
wt_wi_002                     ghi9012 [feature/wi-002]
wt_wi_003                     jkl3456 [feature/wi-003]
```

### Step 3: Pre-Creation Validation

Before creating worktrees, ensure no conflicts in file ownership:

```bash
# Identify files touched by each WI's acceptance criteria
grep -r "^\-.*src/" backlog/001_*.md | cut -d: -f2 | sort -u > /tmp/wi_001_files.txt
grep -r "^\-.*src/" backlog/002_*.md | cut -d: -f2 | sort -u > /tmp/wi_002_files.txt
grep -r "^\-.*src/" backlog/003_*.md | cut -d: -f2 | sort -u > /tmp/wi_003_files.txt

# Verify no overlaps
comm -12 <(cat /tmp/wi_001_files.txt) <(cat /tmp/wi_002_files.txt)
# Should be empty if truly independent
```

## Execution Phase (Parallel Subagents)

Each subagent works independently in its assigned worktree:

### Per-Subagent Invocation

```bash
# Main agent spawns subagent for WI-001
spawn_subagent \
  work_item_id=001 \
  workspace=/repo/wt_wi_001/ \
  prompt="Implement WI-001: [description]. Update status to ready-for-review in backlog/001_*.md, then stop."

# Simultaneously spawn other subagents
spawn_subagent \
  work_item_id=002 \
  workspace=/repo/wt_wi_002/ \
  prompt="Implement WI-002: [description]. Update status to ready-for-review in backlog/002_*.md, then stop."
  
spawn_subagent \
  work_item_id=003 \
  workspace=/repo/wt_wi_003/ \
  prompt="Implement WI-003: [description]. Update status to ready-for-review in backlog/003_*.md, then stop."
```

### Subagent Workflow (Code-Only)

Inside each worktree, subagents:

1. **Update work item status**:
   ```bash
   cd /repo/wt_wi_001/
   # Edit backlog/001_*.md: set status: in-progress, record started_at
   git add backlog/001_*.md
   git commit -m "chore(wi-001): mark in-progress"
   ```

2. **Implement code**:
   ```bash
   # Edit src/... files
   git add src/...
   git commit -m "feat(wi-001): [description]"
   git commit -m "test(wi-001): add unit tests"
   # Multiple commits are fine
   ```

3. **Update work item when complete**:
   ```bash
   # Edit backlog/001_*.md: set status: ready-for-review, record actual hours
   git add backlog/001_*.md
   git commit -m "chore(wi-001): mark ready-for-review"
   ```

4. **Report back**:
   Provide summary of commits, test results, and status.

### Isolation Guarantee

Each worktree has:
- Isolated working directory (no cross-contamination)
- Isolated index/staging area
- Shared git refs (feature branches are visible to all)
- Shared object database (commits are immediately shared)

Result: Subagents can **commit independently** without affecting other worktrees.

## Review & Merge Phase (Main Agent - Sequential)

Main agent handles all git/PR operations **serially** to avoid conflicts:

### Step 1: Update from Origin

```bash
cd /repo  # Main worktree

# Fetch latest from origin
git fetch origin

# Check for updates to main
git log --oneline main..origin/main
```

### Step 2: Process One WI at a Time

For each work item in topological dependency order:

#### 2a. Verify Worktree Status

```bash
cd /repo

# Check if worktree has commits ready
git log origin/main..wt_wi_001/feature/wi-001 --oneline
```

#### 2b. Merge with Main (Avoid Conflicts)

```bash
# Option A: Rebase onto main (clean history)
cd wt_wi_001
git fetch origin
git rebase origin/main
# If conflicts, resolve and git rebase --continue

# Option B: Merge main into feature branch
cd wt_wi_001
git fetch origin
git merge origin/main
# If conflicts, resolve and git commit
```

#### 2c. Validate Tests

```bash
cd wt_wi_001

# Run tests for affected files
pnpm test:affected

# If failures: Subagent may need to fix, or main agent fixes directly
```

#### 2d. Create PR from Main Directory

```bash
cd /repo  # Back to main worktree, NOT in wt_*

# Get commits to be in PR
git log --oneline origin/main..wt_wi_001/feature/wi-001

# Create PR
gh pr create \
  --base main \
  --head feature/wi-001 \
  --title "wi-001: [Title from work item]" \
  --body "Implements WI-001: [description from backlog/001_*.md]"

# Get PR number
pr_number=$(gh pr list --head feature/wi-001 --json number -q '.[0].number')
```

#### 2e. Wait for Approval & CI

```bash
# Check PR status
gh pr status --head feature/wi-001

# Wait for approval (manual or via codeowners)
gh pr view $pr_number  # Check state, reviews
```

#### 2f. Merge PR

```bash
# Merge PR
gh pr merge $pr_number --squash

# Pull merged main locally
git fetch origin
git log --oneline main..origin/main
```

#### 2g. Update Work Item & Cleanup

Back in the main worktree, update the work item:

```bash
cd /repo

# Update work item status to closed
# Edit backlog/001_*.md: set status: closed, completed_date: ..., etc.

# Commit the WI update
git add backlog/001_*.md
git commit -m "chore: close wi-001 after PR merge

Closes #PR_NUMBER
"

# Push to origin/main
git push origin main

# Cleanup worktree
git worktree remove wt_wi_001

# List remaining worktrees
git worktree list
```

### Step 3: Repeat for Other WIs

```bash
# Process WI-002 using same workflow
# Then WI-003
# Until all are merged and worktrees removed
```

## Handling Conflicts

### Situation: Merge Conflict in Rebase

During Step 2b, if `git rebase origin/main` encounters a conflict:

```bash
cd wt_wi_001

# Git shows conflict markers
# <<<<<<<<<<<<<
# Subagent-001 code
# ==========
# Origin/main code
# >>>>>>>>>>>>>

# Main agent resolves the conflict
git checkout --theirs conflicted_file.ts  # Accept origin/main version
# OR
vim conflicted_file.ts  # Manual merge
# Then stage
git add conflicted_file.ts

# Continue rebase
git rebase --continue

# Re-test
pnpm test

# If tests fail: main agent fixes code OR reverts PR
```

### Situation: Test Failure After Merge

After merging origin/main, tests fail:

```bash
cd wt_wi_001

# Run tests to identify failures
pnpm test

# Option A: Main agent fixes directly
vim src/failing_file.ts
git add src/failing_file.ts
git commit -m "fix(wi-001): address regression from main rebase"

# Option B: Return to subagent for rework
# Issue: git rebase --abort
# Unlock worktree
git worktree unlock wt_wi_001
# [Subagent fixes code in wt_wi_001]
# Re-attempt PR
```

### Prevention

To minimize conflicts during fan-in:

1. **File isolation**: Ensure WIs modify different files or subsystems
2. **Frequent rebases**: Have subagents rebase onto main periodically during development
3. **Communication**: Document which files each WI touches in its acceptance criteria

## Performance: Parallel vs Sequential

### Sequential Execution (3 WIs, each 8 hours)

```
WI-001  |========== 8h ==========|
WI-002                           |========== 8h ==========|
WI-003                                                    |========== 8h ==========|

Total: ~24 hours
Fan-in overhead: Minimal (PRs created sequentially)
```

### Parallel Execution with Worktrees

```
WI-001  |========== 8h ==========|
WI-002  |========== 8h ==========|  (parallel start)
WI-003  |========== 8h ==========|  (parallel start)
        |__________________________|
        |====== ~10 hours total =====|

Total: ~10 hours (3 parallel + ~2h fan-in overhead)
Speedup: ~2.4x
```

## Worktree Lifecycle

### Creation

```bash
git worktree add <path> <branch>
```

### Lock (Prevent Deletion)

```bash
git worktree lock <path>  # Add safety lock
```

### Unlock

```bash
git worktree unlock <path>  # Remove lock
```

### Repair Broken Link

```bash
git worktree repair  # Auto-repair if .git link is broken
```

### Cleanup (Remove Dead References)

```bash
git worktree prune  # Remove refs to deleted worktrees
```

### List

```bash
git worktree list
```

### Remove

```bash
git worktree remove <path>  # After PR merged and cleanup done
```

## Checklist: Parallel Execution

**Setup Phase**:
- [ ] All WIs have no inter-dependencies (`links.depends_on` all resolved)
- [ ] File sets don't overlap (conflict-free merges)
- [ ] Worktrees created successfully
- [ ] Feature branches exist and are checked out

**Execution Phase**:
- [ ] Each subagent assigned unique worktree
- [ ] Code changes stay within worktree boundaries
- [ ] Status updates committed before subagent exits
- [ ] Commits are atomic and WI-scoped

**Review Phase**:
- [ ] Fan-in processes WIs sequentially
- [ ] Rebase/merge conflicts resolved
- [ ] Tests pass after merging origin/main
- [ ] PRs created one at a time (no race conditions)
- [ ] Worktrees cleaned up after merge

## Example Execution

```bash
# Setup
git worktree add wt_wi_001 feature/wi-001
git worktree add wt_wi_002 feature/wi-002
git worktree add wt_wi_003 feature/wi-003
git worktree list

# Spawn 3 subagents in parallel
# [Wait ~8-10 hours]

# Fan-in (sequential)
cd repo
git fetch origin

# Process WI-001
cd wt_wi_001 && git rebase origin/main && cd ..
pnpm test
gh pr create --head feature/wi-001 --base main
gh pr merge <pr_number> --squash
git pull origin main
git add backlog/001_*.md && git commit && git push origin main
git worktree remove wt_wi_001

# Process WI-002 (repeat)
# Process WI-003 (repeat)

# Done!
```

## Related Skills

- `update-work-item`: Called by subagents to transition statuses during execution
- `executing-backlog`: Use for single WI sequential execution (no worktrees needed)
- `parallel-execution`: Use this skill + parallel-execution skill for optimal throughput
- `guarding-branches`: Apply during fan-in (Step 2b-2f) for conflict detection
- `validating-changes`: Apply during fan-in (Step 2c) for test validation
