---
title: PR Management Backend Parity Validation Report
description: Cross-backend analysis of PR management operations, identifying gaps in implementation across copilot-pull-request and gh-pr-review
audience: agents, architects, reviewers
version: 1.0
status: draft
date: 2026-02-25
---

## Executive Summary

**Validation Date**: 2026-02-25  
**Status**: ⚠️ **INCOMPLETE IMPLEMENTATIONS IDENTIFIED**

### Key Findings

1. **Interface Coverage**: Both backends claim 100% coverage of `PR_MANAGEMENT_INTERFACE.md` operations
2. **Actual Coverage**:
   - ✅ **copilot-pull-request**: 4/6 operations confirmed mapped to specific APIs
   - ✅ **gh-pr-review**: 5/6 operations have CLI examples, 1 lacks clear implementation
   - ⚠️ **Undocumented divergences**: Check-status operation has ambiguous implementation
3. **Missing Implementations**:
   - `check-status` operation in copilot-pull-request: No clear API mapping documented
   - `check-status` operation in gh-pr-review: Partial implementation documented
4. **Overall Risk**: **MEDIUM** - Both backends mostly functional but check-status needs clarification

---

## Canonical Interface (Source of Truth)

### PR_MANAGEMENT_INTERFACE.md

**Defined Operations**:

| #   | Operation          | Parameters                                         | Expected Output                                       | Status       |
| --- | ------------------ | -------------------------------------------------- | ----------------------------------------------------- | ------------ |
| 1   | `fetch-pr-details` | pr-number, repository                              | PR metadata, branch info, check status, review status | ✅ Canonical |
| 2   | `list-comments`    | pr-number, repository, [filters]                   | Review threads, comments, resolved status             | ✅ Canonical |
| 3   | `reply-comment`    | pr-number, thread-id, body, repository             | Success/failure, comment ID                           | ✅ Canonical |
| 4   | `resolve-thread`   | pr-number, thread-id, repository                   | Success/failure, thread status                        | ✅ Canonical |
| 5   | `merge-pr`         | pr-number, repository, merge-method, delete-branch | Success/failure, commit SHA, branch status            | ✅ Canonical |
| 6   | `check-status`     | pr-number, repository                              | CI status, required checks, pending                   | ⚠️ Ambiguous |

---

## Backend 1: copilot-pull-request

**Type**: API-based  
**Compatibility**: Copilot agent environments  
**Backend Availability**: Requires Copilot API access

### Operation Coverage

#### 1. fetch-pr-details ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: fetch-pr-details
pr-number: 42
repository: owner/repo

# Backend API:
Tools Used:
  - github-pull-request_activePullRequest
  - github-pull-request_openPullRequest

Fields Extracted:
  - title, state, author
  - mergeable, mergeStateStatus
  - statusCheckRollup (CI checks)
  - reviewDecision (APPROVED/CHANGES_REQUESTED/PENDING)

# Documented in: SKILL.md line 23-26
```

**Verification**: ✅ Clear API mapping, tool names documented

---

#### 2. list-comments ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: list-comments
pr-number: 42
repository: owner/repo
filters:
  unresolved: true

# Backend API:
Tool Used:
  - github-pull-request_activePullRequest (field: reviewThreads)

Fields Extracted:
  - reviewThreads (array of threads)
  - thread-id (PRRT_abc123 format)
  - body (comment text)
  - isResolved (thread state)

# Documented in: SKILL.md line 28-31
```

**Verification**: ✅ Clear API mapping, filter support documented

---

#### 3. reply-comment ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: reply-comment
pr-number: 42
thread-id: PRRT_abc123
body: "Thanks for the feedback!"
repository: owner/repo

# Backend API:
Tool Used:
  - pull_request_review_write (action: add comment)

Parameters:
  - owner, repo, pull_number, thread_id, body

# Documented in: SKILL.md line 33-38
```

**Verification**: ✅ Clear API mapping, tool name documented

---

#### 4. resolve-thread ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: resolve-thread
pr-number: 42
thread-id: PRRT_abc123
repository: owner/repo

# Backend API:
Tool Used:
  - pull_request_review_write (action: resolve thread)

# Documented in: SKILL.md line 40-44
```

**Verification**: ✅ Clear API mapping, tool name documented

---

#### 5. merge-pr ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: merge-pr
pr-number: 42
repository: owner/repo
merge-method: squash
delete-branch: true

# Backend API:
Tool Used:
  - pull_request_review_write (action: merge)

Parameters:
  - merge_method: SQUASH | MERGE | REBASE
  - delete_branch_on_merge: boolean

# Documented in: SKILL.md line 46-51
```

**Verification**: ✅ Clear API mapping, tool name documented

---

#### 6. check-status ⚠️

**Status**: **MISSING / UNDOCUMENTED**

```yaml
operation: check-status
pr-number: 42
repository: owner/repo

# Expected Output (from interface):
{
  "mergeable": true|false,
  "mergeStateStatus": "CLEAN|DIRTY|BLOCKED|UNKNOWN",
  "statusCheckRollup": [
    { "name": "CI", "state": "SUCCESS|FAILURE|PENDING" }
  ]
}

# Backend API:
Tool Used: ???
  OPTION A: github-pull-request_activePullRequest
            (same tool as fetch-pr-details?)
  OPTION B: Separate tool for polling? Not documented.

# Documented in: SKILL.md - NO MENTION
# Description says operation "check and wait for CI/status checks"
# but no API mapping provided
```

**Verification**: ❌ **NOT DOCUMENTED**

**Issue**: The copilot-pull-request skill claims to support check-status in `PR_MANAGEMENT_INTERFACE.md` (line 11: "Check and wait for CI/status checks"), but provides no API mapping in the skill's own documentation.

**Recommendation**: Either:

1. Document the API mapping for check-status (likely reuse of activePullRequest), OR
2. If polling is needed, document separate tool or polling logic, OR
3. Remove check-status from copilot-pull-request scope if it's not actually implemented

---

### Summary: copilot-pull-request

| Operation        | Implemented | API Mapped | Status                    |
| ---------------- | ----------- | ---------- | ------------------------- |
| fetch-pr-details | ✅ Yes      | ✅ Yes     | Fully implemented         |
| list-comments    | ✅ Yes      | ✅ Yes     | Fully implemented         |
| reply-comment    | ✅ Yes      | ✅ Yes     | Fully implemented         |
| resolve-thread   | ✅ Yes      | ✅ Yes     | Fully implemented         |
| merge-pr         | ✅ Yes      | ✅ Yes     | Fully implemented         |
| **check-status** | ❓ Unclear  | ❌ No      | **Missing documentation** |

**Coverage**: 5/6 operations clearly implemented, 1 undocumented

---

## Backend 2: gh-pr-review

**Type**: CLI-based  
**Compatibility**: Any environment with GitHub CLI (`gh`)  
**Backend Availability**: Requires `gh` installed + authenticated

### Operation Coverage

#### 1. fetch-pr-details ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: fetch-pr-details
pr-number: 42
repository: owner/repo

# Backend CLI:
Command: gh pr view <number> --json title,state,author,mergeable,statusCheckRollup

Output Fields:
  - title, state, author
  - mergeable (true|false)
  - statusCheckRollup (array of checks)

# Documented in: SKILL.md line 37-40
```

**Verification**: ✅ Clear CLI command, example provided

---

#### 2. list-comments ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: list-comments
pr-number: 42
repository: owner/repo
filters:
  unresolved: true

# Backend CLI:
Command:
  gh pr-review review view -R owner/repo --pr <number>
  Filters:
    --unresolved
    --reviewer <login>
    --states APPROVED,CHANGES_REQUESTED,COMMENTED
    --not_outdated

Output Fields:
  - Review threads, comments
  - Thread state (resolved/unresolved)

# Documented in: SKILL.md line 42-50
```

**Verification**: ✅ Clear CLI command, filter examples provided

**Note**: Requires `gh-pr-review` extension (not built into core `gh`)

---

#### 3. reply-comment ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: reply-comment
pr-number: 42
thread-id: PRRT_abc123
body: "message"
repository: owner/repo

# Backend CLI:
Command: gh pr-review comments reply <pr-number> -R owner/repo \
  --thread-id <PRRT_...> \
  --body "Your reply message"

# Documented in: SKILL.md line 52-56
```

**Verification**: ✅ Clear CLI command provided

**Note**: Requires `gh-pr-review` extension

---

#### 4. resolve-thread ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: resolve-thread
pr-number: 42
thread-id: PRRT_abc123
repository: owner/repo

# Backend CLI:
Command: gh pr-review threads resolve -R owner/repo <pr-number> \
  --thread-id <PRRT_...>

Listing unresolved: gh pr-review threads list -R owner/repo <pr-number> --unresolved

# Documented in: SKILL.md line 58-65
```

**Verification**: ✅ Clear CLI command provided

**Note**: Requires `gh-pr-review` extension

---

#### 5. merge-pr ✅

**Status**: **FULLY IMPLEMENTED**

```yaml
operation: merge-pr
pr-number: 42
repository: owner/repo
merge-method: squash
delete-branch: true

# Backend CLI:
Command: gh pr merge <number> --merge|--squash|--rebase [--auto] [--delete-branch]

Options: --merge (default merge commit)
  --squash (squash commits)
  --rebase (rebase and merge)
  --delete-branch (delete after merge)
  --auto (auto-merge when ready)

# Documented in: SKILL.md line 67-69
```

**Verification**: ✅ Clear CLI command provided

**Note**: Core `gh` feature, no extension needed

---

#### 6. check-status ✅

**Status**: **PARTIALLY IMPLEMENTED**

```yaml
operation: check-status
pr-number: 42
repository: owner/repo

# Expected Output:
{
  "mergeable": true|false,
  "mergeStateStatus": "CLEAN|DIRTY|BLOCKED|UNKNOWN",
  "statusCheckRollup": [...]
}

# Backend CLI:
Command:
  gh pr view <number> --json mergeable,mergeStateStatus,statusCheckRollup

Output Fields:
  - mergeable (boolean)
  - mergeStateStatus (string: CLEAN, DIRTY, BLOCKED, UNKNOWN)
  - statusCheckRollup (array of checks)

# Documented in: SKILL.md line 61-63
```

**Verification**: ✅ Clear CLI command, matches interface

**Note**: Essentially same data as fetch-pr-details, can be invoked separately for status polling

---

### Summary: gh-pr-review

| Operation        | Implemented | CLI Command                    | Status                                 |
| ---------------- | ----------- | ------------------------------ | -------------------------------------- |
| fetch-pr-details | ✅ Yes      | `gh pr view`                   | Fully implemented                      |
| list-comments    | ✅ Yes      | `gh pr-review review view`     | Fully implemented (requires extension) |
| reply-comment    | ✅ Yes      | `gh pr-review comments reply`  | Fully implemented (requires extension) |
| resolve-thread   | ✅ Yes      | `gh pr-review threads resolve` | Fully implemented (requires extension) |
| merge-pr         | ✅ Yes      | `gh pr merge`                  | Fully implemented                      |
| **check-status** | ✅ Yes      | `gh pr view`                   | Fully implemented                      |

**Coverage**: 6/6 operations implemented

---

## Parity Matrix

### Canonical Interface Operations

```markdown
| Operation        | copilot-pull-request | gh-pr-review   | Parity Status |
| ---------------- | -------------------- | -------------- | ------------- |
| fetch-pr-details | ✅ Implemented       | ✅ Implemented | ✅ EQUAL      |
| list-comments    | ✅ Implemented       | ✅ Implemented | ✅ EQUAL      |
| reply-comment    | ✅ Implemented       | ✅ Implemented | ✅ EQUAL      |
| resolve-thread   | ✅ Implemented       | ✅ Implemented | ✅ EQUAL      |
| merge-pr         | ✅ Implemented       | ✅ Implemented | ✅ EQUAL      |
| check-status     | ❓ UNDOCUMENTED      | ✅ Implemented | ⚠️ DIVERGENT  |

================================================================================
Total Coverage | 5/6 (83%) | 6/6 (100%) | UNEQUAL
```

---

## Divergences & Issues

### Issue 1: check-status Operation Undocumented in copilot-pull-request

**Severity**: MEDIUM

**Details**:

- `PR_MANAGEMENT_INTERFACE.md` lists "Check and wait for CI/status checks" as supported operation
- `copilot-pull-request/SKILL.md` does NOT document any API mapping for check-status
- `gh-pr-review/SKILL.md` clearly documents CLI command for check-status

**Impact**:

- Users calling `pull-request-tool` with `check-status` operation in Copilot environments may fail
- Workflows depending on check-status polling are unreliable

**Recommendation**:

1. Either document the API mapping for check-status in copilot-pull-request (likely same as fetch-pr-details)
2. Or update PR_MANAGEMENT_INTERFACE.md to clarify check-status is CLI-only

---

### Issue 2: gh-pr-review Requires Optional Extension

**Severity**: LOW

**Details**:

- Core `gh` CLI provides: fetch, merge operations
- Optional `gh-pr-review` extension provides: list-comments, reply-comment, resolve-thread
- Users without extension will fail on comment operations

**Impact**:

- No automatic fallback if extension not installed
- Silent failures possible

**Recommendation**:

- Document prerequisite: Warn users that `gh pr-review comments` operations require extension
- Or: Add fallback to GraphQL API if extension not available

---

### Issue 3: Workflow Skills Assume Both Backends Implement All Operations

**Severity**: MEDIUM

**Details**:

- `resolve-pr-comments` workflow calls `pull-request-tool` with list-comments + reply operations
- If running in copilot environment without proper API mapping, will fail
- If gh-pr-review backend chosen without extension, will fail

**Impact**:

- Workflow reliability unclear when backend selection happens
- Error messages may not clarify root cause

**Recommendation**:

- Add backend capability detection before operation dispatch
- Fail fast with clear error message if operation not supported by detected backend
- Example: "gh-pr-review backend selected but gh-pr-review extension not installed"

---

## Recommendations

### 1. Fix check-status Documentation (IMMEDIATE)

**Action**: Document API mapping for check-status in copilot-pull-request

**File**: `/Users/macos/dev/pax/skills/tools/copilot-pull-request/SKILL.md`

**Change**: Add section after merge-pr:

```markdown
### Check Status / Wait for Checks

operation: check-status
pr-number: 42
repository: owner/repo

Uses: github-pull-request_activePullRequest
(same API as fetch-pr-details, field: statusCheckRollup + mergeable)

For polling: Call repeatedly until statusCheckRollup shows all required checks passing
or mergeStateStatus equals CLEAN
```

**Or** create explicit polling documentation if different tools needed.

---

### 2. Update PR_MANAGEMENT_INTERFACE.md for Clarity

**Action**: Clarify which backends support which operations

**Change**: Add backend support table in interface spec

```markdown
## Backend Support Matrix

| Operation        | copilot-pull-request | gh-pr-review | Notes                                           |
| ---------------- | -------------------- | ------------ | ----------------------------------------------- |
| fetch-pr-details | ✅                   | ✅           | Both fully supported                            |
| list-comments    | ✅                   | ✅\*         | \*Requires gh-pr-review extension               |
| reply-comment    | ✅                   | ✅\*         | \*Requires gh-pr-review extension               |
| resolve-thread   | ✅                   | ✅\*         | \*Requires gh-pr-review extension               |
| merge-pr         | ✅                   | ✅           | Both fully supported                            |
| check-status     | ⚠️ (See note)        | ✅           | copilot: see copilot-pull-request documentation |
```

---

### 3. Add Backend Capability Detection to pull-request-tool

**Action**: Implement capability checking before operation dispatch

**Pseudocode**:

```python
def pull_request_tool(operation, params):
    backend = detect_backend()  # copilot-pull-request | gh-pr-review

    capabilities = CAPABILITIES[backend]
    if operation not in capabilities:
        raise Error(f"{operation} not supported by {backend} backend. "
                    f"Supported operations: {capabilities}")

    return BACKEND_IMPL[backend](operation, params)
```

---

### 4. Reduce Complexity: Clarify merge-pr, process-pr, resolve-pr-comments

**Action**: Document clear overlaps and intended use cases

**Analysis**:

| Skill                   | Purpose                                       | When to Use                               | Composes                                       |
| ----------------------- | --------------------------------------------- | ----------------------------------------- | ---------------------------------------------- |
| **resolve-pr-comments** | Address review threads one-by-one             | PR has comments, need systematic approach | pull-request-tool + execution                  |
| **handle-pr-feedback**  | Triage feedback by severity, auto-fix trivial | PR has feedback, need triage              | resolve-pr-comments + decision logic           |
| **merge-pr**            | Safely verify and merge PR                    | PR ready to merge                         | pull-request-tool + verification               |
| **process-pr**          | Full lifecycle: assess → fix → merge          | PR in review phase, process to completion | resolve-pr-comments + merge-pr + orchestration |

**Recommendation**: Document this clearly in skills-manifest.md. Clarify that:

- `resolve-pr-comments` is reusable building block
- `handle-pr-feedback` adds severity logic on top
- `process-pr` orchestrates full workflow (may be more than most users need)
- Single-operation workflows (`merge-pr` alone, etc.) are valid use cases

---

### 5. Add Integration Tests for Backend Parity

**Action**: Create test suite that validates both backends produce equivalent output

**Scope**:

- Test fetch-pr-details returns same fields from both backends
- Test list-comments returns same thread data from both backends
- Test merge succeeds/fails same way on both backends

**Why**: Prevent future divergence; ensure swappability

---

## Test Coverage Gaps

### copilot-pull-request

**Tested Operations**: Unknown (no test file found in skill directory)

**Needed Tests**:

- ✅ fetch-pr-details (list, filter, fields)
- ✅ list-comments (unresolved filtering, thread structure)
- ✅ reply-comment (thread-id mapping, body parsing)
- ✅ resolve-thread (idempotency, already-resolved handling)
- ✅ merge-pr (merge method selection, branch deletion)
- ⚠️ check-status (polling, timeout, CI check parsing)

---

### gh-pr-review

**Tested Operations**: Unknown (no test file found)

**Needed Tests**:

- ✅ fetch-pr-details (field parity with copilot backend)
- ✅ list-comments (extension detection, graceful failure if not installed)
- ✅ reply-comment (thread-id mapping, body parsing)
- ✅ resolve-thread (idempotency, already-resolved handling)
- ✅ merge-pr (field parity with copilot backend)
- ✅ check-status (polling simulation, timeout handling)

---

## Validation Checklist

- [ ] copilot-pull-request documents check-status API mapping
- [ ] gh-pr-review documents extension prerequisite clearly
- [ ] PR_MANAGEMENT_INTERFACE.md updated with backend support matrix
- [ ] pull-request-tool implements capability detection
- [ ] Integration tests added for both backends
- [ ] Workflow skills updated if backend divergence found
- [ ] Error messages improved for backend mismatch scenarios

---

## Conclusion

**Status**: Both backends are **mostly compatible** but **incomplete documentation** creates risk.

**Critical Issues**:

1. ⚠️ check-status operation undocumented in copilot-pull-request
2. ⚠️ gh-pr-review extension prerequisite not clearly communicated

**Positive Findings**:

1. ✅ Both backends implement 5-6 core operations
2. ✅ Interface abstraction working well
3. ✅ Workflows can compose tools cleanly

**Recommendation**: Complete documentation and add backend capability detection before workflows depend critically on both backends.

---

## Appendix: Full Command Reference

### copilot-pull-request Backend

```text
OPERATION: fetch-pr-details
API: github-pull-request_activePullRequest | openPullRequest
FIELDS: title, state, author, mergeable, statusCheckRollup, reviewDecision

OPERATION: list-comments
API: github-pull-request_activePullRequest (reviewThreads field)
FILTERS: unresolved, by-reviewer, by-state

OPERATION: reply-comment
API: pull_request_review_write (add comment action)
PARAMS: owner, repo, pull_number, thread_id, body

OPERATION: resolve-thread
API: pull_request_review_write (resolve thread action)
PARAMS: owner, repo, pull_number, thread_id

OPERATION: merge-pr
API: pull_request_review_write (merge action)
PARAMS: owner, repo, pull_number, merge_method, delete_branch_on_merge

OPERATION: check-status
API: ??? (UNDOCUMENTED)
```

### gh-pr-review Backend

```text
OPERATION: fetch-pr-details
CLI: gh pr view <number> --json title,state,author,mergeable,statusCheckRollup

OPERATION: list-comments
CLI: gh pr-review review view -R owner/repo --pr <number> [--unresolved] [--not_outdated]
REQUIRES: gh-pr-review extension

OPERATION: reply-comment
CLI: gh pr-review comments reply <pr-number> -R owner/repo --thread-id <id> --body "msg"
REQUIRES: gh-pr-review extension

OPERATION: resolve-thread
CLI: gh pr-review threads resolve -R owner/repo <pr-number> --thread-id <id>
REQUIRES: gh-pr-review extension

OPERATION: merge-pr
CLI: gh pr merge <number> --squash|--rebase|--merge [--delete-branch] [--auto]
REQUIRES: gh (built-in)

OPERATION: check-status
CLI: gh pr view <number> --json mergeable,mergeStateStatus,statusCheckRollup
REQUIRES: gh (built-in)
```

---

**Report Version**: 1.0  
**Generated**: 2026-02-25  
**Next Review**: After check-status documentation completed
