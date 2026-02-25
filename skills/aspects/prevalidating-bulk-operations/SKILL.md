---
name: prevalidating-bulk-operations
description: "Route bulk file operations (3+ similar files) to systematic validation pattern or direct implementation. Use when: (1) Planning bulk updates, (2) Need to decide sample-validation approach, (3) Assessing validation risk in bulk operations. Evaluates file count, schema discoverability, and operation type to determine routing: PATTERN_REQUIRED, PATTERN_CONDITIONAL, or DIRECT."
---

# Prevalidating Bulk Operations

## Overview

This aspect provides a **decision framework** to route bulk file operations: when to apply the three-phase validation pattern (discover → sample → bulk apply) versus proceed directly to implementation.

**Use this aspect when**: About to implement changes affecting 3+ similar files and need to decide routing.

**Output**: Routing decision (PATTERN_REQUIRED / PATTERN_CONDITIONAL / DIRECT) + evidence.

**Related skills**:

- `discover-validation-criteria`: Called if pattern routing recommended
- `executing-backlog`: Calls this aspect in Phase 1 for bulk operations
- `agentic-eval`: Used during Phase 2a sample validation (if pattern applied)

---

## Quick Decision Framework

**Question 1: File Count**

| Count | Routing          | Rationale                              |
| ----- | ---------------- | -------------------------------------- |
| 1–2   | DIRECT           | Cost/benefit ratio too low             |
| 3–4   | CONDITIONAL      | Depends on schema discoverability (Q2) |
| 5+    | PATTERN_REQUIRED | Pattern cost amortizes well            |

**Question 2: Schema Discoverable** (ask only if 3–4 files)

| Result | Routing          | Rationale                       |
| ------ | ---------------- | ------------------------------- |
| Yes    | PATTERN_REQUIRED | Proceed with criteria discovery |
| No     | DIRECT (caution) | Document constraints first      |

**Question 3: Operation Type** (informs Phase 2a/2b approach)

| Type    | Pattern fit | Sample strategy                          |
| ------- | ----------- | ---------------------------------------- |
| UPDATE  | Standard    | Copy existing, edit sample               |
| CREATE  | Moderate    | Optional if 3–5 files; recommended if 6+ |
| MIGRATE | Critical    | Must use pattern (high risk)             |

---

## Routing Outputs

After evaluating all three questions, the aspect produces:

```json
{
  "routing": "PATTERN_REQUIRED | PATTERN_CONDITIONAL | DIRECT",
  "evidence": {
    "file_count": "numeric value + reasoning",
    "schema_discoverable": "true|false + check performed",
    "operation_type": "UPDATE|CREATE|MIGRATE + risk assessment"
  },
  "phase_sequence": [
    "Phase 1: discover-validation-criteria",
    "Phase 2a: sample-validation",
    "Phase 2b: bulk-apply"
  ],
  "cost_estimate": "total hours including sample validation",
  "next_steps": "specific skill calls and commands"
}
```

---

## Integration Points

### Called By

- **executing-backlog** (Phase 1): Decides whether to call `discover-validation-criteria`

  ```
  Phase 1: For bulk operations → prevalidating-bulk-operations →
           If PATTERN: discover-validation-criteria → continue Phase 2
           If DIRECT: skip discovery → continue Phase 2
  ```

- **auditing-backlog**: Risk assessment on bulk changes in backlog
  ```
  If bulk operation not using pattern → flag as "high-risk bulk"
  Recommend pattern for future similar tasks
  ```

### Calls

- **discover-validation-criteria** (if routing PATTERN_REQUIRED or CONDITIONAL+yes)
  - Input: file paths, schema locations
  - Output: validation criteria dict

- **executing-backlog** (receives routing evidence)
  - Uses routing decision to determine Phase 1 discovery requirement
  - Includes evidence in mandatory planning output

---

## Detailed Reference

For complete decision framework, examples, escalation protocol, and machine-executable YAML tree:

- **Decision Framework, Examples & Escalation**: [references/decision-framework.md](references/decision-framework.md)
- **Architectural Principles**: [references/systematic-validation-workflow.md](references/systematic-validation-workflow.md)
- **Operational Procedures**: [references/schema-validation-bulk-operations.md](references/schema-validation-bulk-operations.md)

---

## Success Criteria

- [ ] Routing decision logged in work item notes
- [ ] Pattern applied when aspect recommended
- [ ] Pattern skipped when aspect recommended direct
- [ ] Evidence (file count + schema check + operation type) documented
- [ ] Next step (discover-criteria or direct implementation) confirmed before Phase 2

---

## Anti-Patterns Prevented

❌ **Applying direct to 10-file operation** → Should route PATTERN_REQUIRED
❌ **Using pattern for 1-file operation** → Cost not justified, should route DIRECT
❌ **Assuming schema is discoverable without checking** → Wastes discovery time (Q2)
❌ **Applying pattern to undocumented constraints** → Discovery cost balloons (Q2: No)
❌ **Skipping sample validation for MIGRATE** → High cascading risk (Q3: MIGRATE)
