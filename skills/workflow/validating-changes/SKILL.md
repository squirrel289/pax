---
name: validating-changes
description: "Validate code changes before PR update and merge. Use when preparing to update a PR, pushing changes, or running pre-merge checks: (1) run local CI parity tests, (2) add regression tests for new failures, (3) verify all tests pass before pushing or requesting review."
metadata:
  type: document
  subtype: skill
---

# Validating Changes

Ensure code quality and prevent regressions by validating changes locally before PR updates and merges.

## When to Use

- Before updating a feature branch with new commits
- After resolving merge conflicts to re-validate tests
- Before pushing to origin (pre-push gate)
- When CI tests fail and need local replication and fix

## Core Validation Steps

### 1. Run Affected Tests Locally

Before updating a PR or pushing:

1. Run: `pnpm test:affected:ci`
2. Review output for failures
3. **Pass if**: All tests pass
4. **Fail if**: Any test fails — do not skip or commit

If failures occur, proceed to step 2 (add regression test).

### 2. Add Regression Test

When a new failure is discovered:

1. Locate the test file for the failing module (e.g., `src/packages/volar/src/position-mapping.test.ts`)
2. Add a test case that reproduces the failure with clear scenario name (e.g., "maps positions within template blocks")
3. Include comments explaining why this edge case matters
4. Run the test suite for that file only: `pnpm -C <package> test -- <test-file>`
5. Verify new test fails before your fix, then passes after

**Example**:

```typescript
it('maps positions within template blocks', () => {
  // Regression: positions falling within template syntax must map back to original
  const input = 'Hello {{ name }}\nWorld';
  const mappings = generatePositionMappings(input, templateRegex);
  expect(mappings).toContainEqual({ originalOffset: 8, ...});
});
```

### 3. Run Full Package Tests

After adding regression tests:

1. Run all tests for the affected package: `pnpm -C src/packages/<package> test`
2. Confirm all pass, including the new regression test
3. If any test fails, fix the code and re-run
4. Repeat until full suite passes

### 4. Replicate CI Failures Locally

If a PR CI check fails but local tests pass:

1. Get the exact command from the GitHub Actions workflow (e.g., in `.github/workflows/*.yml`)
2. Run that command locally in the same environment
3. If you can reproduce the failure, fix the code and re-validate with step 2
4. If you cannot reproduce, investigate environment differences (Node version, dependencies, etc.)

**Common commands**:

- Type check: `pnpm run type:check`
- Lint: `pnpm run lint:eslint` or `pnpm run lint:staged`
- Tests: `pnpm test:affected:ci` or `pnpm -C <package> test`
- Frontmatter validation: `pnpm run lint:frontmatter`

### 5. Pre-Push Gate

Before pushing to origin:

1. Run: `pnpm run hooks:pre-push`
2. This runs all gating checks (lint, tests, frontmatter validation)
3. **Pass if**: All checks pass
4. **Fail if**: Any check fails — fix locally before pushing

The hook is configured in `.husky/pre-push`; if disabled, manually run the command above.

## Integration with Other Skills

- **executing-backlog**: Invokes this skill before PR merge gates
- **parallel-execution**: Runs this skill per workspace after subagent code changes
- **guarding-branches**: Works in tandem — validate changes, then apply merge guardrails

## Troubleshooting

**Tests fail but I think they should pass?**

- Check the test file for recent changes that might affect it
- Read the failure message carefully — it often suggests the fix
- Run the test in isolation: `vitest run <test-file>` for more detail

**CI passes locally but fails on GitHub?**

- Environment mismatch: Check Node version, pnpm version in CI vs local
- Cache issue: Try `pnpm install --frozen-lockfile` to match CI exactly
- Race condition: Some tests may be order-dependent; run full suite, not individual tests

**Pre-push hook is too slow?**

- The hook runs many checks; if it's blocking, file an issue for optimization
- DO NOT disable the hook; instead, improve the hooks configuration per repo instructions

**Regression test feels like overkill?**

- It prevents the same bug from shipping twice; it's worth the token cost
- Keep regression tests concise and focused on the specific edge case
- Link the test to the issue/PR in a comment for context
