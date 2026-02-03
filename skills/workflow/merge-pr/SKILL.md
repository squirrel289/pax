---
name: merge-pr
description: Workflow skill for safely merging pull requests after verification
category: workflow
license: MIT
composed-from:
  - pull-request-tool
  - sequential-execution
  - yolo OR collaborative
---

# Merge PR

A workflow skill that safely merges pull requests after comprehensive verification of readiness.

## Purpose

Automates the PR merge process with proper safety checks, ensuring all requirements are met before merging.

## When to Use

Use this workflow when:

- PR is ready to be merged to main branch
- You want automated verification before merge
- Need to ensure all checks pass
- Want consistent merge process across team

## Skill Composition

This workflow composes:

1. **pull-request-tool**: Check PR status, verify checks, execute merge
2. **sequential-execution**: Step through verification stages
3. **yolo** OR **collaborative**: Execution mode (autonomous vs interactive)

## Parameters

### Required

- **pr-number**: Pull request number to merge
- **repository**: Repository in format `owner/repo`

### Optional

- **interaction-mode**: `yolo` (autonomous) or `collaborative` (ask before merge)
- **merge-method**: `merge` (default), `squash`, or `rebase`
- **delete-branch**: Delete branch after merge (default: true)
- **auto-merge**: Enable auto-merge if checks pending (default: false)
- **require-reviews**: Minimum required approvals (default: 1)
- **require-checks**: Require all status checks pass (default: true)

## Workflow Steps

### Phase 1: Pre-Merge Verification

1. **Fetch PR details**
   - Get PR metadata
   - Verify PR is open
   - Check base and head branches

2. **Verify approvals**
   - Check review status
   - Count approvals
   - Verify required approvals met
   - Check for blocking reviews

3. **Check status**
   - Verify mergeable state
   - Check for merge conflicts
   - Verify branch is up to date

4. **Verify CI checks**
   - List all status checks
   - Verify required checks pass
   - Check for failing checks
   - Ensure no pending required checks

5. **Check review threads**
   - Verify no unresolved threads (or policy allows)
   - Check for blocking comments

### Phase 2: Merge Decision

1. **Determine merge readiness**

   PR is ready to merge if:
   - ✅ Mergeable state is CLEAN or UNSTABLE (no conflicts)
   - ✅ Required approvals received
   - ✅ All required status checks pass
   - ✅ No blocking review comments
   - ✅ Branch protection rules satisfied

2. **Select merge method**
   - Use specified merge-method parameter
   - Or infer from repo settings/history
   - Default to squash if uncertain

### Phase 3: Execution

1. **Execute merge** (if ready)

   YOLO mode:
   - Merge immediately if all checks pass
   - Report success or failure

   Collaborative mode:
   - Show merge summary
   - Request confirmation
   - Execute after approval

2. **Post-merge cleanup**
   - Delete branch if requested
   - Verify merge succeeded
   - Check main branch updated

### Phase 4: Finalization

1. **Verify completion**
    - Confirm PR status is merged
    - Verify commit appears in main
    - Check branch deleted if requested

2. **Report results**
    - Summarize merge operation
    - Report any issues
    - Provide next steps if needed

## Interaction Modes

### YOLO Mode (Autonomous)

```markdown
When interaction-mode = yolo:
- Automatically merge if all checks pass
- Use default merge method (or specified)
- Delete branch automatically
- Report only final status
```

Example:

```markdown
User: "Merge PR #42 in YOLO mode"

Agent:
- Verifies all checks pass
- Verifies approvals present
- Merges using squash (repo default)
- Deletes feature branch
- Reports: "PR #42 merged successfully to main, branch deleted"
```

### Collaborative Mode (Interactive)

```markdown
When interaction-mode = collaborative:
- Show merge readiness status
- Display all checks and approvals
- Request confirmation before merging
- Confirm branch deletion
```

Example:

```markdown
User: "Merge PR #42"

Agent: "Checking merge readiness for PR #42...

PR Status:
✅ Mergeable: Yes (no conflicts)
✅ Reviews: 2 approvals (reviewer1, reviewer2)
✅ Status Checks: All passing (8/8)
  ✅ CI Tests
  ✅ Linter
  ✅ Security Scan
  ✅ Build
  ✅ Integration Tests (x4)
✅ Branch Protection: Satisfied
✅ Unresolved Threads: 0

Ready to merge using squash method.
Delete branch 'feature-xyz' after merge? (yes/no)"

User: "yes"

Agent: "Merging PR #42..."
[executes merge]
"✅ PR #42 merged successfully and branch deleted"
```

## Merge Methods

### Merge Commit (--merge)

- Creates merge commit
- Preserves full history
- Use when: History context important

### Squash and Merge (--squash)

- Combines all commits into one
- Clean linear history
- Use when: Feature commits not important

### Rebase and Merge (--rebase)

- Replays commits on base
- Linear history, preserves commits
- Use when: Clean history with commit granularity

## Auto-Merge Option

When `auto-merge = true`:

- Enables GitHub auto-merge feature
- PR will merge automatically when checks pass
- Useful for:
  - PRs with pending checks
  - Dependabot updates
  - Automated workflows

## Verification Checklist

Before merging, verify:

- [ ] PR is open (not closed/merged already)
- [ ] No merge conflicts
- [ ] Required approvals received
- [ ] All required status checks pass
- [ ] No blocking review comments
- [ ] Branch protection rules satisfied
- [ ] Correct base branch (usually main)
- [ ] Changes reviewed and acceptable

## Error Handling

### Common Issues and Resolutions

1. **Merge conflicts**
   - YOLO: Report blocker, cannot proceed
   - Collaborative: Suggest rebasing or conflict resolution
   - Manual intervention required

2. **Failing status checks**
   - YOLO: Wait or report blocker
   - Collaborative: Show failing checks, ask to wait or investigate
   - Auto-merge option: Enable auto-merge to merge when passes

3. **Missing approvals**
   - YOLO: Report blocker, request reviews
   - Collaborative: Show who can approve, ask to request
   - Cannot proceed without required approvals

4. **Unresolved threads**
   - YOLO: Attempt to resolve if trivial, otherwise report
   - Collaborative: Show threads, ask to resolve
   - Policy-dependent: Some repos allow merging with unresolved

5. **Branch protection violations**
   - Report specific requirement not met
   - Cannot override (requires admin)
   - Must satisfy all rules

## Best Practices

1. **Always verify checks**: Never merge with failing tests
2. **Respect approvals**: Ensure required reviews complete
3. **Clean up branches**: Delete after merge to reduce clutter
4. **Use appropriate method**: Match repo conventions
5. **Verify conflicts**: Check mergeable state first
6. **Update main locally**: Pull after merging
7. **Notify team**: Communication for significant merges
8. **Tag releases**: Create tags for versioned merges

## Safety Guards

Even in YOLO mode, never:

- ❌ Merge with failing required checks
- ❌ Merge without required approvals
- ❌ Merge with conflicts
- ❌ Override branch protection
- ❌ Skip verification steps

Always:

- ✅ Verify PR is ready
- ✅ Check all status checks
- ✅ Confirm approvals present
- ✅ Use safe merge method
- ✅ Report any issues

## Output Format

### YOLO Mode Output

```markdown
TASK: Merge PR #42
STATUS: Success

VERIFICATION:
✅ Approvals: 2/1 required
✅ Status Checks: 8/8 passing
✅ Merge Conflicts: None
✅ Branch Protection: Satisfied

MERGE:
Method: Squash and merge
Commit: abc1234
Branch: feature-xyz (deleted)

RESULT: PR #42 successfully merged to main
```

### Collaborative Mode Output

```markdown
PR Merge Readiness (#42)

Status Checks:
✅ CI Tests (3m 24s)
✅ Linter (45s)
✅ Security Scan (1m 12s)
❌ Integration Tests (failed)

Current Status: NOT READY
Blocker: Integration tests failing

Recommended action: Fix test failures or investigate

Would you like me to:
A) Show test failure details
B) Wait for checks to be fixed and retry
C) Cancel merge operation
```

## Integration Example

```markdown
# Full PR workflow using composed skills

1. process-pr (parent workflow)
   
2. resolve-pr-comments
   - Address all feedback
   
3. merge-pr (this workflow)
   - Verify readiness
   - Execute merge
   
Done: PR fully processed and merged
```

## Quick Reference

```markdown
PURPOSE:
  Safely merge PR after comprehensive verification

COMPOSITION:
  pull-request-tool + sequential-execution + (yolo OR collaborative)

MODES:
  YOLO:          Auto-merge if ready
  Collaborative: Confirm before merge

PHASES:
  1. Pre-Merge Verification
  2. Merge Decision
  3. Execution
  4. Finalization

VERIFICATION:
  - Mergeable state
  - Required approvals
  - Status checks
  - No conflicts
  - Branch protection

MERGE METHODS:
  merge:   Merge commit (preserves history)
  squash:  Single commit (clean history)
  rebase:  Linear history (preserves commits)

PARAMETERS:
  pr-number:      Required
  repository:     Required (owner/repo)
  interaction-mode: yolo or collaborative
  merge-method:   merge/squash/rebase
  delete-branch:  true (default)
  auto-merge:     false (default)

SAFETY:
  Never merge with:
  - Failing required checks
  - Missing approvals
  - Merge conflicts
  - Branch protection violations
```
