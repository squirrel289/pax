# Decision Point Encoding

Formalized pattern for skills that pause execution, prompt users with discrete options, and resume based on user input.

## Related Documentation

- **Examples:** [examples/DECISION_POINTS.md](examples/DECISION_POINTS.md) - Canonical usage patterns for common scenarios
- **Schema:** [skills/aspects/interaction-modes/decisions.schema.yaml](../skills/aspects/interaction-modes/decisions.schema.yaml) - Validation rules
- **Aspect Specification:** [skills/aspects/interaction-modes/ASPECT.md](../skills/aspects/interaction-modes/ASPECT.md) - Implementation contract

## Overview

Decision points are branch points in skill execution where the appropriate action depends on user preference or context evaluation. Rather than embedding decision logic in individual skills, decision points are:

1. **Declared explicitly** in skill metadata
2. **Implemented consistently** via aspect pattern
3. **Compatible with multiple modes** (yolo, collaborative, custom)
4. **Resumable** from any decision point

## Problem This Solves

Currently decision logic is scattered:

```markdown
❌ handle-pr-feedback: Custom prompting logic (lines 197-236)
❌ merge-pr: Custom prompting logic (lines 130-193)
❌ create-pr: Custom prompting logic (lines 254-285)
```

**Result**: Each skill reinvents decision handling → inconsistent UX, maintenance overhead.

## Formalized Pattern

### 1. Declare Decision Points in Skill Metadata

```yaml
---
name: merge-pr
description: Safely merge PRs with verification
metadata:
  aspects:
    - interaction-modes
  decisions:
    - id: merge_readiness
      trigger: after-verification-phase
      yolo: [IF all-checks-pass THEN merge ELSE abort]
      collaborative:
        prompt: "Merge readiness status"
        options:
          - id: merge-squash
            label: "Merge with squash"
            action: execute-merge --squash
          - id: merge-rebase
            label: "Merge with rebase"
            action: execute-merge --rebase
          - id: create-draft
            label: "Create draft instead"
            action: mark-as-draft
          - id: custom
            label: "Other action..."
            allow_freeform: true
        resume: |
          Execute chosen action
          Inject decision result into workflow state
          Continue to next phase
---
```

### 2. Execution Flow

```ascii-tree
Decision Point Execution:
├─ YOLO Mode
│  ├─ Evaluate heuristics (IF all-checks-pass THEN merge)
│  ├─ Execute default action
│  └─ Report result, continue
│
├─ Collaborative Mode
│  ├─ Display prompt with options
│  ├─ Show current status/recommendation
│  ├─ Wait for user input (including custom response)
│  ├─ Validate custom input if provided
│  └─ Resume workflow with decision result
│
└─ Custom/Future Modes
   └─ Delegate to mode handler
```

### 3. Decision Result Injection

After user decides, inject result into workflow state:

```yaml
# Before decision point:
context:
  pr_number: 42
  checks_passed: true
  approvals_count: 2

# User chooses: "Merge with squash"

# After decision point:
context:
  pr_number: 42
  checks_passed: true
  approvals_count: 2
  decisions:
    - merge_readiness: merge-squash  # ← Available to subsequent phases
      custom_response: false         # ← Created via prompt, not custom
```

### 4. Multiple Decision Points

A single skill can have multiple decision points:

```yaml
decisions:
  - id: perform_verification
    trigger: start
    # Decide: skip verification or run full checks?
    
  - id: merge_readiness
    trigger: after-verification-phase
    # Decide: merge, draft, or abort?
    
  - id: cleanup_confirmation
    trigger: after-merge
    # Decide: delete branch or keep?
```

**Flow**:

```text
Start → Verification Decision → Verification Phase → 
  Merge Readiness Decision → Merge Action → 
  Cleanup Confirmation → Cleanup/Done
```

Each decision point pauses, prompts (in collaborative mode), and resumes.

## Implementation Template

### In Skill Metadata

```yaml
aspects:
  - interaction-modes  # Provides standardized prompting
decisions:
  - id: <decision_id>
    trigger: <phase_name>
    yolo: <heuristic_or_action>
    collaborative:
      prompt: <string>
      options:
        - id: <option_id>
          label: <user_visible>
          action: <action_reference>
        - custom: true  # Always include
      resume: <instructions>
```

### In Skill Execution

```bash
# Phase 1: Pre-Action
verify_preconditions()

# Decision Point 1: Should we proceed?
if [ "$INTERACTION_MODE" = "yolo" ]; then
  # Evaluate heuristic
  if [ "$all_checks_pass" = true ]; then
    DECISION_RESULT="proceed"
  else
    DECISION_RESULT="abort"
  fi
else
  # Collaborative: Show prompt, wait for input
  decision_point_prompt "merge_readiness" \
    "options: [merge-squash, merge-rebase, create-draft, custom]"
  DECISION_RESULT="$USER_DECISION"
fi

# Resume: Execute action based on DECISION_RESULT
case "$DECISION_RESULT" in
  merge-squash) merge_pr --squash ;;
  merge-rebase) merge_pr --rebase ;;
  create-draft) mark_as_draft ;;
  custom) execute_custom_action "$CUSTOM_INPUT" ;;
  abort) exit_skill "User aborted" ;;
esac
```

## Benefits for LLM Consistency

✅ **Explicit pattern**: LLMs see clear decision point structure vs scattered logic  
✅ **Reusable**: Same "prompt + options + custom" flow everywhere  
✅ **Testable**: Decision points can be tested in isolation  
✅ **Debuggable**: Clear where execution paused and why  
✅ **Extendable**: New modes just implement decision_point_prompt differently  

## When to Use Decision Points

Use decision points when:

- ✅ Skill has 2+ execution paths based on user choice
- ✅ Different modes (yolo vs collaborative) should behave differently
- ✅ Intermediate human input needed between phases
- ✅ Custom actions should be possible (not just predefined options)

Don't use for:

- ❌ Automatic routing based on data (use conditional skill composition instead)
- ❌ Questions with clear right answer (use skill logic instead)
- ❌ Rarely-used options (document in skill, don't force as decision point)

## Examples Using New Pattern

### Example 1: Merge PR with Decision Points

```yaml
---
name: merge-pr
aspects: [interaction-modes]
decisions:
  - id: merge_readiness
    trigger: after-verification
    yolo: [IF all-checks-pass THEN proceed ELSE abort]
    collaborative:
      prompt: "PR merge status\n\n[checklist of checks]"
      options:
        - label: "Merge with squash"
          action: merge --squash
        - label: "Merge with rebase"
          action: merge --rebase
        - label: "Create draft PR instead"
          action: mark-draft
        - custom: true
---
```

### Example 2: Handle PR Feedback with Decision Points

```yaml
---
name: handle-pr-feedback
aspects: [interaction-modes]
decisions:
  - id: feedback_severity
    trigger: after-triage
    yolo: [use-heuristics-for-severity]
    collaborative:
      prompt: "Comment severity classification"
      options:
        - label: "Trivial (auto-fix)"
          action: auto-fix
        - label: "Minor (discuss)"
          action: request-clarification
        - label: "Major (revert to in_progress)"
          action: revert-status
        - custom: true
---
```

## Related Patterns

- **[[ASPECTS.md]]**: Reusable behavior patterns (like interaction-modes)
- **[[SKILL_COMPOSITION.md]]**: How skills combine decision points with phases
- **[[SCRIPTING_BOUNDARY.md]]**: When to embed scripts vs compose skills
