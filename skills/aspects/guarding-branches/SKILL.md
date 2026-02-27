---
name: guarding-branches
description: "Enforce protected-branch guardrails for safe PR lifecycle, conflict resolution, and merge safety. Use when working on feature branches against protected main: before merging feature PRs, resolving merge conflicts, syncing with main, or managing work-item updates on protected branches."
metadata:
  type: document
  subtype: skill
---

# Guarding Branches

Protect merge integrity and prevent accidental deletions or regressions when working with protected main branches.

## When to Use

- Before merging a feature branch to protected main
- When resolving merge conflicts with main
- When syncing a feature branch with main for PR updates
- When updating work items on protected main
- When multiple parallel work items risk cross-branch contamination

## Core Guardrails

### 1. Mergeability Check

Before opening or updating a PR:

1. Verify the feature branch has no uncommitted changes: `git status`
2. Fetch latest main: `git fetch origin main`
3. Check PR mergeable state: `gh pr view <pr-number> --json mergeable`
4. If mergeable is `CONFLICTING`, run merge conflict resolution (step 3).

**Fail if**: PR is marked `UNMERGEABLE` or branch protection rules are violated. Do not bypass with `--admin` or `--force` flags.

### 2. Merge Conflict Resolution

When main diverges and PR shows conflicts:

1. Sync feature branch with main: `git merge origin/main --no-edit`
2. If conflicts occur:
   - Resolve conflicts manually in conflicting files
   - Re-run affected tests locally to validate fixes
   - Stage resolved files: `git add <resolved-file>`
3. Commit merge: `git commit -m "chore: merge main into <branch-name>"`
4. Verify no deletions: `git diff origin/main...HEAD --name-status | grep '^D'` — if deletions appear, restore from known-good commit
5. Push updated branch: `git push`

**Fail if**: Merge introduces unintended file deletions. Restore and add regression tests.

### 3. Export and Type Conflict Scan

When merging providers (diagnostic, intellisense, etc.):

1. After merge, scan `src/packages/volar/src/index.ts` (or equivalent) for duplicate exports: `rg "export \* from" <file>`
2. If two providers export the same type (e.g., `TemplateDelimiters`), rename one to disambiguate (e.g., `IntellisenseDelimiters`)
3. Run TypeScript check: `pnpm run type:check` — must pass with no errors
4. Re-run tests: `pnpm test:affected:ci` — must pass

**Fail if**: Type conflicts remain after rename or tests fail.

### 4. Diff Against Main

After merge, verify no unexpected deletions or mutations:

1. Run: `git diff origin/main...HEAD --name-status`
2. Review `D` (deleted) files — should only be intentional deletions
3. Review `M` (modified) files — should only touch intended source files
4. If work-item files were merged from main, restore them: `git restore <backlog-file>`

**Fail if**: Unintended deletions or cross-branch contamination detected.

### 5. Protected Main Updates

When updating work items or documentation on protected main:

1. **Never push directly to main** — always use a PR, even for small changes
2. If main is protected, create a dedicated PR for work-item status updates (e.g., `docs(backlog): mark WI-XXX ready-for-review`)
3. Validate frontmatter before committing: `pnpm run lint:frontmatter`
4. Use squash or rebase merges to keep history clean

**Fail if**: Attempting to bypass protection rules. Request an exception through branch-admin interface if truly necessary.

## Integration with Other Skills

- **executing-backlog**: References this aspect at orchestration gates (mergeability, conflict resolution, diff checks)
- **update-work-item**: References this aspect in "in-progress" and "ready-for-review" transitions
- **parallel-execution**: Uses this aspect to validate each workspace's branch state before checkout

## Troubleshooting

**Merge conflicts not resolved?**

- Manually inspect conflicting file
- Check git status: `git status --porcelain`
- Resolve with editor, then stage and commit

**Type conflicts after merge?**

- Search for duplicate exports: `rg "export.*<typename>" <file>`
- Rename one variant (e.g., append provider prefix)
- Re-run type check

**Unintended deletions detected?**

- Identify deleted files: `git diff origin/main...HEAD --name-status | grep '^D'`
- Restore from main: `git show origin/main:<file> > <file>`
- Commit restoration: `git add <file> && git commit -m "chore: restore deleted file"`
- Add regression test to prevent recurrence
