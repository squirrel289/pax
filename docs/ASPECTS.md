# Skills as Aspects

Aspects are reusable behavior patterns that can be composed with any skill.

## Related Documentation

- **Examples:** [examples/DECISION_POINTS.md](examples/DECISION_POINTS.md) - Canonical decision point patterns
- **Decision Encoding:** [DECISION_POINT_ENCODING.md](DECISION_POINT_ENCODING.md) - Full pattern specification
- **Aspect Specification:** [skills/aspects/interaction-modes/ASPECT.md](../skills/aspects/interaction-modes/ASPECT.md) - Implementation contract

## Overview

An **aspect** is a cross-cutting concern that modifies skill behavior without changing core skill logic.

```text
Skill = Core Logic + Aspects

Example:
merge-pr = [Verify PR Status + Merge/Cleanup] + [interaction-modes aspect]
           └─ Core skill logic ────────────────  └─ Standardized behavior
```

## Why Aspects?

**Problem**: Interaction modes fragmented across skills causing inconsistency and repetition.

**Solution**: Factor out as reusable aspect

```ascii-tree
✅ aspects/interaction-modes/ (single source of truth)
   └─ Applied to any skill that declares: aspects: [interaction-modes]
```

## Aspect Structure

```ascii-tree
aspects/
└── interaction-modes/
    ├── ASPECT.md              (specification)
    ├── aspect.schema.yaml     (validation schema)
    ├── yolo.sh                (implementation: autonomous mode)
    ├── collaborative.sh       (implementation: interactive mode)
    └── examples/
        ├── merge-pr-example.md
        └── handle-feedback-example.md
```

## How Aspects Work

### 1. Skill Declares Aspect Usage

```yaml
---
name: merge-pr
metadata:
  aspects:
    - interaction-modes      # Skill uses this aspect
  decisions:
    - id: merge_readiness
      trigger: after-verification
      # Aspect handles the prompting automatically
---
```

### 2. Aspect Modifies Skill Behavior

**YOLO Mode** (aspect implementation):

```bash
# aspect/interaction-modes/yolo.sh
evaluation_mode() {
  # Skip prompts, use heuristics
  case "$DECISION_POINT" in
    merge_readiness) 
      if [ "$all_checks_pass" = true ]; then
        echo "proceed"
      else
        echo "abort"
      fi
      ;;
  esac
}
```

**Collaborative Mode** (aspect implementation):

```bash
# aspects/interaction-modes/collaborative.sh
interactive_mode() {
  # Show prompts, wait for user input
  case "$DECISION_POINT" in
    merge_readiness)
      show_pr_status
      echo "Ready to merge using?"
      select option in "Merge (squash)" "Merge (rebase)" "Create draft" "Custom"; do
        case $option in
          "Merge (squash)") echo "merge-squash"; break ;;
          "Merge (rebase)") echo "merge-rebase"; break ;;
          "Create draft") echo "create-draft"; break ;;
          "Custom") read -p "Enter action: " custom; echo "$custom"; break ;;
        esac
      done
      ;;
  esac
}
```

### 3. Skill Execution Orchestrates

```bash
# merge-pr/merge-pr.sh

source "aspects/interaction-modes/${INTERACTION_MODE}.sh"

# Phase 1: Verify
verify_merge_readiness

# Phase 2: Decision Point (using aspect)
DECISION_RESULT=$(evaluation_mode)  # or interactive_mode, depending on aspect/mode

# Phase 3: Execute Based on Result
case "$DECISION_RESULT" in
  merge-squash) git merge --squash ;;
  merge-rebase) git merge --rebase ;;
  create-draft) gh pr ready --draft ;;
  custom) execute "$DECISION_RESULT" ;;
esac
```

## Built-In Aspects

### interaction-modes

Controls how skills handle user prompts and decisions.

**Modes**:

- `yolo`: Autonomous (use heuristics, no prompts)
- `collaborative`: Interactive (show options, ask for confirmation)
- Your custom modes: Can be added per-org

**Aspect declares**:

```yaml
name: interaction-modes
modes:
  - yolo
  - collaborative
  - custom  # Orgs can add more
implementations:
  yolo: "yolo.sh"
  collaborative: "collaborative.sh"
compatible_with:
  - decision_points: all
```

## Creating New Aspects

### Step 1: Define Aspect

```yaml
# aspects/my-aspect/ASPECT.md
name: my-aspect
description: "..."
parameters:
  - name: retries
    type: integer
    default: 3
implementations:
  - immediate_fail
  - fault_tolerant
```

### Step 2: Implement Behavior

```bash
# aspects/retry/immediate_fail.sh
my_aspect_immediate_fail() {
  # Fail immediately
}

# aspects/my-aspect/fault_tolerant.sh
my_aspect_fault_tolerant() {
  # Retry ${retries} times 
}
```

### Step 3: Document Usage

```markdown
# aspects/my-aspect/examples/my-skill-example.md
When merge-pr uses my-aspect...
```

### Step 4: Declare in Skill

```yaml
---
name: my-skill
aspects:
  - my-aspect
---
```

## Benefits for LLM Consistency

✅ **Reusable patterns**: LLM sees "interaction-modes aspect" used consistently  
✅ **Reduced code**: Core skill logic focused, no decision boilerplate  
✅ **Testable aspects**: Each aspect can be tested independently  
✅ **Composable**: Any skill can use any aspect  
✅ **Evolvable**: New modes added to aspect → automatically available to all skills  

## Related Patterns

- **[[DECISION_POINT_ENCODING]]**: How to declare decision points
- **[[SCRIPTING_BOUNDARY]]**: When to embed scripts vs use aspects
- **[[SKILL_COMPOSITION]]**: How skills combine aspects and logic
