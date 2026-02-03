---
name: yolo
description: Autonomous "just do it" interaction mode - execute actions without confirmation or human intervention
category: interaction
license: MIT
---

# YOLO Interaction

Autonomous execution mode where the agent makes all decisions and takes all actions without seeking confirmation or clarification.

## When to Use

Use YOLO mode when:

- User explicitly requests autonomous operation ("just do it", "YOLO mode", "fully automated")
- User wants end-to-end automation without interruptions
- Workflow is well-defined and low-risk
- Time efficiency is critical
- User trusts the agent to make reasonable decisions

## When NOT to Use

Avoid YOLO mode for:

- Destructive operations (deleting data, dropping databases)
- Production deployments
- Security-sensitive changes
- Operations requiring approval
- Ambiguous requirements
- High-risk or irreversible actions

## Characteristics

### Decision Making

- Agent makes all decisions independently
- Uses best practices and reasonable defaults
- Resolves ambiguities using context and common patterns
- No pausing for clarification

### Error Handling

- Attempts automatic recovery
- Uses fallback strategies
- Logs errors but continues if possible
- Only stops for critical, unresolvable blockers

### Reporting

- Minimal interruptions
- Reports only when complete or blocked
- Provides summary of actions taken
- Documents decisions made

## Parameters

- **confidence-threshold** (default: 0.7): Minimum confidence to proceed without confirmation
- **max-retries** (default: 3): Maximum retry attempts for failed operations
- **fallback-strategy**: What to do when primary approach fails
- **blockers-only**: Only report critical blockers, not progress updates

## Behavioral Guidelines

### 1. Make Reasonable Assumptions

When faced with ambiguity:

- Use industry best practices
- Follow established patterns in codebase
- Choose safe, conservative defaults
- Document assumptions in code/commits

### 2. Proceed with Best Effort

- Attempt task completion even with incomplete information
- Use context clues and workspace analysis
- Implement most likely interpretation
- Handle edge cases gracefully

### 3. Minimize User Interaction

- No confirmation prompts
- No clarifying questions
- No progress check-ins (unless critical)
- Report only final results

### 4. Auto-Resolve Issues

When encountering problems:

- Try automatic fixes first
- Use retry logic for transient failures
- Apply known solutions to common issues
- Fall back to safe alternatives

### 5. Track Decisions

Document autonomous decisions:

- Log assumptions made
- Record alternatives considered
- Note confidence levels
- Explain trade-offs

## YOLO Workflows

### Pattern 1: End-to-End Automation

User request: "Process and merge all approved PRs"

YOLO execution:

1. List all open PRs
2. Filter for approved PRs
3. For each approved PR:
   - Check status checks
   - Resolve any resolvable threads
   - Merge if ready
   - Delete branch
4. Report summary

No confirmations, no check-ins, complete autonomy.

### Pattern 2: Fix All Issues

User request: "Fix all linting errors"

YOLO execution:

1. Run linter
2. Parse errors
3. Apply auto-fixes
4. Run linter again
5. Manually fix remaining issues
6. Commit changes
7. Report results

### Pattern 3: Multi-Step Pipeline

User request: "Deploy to staging"

YOLO execution:

1. Run tests
2. Build artifacts
3. Update version
4. Deploy to staging
5. Run smoke tests
6. Notify team
7. Report completion

## Decision Framework

When making autonomous decisions, prioritize:

1. **Safety**: Choose safe over risky
2. **Reversibility**: Prefer reversible actions
3. **Standards**: Follow established conventions
4. **Simplicity**: Choose simple over complex
5. **Documentation**: Document non-obvious choices

## Confidence Levels

Guide for proceeding without confirmation:

| Confidence       | Action                    | Example                                 |
|------------------|---------------------------|-----------------------------------------|
| High (>0.9)      | Proceed immediately       | Formatting code, running tests          |
| Medium (0.7-0.9) | Proceed with logging      | Merging approved PR, fixing lint errors |
| Low (0.5-0.7)    | Proceed with caution      | Refactoring, API changes                |
| Very Low (<0.5)  | **STOP** - report blocker | Unclear requirements, security changes  |

## Error Recovery Strategies

### Strategy 1: Retry with Backoff

For transient failures (network, rate limits):

- Retry 3 times with exponential backoff
- Log each attempt
- Proceed to fallback after max retries

### Strategy 2: Alternative Approach

For method failures:

- Try alternative tool/approach
- Use workaround if available
- Document deviation from primary plan

### Strategy 3: Partial Completion

For multi-step workflows:

- Complete what's possible
- Skip failed steps
- Report partial results and failures

### Strategy 4: Graceful Degradation

For feature failures:

- Implement core functionality
- Skip optional enhancements
- Note limitations in output

## Reporting Format

YOLO mode reports should be concise:

```markdown
TASK: Process approved PRs
STATUS: Complete

ACTIONS TAKEN:
- Processed 3 approved PRs
- Merged PR #42, #45, #47
- Deleted 3 feature branches
- Resolved 5 review threads

DECISIONS MADE:
- Used squash merge (most common in repo)
- Auto-resolved "LGTM" threads
- Deleted branches (no active work)

ISSUES:
- PR #44 has failing checks (skipped)
```

## Integration with Other Skills

YOLO mode can orchestrate:

- **parallel-execution**: Launch multiple autonomous tasks
- **sequential-execution**: Execute multi-stage pipelines
- **pull-request-tool**: Autonomous PR processing
- **merge-pr**: Auto-merge ready PRs
- **resolve-pr-comments**: Auto-resolve threads

## Best Practices

1. **Set clear scope**: Understand full extent of automation
2. **Use safe defaults**: Conservative choices when uncertain
3. **Log everything**: Comprehensive action logging
4. **Validate inputs**: Ensure prerequisites met before starting
5. **Plan rollback**: Know how to undo if needed
6. **Test first**: Validate approach on small scale if possible
7. **Document decisions**: Explain non-obvious choices
8. **Report concisely**: Summary at end, not play-by-play

## Safety Guardrails

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

## Quick Reference

```markdown
WHEN TO USE:
  ✓ User requests autonomous operation
  ✓ Well-defined workflow
  ✓ Low-risk actions
  ✓ Efficiency critical

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

SAFETY:
  - Validate before commit
  - Test before merge
  - Never delete production data
  - Never skip required approvals
```
