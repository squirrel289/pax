---
name: auditing-backlog
description: "Run an end-to-end backlog audit by composing dependency graph validation with evidence-backed checklist validation. Use when asked to audit backlog quality before release, verify closure readiness, clean up stale completion status, or produce one cohesive backlog health report from dependency and checkbox findings."
metadata:
  type: document
  subtype: skill
---

# Auditing Backlog

Use this skill as an orchestrator. It composes:

- [`$auditing-backlog-dependency-graph`](../auditing-backlog-dependency-graph/SKILL.md)
- [`$auditing-backlog-checkboxes`](../auditing-backlog-checkboxes/SKILL.md)

Do not duplicate lower-level checks here. Delegate detailed dependency heuristics and checkbox evidence rules to the source skills.

## Inputs

- Backlog scope: all work items or explicit file list
- Audit mode:
  - `report-only`: analyze and report findings without edits
  - `fix-and-report`: apply safe fixes, then report
- Checkbox status scope (default): `closed,completed,ready-for-review`

## Workflow

### 1) Preflight and Scope

1. Confirm both composed skills exist and are readable.
2. Confirm work-item frontmatter validation is runnable (`pnpm run lint:frontmatter`).
3. Resolve target backlog files from user-provided scope; if no scope is provided, audit all work items.

If schema validation fails, fix schema issues first or stop in `report-only` mode with blockers.

### 2) Dependency Graph Audit Pass

Invoke `$auditing-backlog-dependency-graph` for the selected scope and run its full dependency workflow.

Capture findings by class:

- schema/validation blockers
- orphan work items
- missing direct dependencies
- broken dependency chains or pattern gaps
- consistency or circular-dependency risks

If running `fix-and-report`, apply dependency fixes first and re-run validation before moving to checkbox auditing.

### 3) Checkbox Evidence Audit Pass

Invoke `$auditing-backlog-checkboxes` after dependency pass completion.

Use default status scope unless user overrides it. Keep its evidence rules strict:

- mark `[x]` only with direct implementation and verification evidence
- keep unresolved items as `[ ]`
- do not mutate status fields unless explicitly requested

### 4) Cohesive Backlog Report

Return one consolidated report with these sections in order:

1. Dependency Graph Summary
2. Checkbox Evidence Summary
3. Cross-Signal Risks
4. Recommended Next Steps

For Cross-Signal Risks, highlight items where dependency or status state conflicts with checkbox completion claims.

## Deterministic Decision Rules

1. If schema/frontmatter blockers exist, do not present closure-ready recommendations.
2. Always run dependency audit before checkbox audit.
3. If an item is `closed` or `completed` with unresolved unchecked boxes, recommend reopening via `update-work-item`.
4. If both passes are clean for an item, recommend `finalize-work-item` only when status is `closed`.

## Output Contract

Produce:

1. Any applied file edits (only in `fix-and-report` mode).
2. A single consolidated backlog audit summary in the section order defined above.
