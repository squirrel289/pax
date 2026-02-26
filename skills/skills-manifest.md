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

### Decision & Discovery

#### discovering-alternatives

**Purpose**: Exhaustive discovery of build, buy, and hybrid options for a stated problem with evidence-backed decision matrix output.

**When to Use**:

- Early in solution selection to map the landscape
- Build vs buy vs hybrid assessments
- Creating a vendor shortlist with documented evidence

**Integration Point**: Upstream of comparative decision workflows and final selection.

**Example Usage**:

```bash
# Agent command
@agent discover alternatives for a templating linter (build vs buy vs hybrid) and provide a decision matrix
```

**Location**: [skills/workflow/discovering-alternatives/SKILL.md](workflow/discovering-alternatives/SKILL.md)

### Safety & Guardrails

> **Architecture Decision**: See [ADR-002: Centralize Safety Guardrails at Merge Bottleneck](../docs/adr/ADR-002-Centralize-Guardrails-at-Merge-Bottleneck.md) for design rationale.

Three guardrails skills enforce safety at critical merge points to prevent regressions.

#### guarding-branches

**Purpose**: Protect main branch during merge operations through conflict detection and safety checks.

**When to Use**:

- Before merging PRs to main
- Verifying branch mergeability
- Detecting unintended file deletions
- Scanning for type/export conflicts

**Integration Point**: `merge-pr` Phase 2 (Pre-Merge Verification)

**Key Checks**:

- Merge conflict detection (`git merge --no-commit --no-ff`)
- Type/export conflict scanning (`grep -r type` patterns)
- Unintended file deletion detection (`git diff --name-status`)
- Branch protection rule validation

**Location**: [`skills/aspects/guarding-branches/SKILL.md`](aspects/guarding-branches/SKILL.md)

#### validating-changes

**Purpose**: Ensure code quality before PR submission through local test runs.

**When to Use**:

- Before creating a PR
- Before requesting review
- During Test Parity Gate enforcement
- Verifying no regressions introduced

**Integration Point**: `merge-pr` Phase 1 (Test Parity Gate)

**Key Checks**:

- Affected tests pass locally (`pnpm test:affected:ci`)
- No regression runs (test before/after comparison)
- Coverage meets targets
- Integration tests pass in local environment

**Location**: [`skills/workflow/validating-changes/SKILL.md`](workflow/validating-changes/SKILL.md)

#### workspace-isolation

**Purpose**: Enable parallel work item execution with git worktrees for complete workspace separation.

**When to Use**:

- Executing multiple work items in parallel
- Need isolated working directories per WI
- Want ~3× speedup for N independent WIs
- Coordinating subagent code implementation

**Integration Point**: `executing-backlog` Phase 1, `update-work-item` Section 1

**Key Features**:

- Worktree creation for each active WI
- Isolated working directories, shared git database
- Subagent code-only implementation (subagent split rule)
- Main agent serialized PR operations during fan-in

**Location**: [`skills/execution/workspace-isolation/SKILL.md`](execution/workspace-isolation/SKILL.md)

**Example Usage**:

```bash
# Agent command
@agent execute 3 work items in parallel using workspace isolation

# Triggers workspace-isolation skill:
# 1. Create worktrees (WI-007, WI-008, WI-009)
# 2. Spawn N subagents (code implementation only)
# 3. Fan-in: Main agent merges serially via merge-pr
# Result: ~3× faster than sequential execution
```

#### Guardrail Activation Flow

```plaintext
User via executing-backlog or direct merge-pr call
│
├─ Developer finishes implementation
│  └─ Push branch + create PR
│
├─ Reviews/approvals complete
│  └─ Ready to merge
│
└─ Call merge-pr (enforces all guardrails)
   ├─ PHASE 1: Test Parity Gate (validating-changes)
   │  ├─ Run pnpm test:affected:ci
   │  ├─ Verify no unintended deletions
   │  └─ FAIL if tests don't pass → Stop, don't merge
   │
   ├─ PHASE 2: Pre-Merge Verification (guarding-branches)
   │  ├─ Verify GitHub PR checks pass
   │  ├─ Verify approvals received
   │  ├─ Check merge conflicts
   │  └─ FAIL if constraints violated → Stop
   │
   ├─ PHASE 4: Execute Merge
   │  └─ Merge to main (squash/rebase/merge)
   │
   └─ PHASE 5: Finalization
      └─ Report results, cleanup branches
```

**Result**: Guardrails enforced at **merge bottleneck**. Any code path calling `merge-pr` (directly or via workflow) must pass Test Parity Gate + guarding-branches checks.

#### Usage Patterns

##### Pattern 1: executing-backlog Workflow

```plaintext
Phase 1: Planning
Phase 2: Branching & Implementation
Phase 3: PR & Review (validation delegated to merge-pr)
Phase 4: Merge (calls merge-pr)
        └─ merge-pr enforces Test Parity Gate + guarding-branches
```

##### Pattern 2: Direct merge-pr Usage

```bash
# Script or automation calls merge-pr directly
merge_pr pr-number=123 repo=owner/repo
# Automatically enforces Test Parity Gate + guarding-branches
```

##### Pattern 3: Parallel Work Items

```plaintext
1. Setup: Create worktrees for each WI (workspace-isolation)
2. Execution: Spawn N subagents in parallel (code-only)
3. Fan-in: Main agent calls merge-pr serially for each WI
   └─ Each merge enforces guardrails
```

#### Testing & Validation Status

All guardrails are **production-ready**:

- ✅ `merge-pr` Phase 1 enforcement: Prevents broken code merges
- ✅ `guarding-branches` aspect: Tested in temple-linter, vscode-temple-linter workflows
- ✅ `validating-changes` aspect: Tested against CI/test patterns
- ✅ `workspace-isolation` skill: Reference implementation with realistic examples

**Replaces**: `process-pr` skill (deprecated)  
**Extends**: `feature-branch-management` (branch creation/sync)  
**Complements**: `finalize-work-item` (WI archival)

### Aspect Skills

Aspect skills provide reusable behavioral patterns that can be composed into workflow and tool skills.

See [skills/aspects/README.md](aspects/README.md) for complete documentation of all aspect skills, including:

- `interaction-modes`: Standardize yolo and collaborative execution patterns
- `guarding-branches`: Protect main branch during merges
- `prevalidating-bulk-operations`: Route bulk operations to systematic validation
- `organizing-documents-diataxis`: Apply Diataxis framework to output placement

### Continuous Improvement

Skills that enable learning from development patterns and evolving the skills library based on observed usage.

#### capture-events

**Purpose**: Capture workspace events (file modifications, terminal commands, diagnostics, skill invocations) into local memory for pattern detection and continuous feedback loop.

**When to Use**:

- Running continuously in background during development
- Building episodic memory for pattern analysis
- Supporting assistant-agnostic feedback loops (Copilot, Codex, Cursor)
- Enabling skill evolution based on usage patterns

**Integration Point**: `.vscode/pax-memory/` (git-ignored local storage)

**Example Usage**:

```bash
# Automatic (via workspace settings)
{
  "pax.feedbackLoop.enabled": true,
  "pax.feedbackLoop.provider": "universal"
}

# Manual control
capture-events --start --provider universal
capture-events --stop
capture-events --status
```

**Supports**:

- Universal provider (workspace-only, no assistant required)
- GitHub Copilot provider (extension integration)
- Codex provider (API-based)
- Cursor provider (extension integration)

#### creating-skill

**Purpose**: Evaluate a specific use case or skill idea against memory patterns and existing skills, then provide actionable recommendations. Delegates actual skill creation to skill-creator.

**When to Use**:

- Developer has an idea for a new skill
- Repeated pattern detected by continuous feedback loop
- Deciding between enhancing existing skill vs. creating new one
- Determining if pattern should become PAX skill, project skill, aspect, or AGENTS.md update

**Integration Point**: Continuous Feedback Loop (Recommendation Layer)

**Example Usage**:

```bash
# Agent command
@agent I need a skill for batch updating work items from CSV

# creating-skill analyzes:
# 1. Searches memory for similar patterns
# 2. Compares against existing skills (e.g., update-work-item)
# 3. Computes overlap and gaps
# 4. Recommends: enhance existing (70% overlap found)
# 5. Delegates to skill-creator if approved
```

**Recommendation Types**:

- Enhance existing PAX skill (high overlap)
- Create new PAX skill (reusable across projects)
- Create project-local skill (project-specific use case)
- Create or update aspect (cross-cutting concern)
- Update AGENTS.md (routing/orchestration change)

**Related**:

- Uses [[capture-events]] memory data
- Uses [[skill-reviewer]] rubric patterns
- Delegates to [[skill-creator]] for execution
- Part of [Continuous Feedback Loop](../docs/architecture/continuous-feedback-loop.md)

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
