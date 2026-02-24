---
name: authoring-json-schema
description: "Author, refactor, and maintain JSON Schema for reuse, composition, and long-term stability. Use when asked to create schemas, reduce duplication, compose schemas with $ref/allOf/oneOf/if-then-else, review schema quality, or migrate legacy draft-04+ schemas. Prefer draft-2020-12 for new authoring; treat draft-04/draft-06 as migration-only."
license: MIT
---

# JSON Schema Authoring

Create and evolve JSON Schema contracts that stay reusable, readable, and safe to change.

## When to Use This Skill

- User asks to "create a JSON schema" or "define validation rules"
- User asks to reduce duplication across schemas
- User asks to compose schemas with `$ref`, `allOf`, `oneOf`, or conditionals
- User asks to migrate from draft-07 to draft-2020-12
- User asks to migrate legacy draft-04 or draft-06 schemas
- User asks to version and maintain schemas safely
- User asks to review schema quality, maintainability, or compatibility

## Draft Policy

- Preferred: draft-2020-12
- Allowed for active authoring: draft-07+
- Migration-only input: draft-04 and draft-06
- Never author new long-lived schemas on draft-04 or draft-06

## Core Rules

- Keep schemas contract-first and example-driven
- Reuse via `$defs` + `$ref`, not copy-paste
- Favor explicit constraints over implicit assumptions
- Keep composition shallow and legible
- Treat schema changes as versioned API changes
- Validate with both positive and negative fixtures

## Execution Workflow

1. Capture contract first: use real valid and invalid examples before writing schema logic.
2. Select target draft: default to draft-2020-12; if source is draft-04 or draft-06, plan migration path first.
3. Establish schema identity: set `$schema`, stable `$id`, `title`, and `description`.
4. Model constraints: define `type`, `properties`, `required`, and object openness policy.
5. Extract reusable modules: move repeated structures into `$defs` (or `definitions` when staying on draft-07).
6. Compose intentionally: use `allOf` for orthogonal layering, `oneOf` for exclusive variants, and `if/then/else` for conditional rules.
7. Harden with fixtures: require passing all valid fixtures and failing all invalid fixtures.
8. Version safely: treat breaking validation changes as major versions and publish migration notes.

## Minimal Starters

Draft-2020-12 baseline:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/entity.json",
  "type": "object",
  "properties": {},
  "required": [],
  "unevaluatedProperties": false,
  "$defs": {}
}
```

Draft-07 baseline:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/schemas/entity.json",
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false,
  "definitions": {}
}
```

## Legacy Migration Rules (draft-04 and draft-06)

1. Freeze legacy behavior with fixtures before changing keywords.
2. Prefer two-step migration: draft-04/06 -> draft-07 -> draft-2020-12.
3. Preserve old schema URLs during migration if consumers resolve by URL.
4. Track keyword deltas explicitly: `id` -> `$id`; `definitions` -> `$defs`; `dependencies` -> `dependentRequired` or `dependentSchemas`; re-check `exclusiveMinimum`/`exclusiveMaximum` behavior.
5. Keep draft-04/06 support only as temporary compatibility.

## Quality Gates

- Schema declares correct draft and stable `$id`
- Reuse is via `$ref`, not duplicate subschemas
- Composition is shallow and unambiguous
- Object openness policy is explicit
- Positive and negative fixtures both exist and pass expected outcomes
- Version impact and migration notes are recorded for behavioral changes

## Validator Check Pattern

```bash
ajv validate -s schemas/example.json -d fixtures/valid/*.json
ajv validate -s schemas/example.json -d fixtures/invalid/*.json && exit 1 || true
```

## Output Expectations

- Maintainable schema file(s) with clear ref strategy
- Fixture coverage for accepted and rejected payloads
- Short migration note for any breaking change
