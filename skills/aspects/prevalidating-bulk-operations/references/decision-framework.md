# Decision Framework Examples & Escalation

## Full Decision Tree by Question

### Question 1: File Count

```text
How many files will be updated?

1-2 files
└─ Pattern cost > benefit
   └─ Route: DIRECT (Phase 2 only)
   └─ Proceed to implementing-backlog directly

3-4 files
└─ Pattern is breakeven to beneficial
   └─ Depends on Question 2 (schema discoverability)
   └─ Route: CONDITIONAL (see Question 2)

5+ files
└─ Pattern is strongly recommended
   └─ Cost of discover << cost of N failures × rework
   └─ Route: PATTERN REQUIRED
   └─ Proceed to Phase 1 (discover-validation-criteria)

---
Reasoning: Discovery cost (1-2 hours) amortizes over file count.
At N=3-4, benefit = cost. At N≥5, benefit >> cost.
```

### Question 2: Schema Discoverability

#### When to ask

Only ask if file count is 3-4 (from Question 1 CONDITIONAL)

```text
Are validation constraints discoverable?

YES (schema files, lint configs, docs exist)
└─ Pattern applies
   └─ Proceed to Phase 1 (discover-validation-criteria)
   └─ Expected savings: 4× fewer file operations

NO (constraints implicit/undocumented)
└─ Pattern cost too high
   └─ First: Document constraints as schema/config
   └─ Then: Re-evaluate with Phase 1
   └─ Alternative: Direct with high caution

---
Reasoning: Pattern assumes criteria are discoverable.
If not, discovery cost balloons; direct might be safer.
```

### Question 3: Operation Type

#### When to ask

Ask for all routes: affects Phase 2a/2b specifics

```text
What type of bulk operation?

UPDATE (modifying existing N files)
└─ Pattern applies standard
   └─ Sample = copy existing file, edit
   └─ Risk = cascading failures to all N
   └─ Use full three-phase pattern

CREATE (generating N new files from template)
└─ Pattern applies with variation
   └─ Sample = first generated file
   └─ Risk = lower (no existing state)
   └─ Judgement call: if N ≥ 6, use pattern; if 3-5, optional

MIGRATE (transitioning from format A to B)
└─ Pattern strongly recommended
   └─ Sample = convert 1 file A→B, validate
   └─ Risk = high (all files must convert successfully)
   └─ Always use full three-phase pattern

---
Reasoning: Risk profile varies; UPDATE and MIGRATE benefit most from pattern
```

---

## Routing Decision Output Structure

```json
// Example JSON structure returned by routing decision
{
  "evaluation_timestamp": "2026-02-25T14:30:00Z",
  "file_count": 9,
  "operation_type": "UPDATE|CREATE|MIGRATE",
  "schema_discoverable": true,
  "routing": "PATTERN_REQUIRED|PATTERN_CONDITIONAL|DIRECT",
  "applied_pattern": true,
  "phase_sequence": [
    "Phase 1: discover-validation-criteria",
    "Phase 2a: sample-validation",
    "Phase 2b: bulk-apply"
  ],
  "evidence": {
    "decision_1_file_count": "9 files >= 5 threshold → PATTERN_REQUIRED",
    "decision_2_schema": "Schema file found at schemas/frontmatter/work-item.json → discoverable",
    "decision_3_operation": "UPDATE (modifying existing files) → use standard pattern"
  },
  "cost_estimate": {
    "discovery_phase_1": "1-2 hours",
    "sample_validation_phase_2a": "30-60 minutes",
    "bulk_apply_phase_2b": "30-60 minutes",
    "total": "2-4 hours (includes fallback iterations)"
  },
  "escalation_threshold": 3,
  "escalation_trigger": "After 3 failed sample validation attempts, stop and ask for clarification",
  "next_steps": [
    "Call discover-validation-criteria skill (Phase 1)",
    "Document criteria dict",
    "Include in planning output",
    "Proceed to Phase 2a: sample validation"
  ]
}
```

---

## Real-World Examples

### Example 1: 9 work item files (UPDATE)

```text
Q1: File count = 9
    → 9 >= 5 → PATTERN_REQUIRED

Q2: (not asked; already PATTERN_REQUIRED)

Q3: Operation = UPDATE (modifying frontmatter)
    → Standard pattern applies

Output: routing = PATTERN_REQUIRED
Evidence: File count exceeds threshold
Next: Call discover-validation-criteria
```

### Example 2: 4 config files (UPDATE)

```text
Q1: File count = 4
    → 3 <= 4 <= 4 → PATTERN_CONDITIONAL

Q2: Schema discoverable?
    Check: find . -name "*.schema.json" | grep -i config
    Result: YES (config.schema.json exists)
    → PATTERN_REQUIRED

Q3: Operation = UPDATE (changing config fields)
    → Standard pattern applies

Output: routing = PATTERN_REQUIRED
Evidence: Conditional routed to pattern due to schema discoverability
Next: Call discover-validation-criteria
```

### Example 3: 2 config files (UPDATE)

```text
Q1: File count = 2
    → 2 < 3 → DIRECT

Q2: (not asked; already DIRECT)

Q3: Operation = UPDATE
    (not relevant for routing, but document for Phase 2)

Output: routing = DIRECT, applied_pattern = false
Next: Skip Phase 1, proceed to Phase 2 (direct implementation)
Risk note: "Bulk operation with pattern not applied. If validation fails,
           rework will affect 2 files. Consider using pattern for future."
```

### Example 4: 8 migration files (MIGRATE)

```text
Q1: File count = 8
    → 8 >= 5 → PATTERN_REQUIRED

Q2: (not asked; already PATTERN_REQUIRED)

Q3: Operation = MIGRATE (format A → B)
    → Pattern strongly recommended (high risk)

Output: routing = PATTERN_REQUIRED
Evidence: File count + operation type both recommend pattern
Next: Call discover-validation-criteria
High-priority note: "Format migration. Sample validation MUST pass before
                    applying to all 8 files. Risk: cascading format errors."
```

---

## Escalation Protocol

If agent cannot answer a decision tree question:

```text
Q1: File count
    - Cannot determine: Ask user "How many files will be updated?"
    - If uncertain: Assume worst case (ask Q2 to be safe)

Q2: Schema discoverable?
    - Cannot find schema: Ask user where constraints are documented
    - If undocumented: User must document as schema/config first
    - Fallback: Route to DIRECT with "high caution" flag

Q3: Operation type
    - If unclear: Default to pattern (safer, less risk)
```

---

## Machine-Executable Decision Tree (YAML)

```yaml
decision_tree:
  file_count:
    type: "numeric threshold"
    values:
      1-2: "route: DIRECT"
      3-4: "route: CONDITIONAL → ask question_2"
      5+: "route: PATTERN_REQUIRED"

  schema_discoverable:
    condition: "file_count in [3, 4]"
    type: "boolean (can schema files be found?)"
    values:
      true: "route: PATTERN_REQUIRED"
      false: "route: DIRECT (high caution)"

  operation_type:
    type: "enum"
    values:
      UPDATE: "standard pattern"
      CREATE: "pattern if file_count >= 6, optional if 3-5"
      MIGRATE: "always use standard pattern"

  final_routing:
    DIRECT: "skip Phase 1, proceed to Phase 2"
    PATTERN_CONDITIONAL: "use pattern if Question 2 = true"
    PATTERN_REQUIRED: "use pattern, enforce all phases"
```

---

## Anti-Patterns Prevented

- ❌ Applying direct approach to 10-file operation (should use pattern)
- ❌ Using pattern for 1-file operation (cost not justified)
- ❌ Assuming schema is discoverable without checking (wasted discovery time)
- ❌ Applying pattern to undocumented constraints (discovery impossible)
- ❌ Skipping Phase 2a sample validation for MIGRATE operations (high cascading risk)

---

## Success Metrics

Track routing accuracy across phases:

- [ ] Routing decisions logged in work item notes
- [ ] Pattern applied when aspect recommended
- [ ] Pattern skipped when aspect recommended direct
- [ ] Actual failures match or beat predicted risk (validation loops)
- [ ] Phase 1 discovery cost aligns with estimate (1-2 hours actual)
