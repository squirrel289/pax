---
id: guardrails-implementation
type: document
subtype: summary
status: complete
title: Guardrails Implementation - Complete
created_at: 2024-12-19T00:00:00Z
---

## Guardrails Implementation Summary

Three new guardrails skills have been created and integrated into the main workflow skills to prevent regressions and enforce safety at critical points.

### 1. **guarding-branches** Skill

- **Purpose**: Protect main branch during merge operations through mergeability checks, conflict detection, and export scanning
- **Location**: [skills/aspects/guarding-branches/SKILL.md](../../skills/aspects/guarding-branches/SKILL.md)
- **Key Checks**:
  - Merge conflict detection (`git merge --no-commit --no-ff`)
  - Type/export conflict scanning (`grep -r type` patterns)
  - Unintended file deletion detection (`git diff --name-status`)
  - Branch protection rule validation

### 2. **validating-changes** Skill

- **Purpose**: Ensure code quality before PR submission through local test runs and regression capture
- **Location**: [skills/aspects/validating-changes/SKILL.md](../../skills/aspects/validating-changes/SKILL.md)
- **Key Checks**:
  - Affected tests pass locally (`pnpm test:affected:ci`)
  - No regression runes (run tests before/after, compare outputs)
  - Coverage meets targets
  - Integration tests pass in local CI environment

### 3. **workspace-isolation** Skill

- **Purpose**: Enable parallel work item execution with git worktrees for complete workspace separation
- **Location**: [skills/execution/workspace-isolation/SKILL.md](../../skills/execution/workspace-isolation/SKILL.md)
- **Key Features**:
  - Worktree creation for each active WI
  - Isolated working directories, shared git database
  - Subagent code-only implementation
  - Main agent serialized PR operations during fan-in

## Integration Points

### Architectural Refinement: merge-pr Enforcement

**Key Change**: Test Parity Gate and guarding-branches checks moved to `merge-pr` skill as **mandatory Phase 1** (before any GitHub PR verification).

This ensures guardrails are **always** enforced when merging, regardless of which workflow calls `merge-pr`.

### merge-pr Skill Updates

Added mandatory pre-merge verification stages:

1. **Phase 1: Test Parity Gate** (Mandatory - NEW)
   - Run `pnpm test:affected:ci` locally
   - Verify no unintended deletions: `git diff origin/main...HEAD --name-status`
   - Fail stop if tests don't pass or deletions are unintended

2. **Phase 2: Pre-Merge Verification** (Renamed from Phase 1)
   - Fetch PR details, verify approvals, check mergeable state
   - Verify CI checks pass (guarding-branches aspect)
   - Check review threads

3. **Phase 4: Execution** (Renamed from Phase 3)
   - Execute merge with selected strategy (squash/rebase/merge)

4. **Phase 5: Finalization** (Renamed from Phase 4)
   - Verify completion, cleanup branches, report results

### executing-backlog Skill Updates

Simplified to leverage `merge-pr` enforcement:

1. **Phase 3: PR & Review** - Removed validation details
   - Create PR with `create-pr`
   - Seek reviewers with `code-review-excellence`
   - (Validation now handled by `merge-pr`)

2. **Phase 4: Feedback, Merge, Finalization** - Simplified to use `merge-pr`
   - Handle PR feedback with `resolve-pr-comments`
   - Merge with `merge-pr` (Test Parity Gate + guarding-branches automatically enforced)
   - Finalize with `finalize-work-item`

## Guardrail Activation Flow

```plaintext
User via executing-backlog or direct merge-pr call
│
├─ Developer finishes implementation
│  └─ Push branch + create PR
│
├─ Reviews/approvals complete
│  └─ Ready to merge
│
└─ Call merge-pr (NEW: enforces all guardrails)
   ├─ PHASE 1: Test Parity Gate (MANDATORY)
   │  ├─ Run pnpm test:affected:ci
   │  ├─ Verify no unintended deletions
   │  └─ FAIL if tests don't pass → Stop, don't merge
   │
   ├─ PHASE 2: Pre-Merge Verification
   │  ├─ Verify GitHub PR checks pass
   │  ├─ Verify approvals received
   │  ├─ Check guarding-branches constraints
   │  └─ FAIL if constraints violated → Stop
   │
   ├─ PHASE 4: Execute Merge
   │  └─ Merge to main (squash/rebase/merge strategy)
   │
   └─ PHASE 5: Finalization
      └─ Report results, cleanup branches
```

**Result**: Guardrails enforced at **merge bottleneck**, not in workflow skill. Any code path that calls `merge-pr` (directly or via workflow) must pass Test Parity Gate + guarding-branches.

## Key Design Decisions

1. **Test Parity Gate at Merge Bottleneck**: Instead of distributed checks in multiple workflows, `merge-pr` Phase 1 enforces local test validation before any GitHub checks are verified
   - **Prevents**: Merging code that fails CI locally (caught during Phase 2 implementation)
   - **Rationale**: Fail fast before wasting review cycles on broken code

2. **Mandatory Pre-Merge Validation**: `merge-pr` will not proceed to execution if:
   - Local tests don't pass (`pnpm test:affected:ci` fails)
   - Unintended file deletions detected
   - GitHub checks fail
   - Approvals not received
   - **Result**: Every merge to main passes all gates, no exceptions

3. **Aspect vs Skill**: `guarding-branches` and `validating-changes` aspects are composable patterns reused in multiple skills
   - `merge-pr` uses guarding-branches in Phase 2 (GitHub checks also verified)
   - `merge-pr` uses validating-changes pattern in Phase 1 (local test runs)
   - Other workflows can apply these aspects as needed

4. **Workspace Isolation for Parallel Execution**: `workspace-isolation` skill enables true parallelism with git worktrees
   - **Subagents**: Code implementation ONLY (isolated worktrees)
   - **Main Agent**: All git/PR operations (serialized fan-in)
   - **Prevents**: Merge race conditions, conflicting commits, state corruption

5. **Unintended Deletion Detection**: Both Phase 1 and guarding-branches aspect scan for unexpected file deletions
   - `git diff origin/main...HEAD --name-status | grep '^D'`
   - Verified before and after merge to catch accidental deletions

## Testing & Validation

All guardrails are **production-ready**:

- [x] `merge-pr` Phase 1 enforcement: Prevents broken code merges
- [x] `guarding-branches` aspect: Tested in temple-linter, vscode-temple-linter workflows
- [x] `validating-changes` aspect: Tested against CI/test patterns
- [x] `workspace-isolation` skill: Reference implementation with realistic examples

## Usage in Projects

### executing-backlog Workflow

```
Phase 1: Planning
Phase 2: Branching & Implementation
Phase 3: PR & Review (no validation - delegated to merge-pr)
Phase 4: Merge (calls merge-pr, which enforces Test Parity Gate)
        └─ merge-pr handles ALL validation automatically
```

### Direct merge-pr Usage

Any script or automation that needs to merge PRs calls `merge-pr` directly:

```bash
merge_pr pr-number=123 repo=owner/repo
# Automatically enforces Test Parity Gate + guarding-branches
```

### Parallel Work Items

Use `workspace-isolation` skill for N independent work items:

1. Setup: Create worktrees for each WI
2. Execution: Spawn N subagents in parallel (code-only)
3. Fan-in: Main agent calls `merge-pr` serially for each WI

## Connection to Existing Patterns

- **Replaces**: Old `process-pr` skill (deprecated)
- **Extends**: `feature-branch-management` (branch creation/sync)
- **Complements**: `finalize-work-item` (WI archival)
- **Aligns with**: Atomic commit patterns in ADRs

---

**Status**: Production-ready guardrails at merge bottleneck. Ready for adoption across pax, temple, and templjs projects.
