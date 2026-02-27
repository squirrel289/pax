---
name: auditing-backlog-checkboxes
description: "Audit backlog work items in `closed`, `completed`, or `ready-for-review` status that still contain unchecked checklist items (`[ ]`). Validate each unchecked item against code and test evidence, mark only fully validated items as `[x]`, and output only a per-work-item summary status report for Tasks and Acceptance Criteria plus recommended workflow next steps. Use when asked to audit completion evidence, clean up stale checklists, or prepare work items for closure/finalization."
metadata:
  type: document
  subtype: skill
---

# Auditing Backlog Checkboxes

## Overview

Audit checklist accuracy for late-stage work items and enforce evidence-backed completion updates.

Use this skill to eliminate false-positive completion by requiring direct repository evidence before changing any `[ ]` to `[x]`.

## Inputs

- Backlog root directories (default: auto-discover directories named `backlog`)
- Target statuses (default: `closed,completed,ready-for-review`)
- Scope boundary (entire backlog or explicit file list)

## Resources

- Discovery helper: [`scripts/find_target_checkboxes.sh`](scripts/find_target_checkboxes.sh)
- Evidence rubric: [`references/evidence-validation-rubric.md`](references/evidence-validation-rubric.md)

## Path Resolution (Required)

- Resolve all bundled resource paths relative to this `SKILL.md` file, not relative to the current workspace root.
- Define `SKILL_DIR` as the directory containing this `SKILL.md`.
- Invoke resources via `"$SKILL_DIR/<resource-path>"` (for example, `"$SKILL_DIR/scripts/find_target_checkboxes.sh"`).

## Workflow

### 1) Discover Candidate Checklists

Run the helper script via `SKILL_DIR` so invocation works from any workspace:

```bash
SKILL_FILE="/absolute/path/to/auditing-backlog-checkboxes/SKILL.md"
SKILL_DIR="$(cd "$(dirname "$SKILL_FILE")" && pwd)"
"$SKILL_DIR/scripts/find_target_checkboxes.sh"
```

Optional scoping:

```bash
SKILL_FILE="/absolute/path/to/auditing-backlog-checkboxes/SKILL.md"
SKILL_DIR="$(cd "$(dirname "$SKILL_FILE")" && pwd)"
"$SKILL_DIR/scripts/find_target_checkboxes.sh" \
  --backlog-dir backlog \
  --backlog-dir nirvana/backlog \
  --status closed,completed,ready-for-review
```

Treat each row as one validation target.

### 2) Validate Evidence per Unchecked Checkbox

For each `[ ]` entry:

1. Translate checkbox text into a verifiable claim.
2. Collect direct evidence from implementation and tests:
   - `rg -n "<claim keywords>" <code paths>`
   - `rg -n "<claim keywords>" test* docs*`
   - Run focused tests when a command exists for the claim.
3. Apply the rubric in [`references/evidence-validation-rubric.md`](references/evidence-validation-rubric.md).

Mark as validated only when:

- The implementation exists at a concrete file path.
- Behavior is covered by passing tests or equivalent objective verification.
- The checkbox wording matches what is actually implemented.

If any of the above is missing, keep `[ ]`.

Track per-section counts while auditing each work item:

- `checked this turn`: count of checkboxes changed from `[ ]` to `[x]` in this audit run.
- `total checked`: total `[x]` currently present after edits.
- `total unchecked`: total `[ ]` currently present after edits.

Compute these counts separately for:

- `Tasks` section
- `Acceptance Criteria` section

Record warnings about unvalidated checkboxes (i.e., changed from `[x]` to `[ ]`), ambiguous checkbox text, missing evidence, or other issues for later reporting.

### 3) Update Backlog Files

For each validated checkbox, update `[ ]` to `[x]` in place.

For each remaining unchecked checkbox:

- Keep `[ ]` unchanged in the work item file.
- Do not add `resolution-plan` fields or append resolution-plan sections to work items.
- Do not remove unresolved checkboxes. Keep them visible until completion evidence exists.

### 4) Final Consistency Pass

After edits:

1. Re-run `"$SKILL_DIR/scripts/find_target_checkboxes.sh"` and confirm remaining `[ ]` lines are intentional.
2. Produce only this inline per-work-item summary format:

```markdown
### <work item path or id>

- Tasks:
  - checked this turn / total checked: `<n> / <n>`
  - total unchecked / total checkboxes: `<n> / <n>`
- Acceptance Criteria:
  - checked this turn / total checked: `<n> / <n>`
  - total unchecked / total checkboxes: `<n> / <n>`
- WARNINGS (if any):
  - Ambiguous checkbox text: `<checkbox text>` at `<file path>:<line number>`
  - Missing implementation evidence for: `<checkbox text>` at `<file path>:<line number>`
  - Missing or failing test evidence for: `<checkbox text>` at `<file path>:<line number>`
- Recommended Next Steps:
  - `<deterministically generated action 1>`
  - `<deterministically generated action 2>`
  - `<deterministically generated action 3>`
```

Guidance for `Recommended Next Steps` generation:

- Generate recommendations dynamically from findings, warnings, status, and unchecked counts, but use the deterministic synthesis order below.
- Do not constrain recommendations to a fixed command set or a fixed domain.
- Keep `2-5` bullets unless the "no further action" rule applies.

Deterministic synthesis order (apply top to bottom, include only applicable actions):

1. Ambiguous checkbox warnings: add an action to clarify/rewrite checkbox wording to a verifiable claim.
2. Missing implementation evidence warnings: add an action to implement or link the concrete code path.
3. Missing or failing test evidence warnings: add an action to add/fix verification and re-run targeted tests.
4. Unchecked items remain and status is `closed` or `completed`: add an action to use `update-work-item` to move to an active status before further work.
5. Unchecked items remain (any status): add an action to execute remaining scope via the most relevant workflow (for example `executing-backlog` when applicable).
6. No unchecked items and no warnings and status is `closed`: add `finalize-work-item`.
7. No unchecked items and no warnings and status is not `closed`: emit exactly one bullet, `No further action required.`

Normalization rules:

- De-duplicate semantically equivalent actions.
- Preserve synthesis order; do not reorder by style.
- Write imperative, concrete actions that reference the relevant section, warning class, or work item context.

## Non-Negotiable Rules

- Do not mark a checkbox complete based on intent, comments, or TODO notes.
- Do not mark a checkbox complete if tests are absent, failing, or unrelated to the checkbox claim.
- Do not change work item status fields unless explicitly requested.
- Keep evidence references concrete (file path, test file, command, result).
- Do not emit per-checkbox remediation plans; output only the summary status format above.

## Output Contract

Return:

1. Files updated with newly marked `[x]` checkboxes.
2. Only an inline per-work-item summary status including exactly as defined in [Final Consistency Pass](#4-final-consistency-pass).
