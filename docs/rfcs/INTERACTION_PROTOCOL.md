# Resolution Conversation Session

This protocol is authoritative for turns that target `docs/rfcs/**`.

## Marker Grammar

- `RFC: START <rfc_name>`
- `RFC: HELP`
- `RFC: END`
- `POINT_REVIEW: <n>`
- `SIDEBAR: <text>`
- `RESUME`
- `RESUME: POINT <n>`

Markers are case-sensitive and MUST match exactly.

## Session State Machine

State fields:

- `rfc_name`: active RFC slug from `RFC: START`
- `mode`: `POINT_REVIEW` or `SIDEBAR`
- `current_point`: integer or `null`
- `session_active`: boolean

Transitions:

1. `RFC: START <rfc_name>`
   - set `session_active=true`, `rfc_name=<rfc_name>`, `mode=POINT_REVIEW`, `current_point=null`
   - scope defaults to `docs/rfcs/<rfc_name>/**`
2. `POINT_REVIEW: <n>`
   - require `session_active=true`
   - set `mode=POINT_REVIEW`, `current_point=<n>`
3. `SIDEBAR: <text>`
   - require `session_active=true`
   - set `mode=SIDEBAR`
4. `RESUME`
   - require `session_active=true`
   - set `mode=POINT_REVIEW`; keep existing `current_point`
5. `RESUME: POINT <n>`
   - require `session_active=true`
   - set `mode=POINT_REVIEW`, `current_point=<n>`
6. `RFC: END`
   - set `session_active=false`, `rfc_name=null`, `mode=null`, `current_point=null`
7. `RFC: HELP`
   - allowed in any state.
   - MUST NOT mutate session state.
   - MUST return current state, valid next markers for the current state, and one recommended next action.

Default behavior for unmarked turns:

- if `session_active=true`, treat as `SIDEBAR` (non-mutating).
- if `session_active=false`, follow normal repository instructions.

## Output Contract

For all turns while `session_active=true`, assistant MUST begin output with:

`RFC_SESSION: <rfc_name> | MODE: <mode> | POINT: <n|none>`

Additional marker rules:

- In `POINT_REVIEW`, assistant MUST emit exactly one `POINT_CONCLUSION: CLOSED|OPEN` at the end of the point response.
- In `SIDEBAR`, assistant MUST NOT emit `POINT_CONCLUSION`.
- Review cycle completion MUST emit `REBASELINE_CONCLUSION: SYNCHRONIZED`.
- For `RFC: HELP`, assistant MUST return this block shape and MUST NOT emit `POINT_CONCLUSION`:
  - `HELP_STATE`: snapshot of session fields (`session_active`, `rfc_name`, `mode`, `current_point`, `last_point_conclusion`, `last_rebaseline`)
  - `HELP_OPTIONS`: list of valid next markers from the current state
  - `HELP_RECOMMENDED_NEXT_ACTION`: exactly one suggested marker

Recommended-next-action policy:

- if `session_active=false`: recommend `RFC: START <rfc_name>`
- if `session_active=true` and `mode=POINT_REVIEW` and `current_point=null`: recommend `POINT_REVIEW: <n>`
- if `session_active=true` and `mode=SIDEBAR` and `current_point!=null`: recommend `RESUME: POINT <current_point>`
- if `session_active=true` and `mode=SIDEBAR` and `current_point=null`: recommend `RESUME`
- if `session_active=true` and `mode=POINT_REVIEW` and `last_point_conclusion=OPEN`: recommend one of `ACCEPT`, `CHALLENGE: <reason>`, or `REVISE: <change>`

## Skill Binding

- In `POINT_REVIEW` mode, assistant MUST apply `write-technical-rfc` for RFC/finding artifacts under `docs/rfcs/**`.
- In `SIDEBAR` mode, assistant SHOULD answer directly and MUST avoid mutating RFC/finding artifacts unless explicitly authorized.

## File Mutation Rules

- `POINT_REVIEW` mode:
  - RFC/finding file edits are allowed when requested.
  - assistant MAY update evidence line references and status markers.
- `SIDEBAR` mode:
  - assistant MUST NOT change point status.
  - assistant MUST NOT emit `POINT_CONCLUSION`.
  - assistant MUST NOT modify files under `docs/rfcs/<rfc_name>/**` unless the user explicitly asks for edits during sidebar.

## Session Persistence

Assistant MUST persist state in `docs/rfcs/.session-state.json` whenever mode/point/session changes.

The state file MUST conform to:

- `docs/rfcs/session-state.v1.schema.json`

Required fields:

- `schema_version` (string, currently `"1"`)
- `session_active` (boolean)
- `rfc_name` (string or null)
- `mode` (`POINT_REVIEW` | `SIDEBAR` | null)
- `current_point` (integer or null)
- `last_point_conclusion` (`OPEN` | `CLOSED` | null)
- `last_rebaseline` (ISO-8601 datetime or null)
- `updated_at` (ISO-8601 datetime)

Initialization rule:

- If `docs/rfcs/.session-state.json` does not exist, assistant MUST create it with
  `session_active=false` and other state fields set to `null` (except `schema_version` and `updated_at`).

## Protocol

1. I present one point only: claim, evidence, risk, and concrete fix.
2. You respond with one of:
   - `ACCEPT`
   - `CHALLENGE: <reason>`
   - `REVISE: <change you want>`
3. I either revise or defend once.
4. I emit a definitive marker:
   - `POINT_CONCLUSION: CLOSED` (we move to next point)
   - `POINT_CONCLUSION: OPEN` (we stay on this point)
5. Rebaseline (required before declaring review complete):
   - Re-scan the current spec and findings.
   - Update statuses (`OPEN`/`CLOSED`), severity, evidence paths/line refs, and scorecard.
   - Remove or mark superseded claims.
   - Emit `REBASELINE_CONCLUSION: SYNCHRONIZED`.

Advance rule: move point-to-point only after `POINT_CONCLUSION: CLOSED`; declare review completion only after `REBASELINE_CONCLUSION: SYNCHRONIZED`.
