# Quality Gates

Apply these gates on every isolated evaluator run.

## Pre-Evaluation Gates

- Input validates against `references/input-schema.json`.
- `criteria_confirmed=true` unless explicitly running a simulation.
- `criteria_confirmation_source` is present and valid when criteria are confirmed.
- Exactly one `target_alternative` is provided.
- No cross-option ranking context is required to complete evaluation.
- `evaluator_id` is present and unique in the parent workflow context.

## Scoring Gates

- Every criterion is evaluated for every required platform when evidence exists.
- Missing evidence is represented as `null`, never silently coerced to zero.
- Option-level `justification` is explicit and traceable to evidence.
- Feasibility, effort, and risk are preserved in the evaluated alternative.

## Output Gates

- Output validates against `references/output-schema.json`.
- `independent_evaluation.alternative_id` matches `evaluated_alternative.id`.
- `independent_evaluation.isolation_confirmed=true`.
- No ranking, winner, or final recommendation fields are emitted.
- Evidence refs and evidence gaps are explicit when data is incomplete.
