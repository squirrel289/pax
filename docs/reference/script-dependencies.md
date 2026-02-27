# Decision-Analysis Scripts: Dependency Map & Compatibility Matrix

**Date**: 2026-02-25  
**Purpose**: Guide unified scorer implementation and migration path

---

## Part 1: Script Inventory with Feature Table

### Python Scorer Scripts

| Script                     | Variant | Size   | Core Logic                                                     | Key Additions                                                                                        | Validation                 | Test                          |
| -------------------------- | ------- | ------ | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------- | ----------------------------- |
| `score_alternatives.py`    | CA      | 376 L  | Basic 0-100 scoring, ranking, action rules                     | None                                                                                                 | None                       | None                          |
| `score_options.py`         | CDR     | 430 L  | 1-5/0-100 scale, effort/risk tie-breaks                        | Score conversion, effort_rank, risk_rank, coverage                                                   | None                       | None                          |
| `score_with_guardrails.py` | CDA     | 655 L  | Full guardrails, criteria confirmation, independent evaluators | Evaluator isolation, coverage gates, pre-scoring quality gates                                       | None                       | test_score_with_guardrails.py |
| `score_with_guardrails.py` | HDA     | 655+ L | Same as CDA + discovery, type classification, evidence arrays  | Discovery block reason, alternative type, external evidence, decision_status, JSON Schema validation | validate_json_contract.mjs | test_score_with_guardrails.py |

### Wrapper Scripts

| Script                                | Variant | Purpose                          | Calls                        |
| ------------------------------------- | ------- | -------------------------------- | ---------------------------- |
| `run_comparative_decision_harness.py` | CDA     | Reproducible runs with manifests | → `score_with_guardrails.py` |

### Test & Validation Scripts

| Script                        | Variant | Type    | Covers                                                                        |
| ----------------------------- | ------- | ------- | ----------------------------------------------------------------------------- |
| test_score_with_guardrails.py | CDA     | pytest  | Tie-break ordering, missing evidence, coverage gating, single-option behavior |
| test_score_with_guardrails.py | HDA     | pytest  | Same as CDA + discovery validation                                            |
| validate_json_contract.mjs    | HDA     | Node.js | Input/output JSON Schema validation                                           |

---

## Part 2: Line-by-Line Code Analysis

### score_alternatives.py (Lite, 376 lines)

**Core functions**:

```python
_to_float(value, field)                 # Parse numeric
_normalize_weights(criteria)            # Normalize criterion weights
_normalize_blend(weights)               # Normalize platform weights (0.6/0.4)
_normalize_rules(rules)                 # Min/margin/gap thresholds
_clamp_score(value, field)              # 0-100 bound
_platform_score(option, platform, criteria)  # Weighted avg per platform
_evaluate(data)                         # Main: compute scores, rank, recommend
_format_report(data, result)            # Markdown output
```

**Key logic**:

- Score clamping: `max(0, min(100, value))`
- Weight normalization: `weight_i / Σweights`
- Platform avg: mean across major platforms
- Current platform: weighted sum on single platform
- Success score: `0.6 × major + 0.4 × current`
- Ranking: `(overall_success_score desc, current_platform desc, major_avg desc, name asc)`
- Action rules: fixed thresholds (select_min=80, select_margin=7, etc.)

**Missing from CA**:

- Score scale conversion (1-5 → 0-100)
- Effort/risk fields or tie-breaks
- Criteria confirmation gating
- Independent evaluator support
- Discovery tracking
- Type classification
- Evidence arrays
- JSON Schema validation
- Decision status output

### score_options.py (Medium, 430 lines)

**Additions**:

```python
_normalize_score_scale(value)           # "0-100" or "1-5"
_to_percent_score(value, scale, field)  # Convert 1-5 to 0-100
EFFORT_ORDER = {"s": 0, "m": 1, "l": 2}
RISK_ORDER = {"low": 0, "med": 1, "medium": 1, "high": 2}
_normalize_alternatives(...)            # Extract effort, risk, scores
_alternative_summary(...)               # Effort/risk string
_calculate_coverage(...)                # Missing evidence ratio
_rank_alternatives(...)                 # Ranking with effort/risk tie-breaks
_apply_rules(...)                       # Action rule selection
```

**Key changes vs. CA**:

- `score_scale` parameter: "1-5" or "0-100"
- Conversion: `1-5 × 20 = 0-100` (before weighting)
- Tie-breaks: effort (S < M < L), then risk (Low < Med < High)
- Coverage: `effort_rank`, `risk_rank` added to output
- No scale validation before scoring (assumes valid input)

**Missing from CDR**:

- Criteria confirmation gating (field accepted but not enforced)
- Independent evaluator support
- Discovery tracking
- Type classification
- Evidence arrays
- JSON Schema validation
- Decision status output

### score_with_guardrails.py (CDA/HDA, 655+ lines)

**Unified by both CDA and HDA, with HDA adding**:

```python
# All CDA features
_normalize_criteria(...)                # Full criterion contract (metric, data_source, scoring_rule)
_normalize_alternatives(...)            # Effort, risk, feasible, justification
_normalize_independent_evaluations(...) # Evaluator isolation check
_check_pre_scoring(...)                 # Quality gates: criteria confirmation, evaluators, coverage

# HDA-specific additions
_normalize_discovery(...)               # external_discovery_done, blocked, reason
_check_discovery_contract(...)          # Enforce external_discovery in rigorous mode
_classify_alternative_type(...)         # internal|compose|external|build-new
_validate_external_evidence(...)        # Evidence arrays per external alt
_compute_decision_status(...)           # proceed|defer|no-go based on coverage/recommendation
_validate_against_schema(...)           # JSON Schema validation (input/output)
```

**Key differences CDA vs HDA**:

| Feature           | CDA                   | HDA                                                            |
| ----------------- | --------------------- | -------------------------------------------------------------- |
| Discovery         | Optional guidance     | Required field + validation                                    |
| Alternative type  | Not tracked           | Classified (internal/compose/external/build-new)               |
| External evidence | Not supported         | Structured arrays (source_url, source_date, evidence_strength) |
| JSON Schema       | None                  | Full validation (input.schema.json, output.schema.json)        |
| Decision status   | Not output            | Required output (proceed/defer/no-go)                          |
| Run ID tracking   | Not output            | Required output + scorer_version + timestamp                   |
| Quality gates     | Pre-scoring + scoring | Same + output gates                                            |

**Shared scoring logic** (both CDA & HDA):

- Score scale conversion (1-5 → 0-100)
- Weighted averaging per platform
- Coverage computation (missing criterion count)
- Deterministic ranking (same tie-breaks as CDR)
- Action rule selection (select/compose/improve/extend/build-new)

---

## Part 3: Feature Inheritance Diagram

```asciitree
score_alternatives.py (CA - 376 L)
  │
  ├─→ score_options.py (CDR - 430 L) [+54 lines]
  │       └─ Adds: scale conversion, effort/risk, coverage
  │
  └─→ score_with_guardrails.py (CDA - 655 L) [+279 lines]
          │
          ├─ (CDA) Adds: criteria confirmation, evaluator isolation, quality gates
          │
          └─→ score_with_guardrails.py (HDA - 655+ L) [same or +features]
                  └─ (HDA) Adds: discovery, alternative type, evidence arrays,
                        JSON Schema validation, decision status, harness integration
```

---

## Part 4: Unified Scorer Implementation Map

### Proposed score_decision.py (Unified, ~800L)

**Structure**:

```python
# 1. Input parsing & mode detection (50 L)
def parse_args():
def load_json(path):
def detect_mode(data):  # Heuristic: look for criteria_confirmed, discovery, etc.

# 2. Validation layer (250 L, mode-conditional)
def validate_lite_input(data):        # Strict: id, name, weight, scores
def validate_medium_input(data):      # Add: score_scale, effort, risk, coverage
def validate_rigorous_input(data):    # Add: criteria_confirmed, discovery, independent_evaluations
def _validate_against_schema(data, schema_path, mode):  # JSON Schema validation (rigorous)

# 3. Normalization (150 L, shared)
def _normalize_weights(criteria):
def _normalize_score_scale(value):
def _to_percent_score(value, scale):
def _normalize_blend(weights):
def _normalize_rules(rules):
def _normalize_alternatives(alternatives, mode):
def _normalize_criteria(criteria, mode):

# 4. Pre-scoring quality gates (50 L, mode-conditional)
def check_pre_scoring_gates(data, mode):  # Enforced only if mode=rigorous

# 5. Scoring logic (200 L, shared)
def _platform_score(alternative, platform, criteria, scale):
def compute_platform_scores(data):
def rank_alternatives(scores, alternatives, mode):  # Tie-breaks per mode
def select_action(ranking, rules, mode):

# 6. Output formatting & decision status (100 L, mode-conditional)
def build_output(data, ranking, recommendation, mode):
def compute_decision_status(ranking, rules, mode):  # rigorous only
def format_report(output, format):

# 7. Main (50 L)
def main():
    args = parse_args()
    data = load_json_and_validate(args)
    scores = compute_platform_scores(data)
    ranking = rank_alternatives(scores, data)
    recommendation = select_action(ranking, data)
    output = build_output(...)
    write_json(args.json_output, output)
    write_report(args.output, output)
```

**Code reuse opportunities**:

| Function                 | CA  | CDR | CDA | HDA | Unified                                   |
| ------------------------ | --- | --- | --- | --- | ----------------------------------------- |
| `_normalize_weights`     | ✓   | ✓   | ✓   | ✓   | Shared, identical                         |
| `_normalize_blend`       | ✓   | ✓   | ✓   | ✓   | Shared, identical                         |
| `_normalize_rules`       | ✓   | ✓   | ✓   | ✓   | Shared, identical                         |
| `_to_float`              | ✓   | ✓   | ✓   | ✓   | Shared, identical                         |
| `_clamp_score`           | ✓   | -   | -   | -   | Variant CA, not used elsewhere            |
| `_normalize_score_scale` | -   | ✓   | ✓   | ✓   | Shared, identical                         |
| `_to_percent_score`      | -   | ✓   | ✓   | ✓   | Shared, identical                         |
| `_platform_score`        | ✓   | ✓   | ✓   | ✓   | Shared, signature varies by scale support |
| Ranking logic            | ✓   | ✓   | ✓   | ✓   | Shared base, mode-conditional tie-breaks  |
| Action rules             | ✓   | ✓   | ✓   | ✓   | Shared, identical                         |

**Duplication eliminated**:

- CA & CDR both implement weight normalization → 1 version
- CDR, CDA, HDA all implement score scale conversion → 1 version
- Score clamping logic duplicated in CDR/CDA/HDA → 1 version
- Ranking duplicated in CDR/CDA/HDA → 1 parametrized version
- Action rule selection duplicated 3x → 1 version

---

## Part 5: Validation Rules by Mode

### Lite Mode (comparative-analysis)

**Required input**:

- `decision` (string, non-empty)
- `current_platform` (string, non-empty)
- `criteria` (array, min 1 item)
  - Each: `id` (string), `name` (string), `weight` (number ≥ 0)
- `alternatives` (array, min 1 item)
  - Each: `id` (string), `name` (string), `scores` (object)
    - `scores[platform][criterion_id]` = number (0-100) or null

**Optional input**:

- `major_platforms` (array of strings, default: ChatGPT, Claude, Gemini, Copilot)
- `weights` (object: major_platform_average, current_platform)
- `recommendation_rules` (object: select_min, select_margin, etc.)

**Validation rules**:

- All scores must be 0-100 or null
- `current_platform` must be in `major_platforms` or treated as omitted
- At least 2 alternatives preferred (warning if 1)
- No schema validation (structural only)

**Output fields**:

- Minimal: `decision`, `ranked_alternatives[].{id, name, rank, major_platform_average, current_platform_score, overall_success_score}`, `recommendation.{action, chosen_option_ids, reason}`

### Medium Mode (comparative-decision-review)

**Required input** (all Lite fields plus):

- `criteria_confirmed` (boolean, optional; if missing, assume true)
- `score_scale` (string: "0-100" or "1-5", default "0-100")
- `alternatives[].{effort, risk, feasible, justification}` (required)

**Enhanced criteria** (optional but recommended):

- `metric` (string: how to measure)
- `data_source` (string: evidence source)
- `scoring_rule` (string: guidance)

**Validation rules**:

- All Lite rules plus:
- Score scale must be "0-100" or "1-5"
- If scale="1-5", scores must be 1-5 (or null)
- If scale="0-100", scores must be 0-100 (or null)
- `effort` must be "S", "M", or "L"
- `risk` must be "Low", "Med", "Medium", or "High"
- `feasible` must be boolean
- `justification` must be non-empty string
- No independent evaluators
- No discovery field (ignored if present)
- No schema validation

**Output fields** (all Lite fields plus):

- `effort_rank` (integer, tie-break order)
- `risk_rank` (integer, tie-break order)
- `coverage` (float, 0-1, missing evidence ratio)
- `notes` (string, optional)

### Rigorous Mode (comparative-decision-analysis / hybrid-decision-analysis)

**Required input** (all Medium fields plus):

- `criteria_confirmed` (boolean, must be `true` or mode rejects)
- `criteria[].{metric, data_source, scoring_rule}` (required, not optional)
- `criteria_confirmation_source` (enum: "user-confirmed", "provided-input", "yolo-mode", required if criteria_confirmed=true)
- (HDA only) `discovery` (object: external_discovery_done, external_discovery_blocked, block_reason if blocked)
- (CDA only) `independent_evaluations` (array: one per alternative with isolation_confirmed=true)

**Enhanced alternatives** (HDA only):

- `type` (enum: "internal", "compose", "external", "build-new")
- `evidence` (array, required if type="external")
  - Each: `source_url` (URI), `source_date` (ISO 8601), `evidence_strength` (low|medium|high), `notes` (optional)

**Validation rules**:

- All Medium rules plus:
- `criteria_confirmed` must be `true`
- `criteria_confirmation_source` required when confirmed (validates choice)
- Criteria must include `metric`, `data_source`, `scoring_rule` (non-empty strings)
- `min_coverage` rule (default 0.8) must be met for "select" or "compose" actions
- If CDA: `independent_evaluations` array required
  - One record per alternative
  - Each: `alternative_id` (matches alternative), `evaluator_id` (unique), `isolation_confirmed` (const true), `summary` (non-empty)
- If HDA: `discovery` object required
  - `external_discovery_done` (boolean)
  - `external_discovery_blocked` (boolean)
  - If `blocked=true`, `block_reason` required (non-empty string)
- If HDA: `alternatives[].type` required (internal|compose|external|build-new)
- If HDA and type="external": `evidence` array required, min 1 item
- JSON Schema validation against input.schema.json (HDA only)

**Output fields** (all Medium fields plus):

- `run_id` (string, unique run identifier)
- `scorer_version` (string, e.g., "2.0.0")
- `rules_version` (string, e.g., "2026-02-20")
- `evaluated_at` (ISO 8601 timestamp)
- `decision_status` (enum: "proceed", "defer", "no-go")
- `platform_scores` (object: per-platform scores per alternative)
- All fields in `ranked_alternatives[].{...}` (same as Medium)
- JSON Schema validation against output.schema.json (HDA only)

---

## Part 6: Test Coverage Plan

### Unified Test Suite (test_score_decision.py)

```python
import pytest

class TestLiteMode:
    def test_basic_scoring(self):
        # Input: minimal, 0-100 only
        # Verify: ranking, overall_success_score

    def test_missing_platform(self):
        # current_platform not in major_platforms, treated as extra

    def test_single_alternative(self):
        # Warning, but still scores

    def test_score_clamping(self):
        # Scores -10, 150 clamped to 0, 100

class TestMediumMode:
    def test_score_scale_1_5(self):
        # 1-5 converted to 0-100 (× 20)

    def test_effort_risk_tiebreak(self):
        # Same overall_success_score, effort breaks first

    def test_coverage_computation(self):
        # Missing criteria counted, coverage ratio calculated

    def test_feasible_gating(self):
        # Infeasible option not recommended unless all infeasible

    def test_score_scale_0_100(self):
        # 0-100 used directly, no conversion

class TestRigorousMode:
    def test_criteria_confirmation_required(self):
        # criteria_confirmed=false → reject

    def test_confirmation_source_required(self):
        # criteria_confirmed=true but no source → reject

    def test_independent_evaluators_required_cda(self):
        # CDA: one evaluator per alternative, isolation_confirmed=true

    def test_discovery_required_hda(self):
        # HDA: external_discovery_done, blocked, block_reason if blocked

    def test_alternative_type_classification_hda(self):
        # type in [internal, compose, external, build-new]

    def test_external_evidence_required_hda(self):
        # type=external → evidence array required, min 1 item

    def test_json_schema_validation_hda(self):
        # Input validates against input.schema.json
        # Output validates against output.schema.json

    def test_coverage_gating(self):
        # select/compose require coverage >= min_coverage
        # decision_status=defer if not met

    def test_decision_status_gates(self):
        # proceed if top is strong
        # defer if coverage low
        # no-go if all infeasible

class TestCrossMode:
    def test_ranking_consistency(self):
        # Same alternatives, mode shouldn't change ranking
        # (only output fields differ)

    def test_action_selection_consistency(self):
        # Same scores, mode shouldn't change action

    def test_validation_mode_isolation(self):
        # Lite input rejected by Medium/Rigorous
        # Medium input rejected by Rigorous
        # Rigorous input accepted by all (downgrade via mode flag?)

class TestRegressionCases:
    # Migrated from original test suites

    def test_tie_break_ordering(self):
        # From CDA/HDA: name↑ vs effort/risk ordering

    def test_missing_evidence_handling(self):
        # null values excluded from average, not coerced to 0

    def test_single_platform(self):
        # Only current_platform, major_platform_average = current_platform_score

    def test_zero_weight_criterion(self):
        # Normalized away, contributes 0 to scores

    def test_all_missing_scores(self):
        # Alternative with all null values scores 0

    def test_action_rule_thresholds(self):
        # select_min=80, select_margin=7, etc. applied correctly
```

### Coverage Targets

- **Unit tests**: 90%+ of scorer logic
- **Integration tests**: Each mode independently
- **Regression tests**: All 4 original variant test suites pass
- **Schema validation**: Input/output for each mode

---

## Part 7: Migration Execution

### Step 1: Create Unified Input Schema

**File**: `/pax/skills/workflow/shared/unified-input.schema.json` (or decision-analysis/references/input.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Unified Decision Analysis Input",
  "description": "Adaptive schema: required fields depend on mode parameter.",
  "type": "object",
  "required": ["decision", "current_platform", "criteria", "alternatives"],
  "properties": {
    "mode": { "enum": ["lite", "medium", "rigorous"] },
    "decision": { "type": "string", "minLength": 1 },
    "current_platform": { "type": "string", "minLength": 1 },
    "criteria_confirmed": { "type": "boolean" },
    "criteria_confirmation_source": {
      "enum": ["user-confirmed", "provided-input", "yolo-mode"]
    },
    "score_scale": { "enum": ["0-100", "1-5"] },
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
    "discovery": { "$ref": "#/$defs/discovery" },
    "independent_evaluations": { "type": "array" },
    "major_platforms": { "type": "array", "items": { "type": "string" } },
    "weights": { "type": "object" },
    "recommendation_rules": { "type": "object" }
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
      ],
      "properties": {
        "evidence": { "type": "array" }
      }
    },
    "discovery": {
      "type": "object",
      "required": ["external_discovery_done", "external_discovery_blocked"]
    }
  }
}
```

### Step 2: Create Unified Output Schema

**File**: `/pax/skills/workflow/decision-analysis/references/output.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Unified Decision Analysis Output",
  "type": "object",
  "required": ["decision", "mode", "ranked_alternatives", "recommendation"],
  "properties": {
    "mode": { "enum": ["lite", "medium", "rigorous"] },
    "decision": { "type": "string" },
    "run_id": { "type": "string" },
    "scorer_version": { "type": "string" },
    "decision_status": { "enum": ["proceed", "defer", "no-go"] },
    "ranked_alternatives": { "type": "array" },
    "recommendation": { "type": "object" }
  }
}
```

### Step 3: Implement score_decision.py

**Skeleton** (annotated):

```python
#!/usr/bin/env python3
"""Unified decision analysis scorer (all 3 modes)."""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# === Mode detection ===
def detect_mode(data: dict[str, Any]) -> str:
    """Infer mode from input structure."""
    if "discovery" in data and data.get("discovery", {}).get("external_discovery_done") is not None:
        return "rigorous"
    if "criteria_confirmed" in data and data["criteria_confirmed"]:
        return "rigorous"
    if "effort" in str(data.get("alternatives", [])):
        return "medium"
    return "lite"

# === Validation (mode-conditional) ===
def validate_input(data: dict[str, Any], mode: str) -> None:
    """Validate input based on mode."""
    if not data.get("decision") or not isinstance(data["decision"], str):
        raise ValueError("decision required (non-empty string)")
    if not data.get("current_platform") or not isinstance(data["current_platform"], str):
        raise ValueError("current_platform required (non-empty string)")

    if mode == "lite":
        _validate_lite(data)
    elif mode == "medium":
        _validate_medium(data)
    elif mode == "rigorous":
        _validate_rigorous(data)

def _validate_lite(data: dict[str, Any]) -> None:
    """Minimal validation: id, name, weight, scores 0-100 only."""
    if not isinstance(data.get("criteria"), list) or not data["criteria"]:
        raise ValueError("criteria required (non-empty array)")
    for i, c in enumerate(data["criteria"]):
        if not c.get("id") or not c.get("name") or "weight" not in c:
            raise ValueError(f"criteria[{i}] missing id/name/weight")

def _validate_medium(data: dict[str, Any]) -> None:
    """Medium validation: + score_scale, effort, risk."""
    _validate_lite(data)
    scale = data.get("score_scale", "0-100")
    if scale not in {"0-100", "1-5"}:
        raise ValueError("score_scale must be '0-100' or '1-5'")
    if not isinstance(data.get("alternatives"), list):
        raise ValueError("alternatives required (array)")
    for i, a in enumerate(data["alternatives"]):
        if not a.get("effort") or a["effort"] not in {"S", "M", "L"}:
            raise ValueError(f"alternatives[{i}].effort required (S|M|L)")
        if not a.get("risk") or a["risk"] not in {"Low", "Med", "Medium", "High"}:
            raise ValueError(f"alternatives[{i}].risk required")

def _validate_rigorous(data: dict[str, Any]) -> None:
    """Rigorous validation: criteria confirmation, discovery, evaluators, JSON Schema."""
    _validate_medium(data)
    if not data.get("criteria_confirmed"):
        raise ValueError("criteria_confirmed must be true")
    if "criteria_confirmation_source" not in data:
        raise ValueError("criteria_confirmation_source required when criteria_confirmed=true")

    # Check if HDA features present
    if "discovery" in data:
        _validate_discovery(data["discovery"])
    if "independent_evaluations" in data:
        _validate_independent_evaluations(data)

def _validate_discovery(discovery: dict[str, Any]) -> None:
    """Validate discovery object (HDA)."""
    if "external_discovery_done" not in discovery or "external_discovery_blocked" not in discovery:
        raise ValueError("discovery must have external_discovery_done and external_discovery_blocked")
    if discovery.get("external_discovery_blocked") and not discovery.get("block_reason"):
        raise ValueError("block_reason required when external_discovery_blocked=true")

def _validate_independent_evaluations(data: dict[str, Any]) -> None:
    """Validate evaluator isolation (CDA)."""
    evals = data.get("independent_evaluations", [])
    alternatives = {a["id"]: a for a in data.get("alternatives", [])}
    evaluator_ids = set()
    for eval_rec in evals:
        if eval_rec["alternative_id"] not in alternatives:
            raise ValueError(f"evaluator[].alternative_id '{eval_rec['alternative_id']}' not found")
        if eval_rec["evaluator_id"] in evaluator_ids:
            raise ValueError(f"duplicate evaluator_id '{eval_rec['evaluator_id']}'")
        evaluator_ids.add(eval_rec["evaluator_id"])
        if not eval_rec.get("isolation_confirmed"):
            raise ValueError("isolation_confirmed must be true")

# === Normalization (shared) ===
def _normalize_weights(criteria: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize criterion weights."""
    total = sum(c.get("weight", 0) for c in criteria)
    if total <= 0:
        raise ValueError("sum of weights must be > 0")
    return [
        {**c, "weight": c.get("weight", 0) / total}
        for c in criteria
    ]

def _normalize_score_scale(scale: str | None) -> str:
    """Normalize score scale."""
    scale = (scale or "0-100").lower()
    if scale not in {"0-100", "1-5"}:
        raise ValueError("score_scale must be '0-100' or '1-5'")
    return scale

def _to_percent_score(value: float, scale: str) -> float:
    """Convert score to 0-100."""
    if scale == "1-5":
        return min(100, max(0, value * 20))
    return min(100, max(0, value))

# === Scoring (shared) ===
def compute_platform_scores(
    alternatives: list[dict[str, Any]],
    criteria: list[dict[str, Any]],
    scale: str,
) -> dict[str, dict[str, dict[str, float]]]:
    """Compute weighted scores per platform per alternative."""
    result = {}
    for alt in alternatives:
        alt_scores = {}
        for platform, criterion_scores in alt.get("scores", {}).items():
            weighted_sum = 0.0
            count = 0
            for criterion in criteria:
                crit_id = criterion["id"]
                raw = criterion_scores.get(crit_id)
                if raw is not None:
                    score = _to_percent_score(raw, scale)
                    weighted_sum += criterion["weight"] * score
                    count += 1
            alt_scores[platform] = weighted_sum if count > 0 else 0.0
        result[alt["id"]] = alt_scores
    return result

def rank_alternatives(
    alternatives: list[dict[str, Any]],
    scores_by_alt: dict[str, dict[str, float]],
    major_platforms: list[str],
    current_platform: str,
    blend: dict[str, float],
    mode: str,
) -> list[dict[str, Any]]:
    """Rank alternatives deterministically."""
    ranked = []
    for alt in alternatives:
        alt_id = alt["id"]
        platform_scores = scores_by_alt.get(alt_id, {})

        # Major platform average
        major_scores = [platform_scores.get(p, 0) for p in major_platforms]
        major_avg = sum(major_scores) / len(major_scores) if major_scores else 0

        # Current platform score
        current_score = platform_scores.get(current_platform, 0)

        # Overall success score
        overall = blend["major_platform_average"] * major_avg + blend["current_platform"] * current_score

        ranked.append({
            "id": alt_id,
            "name": alt["name"],
            "major_platform_average": round(major_avg, 2),
            "current_platform_score": round(current_score, 2),
            "overall_success_score": round(overall, 2),
            "effort": alt.get("effort"),
            "risk": alt.get("risk"),
            "feasible": alt.get("feasible", True),
            "justification": alt.get("justification", ""),
        })

    # Sort: overall_success_score ↓, current_platform ↓, major_avg ↓, effort, risk, name ↑
    def sort_key(r):
        effort_rank = {"S": 0, "M": 1, "L": 2}.get(r.get("effort", ""), 99)
        risk_rank = {"Low": 0, "Med": 1, "Medium": 1, "High": 2}.get(r.get("risk", ""), 99)
        return (
            -r["overall_success_score"],
            -r["current_platform_score"],
            -r["major_platform_average"],
            effort_rank if mode in {"medium", "rigorous"} else 99,
            risk_rank if mode in {"medium", "rigorous"} else 99,
            r["name"],
        )

    ranked.sort(key=sort_key)

    # Add rank
    for i, r in enumerate(ranked, 1):
        r["rank"] = i

    return ranked

def select_action(
    ranked: list[dict[str, Any]],
    rules: dict[str, float],
) -> str:
    """Select action (select|compose|improve|extend|build-new)."""
    if not ranked or not ranked[0].get("feasible"):
        return "build-new"

    top = ranked[0]["overall_success_score"]
    current = ranked[0]["current_platform_score"]
    major = ranked[0]["major_platform_average"]

    if top < rules.get("improve_min", 55):
        return "build-new"
    if top < rules.get("select_min", 80):
        return "improve"

    second = ranked[1]["overall_success_score"] if len(ranked) > 1 else 0
    if top - second <= rules.get("select_margin", 7):
        return "compose"

    if current < major - rules.get("extend_gap", 10):
        return "extend"

    return "select"

# === Output ===
def build_output(
    data: dict[str, Any],
    ranked: list[dict[str, Any]],
    action: str,
    mode: str,
) -> dict[str, Any]:
    """Build output object."""
    output = {
        "decision": data["decision"],
        "mode": mode,
        "ranked_alternatives": ranked,
        "recommendation": {
            "action": action,
            "chosen_option_ids": [ranked[0]["id"]] if ranked else [],
            "top_option_id": ranked[0]["id"] if ranked else None,
            "score_margin_vs_second": round(ranked[0]["overall_success_score"] - ranked[1]["overall_success_score"], 2) if len(ranked) > 1 else 0,
            "reason": f"Recommended action: {action}"
        }
    }

    if mode == "rigorous":
        output.update({
            "run_id": data.get("run_id", ""),
            "scorer_version": "2.0.0",
            "rules_version": "2026-02-20",
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "decision_status": compute_decision_status(ranked, data),
        })

    return output

def compute_decision_status(ranked: list[dict[str, Any]], data: dict[str, Any]) -> str:
    """Compute decision status (proceed|defer|no-go)."""
    if not ranked:
        return "no-go"
    if any(alt.get("feasible") for alt in ranked):
        return "proceed"
    return "no-go"

# === Main ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--mode", choices=["lite", "medium", "rigorous"], default=None)
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    mode = args.mode or detect_mode(data)
    validate_input(data, mode)

    # Normalize
    criteria = _normalize_weights(data["criteria"])
    scale = _normalize_score_scale(data.get("score_scale"))
    major_platforms = data.get("major_platforms", ["chatgpt", "claude", "gemini", "copilot"])
    blend = {
        "major_platform_average": 0.6,
        "current_platform": 0.4,
    }
    blend.update(data.get("weights", {}))
    rules = {
        "select_min": 80, "select_margin": 7,
        "compose_min": 70, "compose_margin": 7,
        "improve_min": 55, "extend_gap": 10,
    }
    rules.update(data.get("recommendation_rules", {}))

    # Score
    platform_scores = compute_platform_scores(data["alternatives"], criteria, scale)
    ranked = rank_alternatives(data["alternatives"], platform_scores, major_platforms, data["current_platform"], blend, mode)
    action = select_action(ranked, rules)

    # Output
    output = build_output(data, ranked, action, mode)

    with open(args.json_output, "w") as f:
        json.dump(output, f, indent=2)

    # Report (Markdown)
    report = f"# Decision Analysis Report\n\n"
    report += f"Decision: {data['decision']}\n\n"
    report += f"Mode: {mode}\n\n"
    report += f"## Ranked Alternatives\n\n"
    for alt in ranked:
        report += f"- **{alt['rank']}. {alt['name']}** ({alt['overall_success_score']:.1f})\n"
    report += f"\n## Recommendation\n\n"
    report += f"**Action**: {action}\n\n"

    with open(args.output, "w") as f:
        f.write(report)

if __name__ == "__main__":
    main()
```

### Step 4: Migrate References

Copy/consolidate from all 4 variants:

- `rubric-packs.md`
- `discovery-protocol.md`
- `quality-gates.md`
- `scenario-bakeoff-protocol.md`

### Step 5: Run Tests

```bash
pytest skills/decision-analysis/scripts/test_score_decision.py --mode lite
pytest skills/decision-analysis/scripts/test_score_decision.py --mode medium
pytest skills/decision-analysis/scripts/test_score_decision.py --mode rigorous
```

---

## Summary

**Files to create**:

1. `/pax/skills/workflow/decision-analysis/` (new)
2. `scripts/score_decision.py` (unified, ~800 L)
3. `scripts/test_score_decision.py` (unified, ~400 L)
4. `references/input.schema.json` (new)
5. `references/output.schema.json` (new)
6. `references/{rubric-packs, discovery, quality-gates, bakeoff}.md` (merged)
7. `SKILL.md` (consolidated from all 5)

**Files to deprecate**:

1. `comparative-analysis/` → archive
2. `comparative-decision-review/` → archive
3. `comparative-decision-analysis/` → archive
4. `hybrid-decision-analysis/` → archive
5. `hybrid-decision-analysis.v1/` → already archived

**Code reduction**: 2,116 lines → ~800 lines (63% savings)
