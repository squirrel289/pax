# File Organization

This document defines the directory structure and file organization rules for the PAX Agent Skills Library to ensure consistent layout, logical grouping, and ease of navigation.

## Directory Structure

```
pax/
├── README.md                          # Repository overview
├── pax.code-workspace                 # VS Code workspace config
├── .github/                           # GitHub automation
│   ├── copilot-instructions.md        # Agent behavior guidelines
│   ├── workflows/                     # CI/CD workflows
│   └── skills/                        # GitHub Copilot Skills integration
├── docs/                              # Documentation
│   ├── conventions/                   # Standards and specifications
│   │   ├── NAMING_CONVENTIONS.md
│   │   ├── FRONTMATTER_SPECIFICATION.md
│   │   └── FILE_ORGANIZATION.md (this file)
│   ├── reference/                     # Reference documentation
│   │   ├── TAG_TAXONOMY.md
│   │   └── SKILLS_INDEX.md (generated)
│   ├── guides/                        # User guides and tutorials
│   │   ├── GETTING_STARTED.md
│   │   └── SKILL_AUTHORING.md
│   └── architecture/                  # Architecture documentation
│       ├── SKILL_COMPOSITION.md
│       └── ASPECTS.md
├── skills/                            # Skill library (primary)
│   ├── README.md                      # Skills overview
│   ├── execution/                     # Execution modes and styles
│   │   ├── README.md
│   │   ├── yolo.md
│   │   └── collaborative.md
│   ├── tools/                         # Tool integration skills
│   │   ├── README.md
│   │   ├── git-commit.md
│   │   └── gh-pr-review.md
│   ├── workflow/                      # Multi-step workflow skills
│   │   ├── README.md
│   │   ├── create-pr.md
│   │   ├── handle-pr-feedback.md
│   │   ├── merge-pr.md
│   │   └── process-pr.md
│   └── aspects/                       # Reusable behavior modifiers
│       ├── README.md
│       ├── aspect-yolo.md
│       └── aspect-collaborative.md
├── schemas/                           # JSON schemas for validation
│   ├── skill-frontmatter.schema.json
│   ├── work-item-frontmatter.schema.json
│   └── README.md
├── templates/                         # Temple templates
│   ├── skill-definition.md.tmpl
│   ├── work-item.md.tmpl
│   └── README.md
├── scripts/                           # Automation scripts
│   ├── validate-naming.sh
│   ├── validate-frontmatter.sh
│   ├── generate-index.sh
│   └── README.md
└── backlog/                           # Work items and planning
    ├── README.md
    ├── 001-feature-name.md
    └── archive/
        └── 000-completed-feature.md
```

---

## Skills Directory (`skills/`)

### Purpose

The `skills/` directory is the **authoritative skill registry** for PAX. All skills must be located here to be discoverable and usable by agents.

### Organization by Category

Skills are organized into **category subdirectories** based on their primary purpose:

#### `execution/` - Execution Modes and Styles

**Purpose**: Define how agents operate (interaction models, execution patterns)

**Characteristics**:
- Modify agent behavior globally
- Typically noun names (modes/styles)
- Often used as aspects for composition

**Examples**:
- `yolo.md` - Autonomous execution mode
- `collaborative.md` - Interactive confirmation mode
- `sequential-execution.md` - Ordered task execution
- `parallel-execution.md` - Concurrent task execution

**File Count**: 4 skills

---

#### `tools/` - Tool Integration Skills

**Purpose**: Wrap external tools/CLIs with agent-friendly interfaces

**Characteristics**:
- Depend on external binaries (`git`, `gh`, `docker`, etc.)
- Action-oriented names: `{tool}-{action}`
- Focus on single-tool operations

**Examples**:
- `git-commit.md` - Git commit automation
- `gh-pr-review.md` - GitHub PR review via CLI
- `docker-build.md` (future)
- `npm-publish.md` (future)

**File Count**: 2 skills

---

#### `workflow/` - Multi-Step Workflow Skills

**Purpose**: Orchestrate complex, multi-step processes

**Characteristics**:
- Compose multiple atomic operations
- Often require other skills (`requires: [...]`)
- Action-oriented names: `{verb}-{noun}[-context]`
- May span multiple tools/systems

**Examples**:
- `create-pr.md` - PR creation workflow
- `handle-pr-feedback.md` - PR feedback resolution
- `merge-pr.md` - PR merge workflow
- `process-pr.md` - End-to-end PR processing
- `create-work-item.md` - Work item creation
- `update-work-item.md` - Work item updates
- `finalize-work-item.md` - Work item completion

**File Count**: 11 skills

---

#### `aspects/` - Reusable Behavior Modifiers

**Purpose**: Provide composable behaviors for skill augmentation

**Characteristics**:
- Prefixed with `aspect-` (see [[docs/conventions/NAMING_CONVENTIONS.md]])
- Designed for composition (`git-commit+aspect-yolo`)
- Define specific behavior transformations

**Examples**:
- `aspect-yolo.md` - Auto-execution behavior
- `aspect-collaborative.md` - Interactive behavior

**File Count**: 2 skills

**Rules**:
- Aspects **must** be prefixed with `aspect-`
- Aspects **must** be located in `skills/aspects/`
- Aspects should be reusable across multiple base skills

---

### Category README Files

Each category directory **must** have a `README.md` file:

**Purpose**:
- Describe category intent and scope
- List skills in the category
- Provide usage examples

**Template**:

```markdown
# {Category Name} Skills

{Brief description of category purpose}

## Skills in This Category

- **[skill-name](skill-name.md)**: Brief description
- **[another-skill](another-skill.md)**: Brief description

## When to Use

{Guidance on when to use skills in this category}

## Examples

{Usage examples}

## See Also

- [[other-category]]
- [[docs/guides/GETTING_STARTED.md]]
```

---

## Documentation Directory (`docs/`)

### Purpose

The `docs/` directory contains all documentation for PAX, organized into logical subdirectories.

### Subdirectories

#### `conventions/` - Standards and Specifications

**Purpose**: Define rules, formats, and standards for skill authoring

**Files**:
- `NAMING_CONVENTIONS.md` - Naming rules for files, skills, aspects
- `FRONTMATTER_SPECIFICATION.md` - YAML frontmatter schema
- `FILE_ORGANIZATION.md` (this file) - Directory structure

**Target Audience**: Skill authors, contributors

---

#### `reference/` - Reference Documentation

**Purpose**: Comprehensive reference materials, indices, and lookups

**Files**:
- `TAG_TAXONOMY.md` - Standardized tags catalog
- `SKILLS_INDEX.md` - Auto-generated skills index (all categories)
- `API_REFERENCE.md` (future)

**Target Audience**: All users

---

#### `guides/` - User Guides and Tutorials

**Purpose**: Step-by-step instructions and learning materials

**Files**:
- `GETTING_STARTED.md` - Quickstart guide for new users
- `SKILL_AUTHORING.md` - How to create new skills
- `COMPOSITION_TUTORIAL.md` - Aspect composition guide
- `TROUBLESHOOTING.md` (future)

**Target Audience**: New users, skill authors

---

#### `architecture/` - Architecture Documentation

**Purpose**: System design, patterns, and architectural decisions

**Files**:
- `SKILL_COMPOSITION.md` - Composition patterns and mechanics
- `ASPECTS.md` - Aspect system design
- `DECISION_POINT_ENCODING.md` - Decision tree patterns

**Target Audience**: Advanced users, architects, maintainers

---

### Documentation Conventions

**Diátaxis Framework**:

PAX documentation follows the [Diátaxis framework](https://diataxis.fr/):

| Type | Purpose | Location | Style |
|------|---------|----------|-------|
| **Tutorials** | Learning-oriented | `docs/guides/` | Step-by-step, hands-on |
| **How-To Guides** | Task-oriented | `docs/guides/` | Problem-solving recipes |
| **Reference** | Information-oriented | `docs/reference/` | Dry, precise, complete |
| **Explanation** | Understanding-oriented | `docs/architecture/` | Concepts, rationale, theory |

**Linking**:
- Use wikilinks for internal references: `[[NAMING_CONVENTIONS.md]]`
- Use relative Markdown links for external references: `[GitHub](https://github.com)`

**Frontmatter**:
- All documentation files **must** have frontmatter (Phase 3)
- Use `doc-vader` schemas for validation (Phase 3)

---

## Schemas Directory (`schemas/`)

### Purpose

The `schemas/` directory contains JSON Schema definitions for validation:

**Files**:
- `skill-frontmatter.schema.json` - Validates skill YAML frontmatter
- `work-item-frontmatter.schema.json` - Validates work item frontmatter
- `README.md` - Schema usage documentation

**Usage**:

```bash
# Validate skill frontmatter
./scripts/validate-frontmatter.sh skills/tools/git-commit.md

# Validate work item
./scripts/validate-frontmatter.sh backlog/001-feature.md
```

**See**: [[backlog/phase-2-schema-infrastructure.md]]

---

## Templates Directory (`templates/`)

### Purpose

The `templates/` directory contains Temple templates for code generation:

**Files**:
- `skill-definition.md.tmpl` - Skill file template
- `work-item.md.tmpl` - Work item template
- `README.md` - Template usage documentation

**Usage**:

```bash
# Generate new skill from template
temple render --template templates/skill-definition.md.tmpl \
  --data '{"name": "docker-build", "category": "tools"}' \
  --output skills/tools/docker-build.md
```

**See**: [[backlog/phase-2-template-creation.md]]

---

## Scripts Directory (`scripts/`)

### Purpose

The `scripts/` directory contains automation scripts for validation, generation, and maintenance:

**Files**:
- `validate-naming.sh` - Check filename conventions
- `validate-frontmatter.sh` - Validate YAML frontmatter against schema
- `generate-index.sh` - Generate SKILLS_INDEX.md
- `link-validation.sh` - Check wikilink integrity (Phase 4)
- `README.md` - Script usage documentation

**CI Integration**: All scripts must be runnable in CI

---

## Backlog Directory (`backlog/`)

### Purpose

The `backlog/` directory contains work items for feature development, improvements, and technical debt.

### File Naming

**Format**: `{issue-id}-{slug}.md`

**Examples**:
- `001-frontmatter-schema-validation.md`
- `042-add-docker-build-skill.md`
- `099-refactor-pr-workflows.md`

**Rules**:
- Zero-padded issue IDs (3 digits)
- Kebab-case slugs (see [[docs/conventions/NAMING_CONVENTIONS.md]])
- `.md` extension

### Frontmatter

Work items **must** have frontmatter:

```yaml
---
id: 001
title: Implement Frontmatter Schema Validation
status: in-progress
priority: high
estimated-hours: 8
actual-hours: 6
created: 2026-02-10
updated: 2026-02-15
tags: [tooling, validation, schema]
---
```

**See**: [[docs/conventions/FRONTMATTER_SPECIFICATION.md]] (work-item schema)

### Archive

Completed work items are moved to `backlog/archive/`:

```bash
git mv backlog/001-feature.md backlog/archive/001-feature.md
```

**See**: [[.github/skills/finalize-work-item/SKILL.md]]

---

## GitHub Directory (`.github/`)

### Purpose

The `.github/` directory contains GitHub-specific configuration and automation.

### Key Files

- **`copilot-instructions.md`**: Agent behavior guidelines and project context
- **`workflows/`**: CI/CD workflows (lint, test, deploy)
- **`skills/`**: Copilot Skills integration (symlink to `skills/` or copy)

---

## File Organization Rules

### Rule 1: One Skill Per File

**Each skill must be in its own Markdown file**: No combining multiple skills in one file.

❌ **Bad**:
```
skills/tools/git-tools.md
  - Contains: git-commit, git-push, git-pull
```

✅ **Good**:
```
skills/tools/git-commit.md
skills/tools/git-push.md
skills/tools/git-pull.md
```

**Rationale**: Enables skill-level versioning, composition, and discovery

---

### Rule 2: Category from Directory

**Skill category is determined by directory location**, not frontmatter.

❌ **Bad**:
```yaml
# File: skills/workflow/git-commit.md
---
name: git-commit
category: tools  # ❌ Conflicts with directory
---
```

✅ **Good**:
```
# File: skills/tools/git-commit.md
---
name: git-commit
# Category inferred from directory: tools
---
```

**Rationale**: Single source of truth (directory structure)

---

### Rule 3: Aspects in `aspects/`

**All aspect skills must be in `skills/aspects/` and prefixed with `aspect-`**.

❌ **Bad**:
```
skills/execution/yolo.md  # Should be aspect
skills/aspects/yolo.md     # Missing prefix
```

✅ **Good**:
```
skills/aspects/aspect-yolo.md
```

**Rationale**: Clear separation, easy composition detection

---

### Rule 4: No Nested Categories

**Skills directories are flat (one level deep): no subcategories**.

❌ **Bad**:
```
skills/tools/git/commit.md
skills/tools/git/push.md
```

✅ **Good**:
```
skills/tools/git-commit.md
skills/tools/git-push.md
```

**Rationale**: Simplicity, avoid ambiguous categorization

**Exception**: If tool-specific subcategories are needed (e.g., 20+ git skills), propose as Phase 10 enhancement.

---

### Rule 5: README Files Are Required

**Every category directory must have a `README.md`**.

❌ **Bad**:
```
skills/tools/
  git-commit.md
  gh-pr-review.md
  # No README.md
```

✅ **Good**:
```
skills/tools/
  README.md          # ✅ Present
  git-commit.md
  gh-pr-review.md
```

**Rationale**: Category documentation and skill lists

---

## Path References

### Absolute Paths

When referencing files from **outside the repository**, use absolute paths:

```bash
/Users/macos/dev/pax/skills/tools/git-commit.md
```

### Relative Paths

When referencing files **within the repository**, use relative paths:

From `skills/tools/git-commit.md`:
```markdown
See also: [PR Workflow](../workflow/create-pr.md)
```

### Wikilinks

For **documentation references**, use wikilinks (Phase 4 migration):

```markdown
See [[docs/conventions/NAMING_CONVENTIONS.md]] for naming rules.
```

**Rationale**: Wikilinks are backlink-aware and easier to refactor

---

## Adding New Skills

### Process

1. **Determine category**: Where does this skill belong?
   - Execution mode? → `skills/execution/`
   - Tool integration? → `skills/tools/`
   - Workflow orchestration? → `skills/workflow/`
   - Aspect/modifier? → `skills/aspects/`

2. **Choose filename**: Follow [[docs/conventions/NAMING_CONVENTIONS.md]]
   - Kebab-case
   - Action-oriented (verbs)
   - Prefix `aspect-` for aspects

3. **Create skill file**:
   ```bash
   touch skills/{category}/{skill-name}.md
   ```

4. **Add frontmatter**: Follow [[docs/conventions/FRONTMATTER_SPECIFICATION.md]]
   - Required: `name`, `description`
   - Recommended: `tags`, `triggers`, `version`, `status`

5. **Write skill content**: See [[docs/guides/SKILL_AUTHORING.md]]

6. **Update category README**: Add skill to category list

7. **Validate**:
   ```bash
   ./scripts/validate-naming.sh skills/{category}/{skill-name}.md
   ./scripts/validate-frontmatter.sh skills/{category}/{skill-name}.md
   ```

8. **Regenerate index**:
   ```bash
   ./scripts/generate-index.sh
   ```

---

## Adding New Categories

### When to Add a New Category

- **5+ skills** share a common theme not covered by existing categories
- Skills don't fit cleanly into `execution`, `tools`, `workflow`, or `aspects`
- Clear category purpose and boundaries

### Process

1. **Propose category**:
   - Create work item: `backlog/{id}-add-{category}-category.md`
   - Justify need and describe scope

2. **Create directory**:
   ```bash
   mkdir skills/{category-name}
   ```

3. **Add README**:
   ```bash
   cat > skills/{category-name}/README.md <<EOF
   # {Category Name} Skills
   
   {Purpose and scope}
   
   ## Skills in This Category
   
   _(None yet)_
   
   ## See Also
   
   - [[skills/README.md]]
   EOF
   ```

4. **Update main README**: Add category to `skills/README.md`

5. **Update documentation**: Add to [[docs/reference/FILE_ORGANIZATION.md]] (this file)

---

## Deprecated Structures

### Legacy Locations

The following directory structures are **deprecated** and should not be used:

❌ **Deprecated**:
```
.github/skills/         # Old Copilot Skills integration location
pax/skills_old/         # Pre-refactor structure
docs/old/               # Unorganized documentation
```

✅ **Current**:
```
skills/                 # All skills here
docs/                   # All documentation here
.github/skills/         # Symlink or copy from skills/
```

---

## Rationale

### Why This Structure?

1. **Flat is Better Than Nested**: One level of categories avoids ambiguity
2. **Category from Directory**: Single source of truth for categorization
3. **README per Category**: Self-documenting structure
4. **Consistent Naming**: Enablestooling and automation
5. **Clear Separation**: Docs, skills, schemas, templates are distinct

### Design Principles

- **Discoverability**: Clear directory names, logical grouping
- **Maintainability**: Flat structure, no deep nesting
- **Automation-Friendly**: Consistent patterns enable scripting
- **Documentation-Driven**: Every directory has a README

---

## References

### Internal References

- **Naming Conventions**: [[docs/conventions/NAMING_CONVENTIONS.md]]
- **Frontmatter Specification**: [[docs/conventions/FRONTMATTER_SPECIFICATION.md]]
- **Skills Index**: [[docs/reference/SKILLS_INDEX.md]]
- **Skill Authoring Guide**: [[docs/guides/SKILL_AUTHORING.md]]

### External References

- [Diátaxis Documentation Framework](https://diataxis.fr/)
- [GitHub Repository Best Practices](https://github.com/jehna/readme-best-practices)

---

**Last Updated**: February 16, 2026  
**Status**: Active Specification (Enforced)  
**Version**: 1.0.0
