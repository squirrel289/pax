---
name: auditing-backlog-checkboxes
description: "Audit backlog work items in `closed`, `completed`, or `ready-for-review` status that still contain unchecked checklist items (`[ ]`). Validate each unchecked item against code and test evidence, mark only fully validated items as `[x]`, and add a concrete resolution plan for every remaining unchecked item. Use when asked to audit completion evidence, clean up stale checklists, or prepare work items for closure/finalization."
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

## Workflow

### 1) Discover Candidate Checklists

Run the helper script to locate only eligible files and unchecked checkbox lines:

```bash
skills/tools/auditing-backlog-checkboxes/scripts/find_target_checkboxes.sh
```

Optional scoping:

```bash
skills/tools/auditing-backlog-checkboxes/scripts/find_target_checkboxes.sh \
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

### 3) Update Backlog Files

For each validated checkbox, update `[ ]` to `[x]` in place.

For each remaining unchecked checkbox, add or update a section named:

```markdown
### Resolution Plan for Remaining Unchecked Items
```

Use one numbered plan item per unchecked checkbox with this format:

```markdown
1. [ ] <original checkbox text>
             - Missing evidence: <specific missing code/test/proof>
             - Next action: <concrete implementation or validation step>
             - Verification command: `<exact command>`
             - Completion signal: <artifact proving it can be marked [x]>
```

Do not remove unresolved checkboxes. Keep them visible until completion evidence exists.

### 4) Final Consistency Pass

After edits:

1. Re-run `find_target_checkboxes.sh` and confirm remaining `[ ]` lines are intentional.
2. Ensure every remaining `[ ]` has a matching plan item in the resolution section.
3. Prepare a summary grouped by file:
   - Count marked `[x]`
   - Count unresolved `[ ]`
   - Commands used for verification

## Non-Negotiable Rules

- Do not mark a checkbox complete based on intent, comments, or TODO notes.
- Do not mark a checkbox complete if tests are absent, failing, or unrelated to the checkbox claim.
- Do not change work item status fields unless explicitly requested.
- Keep evidence references concrete (file path, test file, command, result).

## Output Contract

Return:

1. Files updated with newly marked `[x]` checkboxes.
2. A per-file resolution plan for remaining unchecked items.
3. A concise audit summary with evidence references and verification commands.
