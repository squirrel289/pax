# Getting Started with PAX Agent Skills Library

This guide will help you start using the PAX skills library for LLM-driven automation.

## What are Agent Skills?

Agent Skills are reusable, parameterized capabilities that LLM agents can invoke to perform tasks. Skills can be:

- **Atomic**: Single-purpose tools (e.g., pull-request-tool)
- **Composed**: Workflows built from multiple skills (e.g., process-pr)

## Installation

### Prerequisites

- GitHub CLI (`gh`) for PR-related skills
- Git for version control operations
- Access to LLM agent capable of tool/skill invocation

### Setup

1. Clone or access the PAX library
2. Install GitHub CLI:

   ```bash
   brew install gh  # macOS
   gh auth login
   ```

3. Optional: Install gh-pr-review extension:

   ```bash
   gh extension install agynio/gh-pr-review
   ```

## Basic Concepts

### Skill Categories

**Execution Skills**: Control how tasks execute

- `parallel-execution`: Run tasks concurrently
- `sequential-execution`: Run tasks in order

**Tool Skills**: Concrete integrations

- `gh-pr-review`: GitHub PR operations

**Interaction Skills**: Agent-human collaboration

- `yolo`: Autonomous execution
- `collaborative`: Interactive with confirmations

**Workflow Skills**: Composed automations

- `resolve-pr-comments`: Address PR feedback
- `merge-pr`: Safe PR merging
- `process-pr`: End-to-end PR workflow

### Skill Composition

Skills compose like building blocks:

```tree
process-pr (workflow)
├── parallel-execution (fetch + check + analyze)
├── resolve-pr-comments (workflow)
│   ├── pull-request-tool (tool)
│   ├── sequential-execution
│   └── yolo (interaction)
└── merge-pr (workflow)
    ├── pull-request-tool (tool)
    └── sequential-execution
```

## First Steps

### Example 1: Simple Tool Usage

Use a single skill directly:

```markdown
Agent Prompt: "Get all unresolved comments on PR #42 in owner/repo"

Skill Used: pull-request-tool
Action: Fetches and displays unresolved review threads
```

### Example 2: Workflow Execution

Use a composed workflow:

```markdown
Agent Prompt: "Process PR #42 in owner/repo"

Skill Used: process-pr (composed workflow)
Actions:
1. Fetches PR details (pull-request-tool)
2. Checks status in parallel (parallel-execution)
3. Addresses comments (resolve-pr-comments)
4. Merges if ready (merge-pr)
```

### Example 3: Mode Selection

Choose interaction mode:

```markdown
YOLO Mode:
Agent Prompt: "Process PR #42 in YOLO mode"
→ Fully autonomous, no confirmations

Collaborative Mode:
Agent Prompt: "Let's process PR #42 together"
→ Interactive, asks for approval at key steps
```

## Common Use Cases

### Use Case 1: PR Review Automation

**Goal**: Automatically process approved PRs

**Approach**:

```markdown
1. List open PRs
2. Filter for approved
3. For each: process-pr in yolo mode
```

**Prompt**:

```markdown
"Process all approved PRs in owner/repo using YOLO mode"
```

### Use Case 2: Interactive PR Merge

**Goal**: Safely merge PR with oversight

**Approach**:

```markdown
1. Check merge readiness
2. Show status to user
3. Get approval
4. Execute merge
```

**Prompt**:

```markdown
"Help me merge PR #42 - show me the status first"
```

### Use Case 3: Address Review Feedback

**Goal**: Resolve all review comments

**Approach**:

```markdown
1. Fetch unresolved comments
2. For each comment:
   - Read feedback
   - Make changes or reply
   - Resolve thread
```

**Prompt**:

```markdown
"Resolve all comments on PR #42 in collaborative mode"
```

## Understanding Execution Modes

### Parallel Execution

**When to use**: Independent tasks that can run simultaneously

```markdown
Example: Analyze codebase from multiple perspectives

Tasks:
- Security analysis
- Performance analysis  
- Test coverage analysis

All run at the same time → 3x faster
```

### Sequential Execution

**When to use**: Tasks with dependencies

```markdown
Example: Git workflow

Tasks:
1. Make changes
2. Commit changes (depends on #1)
3. Push changes (depends on #2)
4. Create PR (depends on #3)

Must happen in order
```

## Choosing Interaction Mode

### Use YOLO Mode When

- Workflow is well-defined
- Risk is low
- Speed is important
- You trust the agent's decisions

### Use Collaborative Mode When

- Risk is high
- Requirements are ambiguous
- You want visibility into process
- Learning how workflows work

## Skill Parameters

Most skills accept parameters to customize behavior:

```markdown
process-pr parameters:
- pr-number: Which PR to process
- repository: owner/repo format
- interaction-mode: yolo or collaborative
- merge-method: merge, squash, or rebase
- delete-branch: true/false
- run-local-checks: true/false
```

Example with parameters:

```markdown
"Process PR #42 in owner/repo with squash merge and delete the branch"
```

## Error Handling

Skills handle errors gracefully:

### YOLO Mode

- Attempts automatic recovery
- Uses fallback strategies
- Reports only critical blockers

### Collaborative Mode

- Shows error details
- Proposes solutions
- Asks for guidance

Example error handling:

```markdown
Error: CI checks failing

YOLO: Waits for checks to pass, then continues
Collaborative: "Tests are failing. Options: A) Wait B) Investigate C) Skip"
```

## Best Practices

1. **Start with workflows**: Use high-level skills like `process-pr`
2. **Use appropriate mode**: YOLO for routine, collaborative for critical
3. **Leverage parallelism**: Faster execution for independent tasks
4. **Verify before merging**: Always check status before merge
5. **Clean up branches**: Delete after merging
6. **Document decisions**: Skills log choices made

## Next Steps

1. **Read skill documentation**: Check SKILL.md files for details
2. **Try examples**: Run the examples in this guide
3. **Compose workflows**: Create custom workflows from existing skills
4. **Explore patterns**: See [SKILL_COMPOSITION.md](SKILL_COMPOSITION.md)
5. **Build new skills**: Add domain-specific skills for your needs

## Quick Reference

### Common Prompts

```bash
# View PR status
"Check the status of PR #42"

# Address review comments
"Resolve all comments on PR #42"

# Merge PR safely
"Merge PR #42 after checking all requirements"

# Full PR workflow
"Process PR #42 end-to-end in YOLO mode"

# Batch processing
"Process all approved PRs"

# Parallel analysis
"Analyze security and performance in parallel"
```

### Skill Discovery

To find skills:

1. Browse `skills/` directory
2. Check README for skill list
3. Read SKILL.md for details
4. Look at composed-from field in workflow skills

### Getting Help

- **Documentation**: Check SKILL.md files
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Composition**: See [SKILL_COMPOSITION.md](SKILL_COMPOSITION.md)

## Troubleshooting

### "Permission denied" errors

→ Run `gh auth login` to authenticate GitHub CLI

### "PR not found" errors

→ Verify PR number and repository format (owner/repo)

### "Merge conflicts" errors

→ Resolve conflicts manually, skills cannot auto-resolve

### Skills not composing correctly

→ Check composed-from field to verify compatibility

## Summary

You now understand:

- ✅ What Agent Skills are
- ✅ Skill categories (execution, tools, interaction, workflow)
- ✅ How skills compose together
- ✅ Interaction modes (yolo vs collaborative)
- ✅ Common use cases
- ✅ How to invoke skills with prompts

Ready to automate? Try processing your first PR!

```markdown
"Process PR #<number> in <owner/repo> using collaborative mode"
```
