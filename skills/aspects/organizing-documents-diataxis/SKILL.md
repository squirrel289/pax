---
name: organizing-documents-diataxis
description: Apply Diataxis framework to organize workflow output into documentation directories. Use to guide skill output placement: inline by default unless user requests file; rationale-heavy content to docs/architecture/; lookup tables and reference guides to docs/reference/. Avoid standalone analysis summaries in docs root. Composable into any analysis or decision-making skill.
---

# Aspect: Organizing Documents (Diataxis)

Reusable aspect providing consistent guidance for placing skill-generated documentation into Diataxis-aligned directories.

## Purpose

Standardize where workflow outputs and analysis results should be placed in the documentation hierarchy, based on the Diátaxis framework categorization.

## When to Use This Aspect

Compose this aspect into any skill that:

- Produces analysis records or comparative decision results
- May generate documentation files
- Needs guidance on organizing outputs by type (explanation, reference, etc.)
- Should follow PAX documentation conventions

## The Diátaxis Framework

PAX documentation uses the [Diátaxis framework](https://diataxis.fr/) to organize content:

| Type | Purpose | Location | Style | Examples |
|------|---------|----------|-------|----------|
| **Tutorials** | Learning-oriented, step-by-step | `docs/guides/` | Hands-on, narrative | Getting started guides |
| **How-to Guides** | Task-oriented, problem-solving | `docs/guides/` | Recipe format, context-specific | Common workflows, checklists |
| **Reference** | Information-oriented, complete | `docs/reference/` | Dry, precise, lookup-oriented | Decision trees, quick refs, schemas, matrices |
| **Explanation** | Understanding-oriented, rationale | `docs/architecture/` | Conceptual, decision drivers, theory | Analysis records, design decisions, reports |

## Output Placement Rules

### Rule 1: Default to Inline Output

Unless the user explicitly requests a file:

- Provide analysis results, recommendations, and decision records **inline** in the chat
- Do not automatically create files in `docs/`
- This respects user intent and AI cost constraints

**Example**:
```
User: "Compare these tools using comparative-analysis"
→ Provide ranking + recommendation inline
→ Do not create docs/architecture/comparison-record.md automatically
```

### Rule 2: Rationale-Heavy Records → `docs/architecture/`

When creating files, place explanation-oriented outputs here:

- Comparative decision records with full rationale
- Analysis reports with decision drivers
- Architecture recommendations with justification
- Evaluation summaries with evidence traces

**Naming**: Use descriptive names with context
- ✅ Good: `pr-workflow-analysis-2026-02.md`, `comparing-parsing-approaches.md`
- ❌ Bad: `analysis.md`, `comparison.md`, `report.md`

**Format**: Include:
- Decision context (what was being decided)
- Evaluation criteria and evidence
- Ranked options with score breakdowns
- Selected recommendation with rationale
- Evidence gaps and follow-up actions

### Rule 3: Reference Tables and Decision Trees → `docs/reference/`

Place information-oriented lookup content here:

- Quick reference tables (tools, features, platform matrix)
- Decision trees (routing, escalation, workflow selection)
- Schema summaries and field catalogs
- Index and lookup tables for complex information

**Naming**: Use short, lookup-friendly names
- ✅ Good: `tool-feature-matrix.md`, `workflow-decision-tree.md`, `api-quick-ref.md`
- ❌ Bad: `tools-comparison-analysis.md` (too detailed for reference)

**Format**: 
- Scannable tables or short descriptions
- No lengthy explanations (move rationale to `docs/architecture/`)
- Cross-references to fuller explanations in `docs/architecture/` if needed

### Rule 4: Avoid Docs Root Analysis Summaries

Do **not** create ephemeral analysis files in the `docs/` root:

- ❌ `docs/ANALYSIS_SUMMARY.md` (ephemeral, clutters docs root)
- ❌ `docs/SKILL_REVIEW_ASSESSMENT.md` (should be in architecture/ or omitted)
- ❌ `docs/DECISION_SUMMARY.md` (belongs in architecture/ or inline)

**Why**: Analysis summaries are output artifacts, not documentation. The docs/ root should contain durable, user-facing documentation.

## Decision Flow

```
User asks for analysis/comparison
    ↓
1. Generate output inline by default
    ↓
2. User asks "save this to a file"?
    ├─ NO  → done (inline output sufficient)
    └─ YES → proceed to step 3
    ↓
3. Is the content primarily rationale/explanation?
    ├─ YES → docs/architecture/{descriptive-name}.md
    └─ NO  → proceed to step 4
    ↓
4. Is the content a lookup table or reference guide?
    ├─ YES → docs/reference/{lookup-name}.md
    └─ NO  → reconsider if file output needed; prefer inline
```

## Examples

### Example 1: Skill Comparison Analysis

**User request**: "Compare skills X, Y, Z using comparative-analysis and save results"

**Output placement**:
- Inline: Ranked list with top recommendation
- If file requested:
  - Summary table → `docs/reference/skill-comparison-matrix.md` (lookup table)
  - Full analysis with evidence → `docs/architecture/skill-selection-analysis.md` (rationale)

### Example 2: Tool Evaluation Record

**User request**: "Evaluate these build tools with scoring and recommendation"

**Output placement**:
- Inline: Recommendation and top option summary
- If file requested:
  - Full comparative decision record → `docs/architecture/build-tool-evaluation-2026-02.md`
  - Quick reference table → `docs/reference/build-tool-feature-matrix.md` (optional, if useful for future lookups)

### Example 3: Workflow Decision

**User request**: "Decide on PR merge strategy"

**Output placement**:
- Inline: Selected strategy and decision rationale
- If file requested:
  - Decision record → `docs/architecture/pr-merge-strategy-decision.md`
  - Decision tree for future use → `docs/reference/pr-strategy-decision-tree.md`

## Composing This Aspect

When a workflow skill uses this aspect, document it in the skill's section:

```markdown
## Output Placement and File Organization (Diataxis)

This skill uses the `aspect-organizing-documents-diataxis` aspect to guide output placement:

- Default to inline output unless the user requests a file.
- Place rationale-heavy records in `docs/architecture/`.
- Place lookup tables or decision trees in `docs/reference/`.
- Avoid creating standalone analysis summaries in the docs root.

See [[skills/aspects/organizing-documents-diataxis/SKILL.md]] for full guidance.
```

Then, when generating outputs:

1. Follow the output placement rules above
2. Name files descriptively (context + date if multiple versions)
3. Structure content according to category (explanation vs. reference)
4. Always provide inline summary; ask before creating files

## Related Documentation

- **Diátaxis Framework**: https://diataxis.fr/
- **File Organization**: [[docs/reference/FILE_ORGANIZATION.md]]
- **Naming Conventions**: [[docs/conventions/NAMING_CONVENTIONS.md]]
- **Frontmatter Specification**: [[docs/conventions/FRONTMATTER_SPECIFICATION.md]]