# Naming Conventions

This document establishes naming standards for all files, directories, skills, and aspects in the PAX Agent Skills Library to ensure consistency, discoverability, and compatibility with tooling.

## File Naming Rules

### Skill Files

**Format**: `{skill-name}.md`

**Rules**:
- Use **kebab-case** (lowercase with hyphens)
- No underscores, no spaces, no camelCase
- Descriptive, action-oriented names
- Maximum 50 characters (prefer shorter)

**Examples**:
- ✅ `git-commit.md`
- ✅ `create-work-item.md`
- ✅ `merge-pr.md`
- ❌ `git_commit.md` (underscores)
- ❌ `GitCommit.md` (uppercase)
- ❌ `commit.md` (too vague)

**Rationale**:
- Kebab-case is standard for web URLs and CLIs
- Consistent with GitHub convention (repo names, branch names)
- Compatible with all operating systems
- Easily readable without camelCase parsing

---

### Aspect-Composed Skills

**Format**: `aspect-{aspect-name}.md`

**Rules**:
- Prefix with `aspect-`
- Aspect name in kebab-case
- Located in `skills/aspects/` directory

**Examples**:
- ✅ `aspect-yolo.md`
- ✅ `aspect-collaborative.md`
- ❌ `yolo-aspect.md` (wrong suffix)
- ❌ `aspect_yolo.md` (underscores)

**Rationale**:
- Prefix makes aspects immediately recognizable
- Consistent with skill naming (kebab-case)
- Easy to filter/search: `ls skills/aspects/aspect-*.md`

---

### Skill Documentation Files

**Format**: Various (see table)

| File Type | Format | Example |
|-----------|--------|---------|
| Skill definition | `{skill-name}.md` | `git-commit.md` |
| Skill README | `README.md` | `skills/workflow/README.md` |
| Implementation script | `{skill-name}.{ext}` | `git-commit.sh` (if used) |
| Test file | `test-{skill-name}.{ext}` | `test-git-commit.ts` |

**Rules**:
- README files are always `README.md` (uppercase)
- Scripts match skill name (same kebab-case)
- Tests prefixed with `test-`

---

### Directory Naming

**Format**: `{category-name}/`

**Rules**:
- Use **kebab-case** for multi-word categories
- Singular or plural based on content type (prefer plural)
- No special characters

**Examples**:
- ✅ `skills/`
- ✅ `aspects/`
- ✅ `execution/`
- ✅ `pull-requests/` (if needed for subcategory)
- ❌ `Execution/` (uppercase)
- ❌ `pull_requests/` (underscores)

---

## Skill Naming Patterns

### Action-Oriented Names

Skills should be named as **actions** (verbs or verb phrases):

| Pattern | Examples |
|---------|----------|
| `{verb}-{noun}` | `create-pr`, `merge-pr`, `update-work-item` |
| `{verb}-{noun}-{context}` | `handle-pr-feedback`, `finalize-work-item` |
| `{tool}-{action}` | `git-commit`, `gh-pr-review` |
| `{concept}` (nouns for modes) | `yolo`, `collaborative`, `sequential-execution` |

**Rationale**:
- Action-oriented names are self-documenting
- Matches user intent: "I want to commit changes" → `git-commit`
- Distinguishes from aspect modes (nouns like `yolo`)

---

### Avoid Abbreviations

Use full words unless abbreviation is universally recognized:

| ❌ Avoid | ✅ Use Instead |
|---------|---------------|
| `create-wi` | `create-work-item` |
| `upd-item` | `update-work-item` |
| `proc-pr` | `process-pr` |

**Exceptions** (widely recognized):
- ✅ `pr` (pull request)
- ✅ `cli` (command-line interface)
- ✅ `ui` (user interface)
- ✅ `gh` (GitHub, when tool-specific like `gh-pr-review`)

---

### Composed Skill Naming

**Format**: `{base-skill}+{aspect1}+{aspect2}`

**Rules**:
- Skills composed from aspects use `+` separator in **frontmatter only**
- Filename is still kebab-case without `+`
- `composed-from` field lists aspects

**Example**:

```yaml
---
name: git-commit-yolo
composed-from: git-commit+yolo
---
```

**Filename**: `git-commit-yolo.md` (not `git-commit+yolo.md`)

**Rationale**:
- `+` operator is clear composition notation (math/set theory)
- Kebab-case filename for filesystem compatibility
- Frontmatter records composition relationship

---

## Category Naming

### Existing Categories

| Category | Purpose | Naming Pattern |
|----------|---------|----------------|
| `execution/` | How agents operate (yolo, collaborative) | Mode or style names |
| `tools/` | Integration with external tools (git, gh) | Tool-based names |
| `workflow/` | Multi-step processes (create-pr, merge-pr) | Workflow action names |
| `aspects/` | Reusable behavior modifiers | `aspect-{name}` |

---

### Adding New Categories

**Process**:

1. **Identify need**: Multiple skills share a common theme
2. **Choose category name**: 
   - Singular for concepts (e.g., `execution/`)
   - Plural for collections (e.g., `tools/`)
   - Kebab-case for multi-word (e.g., `code-generation/`)
3. **Create directory**: `skills/{category-name}/`
4. **Add README.md**: Describe category purpose
5. **Update**: [[docs/reference/FILE_ORGANIZATION.md]]

**Example**:

```bash
mkdir skills/code-generation
cat > skills/code-generation/README.md <<EOF
# Code Generation Skills

Skills for generating code from templates, schemas, and specifications.
EOF
```

---

## Naming Anti-Patterns

### Anti-Pattern 1: Generic Names

❌ **Bad**:
- `skill.md`
- `process.md`
- `handler.md`

✅ **Good**:
- `git-commit.md`
- `process-pr.md`
- `handle-pr-feedback.md`

**Why**: Generic names don't convey purpose; specific names are discoverable

---

### Anti-Pattern 2: Inconsistent Separators

❌ **Bad**:
- `git_commit.md` (underscore)
- `GitCommit.md` (PascalCase)
- `git.commit.md` (dots)

✅ **Good**:
- `git-commit.md` (kebab-case)

**Why**: Consistency enables automated tooling and pattern matching

---

### Anti-Pattern 3: Overly Long Names

❌ **Bad**:
- `create-and-initialize-new-work-item-with-metadata.md`

✅ **Good**:
- `create-work-item.md`

**Why**: Long names are unwieldy; skill description provides details

---

### Anti-Pattern 4: Duplicate Information

❌ **Bad**:
- `git-commit-skill.md` (redundant `-skill`)
- `aspect-yolo-aspect.md` (redundant `-aspect`)

✅ **Good**:
- `git-commit.md`
- `aspect-yolo.md`

**Why**: Location (`skills/`) and prefix (`aspect-`) already indicate type

---

## Renaming Process

### When to Rename

- Breaking naming conventions
- Confusing or ambiguous names
- Duplicate names across categories
- Community feedback on clarity

### How to Rename

1. **Identify current usage**:
   ```bash
   grep -r "old-skill-name" pax/
   ```

2. **Update references**:
   - Frontmatter `name:` field
   - Documentation wikilinks: `[[old-name]]` → `[[new-name]]`
   - Examples and tutorials

3. **Rename file**:
   ```bash
   git mv skills/{category}/old-name.md skills/{category}/new-name.md
   ```

4. **Deprecation notice** (if widely used):
   - Keep old file with redirect for 1 minor version
   - Add deprecation warning:
     ```markdown
     > **DEPRECATED**: This skill has been renamed to [[new-name]].
     > This redirect will be removed in v2.0.0.
     ```

5. **Update index**:
   - Regenerate skills index
   - Update category README.md

---

## Validation

### Automated Checks

**Proposed tooling** (Phase 6):

```bash
# Check skill filenames
./scripts/validate-naming.sh

# Example output:
# ✅ git-commit.md
# ❌ git_commit.md (use kebab-case)
# ❌ GitCommit.md (use lowercase)
```

**Implementation** (see [[backlog/naming-validation-tool.md]]):
- Shell script with regex patterns
- Pre-commit hook integration
- CI check for PRs

---

### Manual Review Checklist

- [ ] **Filename**: kebab-case, no underscores, lowercase
- [ ] **Aspect prefix**: `aspect-` for all aspect skills
- [ ] **Action-oriented**: Verb or verb phrase (unless aspect/mode)
- [ ] **No abbreviations**: Full words (except `pr`, `cli`, `gh`)
- [ ] **Consistent with category**: Location matches purpose
- [ ] **No duplicates**: Unique name across all categories
- [ ] **Length**: Under 50 characters

---

## Examples by Category

### Execution Skills (Mode/Style Names)

- `yolo.md` - Autonomous execution mode
- `collaborative.md` - Interactive confirmation mode
- `sequential-execution.md` - Ordered task execution

**Pattern**: Noun or adjective describing execution style

---

### Tools Skills (Tool-Based Names)

- `git-commit.md` - Git commit automation
- `gh-pr-review.md` - GitHub PR review via CLI

**Pattern**: `{tool}-{action}` or `{tool}-{feature}`

---

### Workflow Skills (Multi-Step Actions)

- `create-pr.md` - PR creation workflow
- `handle-pr-feedback.md` - PR feedback resolution
- `merge-pr.md` - PR merge workflow
- `process-pr.md` - End-to-end PR processing

**Pattern**: `{verb}-{noun}` or `{verb}-{noun}-{context}`

---

### Aspect Skills (Reusable Behaviors)

- `aspect-yolo.md` - Auto-execution behavior
- `aspect-collaborative.md` - Interaction behavior

**Pattern**: `aspect-{behavior-name}`

---

## Future Considerations

### Namespace Prefixes

**Proposal**: For large skill collections, consider namespacing:
- `pax-core:git-commit`
- `pax-github:create-pr`
- `pax-workflow:process-pr`

**Status**: Not implemented (Phase 9: Distribution & Packaging)

### Skill Aliasing

**Proposal**: Allow skills to have multiple aliases:

```yaml
---
name: merge-pr
aliases:
  - merge-pull-request
  - pr-merge
---
```

**Status**: Not implemented (requires tooling support)

---

## References

### Internal References

- **File Organization**: [[docs/reference/FILE_ORGANIZATION.md]]
- **Frontmatter Specification**: [[docs/conventions/FRONTMATTER_SPECIFICATION.md]]
- **Skill Composition**: [[docs/SKILL_COMPOSITION.md]]

### External References

- [Kebab Case Naming Convention](https://en.wikipedia.org/wiki/Letter_case#Kebab_case)
- [GitHub Repository Naming Guidelines](https://github.com/bcgov/BC-Policy-Framework-For-GitHub/blob/master/BC-Gov-Org-HowTo/Naming-Repos.md)
- [W3C Web Standards Naming Conventions](https://www.w3.org/wiki/Naming_Conventions)

---

**Last Updated**: February 16, 2026  
**Status**: Active Convention (Enforced)  
**Version**: 1.0.0
