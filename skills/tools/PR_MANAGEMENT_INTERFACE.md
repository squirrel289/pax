# PR Management Skill Interface (v1)

## Supported Operations

- Fetch PR details
- List and filter review comments
- Reply to comments
- Resolve threads
- Merge PRs (with method selection, branch deletion)
- Check and wait for CI/status checks

## Interface (Parameters)

- `operation`: fetch-pr-details | list-comments | reply-comment | resolve-thread | merge-pr | check-status
- `pr-number`: Pull request number
- `repository`: owner/repo
- `comment-id`, `thread-id`, `body`, `merge-method`, etc. as needed

## Common Workflows

### Workflow 1: Check PR Status

1. Fetch PR details
2. Check if mergeable (field: `mergeable`)
3. Verify status checks (field: `statusCheckRollup`)
4. Check for required approvals (field: `reviewDecision`)

### Workflow 2: Address Review Comments

1. List review comments (filter for unresolved threads)
2. For each thread:
   - Read comment and context
   - Reply
   - Resolve
3. Push changes if needed
4. Re-run checks

### Workflow 3: Automated PR Merge

1. Check PR is mergeable
2. Verify all status checks pass
3. Verify required approvals
4. Resolve any outstanding threads
5. Merge PR
6. Delete branch if desired

### Workflow 4: Full PR Processing

1. Fetch PR details
2. Run local checks (if supported)
3. Review all comments
4. Address feedback
5. Resolve threads
6. Wait for CI checks
7. Merge PR

## Output Format

- Structured JSON or markdown for agent consumption
- Consistent field names and ordering
- Essential data only
- Include error messages and status codes

## Best Practices

1. Always specify repository and PR number
2. Check merge readiness before merging
3. Filter for actionable review threads (unresolved, not outdated)
4. Use structured output for downstream skills
5. Handle errors gracefully and report status
6. Prefer Copilot API, fallback to CLI only if needed
7. Use this wrapper in all workflow skills

## Error Handling

Common errors and solutions:

- **PR not found**: Verify PR number and repository
- **Insufficient permissions**: Ensure proper repository access
- **Merge conflicts**: Resolve conflicts before merging
- **Failed status checks**: Wait for checks to pass or investigate failures
- **Missing approvals**: Request reviews from maintainers
- **API unavailable**: Fallback to CLI or report error

## Quick Reference

```markdown
FETCH PR:
  operation: fetch-pr-details
  pr-number: <number>
  repository: <owner/repo>

LIST COMMENTS:
  operation: list-comments
  pr-number: <number>
  repository: <owner/repo>

LIST UNRESOLVED COMMENTS:
  operation: list-comments
  pr-number: <number>
  repository: <owner/repo>
  filters:
    unresolved: true

REPLY TO COMMENT:
  operation: reply-comment
  pr-number: <number>
  thread-id: <id>
  body: "message"
  repository: <owner/repo>

RESOLVE THREAD:
  operation: resolve-thread
  pr-number: <number>
  thread-id: <id>
  repository: <owner/repo>

CHECK MERGEABLE:
  operation: check-status
  pr-number: <number>
  repository: <owner/repo>

MERGE PR:
  operation: merge-pr
  pr-number: <number>
  repository: <owner/repo>
  merge-method: squash|merge|rebase
  delete-branch: true|false
```
