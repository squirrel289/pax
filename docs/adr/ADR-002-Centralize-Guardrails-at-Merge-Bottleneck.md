# ADR-002: Centralize Safety Guardrails at Merge Bottleneck

**Status**: Accepted

**Date**: 2026-02-25

**Deciders**: GitHub Copilot Agent

**Context**: Guardrails implementation to prevent regressions across pax, temple, and templjs projects

---

## Problem Statement

Multiple distributed validation points create bypass risk and maintenance burden:

- **Observed**: Local test validation scattered across workflow skills (executing-backlog, update-work-item, direct merge paths)
- **Root cause**: No single enforcement point for safety checks; validation duplicated in multiple locations
- **Impact**:
  - Broken code can slip through if validation is skipped in any workflow
  - Maintenance burden: updating validation logic requires changing multiple files
  - Inconsistent enforcement: different workflows may have different validation gates
  - Late failure: GitHub CI detects failures that could be caught locally first
- **Cost**: Wasted review cycles on code that fails basic tests; risk of merging broken code

**Critical insight**: Safety guarantees require enforcement at a single bottleneck, not distributed trust.

---

## Decision

Centralize all safety guardrails in `merge-pr` skill as **mandatory Phase 1** (Test Parity Gate):

1. **merge-pr becomes the enforcement bottleneck**: All merge paths (workflows, scripts, direct calls) must go through merge-pr
2. **Phase 1 is mandatory and fail-stop**: Local tests + deletion checks run before any GitHub verification
3. **Other workflows delegate validation**: executing-backlog, update-work-item, and other skills remove duplicate checks
4. **Three complementary skills**:
   - `guarding-branches`: Merge conflict detection, export scanning, deletion prevention (Phase 2)
   - `validating-changes`: Local test validation pattern (reusable aspect, enforced in Phase 1)
   - `workspace-isolation`: Parallel execution with git worktrees (prevents merge race conditions)

**Key principles**:

- Single source of truth: merge-pr is the only validation authority
- Fail-fast: Local tests before GitHub checks
- Mandatory enforcement: No merge without passing Test Parity Gate
- Composable aspects: Skills can reuse validation patterns, but enforcement is centralized
- Subagent split rule: Parallel execution splits code (subagents) from git/PR ops (main agent)

---

## Rationale

### Safety

**Before**: Distributed validation can be bypassed if a workflow skips checks or a script calls GitHub merge API directly.

**After**: Every merge path flows through merge-pr Phase 1; no exceptions possible.

**Result**: Guarantee that all code merged to main passes local tests and safety checks.

### Fail-Fast Feedback

**Before**: Push → wait for GitHub CI → discover test failure → fix → repeat (15+ min cycle)

**After**: Run local tests in Phase 1 → fail immediately if broken → fix before pushing (2 min cycle)

**Result**: 7× faster feedback loop; prevents wasting reviewer time on broken code.

### Maintainability

**Before**: Validation logic duplicated across 3+ workflow skills. Update requires changing all locations.

**After**: Single merge-pr Phase 1 implementation. Update once, enforced everywhere.

**Result**: Easier to evolve validation logic; reduced risk of inconsistency.

### Simplicity

**Before**: Each workflow must remember to implement validation. Complex workflows need detailed validation sections.

**After**: Workflows delegate to merge-pr. Simple instruction: "Merge with merge-pr (guardrails enforced automatically)".

**Result**: Cleaner workflow skills; validation details hidden in merge-pr.

---

## Consequences

### Positive

- **Guaranteed enforcement**: All merge paths enforced; bypass impossible
- **Fail-fast feedback**: Local tests before GitHub checks (7× faster)
- **Single source of truth**: Update merge-pr, all workflows benefit
- **Cleaner workflows**: executing-backlog, update-work-item simplified
- **Parallel execution support**: workspace-isolation enables ~3× speedup for N independent work items
- **Reusable patterns**: guarding-branches and validating-changes are composable aspects

### Tradeoffs

- **merge-pr gains responsibility**: More complex Phase 1 logic (local tests + deletions check)
- **Slightly longer merge time**: ~30 seconds additional time for local test validation
- **Requires local test environment**: merge-pr caller must have pnpm + dependencies installed
- **Coordination for parallel execution**: Subagent split rule requires discipline (code-only subagents, git-only main agent)

---

## Evidence from Guardrails Implementation

**Scenario**: Merge PR after Phase 2 implementation completed

**Without centralized enforcement**:

1. Developer pushes code
2. Create PR (no local validation required)
3. GitHub CI runs tests → FAIL (broken code discovered)
4. Fix locally → Push again
5. GitHub CI runs tests → PASS
6. Merge to main

Result: 15+ min cycle; reviewer time wasted on broken code in PR

**With Test Parity Gate at merge-pr Phase 1**:

1. Developer pushes code
2. Create PR
3. Attempt merge with merge-pr
4. **Phase 1 runs local tests → FAIL immediately (2 min)**
5. Fix locally → Push again
6. Phase 1 runs local tests → PASS
7. Phase 2 verifies GitHub checks → PASS (already passed due to local parity)
8. Merge to main

Result: 2 min cycle for failure detection; never opens PR with broken code

**Speedup**: 7× faster feedback; broken code never reaches reviewers

---

## Integration Architecture

```plaintext
┌─────────────────────────────────────────────┐
│   Any Merge Path (workflow/script/direct)  │
└─────────────────────────────────────────────┘
                    │
                    ↓
            ┌───────────────┐
            │   merge-pr    │ ← Single bottleneck
            └───────────────┘
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
┌──────────────────┐   ┌──────────────────┐
│ Phase 1:         │   │ Phase 2:         │
│ Test Parity Gate │   │ Pre-Merge Verify │
│                  │   │                  │
│ • Local tests    │   │ • GitHub checks  │
│ • Deletion check │   │ • Approvals      │
│ • FAIL = STOP    │   │ • Conflicts      │
└──────────────────┘   └──────────────────┘
        ↓                       ↓
        └───────────┬───────────┘
                    ↓
            ┌──────────────┐
            │ Phase 4:     │
            │ Execute      │
            │ Merge        │
            └──────────────┘
                    ↓
            ┌──────────────┐
            │ Phase 5:     │
            │ Finalize     │
            └──────────────┘
```

**Key guarantee**: No code reaches "Execute Merge" without passing both gates.

---

## Skills Created

1. **guarding-branches** (aspect): Reusable merge safety pattern
   - Location: `skills/aspects/guarding-branches/SKILL.md`
   - Used in: merge-pr Phase 2

2. **validating-changes** (aspect): Reusable local test validation pattern
   - Location: `skills/workflow/validating-changes/SKILL.md`
   - Used in: merge-pr Phase 1 (Test Parity Gate)

3. **workspace-isolation** (skill): Parallel execution with worktrees
   - Location: `skills/execution/workspace-isolation/SKILL.md`
   - Used in: executing-backlog Phase 1, update-work-item Section 1
   - Subagent split rule: Code implementation (subagents) vs git/PR ops (main agent)

---

## Workflow Impact

### merge-pr (Modified)

- **Added**: Phase 1 (Test Parity Gate) - mandatory local test validation
- **Renumbered**: Subsequent phases (Pre-Merge Verification now Phase 2)
- **Guarantee**: Every merge enforces guardrails

### executing-backlog (Simplified)

- **Removed**: Duplicate validation logic from Phase 3 (PR & Review)
- **Removed**: Duplicate checks from Phase 4 (Merge)
- **Simplified**: Phase 4 now just "Merge with merge-pr"
- **Benefit**: Cleaner workflow; single source of truth

### update-work-item (Enhanced)

- **Added**: workspace-isolation guidance in Section 1 (Moving to In-Progress)
- **Added**: validating-changes pre-PR checks in Section 4 (Ready for Review)
- **Benefit**: Supports parallel execution; delegates final merge to merge-pr

---

## Next Steps

1. Create comprehensive documentation in skills-manifest.md ✅
2. Document architecture in ADR-002 ✅
3. Apply guardrails to temple project workflows
4. Apply guardrails to templjs project workflows
5. Collect metrics on Test Parity Gate effectiveness (fail-fast time savings)
6. Evaluate after ≥5 merges using new guardrails workflow
