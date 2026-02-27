# AGENTS.md Quality Checklist

Use this checklist to review or score an `AGENTS.md` or `.github/agents/*.md` file.

## Core Coverage

Score each area `0-2`:

- `0`: Missing
- `1`: Present but vague
- `2`: Specific and actionable

Areas:

1. `Commands`
   - Runnable commands are listed near the top.
   - Commands include full syntax (flags/options when needed).
2. `Testing`
   - Test commands and pass criteria are explicit.
   - Agent behavior on failing tests is defined.
3. `Project Structure`
   - Key directories and ownership are documented.
   - Read/write boundaries are explicit.
4. `Code Style / Output Standards`
   - Rules are concrete and short.
   - At least one real good-output example is included.
5. `Git Workflow`
   - Commit/branch/PR expectations are specified for the repo.
6. `Boundaries`
   - Three-tier rules exist: `Always`, `Ask first`, `Never`.
   - Forbidden actions include secrets handling and unsafe/destructive edits.

Target score: `>=10/12` before considering the file production-ready.

## Anti-Patterns and Fixes

- Anti-pattern: Generic role text ("helpful assistant")
  - Fix: Use a narrow role with explicit deliverables.
- Anti-pattern: Tool names without commands
  - Fix: Replace with exact executable commands.
- Anti-pattern: Hidden constraints in long prose
  - Fix: Convert to explicit bullet rules under `Boundaries`.
- Anti-pattern: Stack labels without versions
  - Fix: Add key versions and frameworks.
- Anti-pattern: No examples
  - Fix: Add one concrete style/output snippet.

## Iteration Loop

When an agent makes a mistake:

1. Capture the failure mode (what happened, where, why).
2. Add or tighten one instruction to prevent that class of failure.
3. Re-run commands/tests.
4. Keep the file concise; remove redundant text.
