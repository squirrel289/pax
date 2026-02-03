# PAX Skills Library - Real-World Examples

Practical examples of using Agent Skills for automation.

## Table of Contents

1. [PR Processing Examples](#pr-processing-examples)
2. [Batch Operations](#batch-operations)
3. [Analysis and Review](#analysis-and-review)
4. [Workflow Automation](#workflow-automation)
5. [Advanced Compositions](#advanced-compositions)

---

## PR Processing Examples

### Example 1: Simple PR Merge

**Scenario**: Merge a ready PR

**Prompt**:

```markdown
"Merge PR #42 in owner/repo"
```

**Execution**:

```markdown
Skill: merge-pr
Mode: collaborative (default)

Steps:
1. Fetch PR #42 details
2. Check mergeable status
3. Verify approvals (2 found)
4. Check CI status (all pass)
5. Show summary to user
6. Ask for confirmation
7. Merge with squash method
8. Delete branch

Output: "PR #42 merged successfully"
```

### Example 2: Autonomous PR Processing

**Scenario**: Fully automated PR handling

**Prompt**:

```markdown
"Process PR #42 in owner/repo using YOLO mode"
```

**Execution**:

```markdown
Skill: process-pr
Mode: yolo

Steps:
1. Parallel assessment:
   - Fetch PR details
   - Check reviews (2 approvals)
   - Verify CI (8/8 passing)
2. Run local tests (all pass)
3. Check for comments (3 unresolved)
4. Resolve comments:
   - "Add error handling" → Added try/catch
   - "Fix typo" → Fixed
   - "LGTM" → Acknowledged
5. Push fixes
6. Wait for CI (all pass)
7. Merge automatically
8. Delete branch

Output: "PR #42 processed and merged. Addressed 3 comments."
Time: 6 minutes
```

### Example 3: Interactive Comment Resolution

**Scenario**: Collaborate on addressing feedback

**Prompt**:

```markdown
"Help me resolve comments on PR #42"
```

**Execution**:

```markdown
Skill: resolve-pr-comments
Mode: collaborative

Dialog:
Agent: "Found 5 unresolved comments. Starting with comment 1/5:

Comment from @alice on auth.ts:42:
'This timeout should be configurable'

Proposed action:
- Extract to AUTH_TIMEOUT constant
- Add to config file
- Update documentation

Approve? (yes/no/modify)"

User: "modify - make it an environment variable instead"

Agent: "Updated approach:
- Use process.env.AUTH_TIMEOUT
- Default to 30000
- Add to .env.example

Proceed? (yes/no)"

User: "yes"

Agent: [makes changes]
"Change complete. Resolving thread..."
"Comment 1/5 resolved. Moving to comment 2/5..."
```

---

## Batch Operations

### Example 4: Process Multiple PRs

**Scenario**: Process all approved PRs at once

**Prompt**:

```markdown
"Process all approved PRs in owner/repo"
```

**Execution**:

```markdown
Skills: parallel-execution + process-pr
Mode: yolo

Steps:
1. List all open PRs
2. Filter for approved status
3. Found: PR #41, #42, #43
4. Launch parallel:
   - process-pr(#41, yolo)
   - process-pr(#42, yolo)
   - process-pr(#43, yolo)
5. Each PR processes independently:
   #41: 2 comments → merged
   #42: 0 comments → merged
   #43: CI failing → reported (skipped)

Output:
"Processed 3 PRs:
✅ #41 - Merged (addressed 2 comments)
✅ #42 - Merged (no issues)
❌ #43 - Skipped (failing tests)

2/3 successfully merged"

Time: 5 minutes (parallel execution)
```

### Example 5: Bulk Comment Resolution

**Scenario**: Resolve all comments across multiple PRs

**Prompt**:

```markdown
"Resolve all my unresolved PR comments in owner/repo"
```

**Execution**:

```markdown
Skills: parallel-execution + resolve-pr-comments
Mode: collaborative

Steps:
1. List my open PRs
2. Found: PR #40, #41, #42
3. Check each for unresolved threads
4. Parallel execution:
   PR #40: 2 threads
   PR #41: 0 threads (skip)
   PR #42: 3 threads
5. Interactive resolution:
   
[For PR #40]
Agent: "PR #40 has 2 comments. Process now? (yes/no)"
User: "yes"
[Resolves 2 comments with approval]

[For PR #42]
Agent: "PR #42 has 3 comments. Process now? (yes/no)"
User: "yes"
[Resolves 3 comments with approval]

Output: "Resolved 5 comments across 2 PRs"
```

---

## Analysis and Review

### Example 6: Codebase Security Analysis

**Scenario**: Analyze repository for security issues

**Prompt**:

```markdown
"Analyze security vulnerabilities in this codebase"
```

**Execution**:

```markdown
Skill: parallel-execution
Tasks: Multiple security perspectives

Parallel tasks:
1. Authentication analysis
   - Check auth flows
   - Verify token handling
   - Review session management

2. Input validation analysis
   - Find user input points
   - Check validation logic
   - Identify injection risks

3. Secrets analysis
   - Scan for hardcoded secrets
   - Check environment usage
   - Review .env handling

4. Dependency analysis
   - Check for vulnerable packages
   - Review update status
   - Identify outdated deps

Synthesis:
"Found 12 security issues:
- 3 High: Hardcoded API keys
- 5 Medium: Missing input validation
- 4 Low: Outdated dependencies

Detailed report: [...]"

Time: 2 minutes (vs 8 mins sequential)
```

### Example 7: Multi-Perspective Code Review

**Scenario**: Comprehensive PR review

**Prompt**:

```markdown
"Review PR #42 from all angles"
```

**Execution**:

```markdown
Skill: parallel-execution
Tasks: Different review perspectives

Parallel reviews:
1. Security review
   → Findings: 2 issues

2. Performance review
   → Findings: 1 N+1 query, 1 memory leak

3. Test coverage review
   → Findings: 3 untested functions

4. Architecture review
   → Findings: 1 abstraction violation

5. Code quality review
   → Findings: 5 lint violations

Synthesis:
"PR #42 Review Summary:

Security: ⚠️  2 issues
Performance: ⚠️  2 issues
Testing: ❌ Coverage gaps
Architecture: ⚠️  1 concern
Quality: ✅ Minor issues

Recommendation: Request changes

Priority fixes:
1. [Security] Sanitize user input
2. [Performance] Fix N+1 query
3. [Testing] Add tests for auth flow
"

Agent: "Should I post this review? (yes/no)"
```

---

## Workflow Automation

### Example 8: Automated Release Pipeline

**Scenario**: Full release automation

**Prompt**:

```markdown
"Create release v2.1.0"
```

**Execution**:

```markdown
Skill: release-pipeline (custom workflow)
Composed: sequential-execution + parallel-execution
Mode: yolo

Steps:
1. Verify main branch
   ✅ On main, up to date

2. Run full test suite
   ✅ All 247 tests pass

3. Parallel build:
   - Build for Linux ✅
   - Build for macOS ✅
   - Build for Windows ✅

4. Update version
   ✅ Updated to 2.1.0

5. Generate changelog
   ✅ Generated from commits

6. Create git tag
   ✅ Created v2.1.0

7. Push tag
   ✅ Pushed to origin

8. Create GitHub release
   ✅ Release published

9. Upload artifacts
   ✅ 3 binaries uploaded

10. Notify team
    ✅ Slack notification sent

Output: "Release v2.1.0 published successfully"
Time: 4 minutes
```

### Example 9: Dependency Update Workflow

**Scenario**: Update and test dependencies

**Prompt**:

```markdown
"Update all dependencies and create PR"
```

**Execution**:

```markdown
Skill: dependency-updater (custom workflow)
Composed: sequential-execution + parallel-execution
Mode: collaborative

Steps:
1. Check for updates
   Found: 15 packages with updates

Agent: "15 updates available:
- 3 major (breaking)
- 7 minor (features)
- 5 patch (fixes)

Update all or selective? (all/selective/major-only)"

User: "selective - skip major updates"

2. Update packages
   ✅ Updated 12 packages (7 minor + 5 patch)

3. Parallel testing:
   - Unit tests ✅
   - Integration tests ✅
   - E2E tests ✅

4. Create branch
   ✅ Created: deps-update-2026-02-02

5. Commit changes
   ✅ Committed with changelog

6. Push branch
   ✅ Pushed to origin

7. Create PR
   ✅ PR #44 created

Output: "Created PR #44 with 12 dependency updates"
```

---

## Advanced Compositions

### Example 10: Smart PR Router

**Scenario**: Route PRs to appropriate reviewers

**Prompt**:

```markdown
"Route new PRs to correct reviewers"
```

**Execution**:

```markdown
Skill: pr-router (custom workflow)
Composed: parallel-execution + pull-request-tool
Mode: yolo

Steps:
1. Fetch new PRs (last 24h)
   Found: PR #45, #46, #47

2. For each PR, parallel analysis:
   
PR #45:
- Files: src/auth/* (auth team)
- Size: Large (2 reviewers needed)
- Assigns: @alice, @bob

PR #46:
- Files: docs/* (any team)
- Size: Small (1 reviewer)
- Assigns: @carol

PR #47:
- Files: src/api/*, src/db/* (backend team)
- Size: Medium (1 reviewer)
- Complexity: High (senior needed)
- Assigns: @dave

3. Apply assignments
   ✅ All PRs assigned

4. Add labels
   ✅ Labels applied

5. Notify reviewers
   ✅ Notifications sent

Output: "Routed 3 PRs to appropriate reviewers"
```

### Example 11: Continuous Integration Monitor

**Scenario**: Monitor and fix failing CI

**Prompt**:

```markdown
"Monitor CI and auto-fix common failures"
```

**Execution**:

```markdown
Skill: ci-monitor (custom workflow)
Composed: parallel-execution + sequential-execution
Mode: yolo

Monitoring loop:
1. Check all PRs for failing CI

Found failures:
- PR #40: Linting errors
- PR #41: Test timeouts
- PR #42: Build failure

2. Parallel auto-fix attempts:

PR #40 (Linting):
- Run auto-formatter
- Fix import ordering
- Commit fixes
- Push changes
- ✅ CI now passing

PR #41 (Timeouts):
- Analyze slow tests
- Increase timeout values
- Commit changes
- Push changes
- ✅ CI now passing

PR #42 (Build):
- Error: Missing dependency
- ❌ Cannot auto-fix
- Posted comment: "@author Build fails due to missing dep"

Output:
"CI Monitor Results:
✅ Fixed: PR #40, #41
❌ Needs attention: PR #42 (build)"
```

### Example 12: Monorepo Sync Workflow

**Scenario**: Sync changes across monorepo packages

**Prompt**:

```markdown
"Sync API changes to all client packages"
```

**Execution**:

```markdown
Skill: monorepo-sync (custom workflow)
Composed: parallel-execution + sequential-execution
Mode: collaborative

Steps:
1. Detect API changes
   Found: 3 breaking changes in api/

Agent: "Detected breaking API changes:
1. auth.login() → now returns Promise
2. user.get() → renamed to user.fetch()
3. config.timeout → moved to config.http.timeout

Affected packages:
- web-client
- mobile-client
- admin-client

Proceed with updates? (yes/no/show-details)"

User: "show-details"

[Shows file-by-file changes]

User: "yes"

2. Parallel updates:

web-client:
- Update auth calls (3 files)
- Update user calls (2 files)
- Update config (1 file)
- Run tests ✅

mobile-client:
- Update auth calls (2 files)
- Update user calls (1 file)
- Update config (1 file)
- Run tests ✅

admin-client:
- Update auth calls (1 file)
- Update config (1 file)
- Run tests ✅

3. Create PRs
   ✅ PR #48: web-client sync
   ✅ PR #49: mobile-client sync
   ✅ PR #50: admin-client sync

Output: "Synced API changes across 3 packages.
Created PRs #48, #49, #50"

Time: 3 minutes (parallel execution)
```

---

## Quick Tips for Each Example

### PR Processing

- Use `yolo` mode for routine merges
- Use `collaborative` for complex PRs
- Always verify CI before merging

### Batch Operations

- Leverage `parallel-execution` for speed
- Filter carefully before batch operations
- Review results summary

### Analysis

- Run multiple analyses in parallel
- Synthesize findings for coherent report
- Prioritize findings by severity

### Automation

- Use sequential for ordered workflows
- Use parallel for independent tasks
- Add checkpoints for critical steps

### Advanced

- Combine multiple patterns
- Build domain-specific workflows
- Document custom compositions

---

## Using These Examples

1. **Copy the prompt**: Start with exact prompts
2. **Adjust parameters**: Change PR numbers, repos, etc.
3. **Choose mode**: Pick yolo or collaborative
4. **Observe results**: Learn from execution
5. **Customize**: Modify for your needs

## Next Steps

- Try simple examples first (1-3)
- Progress to batch operations (4-5)
- Explore advanced compositions (10-12)
- Build your own custom workflows
- Share your examples with the community

Happy automating!
