---
name: sandboxing-workspace
description: "Enforce one-sandbox-per-effort execution with explicit ownership and channel-only handoffs. Use when work is delegated, parallelized, or split across git worktrees, processes, terminal sessions, or subagent contexts."
license: MIT
metadata:
  type: document
  subtype: skill
  category: aspect
  audience: agents, developers
---

# Sandboxing Workspace

Reusable aspect for strict workspace isolation and ownership boundaries across orchestrator/subagent execution.

## When to Use

Use this aspect when a workflow:

- delegates work to subagents
- runs multiple efforts in parallel
- hands off responsibility between orchestrator and subagent
- uses separate worktrees, processes, terminal sessions, or agent contexts

## Required Contract

### 1) One Effort, One Sandbox

- Each discrete effort (for example: work item, analysis, test suite) gets its own sandbox.
- Never run unrelated active efforts in the same mutable sandbox.

### 2) Single Active Owner

- Exactly one active owner writes to a sandbox at a time.
- A subagent may edit only within its assigned sandbox and allowed scope.
- The orchestrator must not modify delegated scope until handoff completes.

### 3) Context Switch Means Sandbox Switch

- If ownership transfers to a subagent, execution for that effort occurs entirely in the subagent sandbox.
- Ownership returns only after explicit completion/handoff.

### 4) Channel-Only Coordination

Allowed bidirectional channels:

- orchestrator -> subagent prompt/send_input
- subagent -> orchestrator report/status
- git artifacts for state transfer (commit/push/cherry-pick/PR)

Disallowed:

- ad-hoc mutable file transfer between sandboxes
- cross-sandbox edits without explicit handoff
- implicit ownership switches

## Canonical Handoff Payload

```json
{
  "effort_id": "WI-123",
  "sandbox_path": "/repo/wt_wi_123",
  "branch": "feature/wi-123",
  "allowed_scope": ["src/payments/**", "tests/payments/**", "backlog/123_*.md"],
  "done_criteria": [
    "acceptance criteria complete",
    "tests for touched scope pass",
    "status set to ready-for-review"
  ]
}
```

## Canonical Isolation Examples

### Git Isolation (worktree + branch)

```bash
# Orchestrator creates sandbox
git worktree add /repo/wt_wi_123 feature/wi-123

# Orchestrator delegates ownership
spawn_subagent \
  effort_id=WI-123 \
  workspace=/repo/wt_wi_123 \
  prompt="You own WI-123 in /repo/wt_wi_123 on feature/wi-123. Modify only src/payments/**, tests/payments/**, backlog/123_*.md."
```

### Process Isolation (one effort per process identity)

```bash
export EFFORT_ID="WI-123"
export SANDBOX_PATH="/repo/wt_wi_123"
export ALLOWED_SCOPE="src/payments/** tests/payments/** backlog/123_*.md"

# Optional ownership lock
mkdir "/tmp/locks/${EFFORT_ID}.lock"
trap 'rmdir "/tmp/locks/${EFFORT_ID}.lock"' EXIT
```

### Terminal Isolation (one effort per terminal session)

```bash
# Example with tmux
tmux new-session -d -s wi-123 -c /repo/wt_wi_123
tmux send-keys -t wi-123 "git status -sb" C-m

# Do not run WI-124 in session wi-123
```

### Agent Context Isolation (one owner subagent)

```json
{
  "tool": "spawn_agent",
  "message": "Implement WI-123 in /repo/wt_wi_123 on feature/wi-123. Allowed scope: src/payments/** tests/payments/** backlog/123_*.md. Do not modify outside this sandbox."
}
```

### Scope Guard (shell preflight)

```bash
# Fail fast if command is run in wrong sandbox
[[ "$PWD" == "/repo/wt_wi_123"* ]] || { echo "wrong sandbox"; exit 1; }
git rev-parse --abbrev-ref HEAD | grep -qx "feature/wi-123" || { echo "wrong branch"; exit 1; }
```

## Integration Pattern

Declare this aspect in skill frontmatter:

```yaml
metadata:
  aspects:
    - sandboxing-workspace
```

## Review Checklist

- [ ] effort id is explicit
- [ ] sandbox path and branch are explicit
- [ ] owner is explicit
- [ ] allowed scope is explicit
- [ ] handoff channel is explicit
