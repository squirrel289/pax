---
name: handle-pr-feedback
description: "Coordinate PR review loop—detect feedback severity, address minor comments automatically, revert work items if major changes needed. Use when PR has unresolved review feedback. Supports: (1) Comment triage by severity, (2) Auto-resolution of minor comments, (3) Work item reversion on blocker feedback, (4) Feedback summarization"
metadata:
  category: workflow
  aspects:
    - interaction-modes
  decisions:
    - id: feedback_severity
      trigger: after-triage
      yolo: [use_triage]
      collaborative:
        prompt: "Classify feedback severity"
        options:
          - id: trivial
            label: "Trivial (auto-fix)"
            action: auto-fix
          - id: minor
            label: "Minor (fix and re-request review)"
            action: resolve-minor
          - id: moderate
            label: "Moderate (manual fix)"
            action: resolve-moderate
          - id: major
            label: "Major (revert to in_progress)"
            action: revert-status
          - id: blocker
            label: "Blocker (revert and escalate)"
            action: revert-and-escalate
          - id: custom
            label: "Other action..."
            allow_freeform: true
        resume: "Proceed with selected action"
license: MIT
---

# Handle PR Feedback

## Overview

Monitor and respond to pull request review feedback. Triage comments by severity, automatically address minor issues (typos, documentation), and intelligently revert work items when major changes are requested. Keeps feedback loop coordinated between PR state and work item status.

## When to Use

Handle PR feedback when:

- PR has unresolved review comments or requested changes
- Feedback arrives after initial submission
- Need to decide: address inline fixes vs. major rework
- Want to maintain synchronization between PR state and work item status
- Preparing for subsequent review rounds

## When NOT to Use

Skip this skill for:

- PR just created, awaiting initial review (wait for feedback first)
- Already-merged PRs (use `finalize-work-item` instead)
- Complex architectural feedback requiring discussion (use collaborative mode and escalate)

## Feedback Triage System

### Comment Classification

Comments are classified by severity and required action:

| Severity | Type | Requires | Auto-Fix | Revert | Example |
|----------|------|----------|----------|--------|---------|
| **Trivial** | Typo, formatting, comment | Inline fix | ✅ Yes | ❌ No | Spelling error in variable name |
| **Minor** | Documentation, test expectations | Code change | ✅ Optional | ❌ No | Add docstring, clarify test |
| **Moderate** | Logic refinement, optimization | Code change | ❌ Manual | ❌ No | "Consider using map instead of loop" |
| **Major** | Incorrect approach, design flaw | Significant rework | ❌ Manual | ✅ Yes | "This violates our decorator pattern" |
| **Blocker** | Architectural, breaking change | Scope change | ❌ Escalate | ✅ Yes | "Doesn't comply with RFC-007" |

### Decision Tree

```
Comment Received
├─ Severity: Trivial or Minor?
│  └─ YES → resolve-pr-comments (auto-fix or prompt)
│     ├─ Success → Mark thread resolved
│     └─ Conflict → Notify reviewer, manual fix
├─ Severity: Moderate?
│  └─ YES → Notify developer, manual fix
│     └─ Requires design discussion? → Escalate in collaborative mode
├─ Severity: Major or Blocker?
│  └─ YES → Decision point
│     ├─ Can refactor without scope change? → Manual fix, keep testing status
│     └─ Requires scope change? → Revert to in_progress
│        ├─ update-work-item (testing → in_progress)
│        ├─ feature-branch-management sync (rebase if main changed)
│        └─ Rescope work in notes
```

## Workflow: Handling Feedback

### Phase 1: Fetch and Analyze

1. **Fetch PR Details**
   ```bash
   # Via pull-request-tool: Fetch PR details, reviews, comments
   pr_details = pull-request-tool.fetch(pr_number)
   comments = pull-request-tool.list_comments(pr_number, filter=unresolved)
   reviews = pull-request-tool.fetch_reviews(pr_number)
   ```

2. **Categorize Comments**
   - Extract severity from comment content (manual, or via NLP heuristics)
   - Group by severity and topic
   - Identify blockers vs. nice-to-have

3. **Assess Impact**
   - Count of trivial/minor vs. major/blocker comments
   - Do blockers represent scope change or design issue?
   - Can work proceed incrementally or does rework need full reset?

### Phase 2: Decision

Make decision based on feedback distribution:

**Option A: Minor Feedback Only**
- Proceed with inline fixes via `resolve-pr-comments`
- Keep work item in `testing` status
- Update PR with fixes, re-request review

**Option B: Mixed (Minor + Moderate)**
- Resolve minor items automatically or manually
- Address moderate items with discussion (collaborative mode)
- Keep work item in `testing` but notify reviewer of changes
- Plan for follow-up review round

**Option C: Major/Blocker Feedback**
- Revert work item to `in_progress`
- Notify developer of scope change
- Update work item notes with feedback details
- Schedule rework session

### Phase 3: Execute Resolution

#### If Minor Feedback (Option A):

```yaml
# Step 1: Auto-resolve trivial comments
resolve-pr-comments pr_number=247 severity=trivial auto_resolve=true

# Step 2: Push fixes
git add -A
git commit -m "docs: address review feedback"
git push origin feature/60-filter-adapter

# Step 3: Mark threads resolved
pull-request-tool resolve threads=<ids>

# Step 4: Re-request review
pull-request-tool request-review pr_number=247

# Step 5: Keep work item in testing
# (No status change needed)
```

#### If Moderate Feedback (Option B):

```yaml
# Step 1: Resolve trivial items automatically
resolve-pr-comments pr_number=247 severity=trivial auto_resolve=true

# Step 2: Collaborative resolution for moderate items
resolve-pr-comments pr_number=247 severity=moderate interaction=collaborative

# Step 3: Push all fixes
git add -A
git commit -m "feat: address review feedback and refinements"
git push origin feature/60-filter-adapter

# Step 4: Update work item with changes
update-work-item id=60 \
  status=testing \
  notes="Addressed review feedback: optimized filter logic, improved test coverage"

# Step 5: Re-request review
pull-request-tool request-review pr_number=247
```

#### If Major/Blocker Feedback (Option C):

```yaml
# Step 1: Notify developer
# (In collaborative mode, ask permission to revert)

# Step 2: Revert work item to in_progress
update-work-item id=60 \
  status=in_progress \
  notes="PR feedback: Design violates decorator pattern (Reviewer: @alice).
         Requires rework. See PR #247 for details.
         Plan: Refactor FilterAdapter to use composition instead of inheritance."

# Step 3: Sync branch
feature-branch-management sync --base=main

# Step 4: Create issue or note for rework
# (Can create linked issue for the refactoring)

# Step 5: Notify reviewer of revert
pull-request-tool reply \
  comment_id=<feedback_comment> \
  body="Thanks for the feedback! Reverting to in_progress to refactor approach.
        Will resubmit for review once changes are complete."
```

### Phase 4: Finalize

After fixes are pushed:

```yaml
# Option: Auto re-request review (if using CI auto-merge)
pull-request-tool request-review pr_number=247

# Option: Notify team in notes
# (Work item notes now reflect latest feedback status)

# Next: Wait for follow-up review
# Then: Return to Phase 1 if more feedback, or proceed to merge
```

## Interaction Modes (Aspect)

This skill uses the interaction-modes aspect for decision handling.

- Aspect: [interaction-modes](../../aspects/interaction-modes/ASPECT.md)
- Decision point: `feedback_severity`
- Parameter: `interaction-mode` = yolo | collaborative

## Options

### Filtering

- `severity`: Severity filter (all, trivial, minor, moderate, major, blocker)
  - Default: all unresolved
  - Example: `severity=minor` processes only trivial + minor comments

- `reviewer`: Filter comments by specific reviewer
  - Default: all reviewers
  - Example: `reviewer=@alice` processes only Alice's feedback

### Auto-Fixing

- `auto_fix_trivial`: Automatically fix typos and formatting
  - Default: true
  - Requires branch write access

- `auto_resolve_minor`: Automatically attempt minor fixes
  - Default: false
  - Riskier; may need manual review

### Thresholds

- `blocker_revert_threshold`: Number of blocker comments to trigger revert
  - Default: 1 (any blocker reverts)
  - Example: `blocker_revert_threshold=2` requires 2+ blockers

- `major_discussion_threshold`: Number of major items before escalating to discussion
  - Default: 2
  - Prevents "death by a thousand cuts"

## Integration with Work Item Status

### Status Transitions Triggered

```yaml
# Normal flow:
testing → testing (minor fixes)
testing → in_progress (major feedback, revert for rework)

# After rework:
in_progress → testing (new fixes pushed, re-requests review)
```

### Notes Field Updates

```yaml
# Example annotation after feedback:
notes:
  - timestamp: 2024-06-01T12:00:00Z
    user: @john
    note: |
      ## Review Feedback (Round 1)
      
      **Minor Issues Addressed:**
      - Fixed docstring typos in FilterAdapter.map()
      - Added test for edge case with empty sequences
      - Improved error message clarity
      
      **Blocker Feedback (Reverted):**
      - Reviewer raised: "Doesn't follow decorator pattern"
      - Decision: Refactor FilterAdapter to use composition
      - Branch: feature/60-refactor-adapter
      - Status: Reworking
```

## Error Handling

### Cannot Classify Comment Severity

```yaml
error: "Cannot auto-classify comment severity"
comment: "The impl looks good but let me check the pattern matching part"
action: "Manual review required; ask reviewer for explicit severity label or escalate"
```

## PR Comment Severity Labels (Optional Enhancement)

GitHub labels can help mark comment severity:

```yaml
# Labels to add to work item or PR:
labels:
  - severity/trivial     # Typo, formatting
  - severity/minor       # Docs, test expectations
  - severity/moderate    # Logic refinement
  - severity/major       # Design issue
  - severity/blocker     # Architectural violation
```

Reviewers can label their comments. handle-pr-feedback reads these labels for better classification.

### Exception Handling

#### PR Not Found

```yaml
error: "PR #247 not found"
action: "Verify PR number is correct"
hint: "use pull-request-tool list to find PR number"
```

#### Branch Deleted

```yaml
error: "Branch feature/60-filter-adapter has been deleted"
action: "Cannot sync branch; work item revert would be manual"
hint: "recreate branch from last known commit, or file manual issue"
```

#### Conflicting Feedback

```yaml
warning: "Comment from reviewer 1 conflicts with comment from reviewer 2"
comment_1: "Use list comprehension for clarity"
comment_2: "Use functional map() for consistency"
action: "Require discussion in collaborative mode; escalate if unresolved"
```

## Related Skills

See the dependency matrix in [docs/SKILL_COMPOSITION.md](docs/SKILL_COMPOSITION.md#skill-dependency-matrix) for the canonical calling relationships.

- **`pull-request-tool`**: Fetch PR details, comments, reviews (via PR_MANAGEMENT_INTERFACE)
- **`resolve-pr-comments`**: Execute comment fixes and resolutions
- **`update-work-item`**: Revert work item status and record feedback
- **`feature-branch-management`**: Sync branch during rework
- **`process-pr`**: Full PR workflow (includes feedback loop via handle-pr-feedback)

## Workflow Integration

### Part of process-pr

`handle-pr-feedback` is invoked by `process-pr` in **Stage 3: Address Feedback**:

```yaml
process-pr pr_number=247
├─ Stage 1: Assessment (fetch PR, check reviews)
├─ Stage 2: Local verification (optional)
├─ Stage 3: Address Feedback ← handle-pr-feedback is called here
│  └─ handle-pr-feedback pr_number=247
│     ├─ Fetch comments
│     ├─ Classify severity
│     ├─ Auto-fix or revert as needed
│     └─ Report changes
├─ Stage 4: Final verification
├─ Stage 5: Merge
└─ Stage 6: Post-merge cleanup
```

### Can Be Used Standalone

For manual PR feedback handling:

```bash
handle-pr-feedback pr_number=247 interaction=collaborative
```

## Tips & Best Practices

### 1. Encourage Structured Feedback

Ask reviewers to follow pattern:

```markdown
**[SEVERITY: BLOCKER]** Design violates RFC-007
Details: ...
Suggestion: Refactor to use decorator pattern
Priority: Must fix before merge
```

Enables better automation of triage.

### 2. Set Feedback Expectations

Document in CONTRIBUTING.md:

```markdown
## Review Comment Severity

- **Trivial**: Typos, formatting. Author may auto-fix.
- **Minor**: Docs, tests. Author fixes before merge.
- **Moderate**: Logic refinement. Discuss if time is constrained.
- **Major**: Design issue. Requires rework before merge.
- **Blocker**: Architectural violation. Reverts PR for rework.
```

### 3. Use Labels for Clarity

```markdown
Label comments with severity:
- `[trivial]` Typo in variable name
- `[minor]` Add docstring
- `[major]` Doesn't follow pattern
```

### 4. Escalate Early

If feedback suggests scope creep, escalate to product/architecture:

```yaml
# In collaborative mode:
> Multiple blockers suggest scope mismatch. 
> Escalate to architecture review? [Y/n]
```

Prevents code thrashing from misaligned expectations.

### 5. Document Decisions

In work item notes, record feedback and decision:

```yaml
notes:
  - timestamp: 2024-06-01T12:00:00Z
    user: @john
    note: |
      ## Review Feedback

      **Concern**: "Filter logic doesn't handle None values"
      **Decision**: Add filter(None) pass; document in ADAPTER_SPEC.md
      **Status**: Fixed and re-requested review
```

## Common Scenarios

### Scenario A: One Round of Minor Fixes

```
1. PR submitted, reviewer approves with minor comments
2. handle-pr-feedback auto-fixes trivial issues
3. Changes pushed, reviewer re-requested
4. All approved, merge via process-pr
```

### Scenario B: Feedback Leads to Rework

```
1. PR submitted, reviewer requests major redesign
2. handle-pr-feedback reverts work item to in_progress
3. Developer reworks architecture
4. New branch/PR created
5. Reviewer approves second round
6. Merge via process-pr
```

### Scenario C: Conflicting Feedback

```
1. PR submitted, reviewers disagree on approach
2. handle-pr-feedback escalates to discussion (collaborative)
3. Team discusses in comment thread or sync meeting
4. Decision made, developer implements
5. Re-submit for review
```

## References

- GitHub PR Comments API: https://docs.github.com/en/rest/reference/pulls#comments
- Review Comments: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-a-pull-request/about-pull-request-reviews
- PR_MANAGEMENT_INTERFACE: See tools/PR_MANAGEMENT_INTERFACE.md
