# Discovery Protocol

> **DEPRECATED**: This discovery protocol is now superseded by the `discovering-alternatives` skill (see `../../discovering-alternatives/SKILL.md`), which provides:
>
> - Exhaustive 5-source discovery (pretrained, memory, repo, user context, web)
> - Hard fail-fast gates and evidence requirements
> - Structured logging with timestamps
> - User confirmation before ranking
>
> **Use this legacy protocol only if `discovering-alternatives` is unavailable** or for lightweight discovery scenarios that don't require full rigor.

Use this before scoring.

## Objective

Prevent local-option bias and surface non-obvious alternatives.

## Discovery Lanes

Run all lanes unless explicitly blocked:

1. Internal lane:
   - Existing local skills, scripts, and workflows.
2. Adjacent lane:
   - Compose or extend internal options.
   - Build-new baseline.
3. External lane:
   - At least one external alternative (tool, vendor, framework, pattern, or service).
   - Use recent primary sources when possible (official docs, specs, vendor docs, standards, papers).

## Minimum Option Set

- At least 4 normalized alternatives when feasible.
- At least 2 alternatives required for scoring.
- At least 1 external option unless network or policy blocks external discovery.

If external discovery is blocked, record:

- blocking reason
- date of check
- follow-up action to revisit discovery

## Normalization Fields

For every alternative, record:

- `id`
- `name`
- `type` (`internal`, `compose`, `external`, `build-new`)
- `effort` (`S|M|L`)
- `risk` (`Low|Med|High`)
- `feasible` (`true|false`)
- `constraints_met` (list)
- `known_gaps` (list)
- `key_unknowns` (list)
- `source_links` (list, required for external options)

## Output

Produce a concise discovery log in the final record:

- discovered options by lane
- rejected options and reasons
- external sources consulted
