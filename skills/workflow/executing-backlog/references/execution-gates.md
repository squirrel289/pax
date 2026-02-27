# Execution Gates

Quality gates to prevent common workflow issues.

## Clarification Gate

If the request lacks a concrete work item, dependencies, acceptance criteria, or target branch, stop and ask for the missing details. Do **not** proceed until the user supplies:

1. The WI identifier(s) or a well-defined feature description.
2. Existing blockers/dependencies that might delay execution.
3. Desired outcomes (tests, documentation, release step).

Every response here should reference the dependency graph defined in `skills/tools/auditing-backlog-dependency-graph/SKILL.md` (Phases 2-4) as the single source for dependency validation before making implementation decisions.

## Completion Gate

- Never mark a work item `closed` or `completed` when any required checklist item is unchecked.
- If a checkbox is intentionally skipped, record the reason and explicit user approval before changing status.
- If evidence is missing for any checklist/test/dependency item, keep the work item in `in-progress` or `ready-for-review`.
- Never close a WI from a combined PR that also includes unrelated WI scope.

## Atomic Scope Gate

- Keep branch, commits, and PR scoped to one WI.
- Create one PR per WI. Do not open phase-level or multi-WI umbrella PRs for implementation work.
- Split implementation into atomic commits: each commit should represent one coherent change with matching tests/docs updates when applicable.
- If the user asks for multiple WIs, plan parallel/sequential execution as separate branches and separate PRs.
- If scope drifts beyond the active WI, stop and either: (1) create a follow-up WI, or (2) ask user approval to re-scope.

## Workspace Safety Gate

- Treat existing uncommitted changes outside the active WI as protected parallel work.
- Never discard, reset, checkout, or overwrite out-of-scope workspace changes.
- Never run destructive cleanup commands (`git reset --hard`, `git checkout --`, broad `git clean`) unless the user explicitly requests that exact action.
- If out-of-scope changes block progress, stop and ask the user how to proceed (for example: isolate on a new branch, stash with explicit approval, or sequence WI execution).
- Before commit/PR actions, verify staged files only belong to the active WI; unstage unrelated files instead of deleting changes.
