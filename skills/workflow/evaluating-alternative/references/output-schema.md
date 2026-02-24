# Isolated Evaluator Output Schema

This output is designed to plug directly into comparative scoring workflows.
Use `output-schema.json` in this directory as the machine-readable source of truth.

## Required Top-Level Fields

| Field | Type | Notes |
| --- | --- | --- |
| `evaluated_alternative` | object | Single alternative with completed scores and justification. |
| `independent_evaluation` | object | Isolated evaluator record compatible with comparative workflows. |

## Optional Top-Level Fields

| Field | Type | Notes |
| --- | --- | --- |
| `quality_notes` | object | Evidence gaps, assumptions, and follow-up actions. |

## `evaluated_alternative` Contract

Must include:

- `id`
- `name`
- `effort` (`S|M|L`)
- `risk` (`Low|Med|Medium|High`)
- `feasible` (`true|false`)
- `scores` (platform -> criterion -> numeric score or `null`)
- `justification` (single-option rationale only)

## `independent_evaluation` Contract

Must include:

- `alternative_id` (must match `evaluated_alternative.id`)
- `evaluator_id` (must match evaluator input)
- `isolation_confirmed` (must be `true`)
- `summary` (isolated findings summary)
- `evidence_refs` (optional array of evidence pointers)

## Consistency Rules

- Do not include ranking, winner selection, or recommendation fields.
- Keep all rationale tied to this single alternative.
- Use `null` for missing evidence-driven scores.
