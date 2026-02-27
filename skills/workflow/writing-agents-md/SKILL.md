---
name: writing-agents-md
description: Create, review, and improve AGENTS.md or agent.md files using proven patterns from GitHub's analysis of 2,500+ repositories. Use when asked to author or refactor repository-level AGENTS.md guidance, .github/agents/*.md personas, command/runbook sections, safety boundaries, or agent templates.
license: MIT
metadata:
  type: document
  subtype: skill
  audience: agents, developers
  tags: agents-md, agent-md, copilot, persona, boundaries, workflow
---

# Writing AGENTS.md

## Overview

Use this skill to produce high-signal agent instructions: specific persona, executable commands, concrete examples, clear boundaries, and precise stack details. It codifies guidance from GitHub's "How to write a great agents.md" analysis of 2,500+ repositories. Prefer concise operational guidance over generic prose.

## Workflow

1. Determine the target file type.
   - Repository policy file: `AGENTS.md`
   - Persona file: `.github/agents/<name>.md`
2. Gather project facts before drafting.
   - Commands that are actually runnable (`test`, `build`, `lint`, `dev`, docs checks)
   - Stack with versions and key frameworks
   - File boundaries (read/write directories, sensitive paths)
   - Existing style examples to mirror
3. Draft command-first instructions.
   - Put runnable commands near the top.
   - Include full commands with flags/options where relevant.
4. Fill six core areas.
   - Commands
   - Testing
   - Project structure
   - Code style/output standards
   - Git workflow
   - Boundaries
5. Add three-tier boundaries.
   - `Always`: safe/default actions
   - `Ask first`: risky or ambiguous actions
   - `Never`: forbidden actions (secrets, unsafe paths, destructive actions)
6. Validate with the checklist in `references/agents-md-quality-checklist.md`.
7. If requested, generate role-specific variants using `references/starter-templates.md`.

## Required Output Shape

Use this structure unless the user asks for a different format:

```markdown
---
name: <agent_name>
description: <one sentence: role + scope>
---

You are <specific role> for this project.

## Commands

- Build: `<command>`
- Test: `<command>`
- Lint/Format: `<command>`

## Project Knowledge

- Tech stack with versions
- File structure and allowed write locations

## Standards

- Naming/style rules
- One concrete good example (code or output snippet)

## Boundaries

- ✅ Always: ...
- ⚠️ Ask first: ...
- 🚫 Never: ...
```

## Editing Existing Agent Files

1. Preserve the current intent and role unless the user asks to change it.
2. Remove vague language and replace with concrete, testable instructions.
3. Promote any buried commands into the `Commands` section near the top.
4. Convert implicit constraints into explicit `Always/Ask first/Never` rules.
5. Keep instructions short, directive, and specific to the repo.

## Guidance on References

- Use `references/agents-md-quality-checklist.md` for scoring and gap analysis.
- Use `references/starter-templates.md` when the user asks for examples or new personas.

## Source

- <https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/>
