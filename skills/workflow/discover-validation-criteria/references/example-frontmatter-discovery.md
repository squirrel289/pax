# Example: Work Item Frontmatter Discovery

Real scenario from `templjs` Phase 2 closeout showing complete discovery workflow.

## Scenario

Closing 9 work items (WI-001 through WI-011) with new frontmatter fields.

## Discovery Process

```bash
# 1. Find schema
find . -name "*frontmatter*.json" -o -name "*work*.json" | grep schema
# → schemas/frontmatter/work-item.json

# 2. Read schema, extract requirements for closed status
cat schemas/frontmatter/work-item.json | jq '.properties | keys[]'
# → [ "id", "type", "title", "description", "status", "status_reason", "links", ... ]

# 3. Check "closed" status constraints
cat schemas/frontmatter/work-item.json | jq 'select(.properties.status.enum[] == "closed")'
# → Shows: "when status=closed, then required: [...links, actual, completed_date, ...]"

# 4. Extract links constraints
cat schemas/frontmatter/work-item.json | jq '.properties.links.properties.commits'
# → Shows: "type: array, items.format: URL pattern, pattern: '^https://github.com/...'"

# 5. Test on sample
cp backlog/001_*.md backlog/SAMPLE_001.md
# Edit SAMPLE_001.md with new format
pnpm run lint:frontmatter -- backlog/SAMPLE_001.md
# ✅ Passes → proceed to all 9 files
# ❌ Fails → refine format based on error message, test again

# 6. Create discovery output doc
cat > validation_criteria.json << 'EOF'
{
  "field": "links.commits",
  "type": "array",
  "items_type": "string",
  "format": "GitHub commit URL",
  "pattern": "^https://github.com/templjs/templ.js/commit/[0-9a-f]{7}$",
  "example": "https://github.com/templjs/templ.js/commit/22ae441",
  "required": true
}
EOF
```

## Result

Instead of 4 failed validation attempts:

- 1 schema read → 1 test → 1 bulk apply ✅

## Key Insights

- **Pattern requirement**: Schema enforced exact GitHub URL pattern with 7-char commit hash
- **Array constraint**: Must be array of strings, not object with URLs
- **Sample testing**: Testing on 1 file before 9 prevented 36 total failed validation attempts (4 iterations × 9 files)
