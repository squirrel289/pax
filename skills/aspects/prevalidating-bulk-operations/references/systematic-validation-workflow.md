# Systematic Validation Workflow

## Overview

When updating multiple files against schema constraints, a three-phase pattern prevents trial-and-error iteration and reduces validation failures. This document describes the reusable architectural pattern applicable to any schema validation + bulk operations task.

**Core Principle**: Discover requirements → test sample → bulk apply (not: guess → apply → fail → retry)

---

## Problem Being Solved

When implementing bulk file changes (3+ similar files) with format or schema constraints:

- **Challenge**: Validation rules are scattered across schema files, lint configs, and documentation
- **Risk**: Discovering requirements during implementation leads to multiple failed validation attempts
- **Cost**: Each failed bulk operation requires investigating the error, updating all files again, and re-validating
- **Example impact**: 4 validation attempts × 9 files × time-to-update-and-test = significant waste

## Solution: Three-Skill Composition

```text
Discover Criteria (Skill 1)
         ↓
    [Criteria Dict]
         ↓
Sample Validation (Skill 2, Phase 2a)
         ↓
    ├─ PASS → Bulk Apply (Skill 2, Phase 2b)
    │
    └─ FAIL → Evaluate & Refine (Skill 3) → Re-test Sample → [Loop max 3×]
```

The pattern decomposes validation work into three distinct responsibilities:

### Skill 1: Criteria Discovery

**Input**: File paths, schema locations

**Output**: Structured criteria dict (field constraints, formats, required fields, validation commands)

**Cost**: One-time, Phase 1

### Skill 2: Execution & Sample Validation

**Input**: Criteria dict, work item scope

**Output**: Sample-validated changes (Phase 2a), bulk-applied changes (Phase 2b)

**Cost**: Multiple iterations only on 1 sample file, not all 9

### Skill 3: Systematic Evaluation

**Input**: Validation error, criteria dict

**Output**: Targeted refinement (not guessing), format fix

**Cost**: Called only if sample fails (not standard path)

---

## Data Flow

```text
Phase 1: Planning
├─ Run Skill 1 (discover-validation-criteria)
├─ Extract: schema files, constraints, formats
├─ Output: Structured criteria dict
└─ Include in plan: "Validation Criteria Discovered: [fields, constraints, commands]"

Phase 2a: Sample Validation
├─ Create/modify 1 sample file
├─ Run validation command (from criteria dict)
├─ If PASS → advance to Phase 2b
├─ If FAIL → invoke Skill 3 (agentic-eval)
│  ├─ Evaluate: Parse error message
│  ├─ Refine: Generate fix using error + criteria (not guessing)
│  ├─ Validate: Re-test on sample
│  └─ Repeat: Max 3 attempts, then escalate
└─ After max 3 attempts and PASS → Phase 2b

Phase 2b: Bulk Apply
├─ Apply validated format to all remaining files
├─ Run final validation (should pass on first attempt)
└─ Assert: All files pass in one validation run
```

---

## Key Concepts

### Validation Criteria Dict

Structured output from Skill 1 that documents all discovery findings:

```json
{
  "affected_files": ["file_pattern/*.md"],
  "validation_commands": {
    "schema": "pnpm run lint:schema",
    "format": "pnpm run format:check"
  },
  "constraints": {
    "field_name": {
      "type": "string|array|object",
      "required": true|false,
      "format": "description",
      "pattern": "regex (if applicable)",
      "enum": ["value1", "value2"],
      "example": "actual example"
    }
  },
  "test_commands": ["command1", "command2"],
  "notes": "Schema source, special considerations"
}
```

### Sample-File Validation Pattern

Before applying changes to all files:

1. **Prepare 1 sample** (create or modify ONE file with new format)
2. **Validate sample** (run validation command on sample only)
3. **Result: PASS** → proceed to bulk apply
4. **Result: FAIL** → evaluate error + refine using Skill 3 → re-test sample (max 3 attempts)

**Why this works**: Failures are fast (1 file vs. all N files), and fixes are validated before scaling.

### Iteration Limits & Escalation

- **Sample validation loop**: Maximum 3 evaluation attempts
- **Escalation trigger**: After 3 failed attempts, stop and escalate to user (don't continue guessing)
- **Escalation path**: Document the error, the tried formats, and ask for clarification on requirements

---

## Benefits

### Efficacy

**Before**: Multiple format attempts with no systematic path to correct solution.

- Risk: Bulk operation fails, cascades to all N files
- Mitigation path unclear (guess better next time)

**After**: Criteria-guided refinement with explicit error → fix mapping.

- Criteria sourced from schema (authoritative)
- Error messages + criteria → targeted refinement
- Validation on sample before scaling to N files
- Clear escalation path after 3 attempts

### Efficiency

| Aspect          | Before                   | After                 | Savings                   |
| --------------- | ------------------------ | --------------------- | ------------------------- |
| Schema reads    | Multiple (per iteration) | 1 (Phase 1)           | Fewer reads               |
| Validation runs | N × attempts             | 1 (sample) + N (bulk) | 4× fewer file validations |
| File writes     | N × attempts             | N (bulk once)         | 4× fewer writes           |
| Iteration cycle | Slow (bulk update)       | Fast (1-file sample)  | Faster feedback           |

For bulk operations touching N files with C constraints:

- Trial-and-error: O(N × iterations)
- Systematic workflow: O(1 + N) after criteria discovery

### Composability

The three-skill pattern is reusable across different domains:

- Schema validation (JSON, YAML, TypeScript)
- Bulk format migrations
- Any scenario with "test on sample before production"
- Pairs with standard evaluation patterns (reflection, error analysis)

---

## Anti-Patterns

❌ **Skip criteria discovery, guess format based on intuition**

- Result: Multiple failed attempts; no way to know if you're getting closer

❌ **Apply changes to all N files before testing on 1**

- Result: All N files fail validation; slow feedback loop

❌ **Use trial-and-error instead of error message + criteria**

- Result: Systematic refinement impossible; iteration limit unclear

❌ **Continue iterating beyond 3 attempts without escalation**

- Result: Infinite loop; unclear if problem is solvable

❌ **Discover criteria during Phase 2, not Phase 1**

- Result: Planning output incomplete; mid-implementation discovery wasted

---

## Integration Points

| Skill/Pattern                 | Role              | Triggered By                                  |
| ----------------------------- | ----------------- | --------------------------------------------- |
| Validation Criteria Discovery | Phase 1 gate      | Start of execution planning                   |
| Planning Output               | Documentation     | After criteria discovery                      |
| Sample-File Validation        | Phase 2a workflow | Before bulk operations                        |
| Systematic Evaluation         | Phase 2a fallback | If sample validation fails                    |
| Bulk Apply                    | Phase 2b          | After sample passes or max iterations reached |

---

## When to Use This Pattern

**Ideal scenarios**:

- Updating 3+ similar files with identical format/schema changes
- Files have schema validation (JSON Schema, YAML, linting, type checking)
- Format constraints are discoverable from schema or documentation
- Need predictable, repeatable validation workflow

**Less ideal scenarios**:

- Single-file changes (skip to bulk apply directly)
- No schema/validation (no criteria to discover)
- Validation rules are implicit or undocumented (discovery harder)

---

## Example: Generic Bulk Update

**Task**: Update 5 configuration files with new required field.

**Phase 1**:

```text
1. Find schema file (config.schema.json)
2. Read required fields, new field constraints
3. Note validation command (npm run validate:config)
4. Output: Criteria dict with field constraints
```

**Phase 2a**:

```text
1. Create config-sample.json with new field
2. Run: npm run validate:config -- config-sample.json
   Result: PASS ✓
3. Advance to Phase 2b
```

**Phase 2b**:

```text
1. Apply new field to all 5 config files
2. Run: npm run validate:config (validates all)
   Result: All PASS ✓
```

**Total effort**: 1 schema read + 1 sample validation + 1 bulk validation = predictable, fast.

---

## Related Concepts

- **Shift-left validation**: Discover requirements before implementation (Phase 1, not Phase 2)
- **Test-driven development**: Validate format on sample before committing to all files
- **Error-driven refinement**: Use error messages + constraints to guide fixes, not intuition
- **Escalation protocol**: Know when to ask for help (after 3 attempts)
