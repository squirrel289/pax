# Frontmatter Specification

This document defines the YAML frontmatter structure for PAX skill files. Frontmatter provides structured metadata that enables skill discovery, composition, validation, and tooling integration.

## Format

**Location**: First content block in Markdown file  
**Delimiter**: Triple-dash (`---`)  
**Syntax**: YAML

**Template**:

```yaml
---
# Required fields
name: skill-name
description: |
  Brief description of what the skill does.

# Optional fields (context)
category: execution
tags: [git, automation, workflow]
triggers: ["commit", "save changes"]
version: 1.0.0
status: stable

# Optional fields (composition)
composed-from: base-skill+aspect1+aspect2
requires: [other-skill-1, other-skill-2]
provides: [capability-1, capability-2]

# Optional fields (implementation)
tools: [git, gh]
platforms: [linux, macos, windows]
min-copilot-version: 1.210.0

# Optional fields (documentation)
author: GitHub Copilot Team
license: MIT
see-also: [related-skill-1, related-skill-2]
---

# Skill content starts here
```

---

## Required Fields

### `name`

**Type**: String  
**Format**: kebab-case (see [[docs/conventions/NAMING_CONVENTIONS.md]])  
**Purpose**: Unique identifier for the skill

**Rules**:
- Must match filename (without `.md` extension)
- Lowercase only
- Hyphens for word separation
- No spaces, underscores, or special characters
- Maximum 50 characters

**Examples**:

```yaml
# ✅ Valid
name: git-commit

# ❌ Invalid
name: Git Commit        # Spaces
name: git_commit        # Underscores
name: gitCommit         # camelCase
name: different-name    # Doesn't match filename
```

**Validation**: Must match filename and conform to naming conventions

---

### `description`

**Type**: String (multiline allowed with `|` or `>`)  
**Purpose**: Brief human-readable explanation of skill functionality

**Rules**:
- 1-3 sentences maximum (concise overview)
- Should answer: "What does this skill do?"
- Use active voice and action verbs
- Avoid redundancy with skill name
- Maximum 500 characters

**Examples**:

```yaml
# ✅ Good
description: |
  Execute git commit with conventional commit message analysis,
  intelligent staging, and message generation. Supports auto-detecting
  type and scope from changes.

# ❌ Too vague
description: Commits changes

# ❌ Too long (should be in skill body)
description: |
  This skill provides comprehensive git commit functionality including
  auto-detection of commit type and scope, conventional commit message
  generation from diff context, interactive commit workflow with optional
  overrides, intelligent file staging for logical grouping, pre-commit
  hook integration, commit message validation, and support for co-authored
  commits. It also handles edge cases like empty commits...
```

**Validation**: Required, non-empty, under 500 characters

---

## Optional Context Fields

### `category`

**Type**: String  
**Purpose**: Primary classification for skill organization  
**Default**: Inferred from file path if not specified

**Allowed Values**:
- `execution` - How agents operate (mode/style)
- `tools` - Integration with external tools
- `workflow` - Multi-step processes
- `aspects` - Reusable behavior modifiers
- (Custom categories allowed with documentation)

**Examples**:

```yaml
# ✅ Valid
category: workflow

# ⚠️ Will be inferred from path if omitted
# File: skills/workflow/create-pr.md → category: workflow
```

**Validation**: Optional, must match directory if specified

---

### `tags`

**Type**: Array of strings  
**Purpose**: Multi-dimensional classification for search and filtering

**Rules**:
- 3-7 tags recommended (avoid over-tagging)
- Use existing tags when possible (see [[docs/reference/TAG_TAXONOMY.md]])
- Lowercase, kebab-case for multi-word tags
- No redundant tags (e.g., don't tag `git` if category is `tools/git`)

**Common Tags**:
- **Tools**: `git`, `github`, `npm`, `docker`, `kubernetes`
- **Languages**: `python`, `typescript`, `bash`, `yaml`
- **Domains**: `workflow`, `automation`, `testing`, `deployment`
- **Behaviors**: `interactive`, `autonomous`, `validation`

**Examples**:

```yaml
# ✅ Good
tags: [git, conventional-commits, automation]

# ❌ Over-tagging
tags: [git, github, commit, commits, committing, version-control, vcs, automation, auto, automatic, workflow, process]

# ❌ Redundant
category: tools
tags: [tools, git]  # 'tools' redundant with category
```

**Validation**: Optional, must be array of non-empty strings

---

### `triggers`

**Type**: Array of strings  
**Purpose**: User phrases that should invoke this skill

**Rules**:
- Natural language phrases (how users describe intent)
- 3-5 triggers recommended
- Lowercase preferred
- Avoid overly generic triggers

**Examples**:

```yaml
# git-commit skill
triggers: ["commit", "save changes", "make a commit", "/commit"]

# create-pr skill
triggers: ["create pr", "open pull request", "submit for review"]

# yolo skill
triggers: ["just do it", "skip confirmations", "autonomous mode"]
```

**Validation**: Optional, must be array of non-empty strings

---

### `version`

**Type**: String (semver)  
**Purpose**: Track skill evolution for compatibility

**Format**: `MAJOR.MINOR.PATCH`

**Semantic Versioning**:
- **MAJOR**: Breaking changes (interface changes)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Examples**:

```yaml
# ✅ Valid
version: 1.2.3
version: 0.1.0  # Pre-release

# ❌ Invalid
version: 1.2     # Missing patch
version: v1.2.3  # Don't include 'v' prefix
version: latest  # Not semver
```

**Validation**: Optional, must match semver pattern if specified

---

### `status`

**Type**: String (enum)  
**Purpose**: Indicate skill maturity and stability

**Allowed Values**:
- `draft` - Work in progress, not yet functional
- `experimental` - Functional but API may change
- `stable` - Production-ready, API frozen
- `deprecated` - Replaced or obsolete, will be removed

**Examples**:

```yaml
# ✅ Valid
status: stable

# ⚠️ Default if not specified
# status: stable (assumed)
```

**Lifecycle**:
1. `draft` → Author is developing
2. `experimental` → Testing with users, gathering feedback
3. `stable` → API frozen, widely used
4. `deprecated` → Scheduled for removal

**Validation**: Optional, must be one of allowed values

---

## Optional Composition Fields

### `composed-from`

**Type**: String  
**Purpose**: Record aspect composition relationship  
**Format**: `{base-skill}+{aspect1}+{aspect2}`

**Rules**:
- Use `+` to separate base skill and aspects
- List base skill first, then aspects
- All components must exist as separate skills
- Filename should reflect composition (e.g., `git-commit-yolo.md`)

**Examples**:

```yaml
# Simple composition (1 aspect)
composed-from: git-commit+yolo

# Multiple aspects
composed-from: create-pr+yolo+sequential-execution

# ❌ Invalid
composed-from: git-commit, yolo    # Use + not comma
composed-from: yolo+git-commit     # Base skill must be first
```

**Validation**: Optional, must reference existing skills if specified

---

### `requires`

**Type**: Array of strings  
**Purpose**: Declare hard dependencies on other skills

**Rules**:
- List skills that **must** be present for this skill to function
- Use skill names (not filenames)
- Avoid circular dependencies

**Examples**:

```yaml
# PR workflow requires base operations
requires: [create-pr, merge-pr]

# Sequential execution requires task breakdown
requires: [task-planner]
```

**Use Cases**:
- Composed skills requiring base skills
- Workflow skills requiring atomic operations
- Integration skills requiring tool wrappers

**Validation**: Optional, must reference existing skills

---

### `provides`

**Type**: Array of strings  
**Purpose**: Declare capabilities this skill offers (for dependency resolution)

**Rules**:
- Capability strings (not skill names)
- Use kebab-case
- One skill can provide multiple capabilities

**Examples**:

```yaml
# git-commit provides
provides: [commit-creation, conventional-commits]

# merge-pr provides
provides: [pr-merge, branch-cleanup]
```

**Use Cases**:
- Abstract interfaces: "Any skill providing `commit-creation`"
- Dependency resolution: Find skill providing `pr-merge`
- Feature detection: Check if `conventional-commits` is available

**Validation**: Optional, must be array of non-empty strings

---

## Optional Implementation Fields

### `tools`

**Type**: Array of strings  
**Purpose**: List external tools/binaries required for skill execution

**Rules**:
- Tool names (not paths)
- Lowercase
- Include version constraints if needed (future)

**Examples**:

```yaml
# CLI tools
tools: [git, gh]

# Multiple tools
tools: [docker, kubectl, helm]

# Future: version constraints
tools: 
  - git: ">=2.40"
  - gh: "^2.0.0"
```

**Use Cases**:
- Pre-flight checks: "Is `gh` installed?"
- Documentation: "This skill requires Docker"
- Environment setup: "Install `kubectl` to use this skill"

**Validation**: Optional, must be array of non-empty strings

---

### `platforms`

**Type**: Array of strings  
**Purpose**: Declare OS/platform compatibility

**Allowed Values**:
- `linux`
- `macos`
- `windows`
- `web` (browser-based)

**Examples**:

```yaml
# Cross-platform
platforms: [linux, macos, windows]

# Unix-only
platforms: [linux, macos]

# Windows-specific
platforms: [windows]
```

**Default**: All platforms if not specified

**Validation**: Optional, must be subset of allowed values

---

### `min-copilot-version`

**Type**: String (semver)  
**Purpose**: Specify minimum GitHub Copilot version required

**Format**: `MAJOR.MINOR.PATCH`

**Examples**:

```yaml
# Requires Copilot Chat API features
min-copilot-version: 1.210.0

# Latest skills API
min-copilot-version: 1.220.0
```

**Validation**: Optional, must be valid semver

---

## Optional Documentation Fields

### `author`

**Type**: String  
**Purpose**: Credit skill creator or maintainer

**Examples**:

```yaml
author: GitHub Copilot Team
author: Jane Doe <jane@example.com>
author: acme-corp
```

**Validation**: Optional, free-form string

---

### `license`

**Type**: String  
**Purpose**: Specify skill licensing

**Common Values**:
- `MIT`
- `Apache-2.0`
- `GPL-3.0`
- `proprietary`

**Examples**:

```yaml
license: MIT
```

**Default**: Inherits from repository license if not specified

**Validation**: Optional, SPDX identifier preferred

---

### `see-also`

**Type**: Array of strings  
**Purpose**: Reference related skills for discovery

**Rules**:
- Skill names or wikilink format
- 3-5 related skills recommended

**Examples**:

```yaml
# Skill names
see-also: [create-pr, merge-pr, handle-pr-feedback]

# Wikilink format (for doc-vader integration)
see-also: 
  - "[[create-pr]]"
  - "[[merge-pr]]"
  - "[[handle-pr-feedback]]"
```

**Validation**: Optional, must be array of non-empty strings

---

## Frontmatter Anti-Patterns

### Anti-Pattern 1: Unsupported Fields

❌ **Bad** (fields removed during Phase 1 cleanup):

```yaml
---
name: git-commit
category: tools      # ❌ Use directory structure instead
aliases: [commit]    # ❌ Not yet supported
keywords: [git]      # ❌ Use 'tags' instead
---
```

✅ **Good**:

```yaml
---
name: git-commit
tags: [git, automation]
---
```

**Why**: Stick to supported fields; proposed fields need implementation

---

### Anti-Pattern 2: Redundant Information

❌ **Bad**:

```yaml
---
name: git-commit
description: This is the git-commit skill that commits changes to git
filename: git-commit.md
path: skills/tools/git-commit.md
---
```

✅ **Good**:

```yaml
---
name: git-commit
description: |
  Execute git commit with conventional commit message analysis
  and intelligent staging.
---
```

**Why**: Name should match filename (enforced), path is discoverable

---

### Anti-Pattern 3: Over-Tagging

❌ **Bad**:

```yaml
tags: [git, github, commit, commits, committing, version-control, vcs, scm, repository, repo, automation, auto, automatic, workflow, process, tool, development, dev, coding]
```

✅ **Good**:

```yaml
tags: [git, conventional-commits, automation]
```

**Why**: Too many tags reduce discoverability (noise)

---

### Anti-Pattern 4: Missing Required Fields

❌ **Bad**:

```yaml
---
category: tools
tags: [git]
---

# Git Commit Skill
...
```

✅ **Good**:

```yaml
---
name: git-commit
description: Execute git commit with conventional commit message analysis
---

# Git Commit Skill
...
```

**Why**: `name` and `description` are required for skill registration

---

## Validation

### Schema Validation

**Proposed**: JSON Schema for frontmatter (Phase 2)

**Location**: `schemas/skill-frontmatter.schema.json`

**Usage**:

```bash
# Validate all skills
./scripts/validate-frontmatter.sh skills/**/*.md

# Example output:
# ✅ skills/tools/git-commit.md
# ❌ skills/workflow/create-pr.md: Missing required field 'description'
# ❌ skills/execution/yolo.md: Invalid field 'category' (use directory instead)
```

**Implementation**: See [[backlog/frontmatter-schema-validation.md]]

---

### Manual Review Checklist

Before committing a skill file:

- [ ] **Required fields present**: `name`, `description`
- [ ] **Name matches filename**: `name: git-commit` → `git-commit.md`
- [ ] **Description is concise**: 1-3 sentences, under 500 chars
- [ ] **Tags are relevant**: 3-7 tags, no over-tagging
- [ ] **Version follows semver**: If specified
- [ ] **Status is valid**: `draft`, `experimental`, `stable`, or `deprecated`
- [ ] **No unsupported fields**: Check against this spec
- [ ] **YAML is valid**: No syntax errors

---

## Migration Guide

### Phase 1 Cleanup (Current)

**Removing Unsupported Fields**:

The following fields were found in existing skills but are not yet supported by tooling:

| Field | Action | Replacement |
|-------|--------|-------------|
| `category` | Remove | Use directory structure |
| `aliases` | Remove | Planned for future (Phase 9) |
| `keywords` | Rename | Use `tags` instead |
| `composed-from` | Keep | ✅ Supported (composition) |

**Example Migration**:

**Before**:
```yaml
---
name: git-commit
category: tools
keywords: [git, commit]
aliases: [commit, save]
---
```

**After**:
```yaml
---
name: git-commit
tags: [git, conventional-commits, automation]
---
```

**Files to Update** (11 files identified):
- See [[backlog/phase-1-frontmatter-cleanup.md]]

---

### Future Enhancements

**Planned for Phase 9**:

- **Aliasing**: `aliases: [short-name, alternative-name]`
- **Versioning**: Tool version constraints (`tools: {git: ">=2.40"}`)
- **Contexts**: Execution contexts (`contexts: [vscode, cli, web]`)
- **Localization**: `i18n: {ja: {description: "..."}, es: {...}}`

---

## Examples by Skill Type

### Execution Skills

```yaml
---
name: yolo
description: |
  Autonomous "just do it" interaction mode - execute actions without
  confirmation or human intervention.
category: execution
tags: [autonomous, automation, mode]
status: stable
version: 1.0.0
triggers: ["just do it", "no confirmations", "yolo mode"]
---
```

---

### Tool Integration Skills

```yaml
---
name: git-commit
description: |
  Execute git commit with conventional commit message analysis,
  intelligent staging, and message generation.
category: tools
tags: [git, conventional-commits, automation]
tools: [git]
platforms: [linux, macos, windows]
triggers: ["commit", "/commit", "save changes"]
status: stable
version: 1.2.0
see-also: [git-push, create-pr]
---
```

---

### Workflow Skills

```yaml
---
name: create-pr
description: |
  Create a pull request from a feature branch with work item metadata.
  Supports PR template auto-population and work item linking.
category: workflow
tags: [github, pull-request, workflow]
tools: [gh, git]
requires: [git-commit]
provides: [pr-creation]
triggers: ["create pr", "open pull request"]
status: stable
version: 1.1.0
see-also: [merge-pr, handle-pr-feedback]
---
```

---

### Aspect Skills

```yaml
---
name: aspect-yolo
description: |
  Auto-execution behavior modifier for composing autonomous skills.
  Skips confirmations and proceeds with actions.
category: aspects
tags: [aspect, behavior, autonomous]
provides: [autonomous-execution]
status: experimental
version: 0.2.0
---
```

---

### Composed Skills

```yaml
---
name: git-commit-yolo
description: |
  Autonomous git commit workflow - stages changes, generates commit
  message, and commits without confirmation.
composed-from: git-commit+aspect-yolo
category: tools
tags: [git, autonomous, composed]
tools: [git]
requires: [git-commit, aspect-yolo]
status: experimental
version: 0.1.0
---
```

---

## References

### Internal References

- **Naming Conventions**: [[docs/conventions/NAMING_CONVENTIONS.md]]
- **File Organization**: [[docs/reference/FILE_ORGANIZATION.md]]
- **Skill Composition**: [[docs/SKILL_COMPOSITION.md]]
- **Tag Taxonomy**: [[docs/reference/TAG_TAXONOMY.md]] (to be created)

### External References

- [YAML Specification](https://yaml.org/spec/1.2.2/)
- [Semantic Versioning](https://semver.org/)
- [JSON Schema](https://json-schema.org/)
- [SPDX License List](https://spdx.org/licenses/)

---

**Last Updated**: February 16, 2026  
**Status**: Active Specification (Enforced)  
**Version**: 1.0.0
