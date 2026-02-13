---
name: finalize-work-item
description: "Complete and archive a finished work item, moving it from /backlog/ to /backlog/archive/. Use when work is tested, reviewed, and ready to close. Supports: (1) Verify completion (all acceptance criteria met), (2) Record final metrics (actual_hours, completed_date, test_results), (3) Archive to history, (4) Link successor work items if needed"
metadata: 
  category: project-management
license: MIT
---

# Finalize Work Item

## Overview

Formally complete a work item by verifying all acceptance criteria, recording final metrics, and archiving it from active backlog to historical record. Finalizing work items keeps the active backlog lean and creates an audit trail of completed work.

## When to Use

Finalize a work item when:

- Implementation is complete and tested
- Code is reviewed and merged to main
- All acceptance criteria are verified
- Test results are recorded
- Actual hours are finalized
- Ready to close and archive

## When NOT to Use

Don't finalize if:

- Work is still in progress (use `update-work-item` instead)
- Tests are still failing or pending
- Code review is incomplete
- Acceptance criteria not fully met
- Successor work needed (create #2 first, then link)

## Finalization Checklist

Before finalizing, verify:

- [ ] Status is `completed`
- [ ] All acceptance criteria checked/verified
- [ ] `actual_hours` recorded (final tally)
- [ ] `completed_date` set (YYYY-MM-DD)
- [ ] `test_results` documented (URL or summary)
- [ ] `related_commit` includes all implementation commits
- [ ] Code merged to main
- [ ] No open PRs or pending reviews
- [ ] Dependencies listed for successor items (if any)
- [ ] `notes` summarize outcome and any follow-ups

## Workflow: Finalizing a Work Item

### 1. Verify Completion

Review the work item's acceptance criteria:

```markdown
## Acceptance Criteria

- [x] FilterAdapter interface implemented and documented
- [x] Core filters (selectattr, map, join, default) working
- [x] Unit tests cover all filter functions (95% coverage)
- [x] Integration tests with renderer pass
- [x] Type annotations complete and validated by mypy
- [x] Code review approved (PR #247)
- [x] Merged to main
```

All boxes should be checked (✓).

### 2. Finalize Frontmatter

Ensure all metadata is complete with appropriate `state_reason`:

```yaml
---
title: "Implement FilterAdapter"
id: 60
status: completed
state_reason: success
priority: high
complexity: medium
estimated_hours: 20
actual_hours: 22  # Final recorded hours
completed_date: 2026-02-15  # Completion date
related_commit:
  - 6d8c044  # feat(sdk): FilterAdapter interface
  - f00459b  # feat(filters): core filters (selectattr, map, join, default)
  - a1b2c3d  # test(filters): unit and integration tests
  - c4d5e6f  # docs: add filter usage to ADAPTER_SPEC.md
test_results: "https://github.com/squirrel289/temple/actions/runs/98765432"
dependencies: []
related_backlog: []
notes: |
  Completed successfully. All 4 core filters implemented with type signatures.
  
  Test results:
  - 102 tests pass
  - 0 tests fail
  - Coverage 95%
  - CI complete
  
  Merged to main in commit c4d5e6f.
  
  Follow-up work:
  - Custom filters via plugin interface (proposed #61)
  - Filter documentation and examples (proposed #62)
---
```

### State Reason Values

Set `state_reason` to document why work is complete:

| state_reason | Meaning | Use When |
|--------------|---------|----------|
| `success` | Completed successfully | All acceptance criteria met, fully tested, merged |
| `obsolete` | No longer relevant | Market changed, approach outdated, not needed anymore |
| `redundant` | Duplicate | Same work done in another item (reference it) |
| `superseded` | Made moot | Different item solves it better (reference it) |
| `cancelled` | Work stopped | Stopped before completion (note why, may save effort for later) |

**Key requirements**:
- `status: completed` (no other value)
- `state_reason: success | obsolete | redundant | superseded | cancelled`
- `actual_hours: <number>` (not null)
- `completed_date: YYYY-MM-DD`
- `test_results: <URL or summary>` (required for success, optional for other reasons)
- `related_commit:` (required for success, optional for other reasons)

### 3. Record Final Notes

Add final context in `notes`:

```yaml
notes: |
  ## Completion Summary
  
  Successfully implemented FilterAdapter SDK and core filters.
  
  ### Deliverables
  - temple/sdk/adapter.py extended with FilterAdapter class
  - temple/sdk/filters.py with selectattr, map, join, default
  - tests/test_filters.py with 47 new tests
  - docs/ADAPTER_SPEC.md with filter documentation
  
  ### Metrics
  - Estimated: 20 hours
  - Actual: 22 hours (slight scope expansion for validation layer)
  - Test coverage: 95%
  - Tests passing: 102/102
  
  ### Follow-ups
  - Plugin architecture for custom filters (proposed #61)
  - Advanced filter examples (proposed #62)
  - Performance benchmarking (tracked in asv/)
  
  Ready for release in v1.0 milestone.
```

### 4. Archive the File

Move the file from `/backlog/` to `/backlog/archive/`:

**Before**:
```
/backlog/60_implement_filter_adapter.md
```

**After**:
```
/backlog/archive/60_implement_filter_adapter.md
```

### 5. Update Index (if applicable)

If the backlog has an index file (`template.md`, `README.md`), update it to move the item from active to completed section.

Example, in `/backlog/temple.md`:

```markdown
## Active Work Items (In Progress)

- [[55_adapter_spec_impl.md]] - Implement Adapter SDK
- [[56_jinja2_adapter_prototype.md]] - Jinja2 adapter prototype

## Completed Work Items (Archived)

- [[60_implement_filter_adapter.md]] ✓ (2026-02-15)
- [[54_complete_temple_native.md]] ✓ (2026-02-10)
```

## Examples

### Example 1: Successful Feature Completion

**Original work item**:
```yaml
---
title: "Implement FilterAdapter"
id: 60
status: not_started
estimated_hours: 20
actual_hours: null
completed_date: null
dependencies:
  - "[[54_complete_temple_native.md]]"
---
```

**Finalized**:
```yaml
---
title: "Implement FilterAdapter"
id: 60
status: completed
state_reason: success
estimated_hours: 20
actual_hours: 22
completed_date: 2026-02-15
test_results: "https://github.com/squirrel289/temple/actions/runs/98765432"
related_commit:
  - 6d8c044
  - f00459b
  - a1b2c3d
  - c4d5e6f
dependencies: []
notes: |
  ✓ Completed successfully
  
  All 4 core filters implemented, tested, and merged.
  Follow-up items #61 (custom filters) and #62 (examples) created.
---
```

**File moved**: `backlog/60_implement_filter_adapter.md` → `backlog/archive/60_implement_filter_adapter.md`

### Example 2: Partially Completed Spike

**Original**:
```yaml
---
title: "Evaluate expression engines"
id: 61
status: in_progress
estimated_hours: 16
actual_hours: 14
---

## Goal

Research three expression engine approaches for advanced data filtering.

## Tasks

1. **JMESPath evaluation** ✓
   - Mature library with JSON support
   - Limited type system control
   - Conclusion: Good but not ideal for typed filters

2. **Custom recursive descent parser** ✓
   - Flexible, integrates with type system
   - Requires maintenance burden
   - Conclusion: Best option for our needs

3. **meval Python evaluator** (deferred)
   - Lightweight but less type-aware
   - Deferred to future evaluation
```

**Finalized as partial completion** (some criteria deferred):
```yaml
---
title: "Evaluate expression engines"
id: 61
status: completed
state_reason: success
estimated_hours: 16
actual_hours: 14
completed_date: 2026-02-12
test_results: |
  Evaluation document: docs/expression_engine_evaluation.md
  Recommend: Custom parser (option 2)
notes: |
  ✓ Completed (spike, scope limited)
  
  Evaluated JMESPath and custom parser options in depth.
  Deferred meval evaluation (low priority).
  
  Recommendation: Build custom recursive descent parser for type-aware expressions.
  This decision will guide implementation in #62.
  
  Deliverable: Expression engine evaluation report (docs/expression_engine_evaluation.md)
---
```

### Example 3: Completed with Known Limitations

**Work item**:
```yaml
---
title: "Implement base linting integration"
id: 57
status: completed
state_reason: success
estimated_hours: 12
actual_hours: 11
completed_date: 2026-02-09
test_results: "91 tests pass, 2 known failures in edge cases"
related_commit:
  - abc1234  # feat(linter): integrate external base format linters
  - def5678  # test: add integration tests for JSON/YAML/Markdown
notes: |
  ✓ Completed with known limitations
  
  Core functionality implemented: JSON, YAML, Markdown linting integrated.
  
  Known issues (defer to follow-up):
  - HTML linting incomplete (requires additional parser setup) → tracked in #58
  - Performance: Large files (>10MB) slow (tracked in #63)
  
  Follow-up items:
  - HTML linting completion (#58)
  - Performance optimization (#63)
  
  Tests: 91 pass, 2 skip (HTML-related), 0 fail
  Coverage: 87%
---
```

### Example 4: Completed but Superseded

**Work item**:
```yaml
---
title: "Evaluate TOML support for schemas"
id: 52
status: completed
state_reason: obsolete
completed_date: 2026-02-05
actual_hours: 6
notes: |
  ✗ Marked obsolete
  
  Researched TOML schema support. Concluded that JSON Schema is sufficient
  and TOML adds minimal value (most users prefer JSON).
  
  Decision: Defer TOML support indefinitely.
  Superseded by: Decision in ADR-004 to focus on JSON Schema only.
  
  This work is archived for reference but no follow-up planned.
---
```

## Completion Scenarios

### Scenario A: Successful Completion

All acceptance criteria met, no follow-ups:

```yaml
status: completed
state_reason: success
notes: |
  ✓ Completed successfully
  All acceptance criteria verified.
  No follow-up work required.
```

Move to archive.

### Scenario B: Success with Follow-ups

Work complete, but identified future improvements:

```yaml
status: completed
state_reason: success
notes: |
  ✓ Completed successfully
  
  Follow-up work identified:
  - Performance optimization #63
  - HTML linting completion #58
```

Create the follow-up items (with dependencies linking back), then move to archive.

### Scenario C: Made Obsolete

Market changed, approach outdated, or decision made to not pursue:

```yaml
status: completed
state_reason: obsolete
notes: |
  ✗ Marked obsolete
  
  Reason: Market moved away from this approach.
  Decision in ADR-005 to focus on alternative solution.
  
  Related item: #72 (new approach)
```

Move to archive for historical reference.

### Scenario D: Redundant/Duplicate

Same work done elsewhere:

```yaml
status: completed
state_reason: redundant
notes: |
  ✗ Marked redundant
  
  Duplicate of: [[63_similar_feature_name.md]]
  
  This item identified same problem independently.
  Resolution implemented in #63 instead.
  Archiving to avoid confusion.
```

Move to archive with clear reference to canonical item.

### Scenario E: Superseded

Another item solves it better or more broadly:

```yaml
status: completed
state_reason: superseded
notes: |
  ✗ Marked superseded
  
  Original scope: Implement filter validation only
  Superseded by: [[65_unified_expression_validation.md]]
  
  Item #65 provides validation for all expressions, making this
  narrower approach unnecessary. Solution rolled up.
```

Move to archive with reference to superseding item.

### Scenario F: Cancelled

Work stopped before completion (may resume later):

```yaml
status: completed
state_reason: cancelled
actual_hours: 6  # Partial work
notes: |
  ✗ Cancelled
  
  Reason: Dependency on ADR-006 decision not made in time for release.
  Can resume after ADR resolved.
  
  Blocker: Waiting for architecture decision on expression language.
  Status: ADR-006 in draft, expected resolution by 2026-03-15.
  
  Work done:
  - Requirements captured in docs/expression-requirements.md
  - Proof-of-concept in branch feature/expressions-poc
```

Move to archive with clear context for anyone who needs to resume.

## Best Practices

### 1. Link Related Work

If this item enables follow-ups, create those items first and link them:

```yaml
notes: |
  Follow-up items created:
  - [[61_advanced_filters.md]]
  - [[62_filter_documentation.md]]
```

### 2. Document Lessons Learned

In `notes`, capture insights for future similar work:

```yaml
notes: |
  ## Lessons Learned
  
  - Type annotation setup took longer than expected (3 extra hours)
    → Future features should allocate more time for type validation
  - Early integration with CI saved debugging time
    → Recommend CI integration in design phase
```

### 3. Consistent Completed Dates

Use consistent date format: `YYYY-MM-DD` (ISO 8601)

```yaml
completed_date: 2026-02-15  # Good
completed_date: "Feb 15, 2026"  # Avoid
```

### 4. Comprehensive Related Commits

Link all commits that implement this work:

```yaml
related_commit:
  - 6d8c044  # Initial design
  - f00459b  # Feature implementation
  - a1b2c3d  # Bug fixes from review
  - c4d5e6f  # Documentation updates
  - d6e7f8g  # Performance tuning
```

Order chronologically. This creates an audit trail.

### 5. Accurate Effort Recording

Final `actual_hours` should include all time:

```yaml
estimated_hours: 20
actual_hours: 22  # Include design review, testing, docs, PR feedback
```

This helps calibrate estimates for future similar work.

## Archiving Process

### File Operations

```bash
# Move file to archive
mv /backlog/<number>_<slug>.md /backlog/archive/<number>_<slug>.md

# Update index if applicable
# Edit /backlog/temple.md or similar
```

### Git Commit

Optionally commit the archival as a housekeeping change:

```bash
git add backlog/archive/<number>_<slug>.md backlog/temple.md
git commit -m "chore: archive completed backlog item #<number>"
```

## Quick Checklist

```markdown
## Finalization Checklist for Item #<number>

- [ ] Implementation complete and tested (or decision made to stop work)
- [ ] All acceptance criteria verified ✓ (or marked with state_reason)
- [ ] `status: completed`
- [ ] `state_reason: success | obsolete | redundant | superseded | cancelled`
- [ ] `actual_hours` recorded
- [ ] `completed_date` set (YYYY-MM-DD)
- [ ] `test_results` documented (if applicable)
- [ ] `related_commit` lists all implementation commits (if applicable)
- [ ] Code merged to main (if applicable)
- [ ] `notes` summarize outcome and explain state_reason
- [ ] Follow-up items created (if applicable and linked in notes)
- [ ] File moved to `/backlog/archive/`
- [ ] Index updated (if applicable)
```

## Related Skills

- **`create-work-item`**: For creating new work items
- **`update-work-item`**: For tracking progress during implementation
- **`git-commit`**: For recording commits that link to work items
