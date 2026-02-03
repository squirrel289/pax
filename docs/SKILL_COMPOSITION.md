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

### Pattern 5: Mode Injection

Inject interaction mode into workflows:

```markdown
Workflow + Mode → Behavior

Example:
- process-pr + yolo → Fully autonomous
- process-pr + collaborative → Interactive
```

**Implementation**:

```markdown
Skill: any-workflow
Parameters:
  - interaction-mode: yolo | collaborative

Logic:
  All sub-workflows inherit the mode
  Behavior adapts automatically
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
