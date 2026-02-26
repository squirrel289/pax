# Integration Guide: discovering-alternatives → comparative-decision-analysis

This guide shows how to transform `discovering-alternatives` JSON output into `comparative-decision-analysis` input format.

## Workflow Integration

**Step 1**: Run `discovering-alternatives` with JSON output:

```bash
@agent discover alternatives for [problem] using discovering-alternatives skill, output as JSON
```

**Step 2**: Transform JSON using the mapping below

**Step 3**: Feed transformed JSON to `comparative-decision-analysis`

## Field Mapping

### Direct Mappings

| discovering-alternatives   | comparative-decision-analysis | Notes                                        |
| -------------------------- | ----------------------------- | -------------------------------------------- |
| `decision`                 | `decision`                    | Direct copy                                  |
| `constraints.time_horizon` | Include in `decision` context | Append to decision statement                 |
| `options[].id`             | `alternatives[].id`           | Direct copy                                  |
| `options[].name`           | `alternatives[].name`         | Direct copy                                  |
| `options[].effort`         | `alternatives[].effort`       | Direct copy (S/M/L)                          |
| `options[].risk`           | `alternatives[].risk`         | Direct copy (Low/Med/High)                   |
| `options[].feasibility`    | `alternatives[].feasible`     | Map: "feasible" → true, "infeasible" → false |

### Derived Mappings

**`current_platform`**: Extract from `constraints.hard_constraints` or default to first constraint

**`criteria_confirmed`**: Set to `false` initially (criteria must be derived in comparative-decision-analysis Step 4)

**`criteria_confirmation_source`**: Set to `"pending"` until user confirms criteria

**`alternatives[].justification`**: Use `ranking[].rationale` for matching option_id

**`alternatives[].scores`**: Leave empty initially; populated during comparative-decision-analysis evaluation

**`independent_evaluations`**: Created during comparative-decision-analysis Step 6; use `options[].evidence_links` as `evidence_refs`

### Example Transformation

**Input (discovering-alternatives JSON)**:

```json
{
  "decision": "Implement templating linter for JSON and Markdown",
  "constraints": {
    "time_horizon": "8 weeks",
    "budget_sensitivity": "$0 preferred, max $5k/year",
    "hard_constraints": ["Python-based", "VS Code + LSP integration"]
  },
  "options": [
    {
      "id": "opt-001",
      "name": "Volar.js + External LSP",
      "category": "hybrid",
      "feasibility": "feasible",
      "effort": "M",
      "risk": "Low",
      "stack_fit": "High fit with existing VS Code integration",
      "evidence_links": [
        "https://github.com/volarjs/volar.js",
        "docs/adr/003-vscode-architecture.md"
      ],
      "confidence": "high"
    }
  ],
  "ranking": [
    {
      "rank": 1,
      "option_id": "opt-001",
      "rationale": "Proven pattern, low effort, zero cost, battle-tested",
      "implementation_path": [
        "Use Volar.js framework",
        "Create virtual document provider"
      ],
      "time_estimate": "4-6 weeks",
      "cost_estimate": "$0"
    }
  ]
}
```

**Output (comparative-decision-analysis input)**:

```json
{
  "decision": "Implement templating linter for JSON and Markdown (8 weeks, $0-$5k budget)",
  "criteria_confirmed": false,
  "criteria_confirmation_source": "pending",
  "current_platform": "Python-based",
  "criteria": [],
  "alternatives": [
    {
      "id": "opt-001",
      "name": "Volar.js + External LSP",
      "effort": "M",
      "risk": "Low",
      "feasible": true,
      "justification": "Proven pattern, low effort, zero cost, battle-tested",
      "scores": {}
    }
  ],
  "independent_evaluations": []
}
```

## Automated Transformation Script

Use this transformation logic when integrating:

```python
def transform_discovery_to_comparative(discovery_output):
    """Transform discovering-alternatives JSON to comparative-decision-analysis input."""

    # Build decision statement with context
    decision = discovery_output["decision"]
    if "constraints" in discovery_output:
        time_horizon = discovery_output["constraints"]["time_horizon"]
        budget = discovery_output["constraints"]["budget_sensitivity"]
        decision += f" ({time_horizon}, {budget} budget)"

    # Extract current platform from hard constraints
    hard_constraints = discovery_output.get("constraints", {}).get("hard_constraints", [])
    current_platform = hard_constraints[0] if hard_constraints else "unknown"

    # Map options to alternatives
    alternatives = []
    ranking_map = {r["option_id"]: r for r in discovery_output.get("ranking", [])}

    for option in discovery_output["options"]:
        ranking_info = ranking_map.get(option["id"], {})
        alternatives.append({
            "id": option["id"],
            "name": option["name"],
            "effort": option["effort"],
            "risk": option["risk"],
            "feasible": option["feasibility"] == "feasible",
            "justification": ranking_info.get("rationale", ""),
            "scores": {}
        })

    return {
        "decision": decision,
        "criteria_confirmed": False,
        "criteria_confirmation_source": "pending",
        "current_platform": current_platform,
        "criteria": [],
        "alternatives": alternatives,
        "independent_evaluations": []
    }
```

## Usage Example

```bash
# Step 1: Discover alternatives with JSON output
@agent discover alternatives for templating linter (build vs buy vs hybrid), output as JSON

# Step 2: Transform (automatically or manually using mapping above)
# discovering_output.json → comparative_input.json

# Step 3: Run comparative analysis with pre-populated alternatives
@agent analyze using comparative-decision-analysis with input from comparative_input.json
```

## Notes

- **Criteria derivation**: comparative-decision-analysis derives criteria in Step 4 using `references/rubric-packs.md`
- **Evidence preservation**: Use `options[].evidence_links` as `independent_evaluations[].evidence_refs` during evaluation
- **Gate status**: Use `coverage_gates.status` to check if discovery passed all gates before proceeding
- **User confirmation**: Verify `discovery_confirmation.user_approved == true` before transformation
