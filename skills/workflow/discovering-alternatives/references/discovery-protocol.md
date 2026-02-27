# Discovery Protocol

This protocol enforces exhaustive discovery of build, buy, and hybrid alternatives using pretrained knowledge plus RAG sources. All 5 sources must be attempted; if blocked, stop and prompt user with 4 options.

## Before Discovery Starts

Ask user (if not already provided) and record answers:

1. **Time horizon**: Days? Weeks? Months? (Impacts vendor maturity, learning curve, PoC timelines)
2. **Budget sensitivity**: Fixed cost ceiling? Per-seat? TCO range? (Constrains buy/hybrid options)
3. **Hard constraints**: Compliance? Platform? Language? Integration must-haves? (Eliminates options early)

If user cannot answer: STOP and ask user to define constraints before proceeding.

## Required Tool Access (MANDATORY)

All three tools must be **attempted** before proceeding to ranking:

**1. Local Memory Tool (Patterns/Episodes/Decisions)** — MANDATORY

- If unavailable: STOP and prompt user with 4 options (see Gate Handling below)
- If available: Query for prior decisions on similar problems, design patterns, architectural debates

**2. Repo Search (Workspace + Attached Repos)** — MANDATORY

- If blocked/unavailable: STOP and prompt user
- If available: Search for existing implementations, configs, dependencies, test examples
- Minimum acceptable: 3+ hits OR explicitly no matches in repos

**3. Web Search (5+ External Sources)** — MANDATORY

- If blocked by user OR unavailable: Prompt user to grant access, provide manual candidates, or continue without
- If available: Query 5+ sources (vendors, OSS registries, benchmarks, standards, tools)
- Minimum acceptable: 5+ URLs/tools OR user provides manual candidates

## Mandatory Sources (Full List)

1. **Pretrained knowledge** (baseline landscape from training data)
2. **Local memory tools** (patterns, episodes, prior decisions) — MANDATORY
3. **Repo search** (existing code, configs, dependencies, scripts) — MANDATORY
4. **User-provided context** (stated candidates, constraints, requirements)
5. **Web search** (vendors, OSS, standards, benchmarks) — MANDATORY

## Required Queries Per Source

Perform at least one query per source type, all with timestamps:

- **Core domain**: Problem keywords, tooling categories, frameworks
- **Build variants**: Build from scratch, custom implementation, DIY approaches
- **Buy variants**: Vendors, SaaS platforms, commercial tools, managed services
- **Hybrid variants**: Buy + build adapters, OSS + managed, API + orchestration
- **Adjacent categories**: Competitors, substitutes, related solutions
- **Constraints**: Compliance, licensing, platform support, integration requirements
- **Case studies**: What did similar orgs choose? (Re-usable patterns)

## Option Normalization

For each option, capture:

- Name and category (build, buy, hybrid)
- Feasibility status (feasible, infeasible, unknown)
- Integration fit (stack compatibility)
- Evidence summary (source + date)
- Confidence level (high, medium, low)

## Hybrid Patterns to Consider

- Buy core + build adapters
- Build core + buy integrations
- OSS base + managed hosting
- Vendor API + internal orchestration

## Discovery Log Template

Structured log for all discovery attempts (even failed queries). Use this format for each source:

```markdown
### Discovery Log

#### Pretrained Knowledge

- **Query**: [search terms from brainstorm]
- **Date**: [ISO 8601]
- **Results**: [brainstorm output, 3-5 candidates or "no matches"]
- **Evidence**: None (direct knowledge)

#### Local Memory Tool

- **Query**: [exact query syntax or semantic search]
- **Date**: [ISO 8601]
- **Tool**: [memory system identifier]
- **Results**: [linked episodes/patterns/decisions with IDs]
- **Evidence**: [pattern names, decision identifiers, URLs if available]
- **Status**: Available / Blocked / No Matches

#### Repo Search

- **Query**: [exact search terms]
- **Date**: [ISO 8601]
- **Repos**: [temple, templjs, pax, or other workspaces]
- **Results**: [file paths, code snippets, 3+ hits OR "no matches"]
- **Evidence**: [links to specific files/lines, commit refs if available]
- **Status**: Available / No Matches / Search Blocked

#### User-Provided Context

- **Input**: [candidate list, requirements, constraints]
- **Date**: [when user provided]
- **Results**: [normalized as build/buy/hybrid candidates]
- **Evidence**: [user justification or reference links]

#### Web Search

- **Query**: [exact search terms]
- **Date**: [ISO 8601]
- **Sources**: [5+ URLs/vendors/tools/standards]
- **Results**: [summarized matching vendors, OSS projects, benchmarks]
- **Evidence**: [clickable URLs with short descriptions, pricing/features if available]
- **Status**: Available / Blocked by User / Search Failed
```

## Option Inventory Requirements

After discovery, verify coverage before ranking:

**Build Category**: Minimum 2 options

- Examples: custom implementation, DIY framework, internal tooling
- If fewer: document why (e.g., "user explicitly forbids in-house development")

**Buy Category**: Minimum 2 options

- Examples: commercial vendor, SaaS platform, managed service, OSS with support
- If fewer: document why (e.g., "no vendors meet compliance requirements")

**Hybrid Category**: Minimum 2 options

- Examples: buy + build adapters, OSS base + managed hosting, API + orchestration
- If fewer: document why (e.g., "constraints eliminate hybrid approaches")

**Total Inventory**: Minimum 8 options across all categories

- If fewer: Return to Phase 2 and expand queries OR rank with warning if user confirms

**Documented Exclusions**: For each excluded option, record:

- Option name, why excluded (constraint mismatch, infeasible, out-of-scope)
- Excluded == explicit decision, not lazy omission

## Coverage Gate Rules (Fail-Fast)

Gates are checked after all discovery sources complete. Apply rules in order:

1. **Gate 1**: Fewer than 2 build options → **Rank with Warning** (unless user forbids custom build)
2. **Gate 2**: Fewer than 2 buy options → **Rank with Warning** (unless user forbids commercial tools)
3. **Gate 3**: Fewer than 2 hybrid options → **Rank with Warning** (unless user forbids hybrid)
4. **Gate 4**: Fewer than 8 total options → **Rank with Warning** (escalate if user wants 8+)
5. **Gate 5**: Any option lacks evidence_links → **Mark infeasible OR backfill from discovery log**
6. **Gate 6**: Repo search blocked → **STOP and prompt user** with 4 options
7. **Gate 7**: Memory tool blocked → **STOP and prompt user** with 4 options
8. **Gate 8**: Web search blocked (user forbid) → **ASK user**: continue without web sources OR provide manual candidates

## Gate Handling (User Prompts)

**If Gates 1–5 fail (coverage gates):**

- Show which gates failed and why
- If all gate failures are "fewer options": Rank with warning (annotate each warning)
- If any evidence_links missing: Backfill from discovery log OR mark option infeasible
- Proceed to ranking unless user requests re-discovery

**If Gate 6, 7, or 8 fail (blocked sources):**

- STOP and present user with exactly 4 options:
  - **(A) Continue discovery without [source]**: Proceed with current options (show current count)
  - **(B) Grant access to [source]**: Re-run discovery with access (provide instructions)
  - **(C) Provide [source] manually**: Paste candidates/URLs/patterns directly; add to option inventory
  - **(D) Abort**: Escalate and request constraint clarification
- Require explicit user choice before proceeding
- Log user's choice in decision matrix trace

**If memory tool unavailable and user chooses A or C:**

- Continue discovery without memory tool
- Note in Discovery Log: "Memory tool unavailable. User opted to continue."

**If repo search unavailable and user chooses A or C:**

- Continue discovery without repo search
- Note in Discovery Log: "Repo search unavailable. User opted to [continue | provide manual candidates]."

**If web search blocked and user chooses A or C:**

- Continue with user-provided web candidates OR brainstorm only
- Note in Discovery Log: "Web search blocked by user. User opted to [continue | provide manual candidates]."

## User Confirmation Before Ranking (Phase 7)

After all sources complete and gates are checked, PAUSE and show user:

1. **Discovery Log** (all sources, queries, results, timestamps)
2. **Gate Status** (which gates passed/failed and action taken)
3. **Current Option Inventory** (count by category, total, documented exclusions)
4. **Prompt**: "Proceed to ranking with current discovery? [YES / NO / RE-RUN]"

User options:

- **YES**: Proceed to ranking (Phase 8)
- **NO**: Abort and return options for manual review
- **RE-RUN**: Go back to Phase 2 with expanded constraints/queries

All paths logged in final matrix under "discovery_confirmation" field.
