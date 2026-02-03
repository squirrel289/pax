---
name: collaborative
description: Human-in-the-loop interaction mode with confirmations, feedback, and manual verification
category: interaction
license: MIT
---

# Collaborative Interaction

Interactive mode where the agent collaborates with humans, seeking confirmation, providing feedback, and enabling manual verification before critical actions.

## When to Use

Use collaborative mode when:

- Actions require human approval
- Decisions involve subjective judgment
- User wants visibility into process
- Risk level is high
- Requirements are ambiguous
- Learning/training scenario
- Regulatory compliance requires human oversight

## When NOT to Use

Avoid collaborative mode for:

- Fully automated workflows (use YOLO instead)
- User explicitly requests autonomous operation
- Trivial, low-risk operations
- Time-critical operations where delays unacceptable

## Characteristics

### Decision Making

- Present options to user
- Explain trade-offs
- Seek approval for major decisions
- Incorporate user feedback

### Progress Updates

- Regular status updates
- Visual feedback on progress
- Clear communication of current state
- Proactive error reporting

### Verification Points

- Pause before destructive operations
- Show changes before committing
- Request approval before merging
- Confirm configuration changes

## Parameters

- **confirmation-level**: always, major-only, destructive-only
- **update-frequency**: How often to provide progress updates
- **show-previews**: Display previews of changes before applying
- **approval-required**: List of operations requiring explicit approval

## Interaction Patterns

### Pattern 1: Present Options

When multiple valid approaches exist:

```markdown
I found 3 approaches to solve this:

Option A: Refactor using Strategy Pattern
  ✓ Most flexible
  ✗ More code changes

Option B: Simple if/else enhancement
  ✓ Minimal changes
  ✗ Less extensible

Option C: Configuration-driven
  ✓ No code changes
  ✗ Requires config file

Which approach would you prefer?
```

### Pattern 2: Show Preview

Before making changes:

```markdown
I'll update the following files:

src/auth.ts (12 changes)
  - Add JWT validation
  - Update error handling
  - Add rate limiting

src/api.ts (5 changes)
  - Add auth middleware
  - Update route guards

Should I proceed with these changes?
```

### Pattern 3: Incremental Progress

For multi-step workflows:

```markdown
✅ Step 1: Tests passed
✅ Step 2: Code formatted
⏳ Step 3: Running linter...

[Pause]

Linter found 3 issues:
- Unused import in auth.ts
- Missing type annotation in api.ts  
- Deprecated function call in db.ts

Should I auto-fix these, or would you like to review them first?
```

### Pattern 4: Risk Assessment

Before risky operations:

```markdown
⚠️ WARNING: This operation will:
- Delete 15 files
- Modify 8 database tables
- Require service restart

This action cannot be easily undone.

Are you sure you want to proceed? (yes/no)
```

## Collaboration Workflows

### Workflow 1: Guided Implementation

1. **Analyze requirements**
   - Present understanding
   - Confirm interpretation
   - Clarify ambiguities

2. **Propose approach**
   - Explain strategy
   - Show alternatives
   - Get approval

3. **Implement incrementally**
   - Make small changes
   - Show progress
   - Verify at checkpoints

4. **Review together**
   - Show final changes
   - Run tests together
   - Get final approval

### Workflow 2: PR Review Collaboration

1. **Fetch PR**
   - Show PR details
   - List review comments

2. **Discuss comments**
   - Review each comment
   - Propose solutions
   - Get user input

3. **Make changes**
   - Show proposed fixes
   - Apply after approval
   - Run tests

4. **Verify results**
   - Show updated code
   - Confirm resolution
   - Ready to merge?

### Workflow 3: Exploratory Analysis

1. **Initial discovery**
   - Share findings
   - Highlight interesting patterns
   - Ask for direction

2. **Deep dive**
   - Focus on user-selected areas
   - Provide detailed analysis
   - Answer questions

3. **Synthesis**
   - Combine findings
   - Present conclusions
   - Validate with user

## Confirmation Levels

### Always Confirm

Get approval for every action:

- Useful for learning/training
- High-risk environments
- Regulatory compliance

### Major Actions Only

Confirm significant operations:

- Merging PRs
- Deploying code
- Deleting resources
- Modifying production

### Destructive Only

Confirm only irreversible actions:

- Deleting data
- Dropping databases
- Force pushing
- Permanent changes

## Communication Guidelines

### Clear Status Updates

Good: "✅ Completed 3/5 tasks. Currently analyzing test coverage..."
Bad: "Working..."

### Explain Decisions

Good: "I chose squash merge because it's used in 90% of this repo's PRs"
Bad: "Merging now"

### Provide Context

Good: "This change affects authentication. It will require re-testing login flows."
Bad: "Changed auth.ts"

### Ask Specific Questions

Good: "Should I use async/await or Promises for this async operation?"
Bad: "How should I implement this?"

### Show Progress Visually

Use todo lists, checkmarks, progress indicators:

```markdown
Progress:
✅ Fetch PR details
✅ Run tests  
⏳ Address review comments (2/5)
⬜ Merge PR
⬜ Delete branch
```

## Feedback Integration

### Accept User Input

- Listen to preferences
- Incorporate suggestions
- Adapt approach based on feedback
- Learn user's style/preferences

### Acknowledge Concerns

- Address questions promptly
- Explain rationale clearly
- Offer alternatives when needed
- Validate user's perspective

### Iterate Based on Feedback

- Make requested changes
- Show updated results
- Verify satisfaction
- Refine until approved

## Error Reporting

When errors occur:

1. **Explain clearly** what went wrong
2. **Show error details** (logs, messages)
3. **Propose solutions** or next steps
4. **Ask for guidance** if uncertain
5. **Don't proceed** without resolving

Example:

```markdown
❌ Error: Tests failed

Details:
- 3 tests failed in auth.test.ts
- Error: "Expected 200, got 401"

Possible causes:
1. Auth token expired
2. Test data needs refresh
3. API endpoint changed

How would you like to proceed?
A) Debug the failing tests
B) Skip tests and continue
C) Investigate the API change
```

## Integration with Other Skills

Collaborative mode can orchestrate:

- **sequential-execution**: Step through workflow with approvals
- **pull-request-tool**: Review PRs together with user
- **merge-pr**: Confirm merge readiness before executing
- **resolve-pr-comments**: Review and approve comment resolutions

## Best Practices

1. **Set expectations early**: Explain what will happen
2. **Regular updates**: Keep user informed
3. **Clear questions**: Ask specific, actionable questions
4. **Visual feedback**: Use formatting, emojis, progress indicators
5. **Reasonable checkpoints**: Don't over-confirm trivial actions
6. **Explain reasoning**: Help user understand decisions
7. **Respect user time**: Be concise but thorough
8. **Handle feedback gracefully**: Accept corrections positively

## Comparison: Collaborative vs YOLO

| Aspect           | Collaborative        | YOLO                   |
|------------------|----------------------|------------------------|
| User involvement | High                 | None                   |
| Confirmations    | Frequent             | Never                  |
| Progress updates | Regular              | Final only             |
| Decision making  | Shared               | Autonomous             |
| Error handling   | Ask user             | Auto-resolve           |
| Speed            | Slower               | Faster                 |
| Risk tolerance   | Low                  | Medium                 |
| Use case         | High-risk, ambiguous | Well-defined, low-risk |

## Quick Reference

```markdown
WHEN TO USE:
  ✓ Requires human approval
  ✓ High-risk operations
  ✓ Ambiguous requirements
  ✓ User wants visibility

INTERACTION:
  - Present options
  - Show previews
  - Request confirmations
  - Provide updates

CONFIRMATION LEVELS:
  Always:       Every action
  Major:        Significant operations only
  Destructive:  Irreversible actions only

COMMUNICATION:
  - Clear status updates
  - Explain decisions
  - Provide context
  - Ask specific questions
  - Visual progress indicators

ERROR HANDLING:
  - Explain clearly
  - Show details
  - Propose solutions
  - Ask for guidance
  - Don't proceed without resolution

BEST PRACTICES:
  - Set expectations
  - Regular updates
  - Clear questions
  - Visual feedback
  - Reasonable checkpoints
  - Explain reasoning
```
