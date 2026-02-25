---
name: executing-backlog
description: 'Orchestrate the full lifecycle of implementing backlog work items from planning through delivery, with integrated validation gating for bulk operations. Use when: (1) Asked to execute backlog, implement work items (WI-ABC), or close out a task, (2) Implementing changes across 3+ similar files, (3) Need end-to-end delivery including PR/merge. Coordinates with prevalidating-bulk-operations for routing and discover-validation-criteria for schema discovery.'
---

# Execute Backlog

## Allowed Tools

- `terminal` for shell commands
- `git` for repository operations
- `pnpm` for scripts/tests
- `gh` for GitHub interactions

Use no other tools unless the user explicitly authorizes them in the request.

## When to Use this Skill

- Request explicitly names work item IDs (WI-XXX) or describes a backlog task
- Need end-to-end delivery from planning through merge/finalization
- Coordinating multi-phase work (parallel tickets, blockers, release gating)
- Answering "Start working on WI-ABC" / "Execute backlog" / "Close WI-XYZ"

## Execution Gates

This skill enforces quality gates at critical workflow points. See [references/execution-gates.md](references/execution-gates.md) for detailed gate specifications.This skill uses complementary aspects to ensure branch safety:

- **Clarification Gate**: Verify WI identifiers, dependencies, and acceptance criteria before starting
- **Completion Gate**: Ensure all checklist items checked before closing work items
- **Atomic Scope Gate**: One WI per branch/PR, atomic commits with matching tests
- **Workspace Safety Gate**: Protect out-of-scope changes from destructive operations
- **Branch Safety Gate**: Use `guarding-branches` aspect at every merge point (mergeability checks, conflict resolution, export scanning, diff validation against main)

## Mandatory Planning Output (before acting)

Before modifying the repository, publish an explicit plan that includes: a summary sentence, the sequence of phases, the dependency status, required tests/commands, validation criteria discovered, and the next merge/cleanup tasks. Use this template and fill with concrete values:

```
Plan Summary: <short goal>
Work Items: <WI list + dependencies (closed/pending)>
Scope Boundaries: <single active WI for this branch/PR + explicit out-of-scope items>
Execution Phases: 1) Audit/dependencies 2) Branch/implement/test 3) PR/review/merge 4) Finalize
Validation Signals: <required commands/results to confirm before PR>
Completion Steps: <merge strategy, cleanup, metrics update>
```

Do **not** translate this into placeholders; every bullet must mention actual WIs, commands, or outcomes. If a line cannot be filled with facts, pause and ask for clarification.

## Validation Gating for Bulk Operations

When work item affects 3+ similar files:

1. **Use `prevalidating-bulk-operations` aspect** to route the operation (Phase 1)
   - Returns routing decision: PATTERN_REQUIRED, PATTERN_CONDITIONAL, or DIRECT
   - Provides evidence showing file count, schema discoverability, operation type
   - See [aspects/prevalidating-bulk-operations](../../aspects/prevalidating-bulk-operations/SKILL.md) for decision framework

2. **Based on routing, call `discover-validation-criteria`** if pattern applies
   - Extracts all schema, linting, format requirements for affected files
   - Outputs criteria dict with field constraints, validation commands, test procedures
   - One-time discovery cost (Phase 1) saves multiple validation failures during Phase 2
   - Include criteria dict evidence in mandatory planning output

3. **For single-file or direct-routed operations**, skip to Phase 2 directly
   - Document the DIRECT routing decision in planning output
   - Proceed to Phase 2 implementation and validation

## Anti-placeholder Rule

- Never respond with generic placeholders such as "Change 1"/"Change 2", empty checkboxes that read as pre-checked, or unnamed sections. Every section must describe real actions, outcomes, and evidence.
- When summarizing PR changes/tests, reference actual files, commands, or results (e.g., `pnpm test packages/parser -- --runInBand`). Copying template text without filling these fields violates the rule.

## Evaluation Integration

When Phase 2 validation fails, use `agentic-eval` patterns for systematic iteration:

```
Discover Criteria → Sample Change → Validation Fails
                         ↓
                  Evaluate + Fix → Re-test Sample (max 3 attempts)
                         ↓
                  Sample Passes → Bulk Apply
```

**Iteration Constraints**:

- Maximum 3 evaluation attempts per sample
- If sample still fails after 3 attempts, escalate to user (don't continue guessing)
- Each attempt must use error message + discovered criteria (not trial-and-error)

**Anti-Patterns**:

- ❌ Skip schema discovery and guess validation format
- ❌ Update all files before testing format on 1 sample file
- ❌ Use trial-and-error instead of parsing error messages
- ❌ Continue iterating beyond 3 attempts without escalation

Reference `agentic-eval` skill for full evaluation patterns.

## Prerequisites & Preparation

1. Ensure `auditing-backlog` has run recently and that `links.depends_on` data are up to date; rely on the dependency graph coverage described in `skills/auditing-backlog/SKILL.md`, Phases 2-4.
2. Confirm no blocking dependencies are `in-progress` or `ready` by checking their status fields; only start when blockers are `closed` or explicitly deferred.
3. Verify tooling (`pnpm`, `gh`, credentials) is configured locally; document any missing SDKs or credentials in the plan before touching code.
4. If executing multiple work items in parallel, use `parallel-execution` skill to ensure workspace isolation (one working tree per WI) and use the subagent split rule: subagents implement code only, main agent handles all git/PR operations.

## Execution Phases (after plan confirmed)

### Phase 1: Planning & Validation

- Run `auditing-backlog` to surface orphans and dependency chains before work begins.
- **For bulk operations (3+ similar files)**: Run `prevalidating-bulk-operations` aspect to decide routing:
  - If routing = PATTERN_REQUIRED or CONDITIONAL+discoverable: Call `discover-validation-criteria`, document criteria dict
  - If routing = DIRECT: Skip criteria discovery, document DIRECT evidence in plan
- Update the WI status to `in-progress`, list verified dependencies, note any unresolved blockers in work item notes.
- Populate mandatory planning output with: WI list + dependencies, scope boundaries, execution phases, validation routing evidence, completion steps.
- Record the chosen feature branch name, expected tests, merge point, and validation signals (commands to run before PR).
- Record current workspace state (`git status --short`) and identify out-of-scope changes that must be preserved during this WI.

### Phase 2: Branching & Implementation

- Use `feature-branch-management` to create/sync a branch (`feature/wi-NNN-slug` or `bugfix/...`).
- Implement code using guidance from `modern-javascript-patterns`, `typescript-advanced-types`, and `nodejs-backend-patterns` as appropriate.
- **For bulk file updates (e.g., updating 9 similar files)**: Follow the **sample-file validation pattern** before bulk-applying changes:
  1. **Phase 2a (Sample Validation)**: Create or modify ONE sample file with the new format/changes
  2. **Phase 2a (Validate Sample)**: Run the validation command on the sample file only (criteria dict should specify which command: `pnpm run lint:frontmatter`, `pnpm run test`, etc.)
  3. **Phase 2a (Confirm Pass)**: Ensure sample passes validation; if fails, debug format/constraints using error message and discovered criteria
  4. **Phase 2b (Bulk Apply)**: Only after sample passes, apply the same changes to all remaining files
- Expand tests per `javascript-testing-patterns`; reference actual files/commands when documenting coverage.
- Commit via `git-commit` with a conventional message tied to the WI, using multiple atomic commits as work advances instead of a single end-of-phase commit.
- Stage changes with explicit file lists for the active WI; if staging reveals unrelated files, remove them from the index and leave their working-tree changes intact.

**Validation Iteration Note**: If bulk validation fails after Phase 2b, use `agentic-eval` patterns (see "Evaluation Integration" below) to systematically refine changes rather than trial-and-error attempts.

### Phase 3: PR & Review

- Push the WI branch and create exactly one WI-scoped PR with `create-pr`, populating descriptions with real work item summaries, changes, and testing commands.
- Maintain checkbox integrity: check boxes only after confirming evidence (e.g., `[x] Unit tests (`pnpm test src/feature.test.ts`)`). Leave unchecked until the command runs successfully.
- Seek reviewers via `copilot-pull-request`, `pull-request-tool`, or `gh-pr-review` and use `code-review-excellence` to surface gaps.

### Phase 4: Feedback, Merge, Finalization

- Use `handle-pr-feedback`/`resolve-pr-comments` to close blockers; categorize comments (blocker/major/minor) explicitly in responses.
- Merge with `merge-pr` skill, which enforces both Test Parity Gate (local tests pass) and guarding-branches checks (mergeability, conflicts, deletions) before merge.
- Finalize the work item with `finalize-work-item`, recording actual hours, metrics, and cleaning up branches per `feature-branch-management`.

## Monitoring & Metrics

- Track cycle time, review rounds, test coverage, deployment frequency, blocker rate, and rework rate. Use the simple script in the previous version as needed, but document any anomalies directly in the work item.

## Scope-adjustment Proposal

If covering the full end-to-end workflow in one skill proves too broad, split this skill: keep `executing-backlog` focused on orchestration/planning (clarification gate, plan output, dependency checks) and delegate implementation/review to targeted skills (e.g., `code-execution`, `review-management`). That separation keeps each skill concise and easier to validate.
