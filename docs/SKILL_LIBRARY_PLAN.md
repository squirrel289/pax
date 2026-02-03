
# workflow-framework: Greenfield Agent Skills Library Plan

## Vision

Create a greenfield, modular library of composable, general-purpose Agent Skills, designed for LLM-driven automation and workflow orchestration. All skills should be reusable, parameterized, and easily composed into higher-level workflows. The first use case is a streamlined, fully-automated [PR workflow](pr%20workflow.json), but the primary goal is a robust foundation of general skills such as <https://raw.githubusercontent.com/CloudAI-X/opencode-workflow/refs/heads/main/skills/parallel-execution/SKILL.md>.

---

## Core Principles

- **Composability:** All skills are atomic or composable, enabling flexible workflow construction.
- **Parameterization:** Skills accept parameters for maximum reuse across contexts.
- **Modularity:** General skills (e.g., parallel execution, tool invocation, interaction patterns) are separated from workflow-specific skills.
- **Discoverability:** Skills are documented and organized for easy discovery and extension.
- **LLM-Optimized:** All skills are designed for invocation and chaining by LLM agents.

---

## Project Structure

- `/docs/` — Documentation and usage guides.
- `/skills/` — All skills, one subfolder per skill, each with a SKILL.md and implementation.
  - `execution/`
    - `parallel-exection/`
      - `SKILL.md`
    - `sequential-execution/`
      - `SKILL.md`
  - `tools/`
    - `pull-request-tool/`
      - `SKILL.md`
  - `interaction/`
    - `yolo/`
      - `SKILL.md`
    - `collaborative/`
      - `SKILL.md`
  - `workflow/`
    - `resolve-pr-comments/`
      - `SKILL.md`
    - `merge-pr/`
      - `SKILL.md`
    - `process-pr/`
      - `SKILL.md`

---

## Example: Composing a PR Workflow Skill

To automate the PR6 workflow, compose the following skills:

1. **parallel-execution** — Run independent steps in parallel (see [parallel-execution SKILL.md](https://raw.githubusercontent.com/CloudAI-X/opencode-workflow/refs/heads/main/skills/parallel-execution/SKILL.md)).
2. **gh-pr-review** — Interact with GitHub PRs (list, review, comment, resolve, merge). (see [gh-pr-review SKILL.md](https://github.com/agynio/gh-pr-review/raw/refs/heads/main/SKILL.md))
3. **yolo-interaction** — Automate "just do it"/YOLO-style actions (e.g., auto-resolve, auto-merge).
4. **collaborative-interaction** - Human-driven conversation with visual feedback and manual verification.
**process-pr** (workflow skill) — Orchestrate the above to fully process, resolve, and merge a PR, e.g.:
   - Fetch PR details
   - Run pre-commit and CI checks
   - Review and resolve all comments
   - Merge PR to main
   - Post follow-up comments/summary

All steps should be parameterized and allow for serial or parallel execution as appropriate.

---

## Fetch Latest Content Technique

**Before any analysis, planning, or workflow execution, always fetch and review the latest contents from all specified URLs or sources.**

- Download or retrieve the full, current content from each provided URL or file path before proceeding.
- Use the fetched content as the authoritative source for all review, planning, and execution steps.
- Do not rely on cached or previously loaded context—ensure the most recent version is used for all actions.

---

## Implementation Plan

1. **Define atomic, general-purpose skills** (e.g., parallel-execution, sequential-execution, tool-invocation, interaction patterns).
2. **Implement workflow-specific skills** by composing general skills (e.g., process-pr, resolve-pr-comments, merge-pr).
3. **Document all skills** with clear SKILL.md files, parameters, and usage examples.
4. **Test composition** by automating the PR6 workflow as the first use case.
5. **Iterate and extend** the library for new workflows and domains.

---

## Target Outcome

A greenfield, best-practices Agent Skills library: modular, composable, and parameterized. Any complex workflow (such as PR review/merge) can be triggered by a single, simple request, with all logic composed from reusable skills. The library is ready for LLM-driven automation and future extension.
