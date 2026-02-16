---
name: process-pr
description: End-to-end workflow for processing pull requests from review to merge
category: workflow
license: MIT
composed-from:
  - parallel-execution OR sequential-execution
  - yolo OR collaborative
  - resolve-pr-comments
  - merge-pr
  - pull-request-tool
---

# Process PR

A comprehensive workflow skill that orchestrates the complete pull request lifecycle from initial review through merge.

## Purpose

Provides end-to-end automation for processing PRs, composing multiple workflow and tool skills into a unified, efficient process.

## When to Use

Use this workflow when:

- You want complete PR automation from start to finish
- PR is ready for final processing and merge
- You need a consistent, repeatable PR workflow
- Multiple PRs need to be processed efficiently

## Skill Composition

This workflow composes:

1. **pull-request-tool**: PR interaction and status checking
2. **parallel-execution**: Concurrent checks and analyses
3. **sequential-execution**: Ordered workflow stages
4. **resolve-pr-comments**: Address review feedback
5. **merge-pr**: Safe merge execution
6. **yolo** OR **collaborative**: Execution mode

## Parameters

### Required

- **pr-number**: Pull request number(s) to process
- **repository**: Repository in format `owner/repo`

### Optional

- **interaction-mode**: `yolo` (autonomous) or `collaborative` (interactive)
- **merge-method**: `merge`, `squash` (default), or `rebase`
- **delete-branch**: Delete branch after merge (default: true)
- **run-local-checks**: Run tests/lint locally before merge (default: true)
- **resolve-comments**: Auto-resolve review comments (default: true)
- **require-approvals**: Minimum required approvals (default: 1)

## Workflow Stages

### Stage 1: Initial Assessment (Parallel)

Execute these checks simultaneously for speed:

1. **Fetch PR details** (pull-request-tool)
   - Get PR metadata, status, labels
   - Identify base and head branches

2. **Check review status** (pull-request-tool)
   - Count approvals
   - Check for blocking reviews
   - List unresolved threads

3. **Verify CI checks** (pull-request-tool)
   - Get status check results
   - Identify failing/pending checks

Result: Comprehensive PR readiness snapshot

### Stage 2: Local Verification (Sequential)

If `run-local-checks = true`:

1. **Fetch branch**
   - Checkout PR branch
   - Pull latest changes

2. **Run tests** (parallel)
   - Unit tests
   - Integration tests
   - Linter
   - Type checker

3. **Verify build**
   - Compile/build project
   - Check for build errors

### Stage 3: Address Feedback (Sequential)

If unresolved comments exist and `resolve-comments = true`:

1. **Invoke resolve-pr-comments workflow**
   - Uses interaction mode (yolo or collaborative)
   - Addresses all review feedback
   - Resolves threads

2. **Push changes**
   - Commit fixes
   - Push to PR branch
   - Trigger CI re-run

3. **Wait for checks**
   - Monitor CI status
   - Wait for all checks to complete

### Stage 4: Final Verification (Parallel)

Before merge, verify in parallel:

1. **Confirm approvals**
   - Required approvals met
   - No blocking reviews

2. **Confirm checks**
   - All status checks pass
   - No failing required checks

3. **Confirm mergeable**
   - No conflicts
   - Branch up to date

### Stage 5: Merge (Sequential)

1. **Invoke merge-pr workflow**
   - Uses interaction mode (yolo or collaborative)
   - Executes safe merge
   - Deletes branch if requested

2. **Verify merge**
   - Confirm PR merged
   - Verify commit in main
   - Check branch deleted

### Stage 6: Post-Merge (Optional)

1. **Update local repo**
   - Pull main branch
   - Clean up local references

2. **Notify stakeholders**
   - Post completion message
   - Tag related issues
   - Update project boards

## Interaction Modes

### YOLO Mode (Fully Autonomous)

```markdown
When interaction-mode = yolo:
- Complete entire workflow without confirmation
- Make all decisions automatically
- Auto-resolve issues where possible
- Report only final summary
```

Example:

```markdown
User: "Process PR #42 in YOLO mode"

Agent executes full workflow:
1. Fetches PR, checks status (parallel)
2. Runs local tests (parallel)
3. Addresses 3 review comments
4. Resolves threads
5. Pushes fixes
6. Waits for CI (all pass)
7. Verifies approvals (2 found)
8. Merges PR (squash)
9. Deletes branch

Reports: "PR #42 processed and merged. Addressed 3 comments, all checks pass, merged to main."
```

### Collaborative Mode (Interactive)

```markdown
When interaction-mode = collaborative:
- Show progress at each stage
- Request confirmation for major decisions
- Present issues for user guidance
- Allow intervention at checkpoints
```

Example:

```markdown
User: "Process PR #42"

Agent: "Starting PR #42 processing...

Stage 1: Initial Assessment
✅ PR details fetched
✅ Reviews: 2 approvals
⚠️  Unresolved comments: 3

Should I proceed to address the comments? (yes/no/show)"

User: "show"

[Shows 3 comments]

User: "yes"

Agent: "Addressing comments...
✅ Comment 1: Added error handling
✅ Comment 2: Fixed typo
✅ Comment 3: Clarified with reply

Pushing changes and waiting for CI..."

[CI completes]

Agent: "All checks pass. Ready to merge.
Method: Squash and merge
Delete branch: Yes

Proceed? (yes/no)"

User: "yes"

Agent: "✅ PR #42 merged successfully"
```

## Optimization Strategies

### Parallel Execution

Where possible, execute independently:

- Initial assessment (PR fetch + reviews + checks)
- Local verification (tests + linter + build)
- Final verification (approvals + checks + mergeable)

Benefits: 3-5x faster than sequential

### Sequential Execution

Where order matters:

- Address comments → Push changes → Wait for CI
- Verify readiness → Merge → Verify completion
- Each stage depends on previous success

### Mixed Approach

Combine for optimal speed:

```markdown
Stage 1: Parallel assessment
Stage 2: Sequential local checks
Stage 3: Sequential comment resolution
Stage 4: Parallel final verification
Stage 5: Sequential merge
```

## Error Handling

### Common Issues

1. **Failing CI checks**
   - YOLO: Wait for checks to pass or report blocker
   - Collaborative: Show failures, ask to investigate or wait
   - Auto-retry if transient

2. **Unresolved comments**
   - YOLO: Auto-resolve if trivial, otherwise address
   - Collaborative: Show comments, get approval for resolution
   - Invoke resolve-pr-comments workflow

3. **Merge conflicts**
   - YOLO: Report blocker (cannot auto-resolve conflicts)
   - Collaborative: Suggest resolution strategies
   - Requires manual intervention

4. **Missing approvals**
   - YOLO: Report blocker, cannot proceed
   - Collaborative: Show who can approve, ask to request
   - Wait for approvals

5. **Local test failures**
   - YOLO: Investigate and fix if possible
   - Collaborative: Show failures, ask for guidance
   - May skip if only remote checks required

## Workflow Variations

### Quick Merge (Minimal Checks)

For low-risk PRs:

```markdown
Parameters:
  run-local-checks: false
  resolve-comments: false (assume resolved)
  
Workflow:
1. Verify CI and approvals
2. Merge immediately
```

### Thorough Review (All Checks)

For high-risk PRs:

```markdown
Parameters:
  run-local-checks: true
  resolve-comments: true
  interaction-mode: collaborative
  
Workflow:
1. Full local verification
2. Interactive comment resolution
3. Manual merge confirmation
```

### Batch Processing (Multiple PRs)

For processing many PRs:

```markdown
Parameters:
  pr-number: [42, 43, 44, 45]
  interaction-mode: yolo
  
Workflow:
1. Process PRs in parallel using parallel-execution
2. Each PR follows full process-pr workflow
3. Report summary of all PRs
```

## Best Practices

1. **Use appropriate mode**: YOLO for routine, collaborative for critical
2. **Run local checks**: Catch issues before CI
3. **Address comments promptly**: Don't skip feedback
4. **Verify before merge**: Never rush the final checks
5. **Clean up branches**: Delete after merge
6. **Monitor CI**: Ensure checks complete before merge
7. **Document decisions**: Log choices made during process
8. **Consistent method**: Use same merge method across repo

## Safety Guardrails

Always enforce:

- ✅ Required approvals received
- ✅ All required checks pass
- ✅ No merge conflicts
- ✅ PR is actually open
- ✅ Targeting correct base branch

Never:

- ❌ Merge with failing tests
- ❌ Skip required approvals
- ❌ Override branch protection
- ❌ Ignore unresolved blockers
- ❌ Merge conflicted PRs

## Output Format

### YOLO Mode Output

```markdown
TASK: Process PR #42
STATUS: Complete

STAGES COMPLETED:
✅ Stage 1: Initial Assessment (3 checks)
✅ Stage 2: Local Verification (tests, lint, build)
✅ Stage 3: Address Feedback (3 comments resolved)
✅ Stage 4: Final Verification (all pass)
✅ Stage 5: Merge (squash method)

SUMMARY:
- PR #42: "Add authentication middleware"
- Comments addressed: 3
- Files changed: 4
- Tests: All passing
- Approvals: 2 (alice, bob)
- Merge method: Squash
- Branch: feature-auth (deleted)

RESULT: Successfully merged to main
TIME: 8 minutes (5min CI wait)
```

### Collaborative Mode Output

```markdown
PR Processing: #42

Current Stage: 3/5 - Addressing Feedback
Progress: [████████░░] 80%

✅ Stage 1: Initial Assessment
✅ Stage 2: Local Verification
⏳ Stage 3: Addressing Feedback (2/3 comments)
⬜ Stage 4: Final Verification
⬜ Stage 5: Merge

Current Action: Resolving review thread on auth.ts:42
Waiting for: User confirmation to proceed

Next: 1 more comment, then final checks
```

## Integration Examples

### Example 1: Single PR Full Process

```markdown
User: "Process PR #42 end-to-end"

Execution:
- Uses: process-pr (this workflow)
- Mode: collaborative (default)
- Stages: All 5 stages
- Output: Interactive progress updates
```

### Example 2: Batch PR Processing

```markdown
User: "Process all approved PRs"

Execution:
1. List open PRs
2. Filter for approved PRs
3. Use parallel-execution to spawn:
   - process-pr for PR #42
   - process-pr for PR #43
   - process-pr for PR #44
4. Each uses yolo mode
5. Report summary of all
```

### Example 3: PR Pipeline

```markdown
User: "Set up automated PR pipeline"

Execution:
1. Monitor for new reviews/approvals
2. When PR approved:
   - Trigger process-pr in yolo mode
   - Auto-merge if all checks pass
3. Notify on completion
```

## Quick Reference

```markdown
PURPOSE:
  End-to-end PR processing from review to merge

COMPOSITION:
  parallel-execution + sequential-execution + pull-request-tool +
  resolve-pr-comments + merge-pr + (yolo OR collaborative)

MODES:
  YOLO:          Fully autonomous end-to-end
  Collaborative: Interactive with checkpoints

STAGES:
  1. Initial Assessment (parallel)
  2. Local Verification (sequential)
  3. Address Feedback (sequential)
  4. Final Verification (parallel)
  5. Merge (sequential)

PARAMETERS:
  pr-number:        Required (single or array)
  repository:       Required (owner/repo)
  interaction-mode: yolo or collaborative
  merge-method:     merge/squash/rebase
  delete-branch:    true (default)
  run-local-checks: true (default)
  resolve-comments: true (default)

OPTIMIZATION:
  - Parallel where possible (assessment, verification)
  - Sequential where needed (comments, merge)
  - Mixed for optimal speed

SAFETY:
  Always verify:
  - Required approvals
  - All checks pass
  - No conflicts
  - Correct base branch
  
  Never:
  - Merge with failing tests
  - Skip approvals
  - Override protection
```

## Related Skills

- **pull-request-tool**: For PR interaction, checks, and merge operations
- **resolve-pr-comments**: For handling review feedback during PR processing
- **merge-pr**: For executing merge with proper verification and cleanup
- **handle-pr-feedback**: For triaging feedback severity and routing decisions
- **update-work-item**: For updating work item status when PR is merged
- **parallel-execution**: For concurrent assessment of PR readiness
- **sequential-execution**: For ordered workflow phases (assess → resolve → merge)
