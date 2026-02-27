---
name: evaluating-alternative
description: "Evaluate one alternative against confirmed criteria in strict isolation and emit a schema-compatible independent evaluator record. Use for delegated per-option subagent scoring in comparative decision workflows."
metadata:
  category: workflow
  audience: agents, scripts, CI
  derived-from: comparative-decision-analysis
---

# Isolated Evaluator

Single-option evaluator skill for delegated subagent runs. It evaluates exactly one target alternative and returns structured output that a parent workflow can merge into comparative scoring input.

## When to Use

- A parent workflow needs one evaluator per alternative.
- You need strict evaluator isolation for auditability.
- You need a deterministic handoff artifact for later harness scoring.

## Inputs

Use `references/input-schema.md` and `references/input-schema.json` as the source of truth.

Required:

- `decision`
- `criteria_confirmed`
- `criteria_confirmation_source` (when criteria are confirmed)
- `current_platform`
- `criteria`
- `target_alternative`
- `evaluator_id`

Optional:

- `major_platforms`
- `score_scale`
- `known_evidence`
- `assumptions`

## Workflow

1. Validate input and isolation boundaries.
   - Confirm exactly one `target_alternative`.
   - Reject or ignore peer alternatives, rankings, and recommendation hints.
2. Evaluate criterion-by-criterion and platform-by-platform.
   - Score with the declared scale.
   - Use `null` for missing evidence, never zero-fill.
   - Track evidence references for each meaningful claim.
3. Write isolated rationale.
   - Produce option-level `justification`.
   - Produce evaluator `summary` focused on the single target.
4. Emit output using `references/output-schema.md` and `references/output-schema.json`.
   - Include `evaluated_alternative` (scores + justification).
   - Include `independent_evaluation` with `isolation_confirmed=true`.
5. Report evidence gaps and assumptions for parent-level aggregation.

## Output Contract

`evaluated_alternative` must preserve the comparative workflow alternative shape:

- `id`
- `name`
- `effort`
- `risk`
- `feasible`
- `scores`
- `justification`

`independent_evaluation` must preserve the comparative workflow evaluator-record shape:

- `alternative_id`
- `evaluator_id`
- `isolation_confirmed`
- `summary`
- `evidence_refs`

## Guardrails

- No cross-option comparison language.
- No ranking or final recommendation output.
- All missing evidence stays explicit (`null` scores + gap notes).
- Every score and summary claim should be traceable to evidence.
- Apply a brief agentic-eval reflection on the evaluator summary (max 2 iterations) to verify evidence coverage.
- Keep critique output structured (JSON) and do not emit separate analysis files.

Apply `references/quality-gates.md` for pass/fail checks.

## Optional Validation

```bash
python3 -m jsonschema -i <isolated-eval-input.json> skills/workflow/isolated-evaluator/references/input-schema.json
python3 -m jsonschema -i <isolated-eval-output.json> skills/workflow/isolated-evaluator/references/output-schema.json
```

## References

- Input contract: `references/input-schema.md`
- Input schema: `references/input-schema.json`
- Output contract: `references/output-schema.md`
- Output schema: `references/output-schema.json`
- Quality gates: `references/quality-gates.md`
- Output template: `assets/isolated-evaluation-template.v1.json`
