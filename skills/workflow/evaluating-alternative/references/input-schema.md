# Isolated Evaluator Input Schema

Use this contract when delegating single-option scoring to an isolated evaluator subagent.
Use `input-schema.json` in this directory as the machine-readable source of truth.

## Required Fields

| Field | Type | Notes |
| --- | --- | --- |
| `decision` | string | Decision statement the option is being evaluated for. |
| `criteria_confirmed` | boolean | Must be `true` unless running an explicit simulation. |
| `criteria_confirmation_source` | enum | Required when `criteria_confirmed=true`; one of `user-confirmed`, `provided-input`, `yolo-mode`. |
| `current_platform` | string | Platform to optimize around. |
| `criteria` | array | Full criterion contract with weights and scoring rules. |
| `target_alternative` | object | Exactly one alternative to evaluate. |
| `evaluator_id` | string | Unique identifier for this isolated evaluator run. |

## Optional Fields

| Field | Type | Default |
| --- | --- | --- |
| `major_platforms` | string[] | `["chatgpt","claude","gemini","copilot"]` |
| `score_scale` | string | `0-100` (`1-5` supported) |
| `known_evidence` | string[] | `[]` |
| `assumptions` | string[] | `[]` |

## Criterion Contract

Each criterion must include:

- `id`
- `name`
- `weight`
- `metric`
- `data_source`
- `scoring_rule`

## Target Alternative Contract

`target_alternative` must include:

- `id`
- `name`
- `effort` (`S|M|L`)
- `risk` (`Low|Med|Medium|High`)
- `feasible` (`true|false`)

Optional descriptive fields can be included as needed (for example `notes`, `constraints`, or `hypotheses`).

## Isolation Rules

- Input must contain only one target alternative.
- Do not pass other alternatives, rankings, or recommendation results.
- If such context is present, ignore it and mark an assumption or gap.
