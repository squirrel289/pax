# Schema Validation for Bulk Operations: How-To Guide

When updating 3+ similar files with schema/format constraints, follow this systematic workflow.

---

## Quick Reference

```text
Phase 1: Discover Validation Rules
├─ Identify affected files & schemas
├─ Extract all validation constraints
└─ Document as structured criteria dict

Phase 2a: Sample-File Validation
├─ Create/modify ONE sample file
├─ Run validation on sample
├─ If PASS → Phase 2b
└─ If FAIL → Evaluate error, refine, re-test (max 3 attempts)

Phase 2b: Bulk Apply
├─ Apply validated format to all remaining files
└─ Run final validation
```

**Expected outcome**: All N files pass validation in one bulk run.

---

## Phase 1: Discover Validation Criteria

### Step 1: Identify Schemas

List files to update and find schema sources:

**Find schema files**:

```bash
find . -name "*.schema.json" -o -name "*-schema.json"
```

**Find validation configs**:

```bash
find . -name ".eslintrc*" -o -name ".yamllint" -o -name "pyrightconfig.json"
```

### Step 2: Extract Rules

For JSON Schema, read the schema file and note:

- Field name
- Type (string, array, object)
- Required (yes/no)
- Format constraints (pattern, enum, etc.)
- Example value

For linting rules, read the config file and note validation constraints.

### Step 3: Document as Criteria Dict

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
      "required": true,
      "format": "description",
      "pattern": "regex",
      "example": "value"
    }
  },
  "test_commands": ["pnpm run lint:schema"],
  "notes": "Schema source and special considerations"
}
```

### Step 4: Include in Plan

Add discovered criteria to your planning output for reference.

---

## Phase 2a: Sample-File Validation

### Step 1: Create Sample File

Copy an existing file or create from scratch:

```bash
cp backlog/001_example.md backlog/SAMPLE_001.md
```

### Step 2: Apply New Format

Edit the sample file with the new format you want to apply to all files.

### Step 3: Validate Sample

Run validation on the sample file only:

```bash
pnpm run lint:schema -- backlog/SAMPLE_001.md
```

### Step 4: Interpret Results

**If PASS**: Format is correct. Move to Phase 2b.

**If FAIL**: Read error message carefully. Compare to discovered constraints. Refine format and retry (max 3 times).

### Step 5: Debug Failed Validation

When sample validation fails, follow this pattern up to 3 times:

1. **Read error message** - Understand what failed
2. **Check constraints** - Compare error to discovered criteria
3. **Refine format** - Generate fix based on error + constraints (not guessing)
4. **Re-test sample** - Validate again

**After 3 failed attempts**: Stop and escalate. Document error, attempted formats, and constraint source. Ask for clarification.

---

## Phase 2b: Bulk Apply

### Prerequisites

- Sample validation PASSED ✓
- Format confirmed correct
- Ready to scale to all N files

### Step 1: Apply to All Files

Apply the same changes to all remaining files using your preferred method (editor, find-replace, script, etc.).

### Step 2: Validate All Files

Run validation on ALL files at once:

```bash
pnpm run lint:schema
```

**Expected**: ALL files PASS on first run.

### Step 3: Confirm Results

- [ ] All files validated successfully
- [ ] No errors or warnings
- [ ] Format consistent across files
- [ ] Sample file cleaned up (delete SAMPLE_001.md)

---

## Common Pitfalls

### Pitfall 1: Skip Sample Testing

**Wrong**: Edit all 9 files, then validate all at once.

**Right**: Edit 1 sample, validate it, confirm it passes, then apply to all 9.

### Pitfall 2: Guess Format

**Wrong**: Error says "pattern mismatch", so guess a different format without analyzing the error.

**Right**: Read error message, check constraint pattern, generate targeted fix.

### Pitfall 3: Iterate Beyond 3 Attempts

**Wrong**: Keep trying different formats after 3 failed attempts.

**Right**: After 3 attempts with no progress, stop and escalate to user.

### Pitfall 4: Validate Files Separately

**Wrong**: Validate file 1, then file 2, then file 3 separately.

**Right**: Validate all files in one command to catch cross-file issues.

---

## Success Criteria

After completing Phase 2b:

- [ ] Sample file validated before bulk apply
- [ ] All N files pass validation in one bulk run
- [ ] No validation errors
- [ ] Format consistent across all files
- [ ] Criteria dict documented
- [ ] Changes committed with validation reference
