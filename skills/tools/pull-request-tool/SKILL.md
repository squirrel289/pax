---
name: pull-request-tool
description: Unified skill for managing GitHub pull requests and issues. Uses Copilot's native PR/issue APIs when available, and falls back to gh-pr-review CLI otherwise. Ensures maximum compatibility and agent-native features.
category: tools
license: MIT
compatibility: copilot, cli
aliases: [pr-tool]
keywords: [pull request, pr, github, management, merge, review, comment]
metadata:
  audience: agents, scripts, CI
---

# Pull Request Tool

A unified skill for managing GitHub pull requests and issues. Automatically uses Copilot's native APIs when available, and falls back to the `gh-pr-review` CLI tool if not. This ensures robust, composable workflows in both Copilot and non-Copilot environments.

## When to Use

- Any workflow requiring PR/issue management
- When you want to future-proof your skills for Copilot
- When you need to support both agent and CLI environments

## Interface, Workflows, and Best Practices

See [PR_MANAGEMENT_INTERFACE.md](../PR_MANAGEMENT_INTERFACE.md) for the unified interface, supported operations, workflows, best practices, error handling, and quick reference shared by all PR management skills.

## Tool-Specific Logic

This skill detects the environment and delegates to the correct backend:

1. If Copilot PR/issue APIs are available, use the `copilot-pull-request` skill (API)
2. Otherwise, use the `gh-pr-review` skill (CLI)

### Usage Example: Environment Detection

```python
if copilot_api_available():
    result = copilot_pull_request_skill(operation, params)
else:
    result = gh_pr_review_skill(operation, params)
return format_result(result)
```

### Usage Example: In Copilot Agent Environment

```python
# In Copilot agent environment, this skill will use the copilot-pull-request backend automatically:
result = pull_request_tool({
  'operation': 'merge-pr',
  'pr-number': 42,
  'repository': 'owner/repo',
  'merge-method': 'squash',
  'delete-branch': True
})
```

### Usage Example: In CLI Environment

```bash
# In CLI-only environments, this skill will use the gh-pr-review backend automatically:
pull-request-tool --operation merge-pr --pr-number 42 --repository owner/repo --merge-method squash --delete-branch true
```

## Output Format

All outputs follow the unified interface described in [PR_MANAGEMENT_INTERFACE.md](../PR_MANAGEMENT_INTERFACE.md), with structured JSON for programmatic use.

## Common Workflows

See [../PR_MANAGEMENT_INTERFACE.md](../PR_MANAGEMENT_INTERFACE.md) for canonical workflows, error handling, and best practices. All workflows are supported via this tool, with backend selection handled automatically.

## Best Practices

Refer to [../PR_MANAGEMENT_INTERFACE.md](../PR_MANAGEMENT_INTERFACE.md) for best practices. Always specify `repository`, parse structured output, and handle errors as described in the shared interface.

## Error Handling

See [../PR_MANAGEMENT_INTERFACE.md](../PR_MANAGEMENT_INTERFACE.md) for error handling strategies and common issues. Backend-specific errors (e.g., CLI not installed, API unavailable) are surfaced in the output.

## Integration with Other Skills

This skill is fully composable with other PAX skills, including parallel and sequential execution, yolo/collaborative interaction, and dedicated PR processing/merge/comment resolution skills. See [../PR_MANAGEMENT_INTERFACE.md](../PR_MANAGEMENT_INTERFACE.md) for integration patterns.

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
  pr-number: 42
  repository: owner/repo
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
  peration: check-status
  r-number: 42
  epository: owner/repo

MERGE PR:
  operation: merge-pr
  pr-number: <number>
  repository: <owner/repo>
  merge-method: squash|merge|rebase
  delete-branch: true|false
```
