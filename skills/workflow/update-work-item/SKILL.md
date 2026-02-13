---
name: update-work-item
description: "Update an existing work item with status changes, effort tracking, test results, and related commits. Use when progressing work, recording test results, or adjusting estimates. Supports: (1) Status transitions (not_started → in_progress → testing → completed), (2) Effort tracking (estimated_hours → actual_hours), (3) Test and commit tracking, (4) Dependency updates and notes"
metadata: 
  category: project-management
license: MIT
---

# Update Work Item

## Overview

Update progress on an existing work item: change status, record actual effort, add test results, mark related commits, update dependencies, and add implementation notes as work progresses.

## When to Use

Update a work item when:

- Starting work (change status to `in_progress`)
- Completing implementation (change status to `testing`)
- Recording actual hours spent
- Adding related commit hashes
- Logging test results or CI status
- Adjusting estimates based on new information
- Adding implementation notes or blockers

## When NOT to Use

Skip updates for:

- Creating new items (use `create-work-item` skill)
- Finalizing and archiving (use `finalize-work-item` skill)
- Minor comments (just edit as needed, no skill required)

## Frontmatter Fields

### Status and State Reason Fields

```yaml
status: not_started | in_progress | testing | completed
state_reason: null | success | obsolete | redundant | superseded | cancelled
```

| Status | state_reason | Meaning | When to Use |
|--------|--------------|---------|-------------|
| `not_started` | (none) | Ready to begin | Initial creation |
| `in_progress` | (none) | Active development | Actively working |
| `testing` | (none) | Impl done, awaiting results | Tests running, review pending |
| `completed` | `success` | Finished successfully | All criteria met, merged |
| `completed` | `obsolete` | No longer relevant | Market changed, approach outdated |
| `completed` | `redundant` | Duplicate item | Same work in another item |
| `completed` | `superseded` | Made moot by other item | Different item solves it better |
| `completed` | `cancelled` | Work stopped | Stopped, won't implement |

### Effort Tracking

```yaml
estimated_hours: 20          # Set when created
actual_hours: 18             # Update as work progresses, finalize when complete
completed_date: null         # Set when status = completed (YYYY-MM-DD)
```

**Guidelines**:
- `estimated_hours`: Set once, don't change unless scope significantly shifts
- `actual_hours`: Start as `null`, update when complete
- `completed_date`: Set only when moving to completed status

### Commit Tracking

```yaml
related_commit:
  - 6d8c044  # Short hash or fully qualified ref
  - f00459b  # Add commits as they're implemented
```

Record commit hashes and their summary messages as work is merged. Helps trace implementation back to work items.

### Test Results

```yaml
test_results: null | "URL to CI run" | "Local test results summary"
```

Examples:
```yaml
test_results: "https://github.com/squirrel289/temple/actions/runs/12345678"
test_results: "All 47 tests pass, coverage 89%"
test_results: "3 test failures in test_renderer.py (see notes)"
```

### Dependencies

```yaml
dependencies:
  - "[[54_complete_temple_native.md]]"
  - "[[43_implement_template_syntax_validation.md]]"
```

Update if new dependencies emerge during implementation.

## Workflow: Updating Work Items

### 1. Moving to In-Progress

When starting work:

```markdown
---
title: "Implement FilterAdapter"
id: 60
status: in_progress  # Changed from not_started
priority: high
estimated_hours: 20
actual_hours: null
completed_date: null
notes: |
  Started implementation of FilterAdapter in temple/sdk/.
  Initial focus: selectattr and map filters.
---
```

Also add a placeholder for `actual_hours` tracking:
```yaml
actual_hours: 2  # Increment as work progresses
```

### 2. Recording Actual Hours

As work progresses, update `actual_hours`:

```yaml
estimated_hours: 20
actual_hours: 6  # 2 hours initial + 4 more hours
```

Update periodically (after major milestones, at end of session) so you have a sense of actual time investment.

### 3. Adding Related Commits

When work is committed, record the commit hash:

```yaml
related_commit:
  - 6d8c044  # feat(sdk): initial FilterAdapter interface
  - f00459b  # feat(filters): implement selectattr and map
  - a1b2c3d  # docs: add filter usage examples
```
Use the command:
  ```bash
  git log --oneline <short_hash> -n 1 --pretty=format:"  - %h  # %s
  ```
to generate the `related_commit` line for a given `<short_hash>`.

Keep hashes in chronological order. Multiple commits are fine—they show the evolution of the work.

### 4. Transitioning to Testing

When implementation is done, move to testing:

```yaml
status: testing
actual_hours: 18  # Finalize effort
state_reason: null  # Not set yet
notes: |
  Implementation complete. All filters implemented with type signatures.
  Awaiting test results and CI validation.
```

Do NOT set `completed_date` or `state_reason` yet.

### 5. Recording Test Results

After running tests:

```yaml
status: testing
test_results: "https://github.com/squirrel289/temple/actions/runs/98765432"
notes: |
  CI results:
  - 98 tests pass
  - 2 tests fail in test_filter_edge_cases.py (filter_args validation)
  - Coverage 87% (target 85%)
  
  Known issues:
  - Filter arg validation too strict for varargs
  - Will fix in follow-up PR
```

If tests fail, add notes on what needs fixing. Update status back to `in_progress` if rework needed:

```yaml
status: in_progress
actual_hours: 19  # Add time spent debugging
notes: |
  Tests exposed issue with varargs handling. Working on fix in branch feature/varargs-fix.
```

### 6. Moving to Completed

When all tests pass and work is approved:

```yaml
status: completed
state_reason: success  # Set based on completion type
actual_hours: 22  # Final tally
completed_date: 2026-02-12
test_results: "https://github.com/squirrel289/temple/actions/runs/98765432"
notes: |
  All acceptance criteria met:
  - FilterAdapter interface implemented and documented
  - Core filters (selectattr, map, join, default) working
  - 95% test coverage
  - Code reviewed and approved
  - Merged to main in commit a1b2c3d
```

Set `state_reason` to one of:
- `success`: Normal completion with acceptance criteria met
- `obsolete`: Item no longer needed (note why)
- `redundant`: Duplicate of another item (reference it)
- `superseded`: Made moot by another item (reference it)
- `cancelled`: Work stopped before completion (note why)

Leave file in `/backlog/`. The `finalize-work-item` skill handles archiving.

### 7. Adjusting Estimates

If scope changes significantly during work:

```yaml
estimated_hours: 20  # Original
actual_hours: 12     # Current progress, which may exceed estimate
notes: |
  Revised scope: only implementing selectattr, map, and join 
  (default and custom filters deferred to #61).
  New estimated_hours would be ~16, but keeping original to track 
  scope reduction.
```

Or adjust explicitly if scope fundamentally changed:

```yaml
estimated_hours: 28  # Increased from 20 due to schema validation layer
actual_hours: 14
notes: |
  Scope expanded: discovered need for JSON Schema validation 
  in filter arguments. Adjusted estimate by +8 hours.
```

### 8. Updating Dependencies

If new dependencies discovered during work:

```yaml
dependencies:
  - "[[54_complete_temple_native.md]]"
  - "[[44_implement_semantic_validation.md]]"  # Added: type checking needed
```

Update the work item file to reflect these.

## Examples

### Example 1: Feature Work Progress

**Initial creation**:
```yaml
---
title: "Implement FilterAdapter"
id: 60
status: not_started
state_reason: null
priority: high
estimated_hours: 20
actual_hours: null
dependencies:
  - "[[54_complete_temple_native.md]]"
---
```

**After 2 hours**:
```yaml
status: in_progress
actual_hours: 2
notes: |
  Started with interface design and type signatures.
  SelectAttr filter drafted.
```

**After testing**:
```yaml
status: testing
state_reason: null
actual_hours: 18
related_commit:
  - 6d8c044  # feat(sdk): FilterAdapter interface
  - f00459b  # feat(filters): selectattr, map, join, default
test_results: "https://github.com/.../runs/12345678"
notes: |
  All tests pass. 95% coverage. Awaiting code review.
```

**After completion**:
```yaml
status: completed
state_reason: success
actual_hours: 20
completed_date: 2026-02-15
test_results: "https://github.com/.../runs/12345678"
notes: |
  Merged to main. All acceptance criteria met.
```

### Example 2: Bug Fix with Rework

**Starting work**:
```yaml
---
title: "Fix elif parsing edge case"
id: 59
status: in_progress
state_reason: null
estimated_hours: 4
actual_hours: 1
---
```

**Test failure**:
```yaml
status: in_progress
state_reason: null
actual_hours: 3
test_results: "Local: 1 test fails in test_parser.py::test_consecutive_elif"
notes: |
  Found deeper issue: elif blocks interfere when nested.
  Need to refactor block termination logic.
  Revising approach—effort may exceed estimate.
```

**Resolution**:
```yaml
status: testing
state_reason: null
actual_hours: 7
estimated_hours: 4
test_results: "https://github.com/.../runs/87654321"
related_commit:
  - abc1234  # fix(parser): elif block termination logic
notes: |
  Fixed by refactoring block_ends() logic. Took longer due to edge cases,
  but all tests now pass including new consecutive_elif tests.
```

### Example 3: Spike/Research Update

```yaml
---
title: "Evaluate expression engines"
id: 61
status: in_progress
state_reason: null
estimated_hours: 16
actual_hours: 8
notes: |
  Evaluation candidates:
  1. JMESPath - mature, good for JSON, limited type support
  2. Custom recursive descent - flexible, small footprint
  3. meval - lightweight Python evaluator
  
  Progress:
  - JMESPath prototype working (2h)
  - Custom parser WIP (6h) - complexity clear now, drafting comparison doc
  
  Leaning toward option 2 (custom) due to control of type system.
---
```

## Common Patterns

### Weekly Status Update

Review active work items weekly:

```yaml
status: in_progress
actual_hours: 12  # Update from 10
notes: |
  Week of Feb 10: 2 hours progress (mid-week catchup).
  Current blockers: Decision on filter signature format—waiting for architecture review.
  Expected completion: Feb 17
```

### Handling Blockers

```yaml
notes: |
  BLOCKED: Waiting for ADR-006 decision on expression language.
  Cannot finalize filter syntax without it.
  Unblocked when: ADR merged and decision published
  Impact: Pushed completion target to 2026-02-20
```

### Scope Creep Recognition

```yaml
notes: |
  Original estimate: 12 hours (selectattr, map, join)
  Current scope: +default filter + type validation = ~18 hours likely
  Recommendation: Create follow-up item #62 for advanced filters, limit this to core 3.
```

## Tips & Conventions

### Atomic Updates

Each update should correspond to a logical work milestone:
- End of session: time tracking
- After tests run: test results
- After commit: commit hash
- Status change: full progress summary

Don't update work items excessively—focus on meaningful changes.

### Notes Field

Use `notes` for:
- Progress summary
- Blockers or issues
- Scope changes
- Decision points
- Follow-up items

Avoid: detailed implementation notes (keep in commit messages instead)

### Time Tracking Accuracy

Record hours regularly:
- At end of each session
- After significant milestone
- Final tally when completed

This helps estimate accuracy over time.

### Commit Message Integration

Reference work items in commit messages:

```
feat(filters): implement selectattr and map

Implements core filtering operations for FilterAdapter.
Supports filtering sequences by attribute value and projection.

Closes #60
See backlog/60_implement_filter_adapter.md
```

Then update the work item with the commit hash.

## Related Skills

- **`create-work-item`**: For creating new work items
- **`finalize-work-item`**: For archiving completed work items
- **`git-commit`**: For recording commits that can be linked in `related_commit`

## Optional Utility: Repair Commit Order

Use the bundled helper script to normalize `related_commit` / `related_commits`
blocks across backlog files, sorting hashes by commit timestamp and preserving
missing hashes as `MISSING-COMMIT` notes.

```bash
.agents/skills/update-work-item/scripts/normalize-related-commits.sh --dry-run
```
