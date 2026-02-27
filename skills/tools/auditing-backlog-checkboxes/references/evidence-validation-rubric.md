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

## Inline Report Requirements for Remaining `[ ]`

For each unresolved checkbox, provide:

1. Missing evidence

- Specific gap: missing file, missing behavior, missing test, or failing command.

1. Next action

- Concrete development or validation step.

1. Verification command

- Exact command to run when action completes.

1. Completion signal

- Observable result needed to allow `[x]`.

## Example Unresolved Report Item

```markdown
1. [ ] Add integration test for parser error recovery
   - Missing evidence: no failing/passing integration test asserting recovery behavior.
   - Next action: add `test/parser/error-recovery.integration.test.ts` covering malformed nested input.
   - Verification command: `pnpm vitest run test/parser/error-recovery.integration.test.ts`
   - Completion signal: test passes and references the production recovery path.
```
