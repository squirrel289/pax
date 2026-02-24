# Agent Skills Manifest

AI agent tools and workflows used in development.

## Overview

This document catalogs the agent skills integrated into the development workflow. These skills provide structured, reusable patterns for common development tasks and are invoked through GitHub Copilot and other AI assistants.

## Skill Categories

### Work Item Management

#### update-work-item

**Purpose**: Update progress, status, and metadata for backlog work items.

**When to Use**:

- Transitioning work item status (not_started → in_progress → testing → completed)
- Recording actual effort vs estimated effort
- Tracking test results and commits
- Updating dependencies and notes

**Integration Point**: `backlog/*.md` frontmatter updates

**Example Usage**:

```bash
# Agent command
@agent update work item 005 to in_progress

# Manual equivalent
# Edit backlog/005_chevrotain_lexer.md frontmatter:
# status: in_progress
# started_date: 2026-02-18
```

#### finalize-work-item

**Purpose**: Complete and archive a work item after successful merge.

**When to Use**:

- All acceptance criteria met
- PR merged to main
- Tests passing in production
- Ready to close work item

**Integration Point**: Moves work items from `backlog/` to `backlog/archive/`

**Example Usage**:

```bash
# Agent command
@agent finalize work item 005

# Manual equivalent
mv backlog/005_chevrotain_lexer.md backlog/archive/
# Update frontmatter: status: completed, completed_date: 2026-02-18
```

#### create-work-item

**Purpose**: Create new work items with standardized structure and auto-numbering.

**When to Use**:

- Starting new features or tasks
- Proposing enhancements
- Documenting bugs

**Integration Point**: Creates new files in `backlog/` with correct frontmatter

**Example Usage**:

```bash
# Agent command
@agent create work item "Implement AST Renderer"

# Manual equivalent
# Create backlog/007_ast_renderer.md with frontmatter template
# Auto-number next available ID
```

### Version Control

#### git-commit

**Purpose**: Create conventional commits with automatic type/scope detection.

**When to Use**:

- Committing feature changes
- Following conventional commit format
- Generating commit messages from diffs

**Integration Point**: Git commit hooks, `.commitlintrc.json`

**Example Usage**:

```bash
# Agent command
@agent /commit

# Triggers
# 1. Analyzes git diff
# 2. Detects type (feat, fix, docs, etc.)
# 3. Detects scope (core, cli, volar, vscode)
# 4. Generates commit message
# 5. Commits with conventional format
```

#### feature-branch-management

**Purpose**: Create, sync, and clean up feature branches.

**When to Use**:

- Starting work on a work item
- Rebasing feature branches on main
- Deleting merged branches

**Integration Point**: Git workflow, branch naming conventions

**Example Usage**:

```bash
# Agent command
@agent create feature branch for work item 007

# Creates branch: feature/007-ast-renderer
# Tracks in work item frontmatter: branch: feature/007-ast-renderer
```

### Pull Requests

#### create-pr

**Purpose**: Create pull requests with work item metadata auto-populated.

**When to Use**:

- Implementation complete and tested
- Ready for code review
- Status: testing

**Integration Point**: GitHub PRs, `.github/PULL_REQUEST_TEMPLATE.md`

**Example Usage**:

```bash
# Agent command
@agent create PR for work item 007

# Triggers
# 1. Reads work item frontmatter
# 2. Generates PR title from work item title
# 3. Populates PR body with work item content
# 4. Links work item ID
# 5. Sets labels from work item tags
```

#### handle-pr-feedback

**Purpose**: Triage and address PR review comments automatically.

**When to Use**:

- PR receives review feedback
- Comments need to be categorized by severity
- Minor issues can be auto-resolved

**Integration Point**: GitHub PR reviews, comment threads

**Example Usage**:

```bash
# Agent command
@agent handle feedback on PR #42

# Triggers
# 1. Fetches PR comments
# 2. Categorizes: blocker, major, minor, nit
# 3. Auto-resolves minor/nit with fixes
# 4. Flags blockers for manual review
```

### Testing & Quality

#### parallel-execution

**Purpose**: Run multiple independent tasks simultaneously for efficiency.

**When to Use**:

- Running tests across multiple packages
- Parallel linting/formatting
- Independent build steps

**Integration Point**: Nx affected commands, CI/CD workflows

**Example Usage**:

```bash
# Agent command
@agent run tests in parallel for affected packages

# Executes
nx affected -t test --parallel=3
nx affected -t lint --parallel=3
```

### Documentation

#### architecture-decision-records

**Purpose**: Create and maintain ADRs for significant technical decisions.

**When to Use**:

- Major architectural changes
- Technology selection decisions
- Process changes

**Integration Point**: `docs/adr/*.md`

**Example Usage**:

```bash
# Agent command
@agent create ADR for parser selection

# Creates docs/adr/002-parser-selection.md with template
```

## Skill Dependencies

```text
┌─────────────────────────────────────┐
│    Work Item Lifecycle              │
├─────────────────────────────────────┤
│  create-work-item                   │
│         ↓                           │
│  feature-branch-management          │
│         ↓                           │
│  update-work-item (in_progress)     │
│         ↓                           │
│  git-commit (iterative)             │
│         ↓                           │
│  update-work-item (testing)         │
│         ↓                           │
│  create-pr                          │
│         ↓                           │
│  handle-pr-feedback (if needed)     │
│         ↓                           │
│  finalize-work-item (after merge)   │
└─────────────────────────────────────┘
```

## Integration with CI/CD

Skills integrate with automated workflows:

1. **Pre-commit Hooks**: `git-commit` validates conventional commit format
2. **PR Creation**: `create-pr` populates PR template with work item metadata
3. **CI Tests**: `parallel-execution` runs affected tests
4. **Post-merge**: `finalize-work-item` archives completed work

## Custom Skills

### Creating New Skills

Skills are structured prompts with:

1. **Frontmatter**: Metadata (tags, status, scope)
2. **Description**: Purpose and use cases
3. **Instructions**: Step-by-step workflow
4. **Examples**: Sample invocations
5. **Integration**: Where skill fits in workflow

Location: `.agents/skills/`

### Skill Best Practices

- **Single Responsibility**: Each skill does one thing well
- **Composable**: Skills can be chained together
- **Idempotent**: Safe to run multiple times
- **Self-Documenting**: Clear purpose and usage
- **Testable**: Can be validated with test data

## Troubleshooting

### Skill Not Found

**Problem**: Agent doesn't recognize skill name.

**Solution**:

```bash
# Check skill manifest
cat .agents/skills-manifest.md

# Verify skill file exists
ls .agents/skills/skill-name/SKILL.md

# Try alternate phrasing
@agent help with work items
```

### Skill Fails Silently

**Problem**: Skill runs but doesn't produce expected output.

**Solution**:

- Check work item frontmatter is valid YAML
- Verify file paths are correct
- Review git status before running
- Check for merge conflicts

### Skill Permissions

**Problem**: Skill can't create files or branches.

**Solution**:

- Ensure GitHub token has correct scopes
- Check file system permissions
- Verify not in detached HEAD state

## Reference

- **Skill Source**: `.agents/skills/`
- **Copilot Instructions**: `.github/copilot-instructions.md`
- **Work Item Schema**: `schemas/frontmatter/work-item.json`
- **Document Schema**: `schemas/frontmatter/document.json`

## Future Skills (Planned)

- `run-benchmarks`: Execute performance tests and compare results
- `generate-changelog`: Create changelog from commit history
- `sync-dependencies`: Update package dependencies across monorepo
- `validate-coverage`: Ensure code coverage thresholds are met
- `generate-docs`: Auto-generate API documentation from TypeScript
