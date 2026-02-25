# ADR-001: Systematic Validation Workflow via Skill Composition

**Status**: Accepted

**Date**: 2026-02-24

**Deciders**: GitHub Copilot Agent

**Context**: Phase 2 closeout (work items WI-001 through WI-011)

---

## Problem Statement

During Phase 2 work item closure for `templjs`, updating 9 similar files displayed a systemic inefficiency:

- **Observed**: 4+ validation failures across 9 work item files
- **Root cause**: Validation requirements discovered during implementation (Phase 2), not planning (Phase 1)
- **Impact**: Each failed validation required re-updating all 9 files and re-validating
- **Cost**: 4 iterations × 9 files × time-per-update = significant waste

**Critical insight**: Trial-and-error inefficiency affects any bulk file operation with schema constraints, not just this one task.

---

## Decision

Adopt a **three-skill composition pattern** for systematic validation in bulk file operations:

1. **discover-validation-criteria**: Phase 1 discovery gate
2. **executing-backlog**: Phase 2 orchestration (includes sample-validation pattern)
3. **agentic-eval**: Phase 2a evaluation fallback (if sample fails)

**Key principles**:

- Shift-left validation: discover before implementation
- Sample-first testing: validate 1 file before all N
- Error-driven refinement: parse errors, don't guess
- Bounded iteration: max 3 attempts, then escalate
- Composability: each skill has single responsibility

---

## Rationale

### Efficacy

**Before**: Multiple attempts with no guidance path.

**After**: Criteria sourced from schema; error messages + criteria guide fixes.

**Result**: Validation path clear, success predictable.

### Efficiency

**Before**: 4 validation runs × 9 files = 36 file operations

**After**: 1 discovery + 3 sample validations + 1 bulk apply = 9 file operations

**Savings**: 4× fewer file operations, faster feedback loop.

### Composability

Skills are reusable across bulk operation domains; no need to reinvent for each task.

---

## Consequences

### Positive

- Reduced iteration loops (bounded to 3)
- Clearer success path (criteria + error guidance)
- Reusable pattern (applicable to any schema validation)
- Composable skills (clear boundaries)
- Better documentation (criteria dict as future reference)

### Tradeoffs

- Upfront discovery cost (worth it for 3+ file operations)
- Requires discoverable schemas (encourages explicit documentation)
- Skill learning curve (mitigated by clear orchestration in executing-backlog)

---

## Evidence from Phase 2

**Task**: Update 9 work items with new frontmatter fields

**Without systematic discovery**:

1. Guess format → Apply to all 9 → Validate → FAIL
2. Guess format B → Apply to all 9 → Validate → FAIL
3. Guess format C → Apply to all 9 → Validate → FAIL
4. Discover pattern from schema → Apply to all 9 → Validate → PASS

Result: 36 file updates, unclear error guidance

**With systematic discovery**:

1. Read schema → Document criteria
2. Apply format to 1 sample → Validate → FAIL
3. Parse error + refine format → Validate sample → PASS
4. Apply to all 9 → Validate all → PASS

Result: 9 file updates, clear error guidance

---

## Next Steps

1. Document the pattern (docs/systematic-validation-workflow.md) ✅
2. Create operational how-to (docs/schema-validation-bulk-operations.md) ✅
3. Use pattern in Phase 3 work items
4. Collect metrics on Phase 3 adoption
5. Evaluate after ≥2 Phase 3 work items completed
