---
name: performing-retro
description: Conduct a post-session review to organize changes into logical commits and document work. Use when: (1) Session has implemented features, fixes, or refactoring and changes are scattered across files, (2) Need to group related changes into atomic commits with conventional messages, (3) Want to create summary documentation of work completed, (4) Final validation before pushing changes. Helps transform a working session into clean git history and clear documentation.
license: MIT
metadata:
  category: workflow
  audience: agents
---

# Performing Retro

## Overview

A post-session review workflow that transforms scattered changes into clean, logical commits with coherent git history and clear documentation. This skill ensures work is properly organized and documented before contributing to the main branch.

## When to Use

Use this skill when:

- Session has implemented features, fixes, or improvements
- Multiple files have been modified but changes are not yet committed
- Need to organize changes into logical, atomic commits
- Want to create summary documentation of work completed
- Before pushing branches or creating PRs

## Core Principles

1. **Tell a Story**: Each commit should represent one logical change; commits together should tell the story of what was accomplished
2. **Atomic Commits**: One idea per commit; related changes grouped, unrelated changes separated
3. **Clear Documentation**: Summary files document intent and architectural decisions
4. **Conventional Messages**: All commits follow conventional commit format (feat, fix, refactor, docs, etc.)
5. **Evidence-Based**: Every change is traceable to intention; no orphaned files or mysterious modifications

## Workflow: Five Phases

### Phase 1: Gather & Analyze

**Goal**: Understand what changed and why.

1. **Review git status**:
   ```bash
   git status
   git diff --stat        # File change summary
   git diff --name-status # Modified/added/deleted files
   ```

2. **Analyze file groups**:
   - Group files by logical feature/purpose
   - Identify which changes are independent
   - Note any interdependencies

3. **Document intent** (mental checklist):
   - What feature/fix/refactor was implemented?
   - Which files changed and why?
   - Are there architectural decisions worth documenting?

**Example from guardrails implementation**:
```
Modified:
- skills/workflow/merge-pr/SKILL.md (added Test Parity Gate phase)
- skills/workflow/executing-backlog/SKILL.md (simplified to use merge-pr)
- skills/workflow/update-work-item/SKILL.md (added parallel execution guidance)

New:
- skills/aspects/guarding-branches/SKILL.md (new aspect)
- skills/workflow/validating-changes/SKILL.md (new aspect)
- skills/execution/workspace-isolation/SKILL.md (new skill)
- docs/GUARDRAILS_IMPLEMENTATION_SUMMARY.md (documentation)

Grouping:
1. Core guardrail aspects (guarding-branches + validating-changes)
2. Parallel execution skill (workspace-isolation)
3. Workflow integration (merge-pr, executing-backlog, update-work-item)
4. Documentation (summary doc)
```

### Phase 2: Plan Commits

**Goal**: Design the commit sequence to tell a coherent story.

1. **Identify commit boundaries**:
   - Each commit = one logical unit of work
   - Independent features = separate commits
   - Related files = same commit

2. **Order commits logically**:
   - Foundation first (new aspects/core skills)
   - Integration second (updates to existing workflows)
   - Documentation last (summaries of what was done)

3. **Map files to commits**:
   ```
   Commit 1: Create guarding-branches + validating-changes aspects
   Commit 2: Create workspace-isolation skill (parallel execution)
   Commit 3: Integrate guardrails into merge-pr (new Phase 1)
   Commit 4: Integrate guardrails into executing-backlog
   Commit 5: Integrate guardrails into update-work-item
   Commit 6: Document guardrails implementation
   ```

**Rationale**: Each commit is independently reviewable and explains one design decision.

### Phase 3: Create Commits

**Goal**: Stage and commit changes with clear, conventional messages.

For each planned commit:

1. **Stage relevant files**:
   ```bash
   git add path/to/file1 path/to/file2 ...
   ```

2. **Create conventional commit message**:
   - **Type**: feat, fix, refactor, docs, test, chore, perf, build, ci, style, revert
   - **Scope**: Area affected (guardrails, execution, workflow)
   - **Description**: What changed (present tense, <72 chars)
   - **Body**: Why it changed, design decisions, breaking changes (optional)

   ```bash
   git commit -m "feat(guardrails): add guarding-branches and validating-changes aspects
   
   - guarding-branches: Merge conflict detection, export scanning, deletion prevention
   - validating-changes: Local test validation, regression capture
   
   These aspects provide reusable validation patterns for branch safety."
   ```

3. **Verify commit is clean**:
   - Check that only intended files are included
   - Review message for clarity
   - Ensure scope matches content

**Key rule**: Never include unrelated changes in a single commit.

### Phase 4: Document Work

**Goal**: Create summary documentation explaining what was accomplished and why.

1. **Create or update summary file**:
   - Location: `docs/FEATURE-NAME_IMPLEMENTATION_SUMMARY.md` or similar
   - Include:
     - What was implemented (overview)
     - Why (rationale, architecture decisions)
     - How (integration points, workflow changes)
     - Related files (links to skills/code)

2. **Structure summary**:
   ```markdown
   # Feature Name Implementation

   ## Overview
   [1 paragraph explaining what was done]

   ## Architecture
   [Design decisions and rationale]

   ## Integration Points
   [How existing workflows changed]

   ## Key Files Updated
   - [List with brief purpose]

   ## Testing & Validation
   - [Validation approach]

   ## Status
   - Ready for adoption/testing/review
   ```

3. **Commit summary documentation**:
   ```bash
   git add docs/FEATURE-NAME_IMPLEMENTATION_SUMMARY.md
   git commit -m "docs(feature): document implementation and architecture"
   ```

### Phase 5: Validate & Complete

**Goal**: Ensure all work is properly committed and documented.

1. **Verify commits**:
   ```bash
   git log --oneline -N  # Show last N commits
   git log -p            # Review diffs
   ```

2. **Checklist**:
   - [ ] All modified files are committed
   - [ ] Each commit has conventional message
   - [ ] No untracked files (except intentional)
   - [ ] Summary documentation created
   - [ ] Commits tell coherent story
   - [ ] No orphaned changes

3. **Final review**:
   - Read commit messages as a sequence
   - Verify story/narrative flows
   - Check for any missing scope or context

## Commit Message Guidelines

### Conventional Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type       | Use When                          |
| ---------- | --------------------------------- |
| `feat`     | New feature or aspect             |
| `fix`      | Bug fix or issue resolution       |
| `refactor` | Code reorganization (no feature)  |
| `docs`     | Documentation only                |
| `test`     | Add/update tests                  |
| `perf`     | Performance improvement           |
| `chore`    | Maintenance/misc (no code change) |
| `ci`       | CI/workflow config                |
| `style`    | Formatting (no logic change)      |
| `revert`   | Revert previous commit            |

### Scopes

Scopes should identify the area affected:
- `(guardrails)` - Guardrail aspects/skills
- `(execution)` - Execution-related changes
- `(workflow)` - Workflow skill changes
- `(integration)` - Integration of components
- `(docs)` - Documentation

### Examples

```
# New feature with scope
feat(guardrails): add guarding-branches aspect for merge safety

# Bug fix with breaking change
fix!: correct test parity gate logic in merge-pr

# Documentation update
docs(guardrails): explain Test Parity Gate architecture

# Integration change
refactor(workflow): simplify executing-backlog to use merge-pr

# Multiple related features in body
feat(execution): add workspace-isolation skill for parallel work items

- Creates git worktrees for isolated work item execution
- Enables N parallel subagents (code-only) + main agent (git/PR operations)
- Serialized fan-in phase prevents merge conflicts
```

## Anti-Patterns

Avoid these common mistakes:

| Mistake | Why It's Wrong | Solution |
|---------|----------------|----------|
| **Mega-commit** | Mixes unrelated changes; hard to review | Split into atomic commits |
| **Orphaned files** | Unexplained changes; unclear intent | Every change → 1 commit |
| **Vague messages** | "Update stuff", "Fix things" | Use conventional format, describe specifically |
| **Uncommitted work** | Incomplete session; risky to lose | Commit everything in Phase 3 |
| **No summary docs** | Future readers don't understand | Create summary in Phase 4 |
| **Out-of-order commits** | Dependencies unclear | Order: foundation → integration → docs |

## Example Walkthrough

### Session Changes

After implementing guardrails, `git status` shows:

```
Modified:
- skills/workflow/merge-pr/SKILL.md
- skills/workflow/executing-backlog/SKILL.md  
- skills/workflow/update-work-item/SKILL.md

Untracked:
- skills/aspects/guarding-branches/SKILL.md
- skills/workflow/validating-changes/SKILL.md
- skills/execution/workspace-isolation/SKILL.md
- docs/GUARDRAILS_IMPLEMENTATION_SUMMARY.md
```

### Phase 1: Gather & Analyze

**Changes grouped by purpose**:
1. New aspects: guarding-branches, validating-changes (foundation)
2. New skill: workspace-isolation (parallel execution)
3. Modified workflows: merge-pr, executing-backlog, update-work-item (integration)
4. Documentation: summary file (explanation)

### Phase 2: Plan Commits

```
Commit 1: feat(guardrails): add guarding-branches + validating-changes
Commit 2: feat(execution): add workspace-isolation skill
Commit 3: refactor(workflow): centralize guardrails in merge-pr
Commit 4: refactor(workflow): integrate guardrails into executing-backlog
Commit 5: refactor(workflow): integrate guardrails into update-work-item
Commit 6: docs(guardrails): document implementation summary
```

### Phase 3: Create Commits

```bash
# Commit 1
git add skills/aspects/guarding-branches/SKILL.md skills/workflow/validating-changes/SKILL.md
git commit -m "feat(guardrails): add guarding-branches and validating-changes aspects"

# Commit 2
git add skills/execution/workspace-isolation/SKILL.md
git commit -m "feat(execution): add workspace-isolation skill for parallel work items"

# Commit 3
git add skills/workflow/merge-pr/SKILL.md
git commit -m "refactor(workflow): centralize Test Parity Gate in merge-pr Phase 1"

# ... and so on
```

### Phase 4: Document Work

Create `docs/GUARDRAILS_IMPLEMENTATION_SUMMARY.md` explaining:
- What guardrails were implemented
- Architecture decisions (merge bottleneck enforcement)
- Integration points in workflows
- Status (ready for adoption)

```bash
git add docs/GUARDRAILS_IMPLEMENTATION_SUMMARY.md
git commit -m "docs(guardrails): document implementation and architecture"
```

### Phase 5: Validate

```bash
git log --oneline -7
# f8f8afa feat(guardrails): add guarding-branches and validating-changes aspects
# f77ae51 feat(execution): add workspace-isolation skill
# ... (more commits)
```

Each commit tells part of the story; together they show: "Implemented guardrails, created new skill, integrated into workflows, documented work."

## Tips & Best Practices

1. **Commit frequently during work**: Don't wait until session end to commit; logical commits help during development
2. **Review diffs before committing**: Use `git diff` to verify you're only including intended changes
3. **Use interactive staging if needed**: `git add -p` to stage parts of a file
4. **Test after commits**: Verify each commit works independently if possible
5. **Write descriptive bodies**: Especially for architectural decisions or breaking changes
6. **Link to issues**: Use `Closes #123` or `Refs #456` in footers when applicable
7. **Document as you go**: Create summary files while work is fresh, before commits fade from memory

## Safety Guardrails

Never:
- Force push to main/master
- Commit secrets or credentials
- Use `--no-verify` to bypass hooks
- Mix unrelated changes in single commit
- Commit without clear message

Always:
- Review `git status` and `git diff` before committing
- Use conventional commit format
- Keep changes atomic and logical
- Document architectural decisions
- Test changes before final push

## Related Skills

- `git-commit`: Detailed conventional commit guidance and execution
- `executing-backlog`: Workflow that precedes performing-retro
- `finalize-work-item`: Post-retro work item closure and archival

---

**Status**: Ready for use after each development session. Helps maintain clean, documented git history.
