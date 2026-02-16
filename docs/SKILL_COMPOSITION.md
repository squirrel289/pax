# Skill Composition Guide

Learn how to combine Agent Skills into powerful, custom workflows.

## What is Skill Composition?

Skill composition is the practice of combining multiple simpler skills into more complex, domain-specific workflows.

**Benefits**:

- Reuse existing skills
- Build complex automations
- Maintain modularity
- Easy to test and modify

## Composition Principles

### 1. Atomic Skills are Building Blocks

The simplest skills do one thing well:

```markdown
Atomic Skills:
- pull-request-tool: Interact with GitHub PRs
- parallel-execution: Run tasks concurrently
- yolo: Autonomous execution mode
```

### 2. Workflows Compose Atomic Skills

Complex workflows combine atomic skills:

```tree
merge-pr (workflow):
├── pull-request-tool (verify status)
├── pull-request-tool (check approvals)
├── pull-request-tool (execute merge)
└── sequential-execution (orchestrate steps)
```

### 3. Workflows Can Compose Other Workflows

Build hierarchies of workflows:

```tree
process-pr (top-level workflow):
├── parallel-execution
├── resolve-pr-comments (workflow)
│   ├── pull-request-tool
│   └── sequential-execution
└── merge-pr (workflow)
    ├── pull-request-tool
    └── sequential-execution
```

## Composition Patterns

### Pattern 1: Sequential Composition

Chain skills where each depends on the previous:

```markdown
A → B → C → D

Example: Git Workflow
1. Make changes
2. Commit (needs changes)
3. Push (needs commit)
4. Create PR (needs push)
```

**Implementation**:

```markdown
Skill: git-workflow
Composes: sequential-execution
Steps:
  1. Validate changes exist
  2. Commit with message
  3. Push to remote
  4. Create PR via pull-request-tool
```

### Pattern 2: Parallel Composition

Run independent tasks simultaneously:

```plaintext
    A ─┐
    B ─┼─ All run together
    C ─┘

Example: Codebase Analysis
- Security scan
- Performance analysis
- Test coverage check
```

**Implementation**:

```markdown
Skill: codebase-analysis
Composes: parallel-execution
Tasks:
  - Security analysis (independent)
  - Performance analysis (independent)
  - Coverage analysis (independent)
Synthesis: Combine results after all complete
```

### Pattern 3: Conditional Composition

Choose skills based on conditions:

```plaintext
IF condition THEN skill_a ELSE skill_b

Example: Merge Strategy
IF risky_changes THEN collaborative ELSE yolo
```

**Implementation**:

```markdown
Skill: smart-merge
Logic:
  1. Analyze PR (detect risk level)
  2. IF risk > threshold:
       Use merge-pr with collaborative mode
     ELSE:
       Use merge-pr with yolo mode
```

### Pattern 4: Nested Composition

Workflows within workflows:

```tree
Top-Level Workflow
├── Sub-Workflow 1
│   ├── Skill A
│   └── Skill B
└── Sub-Workflow 2
    ├── Skill C
    └── Skill D
```

**Implementation**:

```markdown
Skill: process-pr
Composes:
  - parallel-execution (assessment phase)
  - resolve-pr-comments (workflow)
    ├── pull-request-tool
    └── sequential-execution
  - merge-pr (workflow)
    ├── pull-request-tool
    └── sequential-execution
```

### Pattern 5: Mode Injection (Aspect-Driven)

Inject interaction mode into workflows:

```markdown
Workflow + Aspect + Mode → Behavior

Example:
- process-pr + interaction-modes + yolo → Fully autonomous
- process-pr + interaction-modes + collaborative → Interactive
```

**Implementation**:

```markdown
Skill: any-workflow
Parameters:
  - interaction-mode: yolo | collaborative

Logic:
  Interaction handled by the interaction-modes aspect
  Decision points prompt or auto-execute based on mode
```

## Aspects and Decision Points

Aspects are reusable behavior patterns (for example, interaction-modes) that can be composed into any skill without duplicating logic.

- Aspect reference: [docs/ASPECTS.md](docs/ASPECTS.md)
- Decision point encoding: [docs/DECISION_POINT_ENCODING.md](docs/DECISION_POINT_ENCODING.md)

Decision points define where a workflow pauses for user input or auto-executes based on heuristics. Each decision point must:

- Present discrete options
- Always include a custom response option
- Resume the workflow with a recorded decision result

### Scripting Boundary

Favor scripts when deterministic behavior is desired and practical. Use skill composition for interactive or multi-skill orchestration.

- Guidance: [docs/SCRIPTING_BOUNDARY.md](docs/SCRIPTING_BOUNDARY.md)

## Case Study: Work Management Skill Suite

The work management skills demonstrate advanced composition patterns across a complete lifecycle: item creation → implementation → review → merge → finalization.

### 5-Layer Architecture

```tree
Layer 1: Foundations (External Services & Modes)
├── GitHub API (pull-request-tool facade)
├── Git CLI (branch operations)
└── interaction-modes aspect (yolo, collaborative)

Layer 2: Atomic Skills (Single Responsibility)
├── pull-request-tool (GitHub PR operations)
├── feature-branch-management (Git branch lifecycle)
└── parallel-execution / sequential-execution (execution orchestration)

Layer 3: Specialized Workflows (Single Domain)
├── resolve-pr-comments (address review feedback)
├── create-pr (generate PR from branch)
└── handle-pr-feedback (triage feedback severity)

Layer 4: Merge/Cleanup Workflows (Intermediate Orchestration)
├── merge-pr (merge with verification + branch cleanup)
└── finalize-work-item (archive item + branch cleanup)

Layer 5: Work Item Orchestration (Full Lifecycle)
├── create-work-item (initialize)
├── update-work-item (progress tracking + auto-invocation of branch/PR ops)
└── process-pr (full PR lifecycle: review → merge)
```

### Skill Dependency Matrix

| Skill | Depends On | Called By |
| ----- | ---------- | --------- |
| `feature-branch-management` | Git CLI | update-work-item, merge-pr, finalize-work-item, handle-pr-feedback |
| `create-pr` | pull-request-tool, feature-branch-management | update-work-item (auto on testing), user (manual) |
| `pull-request-tool` | GitHub API | create-pr, merge-pr, handle-pr-feedback, resolve-pr-comments, process-pr |
| `resolve-pr-comments` | pull-request-tool | handle-pr-feedback, process-pr (manual) |
| `handle-pr-feedback` | pull-request-tool, resolve-pr-comments, update-work-item | process-pr, user (manual) |
| `merge-pr` | pull-request-tool, feature-branch-management | process-pr, user (manual) |
| `update-work-item` | feature-branch-management, create-pr | user (manual), handle-pr-feedback (on revert) |
| `create-work-item` | — | user (manual) |
| `finalize-work-item` | feature-branch-management | user (manual) |
| `process-pr` | handle-pr-feedback, merge-pr | user (manual) |

### Full Lifecycle Example

**Scenario**: Work item #60 "Implement FilterAdapter" from creation to merged

```ascii-tree
Phase 1: Create Item
  User invokes: create-work-item
    ├─ Work item status: not_started
    ├─ Metadata created (id=60, title, effort)
    └─ Related skills documented

Phase 2: Start Implementation
  User invokes: update-work-item status=in_progress
    ├─ Auto-invokes: feature-branch-management create feature/60-filter-adapter
    ├─ Feature branch checked out locally
    ├─ Work item.feature_branch = "feature/60-filter-adapter"
    └─ Related skills documented

Phase 3: Implement & Commit
  User makes git commits
    ├─ Work item.related_commits += <latest-sha>
    └─ (update-work-item tracks progress)

Phase 4: Ready for Review
  User invokes: update-work-item status=testing
    ├─ Auto-invokes: feature-branch-management sync --base=main
    │   ├─ Fetches origin/main
    │   └─ Rebases local branch on main
    ├─ Auto-invokes: create-pr work_item=60
    │   ├─ Title: "60: Implement FilterAdapter"
    │   ├─ Description auto-populated from notes + commits
    │   ├─ PR created on GitHub
    │   └─ Work item.pr_number = 123, .pr_url = "https://..."
    └─ Related skills documented

Phase 5A: Good Feedback (Minor Changes)
  Reviewer comments requesting docs
    ├─ Author invokes: resolve-pr-comments pr_number=123
    │   ├─ Reviews comments
    │   ├─ Commits fixes
    │   └─ Updates PR
    └─ Reviewer approves

Phase 5B: Major Feedback (Rework)
  Reviewer requests design change
    ├─ Author invokes: handle-pr-feedback pr_number=123
    │   ├─ Classifies as "Major"
    │   ├─ Invokes: update-work-item status=in_progress (revert)
    │   │   └─ Back to implementation phase (Phase 3)
    │   ├─ Work item status reverted
    │   └─ Branch still exists for rework
    └─ Author re-implements...

Phase 6: Merge
  After approval:
    ├─ User invokes: merge-pr pr_number=123
    │   ├─ Verifies all checks pass
    │   ├─ Executes merge (default: squash)
    │   ├─ Auto-invokes: feature-branch-management cleanup
    │   │   ├─ Deletes local branch
    │   │   └─ Deletes remote branch (origin/<branch>)
    │   └─ Work item.status → completed
    └─ Related skills documented

Phase 7: Finalize
  User invokes: finalize-work-item work_item=60
    ├─ Archives work item
    ├─ Auto-invokes: feature-branch-management cleanup (if not cleaned)
    ├─ Records completion date
    ├─ Work item.status → archived
    └─ Related skills documented
```

### Key Composition Patterns Used

1. **Mode Injection** (Layer 5 → Layers 1-4):
   - Work item orchestration doesn't know if merge-pr will run in `yolo` or `collaborative` mode
   - Mode parameter flows through all composed skills automatically

2. **Auto-Invocation** (Status Transitions):
   - `update-work-item` auto-invokes `feature-branch-management create` on `not_started` → `in_progress`
   - `update-work-item` auto-invokes `feature-branch-management sync` + `create-pr` on `in_progress` → `testing`
   - `merge-pr` auto-invokes `feature-branch-management cleanup` on successful merge
   - Eliminates manual coordination steps

3. **Feedback Loops** (Error Handling):
   - `handle-pr-feedback` classifies severity dynamically
   - Routes to: `resolve-pr-comments` (minor), `update-work-item` revert (major), escalate (blocker)
   - Decision logic encapsulated in single skill

4. **Layered Delegation** (Separation of Concerns):
   - Layer 5 (update-work-item) doesn't know git details; delegates to Layer 2 (branch-management)
   - Layer 4 (merge-pr) doesn't know PR details; delegates to Layer 2 (pull-request-tool)
   - Each layer has single responsibility

5. **Parallel Assessment** (Where Applicable):
   - `process-pr` can use `parallel-execution` for simultaneous assessment (ci checks, approval status, comment count)
   - Once parallel assessment done, sequential execution (resolve → merge)

### DRY Principle: Branch Operations

All skills needing branch operations use **single** `feature-branch-management` skill:

```ascii-tree
update-work-item    ──┐
merge-pr            ──┤──→ feature-branch-management (single source of truth)
finalize-work-item  ──┘
handle-pr-feedback  
```

Benefits:

- Bug fix in branch sync logic fixes all 4 consumers
- New branch operation added once; used everywhere
- Consistent branch naming and cleanup logic

### When NOT to Compose

Sometimes simpler is better:

```markdown
DON'T do this:
  update-work-item
    ├─ create-work-item
    └─ create-pr
  (Items can't update if not created)

DO this instead:
  Each skill is independent + focused
  Users choose which to invoke when
```

## Building a New Workflow

### Step 1: Identify Requirements

Define what the workflow should do:

```markdown
Example: automated-release

Requirements:
- Run all tests
- Build artifacts
- Update version
- Create git tag
- Push to registry
- Create release notes
```

### Step 2: Break Down into Skills

Map to existing skills or create new ones:

```markdown
automated-release breakdown:
1. Run tests → Use: test-runner (new skill)
2. Build artifacts → Use: build-system (new skill)
3. Update version → Use: version-bumper (new skill)
4. Create tag → Use: git-operations (existing)
5. Push to registry → Use: registry-push (new skill)
6. Release notes → Use: gh-release (new skill)
```

### Step 3: Determine Execution Flow

Decide on sequential vs parallel:

```markdown
automated-release flow:

Phase 1 (Sequential):
  1. Run tests (must pass before continuing)

Phase 2 (Parallel):
  2a. Build artifacts
  2b. Generate release notes

Phase 3 (Sequential):
  3. Update version
  4. Create git tag
  5. Push to registry
  6. Create GitHub release
```

### Step 4: Choose Interaction Mode

Select appropriate mode:

```markdown
For automated-release:
- Use yolo mode (well-defined, low-risk)
- Add collaborative option for first-time releases
```

### Step 5: Document Composition

Create SKILL.md:

```markdown
---
name: automated-release
description: Build, version, and release software automatically
category: workflow
composed-from:
  - test-runner
  - build-system
  - version-bumper
  - git-operations
  - registry-push
  - gh-release
  - parallel-execution
  - sequential-execution
  - yolo
---

# Automated Release

[Full documentation...]
```

## Real-World Examples

### Example 1: PR Review Pipeline

**Goal**: Comprehensive PR review before merge

```markdown
Skill: pr-review-pipeline
Composed from:
  - parallel-execution (run checks)
  - code-quality (new skill)
  - security-scan (new skill)
  - test-coverage (new skill)
  - pull-request-tool (post feedback)
  - collaborative (interaction mode)

Flow:
1. Parallel checks:
   - Code quality analysis
   - Security scan
   - Test coverage check
2. Synthesize findings
3. Post review comments (pull-request-tool)
4. Interactive approval (collaborative)
```

### Example 2: Multi-Repo Deployment

**Goal**: Deploy to multiple services simultaneously

```markdown
Skill: multi-repo-deploy
Composed from:
  - parallel-execution (deploy all)
  - git-operations (clone/pull)
  - build-system (build each)
  - deploy-service (new skill)
  - health-check (new skill)
  - yolo (autonomous mode)

Flow:
1. Parallel for each repo:
   - Pull latest
   - Run tests
   - Build artifacts
   - Deploy to staging
   - Health check
2. If all healthy:
   - Deploy to production
3. Report results
```

### Example 3: Issue Triage Bot

**Goal**: Automatically triage and label new issues

```markdown
Skill: issue-triage
Composed from:
  - gh-issues (new skill)
  - text-analysis (new skill)
  - label-classifier (new skill)
  - yolo (autonomous)

Flow:
1. Fetch new issues
2. For each issue:
   - Analyze content
   - Classify type (bug/feature/question)
   - Assign labels
   - Add to project board
   - Notify relevant team
```

## Composition Anti-Patterns

### ❌ Anti-Pattern 1: Over-Composition

Don't compose when a single skill suffices:

```plaintext
BAD:
Skill: simple-merge
  Composes: merge-pr + process-pr + resolve-pr-comments
  (Too much for simple merge)

GOOD:
Just use: pull-request-tool merge command
```

### ❌ Anti-Pattern 2: Circular Dependencies

Avoid skills that depend on each other:

```plaintext
BAD:
Skill A depends on Skill B
Skill B depends on Skill A
(Infinite loop)

GOOD:
Extract common logic to Skill C
Both A and B depend on C
```

### ❌ Anti-Pattern 3: Tight Coupling

Skills should be loosely coupled:

```plaintext
BAD:
Skill A knows internal details of Skill B
Changes to B break A

GOOD:
Skill A uses B through well-defined interface
B can change internally without breaking A
```

### ❌ Anti-Pattern 4: No Parameterization

Hardcoded values reduce reusability:

```plaintext
BAD:
Skill: deploy-to-staging
  Hardcoded: environment = "staging"
  (Cannot reuse for production)

GOOD:
Skill: deploy
  Parameter: environment (staging|production)
  (Reusable for any environment)
```

## Composition Best Practices

### ✅ 1. Single Responsibility

Each skill does one thing well:

```plaintext
GOOD:
- pull-request-tool: GitHub PR operations
- merge-pr: Merge logic and verification
- process-pr: Full PR workflow

NOT:
- super-github-tool: Everything GitHub-related
```

### ✅ 2. Clear Interfaces

Define explicit inputs and outputs:

```markdown
Skill: merge-pr
Inputs:
  - pr-number (required)
  - repository (required)
  - merge-method (optional)
Outputs:
  - merge-status (success/failure)
  - merge-commit-sha
  - errors (if any)
```

### ✅ 3. Fail Fast

Verify prerequisites early:

```markdown
Skill: deploy
Steps:
  1. Verify credentials (fail if missing)
  2. Verify environment exists (fail if not)
  3. Verify tests pass (fail if not)
  4. Then deploy
```

### ✅ 4. Composable Error Handling

Errors should propagate cleanly:

```markdown
process-pr:
  If resolve-pr-comments fails:
    - Log error
    - Skip to merge if critical
    - Or abort if blocker
  Decision based on error type
```

### ✅ 5. Document Composition

Always document what you compose:

```markdown
composed-from:
  - skill-a (for X)
  - skill-b (for Y)
  - skill-c (for Z)
```

## Testing Composed Skills

### Unit Testing

Test each skill in isolation:

```markdown
Test: pull-request-tool
- Mock GitHub API
- Verify correct calls made
- Check error handling
```

### Integration Testing

Test skills working together:

```markdown
Test: merge-pr (composes pull-request-tool)
- Test with real/sandbox repo
- Verify full flow works
- Check edge cases
```

### End-to-End Testing

Test complete workflows:

```markdown
Test: process-pr (composes multiple workflows)
- Create test PR
- Run full process
- Verify PR merged correctly
- Check all steps executed
```

## Advanced Composition Techniques

### Dynamic Composition

Choose skills at runtime:

```markdown
Skill: smart-workflow
Logic:
  analyze_context()
  if needs_security:
    add security-scan skill
  if needs_performance:
    add performance-analysis skill
  execute(composed_skills)
```

### Composition with Feedback Loops

Skills that iterate:

```markdown
Skill: iterative-fix
Loop:
  1. Run tests
  2. If tests fail:
     a. Analyze failures
     b. Attempt fixes
     c. Goto 1
  3. If tests pass: Done
Max iterations: 3
```

### Composition with Rollback

Support undo operations:

```markdown
Skill: safe-deploy
Steps:
  1. Snapshot current state
  2. Deploy new version
  3. Run health checks
  4. If unhealthy:
     Rollback to snapshot
  5. If healthy:
     Delete snapshot
```

## Quick Reference

### Composition Checklist

When building a workflow:

- [ ] Identified all required skills
- [ ] Determined execution order (sequential vs parallel)
- [ ] Chosen interaction mode (yolo vs collaborative)
- [ ] Defined clear parameters
- [ ] Documented composition in SKILL.md
- [ ] Added error handling
- [ ] Tested in isolation
- [ ] Tested with real scenarios

### Composition Template

```markdown
---
name: your-workflow
description: What it does
category: workflow
composed-from:
  - skill-1
  - skill-2
  - skill-3
---

# Your Workflow

## Purpose
[What problem it solves]

## Skill Composition
[How skills combine]

## Workflow Steps
[Detailed flow]

## Parameters
[Configuration options]

## Examples
[Real usage]
```

## Next Steps

1. Review existing workflows in `skills/workflow/`
2. Identify patterns in your domain
3. Design custom workflows
4. Implement using composition patterns
5. Test thoroughly
6. Document for others

Happy composing!
