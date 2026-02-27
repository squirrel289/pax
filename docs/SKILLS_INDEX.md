---
Last updated: February 2, 2026
---

# Skills Library Index

Quick reference index of all available skills.

## Execution Skills

### [parallel-execution](../skills/execution/parallel-execution/SKILL.md)

**Category**: Execution  
**Purpose**: Execute multiple independent tasks simultaneously  
**Key Use**: Speed up independent operations 3-10x  
**Composes**: N/A (atomic skill)

**Example**:

```plaintext
"Analyze security, performance, and testing in parallel"
```

### [sequential-execution](../skills/execution/sequential-execution/SKILL.md)

**Category**: Execution  
**Purpose**: Execute dependent tasks in order  
**Key Use**: Handle workflows with dependencies  
**Composes**: N/A (atomic skill)

**Example**:

```plaintext
"Build → Test → Deploy in sequence"
```

---

## Tool Skills

### [pull-request-tool](../skills/tools/pull-request-tool/SKILL.md)

**Category**: Tools  
**Purpose**: Unified entry point for all PR/issue management. Delegates to Copilot API or CLI as needed.  
**Key Use**: Always use for PR/issue management—future-proof, agent-native, and composable.  
**Composes**: copilot-pull-request, pull-request-tool (as backends)

**Note**: You may also invoke as `pr-tool` (see SKILL.md for details).

**Example**:

```plaintext
"Merge PR #42 using pull-request-tool"
```

### [copilot-pull-request](../skills/tools/copilot-pull-request/SKILL.md)

**Category**: Tools  
**Purpose**: Manage PRs/issues using Copilot's built-in APIs.  
**Key Use**: Agent-native PR/issue management in Copilot environments.  
**Composes**: N/A (backend skill)

**Example**:

```plaintext
"Fetch PR #42 details using copilot-pull-request"
```

### [gh-pr-review](../skills/tools/gh-pr-review/SKILL.md)

**Category**: Tools  
**Purpose**: GitHub PR interaction and management via CLI.  
**Key Use**: CLI-based PR/issue management, fallback backend.  
**Composes**: N/A (backend skill)

**Example**:

```plaintext
"Get unresolved comments on PR #42 using gh-pr-review"
```

### [capture-events](../skills/tools/capture-events/SKILL.md)

**Category**: Tools  
**Purpose**: Capture workspace events for continuous feedback loop and pattern detection.  
**Key Use**: Build episodic memory for skill evolution and recommendations.  
**Composes**: N/A (atomic skill, but feeds [[creating-skill]])

**Supports**:

- Universal provider (workspace-only, no assistant required)
- GitHub Copilot provider (extension integration)
- Codex provider (API-based)
- Cursor provider (extension integration)

**Example**:

```plaintext
"Enable continuous event capture for skill evolution"
```

---

## Interaction Modes

**Usage Guide**: [USAGE_GUIDE.md](../skills/aspects/interaction-modes/USAGE_GUIDE.md)  
**Aspect**: [interaction-modes](../skills/aspects/interaction-modes/ASPECT.md)

Interaction modes are implemented as an aspect rather than standalone skills. Skills declare decision points and use the aspect to handle YOLO (autonomous) or Collaborative (interactive) behavior.

### YOLO Mode

**Purpose**: Autonomous execution without confirmations  
**Key Use**: Well-defined, low-risk automation  
**Implementation**: [yolo.sh](../skills/aspects/interaction-modes/yolo.sh)

**Example**:

```plaintext
"Process all PRs in YOLO mode"
```

### Collaborative Mode

**Purpose**: Interactive execution with human oversight  
**Key Use**: High-risk operations, learning, ambiguous requirements  
**Implementation**: [collaborative.sh](../skills/aspects/interaction-modes/collaborative.sh)

**Example**:

```plaintext
"Let's review this PR together"
```

---

## Workflow Skills

### [resolve-pr-comments](../skills/workflow/resolve-pr-comments/SKILL.md)

**Category**: Workflow  
**Purpose**: Address and resolve PR review feedback  
**Key Use**: Systematic comment resolution  
**Composes**:

- pull-request-tool
- sequential-execution
- yolo OR collaborative

**Example**:

```plaintext
"Resolve all comments on PR #42"
```

### [merge-pr](../skills/workflow/merge-pr/SKILL.md)

**Category**: Workflow  
**Purpose**: Safely merge PRs with verification  
**Key Use**: Ensure all requirements met before merge  
**Composes**:

- pull-request-tool
- sequential-execution
- yolo OR collaborative

**Example**:

```plaintext
"Merge PR #42 after verifying checks"
```

### [process-pr](../skills/workflow/process-pr/SKILL.md)

**Category**: Workflow  
**Purpose**: End-to-end PR processing  
**Key Use**: Complete PR automation from review to merge  
**Composes**:

- parallel-execution
- sequential-execution
- pull-request-tool
- resolve-pr-comments
- merge-pr
- yolo OR collaborative

**Example**:

```plaintext
"Process PR #42 end-to-end"
```

### [creating-skill](../skills/workflow/creating-skill/SKILL.md)

**Category**: Workflow  
**Purpose**: Evaluate skill ideas against memory patterns and provide recommendations for enhancement or creation.  
**Key Use**: Recommend whether to enhance existing skills, create new PAX skills, project-local skills, aspects, or update AGENTS.md.  
**Composes**:

- capture-events (memory data)
- skill-reviewer (overlap analysis)
- interaction-modes (yolo OR collaborative)

**Example**:

```plaintext
"Should I create a new skill for batch updating work items?"
```

**Note**: Delegates actual creation to [[skill-creator]] per PAX conventions.

---

## Skill Relationships

### Composition Hierarchy

```tree
process-pr (top-level)
├── parallel-execution
├── sequential-execution
├── pull-request-tool
│   ├── copilot-pull-request (API backend)
│   └── gh-pr-review (CLI backend)
├── resolve-pr-comments (sub-workflow)
│   ├── pr-management-wrapper
│   ├── sequential-execution
│   └── yolo OR collaborative
└── merge-pr (sub-workflow)
    ├── pr-management-wrapper
    ├── sequential-execution
    └── yolo OR collaborative
```

### Atomic vs Composed

**Atomic Skills** (building blocks):

- parallel-execution
- sequential-execution
- pull-request-tool
- yolo
- collaborative

**Composed Skills** (workflows):

- resolve-pr-comments
- merge-pr
- process-pr

---

## Quick Skill Selection Guide

### By Use Case

| Use Case                   | Recommended Skill           |
|----------------------------|-----------------------------|
| Merge a PR                 | merge-pr                    |
| Address review feedback    | resolve-pr-comments         |
| Full PR processing         | process-pr                  |
| Multiple independent tasks | parallel-execution          |
| Ordered dependent tasks    | sequential-execution        |
| GitHub PR operations       | pull-request-tool (pr-tool) |
| Autonomous operation       | yolo (mode)                 |
| Interactive operation      | collaborative (mode)        |

### By Complexity

**Simple** (single skill):

- pull-request-tool: "Check PR status"
- parallel-execution: "Analyze in parallel"

**Medium** (workflow):

- resolve-pr-comments: "Resolve comments"
- merge-pr: "Merge with verification"

**Complex** (full workflow):

- process-pr: "End-to-end processing"

### By Risk Level

**Low Risk** → Use yolo mode:

- Merging approved PRs
- Formatting code
- Updating documentation

**Medium Risk** → Use collaborative mode:

- Refactoring code
- Dependency updates
- Non-critical deployments

**High Risk** → Always use collaborative:

- Production deployments
- Security changes
- Database migrations

---

## Skill Parameters

### Common Parameters

Most workflow skills accept:

```markdown
Required:
- pr-number: PR to process
- repository: owner/repo format

Optional:
- interaction-mode: yolo | collaborative
- merge-method: merge | squash | rebase
- delete-branch: true | false
```

### Execution Skills Parameters

```markdown
parallel-execution:
- tasks: Array of task descriptions

sequential-execution:
- tasks: Ordered array of tasks
- dependencies: Task dependency map
```

### Tool Skills Parameters

```markdown
pull-request-tool:
- operation: view | merge | comment | resolve
- pr-number: PR number
- repository: owner/repo
- filters: unresolved | by-reviewer | etc.
```

---

## Performance Characteristics

| Skill                | Speed     | Complexity | Error Handling  |
|----------------------|-----------|------------|-----------------|
| parallel-execution   | Fast (Nx) | Low        | Propagates      |
| sequential-execution | Normal    | Low        | Fail-fast       |
| pull-request-tool    | Fast      | Low        | Graceful        |
| yolo                 | Fast      | Medium     | Auto-recover    |
| collaborative        | Slow      | Medium     | Interactive     |
| resolve-pr-comments  | Medium    | Medium     | Depends on mode |
| merge-pr             | Fast      | Medium     | Fail-safe       |
| process-pr           | Medium    | High       | Comprehensive   |

---

## Adding New Skills

To add a skill to this index:

1. Create skill directory and SKILL.md
2. Add to appropriate category above
3. Document composition relationships
4. Add to quick selection guide
5. Update skill relationships diagram

---

## Skill Status

All skills in this index are:

- ✅ Fully documented
- ✅ Production ready
- ✅ Tested with examples
- ✅ Composable with other skills
