---
name: migrating-git-subtree
description: Move one folder or a set of folders from one Git repository to another with `git subtree` while preserving commit history, authorship, and timestamps. Use when asked to migrate directories across repositories, split monorepos, import a subproject, or keep syncing with `git subtree split/add/merge/pull`.
---

# Git Subtree Migration

## Allowed Tools

- `terminal`
- `git`

Use no other tools unless the user explicitly asks.

## Clarification Gate

Before running commands, collect:

1. Source repository path/URL and source branch.
2. Target repository path/URL and target branch.
3. Mapping list: source prefix -> target prefix.
4. Migration mode: one-time import or ongoing sync.
5. Scope plan: one folder per commit and preferred PR grouping.

If any item is missing or ambiguous, stop and ask.

## Preflight Checks

Run before migration:

```bash
git -C <source-repo> status --short
git -C <target-repo> status --short
git -C <source-repo> rev-parse --is-inside-work-tree
git -C <target-repo> rev-parse --is-inside-work-tree
```

Require clean working trees unless the user explicitly approves working with local changes.

Rules:

- Preserve history: do not use `--squash`.
- Create a target backup branch before import.
- Use `subtree add` for first import to a new prefix.
- Use `subtree merge` or `subtree pull` only after an initial add exists.

## Plan Output (before acting)

Publish this plan before running migration commands:

```text
Migration Goal: <what is moving>
Source: <repo + branch>
Target: <repo + branch>
Mappings: <src-prefix -> dst-prefix list>
Commit Scope: <one folder per commit>
PR Scope: <single mapping per PR or approved grouped mappings>
Verification: <exact git log/blame checks to run>
Rollback: <revert commit strategy>
```

Use concrete paths and branch names; do not leave placeholders.

## Workflow A: Single Folder Import (History Preserved)

Example variables:

```bash
SOURCE_REPO=/path/to/source
TARGET_REPO=/path/to/target
SOURCE_BRANCH=main
TARGET_BRANCH=main
SOURCE_PREFIX=packages/foo
DEST_PREFIX=libs/foo
MIGRATION_ID=foo-$(date +%Y%m%d)
SPLIT_BRANCH=subtree/${MIGRATION_ID}
```

1. Create split branch in source repo from the folder history:

```bash
git -C "$SOURCE_REPO" checkout "$SOURCE_BRANCH"
git -C "$SOURCE_REPO" pull --ff-only
git -C "$SOURCE_REPO" subtree split --prefix "$SOURCE_PREFIX" --branch "$SPLIT_BRANCH"
```

2. Prepare target branch and fetch split history:

```bash
git -C "$TARGET_REPO" checkout "$TARGET_BRANCH"
git -C "$TARGET_REPO" pull --ff-only
git -C "$TARGET_REPO" checkout -b "migrate/${MIGRATION_ID}"
git -C "$TARGET_REPO" branch "backup/pre-subtree-${MIGRATION_ID}"
git -C "$TARGET_REPO" remote add source-tmp "$SOURCE_REPO" 2>/dev/null || true
git -C "$TARGET_REPO" fetch source-tmp "$SPLIT_BRANCH"
```

3. Import into target with full history:

```bash
git -C "$TARGET_REPO" subtree add \
  --prefix "$DEST_PREFIX" \
  source-tmp "$SPLIT_BRANCH" \
  -m "chore(subtree): import $SOURCE_PREFIX from source repo"
```

If `DEST_PREFIX` already exists from a previous import, use:

```bash
git -C "$TARGET_REPO" subtree merge \
  --prefix "$DEST_PREFIX" \
  source-tmp "$SPLIT_BRANCH" \
  -m "chore(subtree): merge updates for $DEST_PREFIX"
```

## Workflow B: Multiple Folder Imports

Preferred approach: process each mapping independently with one commit per mapping.

```bash
SOURCE_REPO=/path/to/source
TARGET_REPO=/path/to/target
MIGRATION_ID=batch-$(date +%Y%m%d)

git -C "$TARGET_REPO" remote add source-tmp "$SOURCE_REPO" 2>/dev/null || true

import_mapping() {
  mapping="$1"
  src="${mapping%%:*}"
  dst="${mapping##*:}"
  key="$(echo "$src" | tr '/ ' '--')"
  split_branch="subtree/${MIGRATION_ID}/${key}"

  git -C "$SOURCE_REPO" subtree split --prefix "$src" --branch "$split_branch"
  git -C "$TARGET_REPO" fetch source-tmp "$split_branch"
  git -C "$TARGET_REPO" subtree add \
    --prefix "$dst" \
    source-tmp "$split_branch" \
    -m "chore(subtree): import $src -> $dst"
}

for mapping in "packages/a:libs/a" "packages/b:libs/b"; do
  import_mapping "$mapping"
done
```

If one mapping was already imported previously, switch only that mapping from `subtree add` to `subtree merge`.

## Verification (Required)

Run after each mapping:

```bash
git -C "$TARGET_REPO" log --oneline -- "$DEST_PREFIX" | head -n 20
git -C "$TARGET_REPO" log --format='%h %an %ad %s' -- "$DEST_PREFIX" | tail -n 5
git -C "$TARGET_REPO" blame "$DEST_PREFIX/<known-file>" | head -n 10
```

Success signals:

- Imported path exists under target prefix.
- Log for the imported path shows historical commits (not just one new commit).
- Blame shows historical authors from the source repository.

## Ongoing Sync (Optional)

To sync later changes from source to target:

```bash
git -C "$SOURCE_REPO" subtree split --prefix "$SOURCE_PREFIX" --branch "$SPLIT_BRANCH"
git -C "$TARGET_REPO" fetch source-tmp "$SPLIT_BRANCH"
git -C "$TARGET_REPO" subtree pull \
  --prefix "$DEST_PREFIX" \
  source-tmp "$SPLIT_BRANCH" \
  -m "chore(subtree): sync $DEST_PREFIX from source"
```

## Rollback

If migration commit is incorrect, prefer safe revert:

```bash
git -C "$TARGET_REPO" log --oneline -n 5
git -C "$TARGET_REPO" revert <subtree-commit-sha>
```

Avoid destructive history rewrites on shared branches unless the user explicitly requests it.

## Cleanup

After merge or confirmed success:

```bash
git -C "$TARGET_REPO" remote remove source-tmp || true
git -C "$SOURCE_REPO" branch -D "$SPLIT_BRANCH" || true
```

## Troubleshooting

- `fatal: prefix '<path>' does not exist`: source prefix is wrong or not present on selected source branch.
- `fatal: prefix '<path>' already exists`: use `subtree merge` or change destination prefix.
- Missing history after import: check for accidental `--squash` usage and rerun from a clean branch.
