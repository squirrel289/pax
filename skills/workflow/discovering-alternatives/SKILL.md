---
name: discovering-alternatives
description: "Exhaustive discovery of build, buy, and hybrid options for a stated problem, using pretrained knowledge plus RAG (local memory, repo search, user-provided details, and web search). Use when you need a comprehensive alternatives list and a decision matrix with ranked options. Trigger phrases: discover alternatives, build vs buy, solution landscape, option discovery, vendor shortlist."
metadata:
  type: document
  subtype: skill
---

# Discovering Alternatives

## Critical Constraint

**DO NOT ACCEPT SHORTCUTS.** This skill enforces discovery before ranking. You must:

1. Execute all 5 mandatory discovery sources (pretrained, memory, repo, user context, web) OR explicitly document why each is unavailable
2. Collect minimum 2 options per category (build, buy, hybrid) OR document exclusions and proceed with warning
3. Collect minimum 8 total options OR pause and ask user before ranking
4. Include evidence_links on every option row OR mark option as infeasible
5. Pause after discovery log is complete—require user confirmation before ranking

If any gate fails (fewer options, missing evidence, blocked sources), **STOP and prompt user** with 4 options:

- Continue discovery without blocked source (provide manual list)
- Grant access to blocked source (re-run discovery)
- Provide candidates manually (proceed with hybrid list)
- Abort and escalate constraints

## When to Use

Use this skill to discover the full set of feasible options (build, buy, hybrid build+buy) for a stated problem, with explicit evidence and coverage. This skill is discovery-first and outputs a decision matrix with ranked options. Discovery is **mandatory** and **non-negotiable**—no ranking without complete coverage log.

## Inputs

Required:

- Problem statement and goals
- Current stack or environment
- Hard constraints and non-goals
- Time horizon and budget sensitivity

Optional:

- Known candidates
- Evaluation criteria (if already defined)
- Required integrations or compliance needs

## Output

Provide a decision matrix plus ranked options with evidence coverage. Support both **Markdown** (human-readable) and **JSON** (machine-readable) output formats.

### Output Formats

**Markdown Format** (default for human review):

Required sections:

- Problem framing and constraints
- Discovery log (sources and queries)
- Option inventory (build, buy, hybrid)
- Decision matrix with scores or confidence
- Ranked shortlist with rationale
- Gaps and next validation steps

**JSON Format** (for tool integration, e.g., `comparative-decision-analysis`):

Use `references/output-schema.json` for the complete schema. Key sections:

- `decision`: Problem statement
- `constraints`: Time horizon, budget, hard constraints
- `discovery_log`: All 5 sources with timestamps, queries, results, evidence
- `options`: Array of normalized alternatives with evidence_links
- `coverage_gates`: Gate status and results
- `ranking`: Ranked options with rationale, implementation path, estimates
- `discovery_confirmation`: User approval record

**When to use JSON**: Request JSON output explicitly when feeding results to `comparative-decision-analysis` or other downstream tools. JSON preserves structured data for automated processing.

## Workflow

### Phase 1: Confirm Constraints

- Ask: Time horizon? Budget sensitivity? Hard constraints? (If not provided: STOP and ask user)
- Record all answers before proceeding

### Phase 2–4: Execute Mandatory Discovery Sources

- Pretrained knowledge: Brainstorm from training data
- Local memory: Query prior decisions/patterns/episodes
- Repo search: Find existing code, configs, scripts in workspace
- User context: Capture provided candidates and constraints
- Web search: 5+ external sources (vendors, OSS, standards, tools)

### Phase 5: Normalize Options

- Bucket into: build (custom), buy (vendor/SaaS), hybrid (mix)
- Capture: name, feasibility, stack fit, evidence link, confidence

### Phase 6: Check Coverage Gates (Fail-Fast)

- If fewer than 2 per category (build/buy/hybrid): rank with warning
- If fewer than 8 total options: rank with warning
- If repo search blocked (unavailable): STOP and prompt user with 4 options
- If memory tool blocked: STOP and prompt user with 4 options
- If web search blocked: Ask user, offer manual candidates or continue without
- If any option lacks evidence_links: Mark infeasible or backfill from sources

### Phase 7: Confirm Before Ranking (User Approval)

- Display discovery log (all sources, queries, results, timestamps)
- Show coverage gate status (warnings or blocks)
- Require explicit user approval: "Proceed to ranking with current discovery?"
- If user rejects: Return to Phase 2 and re-run with expanded queries

### Phase 8: Rank and Summarize

- Generate decision matrix (option, category, feasibility, effort, risk, coverage, evidence_links)
- Rank options 1..N with rationale
- Call out gaps, assumptions, and next validation steps

## Guardrails

- **Do not skip discovery.** All 5 sources must be attempted before ranking. If unavailable, log the reason explicitly.
- **Every option row must include evidence_links.** If no evidence, mark infeasible or backfill from discovery sources.
- **All queries logged with timestamps.** Include exact search terms, results count, and URLs/identifiers for each source.
- **Memory/Repo/Web are MANDATORY sources.** If blocked, STOP and prompt user (4 options: continue without, grant access, provide manual data, abort).
- **Confirm before ranking.** Always pause after discovery log. Display gates status. Require user approval.
- **If fewer than 2 per category: Rank with warning.** If fewer than 8 total: Rank with warning.
- **Coverage gates are tie-breakers.** Use them to decide stop-and-prompt vs rank-with-warning.
- **Document all exclusions.** Why was option X not considered? Attach constraints or rationale.
- **Hybrid patterns mandatory.** Include buy+build, build+buy OSS, managed+custom variants unless excluded by constraints.

## Output Template

Decision Matrix:

- Columns: option, category (build/buy/hybrid), feasibility, effort, risk, coverage, evidence
- Rows: one per option

Ranked Options:

- Rank 1..N with rationale and evidence summary
- Flag assumptions and missing data

## Example Prompt

"Discover all viable options to implement a templating linter for JSON and Markdown. Consider build vs buy vs hybrid, and include a decision matrix and ranked shortlist."

## Related Skills

- [[comparative-decision-analysis]]
- [[hybrid-decision-analysis]]
- [[evaluating-alternative]]

## References

- references/discovery-protocol.md
- **JSON Output Schema**: references/output-schema.json
- **Integration with comparative-decision-analysis**: references/integration-guide.md
- **End-to-End Workflow Example**: references/end-to-end-example.md
