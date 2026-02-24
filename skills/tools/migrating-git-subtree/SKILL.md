---
name: migrating-git-subtree
description: Move one folder or a set of folders from one Git repository to another with `git subtree` while preserving commit history, authorship, and timestamps. Use when asked to migrate directories across repositories, split monorepos, import a subproject, keep syncing with `git subtree split/add/merge/pull`, or retire the source path after a successful import.
---

# Git Subtree Migration

## When to Use

Use this skill when you need history-preserving folder migration between repositories, including one-time imports and ongoing subtree sync.

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
6. Source-retirement policy: keep source prefix, remove immediately after verify, or remove in follow-up PR.

If any item is missing or ambiguous, stop and ask.

## Preflight Checks

Run before migration:

```bash
git -C <source-repo> rev-parse --is-inside-work-tree
git -C <target-repo> rev-parse --is-inside-work-tree
git -C <source-repo> status --short
git -C <target-repo> status --short
```

Require clean working trees unless the user explicitly approves working with local changes.

Rules:

- Preserve history: never use `--squash`.
- Create a target backup branch before import.
- Use a unique split branch name (`subtree/<id>-$(date +%Y%m%d%H%M%S)`) to avoid collisions.
- `git subtree merge` takes a single commit/ref argument. Do not pass `<remote> <branch>` to `subtree merge`.

## Decision Gate: Which Import Path?

Determine destination state before import:

```bash
DEST_EXISTS=no
[ -d "$TARGET_REPO/$DEST_PREFIX" ] && DEST_EXISTS=yes

HAS_SUBTREE_HISTORY=no
git -C "$TARGET_REPO" log --grep="git-subtree-dir: $DEST_PREFIX" --format=%H -n 1 >/dev/null && HAS_SUBTREE_HISTORY=yes

echo "DEST_EXISTS=$DEST_EXISTS HAS_SUBTREE_HISTORY=$HAS_SUBTREE_HISTORY"
```

Pick workflow:

- `DEST_EXISTS=no`: use `subtree add`.
- `DEST_EXISTS=yes` and `HAS_SUBTREE_HISTORY=yes`: use `subtree merge` or `subtree pull`.
- `DEST_EXISTS=yes` and `HAS_SUBTREE_HISTORY=no`: use subtree strategy merge (`git merge -s subtree -Xsubtree=<prefix> --allow-unrelated-histories <split-ref>`).

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

## Workflow A: First Import to New Destination Prefix

Example variables:

```bash
SOURCE_REPO=/path/to/source
TARGET_REPO=/path/to/target
SOURCE_BRANCH=main
TARGET_BRANCH=main
SOURCE_PREFIX=packages/foo
DEST_PREFIX=libs/foo
MIGRATION_ID=foo-$(date +%Y%m%d%H%M%S)
SPLIT_BRANCH=subtree/${MIGRATION_ID}
```

1. Create split branch from source prefix:

```bash
git -C "$SOURCE_REPO" checkout "$SOURCE_BRANCH"
if git -C "$SOURCE_REPO" rev-parse --abbrev-ref --symbolic-full-name "${SOURCE_BRANCH}@{upstream}" >/dev/null 2>&1; then
  git -C "$SOURCE_REPO" pull --ff-only
fi
git -C "$SOURCE_REPO" subtree split --prefix "$SOURCE_PREFIX" --branch "$SPLIT_BRANCH"
```

2. Prepare target and fetch split history:

```bash
git -C "$TARGET_REPO" checkout "$TARGET_BRANCH"
if git -C "$TARGET_REPO" rev-parse --abbrev-ref --symbolic-full-name "${TARGET_BRANCH}@{upstream}" >/dev/null 2>&1; then
  git -C "$TARGET_REPO" pull --ff-only
fi
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

## Workflow B: Update Existing Subtree-Managed Prefix

```bash
SPLIT_REF="source-tmp/$SPLIT_BRANCH"
git -C "$TARGET_REPO" subtree merge \
  --prefix "$DEST_PREFIX" \
  "$SPLIT_REF" \
  -m "chore(subtree): merge updates for $DEST_PREFIX"
```

For direct split+sync in one command after initial add, `subtree pull` is also valid.

## Workflow C: Adopt Existing Destination Prefix (Not Yet Subtree-Managed)

Use when destination path exists but has no subtree metadata in target history.

```bash
SPLIT_REF="source-tmp/$SPLIT_BRANCH"
git -C "$TARGET_REPO" merge \
  --allow-unrelated-histories \
  -s subtree \
  -Xsubtree="$DEST_PREFIX" \
  "$SPLIT_REF" \
  -m "chore(subtree): merge $SOURCE_PREFIX into existing $DEST_PREFIX"
```

## Workflow D: Multiple Folder Imports

Preferred approach: process each mapping independently with one commit per mapping.

```bash
SOURCE_REPO=/path/to/source
TARGET_REPO=/path/to/target
MIGRATION_ID=batch-$(date +%Y%m%d%H%M%S)

git -C "$TARGET_REPO" remote add source-tmp "$SOURCE_REPO" 2>/dev/null || true

import_mapping() {
  mapping="$1"
  src="${mapping%%:*}"
  dst="${mapping##*:}"
  key="$(echo "$src" | tr '/ ' '--')"
  split_branch="subtree/${MIGRATION_ID}/${key}"

  git -C "$SOURCE_REPO" subtree split --prefix "$src" --branch "$split_branch"
  git -C "$TARGET_REPO" fetch source-tmp "$split_branch"

  # Select add/merge/strategy-merge based on destination state for this mapping.
}

for mapping in "packages/a:libs/a" "packages/b:libs/b"; do
  import_mapping "$mapping"
done
```

## Verification (Required)

Run after each mapping:

```bash
git -C "$TARGET_REPO" log --oneline -- "$DEST_PREFIX" | head -n 20
git -C "$TARGET_REPO" log --format='%h %an %ad %s' -- "$DEST_PREFIX" | tail -n 10
git -C "$TARGET_REPO" blame "$DEST_PREFIX/<known-long-lived-file>" | head -n 10
```

Success signals:

- Imported path exists under target prefix.
- Log for the imported path shows historical commits (not just one new commit).
- Blame on a known long-lived file shows historical authors from source history.

Note: If blame is run on a brand-new file, all lines may point to the merge commit; that is not enough to prove history preservation.

## Optional: Retire Source Prefix After Verified Import

Run only if the user requested source removal.

```bash
git -C "$SOURCE_REPO" checkout "$SOURCE_BRANCH"
git -C "$SOURCE_REPO" rm -r "$SOURCE_PREFIX"
git -C "$SOURCE_REPO" commit -m "chore(subtree): remove migrated $SOURCE_PREFIX after verified import"
```

Post-removal verification:

```bash
if [ -d "$SOURCE_REPO/$SOURCE_PREFIX" ]; then
  echo "Residual untracked/ignored files remain under source prefix"
  find "$SOURCE_REPO/$SOURCE_PREFIX" -type f | head -n 20
fi
```

If residual files exist (for example ignored artifacts), remove them only with explicit user approval.

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
git -C "$TARGET_REPO" log --oneline -n 10
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
- `fatal: prefix '<path>' already exists`: destination exists; use decision gate to select merge strategy.
- `fatal: 'source-tmp' does not refer to a commit`: `subtree merge` was called with remote name instead of split ref/commit.
- `fatal: refusing to merge unrelated histories`: use Workflow C when adopting a pre-existing destination path.
- Missing history after import: check for accidental `--squash` usage and rerun from a clean migration branch.
