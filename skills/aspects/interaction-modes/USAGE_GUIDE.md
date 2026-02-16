# Interaction Modes Usage Guide

This guide explains when and how to use the interaction-modes aspect effectively in your skills.

## Overview

The interaction-modes aspect provides two execution modes:

- **YOLO**: Autonomous execution without confirmations
- **Collaborative**: Interactive execution with human-in-the-loop

## Related Documentation

- **Aspect Specification:** [ASPECT.md](ASPECT.md) - Implementation contract
- **Schema:** [decisions.schema.yaml](decisions.schema.yaml) - Validation rules
- **Examples:** [DECISION_POINTS.md](../../../docs/examples/DECISION_POINTS.md) - Canonical usage patterns
- **Decision Encoding:** [DECISION_POINT_ENCODING.md](../../../docs/DECISION_POINT_ENCODING.md) - Full pattern specification

---

## YOLO Mode

Autonomous execution mode where the agent makes all decisions and takes all actions without seeking confirmation or clarification.

### When to Use

Use YOLO mode when:

- User explicitly requests autonomous operation ("just do it", "YOLO mode", "fully automated")
- User wants end-to-end automation without interruptions
- Workflow is well-defined and low-risk
- Time efficiency is critical
- User trusts the agent to make reasonable decisions

### When NOT to Use

Avoid YOLO mode for:

- Destructive operations (deleting data, dropping databases)
- Production deployments
- Security-sensitive changes
- Operations requiring approval
- Ambiguous requirements
- High-risk or irreversible actions

### Characteristics

**Decision Making:**

- Agent makes all decisions independently
- Uses best practices and reasonable defaults
- Resolves ambiguities using context and common patterns
- No pausing for clarification

**Error Handling:**

- Attempts automatic recovery
- Uses fallback strategies
- Logs errors but continues if possible
- Only stops for critical, unresolvable blockers

**Reporting:**

- Minimal interruptions
- Reports only when complete or blocked
- Provides summary of actions taken
- Documents decisions made

### Parameters

**Note:** These parameters guide behavior when implementing YOLO mode in skills. They are not directly consumed by the interaction-modes aspect scripts.

- **confidence-threshold** (default: 0.7): Minimum confidence to proceed without confirmation
- **max-retries** (default: 3): Maximum retry attempts for failed operations
- **fallback-strategy**: What to do when primary approach fails
- **blockers-only**: Only report critical blockers, not progress updates

### Behavioral Guidelines

#### 1. Make Reasonable Assumptions

When faced with ambiguity:

- Use industry best practices
- Follow established patterns in codebase
- Choose safe, conservative defaults
- Document assumptions in code/commits

#### 2. Proceed with Best Effort

- Attempt task completion even with incomplete information
- Use context clues and workspace analysis
- Implement most likely interpretation
- Handle edge cases gracefully

#### 3. Minimize User Interaction

- No confirmation prompts
- No clarifying questions
- No progress check-ins (unless critical)
- Report only final results

#### 4. Auto-Resolve Issues

When encountering problems:

- Try automatic fixes first
- Use retry logic for transient failures
- Apply known solutions to common issues
- Fall back to safe alternatives

#### 5. Track Decisions

Document autonomous decisions:

- Log assumptions made
- Record alternatives considered
- Note confidence levels
- Explain trade-offs

### Safety Guardrails

Even in YOLO mode, always:

- ✅ Validate syntax before committing
- ✅ Run tests before merging
- ✅ Check for merge conflicts
- ✅ Verify permissions before operations
- ✅ Back up before destructive changes
- ❌ Never delete production data
- ❌ Never disable security features
- ❌ Never skip required approvals
- ❌ Never ignore critical errors

### Integration with Other Skills

YOLO mode can orchestrate:

- **parallel-execution**: Launch multiple autonomous tasks
- **sequential-execution**: Execute multi-stage pipelines
- **pull-request-tool**: Autonomous PR processing
- **merge-pr**: Auto-merge ready PRs
- **resolve-pr-comments**: Auto-resolve threads

---

## Collaborative Mode

Interactive mode where the agent collaborates with humans, seeking confirmation, providing feedback, and enabling manual verification before critical actions.

### When to Use

Use collaborative mode when:

- Actions require human approval
- Decisions involve subjective judgment
- User wants visibility into process
- Risk level is high
- Requirements are ambiguous
- Learning/training scenario
- Regulatory compliance requires human oversight

### When NOT to Use

Avoid collaborative mode for:

- Fully automated workflows (use YOLO instead)
- User explicitly requests autonomous operation
- Trivial, low-risk operations
- Time-critical operations where delays unacceptable

### Characteristics

**Decision Making:**

- Present options to user
- Explain trade-offs
- Seek approval for major decisions
- Incorporate user feedback

**Progress Updates:**

- Regular status updates
- Visual feedback on progress
- Clear communication of current state
- Proactive error reporting

**Verification Points:**

- Pause before destructive operations
- Show changes before committing
- Request approval before merging
- Confirm configuration changes

### Parameters

**Note:** These parameters guide behavior when implementing Collaborative mode in skills. They are not directly consumed by the interaction-modes aspect scripts.

- **confirmation-level**: always, major-only, destructive-only
- **update-frequency**: How often to provide progress updates
- **show-previews**: Display previews of changes before applying
- **approval-required**: List of operations requiring explicit approval

### Interaction Patterns

#### Pattern 1: Present Options

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

#### Pattern 2: Show Preview

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

#### Pattern 3: Incremental Progress

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

#### Pattern 4: Risk Assessment

Before risky operations:

```markdown
⚠️ WARNING: This operation will:
- Delete 15 files
- Modify 8 database tables
- Require service restart

This action cannot be easily undone.

Are you sure you want to proceed? (yes/no)
```

### Communication Guidelines

#### Clear Status Updates

Good: "✅ Completed 3/5 tasks. Currently analyzing test coverage..."  
Bad: "Working..."

#### Explain Decisions

Good: "I chose squash merge because it's used in 90% of this repo's PRs"  
Bad: "Merging now"

#### Provide Context

Good: "This change affects authentication. It will require re-testing login flows."  
Bad: "Changed auth.ts"

#### Ask Specific Questions

Good: "Should I use async/await or Promises for this async operation?"  
Bad: "How should I implement this?"

#### Show Progress Visually

Use todo lists, checkmarks, progress indicators:

```markdown
Progress:
✅ Fetch PR details
✅ Run tests  
⏳ Address review comments (2/5)
⬜ Merge PR
⬜ Delete branch
```

### Integration with Other Skills

Collaborative mode can orchestrate:

- **sequential-execution**: Step through workflow with approvals
- **pull-request-tool**: Review PRs together with user
- **merge-pr**: Confirm merge readiness before executing
- **resolve-pr-comments**: Review and approve comment resolutions

---

## Mode Comparison

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

---

## Quick Reference

### YOLO Mode

```markdown
WHEN TO USE:
  ✓ User requests autonomous operation
  ✓ Well-defined workflow
  ✓ Low-risk actions
  ✓ Efficiency critical

WHEN NOT TO USE:
  ✗ Destructive operations
  ✗ Production deployments
  ✗ Security-sensitive changes
  ✗ High-risk or irreversible actions

CHARACTERISTICS:
  - No confirmations
  - No clarifying questions
  - Auto-resolve issues
  - Report only results

DECISION MAKING:
  - Use best practices
  - Safe defaults
  - Document assumptions
  - Log decisions

ERROR HANDLING:
  - Retry transient failures
  - Use fallback strategies
  - Partial completion OK
  - Stop only for critical blockers
```

### Collaborative Mode

```markdown
WHEN TO USE:
  ✓ Requires human approval
  ✓ High-risk operations
  ✓ Ambiguous requirements
  ✓ User wants visibility

WHEN NOT TO USE:
  ✗ Fully automated workflows
  ✗ User requests autonomous operation
  ✗ Trivial, low-risk operations
  ✗ Time-critical operations

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
```
