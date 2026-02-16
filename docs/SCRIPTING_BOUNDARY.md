# Scripting vs Skill Composition

Guidance for when to implement deterministic logic as a script vs composing skills.

## Core Principle

**Favor scripts when deterministic behavior is desired and practical. Otherwise, use skills.**

## Decision Matrix

| Criterion | Script It | Compose Skills |
| --------- | --------- | -------------- |
| Deterministic sequence required | ✅ | ❌ |
| Needs transaction/rollback | ✅ | ❌ |
| Pure CLI operations | ✅ | ❌ |
| Simple inputs, no branching | ✅ | ❌ |
| Requires human input/decision | ❌ | ✅ |
| Requires orchestration across skills | ❌ | ✅ |
| Requires access to structured state | ❌ | ✅ |
| Needs dynamic prompting or modes | ❌ | ✅ |
| Long-running workflow (multi-step) | ❌ | ✅ |

## Practical Boundary

### Use scripts for

- `feature-branch-management` operations
- CLI command sequences (git, gh, fs operations)
- Deterministic transformations
- Preflight validations (fast exit if fails)
- Cleanup actions with guaranteed rollback

### Use skill composition for

- Multi-skill orchestration (create-pr + merge-pr + handle-feedback)
- Decision points requiring user interaction
- Conditional flows based on external API state
- Recursive or looping workflows
- Integration with interaction-modes aspect

## Example: Feature Branch Management

**Scripted**:

```bash
# create-branch.sh
set -e
branch="feature/${id}-${slug}"

if git show-ref --quiet refs/heads/$branch; then
  git switch $branch
else
  git checkout -b $branch
fi
```

**Why script?**

- Fully deterministic
- No external dependencies
- Must behave identically every run
- No user input needed

## Example: Merge PR Workflow

**Composed**:

`merge-pr = verify + decision points + merge + cleanup`

**Why compose?**

- Decisions based on CI, approvals, mergeable state
- Different behavior for yolo vs collaborative
- Requires interaction-modes aspect

## Rule of Thumb

If **it could be unit-tested without any external dependencies**, prefer scripting.
If **it requires API calls, prompts, or branching logic**, prefer skill composition.

## Related Documentation

- **[[DECISION_POINT_ENCODING.md]]**
- **[[ASPECTS.md]]**
- **[[SKILL_COMPOSITION.md]]**
