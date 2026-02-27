# Evidence Validation Rubric

Use this rubric for every unchecked checkbox before changing `[ ]` to `[x]`.

## Validation Gates

A checkbox is eligible for `[x]` only if all gates pass.

1. Claim clarity

- Convert checkbox text into a single concrete claim.
- If claim is ambiguous, keep `[ ]` and record an inline next step to clarify wording.

1. Implementation evidence

- Identify concrete implementation location(s): source file path and key symbol/function.
- Confirm behavior is present now (not planned, stubbed, or commented out).

1. Verification evidence

- Identify test coverage or equivalent objective check tied to the claim.
- Prefer automated test evidence. If only manual verification is possible, record exact steps and output artifact.

1. Consistency check

- Ensure checkbox wording matches real behavior and scope.
- If implementation is partial, keep `[ ]`.

## Decision Matrix

- Mark `[x]`:
  - Implementation exists.
  - Verification evidence exists and passes.
  - Scope matches checkbox text.

- Keep `[ ]`:
  - Missing implementation.
  - Missing or failing verification.
  - Ambiguous or overstated checkbox wording.

## Evidence Note Pattern

Use concise, concrete references during review:

- Code: `<path>:<line or symbol>`
- Tests: `<path>:<test name>`
- Command: `<exact command>`
- Result: `pass` / `fail` with key output summary

## Summary Status Reporting Requirements

For each audited work item, report section-level counts only:

1. Tasks

- checked this turn / total checked
- total unchecked / total checkboxes

1. Acceptance Criteria

- checked this turn / total checked
- total unchecked / total checkboxes

1. WARNINGS (if any):

- Ambiguous checkbox text
- Missing implementation evidence
- Missing or failing test evidence

1. Recommended Next Steps

- Generate next steps dynamically from observed findings and status context, using this deterministic synthesis order:
  1. Ambiguous checkbox warnings.
  2. Missing implementation evidence warnings.
  3. Missing or failing test evidence warnings.
  4. Remaining unchecked items with terminal status (`closed`/`completed`) requiring status reactivation.
  5. Remaining unchecked items requiring execution of outstanding scope.
  6. Fully validated `closed` items ready for finalization.
  7. If no warnings and no unchecked items, emit exactly one bullet: `No further action required.`
- Do not constrain recommendations to a fixed domain; choose actions that best resolve observed evidence gaps.
- Keep recommendations concise, actionable, and ordered by the synthesis sequence.
- De-duplicate semantically equivalent actions.

Do not emit per-checkbox unresolved remediation details in the report output.
