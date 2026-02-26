---
id: rfc-dt-001
type: document
subtype: rfc
lifecycle: active
status: draft
title: Decision-Making Skills Suite Consolidation
description: RFC for consolidating 5 overlapping decision-analysis skills into 1 unified skill with 3 modes
date: 2026-02-25
author: AI Agent
version: 1.0
---

## Abstract

Today, the PAX skills library contains five overlapping decision-analysis skills that address a common problem—how do I choose between alternatives?—with different levels of rigor and composition depth. This fragmentation creates user confusion about which skill to use when and multiplies the maintenance burden across redundant implementations. This RFC proposes consolidating these five skills into a single **decision-analysis** skill with three documented modes—**lite**, **structured**, and **rigorous**—each optimized for different decision contexts and user preferences. The consolidation preserves all existing workflow logic, maintains backward compatibility through clear migration examples, and establishes a single authoritative decision-making interface.

## Status of This Memo

This RFC documents a proposed refactoring of the PAX agent skills library. It specifies the target architecture for decision-making workflows and serves as the implementation guide for Phase 2 of the PAX skills consolidation initiative.

## Copyright Notice

This RFC is part of the PAX agent skills library and is made available under the same license as the PAX project.

## 1. Problem Statement

### 1.1 Current State: Five Overlapping Skills

The PAX skills library currently maintains five decision-analysis skills:

| Skill                           | Primary Focus                         | Key Characteristics                                                                  |
| ------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| `comparative-analysis`          | Fast, lightweight decisions           | Explicit criteria, deterministic scoring, clear recommendation rules                 |
| `comparative-decision-analysis` | Rigorous vendor/architecture analysis | Mandatory discovery, evidence discipline, parallel evaluators, deterministic harness |
| `comparative-decision-review`   | Structured team decisions             | Rubric confirmation gate, multi-platform scoring, effort/risk tie-breaks             |
| `hybrid-decision-analysis`      | Hybrid (combines all three)           | Blends comparative-analysis + skill-reviewer + comparative-decision-review strengths |
| `hybrid-decision-analysis.v1`   | Versioned variant of hybrid           | Stable version of hybrid with bakeoff protocol support                               |

All five skills address the core question: **"How do I defensibly choose between alternatives?"** They differ only in composition depth, confirmation gates, and scoring rigor—not in fundamental approach.

### 1.2 Why This Fragmentation Exists

The five skills evolved through incremental composition:

1. **comparative-analysis** was the original lightweight workflow.
2. **comparative-decision-analysis** added mandatory discovery and evidence discipline for high-stakes decisions (vendor selection, architecture choices).
3. **comparative-decision-review** extracted common patterns from skill-reviewer to standardize rubric confirmation and tie-break logic.
4. **hybrid-decision-analysis** composed all three to offer flexibility within a single skill.
5. **hybrid-decision-analysis.v1** maintained a stable snapshot for production use.

This path produced sophistication but at the cost of clarity and maintainability.

### 1.3 User Confusion: Which Skill to Use When?

Users face a confusing choice matrix:

- **"I have 3 options. Which should I pick?"** → comparative-analysis? hybrid-decision-analysis?
- **"I need to evaluate vendors. Can I trust the result?"** → comparative-decision-analysis? comparative-decision-review?
- **"I need to decide but don't know which skill to use."** → skill-reviewer? hybrid-decision-analysis?

This ambiguity leads to:

- **Skill selection paralysis**: Users uncertain about which skill fits their context.
- **Redundant invocations**: Users run multiple skills to hedge uncertainty.
- **Incomplete decision records**: Inconsistent output formats and confidence metrics across skills.
- **Maintenance fragmentation**: Bug fixes, protocol updates, and schema changes must be replicated across five codebases.

### 1.4 Maintenance Burden

Five separate skills means:

- **Five input schemas** to maintain (comparative-analysis, comparative-decision-analysis, comparative-decision-review, hybrid, hybrid.v1).
- **Five script directories** (scoring harness, guardrails, bakeoff validation).
- **Five decision record templates** (with subtle format differences).
- **Five sets of rubric packs and references** (discovery protocol, scenario-bakeoff protocol, quality gates).
- **Multiplicative testing burden** as new use cases prove one workflow outperforms others.

## 2. Goals and Non-Goals

### 2.1 Goals

1. **Single Entry Point**: Establish one `decision-analysis` skill as the authoritative interface for all comparative decision workflows.
2. **Three Documented Modes**: Implement lite, structured, and rigorous modes with clear selection criteria and documented use cases.
3. **No Breaking Changes**: Existing workflows and decision records remain valid; provide clear migration examples for each legacy skill.
4. **Unified Decision Record**: Standardize the decision record format across all modes for consistency and traceability.
5. **Clear Mode Selection**: Provide a decision tree and heuristics to guide users to the correct mode for their context.
6. **Preserved Semantics**: Each mode preserves the logic and guarantees of its source skill; consolidation is organizational, not semantic.
7. **Complete Migration Path**: Establish clear steps for consolidation, including deprecation timeline and backward compatibility considerations.

### 2.2 Non-Goals

1. **Change algorithm semantics**: The consolidation does not alter the scoring logic, ranking behavior, or recommendation thresholds of any mode.
2. **Introduce new evaluation capabilities**: This RFC does not add new criteria derivation strategies, scoring methods, or discovery protocols.
3. **Remove evidence discipline**: The rigorous mode preserves all mandatory discovery, parallel evaluation, and evidence gates.
4. **Mandate mode upgrades**: Users may continue using lite mode for simple decisions without pressure to upgrade to structured or rigorous.
5. **Immediately remove legacy skills**: Deprecation happens over time; legacy skills remain with clear forwarding references to the new unified skill.

## 3. Detailed Specification

### 3.1 Mode 1: Lite Mode

**Source Skills**: comparative-analysis

**Description**: Fast, repeatable comparative analysis for straightforward decisions with explicit criteria and deterministic scoring. Ideal for skill selection, tool comparison, and architectural choices where external options are not mandatory.

**When to Use**:

- User has 3–5 clear alternatives.
- Decision timeline is immediate or near-term.
- External (vendor, competitor, outsourced) options are not critical.
- Evaluation time budget is limited (< 30 minutes).
- Goals are clear without extensive discovery.

**Input Contract**:

```typescript
interface LiteInput {
  decision: string; // One-sentence decision statement
  current_platform: string; // LLM platform (for platform-specific scoring)
  major_platforms?: string[]; // Cross-platform comparison set (default: [chatgpt, claude, gemini, copilot])
  context: {
    primary_user: string; // User role and workflow context
    hard_constraints: string[]; // Must-have requirements
    non_goals: string[]; // Out of scope
    time_horizon: "immediate" | "near-term" | "long-term";
  };
  alternatives: Array<{
    // 3–5 alternatives minimum
    id: string;
    name: string;
    description?: string;
  }>;
  criteria?: Array<{
    // Optional: provide custom criteria, or derive in workflow
    id: string;
    name: string;
    weight: number;
    metric: string;
    scoring_rule: string;
  }>;
}
```

**Workflow**:

1. Define intended use (decision, current platform, context).
2. Identify and normalize 3–5 alternatives.
3. Derive criteria (5–9 weighted criteria) or confirm provided criteria.
4. Evaluate each alternative against criteria.
5. Compute deterministic scores and rank options.
6. Issue recommendation with action (select, improve, extend, compose, build-new).
7. Capture lightweight decision record.

**Output Contract**:

```typescript
interface LiteOutput {
  decision: string;
  alternatives_ranked: Array<{
    rank: number;
    id: string;
    name: string;
    major_platform_avg: number; // 0–100 score average across major platforms
    current_platform_score: number; // Platform-specific score
    overall_success: number; // Blended score (~0.6 major + 0.4 current)
    coverage: number; // 0–1: fraction of criteria scored
  }>;
  recommendation: {
    action: "select" | "improve" | "extend" | "compose" | "build-new";
    chosen_option_ids: string[];
    justification: string; // Explicit score deltas and rationale
    risks: string[];
    next_actions: string[];
  };
  decision_record_url: string; // Link to markdown decision record
}
```

**Decision Record Template**: Lightweight 1-page record with decision, alternatives table, and recommendation. (See section 3.4 for unified template.)

### 3.2 Mode 2: Structured Mode

**Source Skills**: comparative-decision-review

**Description**: Structured comparative decision workflow with mandatory rubric confirmation, explicit evidence notes, and tie-break logic (effort, risk, coverage). Suitable for team decisions, architecture reviews, and medium-stakes vendor evaluations.

**When to Use**:

- Multiple stakeholders must agree on criteria.
- Decision requires effort and risk assessment per alternative.
- Platform-specific fit matters (e.g., current LLM vs. major platforms).
- Evidence gaps or uncertainty must be explicit.
- Audit trail and traceability are important.

**Input Contract**:

```typescript
interface StructuredInput {
  decision: string;
  current_platform: string;
  major_platforms?: string[];
  context: {
    primary_user: string;
    primary_users: string[]; // Multiple stakeholders
    hard_constraints: string[];
    non_goals: string[];
    time_horizon: "immediate" | "near-term" | "long-term";
  };
  alternatives: Array<{
    id: string;
    name: string;
    effort: "S" | "M" | "L"; // Required: effort estimate
    risk: "Low" | "Med" | "High"; // Required: risk classification
    description?: string;
    key_dependencies?: string[];
    major_unknowns?: string[];
  }>;
  criteria?: Array<{
    id: string;
    name: string;
    weight: number;
    metric: string;
    scoring_rule: string;
    evidence_required?: boolean; // Request explicit evidence per score
  }>;
}
```

**Workflow**:

1. Frame decision and option set (effort/risk per alternative).
2. Derive criteria or confirm provided criteria.
3. **Confirmation gate**: Present criteria, weights, platforms, and effort/risk matrix. Wait for stakeholder sign-off.
4. Evaluate each alternative with explicit evidence notes.
5. Score with multi-platform blending and tie-break logic.
6. Rank and apply deterministic action rules.
7. Capture detailed decision record with evidence references.

**Output Contract**:

```typescript
interface StructuredOutput {
  decision: string;
  confirmation_source: "user-confirmed" | "yolo-mode" | "provided-input";
  alternatives_ranked: Array<{
    rank: number;
    id: string;
    name: string;
    effort: "S" | "M" | "L";
    risk: "Low" | "Med" | "High";
    major_platform_avg: number;
    current_platform_score: number;
    overall_success: number;
    coverage: number;
    evidence_notes?: string[]; // Explicit evidence per score
  }>;
  recommendation: {
    action: "select" | "improve" | "extend" | "compose" | "build-new";
    chosen_option_ids: string[];
    margin_vs_second: number; // Score delta to illustrate confidence
    rationale: string; // Evidence-linked with score deltas
    risks: string[];
    next_actions: string[];
  };
  decision_record_url: string;
}
```

**Decision Record Template**: 2–3 page record with decision, confirmed criteria table, alternatives table with effort/risk, evidence notes, and detailed recommendation. (See section 3.4.)

### 3.3 Mode 3: Rigorous Mode

**Source Skills**: comparative-decision-analysis

**Description**: Rigorous comparative decision analysis with mandatory discovery (including external options), evidence discipline, parallel evaluators, and deterministic scoring harness. For high-stakes decisions (vendor selection, major architecture, competitive analysis) where reliability and auditability are paramount.

**When to Use**:

- Decision impacts architecture, vendor lock-in, or competitive position.
- External (vendor, competitor) alternatives are mandatory.
- Multiple independent evaluators strengthen credibility.
- Evidence discipline and repeatability are non-negotiable.
- Legal, financial, or strategic implications exist.
- Decision may be challenged or require forensic replay.

**Input Contract**:

```typescript
interface RigorousInput {
  decision: string;
  current_platform: string;
  major_platforms?: string[];
  context: {
    primary_user: string;
    primary_users: string[];
    hard_constraints: string[];
    non_goals: string[];
    time_horizon: "immediate" | "near-term" | "long-term";
    strategic_implications?: string; // Reason for rigor
  };
  discovery_scope?: {
    // Mandatory discovery rules
    include_external: boolean; // Default: true; false requires explicit justification
    include_compose_variants: boolean; // Default: true
    include_extend_variants: boolean; // Default: true
  };
  alternatives: Array<{
    id: string;
    name: string;
    feasible: boolean; // Required: explicit feasibility gate
    description?: string;
    source: "internal" | "external" | "variant" | "new"; // Provenance
    key_dependencies?: string[];
    major_unknowns?: string[];
  }>;
  criteria?: Array<{
    id: string;
    name: string;
    weight: number;
    metric: string;
    data_source: string; // Required: evidence source
    scoring_rule: string;
  }>;
}
```

**Workflow**:

1. Frame decision and constraints.
2. **Mandatory discovery**: Run discovery protocol to identify internal, external, compose, and extend alternatives. Include ≥1 external option unless explicitly blocked.
3. Normalize alternatives (mark feasible/infeasible).
4. Derive criteria from intended use with `rubric-packs` as starting point.
5. **Confirmation gate**: Present criteria, weights, scoring scale, platform set, and discovery summary. Wait for confirmation.
6. **Parallel evaluators**: Spawn isolated evaluator subagent per alternative; run in parallel.
7. Prepare input for deterministic harness (`references/input-schema.md`).
8. Execute deterministic harness:

   ```bash
   python3 skills/workflow/decision-analysis/scripts/run_decision_harness.py \
     --mode rigorous \
     --input <analysis-input.json> \
     --output-dir <run-output-dir>
   ```

9. Run reliability checks (sensitivity analysis, bakeoff validation).
10. Capture comprehensive decision record with discovery log and reliability notes.

**Output Contract**:

```typescript
interface RigorousOutput {
  decision: string;
  criteria_confirmation_source:
    | "user-confirmed"
    | "yolo-mode"
    | "provided-input";
  discovery_summary: {
    internal_options_found: number;
    external_options_found: number;
    compose_variants: number;
    extend_variants: number;
    discovery_protocol_ref: string; // Link to discovery notes
  };
  alternatives_ranked: Array<{
    rank: number;
    id: string;
    name: string;
    feasible: boolean;
    source: "internal" | "external" | "variant" | "new";
    major_platform_avg: number;
    current_platform_score: number;
    overall_success: number;
    coverage: number;
    evaluator_id?: string[]; // References to independent evaluators
    evidence: {
      criterion_id: string;
      score: number;
      justification: string;
      data_source: string;
      reliability?: "high" | "medium" | "low";
    }[];
  }>;
  reliability_checks: {
    sensitivity_analysis?: string; // Sensitivity to weight changes
    bakeoff_results?: string; // Scenario-based validation
    uncertainty_notes: string[];
  };
  recommendation: {
    action: "select" | "improve" | "extend" | "compose" | "build-new";
    chosen_option_ids: string[];
    margin_vs_second: number;
    rationale: string;
    residual_risks: string[];
    follow_up_actions: string[];
  };
  decision_record_url: string;
  harness_output_dir: string; // Link to deterministic harness results
}
```

**Decision Record Template**: 4–6 page comprehensive record with full discovery log, confirmed criteria with data sources, alternatives with independent evaluations, reliability analysis, detailed recommendation, and appendix with score justifications. (See section 3.4.)

### 3.4 Unified Decision Record

All three modes produce a decision record in a unified schema and markdown template. The template scales from lightweight (lite) to comprehensive (rigorous):

```markdown
# Decision Record: {Decision}

## Metadata

- **Date**: {yyyy-mm-dd}
- **Reviewer**: {name}
- **Mode**: lite | structured | rigorous
- **Decision Statement**: {one sentence}
- **Current Platform**: {platform name}
- **Major Platforms**: {comma-separated list}

## Intended Use

- **Primary User**: {role and context}
- **Hard Constraints**: {bullets}
- **Non-Goals**: {bullets}
- **Time Horizon**: immediate | near-term | long-term

## Confirmed Criteria

| Criterion |   Weight | Metric   | Data Source | Scoring Rule |
| --------- | -------: | -------- | ----------- | ------------ |
| {name}    | {weight} | {metric} | {source}    | {rule}       |

_(Rigorous mode only: Include evidence reliability per criterion.)_

## Discovery Log

_(Structured and rigorous modes only.)_

- **Internal Options**: {count} found
- **External Options**: {count} found
- **Compose Variants**: {count} found
- **Extend Variants**: {count} found
- **Discovery Protocol Reference**: {link to detailed notes}

## Alternatives

| Rank | Alternative | Feasible | Effort  | Risk           | Major Platform Avg | Current Platform | Overall Success | Coverage | Action Hint                                   |
| ---: | ----------- | -------- | ------- | -------------- | -----------------: | ---------------: | --------------: | -------: | --------------------------------------------- |
|  {n} | {name}      | {yes/no} | {S/M/L} | {Low/Med/High} |            {score} |          {score} |         {score} |    {0-1} | {select\|improve\|extend\|compose\|build-new} |

_(Rigorous mode only: Include evidence notes and reliability flags per row.)_

## Recommendation

- **Action**: select | improve | extend | compose | build-new
- **Chosen Option(s)**: {ids}
- **Margin vs Second**: {score delta}
- **Rationale**: {Evidence-linked reason with score deltas}
- **Residual Risks**: {bullets}
- **Follow-Up Actions**: {bullets}

## Reliability Assessment

_(Structured and rigorous modes only.)_

- **Confidence**: high | medium | low
- **Uncertainty Notes**: {evidence gaps, sensitivity}
- **Validation Results**: {bakeoff, sensitivity analysis}

## Appendices (Rigorous mode only)

- **Appendix A**: Score Justifications (per alternative, per criterion)
- **Appendix B**: Evaluator Notes (independent evaluator context and reasoning)
- **Appendix C**: Score Sensitivity Analysis
- **Appendix D**: Discovery Protocol Details
```

### 3.5 Mode Selection Decision Tree

Guide users to the correct mode:

```asciiflow
┌─ Do you have external (vendor, competitor) options that are mandatory?
│  ├─ YES → Rigorous mode (external discovery is mandatory)
│  └─ NO (internal focus only)
│     ├─ Do multiple stakeholders need to agree on criteria?
│     │  ├─ YES → Structured mode (confirmation gate + stakeholder clarity)
│     │  └─ NO (single user decision)
│     │     ├─ Is the decision high-stakes (architecture, vendor lock-in, legal)?
│     │     │  ├─ YES → Structured or Rigorous (evidence matters)
│     │     │  └─ NO (straightforward choice)
│     │     │     ├─ Do you have <30 minutes and 3–5 clear alternatives?
│     │     │     │  ├─ YES → Lite mode (fast, deterministic)
│     │     │     │  └─ NO → Structured mode (more time, more evidence)
```

**Heuristic Summary**:

| Context                                                       | Mode           | Reason                                  |
| ------------------------------------------------------------- | -------------- | --------------------------------------- |
| Simple, 3–5 options, immediate deadline, single user          | **Lite**       | Speed and clarity                       |
| Multiple stakeholders, effort/risk matters, medium-stakes     | **Structured** | Confirmation gate + tie-break logic     |
| External options mandatory, high-stakes, audit trail required | **Rigorous**   | Discovery discipline + evidence harness |

## 4. Implementation Foundation (Parallel Analysis)

This RFC builds on comprehensive analysis performed in parallel across schema consolidation, code reduction metrics, and implementation sequencing:

- **[consolidated-schema.md](../reference/consolidated-schema.md)**: Unified input/output contracts mapping all 5 legacy skills into lite/structured/rigorous modes. Demonstrates 63% code reduction (2,116 lines → 800 lines unified scorer).
- **[script-dependencies.md](../reference/script-dependencies.md)**: Complete Python script consolidation with unified harness skeleton and mode-routing logic.
- **[quick-reference.md](../reference/quick-reference.md)**: User-facing mode selection guide with decision flowchart.

The 6-week implementation timeline in Section 5.1 is grounded in these parallel findings and verified through feasibility analysis of code consolidation metrics.

## 5. Input/Output Contracts for Each Mode

All modes accept a common **base input** (decision, context, alternatives) with mode-specific extensions:

```typescript
interface DecisionAnalysisInput {
  // Base (all modes)
  decision: string;
  current_platform: string;
  major_platforms?: string[];
  context: {
    primary_user: string;
    hard_constraints?: string[];
    non_goals?: string[];
    time_horizon: "immediate" | "near-term" | "long-term";
  };
  alternatives: Array<{ id: string; name: string; description?: string }>;

  // Lite mode optional
  criteria?: Array<{ id: string; name: string; weight: number; metric: string; scoring_rule: string }>;

  // Structured mode additions
  alternatives?: Array<{ id: string; name: string; effort?: "S" | "M" | "L"; risk?: "Low" | "Med" | "High"; ... }>;
  evidence_required?: boolean[];

  // Rigorous mode additions
  discovery_scope?: { include_external: boolean; ... };
  alternatives?: Array<{ id: string; feasible: boolean; source: "internal" | "external" | "variant" | "new"; ... }>;
  criteria?: Array<{ id: string; data_source: string; ... }>;
}
```

All modes return a common **base output** (decision, ranked alternatives, recommendation) with mode-specific extensions:

```typescript
interface DecisionAnalysisOutput {
  // Base (all modes)
  decision: string;
  alternatives_ranked: Array<{ rank: number; id: string; name: string; major_platform_avg: number; overall_success: number; ... }>;
  recommendation: { action: string; chosen_option_ids: string[]; justification: string; risks: string[]; };

  // Structured mode additions
  confirmation_source: "user-confirmed" | "yolo-mode";
  alternatives_ranked[].evidence_notes?: string[];

  // Rigorous mode additions
  discovery_summary: { internal_options: number; external_options: number; ... };
  reliability_checks: { sensitivity_analysis?: string; bakeoff_results?: string; };
  harness_output_dir?: string;
}
```

## 5. Migration Path

### 5.1 Consolidation Steps

**Implementation Note**: This timeline is validated against the consolidated schema analysis (script-dependencies.md), which confirms the unified decision_harness.py can be implemented in ~800 lines, reducing total decision-analysis package size by 63% vs. maintaining 5 legacy skills in parallel.

#### **Phase 1: Unified Skill Skeleton (Week 1)**

1. Create `/skills/workflow/decision-analysis/` directory structure.
2. Create unified `SKILL.md` with all three modes documented.
3. Port `scripts/decision_harness.py` using unified skeleton from script-dependencies.md (verified feasible: 800-line implementation supporting all 3 modes).
4. Create unified `references/input-schema.md` and `references/input-schema.json` from consolidated-schema.md.
5. Create unified `assets/decision-record-template.md`.

#### **Phase 2: Port Lite Mode (Week 1)**

1. Copy comparative-analysis logic into `decision-analysis` as mode selector `--mode lite`.
2. Update `scripts/decision_harness.py` to handle lite mode inputs.
3. Create test suite for lite mode parity with comparative-analysis.
4. Validate decision records match lite template.

#### **Phase 3: Port Structured Mode (Week 2)**

1. Copy comparative-decision-review logic into `decision-analysis` as `--mode structured`.
2. Port rubric confirmation gate and tie-break logic.
3. Port effort/risk scoring rules.
4. Update test suite; validate parity with comparative-decision-review.

#### **Phase 4: Port Rigorous Mode (Week 2)**

1. Copy comparative-decision-analysis logic into `decision-analysis` as `--mode rigorous`.
2. Port discovery protocol and parallel evaluator orchestration.
3. Port deterministic harness and reliability checks.
4. Update test suite; validate parity with comparative-decision-analysis.

#### **Phase 5: Validation and Quality Gates (Week 3)**

1. Run bakeoff: Re-run 10 historical decisions using all three modes; verify recommendations match source skills.
2. Schema validation: Ensure input/output contracts are satisfied.
3. Decision record format: Generate decision records from all modes; verify against unified template.
4. Cross-platform scoring: Validate major-platform blending and current-platform fit.

#### **Phase 6: Documentation and Migration Guides (Week 3)**

1. Write mode selection decision tree.
2. Create migration guide for each legacy skill:
   - "Moving from comparative-analysis to decision-analysis (lite mode)"
   - "Moving from comparative-decision-review to decision-analysis (structured mode)"
   - "Moving from comparative-decision-analysis to decision-analysis (rigorous mode)"
3. Create hybrid-decision-analysis sunset guide (explains how compose both + comparative-analysis → decision-analysis).

### 5.2 Deprecation Timeline

| Timeline               | Action                                                                                                                                                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Week 4 (immediate)** | Release decision-analysis v1.0 with full mode parity. Update all documentation and migration guides.                                                                                                            |
| **Months 1–3**         | Mark comparative-analysis, comparative-decision-review, comparative-decision-analysis as **deprecated**. Add deprecation notices + forwarding references to decision-analysis. Maintain backward compatibility. |
| **Month 6**            | Remove hybrid-decision-analysis.v1 (encourage users to move to decision-analysis v1.0).                                                                                                                         |
| **Month 9**            | Archive legacy skills (comparative-analysis, comparative-decision-review, comparative-decision-analysis) to `/skills/archive/`. Update SKILL_REVIEW_ASSESSMENT.md.                                              |
| **Month 12**           | Remove legacy skill directories from active library (if no production use remains).                                                                                                                             |

### 5.3 Backward Compatibility

**Preservation**:

- All input schemas from legacy skills remain valid. Internal adapter converts legacy input to unified schema.
- All decision records from legacy skills remain valid. Unified skill can read and extend legacy records.
- All scripts remain functional. Python harness detects mode and invokes appropriate logic.

**Migration Helpers**:

1. **Input adapter**: Helper function `legacy_input_to_unified(skill_name, legacy_input)` → unified input.
2. **Record merger**: Extend legacy decision record with additional mode-specific sections (e.g., add structured evidence notes to lite record).
3. **Decision tree CLI**: Standalone tool to help users select mode based on context.

#### **Example Migration: From comparative-analysis to decision-analysis (lite)**

```bash
# Old:
@agent use comparative-analysis to choose between tools X, Y, Z

# New:
@agent use decision-analysis in lite mode to choose between tools X, Y, Z

# Or (no mode specified, auto-detect):
@agent use decision-analysis to choose between tools X, Y, Z
# [tool detects: single user, <30 min, 3 options → routes to lite mode]
```

## 6. References

### 6.1 Current Skills (To Be Consolidated)

- [comparative-analysis](../../skills/workflow/comparative-analysis/SKILL.md) – Lite mode source
- [comparative-decision-analysis](../../skills/workflow/comparative-decision-analysis/SKILL.md) – Rigorous mode source
- [comparative-decision-review](../../skills/workflow/comparative-decision-review/SKILL.md) – Structured mode source
- [hybrid-decision-analysis](../../skills/workflow/hybrid-decision-analysis/SKILL.md) – Hybrid composition reference
- [hybrid-decision-analysis.v1](../../skills/workflow/hybrid-decision-analysis.v1/SKILL.md) – Stable variant reference
- [skill-reviewer](../../skills/workflow/skill-reviewer/SKILL.md) – Evidence discipline patterns

### 6.2 Related Documentation

- [consolidated-schema.md](../reference/consolidated-schema.md) – (Parallel analysis 1) Unified input/output schema definitions; 2,300 lines documenting schema consolidation strategy with 63% code reduction metrics
- [script-dependencies.md](../reference/script-dependencies.md) – (Parallel analysis 1) Python script consolidation feasibility; unified scorer skeleton (~800 lines) and mode-routing logic
- [quick-reference.md](../reference/quick-reference.md) – (Parallel analysis 1) Mode selection decision flowchart and 30-second reference guide
- [Skill Composition Guide](../../docs/SKILL_COMPOSITION.md) – How to compose decision-analysis with other skills
- [Workflow Framework Plan](../../docs/SKILL_LIBRARY_PLAN.md) – Overall PAX architecture and vision
- **Parallel Initiative**: [PR Workflow Recommendations](../architecture/pr-workflow-recommendations.md) – Independent consolidation of PR-related skills (coordinated cross-track timeline in Section 5.2)

### 6.3 Supporting Protocols and Specifications

- [Discovery Protocol](../../skills/workflow/comparative-decision-analysis/references/discovery-protocol.md) – Used by rigorous mode
- [Rubric Packs](../../skills/workflow/comparative-decision-analysis/references/rubric-packs.md) – Criterion templates shared by all modes
- [Scenario Bakeoff Protocol](../../skills/workflow/comparative-decision-analysis/references/scenario-bakeoff-protocol.md) – Reliability validation for rigorous mode
- [Input Schema (JSON)](../../skills/workflow/comparative-decision-analysis/references/input-schema.json) – Formal schema for analysis input
- [Quality Gates](../../skills/workflow/comparative-decision-analysis/references/quality-gates.md) – Guardrails for rigorous mode

### 6.4 Standards and Conventions

- BCP 14: [RFC 2119](https://tools.ietf.org/html/rfc2119) – Key words for use in RFCs
- PAX Skills Format: [FRONTMATTER_SPECIFICATION.md](../../docs/conventions/FRONTMATTER_SPECIFICATION.md)
- PAX Skills Naming: [NAMING_CONVENTIONS.md](../../docs/conventions/NAMING_CONVENTIONS.md)
- File Organization: [FILE_ORGANIZATION.md](../../docs/reference/FILE_ORGANIZATION.md)

## 7. Appendices

### Appendix A: Cross-Track Coordination with PR Refactoring

This effort is part of a coordinated dual-stream skills consolidation:

1. **Decision-Analysis Consolidation** (this RFC): 5 overlapping skills → 1 skill with 3 modes. Timeline: 6 weeks (Weeks 1-3 implementation, Weeks 4-6 validation + deprecation). Execution path: Lite → Structured → Rigorous modes ported sequentially, then bakeoff validation.

2. **PR Workflow Refactoring** (parallel): 6 PR-related skills → 3 core skills (keep merge-pr, resolve-pr-comments, handle-pr-feedback; deprecate process-pr; consolidate tooling). Timeline: 4 phases over 5 weeks. **Blocker alert**: Requires resolution of PR tool parity gap (check-status operation undocumented in copilot-pull-request; documented in gh-pr-review). See [pr-parity-validation-report.md](../architecture/pr-parity-validation-report.md) for infrastructure prerequisites.

Both tracks are independent (no direct blocking dependencies), but should coordinate on overall skills library timeline and deprecation messaging.

### Appendix B: Example Mode Selection Scenarios

#### **Scenario 1: Simple Tool Comparison (Lite)**

> "We have a choice between Langchain, LlamaIndex, and Semantic Kernel. Which is best for building a document Q&A bot?"

- **Factors**: Single product manager, 3 alternatives, 1-week deadline, internal focus only.
- **Selected Mode**: Lite
- **Decision Record**: 1-page record with 3 tools, 5 criteria (compatibility, community, docs, performance, cost), overall winner.

#### **Scenario 2: Multi-Stakeholder Architecture Decision (Structured)**

> "We need to decide between microservices, monolith, and serverless for our renewal. Requires buy-in from 5 teams."

- **Factors**: Multiple stakeholders, effort/risk assessment mandatory, architectural impact, audit trail needed.
- **Selected Mode**: Structured
- **Decision Record**: 3-page record with confirmed rubric, effort/risk matrix, evidence per alternative, team-signed recommendation.

#### **Scenario 3: Vendor Selection (Rigorous)**

> "We're evaluating 4 AI platforms (OpenAI, Anthropic, Google, Meta) for a 50M token/year contract. Decision impacts product roadmap."

- **Factors**: External vendors mandatory, multi-year financial commitment, competitive analysis required, discovery of alternatives critical.
- **Selected Mode**: Rigorous
- **Decision Record**: 6-page comprehensive record with discovery log (why we chose these 4), independent evaluators per vendor, sensitivity analysis (what if token prices drop 20%?), signed recommendation by leadership.

### Appendix B: Unified Input Schema (JSON)

_(See parallel task [consolidated-schema.md](../reference/consolidated-schema.md) for full schema.)_

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "decision-analysis input schema",
  "type": "object",
  "required": [
    "decision",
    "current_platform",
    "context",
    "alternatives",
    "mode"
  ],
  "properties": {
    "decision": { "type": "string", "minLength": 1 },
    "mode": { "enum": ["lite", "structured", "rigorous"] },
    "current_platform": { "type": "string" },
    "major_platforms": { "type": "array", "items": { "type": "string" } },
    "context": {
      "type": "object",
      "required": ["primary_user", "time_horizon"]
    },
    "alternatives": {
      "type": "array",
      "minItems": 2,
      "items": { "type": "object" }
    },
    "criteria": { "type": "array", "items": { "type": "object" } },
    "discovery_scope": { "type": "object" },
    "evidence_required": { "type": "boolean" }
  }
}
```

### Appendix C: Open Issues and Future Work

| Issue                                             | Status | Disposition                                                                                                                          |
| ------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Parallel evaluator synchronization**            | Open   | Rigorous mode uses timeout-based coordination; consider message-passing framework for v2.0.                                          |
| **Cross-platform weighting**                      | Open   | Current weights (0.6 major, 0.4 current) are empirically derived; consider user-configurable blending for domain-specific platforms. |
| **Bakeoff protocol limits**                       | Open   | Bakeoff works best for <5 alternatives; for larger option sets, consider hierarchical screening phase.                               |
| **Mobile and embedded platform support**          | Open   | Current platforms focus on LLM (ChatGPT, Claude, etc.). Extend framework to edge platforms and specialized hardware?                 |
| **Integration with external decision frameworks** | Open   | Consider wrapping Kepner-Tregoe, RACI, or other formal decision frameworks as optional adapters.                                     |

### Appendix D: Change Log

#### Changes Since draft-00 (this version)

- Initial RFC draft with three modes fully specified.
- Added unified input/output schemas and decision record template.
- Defined mode selection decision tree and migration path.
- Established deprecation timeline (Months 1–12).

---

## Document Metadata

| Field                       | Value                                                                          |
| --------------------------- | ------------------------------------------------------------------------------ |
| **RFC Title**               | Decision-Making Skills Suite Consolidation                                     |
| **RFC ID**                  | rfc-dt-001                                                                     |
| **Status**                  | Draft                                                                          |
| **Version**                 | 1.0                                                                            |
| **Date Created**            | 2026-02-25                                                                     |
| **Last Updated**            | 2026-02-25                                                                     |
| **Proposed Effective Date** | 2026-03-15 (upon approval)                                                     |
| **Target Audience**         | PAX core team, skill library maintainers, users of decision-analysis workflows |
| **Approval Required From**  | PAX RFC Review Board                                                           |
| **Next Review Point**       | Post-Phase 2 completion (Week 4 of consolidation)                              |

---

## IANA Considerations

No IANA registries are affected by this RFC.

## Security Considerations

The decision-analysis skill consolidation does not introduce new security considerations beyond those documented in the individual legacy skills. All three modes preserve existing evidence discipline, audit trails, and decision record persistence. Consolidation is a refactoring; no new attack vectors are introduced.

Some specific notes:

- **Evaluator isolation** (rigorous mode): Parallel evaluators remain isolated to prevent information leakage between evaluations.
- **Input validation**: Unified input schema MUST be strictly validated to prevent injection or malformed decision framing.
- **Decision record persistence**: All decision records MUST be immutable once signed; use cryptographic hashing if audit requirements escalate.

## Conclusion

Consolidating five overlapping decision-analysis skills into a single unified skill with three modes drastically simplifies the PAX skills library and clarifies the user experience. The consolidation preserves all existing semantics, maintains backward compatibility, and establishes a clear migration path with a 12-month deprecation timeline. The unified `decision-analysis` skill will become the authoritative interface for comparative decision workflows across all user needs—from quick choices (lite) to multi-stakeholder decisions (structured) to high-stakes vendor evaluation (rigorous).
