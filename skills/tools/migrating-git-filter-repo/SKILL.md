---
name: migrating-git-filter-repo
description: Move one or more subdirectories or files from one Git repository to another with `git filter-repo` while preserving commit history, authorship, and timestamps. Use when asked to split monorepos, migrate multiple paths between repositories, import selected files/folders into a new or existing repository, or retire source paths after verified migration.
---

# Git Filter-Repo Migration

## When to Use

Use this skill for history-preserving path migration and you need to move one or more directories/files across repositories.

## Allowed Tools

- `terminal`
- `git`

Use no other tools unless the user explicitly asks.

## Clarification Gate

Before running commands, collect:

1. Source repository path/URL and source branch.
2. Target repository path/URL and target branch.
3. Mapping list: source path -> destination path (directories and/or files).
4. Target mode: new target repository or existing target repository.
5. Collision policy for existing destination paths in target: keep, replace, or manual conflict resolution.
6. Source-retirement policy: keep source paths, remove immediately after verify, or remove in follow-up PR.

If any item is missing or ambiguous, stop and ask.

## Preflight Checks

Run before migration:

```bash
git -C <source-repo> rev-parse --is-inside-work-tree
git -C <source-repo> rev-parse <source-branch>
git -C <source-repo> status --short

git filter-repo --version
```

If target already exists:

```bash
git -C <target-repo> rev-parse --is-inside-work-tree
git -C <target-repo> status --short
```

Require clean working trees unless the user explicitly approves working with local changes.

## Safety Rules

- `git filter-repo` rewrites history. Run it only in a disposable clone, never in the canonical source clone.
- Create a backup branch in the target before importing.
- Prefer one migration commit per mapping unless the user approves grouped mappings.
- Keep migration branches and remotes temporary (`migration-tmp`, `migrate/<id>`).

## Plan Output (before acting)

Publish this plan before running migration commands:

```text
Migration Goal: <what is moving>
Source: <repo + branch>
Target: <repo + branch>
Mappings: <src-path -> dst-path list>
Target Mode: <new repo | existing repo>
Collision Policy: <keep | replace | manual resolve>
Commit Scope: <one mapping per commit or approved grouped mappings>
Verification: <exact git log/blame checks to run>
Rollback: <revert/branch restore strategy>
```

Use concrete paths and branch names; do not leave placeholders.

## Workflow A: Build Filtered Migration Repository

Example variables:

```bash
SOURCE_REPO=/path/to/source
SOURCE_BRANCH=main
WORKDIR=/tmp/filter-repo-migration
MIGRATION_ID=batch-$(date +%Y%m%d%H%M%S)
FILTER_REPO="$WORKDIR/source-filtered-$MIGRATION_ID"
```

1. Create disposable clone of source branch:

```bash
mkdir -p "$WORKDIR"
git clone --single-branch --branch "$SOURCE_BRANCH" "$SOURCE_REPO" "$FILTER_REPO"
```

1. Define mappings (directories and files both supported):

```bash
MAPPINGS=(
  "packages/legacy-web/:apps/web/"
  "services/payments/:backend/payments/"
  "README-legacy.md:docs/legacy/README-legacy.md"
)
```

1. Build filter arguments from mapping list and rewrite history:

```bash
FILTER_ARGS=()
for mapping in "${MAPPINGS[@]}"; do
  src="${mapping%%:*}"
  dst="${mapping#*:}"
  FILTER_ARGS+=(--path "$src" --path-rename "$src:$dst")
done

git -C "$FILTER_REPO" filter-repo --force --prune-empty always "${FILTER_ARGS[@]}"
```

Notes:

- For directory mappings, use trailing slashes on both sides (`old/` -> `new/`).
- For single-file mappings, use exact file paths (`old.txt` -> `new/path.txt`).

## Workflow B: Import into a New Target Repository

Use this when target is empty/new.

```bash
TARGET_REPO=/path/to/new-target
TARGET_BRANCH=main

git init -b "$TARGET_BRANCH" "$TARGET_REPO"
git -C "$TARGET_REPO" remote add migration-tmp "$FILTER_REPO"
git -C "$TARGET_REPO" fetch migration-tmp "$SOURCE_BRANCH"
git -C "$TARGET_REPO" checkout -B "$TARGET_BRANCH" "migration-tmp/$SOURCE_BRANCH"
```

If target is a new remote repository URL, clone it first (or create local repo then add remote and push).

## Workflow C: Import into an Existing Target Repository

Use this when target already contains history.

```bash
TARGET_REPO=/path/to/existing-target
TARGET_BRANCH=main

git -C "$TARGET_REPO" checkout "$TARGET_BRANCH"
if git -C "$TARGET_REPO" rev-parse --abbrev-ref --symbolic-full-name "${TARGET_BRANCH}@{upstream}" >/dev/null 2>&1; then
  git -C "$TARGET_REPO" pull --ff-only
fi

git -C "$TARGET_REPO" checkout -b "migrate/$MIGRATION_ID"
git -C "$TARGET_REPO" branch "backup/pre-filter-repo-$MIGRATION_ID"

git -C "$TARGET_REPO" remote add migration-tmp "$FILTER_REPO" 2>/dev/null || true
git -C "$TARGET_REPO" fetch migration-tmp "$SOURCE_BRANCH"
```

### Decision Gate: Handle Destination Collisions

Collect destination paths from mappings:

```bash
DEST_PATHS=(
  "apps/web"
  "backend/payments"
  "docs/legacy/README-legacy.md"
)
```

If destination paths do not exist in target:

```bash
git -C "$TARGET_REPO" merge \
  --allow-unrelated-histories \
  --no-ff \
  "migration-tmp/$SOURCE_BRANCH" \
  -m "chore(migration): import mapped paths via filter-repo"
```

If destination paths exist and policy is `replace`:

```bash
git -C "$TARGET_REPO" rm -r --ignore-unmatch "${DEST_PATHS[@]}"
git -C "$TARGET_REPO" commit -m "chore(migration): clear destination paths before filter-repo import"

git -C "$TARGET_REPO" merge \
  --allow-unrelated-histories \
  --no-ff \
  "migration-tmp/$SOURCE_BRANCH" \
  -m "chore(migration): import mapped paths via filter-repo"
```

If policy is `keep` or `manual resolve`, run merge and resolve conflicts explicitly.

## Workflow D: Multiple Mapping Strategy

Preferred for large migrations: one mapping per migration branch/commit.

```bash
for mapping in \
  "packages/a/:libs/a/" \
  "packages/b/:libs/b/" \
  "tools/legacy.sh:scripts/legacy.sh"
do
  # Rebuild disposable FILTER_REPO for this mapping only,
  # import, verify, then continue to next mapping.
  :
done
```

This keeps rollback and review small and auditable.

## Verification (Required)

Run after each imported mapping:

```bash
git -C "$TARGET_REPO" log --oneline -- <dest-path> | head -n 20
git -C "$TARGET_REPO" log --format='%h %an %ad %s' -- <dest-path> | tail -n 10
git -C "$TARGET_REPO" blame <dest-path-to-known-long-lived-file> | head -n 10
```

Success signals:

- Imported path exists under destination path.
- Log for imported path shows historical commits (not only a new merge/import commit).
- Blame on a long-lived migrated file shows historical source authors.

Note: running blame on a newly created file is not enough to prove history preservation.

## Optional: Retire Source Paths After Verified Import

Run only if requested:

```bash
git -C "$SOURCE_REPO" checkout "$SOURCE_BRANCH"
git -C "$SOURCE_REPO" rm -r <source-path-1> <source-path-2>
git -C "$SOURCE_REPO" commit -m "chore(migration): remove paths moved to target repo"
```

If ignored/untracked residual files remain, remove only with explicit user approval.

## Rollback

For existing target repository imports, prefer safe revert:

```bash
git -C "$TARGET_REPO" log --oneline -n 10
git -C "$TARGET_REPO" revert <merge-or-import-commit-sha>
```

For migration branches not merged yet, reset by deleting the branch and recreating from backup branch.

Avoid destructive history rewrites on shared branches unless the user explicitly requests it.

## Cleanup

After successful verification:

```bash
git -C "$TARGET_REPO" remote remove migration-tmp || true
rm -rf "$FILTER_REPO"
```

Delete temporary clones/branches only after migration is accepted.

## Troubleshooting

- `git: 'filter-repo' is not a git command`: install `git-filter-repo` and rerun preflight.
- `Refusing to destructively overwrite repo history`: run in a fresh disposable clone; do not run inside a working source clone.
- `fatal: refusing to merge unrelated histories`: include `--allow-unrelated-histories`.
- Merge conflicts on destination paths: apply the configured collision policy (`replace`, `keep`, or manual resolve).
- Missing history in target path: confirm mappings and verify that import was not squashed/recreated from copied files.
