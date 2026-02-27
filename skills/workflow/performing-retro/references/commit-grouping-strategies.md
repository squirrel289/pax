# Commit Grouping Strategies

## Common Grouping Patterns

### Pattern 1: Feature Implementation (Foundation → Integration → Documentation)

When implementing a new feature across multiple components:

```bash
Commit 1: feat(core): core feature implementation
          - New data structures
          - Core algorithms
          
Commit 2: feat(api): expose feature via API
          - New endpoints
          - Request/response schemas
          
Commit 3: feat(ui): UI components for feature
          - React components
          - Styling
          
Commit 4: feat(integration): wire feature end-to-end
          - Connect API to UI
          - Data flow setup
          
Commit 5: test(feature): add comprehensive tests
          - Unit tests
          - Integration tests
          - E2E tests
          
Commit 6: docs(feature): document feature and usage
          - README updates
          - API documentation
          - Examples
```

### Pattern 2: Bug Fix with Architectural Change

When fixing a bug that requires refactoring:

```bash
Commit 1: refactor(module): restructure for clarity
          - No behavior change
          - Just reorganization
          
Commit 2: fix(bug): resolve bug with new structure
          - References the refactored code
          - Clear why refactor was needed
          
Commit 3: test(regression): add test to prevent recurrence
          - Test that catches the bug
          - Validates fix
```

### Pattern 3: Guardrails/Safety Features

When adding validation or safety checks:

```bash
Commit 1: feat(aspect): add validation aspect
          - New validation logic
          - Reusable pattern
          
Commit 2: feat(skill): create skill using aspect
          - New skill that uses aspect
          
Commit 3: refactor(integration): integrate into workflows
          - Update existing workflows
          - Add validation gates
          
Commit 4: refactor(process): simplify by delegating validation
          - Remove duplicate validation
          - Consolidate at single point
          
Commit 5: docs(architecture): document design decisions
          - Why validation at this point
          - How enforcement works
```

### Pattern 4: Cleanup and Removal

When removing deprecated features or cleaning up:

```bash
Commit 1: deprecation(feature): mark feature as deprecated
          - Add deprecation warnings
          - Document migration path
          
Commit 2: docs(migration): document how to migrate
          - Migration guide
          - Examples
          
Commit 3: refactor(removal): remove deprecated feature
          - Clean removal
          - Update references
          
Commit 4: docs(cleanup): remove legacy documentation
          - Old docs referencing removed feature
```

### Pattern 5: Multi-Project Coordination

When updating related components across projects:

```bash
Commit per project:
- feat(project-a): change affecting project-a
- feat(project-b): change affecting project-b
- feat(project-c): change affecting project-c

Then:
- docs(architecture): explain cross-project impact
- docs(migration): if breaking changes involved
```

## Decision Checklist

When planning commits, ask:

1. **Is this change independent?**
   - Can it be reviewed in isolation?
   - Does it depend on other changes in this batch?
   → If independent: separate commit
   → If dependent: same commit or sequence them clearly

2. **Does this commit affect multiple concerns?**
   - Feature implementation + tests + docs?
   - Bug fix + refactoring + tests?
   → If mixed concerns: separate based on concern type
   → Feature first, then integration, then docs/tests

3. **Would future readers understand the "why"?**
   - Does the commit message explain intent?
   - Would commit history help someone understand decisions?
   → If unclear: expand message or split commit

4. **Can this be tested independently?**
   - Add tests in same commit or separate?
   → If fundamental to understanding change: same commit
   → If validation/regression test: separate commit

## Examples from Real Sessions

### Guardrails Implementation

```bash
Commit 1: feat(guardrails): add guarding-branches and validating-changes aspects
          Files: skills/aspects/guarding-branches/SKILL.md
                 skills/workflow/validating-changes/SKILL.md

Commit 2: feat(execution): add workspace-isolation skill
          Files: skills/execution/workspace-isolation/SKILL.md

Commit 3: refactor(workflow): centralize Test Parity Gate in merge-pr
          Files: skills/workflow/merge-pr/SKILL.md

Commit 4: refactor(workflow): simplify executing-backlog to use merge-pr
          Files: skills/workflow/executing-backlog/SKILL.md

Commit 5: refactor(workflow): integrate guardrails into update-work-item
          Files: skills/workflow/update-work-item/SKILL.md

Commit 6: docs(guardrails): document implementation and architecture
          Files: docs/GUARDRAILS_IMPLEMENTATION_SUMMARY.md
```bash

**Story**: Creates guardrails (foundation) → creates new skill (capability) → integrates into workflows (adoption) → documents (understanding).

## Anti-Patterns by Developer Type

### Junior Developer (Likely Mistakes)

❌ **Mega-commit**: "Session 1 work" with 15 files
→ **Fix**: One feature per commit, or split by concern

❌ **Orphaned changes**: Modified file with no explanation
→ **Fix**: Commit message must explain why this file changed

❌ **Unrelated grouping**: Bug fix + refactor + new feature in one commit
→ **Fix**: Separate per type/scope, order them logically

### Experienced Developer (Likely Mistakes)

❌ **Over-specialized commits**: One line per commit
→ **Fix**: Group related changes (same feature, same file set)

❌ **Skipped docs**: "Code is self-documenting" for complex changes
→ **Fix**: Add commit message bodies explaining architecture

❌ **Rushed messages**: "updates", "fixes stuff", "changes"
→ **Fix**: Be specific: "fix: prevent race condition in cache invalidation"

## Validation Checklist

Before finalizing your retro:

- [ ] Each commit has one logical purpose
- [ ] Commits are ordered logically (foundation → integration → docs)
- [ ] All message types use conventional format
- [ ] Scopes are consistent and meaningful
- [ ] Descriptions are in present tense, under 72 chars
- [ ] Bodies explain "why", not "what" (diffs show what)
- [ ] No untracked files (except intentional)
- [ ] No uncommitted changes
- [ ] Commit messages tell a coherent story when read sequentially

---

**Remember**: Good commits help future readers (including yourself) understand not just what changed, but why and when each decision was made.
