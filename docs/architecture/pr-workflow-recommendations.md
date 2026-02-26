---
title: PR Workflow Architecture Recommendations
description: Recommended changes to improve clarity, reduce overlap, and strengthen PR workflow skill architecture
audience: agents, architects, leads
version: 1.0
status: ready
date: 2026-02-25
---

## Overview

This document provides specific recommendations to address architecture issues identified in the decision tree analysis and parity validation. Focus areas:

1. **Consolidate overlapping skills** without losing functionality
2. **Document intended composition patterns** clearly
3. **Fix backend parity issues** for reliability
4. **Improve error messaging** for user experience

---

## Issue 1: Skill Overlap - resolve-pr-comments vs handle-pr-feedback

### Current State

| Skill                   | Purpose                                | Scope              | Approach                       |
| ----------------------- | -------------------------------------- | ------------------ | ------------------------------ |
| **resolve-pr-comments** | Address review comments systematically | All comments on PR | Comment-by-comment processing  |
| **handle-pr-feedback**  | Triage and address review feedback     | All feedback on PR | Severity-based decision making |

**Problem**: Both address the same problem (unresolved review comments) but with different approaches. Users confused about which to choose.

### Recommendation: Clarify Composition

**Decision**: Keep both skills, but **clearly document composition relationship**.

**Implementation**:

1. **resolve-pr-comments**: Remains as **reusable building block**
   - Handles: Systematic comment processing (sequential or parallel)
   - Used by: handle-pr-feedback, process-pr
   - Scope: Low-level workflow (address comments, resolve threads)

2. **handle-pr-feedback**: Becomes **high-level orchestrator**
   - Handles: Severity triage, auto-fix logic, escalation decisions
   - Composes: resolve-pr-comments for minor/moderate issues
   - Escalates: Major/blocker issues for manual review
   - Scope: High-level policy (what to do with each comment)

3. **Updated Skills Manifest Entry**:

```markdown
### resolve-pr-comments (Building Block)

**Purpose**: Systematically address review comments and resolve threads.

**When to Use Directly**:

- Know all comments are actionable and ready to address
- Need fine-grained control over comment processing order
- Want to compose with custom decision logic

**When Used Indirectly**:

- Via handle-pr-feedback (severity-based triage first)
- Via process-pr (full lifecycle)

**Composition**:

- pull-request-tool (list-comments, reply-comment, resolve-thread)
- sequential-execution | parallel-execution
- yolo | collaborative mode (via aspect)
```

```markdown
### handle-pr-feedback (High-Level Orchestrator)

**Purpose**: Triage PR review feedback by severity and handle accordingly.

**When to Use**:

- PR has review feedback
- Need automated severity triage
- Want auto-fix for trivial/minor issues
- Want smart escalation for major/blocker issues

**Composition**:

- resolve-pr-comments (used for minor/moderate issues)
- decision logic (for severity classification)
- update-work-item skill (for work item status changes on major issues)
- yolo | collaborative mode (via aspect)

**Difference from resolve-pr-comments**:

- resolve-pr-comments: Assumes all comments are actionable, processes systematically
- handle-pr-feedback: Decides if comments are actionable, may escalate or auto-fix
```

---

## Issue 2: Skill Overlap - merge-pr vs process-pr

### Current State

| Skill          | Purpose                         | Scope               | Workflow                      |
| -------------- | ------------------------------- | ------------------- | ----------------------------- |
| **merge-pr**   | Safely merge after verification | Just the merge      | Verify → Merge → Cleanup      |
| **process-pr** | Full lifecycle processing       | Entire PR lifecycle | Assess → Review → Fix → Merge |

**Problem**: Users unclear when to use merge-pr alone vs process-pr. Is merge-pr a building block or standalone tool?

### Recommendation: Clarify Intended Use Cases

**Decision**: Treat merge-pr as **reusable building block** (like resolve-pr-comments), but **also support standalone use case**.

**Implementation**:

1. **merge-pr**: Dual-purpose skill
   - **Standalone Use**: User can call `merge-pr` directly when PR is already reviewed and ready
   - **Reusable Composition**: process-pr uses merge-pr as its final stage
   - **Key Point**: No dependency on prior stages; can be invoked independently

2. **process-pr**: Full-lifecycle orchestrator
   - Stages: Assess → Fix feedback → Merge
   - Composes: resolve-pr-comments + merge-pr
   - Entry point when starting from review phase

3. **Updated Skills Manifest Entry**:

```markdown
### merge-pr (Dual-Purpose Skill)

**Type**: Composable Building Block + Standalone Workflow

**When to Use Standalone**:

- PR is reviewed, approved, checks passing
- Ready to merge immediately
- No feedback to address
- Just need safe merge verification + execution

**When Used as Building Block**:

- Stage 5 of process-pr
- After feedback addressed, ready for final merge
- Part of larger orchestration

**Composition**:

- pull-request-tool (for verification and merge operation)
- sequential-execution (for verification phase)
- yolo | collaborative mode (via aspect)

**Example Standalone**:
@agent merge PR #42

# Verifies, merges, reports ✓

**Example as Building Block**:
process-pr uses merge-pr internally after addressing feedback
```

```markdown
### process-pr (Full-Lifecycle Orchestrator)

**Type**: Orchestration Skill (Advanced)

**Purpose**: Complete PR processing from review phase through merge.

**When to Use**:

- PR in active review phase
- Need multiple stages: assess → address feedback → merge
- Want single command for complete processing
- Multiple PRs need batch processing

**Composition**:

- Initial Assessment: pull-request-tool (parallel checks)
- Address Feedback: resolve-pr-comments workflow
- Final Merge: merge-pr workflow
- Execution Modes: yolo | collaborative

**Difference from merge-pr**:

- merge-pr: Just handles merge stage, assumes PR ready
- process-pr: Orchestrates entire lifecycle including feedback resolution
```

---

## Issue 3: Backend Parity - check-status Operation Undocumented

### Current State

- `copilot-pull-request`: No documentation for check-status operation
- `gh-pr-review`: Fully implemented with `gh pr view --json` command
- Risk: Workflows assuming both backends support all operations

### Recommendation: Complete Documentation + Add Capability Detection

**Actions**:

1. **Document check-status in copilot-pull-request** (Immediate)

   **File**: `copilot-pull-request/SKILL.md`

   **Add Section**:

   ````markdown
   ### Check Status / Wait for CI Checks

   ```yaml
   operation: check-status
   pr-number: 42
   repository: owner/repo
   ```
   ````

   **API Usage**:
   - Calls `github-pull-request_activePullRequest` (same as fetch-pr-details)
   - Returns: `mergeable`, `mergeStateStatus`, `statusCheckRollup` fields

   **For Polling**:
   - Repeatedly call check-status until:
     - `mergeStateStatus` = "CLEAN", OR
     - `statusCheckRollup` all pass, OR
     - Timeout/failure

2. **Add Capability Detection to pull-request-tool** (Implementation)

   **Pseudocode**:

   ```python
   CAPABILITIES = {
       'copilot-pull-request': [
           'fetch-pr-details',
           'list-comments',
           'reply-comment',
           'resolve-thread',
           'merge-pr',
           'check-status'  # Now documented
       ],
       'gh-pr-review': [
           'fetch-pr-details',
           'list-comments',
           'reply-comment',
           'resolve-thread',
           'merge-pr',
           'check-status'
       ]
   }

   def pull_request_tool(operation, params):
       backend = detect_backend()

       if operation not in CAPABILITIES[backend]:
           raise UnsupportedOperation(
               f"Operation '{operation}' not supported by {backend} backend. "
               f"Available operations: {', '.join(CAPABILITIES[backend])}"
           )

       return BACKEND[backend](operation, params)
   ```

3. **Update PR_MANAGEMENT_INTERFACE.md**

   **Add Backend Support Matrix**:

   ```markdown
   ## Backend Support Matrix

   | Operation        | copilot-pull-request | gh-pr-review | Notes                             |
   | ---------------- | :------------------: | :----------: | --------------------------------- |
   | fetch-pr-details |          ✅          |      ✅      | Core operation                    |
   | list-comments    |          ✅          |     ✅\*     | \*Requires gh-pr-review extension |
   | reply-comment    |          ✅          |     ✅\*     | \*Requires gh-pr-review extension |
   | resolve-thread   |          ✅          |     ✅\*     | \*Requires gh-pr-review extension |
   | merge-pr         |          ✅          |      ✅      | Core operation                    |
   | check-status     |          ✅          |      ✅      | Core operation                    |

   - gh-pr-review extension required for comment operations
   ```

---

## Issue 4: Missing Backend Prerequisites Documentation

### Current State

- gh-pr-review requires `gh` CLI + optional `gh-pr-review` extension
- Users may not know about prerequisites
- Silent failures possible if extension missing

### Recommendation: Add Prerequisite Checking + Clear Error Messages

**Implementation**:

1. **Add Prerequisite Check to gh-pr-review Skill**

   **File**: `gh-pr-review/SKILL.md`

   **Add Section**:

   ````markdown
   ## Prerequisites Checking

   Before executing comment operations, check:

   ```bash
   # Check GitHub CLI installed
   command -v gh > /dev/null || \
     { echo "GitHub CLI not found. Install: brew install gh"; exit 1; }

   # Check gh-pr-review extension for comment operations
   if [[ "$operation" =~ ^(list-comments|reply-comment|resolve-thread)$ ]]; then
     gh extension list | grep -q "gh-pr-review" || \
       { echo "gh-pr-review extension required: gh extension install agynio/gh-pr-review"; exit 1; }
   fi
   ```
   ````

2. **Improve Error Messages in pull-request-tool**

   ```python
   # When gh-pr-review extension missing:
   Error: "Operation 'list-comments' requires GitHub CLI extension 'gh-pr-review'"

   Install with:
   $ gh extension install agynio/gh-pr-review

   Then retry your command.
   ```

---

## Issue 5: create-pr Skill Relationship to PR Workflow

### Current State

- `create-pr` creates PR from feature branch
- Transitions work item from `in_progress` → `testing` → PR created
- Currently standalone, not fully integrated into decision tree

### Recommendation: Document in Decision Tree + Clarify Transition

**Implementation**:

1. **Add to [pr-workflow-decision-tree.md](../reference/pr-workflow-decision-tree.md)** (Already done, but verify)

   Entry point: "Create a PR" → create-pr workflow

2. **Document Transition in Skills Manifest**

   ```markdown
   ### Work Item → PR Transition

   Typical workflow:

   1. Work item status = `in_progress` (development phase)
   2. Tests passing locally
   3. Update: `update-work-item status: testing`
   4. Invoke: `create-pr` (auto-creates PR from work item)
   5. PR created, linked back to work item
   6. Transition: Work item status still `testing`, now PR exists

   Then: 7. Handle feedback via `handle-pr-feedback` 8. Finalize: After merge, `finalize-work-item` archives it
   ```

---

## Recommended File Changes

### 1. Update Skills Manifest

**File**: `/Users/macos/dev/pax/skills/skills-manifest.md`

**Change**: Expand PR section with composition details and use case clarification

**Location**: After "Pull Requests" section heading (around line 100)

**New Content**:

```markdown
### Pull Request Management

Three levels of PR skills:

#### Level 1: Tools (Low-level operations)

**pull-request-tool** - Unified interface for all PR operations

- Auto-selects backend (copilot-pull-request or gh-pr-review)
- Single source of truth for PR operations
- See [tools/PR_MANAGEMENT_INTERFACE.md]

**copilot-pull-request** - Copilot API backend
**gh-pr-review** - GitHub CLI backend

- Implement same interface, different backends
- Selected automatically by pull-request-tool
- See [Backend Parity Report]

#### Level 2: Workflows (Reusable Building Blocks)

**resolve-pr-comments** - Address review threads systematically

- Sequential or parallel comment processing
- Auto-resolve capability
- Use when: Ready to address comments one-by-one

**merge-pr** - Safely merge after verification

- Pre-merge verification (checks, approvals, conflicts)
- Merge method selection
- Use when: PR ready to merge, all checks pass

#### Level 3: Orchestration (High-Level Workflows)

**handle-pr-feedback** - Triage feedback by severity

- Auto-fixes trivial/minor issues
- Escalates major/blocker issues
- Composes: resolve-pr-comments + decision logic
- Use when: PR has feedback, need smart triage

**process-pr** - Full lifecycle from review to merge

- Assesses PR status
- Addresses feedback (via resolve-pr-comments)
- Merges (via merge-pr)
- Composes: resolve-pr-comments + merge-pr + orchestration
- Use when: Processing PR end-to-end

**create-pr** - Create PR from feature branch

- Auto-populates from work item metadata
- Transitions work item status
- Use when: Implementation ready, tests passing locally

#### Use Case Matrix

| Scenario                  | Skill                            | Mode                  |
| ------------------------- | -------------------------------- | --------------------- |
| View PR status            | pull-request-tool (fetch)        | N/A                   |
| Check if mergeable        | pull-request-tool (check-status) | N/A                   |
| Address feedback on PR    | handle-pr-feedback               | yolo or collaborative |
| Resolve specific comments | resolve-pr-comments              | yolo or collaborative |
| Merge a PR                | merge-pr                         | yolo or collaborative |
| Process PR end-to-end     | process-pr                       | yolo or collaborative |
| Create PR from branch     | create-pr                        | N/A                   |
```

---

## Summary of Changes

### 1. Immediate Actions (This Week)

1. ✅ Create `pr-workflow-decision-tree.md` (DONE)
2. ✅ Create `pr-parity-validation-report.md` (DONE)
3. Document check-status API in copilot-pull-request/SKILL.md
4. Add backend support matrix to PR_MANAGEMENT_INTERFACE.md
5. Update skills-manifest.md with composition matrix

### 2. Short-Term (Sprint)

1. Implement capability detection in pull-request-tool
2. Add prerequisite checking to gh-pr-review
3. Improve error messages for backend mismatches
4. Add integration tests for backend parity

### 3. Medium-Term (Next Quarter)

1. Consolidate copilot-pull-request + gh-pr-review docs
2. Consider creating separate "PR Operations" vs "PR Workflows" sections
3. Add examples to each skill showing composition context

---

## Benefits of These Changes

### For Users

1. **Clearer Decision Making**: Decision tree removes ambiguity
2. **Better Error Messages**: Know why operation failed and how to fix
3. **Reduced Frustration**: Understand when to use which skill

### For Agents

1. **Reliable Operation**: Capability detection prevents silent failures
2. **Better Composition**: Clear building blocks and orchestrators
3. **Consistent Behavior**: Both backends work identically (or fail explicitly)

### For Maintainers

1. **Reduced Duplication**: Building blocks composable, not copied
2. **Clear Architecture**: Skill hierarchy documented and enforced
3. **Easier Testing**: Capability detection enables targeted testing

---

## Success Metrics

- [ ] Users can answer "which skill should I use?" by reading decision tree
- [ ] Backend mismatch errors are caught and reported clearly
- [ ] All PR workflows using pull-request-tool pass capability detection
- [ ] Documentation reflects actual implementation (no gaps like check-status)
- [ ] Integration tests verify both backends work equivalently

---

## Next Steps

1. Review this document with team
2. Prioritize immediate actions
3. Assign owners for each change
4. Track via backlog work items
5. Validate changes with E2E tests

---

**Document Version**: 1.0  
**Date**: 2026-02-25  
**Status**: Ready for review and implementation
