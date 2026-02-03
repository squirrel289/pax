# PAX: Agent Skills Library

A greenfield, modular library of composable, general-purpose Agent Skills for LLM-driven automation and workflow orchestration.

## Vision

Build reusable, parameterized skills that can be easily composed into higher-level workflows. All skills are designed for LLM agent invocation, enabling sophisticated automation through simple composition.

## Quick Start

### Basic Usage

Skills can be invoked directly or composed into workflows:

```plaintext
# Direct skill invocation
"Analyze this codebase using parallel-execution"

# Workflow composition
"Process PR #42 end-to-end" (uses process-pr workflow)
```

### Skill Categories

- **Execution**: Control flow and task orchestration
- **Tools**: Concrete integrations (GitHub, APIs, etc.)
- **Interaction**: Human-agent collaboration patterns
- **Workflow**: Composed, domain-specific automations

## Core Principles

### 1. Composability

All skills are atomic or composable, enabling flexible workflow construction.

```tree
workflow: process-pr
  ├─ parallel-execution (assess PR readiness)
  ├─ resolve-pr-comments (address feedback)
  └─ merge-pr (safe merge execution)
```

### 2. Parameterization

Skills accept parameters for maximum reuse across contexts.

```markdown
parallel-execution:
  - tasks: [task1, task2, task3]
  - execution-mode: concurrent

yolo:
  - confidence-threshold: 0.7
  - max-retries: 3
```

### 3. Modularity

General skills (parallel-execution, tool invocation) separate from workflow-specific skills (process-pr).

### 4. Discoverability

Each skill includes comprehensive SKILL.md with parameters, usage examples, and composition patterns.

### 5. LLM-Optimized

All skills designed for natural language invocation and chaining by LLM agents.

## Library Structure

```tree
pax/
├── docs/                          # Documentation
│   ├── README.md                  # This file
│   ├── GETTING_STARTED.md         # Quick start guide
│   ├── SKILL_COMPOSITION.md       # Composition patterns
│   └── EXAMPLES.md                # Real-world examples
│
├── skills/                        # All skills
│   ├── execution/                 # Execution patterns
│   │   ├── parallel-execution/
│   │   │   └── SKILL.md
│   │   └── sequential-execution/
│   │       └── SKILL.md
│   │
│   ├── tools/                     # Tool integrations
│   │   └── pull-request-tool/
│   │       └── SKILL.md
│   │
│   ├── interaction/               # Agent-human interaction
│   │   ├── yolo/
│   │   │   └── SKILL.md
│   │   └── collaborative/
│   │       └── SKILL.md
│   │
│   └── workflow/                  # Composed workflows
│       ├── resolve-pr-comments/
│       │   └── SKILL.md
│       ├── merge-pr/
│       │   └── SKILL.md
│       └── process-pr/
│           └── SKILL.md
│
└── SKILL_LIBRARY_PLAN.md         # Original plan
```

## Available Skills

### Execution Skills

#### [parallel-execution](skills/execution/parallel-execution/SKILL.md)

Execute multiple independent tasks simultaneously for maximum efficiency.

**When to use**: Multiple analyses, independent file processing, concurrent reviews

**Example**:

```plaintext
"Analyze security, performance, and testing in parallel"
```

#### [sequential-execution](skills/execution/sequential-execution/SKILL.md)

Execute dependent tasks in order where each task relies on previous results.

**When to use**: Build pipelines, ordered workflows, dependent steps

**Example**:

```plaintext
"Process PR: fetch → test → review → merge"
```

### Tool Skills

#### [pull-request-tool](skills/tools/pull-request-tool/SKILL.md)

Unified entry point for all GitHub pull request and issue management. Automatically selects the best backend (Copilot API or CLI) for the environment.

**When to use**: Any PR/issue management, review, comment, or merge operation—always start here for maximum compatibility and future-proofing.

**Note**: You may also invoke as `pr-tool` (see SKILL.md for details).

**Example**:

```plaintext
"Merge PR #42 using pull-request-tool"
```

#### [copilot-pull-request](skills/tools/copilot-pull-request/SKILL.md)

Manage GitHub pull requests and issues using Copilot's built-in PR/issue APIs. Provides structured, agent-native operations for review, comment, resolve, and merge workflows.

**When to use**: In Copilot agent environments (VS Code, Copilot CLI, etc.) for maximum integration and reliability.

**Example**:

```plaintext
"Fetch PR #42 details using copilot-pull-request"
```

#### [gh-pr-review](skills/tools/gh-pr-review/SKILL.md)

Interact with GitHub pull requests for review, comment management, and merge operations via the GitHub CLI. Used as a backend by the wrapper when Copilot APIs are unavailable.

**When to use**: CLI environments, or as a fallback for PR/issue management.

**Example**:

```plaintext
"Get all unresolved comments on PR #42"
```

### Interaction Skills

#### [yolo](skills/interaction/yolo/SKILL.md)

Autonomous "just do it" mode - execute actions without confirmation.

**When to use**: Well-defined workflows, time-critical operations, low-risk automation

**Example**:

```plaintext
"Process all approved PRs in YOLO mode"
```

#### [collaborative](skills/interaction/collaborative/SKILL.md)

Human-in-the-loop interaction with confirmations and feedback.

**When to use**: High-risk operations, ambiguous requirements, learning scenarios

**Example**:

```plaintext
"Let's review and merge PR #42 together"
```

### Workflow Skills

#### [resolve-pr-comments](skills/workflow/resolve-pr-comments/SKILL.md)

Systematically address and resolve pull request review comments.

**Composes**: pull-request-tool + sequential-execution + (yolo OR collaborative)

**Example**:

```plaintext
"Resolve all PR comments on #42"
```

#### [merge-pr](skills/workflow/merge-pr/SKILL.md)

Safely merge pull requests after comprehensive verification.

**Composes**: pull-request-tool + sequential-execution + (yolo OR collaborative)

**Example**:

```plaintext
"Merge PR #42 after verifying all checks pass"
```

#### [process-pr](skills/workflow/process-pr/SKILL.md)

End-to-end PR processing from review to merge.

**Composes**: parallel-execution + sequential-execution + pull-request-tool + resolve-pr-comments + merge-pr + (yolo OR collaborative)

**Example**:

```plaintext
"Process PR #42 from start to finish"
```

## Composition Patterns

### Pattern 1: Linear Workflow

```markdown
process-pr:
  Step 1: Assess (parallel)
  Step 2: Verify (sequential)
  Step 3: Resolve (sequential)
  Step 4: Merge (sequential)
```

### Pattern 2: Parallel Analysis

```markdown
codebase-review:
  Parallel:
    - Security analysis
    - Performance analysis
    - Test coverage analysis
  Then:
    - Synthesize findings
```

### Pattern 3: Mode Selection

```markdown
Any workflow:
  IF user wants autonomous → use yolo
  IF user wants interactive → use collaborative
```

### Pattern 4: Tool Orchestration

```markdown
pull-request-tool (tool):
  Canonical entry point for all PR/issue management
  Delegates to:
    - copilot-pull-request (API backend)
    - gh-pr-review (CLI backend)
  Used by:
    - resolve-pr-comments
    - merge-pr
    - process-pr
```

## Real-World Examples

### Example 1: Automated PR Workflow

```markdown
User: "Process PR #42 in YOLO mode"

Execution:
- process-pr skill
- Mode: yolo
- Steps:
  1. Parallel assessment (PR status + reviews + CI)
  2. Run local tests
  3. Resolve 3 comments automatically
  4. Wait for CI to pass
  5. Verify approvals
  6. Merge with squash
  7. Delete branch

Output: "PR #42 merged successfully"
```

### Example 2: Batch PR Processing

```markdown
User: "Process all approved PRs"

Execution:
- List approved PRs: #41, #42, #43
- parallel-execution spawns:
  - process-pr(#41, yolo)
  - process-pr(#42, yolo)
  - process-pr(#43, yolo)
- Each runs independently
- Report: "3 PRs processed and merged"
```

### Example 3: Collaborative Review

```markdown
User: "Help me review and merge PR #42"

Execution:
- process-pr skill
- Mode: collaborative
- Interactive steps with user approval at each stage
- User makes decisions on ambiguous items
- Agent executes approved actions
```

## Extension Guide

### Adding New Skills

1. **Choose category**: execution, tools, interaction, or workflow
2. **Create directory**: `skills/<category>/<skill-name>/`
3. **Write SKILL.md**: Follow existing format
4. **Document**:
   - Purpose and when to use
   - Parameters
   - Usage examples
   - Composition patterns
5. **Test**: Verify skill works in isolation and composition

### Skill Template

```markdown
---
name: skill-name
description: One-line description
category: execution|tools|interaction|workflow
license: MIT
composed-from: [optional list of skills this composes]
---

# Skill Name

Description and purpose.

## When to Use

Specific scenarios...

## Parameters

Required and optional parameters...

## Usage Examples

Concrete examples...

## Quick Reference

Cheat sheet...
```

## Best Practices

1. **Start with general skills**: Use execution and tool skills
2. **Compose into workflows**: Build domain-specific workflows
3. **Choose interaction mode**: yolo for automation, collaborative for oversight
4. **Leverage parallelism**: Use parallel-execution when tasks independent
5. **Document decisions**: Explain choices in skill outputs
6. **Handle errors gracefully**: Implement proper error recovery
7. **Test composition**: Verify skills work together correctly

## Performance Tips

- Use **parallel-execution** for independent tasks: 3-10x faster
- Use **yolo mode** for well-defined workflows: No confirmation delays
- Use **sequential-execution** only when dependencies exist
- Batch process multiple items with parallel-execution

## Contributing

1. Fork the repository
2. Create skill in appropriate category
3. Follow SKILL.md template
4. Add to this README
5. Submit PR with examples

## License

MIT License - See individual skills for details

## Support

- Documentation: [docs/](docs/)
- Examples: [docs/EXAMPLES.md](docs/EXAMPLES.md)
- Composition Guide: [docs/SKILL_COMPOSITION.md](docs/SKILL_COMPOSITION.md)

## Roadmap

- [x] Core execution skills (parallel, sequential)
- [x] GitHub PR tools
- [x] Interaction modes (yolo, collaborative)
- [x] PR workflows (resolve, merge, process)
- [ ] Additional tool integrations (Jira, Slack, etc.)
- [ ] More workflow patterns
- [ ] Skill discovery and search
- [ ] Validation and testing framework
