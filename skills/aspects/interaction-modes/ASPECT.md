# Interaction Modes Aspect

Reusable interaction behavior that can be composed into any skill.

## Purpose

Standardize how skills pause, prompt for choices, and resume execution based on user input.

## Supported Modes

- **yolo**: Autonomous execution, minimal prompts
- **collaborative**: Interactive execution, prompts for decisions

## Documentation

- **Examples:** [DECISION_POINTS.md](../../../docs/examples/DECISION_POINTS.md) - Canonical usage patterns
- **Schema:** [decisions.schema.yaml](decisions.schema.yaml) - Validation rules
- **Encoding Pattern:** [DECISION_POINT_ENCODING.md](../../../docs/DECISION_POINT_ENCODING.md) - Full specification

## Decision Point Contract

Any skill using this aspect must declare decision points in skill metadata:

```yaml
metadata:
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
          - id: custom
            label: "Other action..."
            allow_freeform: true
        resume: <instructions>
```

## Behavior

### YOLO Mode

- Evaluate decision heuristics
- Execute default action
- Continue without prompting

### Collaborative Mode

- Show prompt + discrete options
- Always include a custom response option
- Validate user input
- Resume workflow with decision result

## Files

- [skills/aspects/interaction-modes/yolo.sh](skills/aspects/interaction-modes/yolo.sh)
- [skills/aspects/interaction-modes/collaborative.sh](skills/aspects/interaction-modes/collaborative.sh)

## Related Docs

- [docs/DECISION_POINT_ENCODING.md](docs/DECISION_POINT_ENCODING.md)
- [docs/ASPECTS.md](docs/ASPECTS.md)

## Interaction Skills

The interaction skills (yolo, collaborative) remain as narrative guidance and usage patterns. The interaction-modes aspect provides the execution contract and shared prompting behavior.
