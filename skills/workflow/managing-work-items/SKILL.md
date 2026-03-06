---
name: managing-work-items
description: "Orchestrate the full lifecycle of work items from creation through finalization. Use when: (1) Starting new tracked work with proper structure, (2) Progressing work items through status transitions, (3) Completing and archiving finished work. Composes: creating-work-item, updating-work-item, finalizing-work-item."
metadata:
  type: document
  subtype: skill
  category: project-management
license: MIT
---

# Managing Work Items

Orchestrate the complete lifecycle of backlog work items from creation to archival. This workflow skill composes three atomic tools to ensure consistent structure, tracking, and completion of work items.

## When to Use

Use this skill when:

- Starting new work that needs tracking (features, bugs, spikes)
- Progressing through the work item lifecycle (status transitions)
- Completing and archiving finished work items
- Managing work items end-to-end in one session
- Ensuring proper work item governance and structure

## When NOT to Use

Skip this skill for:

- Single-phase operations (use the specific tool directly)
- Reading or querying work items (no lifecycle action needed)
- Auditing work item quality (use `auditing-backlog` instead)

## Composed Skills

This workflow delegates to three atomic tools:

- [`creating-work-item`](../../tools/creating-work-item/SKILL.md): Create new work items with proper structure
- [`updating-work-item`](../../tools/updating-work-item/SKILL.md): Update status, effort, commits, and notes
- [`finalizing-work-item`](../../tools/finalizing-work-item/SKILL.md): Complete and archive finished items

Do not duplicate implementation details here. Delegate to source skills for field validation, status transitions, and archival rules.

## Work Item Lifecycle

```asciiflow
┌─────────────────────────────────────────────────────────────┐
│                    Work Item Lifecycle                      │
└─────────────────────────────────────────────────────────────┘

1. Creation (creating-work-item)
   ├─ Auto-number next ID
   ├─ Generate frontmatter structure
   ├─ Define goal, tasks, acceptance criteria
   └─ Status: not_started

2. Implementation (updating-work-item)
   ├─ Transition to in_progress
   ├─ Create feature branch
   ├─ Record commits
   ├─ Track actual hours
   ├─ Add test results
   └─ Transition to ready-for-review

3. Completion (updating-work-item)
   ├─ Validate dependencies closed
   ├─ Verify acceptance criteria
   ├─ Record final metrics
   └─ Transition to closed

4. Finalization (finalizing-work-item)
   ├─ Complete all fields
   ├─ Set state_reason
   ├─ Clean up feature branch
   ├─ Archive to /backlog/archive/
   └─ Link successor items
```

## Workflow

### Phase 1: Creation

**Inputs Required**:

- Work item description or goal
- Priority (low/medium/high/critical)
- Complexity (low/medium/high)
- Estimated hours
- Dependencies (optional)

**Workflow**:

1. Invoke `creating-work-item` with required inputs
2. Verify next available ID
3. Generate structured work item file
4. Validate frontmatter schema
5. Return work item path and ID

**Output**:

- Created work item file path: `/backlog/{id}_{slug}.md`
- Work item ID for reference

**Decision Rules**:

- If duplicate work exists, prompt to update existing instead
- If dependencies are not closed, note blockers in frontmatter
- If scope is unclear, recommend spike first

### Phase 2: Progression

**Inputs Required**:

- Work item ID or file path
- Status transition (e.g., not_started → in_progress)
- Updates: commits, notes, test results, actual hours

**Workflow**:

1. Invoke `updating-work-item` with current status and target status
2. Apply status transition validations:
   - Validate dependency states before closing
   - Auto-create feature branch on in_progress
   - Auto-create PR on ready-for-review
3. Update effort tracking and commit references
4. Add timestamped notes if provided
5. Validate frontmatter schema

**Output**:

- Updated work item with new status
- Feature branch name (if created)
- PR URL (if created)

**Decision Rules**:

- Cannot move to closed if dependencies are not closed
- Cannot skip required status transitions
- Must record actual hours before closing
- Must validate acceptance criteria before ready-for-review

### Phase 3: Finalization

**Inputs Required**:

- Work item ID or file path (must be status: closed)
- State reason (success/obsolete/redundant/superseded/cancelled)
- Final metrics: actual_hours, completed_date, test_results

**Workflow**:

1. Verify work item status is closed
2. Invoke `finalizing-work-item` with state reason
3. Validate completion checklist:
   - All acceptance criteria checked
   - All commits recorded
   - Test results documented
   - Actual hours finalized
4. Archive to `/backlog/archive/`
5. Clean up feature branch
6. Link successor work items if provided

**Output**:

- Archived work item path: `/backlog/archive/{id}_{slug}.md`
- Cleanup summary (branches deleted, commits recorded)

**Decision Rules**:

- Must have state_reason when finalizing
- Cannot finalize if status is not closed
- Must have test_results for state_reason: success
- Must have successor links for state_reason: superseded

## Deterministic Decision Rules

### Creation Phase

1. **ID Assignment**: Always use max(existing IDs) + 1 from `/backlog/` (not archive)
2. **Duplicate Detection**: Search for similar titles/goals before creating
3. **Dependency Validation**: Verify all dependency files exist
4. **Schema Validation**: Run frontmatter linter before committing

### Progression Phase

1. **Status Transitions**: Follow strict state machine:

   ```asciiflow
   not_started → ready → in_progress → ready-for-review → closed
   ```

2. **Branch Creation**: Auto-create on first transition to in_progress
3. **PR Creation**: Auto-trigger on transition to ready-for-review
4. **Dependency Blocking**: Cannot close if any dependency is not closed
5. **Effort Tracking**: Must record actual_hours before closing

### Finalization Phase

1. **Completion Gate**: All acceptance criteria must be checked
2. **Metrics Gate**: Must have actual_hours, completed_date, test_results
3. **State Reason**: Required for all finalizations
4. **Archive Move**: Only move to archive/ after full validation
5. **Branch Cleanup**: Delete feature branch after successful finalization

## Cross-Phase Validations

1. **Schema Compliance**: Run `pnpm run lint:frontmatter` at each phase
2. **Git Integration**: Ensure feature branch exists and is clean
3. **Dependency Chain**: Validate dependency links at creation and closing
4. **Audit Trail**: Timestamped notes required for major transitions

## Integration with Other Skills

### Complementary Workflows

- **`executing-backlog`**: Implements work items; uses `updating-work-item` and `finalizing-work-item`
- **`auditing-backlog`**: Validates work item quality; may recommend using these tools to fix issues
- **`feature-branch-management`**: Auto-invoked by `updating-work-item` for branch operations

### Execution Aspects

- **`guarding-branches`**: Applied during status transitions to merge points
- **`prevalidating-bulk-operations`**: Called if updating multiple work items
- **`parallel-execution`**: Used when implementing multiple work items concurrently

### Tool Integration

- **GitHub PR**: Auto-integration via `updating-work-item` on ready-for-review
- **Git Commits**: Tracked in `related_commit` via `updating-work-item`
- **Test Results**: Recorded via `updating-work-item` with CI URLs

## Output Contract

For each phase, produce:

1. **Creation**: Work item file path and validation status
2. **Progression**: Updated fields summary and any auto-triggered actions (branch, PR)
3. **Finalization**: Archive path and cleanup summary

Always return concrete values, never placeholders.

## Examples

### Example 1: Complete Lifecycle

```bash
# Phase 1: Create
@agent Use managing-work-items to create a work item for implementing
JSON schema validation in the template linter. Priority: high,
Complexity: high, Estimated: 20 hours.

# Phase 2: Progress
@agent Use managing-work-items to move WI-057 to in_progress

@agent Use managing-work-items to record commits 6d8c044, f00459b for WI-057

@agent Use managing-work-items to move WI-057 to ready-for-review
with test results: https://github.com/org/repo/actions/runs/12345

# Phase 3: Close and Finalize
@agent Use managing-work-items to close WI-057 with actual hours: 22

@agent Use managing-work-items to finalize WI-057 with state_reason: success
```

### Example 2: Bulk Progression

```bash
@agent Use managing-work-items to move WI-055, WI-056, WI-057 to closed
after validating their dependencies
```

### Example 3: Spike to Implementation

```bash
# Create spike
@agent Create spike WI-058: Evaluate expression engines. Estimated: 16h

# Complete spike
@agent Finalize WI-058 with state_reason: success, successor: WI-059

# Create follow-up implementation
@agent Create WI-059: Implement JMESPath engine, depends on WI-058
```

## Anti-Patterns

1. **❌ Skip creation, update ad-hoc**: Always use `creating-work-item` for proper structure
2. **❌ Manual archiving**: Use `finalizing-work-item` to ensure cleanup
3. **❌ Force status transitions**: Respect state machine and validation gates
4. **❌ Ignore dependencies**: Always validate dependency closure before closing
5. **❌ Missing metrics**: Record actual hours and test results before finalizing

## Related Skills

- **`creating-work-item`**: Atomic tool for creation (composed here)
- **`updating-work-item`**: Atomic tool for progression (composed here)
- **`finalizing-work-item`**: Atomic tool for completion (composed here)
- **`executing-backlog`**: Higher-level workflow for implementing work items
- **`auditing-backlog`**: Quality validation for work items
- **`feature-branch-management`**: Git branch automation for work items
