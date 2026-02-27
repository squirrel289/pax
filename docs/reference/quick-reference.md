# Quick Reference: Decision-Analysis Consolidation Roadmap

**Date**: 2026-02-25  
**Status**: Ready for Phase 1 implementation

---

## TL;DR: The 5 → 3 Consolidation

| Current                       | Merged Into       | Mode     | Python Script     | Size      |
| ----------------------------- | ----------------- | -------- | ----------------- | --------- |
| comparative-analysis          | decision-analysis | lite     | score_decision.py | ~800 L    |
| comparative-decision-review   | decision-analysis | medium   | score_decision.py | (unified) |
| comparative-decision-analysis | decision-analysis | rigorous | score_decision.py | (unified) |
| hybrid-decision-analysis      | decision-analysis | rigorous | score_decision.py | (unified) |
| hybrid-decision-analysis.v1   | Archive           | -        | -                 | -         |

**Benefit**: 2,116 lines of code → ~800 lines (63% reduction)

---

## Mode Selection Flowchart

```asciitree
Do you have pre-identified options?
├─ YES
│  ├─ Do you need effort/risk assessment or 1-5 scale support?
│  │  ├─ NO → LITE (comparative-analysis)
│  │  │  Use for: Quick selection, 0-100 scoring only
│  │  │  Input: decision, current_platform, criteria (id, name, weight), alternatives (scores)
│  │  │  Output: ranked_alternatives, recommendation.action
│  │  │
│  │  └─ YES → MEDIUM (comparative-decision-review)
│  │     Use for: Balanced rigor, effort/risk, qualitative (1-5) or quantitative (0-100)
│  │     Input: + criteria_confirmed, score_scale, effort, risk, justification, coverage
│  │     Output: + effort_rank, risk_rank, coverage
│  │
│  └─ Do you need discovery audit trail, independent evaluators, or JSON Schema validation?
│     ├─ NO → MEDIUM (sufficient)
│     │
│     └─ YES → RIGOROUS (comparative-decision-analysis + hybrid-decision-analysis)
│        Use for: High-stakes decisions, audit trail, external discovery proof
│        Input: + independent_evaluations (CDA) or discovery (HDA) + type + evidence
│        Output: + run_id, decision_status, scorer_version, evaluated_at
│
└─ NO
   └─ Run RIGOROUS with discovery protocol to identify options first
      Then re-evaluate with MEDIUM or RIGOROUS
```

---

## Input Schema Differences at a Glance

### Lite (comparative-analysis)

```json
{
  "decision": "string",
  "current_platform": "string",
  "criteria": [
    {"id": "string", "name": "string", "weight": number}
  ],
  "alternatives": [
    {
      "id": "string",
      "name": "string",
      "scores": {
        "platform": {"criterion-id": 0-100 or null}
      }
    }
  ]
}
```

**Validation**: Basic (id/name/weight present, 0-100 scores)  
**No gating**: Scores immediately

### Medium (comparative-decision-review)

```json
{
  "decision": "string",
  "current_platform": "string",
  "criteria_confirmed": boolean,
  "score_scale": "0-100" | "1-5",
  "criteria": [
    {
      "id": "string",
      "name": "string",
      "weight": number,
      "metric": "string",        // How to measure
      "data_source": "string",   // Where evidence comes from
      "scoring_rule": "string"   // Guidance for scoring
    }
  ],
  "alternatives": [
    {
      "id": "string",
      "name": "string",
      "effort": "S" | "M" | "L",
      "risk": "Low" | "Med" | "High",
      "feasible": boolean,
      "justification": "string", // Why this option?
      "scores": {
        "platform": {"criterion-id": 1-5 or 0-100 or null}
      }
    }
  ]
}
```

**Validation**: Medium (criteria_confirmed optional; effort, risk required on alternatives)  
**1-5 to 0-100 conversion**: `1-5 × 20 = 0-100`

### Rigorous (comparative-decision-analysis + hybrid-decision-analysis)

```json
{
  "decision": "string",
  "current_platform": "string",
  "criteria_confirmed": true,  // MUST be true
  "criteria_confirmation_source": "user-confirmed" | "provided-input" | "yolo-mode",
  "score_scale": "0-100" | "1-5",
  "criteria": [
    {
      "id": "string",
      "name": "string",
      "weight": number,
      "metric": "string",        // REQUIRED (not optional)
      "data_source": "string",   // REQUIRED
      "scoring_rule": "string"   // REQUIRED
    }
  ],
  "alternatives": [
    {
      "id": "string",
      "name": "string",
      "type": "internal" | "compose" | "external" | "build-new",  // HDA only
      "effort": "S" | "M" | "L",
      "risk": "Low" | "Med" | "High",
      "feasible": boolean,
      "justification": "string",
      "evidence": [              // HDA: required if type="external"
        {
          "source_url": "string (URI)",
          "source_date": "string (ISO 8601)",
          "evidence_strength": "low" | "medium" | "high"
        }
      ],
      "scores": {
        "platform": {"criterion-id": 1-5 or 0-100 or null}
      }
    }
  ],

  // CDA-specific
  "independent_evaluations": [
    {
      "alternative_id": "string",  // Must match alternative.id
      "evaluator_id": "string",    // Unique per alternative
      "isolation_confirmed": true, // Required constant
      "summary": "string"          // Isolated finding
    }
  ],

  // HDA-specific
  "discovery": {
    "external_discovery_done": boolean,
    "external_discovery_blocked": boolean,
    "block_reason": "string"  // Required if blocked=true
  }
}
```

**Validation**: Strict (criteria_confirmed=true required; metric/data_source/scoring_rule required on criteria)  
**JSON Schema validation**: input.schema.json (HDA only)

---

## Output Comparison

### Lite & Medium Output

```json
{
  "decision": "string",
  "ranked_alternatives": [
    {
      "id": "string",
      "name": "string",
      "rank": integer,
      "major_platform_average": 0-100,
      "current_platform_score": 0-100,
      "overall_success_score": 0-100,
      "justification": "string",

      // Medium only
      "effort": "S|M|L",
      "risk": "Low|Med|High",
      "effort_rank": integer,
      "risk_rank": integer,
      "coverage": 0-1,
      "feasible": boolean
    }
  ],
  "recommendation": {
    "action": "select" | "compose" | "improve" | "extend" | "build-new",
    "chosen_option_ids": ["string"],
    "top_option_id": "string",
    "score_margin_vs_second": number,
    "reason": "string"
  }
}
```

### Rigorous Output

```json
{
  "decision": "string",
  "mode": "rigorous",
  "run_id": "string",                    // Unique identifier
  "scorer_version": "string",            // e.g., "2.0.0"
  "rules_version": "string",             // e.g., "2026-02-20"
  "evaluated_at": "string (ISO 8601)",  // Timestamp
  "decision_status": "proceed" | "defer" | "no-go",  // Gated recommendation
  "criteria_confirmed": boolean,
  "ranked_alternatives": [
    {
      "id": "string",
      "name": "string",
      "rank": integer,
      "type": "internal|compose|external|build-new",  // HDA
      "effort": "S|M|L",
      "risk": "Low|Med|High",
      "effort_rank": integer,
      "risk_rank": integer,
      "feasible": boolean,
      "justification": "string",
      "major_platform_average": 0-100,
      "current_platform_score": 0-100,
      "overall_success_score": 0-100,
      "coverage": 0-1,
      "missing_values": integer,
      "platform_scores": {"platform": 0-100},
      "notes": "string"
    }
  ],
  "recommendation": {
    "action": "select" | "compose" | "improve" | "extend" | "build-new" | "no-go",
    "chosen_option_ids": ["string"],
    "top_option_id": "string",
    "score_margin_vs_second": number,
    "reason": "string",
    "rules": {
      "select_min": number,
      "select_margin": number,
      "compose_min": number,
      "compose_margin": number,
      "improve_min": number,
      "extend_gap": number,
      "min_coverage": number
    }
  }
}
```

---

## Scoring Logic (All Modes, Identical)

### 1. Normalize weights

```text
weight_i = weight_i / Σ(all weights)
```

### 2. Compute platform scores

```text
For each alternative & platform:
  weighted_sum = 0
  count = 0
  for each criterion:
    if score is not null:
      weighted_sum += weight_i × score_i
      count += 1
  platform_score = weighted_sum / count  [excluding null values]
```

### 3. Compute major platform average

```text
major_platform_average = mean(platform_score for each platform in major_platforms)
```

### 4. Compute overall success score

```text
overall_success_score = 0.6 × major_platform_average + 0.4 × current_platform_score
[Note: 0.6/0.4 configurable via weights parameter]
```

### 5. Rank alternatives

Deterministic order:

1. `overall_success_score` (descending)
2. `current_platform_score` (descending)
3. `major_platform_average` (descending)
4. (Medium/Rigorous only) `effort` (S < M < L)
5. (Medium/Rigorous only) `risk` (Low < Med < High)
6. `name` (ascending)

### 6. Select action (deterministic rules)

```python
if overall_success_score < improve_min (55):
    action = "build-new"
elif overall_success_score < select_min (80):
    action = "improve"
elif current_platform_score < (major_platform_average - extend_gap (10)):
    action = "extend"
elif (top_score - second_score) < select_margin (7):
    action = "compose"
else:
    action = "select"
```

---

## Quick Command Reference

### Lite Mode

```bash
python3 skills/decision-analysis/scripts/score_decision.py \
  --input input.json \
  --output report.md \
  --json-output result.json \
  --mode lite
```

### Medium Mode

```bash
python3 skills/decision-analysis/scripts/score_decision.py \
  --input input.json \
  --output report.md \
  --json-output result.json \
  --mode medium
```

### Rigorous Mode (with schema validation)

```bash
python3 skills/decision-analysis/scripts/score_decision.py \
  --input input.json \
  --output report.md \
  --json-output result.json \
  --mode rigorous

node skills/decision-analysis/scripts/validate_contract.mjs \
  --schema skills/decision-analysis/references/input.schema.json \
  --data input.json

node skills/decision-analysis/scripts/validate_contract.mjs \
  --schema skills/decision-analysis/references/output.schema.json \
  --data result.json
```

---

## Migration Checklist

### Phase 1: Schema Creation (Week 1)

- [ ] Create unified `input.schema.json` (conditional on mode)
- [ ] Create unified `output.schema.json` (conditional on mode)
- [ ] Validate schemas against all 4 existing inputs/outputs
- [ ] Test mode detection heuristics

### Phase 2: Unified Scorer (Weeks 2-3)

- [ ] Implement `score_decision.py` skeleton
- [ ] Port CA scoring logic (lite mode)
- [ ] Port CDR scoring logic (medium mode)
- [ ] Port CDA scoring logic (rigorous mode, evaluators)
- [ ] Port HDA scoring logic (rigorous mode, discovery)
- [ ] Unified ranking & recommendation
- [ ] Mode-conditional output fields

### Phase 3: Tests (Week 4)

- [ ] Migrate CA tests
- [ ] Migrate CDR tests
- [ ] Migrate CDA tests
- [ ] Migrate HDA tests
- [ ] Create cross-mode tests (same input, different modes)
- [ ] Schema validation tests

### Phase 4: Documentation (Week 5)

- [ ] Consolidate SKILL.md (single skill, 3 mode branches)
- [ ] Merge reference documents
- [ ] Create migration guide for users

### Phase 5: Deprecation (Week 6+)

- [ ] Tag old variants `v1.0-deprecated`
- [ ] Add deprecation notices to old SKILL.md files
- [ ] Create archive directory
- [ ] Update skills-manifest.md
- [ ] Update cross-project references

---

## Common Pitfalls & Solutions

| Issue                         | Lite          | Medium                                | Rigorous                                                    |
| ----------------------------- | ------------- | ------------------------------------- | ----------------------------------------------------------- |
| Missing scores treated as...  | 0             | 0                                     | Excluded from average                                       |
| Score scale support           | 0-100 only    | 1-5 or 0-100                          | 1-5 or 0-100                                                |
| Criteria confirmation         | Not enforced  | Optional field                        | REQUIRED                                                    |
| Can score with 1 alternative? | Yes (warning) | Yes (warning)                         | Requires min 2                                              |
| Independent evaluators        | Not supported | Not supported                         | CDA requires 1 per alt                                      |
| JSON Schema validation        | None          | None                                  | HDA requires input+output                                   |
| Feasibility gating            | Not tracked   | Feasible field but not strictly gated | Enforced: cannot recommend infeasible unless all infeasible |

---

## File Structure: Before & After

### Current (Fragmented)

```bash tree
pax/skills/workflow/
├── comparative-analysis/
│   ├── SKILL.md
│   ├── scripts/score_alternatives.py (376 L)
│   ├── references/input-schema.md
│   └── assets/comparative-analysis-record-template.md
├── comparative-decision-review/
│   ├── SKILL.md
│   ├── scripts/score_options.py (430 L)
│   ├── references/input-schema.md, rubric-packs.md
│   └── assets/comparative-decision-record-template.md
├── comparative-decision-analysis/
│   ├── SKILL.md
│   ├── scripts/run_comparative_decision_harness.py (164 L)
│   ├── scripts/score_with_guardrails.py (655 L)
│   ├── references/{discovery, quality-gates, rubric-packs, scenario-bakeoff, input-schema.json}.md
│   └── assets/comparative-decision-record-template.md
├── hybrid-decision-analysis/
│   ├── SKILL.md
│   ├── scripts/{score_with_guardrails.py (655 L), validate_json_contract.mjs, test_...py}
│   ├── references/{discovery, quality-gates, rubric-packs, input.schema.json, output.schema.json}.md
│   └── assets/hybrid-decision-record-template.md
└── hybrid-decision-analysis.v1/ [archived]
```

**Lines of code**: 376 + 430 + 655 + 655 = 2,116 L (4 redundant scorers)

### Proposed (Unified)

```bash tree
pax/skills/workflow/
├── decision-analysis/ [NEW]
│   ├── SKILL.md [consolidated from all 5]
│   ├── scripts/
│   │   ├── score_decision.py (800 L) [unified, all 3 modes]
│   │   ├── test_score_decision.py (parametrized by mode)
│   │   └── validate_contract.mjs [shared validator]
│   ├── references/
│   │   ├── input.schema.json [unified, mode-conditional]
│   │   ├── output.schema.json [unified, mode-conditional]
│   │   ├── input-schema.md
│   │   ├── output-schema.md
│   │   ├── rubric-packs.md [merged from all]
│   │   ├── discovery-protocol.md [merged]
│   │   ├── quality-gates.md [merged]
│   │   └── scenario-bakeoff-protocol.md [optional]
│   └── assets/decision-record-template.md
└── archive/ [deprecated]
    ├── comparative-analysis.v1-deprecated/
    ├── comparative-decision-review.v1-deprecated/
    ├── comparative-decision-analysis.v1-deprecated/
    ├── hybrid-decision-analysis.v1-deprecated/
    └── hybrid-decision-analysis.v1-archive/
```

**Lines of code**: 800 L unified (63% reduction)

---

## Success Metrics

- ✓ Single `score_decision.py` script (no duplicates)
- ✓ All 4 variant tests pass unchanged (regression)
- ✓ Users select mode via `--mode` flag (clear interface)
- ✓ One SKILL.md with mode branching (single source of truth)
- ✓ JSON Schema validation pass/fail (HDA maintains rigor)
- ✓ Deterministic rankings consistent across modes (audit trail)
- ✓ 63% code reduction (2,116 → 800 lines)
- ✓ Faster iteration on shared scoring logic (1 script, not 4)
- ✓ Unified test suite (parametrized, not duplicated)

---

## References

For complete details, see:

- [consolidated-schema.md](consolidated-schema.md) – Full schema mapping, input/output comparison, consolidation roadmap
- [script-dependencies.md](script-dependencies.md) – Python script inventory, feature inheritance, test coverage plan, implementation skeleton
