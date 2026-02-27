# Comparative Decision Analysis: Consolidated Schema & Consolidation Roadmap

**Date**: 2026-02-25  
**Status**: Complete analysis of 5 variants for consolidation planning

---

## Executive Summary

Five decision-analysis skills exist across pax/skills/workflow/:

1. **comparative-analysis** (CA) - Lite: Simple 0-100 scoring, minimal metadata
2. **comparative-decision-review** (CDR) - Medium: Supports 1-5/0-100 scales, effort/risk tie-breaks
3. **comparative-decision-analysis** (CDA) - Rigorous: Mandatory discovery, isolated evaluators, independent evaluations
4. **hybrid-decision-analysis** (HDA) - Comprehensive: Full discovery, JSON Schema validation, decision status gates
5. **hybrid-decision-analysis.v1** (HDA.v1) - Archive: References comparative-analysis scorer (unmaintained)

**Consolidation Goal**: Merge into 3 modes (Lite, Medium, Rigorous) sharing a single unified input/output schema.

---

## Part 1: Common Input Structure (Cross-Variant Base)

All variants accept these **required** fields:

| Field              | Type   | Notes                                                |
| ------------------ | ------ | ---------------------------------------------------- |
| `decision`         | string | Short decision statement (one sentence)              |
| `current_platform` | string | Platform to optimize for (e.g., "chatgpt", "claude") |
| `criteria`         | array  | List of weighted criteria (min 1 item)               |
| `alternatives`     | array  | Candidate options (min 2 items for scoring)          |

### Optional Fields (Variant-Specific)

| Field                          | CA  | CDR | CDA | HDA | Purpose                                                                                   |
| ------------------------------ | --- | --- | --- | --- | ----------------------------------------------------------------------------------------- |
| `score_scale`                  | -   | ✓   | ✓   | ✓   | "0-100" \| "1-5" (default "0-100")                                                        |
| `criteria_confirmed`           | -   | ✓   | ✓   | ✓   | Must be `true` before scoring (gating)                                                    |
| `criteria_confirmation_source` | -   | -   | ✓   | -   | "user-confirmed" \| "provided-input" \| "yolo-mode"                                       |
| `major_platforms`              | ✓   | ✓   | ✓   | ✓   | List of platforms for comparative scoring (default: ChatGPT, Claude, Gemini, Copilot)     |
| `discovery`                    | -   | -   | -   | ✓   | Object: `{external_discovery_done, external_discovery_blocked, block_reason, checked_at}` |
| `independent_evaluations`      | -   | -   | ✓   | -   | Array of evaluator records (one per alternative, required by CDA)                         |
| `weights`                      | ✓   | ✓   | ✓   | ✓   | Custom blend weights: `{major_platform_average, current_platform}` (default 0.6/0.4)      |
| `recommendation_rules`         | ✓   | ✓   | ✓   | ✓   | Custom score thresholds (see below)                                                       |
| `run_id`                       | -   | -   | -   | ✓   | Stable identifier for reproducible runs                                                   |

---

## Part 2: Criterion Contract Evolution

### Minimal (comparative-analysis)

```json
{
  "id": "string",
  "name": "string",
  "weight": number
}
```

**Score source**: Inline in alternative.scores

### Standard (comparative-decision-review, comparative-decision-analysis)

```json
{
  "id": "string",
  "name": "string",
  "weight": number,
  "metric": "string",       // How to measure
  "data_source": "string",  // Evidence source
  "scoring_rule": "string"  // Guidance (e.g., "1-5 rubric" or "0-100")
}
```

### Enhanced (hybrid-decision-analysis)

Same as Standard, plus JSON Schema validation enforces all fields required.

---

## Part 3: Alternative Contract Evolution

### Minimal (comparative-analysis)

```json
{
  "id": "string",
  "name": "string",
  "scores": {
    "platform": {
      "criterion-id": 0-100 or null
    }
  }
}
```

### Standard (comparative-decision-review, hybrid-decision-analysis)

```json
{
  "id": "string",
  "name": "string",
  "effort": "S|M|L",         // Size estimate
  "risk": "Low|Med|High",    // Risk level
  "feasible": boolean,       // Can recommend?
  "justification": "string", // Why this option?
  "scores": {
    "platform": {
      "criterion-id": 0-100|1-5 or null
    }
  }
}
```

### Rigorous (comparative-decision-analysis, hybrid-decision-analysis)

Standard fields plus:

```json
{
  "type": "internal|compose|external|build-new", // Origin (HDA only)
  "notes": "string", // Additional details
  "evidence": [
    // HDA: external evidence array
    {
      "source_url": "string",
      "source_date": "string (ISO 8601)",
      "evidence_strength": "low|medium|high",
      "notes": "string"
    }
  ]
}
```

### Independent Evaluation Record (CDA only)

```json
{
  "alternative_id": "string", // Must match alternative.id
  "evaluator_id": "string", // Unique per alternative
  "isolation_confirmed": true, // Required constant
  "summary": "string", // Isolated finding
  "evidence_refs": ["string"] // Optional pointers
}
```

---

## Part 4: Common Output Structure

All variants produce (variants listed by completeness):

### Required Output Fields (All Variants)

```json
{
  "decision": "string",                    // Original decision statement
  "ranked_alternatives": [                 // All identified options, ranked
    {
      "id": "string",
      "name": "string",
      "rank": integer (1+),
      "feasible": boolean,
      "major_platform_average": 0-100,
      "current_platform_score": 0-100,
      "overall_success_score": 0-100,
      "justification": "string"
    }
  ],
  "recommendation": {
    "action": "select|compose|improve|extend|build-new|no-go",
    "chosen_option_ids": ["string"],
    "top_option_id": "string",
    "score_margin_vs_second": number,
    "reason": "string"
  }
}
```

### Optional Output Fields (Variant-Specific)

| Field                       | CA  | CDR | CDA | HDA | Purpose                                  |
| --------------------------- | --- | --- | --- | --- | ---------------------------------------- |
| `run_id`                    | -   | -   | -   | ✓   | Reproducibility identifier               |
| `scorer_version`            | -   | -   | -   | ✓   | Script version                           |
| `rules_version`             | -   | -   | -   | ✓   | Scoring rules snapshot                   |
| `evaluated_at`              | -   | -   | -   | ✓   | ISO 8601 timestamp                       |
| `decision_status`           | -   | -   | -   | ✓   | "proceed" \| "defer" \| "no-go" (gating) |
| `coverage`                  | -   | ✓   | ✓   | ✓   | Missing evidence ratio per option        |
| `effort_rank` / `risk_rank` | -   | ✓   | ✓   | ✓   | Tie-break ordering                       |
| `platform_scores`           | -   | -   | -   | ✓   | Per-platform scores included in output   |

---

## Part 5: Scoring Methodology Comparison

### Deterministic Ranking (All Variants)

**Primary sort (descending)**:

1. `overall_success_score = 0.6 × major_platform_average + 0.4 × current_platform_score`

**Tie-breaks** (in order):

| Variant | Tie-Break 2               | Tie-Break 3               | Tie-Break 4      | Tie-Break 5           |
| ------- | ------------------------- | ------------------------- | ---------------- | --------------------- |
| CA      | `current_platform_score↓` | `major_platform_average↓` | `name↑`          | -                     |
| CDR     | `current_platform_score↓` | `major_platform_average↓` | `effort (S<M<L)` | `risk (Low<Med<High)` |
| CDA     | `current_platform_score↓` | `major_platform_average↓` | `effort`         | `risk`                |
| HDA     | `current_platform_score↓` | `major_platform_average↓` | `effort`         | `risk`                |

### Score Computation

**Criterion Weighting**:

- All variants normalize weights: `weight_i / Σweights`

**Platform Scores**:

- Weighted average per platform: `Σ(weight_i × score_i) / Σweights`
- Missing scores: Treated as `null`, excluded from average (not zero)

**Major Platform Average**:

- Mean across all major platforms (default: ChatGPT, Claude, Gemini, Copilot)

**Current Platform Score**:

- Weighted score for the single current platform

**Overall Success Score**:

- `0.6 × major_platform_average + 0.4 × current_platform_score` (configurable)

### Score Scale Support

| Variant | 0-100 | 1-5 | Conversion                |
| ------- | ----- | --- | ------------------------- |
| CA      | ✓     | -   | N/A                       |
| CDR     | ✓     | ✓   | `1-5 × 20 = 0-100`        |
| CDA     | ✓     | ✓   | Auto-detected from schema |
| HDA     | ✓     | ✓   | Specified in input        |

### Recommendation Rules

Default thresholds (configurable via `recommendation_rules`):

```python
{
  "select_min": 80.0,           # Top score must be ≥ 80
  "select_margin": 7.0,         # Top must lead 2nd by ≥ 7 points
  "compose_min": 70.0,          # Top 2 must be ≥ 70
  "compose_margin": 7.0,        # Top 2 within 7 points
  "improve_min": 55.0,          # Viable option ≥ 55
  "extend_gap": 10.0,           # Current platform gap threshold
  "min_coverage": 0.8           # Evidence coverage requirement (HDA only)
}
```

**Action Selection** (deterministic):

```python
if overall_success_score < improve_min:
    action = "build-new"
elif overall_success_score < select_min:
    action = "improve"
elif current_platform_score < (major_platform_average - extend_gap):
    action = "extend"
elif top_score - second_score <= select_margin:
    action = "compose"  # if both feasible & strong
else:
    action = "select"
```

**Coverage Gating** (HDA only):

- If `coverage < min_coverage` and action is `select` or `compose`: defer or add warning
- HDA outputs `decision_status: "proceed" | "defer" | "no-go"`

---

## Part 6: Script Dependencies & Compatibility Matrix

### Python Scoring Scripts

| Script                                | Variant | Lines | Key Features                                                                      |
| ------------------------------------- | ------- | ----- | --------------------------------------------------------------------------------- |
| `score_alternatives.py`               | CA      | 376   | Basic 0-100 scoring, no scale support, no effort/risk                             |
| `score_options.py`                    | CDR     | 430   | 1-5/0-100 scale support, effort/risk tie-breaks                                   |
| `run_comparative_decision_harness.py` | CDA     | 164   | Wrapper: calls `score_with_guardrails.py`, records manifest, hashes inputs        |
| `score_with_guardrails.py`            | CDA     | 655   | Full guardrails: discovery, isolated evaluators, coverage gating, decision status |
| `score_with_guardrails.py`            | HDA     | 655+  | Same as CDA + JSON Schema validation (dual role)                                  |

### Harness Scripts

| Script                          | Variant  | Type    | Purpose                                 |
| ------------------------------- | -------- | ------- | --------------------------------------- |
| `validate_json_contract.mjs`    | HDA      | Node.js | JSON Schema validation for input/output |
| `test_score_with_guardrails.py` | CDA, HDA | Python  | Regression tests for scorer logic       |

### Test Files

| File                                                                               | Variant | Coverage                                              |
| ---------------------------------------------------------------------------------- | ------- | ----------------------------------------------------- |
| `test/skills/workflow/comparative-decision-analysis/test_score_with_guardrails.py` | CDA     | Tie-break ordering, missing evidence, coverage gating |
| `skills/hybrid-decision-analysis/scripts/test_score_with_guardrails.py`            | HDA     | Same as CDA tests                                     |

### Reference Documents Shared

| Document                       | CA  | CDR | CDA | HDA | Content                                          |
| ------------------------------ | --- | --- | --- | --- | ------------------------------------------------ |
| `rubric-packs.md`              | -   | ✓   | ✓   | ✓   | 4 pre-built criterion sets (Pack A-D)            |
| `discovery-protocol.md`        | -   | -   | ✓   | ✓   | 3 discovery lanes (internal, adjacent, external) |
| `quality-gates.md`             | -   | -   | ✓   | ✓   | Pre-scoring, scoring, output, regression gates   |
| `scenario-bakeoff-protocol.md` | -   | -   | ✓   | ✓   | Reliability checks & sensitivity testing         |
| `input-schema.md`              | ✓   | ✓   | ✓   | ✓   | Human-readable input spec                        |
| `input-schema.json`            | -   | -   | ✓   | ✓   | Machine-readable JSON Schema (2020-12)           |
| `output-schema.md`             | -   | -   | -   | ✓   | Human-readable output spec                       |
| `output.schema.json`           | -   | -   | -   | ✓   | Machine-readable JSON Schema                     |

---

## Part 7: Feature Matrix (Complexity Tiers)

### Tier 1: Lite (comparative-analysis)

**Simplest entry point for straightforward comparisons.**

- ✓ 0-100 scoring only
- ✓ Basic criteria (id, name, weight)
- ✓ Simple alternatives with scores
- ✗ No scale conversion
- ✗ No effort/risk tiebreaks
- ✗ No discovery protocol
- ✗ No independent evaluators
- ✗ No JSON Schema validation
- ✗ No decision status gating
- ✗ No coverage tracking

**Use case**: Quick skill/tool selection with pre-identified options, no external discovery needed.

**Example input**:

```json
{
  "decision": "Choose skill framework",
  "current_platform": "claude",
  "criteria": [
    { "id": "fit", "name": "Fit", "weight": 2 },
    { "id": "speed", "name": "Speed", "weight": 1 }
  ],
  "alternatives": [
    {
      "id": "alt-1",
      "name": "Option A",
      "scores": { "claude": { "fit": 85, "speed": 90 } }
    }
  ]
}
```

**Output minimal fields**: `ranked_alternatives[].{id, name, rank, major_platform_average, current_platform_score, overall_success_score}`

### Tier 2: Medium (comparative-decision-review, variants)

**Balance between rigor and simplicity. Supports both 1-5 and 0-100 scales.**

- ✓ 1-5 and 0-100 score scales
- ✓ Enhanced criteria (metric, data_source, scoring_rule)
- ✓ Effort (S|M|L) and risk (Low|Med|High) tiebreaks
- ✓ Feasibility gating
- ✓ Justification per alternative
- ✓ Coverage computation
- ✗ No independent evaluators
- ✗ No discovery protocol
- ✗ No JSON Schema validation
- ✗ No decision status gating

**Use case**: Defined options with known effort/risk, qualitative or semi-quantitative scoring.

**Example input**:

```json
{
  "decision": "Select observability approach",
  "criteria_confirmed": true,
  "current_platform": "claude",
  "criteria": [
    {
      "id": "coverage",
      "name": "Use-Case Coverage",
      "weight": 25,
      "metric": "Coverage of required capabilities",
      "data_source": "Design docs + test runs",
      "scoring_rule": "1-5 rubric"
    }
  ],
  "alternatives": [
    {
      "id": "reuse",
      "name": "Reuse existing",
      "effort": "S",
      "risk": "Low",
      "feasible": true,
      "justification": "...",
      "scores": { "claude": { "coverage": 4 } }
    }
  ]
}
```

**Output adds**: `effort_rank`, `risk_rank`, `coverage`, `notes`

### Tier 3: Rigorous (comparative-decision-analysis, hybrid-decision-analysis)

**Full audit trail with discovery, independent evaluations, schema validation, and decision gating.**

**comparative-decision-analysis**:

- ✓ Mandatory criteria confirmation
- ✓ Independent evaluators (per CDA spec)
- ✓ Criteria confirmation source tracking
- ✓ Quality gates (pre-scoring, scoring, output)
- ✗ No JSON Schema validation
- ✗ No decision status gating
- ✗ No alternative type classification

**hybrid-decision-analysis**:

- ✓ All CDA features plus:
- ✓ Discovery tracking (external_discovery_done, blocked reason)
- ✓ Alternative type classification (internal|compose|external|build-new)
- ✓ External evidence arrays (source_url, source_date, evidence_strength)
- ✓ JSON Schema validation (input.schema.json, output.schema.json)
- ✓ Decision status gating (proceed|defer|no-go)
- ✓ Harness wrapper (run_comparative_decision_harness.py)
- ✓ Run ID & scorer version tracking
- ✓ Timestamp audit trail

**Use case**: High-stakes decisions (architecture, vendor, build-vs-buy) requiring audit-trail, discovery proof, and isolated expert evaluation.

**Example input** (HDA):

```json
{
  "decision": "Select vendor for observability",
  "criteria_confirmed": true,
  "current_platform": "claude",
  "run_id": "vendor-eval-2026-02",
  "discovery": {
    "external_discovery_done": true,
    "external_discovery_blocked": false,
    "checked_at": "2026-02-25T14:30:00Z"
  },
  "criteria": [
    {
      "id": "capability-fit",
      "name": "Capability Fit",
      "weight": 25,
      "metric": "Coverage of logging, metrics, traces",
      "data_source": "Feature comparison + docs",
      "scoring_rule": "0-100: 80+ covers all, 60+ covers 2/3"
    }
  ],
  "alternatives": [
    {
      "id": "vendor-a",
      "name": "Vendor A",
      "type": "external",
      "effort": "M",
      "risk": "Med",
      "feasible": true,
      "justification": "...",
      "evidence": [
        {
          "source_url": "https://vendor-a.com/docs",
          "source_date": "2026-02-20",
          "evidence_strength": "high",
          "notes": "Official feature docs"
        }
      ],
      "scores": { "claude": { "capability-fit": 85 } }
    }
  ]
}
```

**Output adds**: `run_id`, `scorer_version`, `rules_version`, `evaluated_at`, `decision_status`, `platform_scores`, full alternative metadata

---

## Part 8: What Each Variant Does Well (vs. Trade-offs)

### comparative-analysis (Lite)

| Strength                        | Trade-off                               |
| ------------------------------- | --------------------------------------- |
| Fastest to implement            | No scale flexibility (0-100 only)       |
| Minimal input scaffolding       | No effort/risk logic (scores only)      |
| Simple criteria structure       | No audit trail for discovery/evaluators |
| Quick scoring for known options | Cannot handle qualitative (1-5) inputs  |

### comparative-decision-review (Medium)

| Strength                          | Trade-off                          |
| --------------------------------- | ---------------------------------- |
| Flexible scoring (1-5 or 0-100)   | Still no discovery mandate         |
| Effort/risk inform ranking        | No independent evaluator isolation |
| Justification required per option | No JSON Schema validation          |
| Coverage track (missing evidence) | No decision status output          |

### comparative-decision-analysis (Rigorous, Evaluator-Focused)

| Strength                              | Trade-off                          |
| ------------------------------------- | ---------------------------------- |
| Mandatory evaluator isolation         | No alternative type classification |
| Independent per-alternative evidence  | No discovery tracking requirements |
| Criteria confirmation source tracking | No external evidence arrays        |
| Quality gates enforced at scoring     | No JSON Schema validation          |

### hybrid-decision-analysis (Rigorous, Discovery-Focused)

| Strength                                     | Trade-off                            |
| -------------------------------------------- | ------------------------------------ |
| Mandatory external discovery                 | More verbose input structure         |
| Alternative type classification              | Schema validation requires more prep |
| Decision status gating (proceed/defer/no-go) | More setup overhead                  |
| JSON Schema & test harness                   | Slower iteration for simple cases    |
| Run ID & scorer audit trail                  |                                      |

### hybrid-decision-analysis.v1 (Archive)

| Strength                      | Trade-off                                           |
| ----------------------------- | --------------------------------------------------- |
| Documented bakeoff evaluation | References unmaintained comparative-analysis scorer |
| Rubric packs + assessment     | No updates planned                                  |

---

## Part 9: Consolidation Roadmap (5 → 3 Variants)

### Proposed Merged Variants

```text
LITE
  ← comparative-analysis
  Implementation: score_alternatives.py (v1.0)

MEDIUM
  ← comparative-decision-review
  Implementation: score_options.py (v1.1, enhanced)

RIGOROUS
  ← comparative-decision-analysis + hybrid-decision-analysis
  Implementation: score_with_guardrails.py (v2.0, unified)
  Output: Unified output.schema.json
  Harness: run_comparative_decision_harness.py (deprecated, features rolled into scorer)
  Validation: validate_json_contract.mjs (built-in)
```

### Implementation Steps

#### Phase 1: Unified Input Schema (Week 1)

**Create** `/pax/skills/workflow/shared/unified-input.schema.json`:

```json
{
  "title": "Unified Decision Analysis Input",
  "type": "object",
  "required": ["decision", "current_platform", "criteria", "alternatives"],
  "properties": {
    "decision": "string",
    "current_platform": "string",
    "mode": {
      "type": "string",
      "enum": ["lite", "medium", "rigorous"],
      "description": "Execution mode determines validation rules"
    },
    "criteria_confirmed": "boolean",
    "criteria_confirmation_source": {
      "enum": ["user-confirmed", "provided-input", "yolo-mode"]
    },
    "criteria": {
      "oneOf": [
        { "$ref": "#/$defs/criterion-lite" },
        { "$ref": "#/$defs/criterion-full" }
      ]
    },
    "alternatives": {
      "oneOf": [
        { "items": { "$ref": "#/$defs/alternative-lite" } },
        { "items": { "$ref": "#/$defs/alternative-full" } }
      ]
    },
    "discovery": {
      "type": "object",
      "required": ["external_discovery_done", "external_discovery_blocked"],
      "description": "Required if mode=rigorous"
    },
    "independent_evaluations": {
      "type": "array",
      "description": "Required if mode=rigorous and not CDA-style"
    }
  },
  "$defs": {
    "criterion-lite": {
      "type": "object",
      "required": ["id", "name", "weight"]
    },
    "criterion-full": {
      "type": "object",
      "required": [
        "id",
        "name",
        "weight",
        "metric",
        "data_source",
        "scoring_rule"
      ]
    },
    "alternative-lite": {
      "type": "object",
      "required": ["id", "name", "scores"]
    },
    "alternative-full": {
      "type": "object",
      "required": [
        "id",
        "name",
        "effort",
        "risk",
        "feasible",
        "justification",
        "scores"
      ]
    }
  }
}
```

**Rationale**: Single conditional schema accepts all variants, validator narrows based on `mode`.

#### Phase 2: Unified Output Schema (Week 2)

**Create** `/pax/skills/workflow/shared/unified-output.schema.json`:

```json
{
  "title": "Unified Decision Analysis Output",
  "required": ["decision", "mode", "ranked_alternatives", "recommendation"],
  "properties": {
    "mode": { "enum": ["lite", "medium", "rigorous"] },
    "run_id": {
      "type": "string",
      "description": "Only present if mode=rigorous"
    },
    "scorer_version": {
      "type": "string",
      "description": "Only present if mode=rigorous"
    },
    "decision_status": {
      "enum": ["proceed", "defer", "no-go"],
      "description": "Only present if mode=rigorous"
    },
    "ranked_alternatives": {
      "items": {
        "required": ["id", "name", "rank"],
        "properties": {
          "effort_rank": {
            "type": "integer",
            "description": "Only if mode=medium|rigorous"
          },
          "risk_rank": {
            "type": "integer",
            "description": "Only if mode=medium|rigorous"
          },
          "coverage": {
            "type": "number",
            "description": "Only if mode=medium|rigorous"
          }
        }
      }
    }
  }
}
```

#### Phase 3: Unified Scorer Implementation (Weeks 3-4)

**Enhance** `score_with_guardrails.py` → `score_decision.py`:

```python
#!/usr/bin/env python3
"""Unified deterministic scorer for all 3 modes."""

def main():
    args = parse_args()
    data = load_json(args.input)

    mode = data.get("mode", "medium")  # Default to medium

    # Validate based on mode
    if mode == "lite":
        validate_lite_input(data)
        apply_lite_rules(data)
    elif mode == "medium":
        validate_medium_input(data)
        apply_medium_rules(data)
    elif mode == "rigorous":
        validate_rigorous_input(data)
        apply_rigorous_rules(data)

    # Unified scoring (all modes share this)
    scores = compute_platform_scores(data)
    ranking = rank_alternatives(scores, mode)
    recommendation = select_action(ranking, mode)

    # Build output based on mode
    output = {
        "decision": data["decision"],
        "mode": mode,
        "ranked_alternatives": ranking,
        "recommendation": recommendation
    }

    if mode == "rigorous":
        output.update({
            "run_id": args.run_id or generate_run_id(),
            "scorer_version": "2.0.0",
            "decision_status": assess_decision_status(ranking, data),
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        })

    write_json(args.json_output, output)
```

**Key changes**:

- Single entry point with conditional validation
- Shared scoring logic (all modes use same ranking algorithm)
- Mode-conditional output fields
- Drop harness script; fold logic into scorer

#### Phase 4: Merge Skill Definitions (Week 5)

**Consolidate SKILL.md** → `/pax/skills/workflow/decision-analysis/SKILL.md`:

````markdown
# Decision Analysis (Unified)

Produce defensible decisions with configurable rigor.

## Modes

- **lite**: Quick selection with identified options (comparative-analysis)
- **medium**: Balanced rigor with effort/risk assessment (comparative-decision-review)
- **rigorous**: Audit-trail decisions with discovery & isolation (comparative-decision-analysis + hybrid-decision-analysis)

## Usage

```bash
python3 skills/decision-analysis/scripts/score_decision.py \
  --input <input.json> \
  --output <analysis-report.md> \
  --json-output <analysis-result.json> \
  --mode [lite|medium|rigorous]
```

# [Detailed mode instructions...]
````

#### Phase 5: Reference Consolidation (Week 6)

**Consolidate references** → `/pax/skills/workflow/decision-analysis/references/`:

```bash tree

├── input.schema.json # Unified (conditional on mode)
├── input-schema.md # Unified guide
├── output.schema.json # Unified
├── output-schema.md # Unified
├── rubric-packs.md # Shared (all modes)
├── discovery-protocol.md # Rigorous mode only
├── quality-gates.md # Shared (validated per mode)
└── scenario-bakeoff-protocol.md # Optional

```

#### Phase 6: Testing & Migration (Weeks 7-8)

**Update tests**:

```bash
python3 skills/decision-analysis/scripts/test_score_decision.py --mode lite
python3 skills/decision-analysis/scripts/test_score_decision.py --mode medium
python3 skills/decision-analysis/scripts/test_score_decision.py --mode rigorous
node skills/decision-analysis/scripts/validate_json_contract.mjs \
  --schema skills/decision-analysis/references/input.schema.json \
  --data input.json \
  --mode rigorous
```

**Deprecation plan**:

- Mark old variants as deprecated (v1.0.0-deprecated)
- Redirect imports
- Archive (5 → archive/) after 2 release cycles
- Update all cross-references

---

## Part 10: Script Dependency Mapping

### Current State (Fragmented)

```bash tree
comparative-analysis/
  └─ scripts/score_alternatives.py (376 lines)

comparative-decision-review/
  └─ scripts/score_options.py (430 lines)

comparative-decision-analysis/
  ├─ scripts/run_comparative_decision_harness.py (164 lines) [wraps score_with_guardrails]
  └─ scripts/score_with_guardrails.py (655 lines)

hybrid-decision-analysis/
  ├─ scripts/score_with_guardrails.py (655 lines) [duplicate of CDA]
  ├─ scripts/test_score_with_guardrails.py
  └─ scripts/validate_json_contract.mjs

hybrid-decision-analysis.v1/
  └─ [archived, references CA]
```

### Proposed Unified State

```bash tree
decision-analysis/
  ├─ scripts/
  │   ├─ score_decision.py (800 lines) [unified scorer, all 3 modes]
  │   ├─ test_score_decision.py
  │   └─ validate_contract.mjs [shared validator]
  ├─ references/
  │   ├─ input.schema.json [unified, mode-conditional]
  │   ├─ output.schema.json [unified, mode-conditional]
  │   ├─ input-schema.md
  │   ├─ output-schema.md
  │   ├─ rubric-packs.md
  │   ├─ discovery-protocol.md
  │   └─ quality-gates.md
  ├─ assets/
  │   └─ [record templates]
  └─ SKILL.md
```

**Reductions**:

- 4 Python scorers → 1 (650 lines saved)
- Duplicate `score_with_guardrails.py` → 1 copy
- Harness wrapper → folded into scorer
- 2 test suites → 1 parametrized suite

---

## Part 11: Migration Checklist

### Pre-Migration (Validate Current State)

- [ ] Run all existing tests

  ```bash
  python3 skills/workflow/comparative-analysis/scripts/score_alternatives.py --help
  python3 skills/workflow/comparative-decision-review/scripts/score_options.py --help
  python3 skills/workflow/comparative-decision-analysis/scripts/run_comparative_decision_harness.py --help
  ```

- [ ] Verify schema compatibility

  ```bash
  jsonschema validate \
    --schema skills/workflow/comparative-decision-analysis/references/input-schema.json \
    test/fixtures/analysis-input-cda.json
  jsonschema validate \
    --schema skills/workflow/hybrid-decision-analysis/references/input.schema.json \
    test/fixtures/analysis-input-hda.json
  ```

- [ ] Document example inputs for each variant
- [ ] Document example outputs for each variant

### Implementation (Phase by Phase)

- [ ] **Phase 1**: Create unified input schema
  - [ ] Test schema against all 4 existing inputs
  - [ ] Validate mode detection logic

- [ ] **Phase 2**: Create unified output schema
  - [ ] Test schema against all 4 existing outputs
  - [ ] Verify conditional fields per mode

- [ ] **Phase 3**: Build unified scorer
  - [ ] Port CA scorer logic (lite mode)
  - [ ] Port CDR scorer logic (medium mode)
  - [ ] Port CDA scorer logic (rigorous mode, no evaluators)
  - [ ] Port HDA scorer logic (rigorous mode, evaluators)
  - [ ] Unified ranking & recommendation
  - [ ] Mode-conditional validation

- [ ] **Phase 4**: Consolidate SKILL.md
  - [ ] Single skill with mode branching
  - [ ] Separate workflows per mode

- [ ] **Phase 5**: Consolidate references
  - [ ] Merge rubric packs
  - [ ] Merge discovery, quality gates
  - [ ] Create mode-specific appendices

- [ ] **Phase 6**: Test coverage
  - [ ] Test all 3 modes independently
  - [ ] Test cross-mode edge cases
  - [ ] JSON Schema validation for each mode
  - [ ] Regression tests from all 4 variants

- [ ] **Phase 7**: Deprecation
  - [ ] Tag old variants v1.0-deprecated
  - [ ] Add deprecation notice to SKILL.md
  - [ ] Update cross-project references
  - [ ] Plan archive (2 release cycles)

### Post-Migration (Validation)

- [ ] All existing tests pass on unified scorer
- [ ] All example scenarios work in all modes
- [ ] Documentation updated
- [ ] Skills manifest updated
- [ ] Cross-project skill references updated

---

## Part 12: Key Metrics for Success

| Metric               | Current                              | Target                   | Reason                         |
| -------------------- | ------------------------------------ | ------------------------ | ------------------------------ |
| Lines of scorer code | 376 + 430 + 655 + 655 = 2,116        | ~800                     | Eliminate duplication          |
| Variants             | 5 (2 active + 2 overlap + 1 archive) | 3                        | Reduce maintenance burden      |
| Input schemas        | 4 distinct                           | 1 adaptive               | Single source of truth         |
| Output formats       | 3-4 variants                         | 1                        | Unified downstream consumption |
| Test suites          | 2 independent                        | 1 parametrized           | Faster regression testing      |
| Documentation        | 5 SKILL.md + scattered refs          | 1 SKILL.md + references/ | Single guidance source         |
| Setup time for users | Mode-dependent (confusing)           | Single `--mode` flag     | Clarity & discoverability      |

---

## Part 13: Quick Reference Tables

### Variant at-a-Glance

| Aspect              | CA               | CDR                      | CDA                 | HDA                 | HDA.v1          |
| ------------------- | ---------------- | ------------------------ | ------------------- | ------------------- | --------------- |
| **Rigor Level**     | Lite             | Medium                   | Rigorous            | Rigorous            | Archive         |
| **Score Scale**     | 0-100            | 1-5 / 0-100              | 0-100               | 0-100               | 0-100           |
| **Criteria Fields** | id, name, weight | Full + scoring_rule      | Full                | Full                | Full            |
| **Alt Fields**      | scores           | + effort, risk, feasible | + justification     | + type, evidence    | + justification |
| **Evaluators**      | -                | -                        | Independent records | -                   | -               |
| **Discovery**       | -                | -                        | -                   | Mandatory           | -               |
| **JSON Schema**     | -                | -                        | -                   | input + output      | -               |
| **Decision Status** | -                | -                        | -                   | proceed/defer/no-go | -               |
| **Harness**         | -                | -                        | Optional wrapper    | Built-in            | -               |
| **Lines (Scorer)**  | 376              | 430                      | 655                 | 655+                | refs CA         |

### Feature Inclusion Matrix

```asciitable
                  CA  CDR  CDA  HDA
Criteria confirmation        ✗   ✓    ✓    ✓
Score scale 1-5             ✗   ✓    ✓    ✓
Effort/risk fields          ✗   ✓    ✓    ✓
Independent evaluators      ✗   ✗    ✓    ✓
Discovery protocol          ✗   ✗    ✗    ✓
Alternative type classes    ✗   ✗    ✗    ✓
External evidence arrays    ✗   ✗    ✗    ✓
JSON Schema validation      ✗   ✗    ✗    ✓
Decision status gating      ✗   ✗    ✗    ✓
Run ID audit trail          ✗   ✗    ✗    ✓
```

---

## Appendix A: Example Inputs by Mode

### Lite Mode (comparative-analysis)

See [comparative-analysis/references/input-schema.md](comparative-analysis/references/input-schema.md)

### Medium Mode (comparative-decision-review)

See [comparative-decision-review/references/input-schema.md](comparative-decision-review/references/input-schema.md)

### Rigorous Mode (hybrid-decision-analysis)

See [hybrid-decision-analysis/references/input-schema.md](hybrid-decision-analysis/references/input-schema.md)

---

## Appendix B: Python Script Line Counts

```bash
wc -l skills/workflow/*/scripts/*.py

comparative-analysis/scripts/score_alternatives.py       376
comparative-decision-review/scripts/score_options.py      430
comparative-decision-analysis/scripts/score_with_guardrails.py  655
hybrid-decision-analysis/scripts/score_with_guardrails.py  655

Total Scorer Logic: 2,116 lines
Estimated Unified: ~800 lines (63% reduction)
```

---

## Appendix C: Deprecation Timeline

**Proposed**:

- Month 1: Announce unified variant, tag old as deprecated
- Months 2-3: Document migration path, run in parallel
- Months 4-5: Migrate all internal uses
- Month 6: Archive old variants to archive/

**Support windows**:

- comparative-analysis: EOL (replaced by decision-analysis lite)
- comparative-decision-review: EOL (replaced by decision-analysis medium)
- comparative-decision-analysis: MERGED into decision-analysis rigorous
- hybrid-decision-analysis: MERGED into decision-analysis rigorous
- hybrid-decision-analysis.v1: Already archived

---

## Appendix D: Files to Create/Modify

### Create

```bash tree
/pax/skills/workflow/decision-analysis/
  ├─ SKILL.md
  ├─ scripts/
  │   ├─ score_decision.py
  │   └─ test_score_decision.py
  ├─ references/
  │   ├─ unified-input.schema.json
  │   ├─ unified-output.schema.json
  │   ├─ input-schema.md
  │   ├─ output-schema.md
  │   ├─ rubric-packs.md
  │   ├─ discovery-protocol.md
  │   ├─ quality-gates.md
  │   └─ scenario-bakeoff-protocol.md
  └─ assets/
      └─ decision-record-template.md
```

### Modify

```bash tree
/pax/skills/workflow/
  ├─ comparative-analysis/ → DEPRECATED
  ├─ comparative-decision-review/ → DEPRECATED
  ├─ comparative-decision-analysis/ → DEPRECATED
  ├─ hybrid-decision-analysis/ → DEPRECATED
  ├─ hybrid-decision-analysis.v1/ → ARCHIVED
  └─ decision-analysis/ → NEW (unified)
```

### Archive

```bash tree
/pax/archive/skills/workflow/
  ├─ comparative-analysis.v1-deprecated/
  ├─ comparative-decision-review.v1-deprecated/
  ├─ comparative-decision-analysis.v1-deprecated/
  ├─ hybrid-decision-analysis.v1-deprecated/
  └─ hybrid-decision-analysis.v1-archive/
```

---

## Conclusion

The 5 decision-analysis variants can be confidently consolidated into **3 modes** (Lite, Medium, Rigorous) sharing:

1. **Common input structure** with mode-conditional validation
2. **Unified output schema** with optional fields per mode
3. **Single deterministic scorer** (score_decision.py, ~800 lines vs. 2,116 spread)
4. **Shared references** (rubric packs, quality gates, discovery protocol)
5. **Consolidated documentation** (SKILL.md, references/)

**Benefits**:

- ✓ 63% code reduction (2,116 → 800 lines scorer)
- ✓ Single source of truth for scoring logic
- ✓ Clear user guidance on mode selection
- ✓ Faster iteration & maintenance
- ✓ Uniform testing & validation
- ✓ Audit-trail capabilities available in all modes

**Timeline**: 8 weeks (2 months) with staged migration & support window.
