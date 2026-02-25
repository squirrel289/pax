---
name: discover-validation-criteria
description: 'Extract validation requirements from schemas before implementing changes. Prevents trial-and-error by discovering constraints upfront.'
license: MIT
---

# Discover Validation Criteria

## Overview

Before implementing changes, discover and document all validation requirements that will gate success. This prevents trial-and-error iteration by surfacing constraints upfront.

**Key Principle**: Criteria discovery happens once (Phase 1), then informs all iterations (Phase 2+).

## When to Use

- **Executing backlog work at start of Phase 1** (called by `executing-backlog`)
- Files or data structures with schema validation (JSON Schema, YAML, TypeScript types, etc.)
- Multi-file updates with consistent format rules (e.g., 9 work items with identical frontmatter requirements)
- Any situation where you'll test/validate later — discover requirements first

## Workflow

### Step 1: Identify Affected Files & Schemas

```bash
# Find schema files in repo (common patterns)
find . -name "*.schema.json" -o -name "*-schema.json" -o -name "schema.json" | head -20
find . -name ".yamllint" -o -name "eslintrc*" -o -name "pyrightconfig.json" | head -20

# Check backlog/docs for constraint documentation
grep -r "must have\|required\|format of\|constraint" backlog/ docs/ | head -20
```

### Step 2: Extract Requirements

For **JSON/TypeScript schemas**:
```bash
# Read schema file, note required fields, constraints, patterns
cat schemas/frontmatter/document.json | jq '.properties, .required'

# Example output to capture:
# - Field name: "links"
# - Type: "object"
# - Required sub-fields: ["commits", "pull_requests"]
# - Format constraint: "commits must be array of GitHub commit URLs matching pattern ..."
```

For **Linting/Formatting Rules**:
```bash
# Read lint config
cat .eslintrc.json .yamllint .prettierrc 2>/dev/null

# Run lint on single sample file to see actual error messages
pnpm run lint:frontmatter -- backlog/001_section.md 2>&1 | head -30
```

For **Custom Validation Scripts**:
```bash
# Check CI scripts and test suites
find scripts -name "*.sh" -o -name "*.ts" | xargs grep -l "validate\|check"

# Look at test files for acceptance criteria
grep -r "describe\|it\(" tests/ | grep -i "format\|schema\|validation"
```

### Step 3: Structure Criteria Output

Document findings as a **validation criteria dict** (JSON or YAML):

```json
{
  "affected_files": [
    "backlog/*.md",
    "schemas/frontmatter/document.json"
  ],
  "validation_commands": {
    "schema": "pnpm run lint:frontmatter",
    "type_check": "pnpm run type-check",
    "format": "pnpm run format:check"
  },
  "constraints": {
    "links": {
      "type": "object",
      "required": ["commits", "pull_requests"],
      "description": "links.commits is array of GitHub commit URLs; links.pull_requests is array of GitHub PR URLs"
    },
    "status": {
      "enum": ["closed", "in-progress", "ready-for-review"],
      "description": "when status=closed, must also include status_reason, completed_date, actual"
    },
    "timestamps": {
      "format": "ISO 8601",
      "example": "2026-02-24T14:30:00.000Z"
    }
  },
  "test_commands": [
    "pnpm run lint:frontmatter",
    "pnpm run format:check"
  ],
  "example_file_location": "backlog/001_github_organization.md",
  "notes": "JSON Schema v7 with strict required fields enforcement for closed items"
}
```

### Step 4: Validate Against Sample

```bash
# Test constraints on ONE file first (before bulk apply)
# This confirms understanding of requirements

# Example for frontmatter:
1. Edit backlog/SAMPLE_001.md to test new format
2. Run pnpm run lint:frontmatter -- backlog/SAMPLE_001.md
3. Confirm output matches expected constraints
4. Document any discrepancies in notes
5. Only then apply to all 9 files
```

## Output Template

When you complete criteria discovery, output:

```markdown
## Validation Criteria Discovered

### Files Affected
- backlog/001_*.md through backlog/011_*.md (9 files)

### Validation Rules
1. **Field: `links.commits`**
   - Type: array
   - Items format: GitHub commit URLs (https://github.com/{owner}/{repo}/commit/{hash})
   - Required: yes (when status=closed)

2. **Field: `status_reason`**
   - Enum: ["completed", "deferred", "cancelled"]
   - Required: yes (when status=closed)
   - Example: "completed"

3. **Field: `completed_date`**
   - Format: ISO 8601 date (YYYY-MM-DD)
   - Required: yes (when status=closed)

### Validation Command
```bash
pnpm run lint:frontmatter
```

### Sample Test File
- Test on: backlog/001_sample_test.md
- Expected result: Must pass `pnpm run lint:frontmatter`
- Failure case: If commits array format is wrong, linter will report pattern mismatch

### Key Insights
- Schema strictly validates arrays for commits/pull_requests
- No object shortcuts: commits must be URL array, not object
- Timestamps must be ISO 8601 format (critical!)
```

## Best Practices

| Practice | Why |
|----------|-----|
| **Discovery before implementation** | Prevents re-doing work multiple times with wrong format |
| **Test on sample file** | Confirms understanding before bulk apply |
| **Document constraints explicitly** | Makes validation rules visible to the team |
| **Capture error messages** | Reuse actual error output as diagnostic reference |
| **Link to schema source** | Make it clear where validation rules come from |

## Example

See [references/example-frontmatter-discovery.md](references/example-frontmatter-discovery.md) for a complete real-world scenario showing discovery workflow for work item frontmatter validation.

## Safety Checks

- **Preserve existing criteria**: Don't override schema; merge new requirements with existing ones
- **All constraints must satisfy**: If field has multiple constraints, document all (not just the first you find)
- **Test failures must be filed**: If sample validation fails, debug before bulk apply; document the fix reason
