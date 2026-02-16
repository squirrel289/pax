# Decision Point Examples

This document provides canonical examples of decision points used with the interaction-modes aspect.

See [DECISION_POINT_ENCODING.md](../DECISION_POINT_ENCODING.md) for the full pattern specification.

---

## Example 1: Merge Readiness Decision

**Context:** Used in merge-pr workflow to determine merge strategy after verification.

**Skill:** [merge-pr](../../skills/workflow/merge-pr/SKILL.md)

**Decision Point:**

```yaml
metadata:
  decisions:
    - id: merge_readiness
      trigger: after-verification
      yolo: "[proceed_if_checks_pass]"
      collaborative:
        prompt: "PR #123 is ready to merge. How would you like to proceed?"
        options:
          - id: merge_squash
            label: "Merge with squash"
            action: "merge --squash"
          - id: merge_rebase
            label: "Merge with rebase"
            action: "merge --rebase"
          - id: create_draft
            label: "Convert to draft for more work"
            action: "mark_as_draft"
          - id: custom
            label: "Other action..."
            allow_freeform: true
        resume: "Proceed with selected merge strategy"
```

**Usage:**

- **YOLO mode:** Automatically merges if CI passes, tests pass, and no review blocks exist
- **Collaborative mode:** Prompts user to choose between squash, rebase, mark as draft, or custom action

---

## Example 2: PR Creation Confirmation

**Context:** Used in create-pr workflow to review PR details before submission.

**Skill:** [create-pr](../../skills/workflow/create-pr/SKILL.md)

**Decision Point:**

```yaml
metadata:
  decisions:
    - id: confirm_pr_details
      trigger: before-pr-create
      yolo: "[create_pr]"
      collaborative:
        prompt: "Review PR details before creating"
        options:
          - id: create_pr
            label: "Create PR as shown"
            action: "submit"
          - id: edit_title
            label: "Edit title"
            action: "edit --field=title"
          - id: edit_description
            label: "Edit description"
            action: "edit --field=description"
          - id: custom
            label: "Other changes..."
            allow_freeform: true
        resume: "Create PR with confirmed or edited details"
```

**Usage:**

- **YOLO mode:** Automatically creates PR using generated title/description
- **Collaborative mode:** Shows preview of title, description, metadata; offers edit options or custom action

---

## Example 3: Feedback Severity Triage

**Context:** Used in handle-pr-feedback workflow to determine severity and appropriate response.

**Skill:** [handle-pr-feedback](../../skills/workflow/handle-pr-feedback/SKILL.md)

**Decision Point:**

```yaml
metadata:
  decisions:
    - id: feedback_severity
      trigger: after-triage
      yolo: "[use_triage]"
      collaborative:
        prompt: "What severity level should be applied to this feedback?"
        options:
          - id: trivial
            label: "Trivial (typos, formatting)"
            action: "auto-fix"
          - id: minor
            label: "Minor (small improvements)"
            action: "auto-fix"
          - id: moderate
            label: "Moderate (requires review)"
            action: "resolve-comments"
          - id: major
            label: "Major (significant changes)"
            action: "update-work-item --mode=revise"
          - id: blocker
            label: "Blocker (revert required)"
            action: "revert-work-item"
          - id: custom
            label: "Custom response..."
            allow_freeform: true
        resume: "Execute action based on severity level"
```

**Usage:**

- **YOLO mode:** Uses AI triage result to automatically classify and route feedback
- **Collaborative mode:** Shows triage result and asks user to confirm or override severity

---

## Example 4: Multi-Decision Point Example

**Context:** Example showing a skill with multiple decision points in sequence.

**Skill:** Hypothetical deployment workflow

**Decision Points:**

```yaml
metadata:
  decisions:
    - id: environment_selection
      trigger: before-deploy
      yolo: "[use_staging]"
      collaborative:
        prompt: "Select deployment environment"
        options:
          - id: staging
            label: "Deploy to staging"
            action: "deploy --env=staging"
          - id: production
            label: "Deploy to production"
            action: "deploy --env=production"
          - id: custom
            label: "Custom environment..."
            allow_freeform: true
        resume: "Proceed with deployment to selected environment"
    
    - id: rollback_strategy
      trigger: after-healthcheck-fail
      yolo: "[auto_rollback]"
      collaborative:
        prompt: "Health check failed. How should we proceed?"
        options:
          - id: rollback
            label: "Rollback immediately"
            action: "rollback --previous"
          - id: investigate
            label: "Keep current, investigate"
            action: "no-op"
          - id: force_healthy
            label: "Mark healthy (override)"
            action: "override-healthcheck"
          - id: custom
            label: "Custom action..."
            allow_freeform: true
        resume: "Execute selected recovery action"
```

**Usage:**

- Shows how multiple decision points can be sequenced in a single workflow
- Each decision is independent and can be handled by YOLO or Collaborative modes
- Decision results are injected back into the skill via environment variables

---

## Schema Validation

Decision points must conform to the schema defined in:
[decisions.schema.yaml](../../skills/aspects/interaction-modes/decisions.schema.yaml)

**Key validation rules:**

- `id` is required and must use snake_case
- `trigger` is required (describes when decision occurs)
- `yolo` must be array or string (heuristic or default action)
- `collaborative.prompt` and `collaborative.options` are required for interactive mode
- Each option must have `id`, `label`, and `action`
- Option IDs must be unique within a decision point

---

## Best Practices

### 1. Decision Point Naming

- Use descriptive IDs that indicate what is being decided: `merge_readiness`, `confirm_pr_details`, `feedback_severity`
- Avoid generic names like `decision_1`, `user_choice`, `next_step`

### 2. YOLO Defaults

- Provide safe, conservative defaults when possible
- Use heuristics that match what an experienced user would typically do
- Document the heuristic logic in the skill's main body

### 3. Collaborative Options

- Order options from most likely to least likely
- Always include a `custom` option with `allow_freeform: true` for flexibility
- Keep labels concise but descriptive (3-6 words)
- Use action strings that map cleanly to skill sub-operations

### 4. Trigger Timing

- Use clear lifecycle phase names: `before-X`, `after-Y`, `on-error`
- Ensure trigger names are self-documenting
- Prefer explicit over implicit triggers

### 5. Resume Instructions

- Provide clear guidance on how workflow continues after decision
- Reference specific skill operations or sub-skills to invoke
- Keep resume instructions concise (1 sentence)

---

## Related Documentation

- [DECISION_POINT_ENCODING.md](../DECISION_POINT_ENCODING.md) - Full pattern specification
- [ASPECTS.md](../ASPECTS.md) - Overview of aspect system
- [interaction-modes/ASPECT.md](../../skills/aspects/interaction-modes/ASPECT.md) - Aspect specification
- [decisions.schema.yaml](../../skills/aspects/interaction-modes/decisions.schema.yaml) - Validation schema
