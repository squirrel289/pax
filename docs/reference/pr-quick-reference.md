---
title: PR Workflow Quick Reference
description: Quick lookup for common PR operations - which skill to use and how
audience: agents, developers (quick reference)
version: 1.0
---

## 30-Second Answers

### **"I want to..."**

#### View / Check Status

| Scenario             | Use This            | Command                                                |
| -------------------- | ------------------- | ------------------------------------------------------ |
| See full PR details  | `pull-request-tool` | `operation: fetch-pr-details`                          |
| Check if mergeable   | `pull-request-tool` | `operation: check-status`                              |
| List review comments | `pull-request-tool` | `operation: list-comments` filters: {unresolved: true} |

#### Create / Submit

| Scenario                      | Use This    | Command                            |
| ----------------------------- | ----------- | ---------------------------------- |
| Create PR from feature branch | `create-pr` | On feature branch, ready to review |

#### Review & Feedback

| Scenario                    | Use This              | Command                                       |
| --------------------------- | --------------------- | --------------------------------------------- |
| Triage feedback by severity | `handle-pr-feedback`  | Auto-fixes trivial, escalates major           |
| Address comments one-by-one | `resolve-pr-comments` | Systematic processing, yes/no on auto-resolve |

#### Merge

| Scenario                    | Use This     | Command            |
| --------------------------- | ------------ | ------------------ |
| Just merge (checks passing) | `merge-pr`   | Quick + safe       |
| Full review→merge lifecycle | `process-pr` | Full orchestration |

---

## Decision Tree (Text Format)

```text
START: "I want to [ACTION]"

A. Create PR?
   → Branch ready, tests pass, work item status = testing
   → Use: create-pr
   ✓

B. View PR details?
   → Use: pull-request-tool
   → operation: fetch-pr-details | list-comments | check-status
   ✓

C. Address feedback?
   → Same PR: Multiple unresolved comments
   → Branch 1: All comments are actionable
      → Use: resolve-pr-comments (sequential or parallel)
   → Branch 2: Some comments may be minor/trivial
      → Use: handle-pr-feedback (auto-fix + escalate)
   ✓

D. Merge PR?
   → All checks passing? Reviews approved? No conflicts?
   → Branch 1: Just merge (quick decision)
      → Use: merge-pr (yolo mode)
   → Branch 2: Ask before merging (controlled)
      → Use: merge-pr (collaborative mode)
   ✓

E. Full processing?
   → PR needs: Review → Fix feedback → Merge
   → Branch 1: Auto everything
      → Use: process-pr (yolo mode)
   → Branch 2: Interactive decisions
      → Use: process-pr (collaborative mode)
   ✓

DONE
```

---

## Skill Reference Card

### create-pr

**Purpose**: Create PR with auto-populated metadata from work item

```bash
# Prerequisites:
# - Feature branch exists and is pushed
# - Work item status = testing
# - No PR already exists for this branch

# Command:
@agent create PR for work item 60

# What happens:
1. Read work item metadata
2. Generate PR title: "#60: Implement FilterAdapter"
3. Populate description from work item
4. Create PR on GitHub
5. Link PR back to work item
```

---

### pull-request-tool

**Purpose**: Unified interface for all PR operations (auto-selects backend)

```bash
# Generic interface (same for both backends):

# FETCH PR DETAILS:
pull-request-tool:
  operation: fetch-pr-details
  pr-number: 42
  repository: owner/repo
→ Returns: title, state, author, mergeable, checks, reviews

# LIST COMMENTS:
pull-request-tool:
  operation: list-comments
  pr-number: 42
  repository: owner/repo
  filters:
    unresolved: true  # optional
→ Returns: threads, comments, resolved status

# REPLY TO COMMENT:
pull-request-tool:
  operation: reply-comment
  pr-number: 42
  thread-id: PRRT_abc123
  body: "..."
  repository: owner/repo
→ Returns: success/failure

# RESOLVE THREAD:
pull-request-tool:
  operation: resolve-thread
  pr-number: 42
  thread-id: PRRT_abc123
  repository: owner/repo
→ Returns: success/failure

# MERGE PR:
pull-request-tool:
  operation: merge-pr
  pr-number: 42
  repository: owner/repo
  merge-method: squash|merge|rebase
  delete-branch: true|false
→ Returns: success/failure, commit SHA

# CHECK STATUS:
pull-request-tool:
  operation: check-status
  pr-number: 42
  repository: owner/repo
→ Returns: mergeable, mergeStateStatus, checks passing/failing
```

---

### resolve-pr-comments

**Purpose**: Systematically address all review comments

```bash
# Prerequisites:
# - PR has review comments
# - Ready to address them

# Command (yolo - auto-fix):
@agent resolve PR comments on #42

# Command (collaborative - ask for each):
@agent resolve PR comments on #42 with confirmation

# What happens:
1. List all unresolved review threads
2. For each thread:
   - Read comment
   - Determine if code change needed
   - Make change OR reply
   - Resolve thread
3. Push changes to PR
4. Trigger CI re-run
```

---

### handle-pr-feedback

**Purpose**: Intelligently triage feedback and handle accordingly

```bash
# Prerequisites:
# - PR has review feedback
# - Want automated severity triage

# Command:
@agent handle feedback on PR #42

# What happens:
1. Fetch review comments
2. Classify by severity:
   - Trivial (typo, formatting)
   - Minor (docs, test)
   - Moderate (logic, optimization)
   - Major (design flaw)
   - Blocker (compliance violation)
3. Actions:
   - Trivial/Minor: Auto-fix
   - Moderate: Flag for review
   - Major/Blocker: Revert to in_progress, escalate
```

---

### merge-pr

**Purpose**: Safely merge PR after verification

```bash
# Prerequisites:
# - PR reviewed and approved
# - All checks passing
# - No conflicts
# - Ready to merge

# Command (yolo - auto-merge):
@agent merge PR #42

# Command (collaborative - ask method):
@agent merge PR #42 with confirmation

# What happens:
1. Fetch PR details
2. Verify:
   - Mergeable state (no conflicts)
   - Approvals met
   - All required checks passing
   - No unresolved threads
3. Decision:
   - YOLO: Auto-merge if ready
   - Collaborative: Ask which merge method
4. Execute merge
5. Delete branch
6. Report success
```

---

### process-pr

**Purpose**: Full lifecycle processing (review → fix → merge)

```bash
# Prerequisites:
# - PR in review/feedback phase
# - Want complete processing

# Command (yolo - full automation):
@agent process PR #42 end-to-end

# Command (collaborative - decisions at each stage):
@agent process PR #42 interactively

# Stages:
1. ASSESS (parallel)
   - PR status
   - Review status
   - CI status

2. FIX FEEDBACK (sequential)
   - Invoke resolve-pr-comments
   - Push changes
   - Wait for CI

3. FINAL CHECK (parallel)
   - Confirm approvals
   - Confirm checks
   - Confirm mergeable

4. MERGE (sequential)
   - Invoke merge-pr
   - Delete branch
   - Report

# Duration:
- YOLO: ~5-30 minutes (depends on CI)
- Interactive: ~30 minutes - 1 hour (user decisions)
```

---

## Flowchart (Simple)

```asciitree
┌─────────────────────────────┐
│ What do you want to do?     │
└──────────────┬──────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    ▼          ▼          ▼          ▼
  CREATE    VIEW/CHECK  REVIEW    MERGE
    │          │         │         │
    │    fetch-details   │    merge-pr
    │    check-status    │    or
    │    list-comments   │ process-pr
    │                    ▼
    │            resolve-pr-comments
    │                 or
    │            handle-pr-feedback
    ▼
  create-pr
```

---

## Error Recovery

### "Operation failed: not supported by backend"

**Cause**: Backend doesn't implement operation

**Solution**:

1. Check which backend was selected (Copilot API or GitHub CLI)
2. See [pr-parity-validation-report.md](../architecture/pr-parity-validation-report.md) for supported operations
3. If GitHub CLI backend, ensure `gh` and `gh-pr-review` extension installed

   ```bash
   # Check installed:
   gh --version
   gh extension list | grep pr-review
   ```

4. Switch to Copilot API backend if available

---

### "PR not mergeable: merge conflicts"

**Cause**: Branch has conflicts with main

**Solution**:

1. Rebase feature branch on main
2. Resolve conflicts locally
3. Push updated branch
4. Retry merge

```bash
# Locally:
git checkout feature/branch
git rebase main
# Resolve conflicts...
git push --force-with-lease
```

---

### "Required approvals not met"

**Cause**: Need more reviewers to approve

**Solution**:

1. Check current approval count: `pull-request-tool fetch-pr-details`
2. Request reviews from required reviewers
3. Wait for approvals
4. Retry merge

---

### "Status checks failing"

**Cause**: CI/linting/tests failing

**Solution**:

1. Check which checks are failing: `pull-request-tool check-status`
2. Fix issues locally
3. Commit and push
4. Wait for CI to re-run
5. Retry merge

---

## Interaction Modes

### YOLO (Autonomous)

- No prompts, auto-decide
- Fast
- Best for: CI/CD, known good workflows
- Risk: Wrong decision possible

**Usage**:

```bash
@agent merge PR #42
# Auto-merges immediately if ready
```

---

### Collaborative (Interactive)

- Prompts for decisions
- Slower but safer
- Best for: High-stakes decisions, learning
- Benefit: User retains control

**Usage**:

```bash
@agent merge PR #42 with confirmation
# Shows status, asks merge method, waits for OK
```

---

## Common Workflows

### Workflow 1: Simple Merge (No Feedback)

```bash
# PR #42 is ready: approved, checks passing
@agent merge PR #42
✓ Done
```

### Workflow 2: Address Feedback + Merge

```bash
# PR #42 has feedback
@agent handle feedback on PR #42
✓ Feedback addressed

@agent merge PR #42
✓ Merged
```

### Workflow 3: Create + Get Feedback + Fix + Merge

```bash
@agent create PR for work item 60
✓ PR #42 created

# ... wait for reviews ...

@agent handle feedback on PR #42
✓ Feedback addressed

@agent merge PR #42
✓ Merged
```

### Workflow 4: Full Processing

```bash
# PR #42 ready for complete processing
@agent process PR #42 end-to-end
✓ All stages completed, PR merged
```

---

## Cheat Sheet

| Need           | Use                               | Mode        |
| -------------- | --------------------------------- | ----------- |
| View status    | `pull-request-tool fetch`         | -           |
| See comments   | `pull-request-tool list-comments` | -           |
| Create PR      | `create-pr`                       | -           |
| Fix comments   | `resolve-pr-comments`             | yolo/collab |
| Smart feedback | `handle-pr-feedback`              | yolo/collab |
| Merge quick    | `merge-pr`                        | yolo        |
| Merge safe     | `merge-pr`                        | collab      |
| Full process   | `process-pr`                      | yolo/collab |

---

## Still Confused?

1. **Decision tree**: See [pr-workflow-decision-tree.md](pr-workflow-decision-tree.md) (full flowchart)
2. **Technical details**: See PR_MANAGEMENT_INTERFACE.md (operations spec)
3. **Backend info**: See [pr-parity-validation-report.md](../architecture/pr-parity-validation-report.md) (which backend does what)
4. **Architecture**: See [pr-workflow-recommendations.md](../architecture/pr-workflow-recommendations.md) (skill design)

---

**Quick Ref Version**: 1.0  
**Last Updated**: 2026-02-25
