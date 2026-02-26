# Aspect Skills

Reusable behavioral patterns that can be composed into agent guidance, skills and direct user prompts.

## Overview

Aspect skills provide cross-cutting concerns and standardized behaviors that multiple skills can reference. They define contracts, patterns, and best practices that guide how skills operate.

## Skills in This Category

### interaction-modes

**Purpose**: Standardize how skills pause, prompt for choices, and resume execution based on user input.

**Modes**:

- **yolo**: Autonomous execution, minimal prompts
- **collaborative**: Interactive execution, prompts for decisions

**Files**: `ASPECT.md`, decision schema, shell scripts

**See**: [interaction-modes/ASPECT.md](interaction-modes/ASPECT.md)

---

### guarding-branches

**Purpose**: Protect main branch during merge operations through conflict detection and safety checks.

**Key Checks**:

- Merge conflict detection
- Type/export conflict scanning
- Unintended file deletion detection
- Branch protection rule validation

**Used By**: `merge-pr` Phase 2 (Pre-Merge Verification)

**See**: [guarding-branches/SKILL.md](guarding-branches/SKILL.md)

---

### prevalidating-bulk-operations

**Purpose**: Route bulk file operations (3+ similar files) to systematic validation pattern or direct implementation.

**Decision Framework**: Evaluates file count, schema discoverability, and operation type to determine routing.

**Outputs**: Routing decision (PATTERN_REQUIRED / PATTERN_CONDITIONAL / DIRECT) + evidence

**Used By**: `executing-backlog`, `discover-validation-criteria`

**See**: [prevalidating-bulk-operations/SKILL.md](prevalidating-bulk-operations/SKILL.md)

---

### organizing-documents-diataxis

**Purpose**: Apply Diataxis framework to organize skill outputs into documentation directories.

**Key Principles**:

- Default to inline output unless user requests file
- Place rationale-heavy records in `docs/architecture/` (Explanation)
- Place lookup tables or decision trees in `docs/reference/` (Reference)
- Avoid standalone analysis summaries in docs root

**Diataxis Categories**:

| Type          | Purpose                | Location             |
| ------------- | ---------------------- | -------------------- |
| Tutorials     | Learning-oriented      | `docs/guides/`       |
| How-to Guides | Task-oriented          | `docs/guides/`       |
| Reference     | Information-oriented   | `docs/reference/`    |
| Explanation   | Understanding-oriented | `docs/architecture/` |

**Used By**: `skill-reviewer`, `comparative-analysis`, `comparative-decision-review`, `comparative-decision-analysis`, `hybrid-decision-analysis`, `hybrid-decision-analysis.v1`

**See**: [organizing-documents-diataxis/SKILL.md](organizing-documents-diataxis/SKILL.md)

---

## When to Use Aspect Skills

Aspect skills are designed for composition. Use them when:

- Multiple workflow skills need the same behavioral pattern
- Standardizing a cross-cutting concern (output placement, interaction mode, validation)
- Defining contracts for skill behavior
- Avoiding duplication across workflow and tool skills

## Composing Aspect Skills

To compose an aspect into a workflow skill:

1. Reference the aspect in the workflow skill's documentation
2. Follow the aspect's contract and guidelines
3. Link to the aspect's SKILL.md for full details

Example reference pattern:

```markdown
## Output Placement and File Organization

This skill uses the `organizing-documents-diataxis` aspect (see [[skills/aspects/organizing-documents-diataxis/SKILL.md]]) for output placement guidance:

- Default to inline output unless user requests a file
- Place rationale-heavy records in `docs/architecture/`
- Place lookup tables or decision trees in `docs/reference/`
- Avoid creating standalone analysis summaries in docs root
```

## Naming Conventions

- Aspect skill directory names should be descriptive and action-oriented
- Follow kebab-case naming: `interaction-modes`, `prevalidating-bulk-operations`
- File name is typically `SKILL.md` or `ASPECT.md` depending on complexity
- Include `references/`, `scripts/`, or `assets/` subdirectories as needed

## See Also

- [[../workflow/README.md]] - Workflow Skills
- [[../execution/README.md]] - Execution Skills
- [[../tools/README.md]] - Tool Skills
- [[../../docs/conventions/NAMING_CONVENTIONS.md]] - Naming Conventions
- [[../../docs/ASPECTS.md]] - Aspects Documentation
