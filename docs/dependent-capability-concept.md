# Dependent Capability Contract

## Interface Specification

### Contract Declaration Modes

#### Fuzzy

- `provider` skills declare capabilities using `description` prose and optional runtime metadata.
- `consumer` skills discover candidate providers from installed and accessible skills.

#### Well-defined

- skills MAY declare a machine-readable `metadata.contract` string using the DCI grammar.
- well-defined contracts improve matching precision, policy enforcement, and reproducibility.

### Discovery and Selection Protocol (Applies to Fuzzy and Well-defined)

This protocol is weighted, not sequentially required. Exact capability matching is not mandatory, but higher-confidence signals are weighted more heavily.

#### Definitions

- `query capabilities`: capability identifiers the consumer requires for the current run.
- `contract token`: an atomic value from `P(...)`, `E(...)`, `A(...)`, `R(...)`, `O(...)`, or `Pol(...)`.
- `candidate`: one installed and accessible skill under evaluation.
- `host runtime`: current execution runtime identifier (for example `copilot`, `cli`, `opencode`).

#### Discovery Scope (Deterministic)

`discover_installed_accessible_skills()` MUST enumerate in this order:

1. workspace-local skills under `skills/**/SKILL.md`
2. runtime-installed skills (registry/extension-managed)
3. explicitly mounted external skill roots (if configured)

Inclusion/exclusion rules:

- include only readable skill files with valid frontmatter.
- exclude skills marked disabled by runtime config.
- exclude unreadable/unparseable skills and record rejection reason.
- deduplicate by canonical candidate id `skill-name::skill-path` (first occurrence by source order wins).

#### Capability Token Validation (No Lossy Normalization)

Capability identifiers in `P/E/R/O` clauses MUST already conform to Agent Skill `name`-field constraints:

- length 1..64
- lowercase alphanumeric plus hyphen only
- no leading or trailing hyphen
- no consecutive hyphens

Reference: https://agentskills.io/specification#name-field

Validation behavior:

- parser MUST decode DCI escapes and trim surrounding whitespace.
- parser MUST NOT remove characters, rewrite characters, or collapse content beyond escape decoding.
- if a capability token fails validation:
  - `strict`: treat as unresolved.
  - `best-effort`: keep candidate and apply `invalid_token_penalty`.

Penalty definition:

- `invalid_token_penalty = min(0.20, 0.02 * invalid_token_count_per_candidate)`.

#### Alias Table Governance

Alias resolution supports interoperability without lossy normalization.

- alias table format: `canonical-token -> aliases[]`.
- canonical and alias tokens MUST each pass capability-token validation.
- alias resolution precedence:
  1. runtime/user-provided alias table
  2. workspace alias table (`.dci/aliases.v1.json`)
  3. built-in alias table
- within a single table, canonical exact match wins before alias match.
- alias tables MUST declare `alias_table_version`; this version MUST be part of cache keys.
- alias cycles MUST be flattened to canonical key at load time.

Schema:

- `docs/schemas/dci/aliases.v1.schema.json`

#### Runtime Compatibility Determination

Runtime compatibility is determined from top-level `compatibility` in skill frontmatter.

Rules:

- parse `compatibility` as comma-delimited tokens.
- normalize runtime tokens by lowercasing and trimming surrounding whitespace.
- if field is absent or empty, candidate is runtime-agnostic.
- token `all` means runtime-agnostic.
- unknown compatibility tokens MUST be ignored and logged in the run artifact.
- `S_runtime = 1.0` when candidate is runtime-agnostic or host runtime is listed; otherwise `0.0`.
- in `strict` mode, runtime-incompatible candidates MUST be filtered out before final selection.

#### Scoring Components (`0.0` to `1.0`)

- `S_contract`: capability fit between query capabilities and candidate contract capabilities.
  - for candidates without `metadata.contract`:
    - derive provisional capabilities from `(name + description)` using the same tokenizer as `S_desc`.
    - provisional capabilities MAY contribute only to fuzzy matching.
    - provisional capability matches are capped at `0.25` (below explicit fuzzy token match `0.33`).
  - exact capability match: `1.0`
  - alias-table match: `0.8`
  - fuzzy lexical match above threshold: `0.33`
  - no match: `0.0`
  - `S_contract` is average best-match score over required query capabilities.
  - fuzzy threshold uses Jaro-Winkler similarity `>= 0.90` with fixed parameters:
    - `prefix_scale=0.10`
    - `max_prefix_length=4`
    - no transposition-cost overrides.
  - `0.33` is calibrated so fuzzy contract effect (`0.60 * 0.33 = 0.198`) is comparable to full `S_desc` effect (`0.20 * 1.0 = 0.20`).

- `S_desc`: lexical relevance between query text and `(name + description)`.
  - tokenizer:
    - lowercase
    - split on non-alphanumeric, hyphen, underscore, and slash boundaries
    - remove fixed english stopword set from `docs/schemas/dci/english-stopwords.v1.txt`
    - Porter stemming
  - scorer:
    - BM25 with `k1=1.2`, `b=0.75`
    - normalize: `S_desc = bm25_i / max_bm25`
    - if `max_bm25 = 0`, set `S_desc = 0.0`.

- `S_namepath`: lexical overlap between query tokens and `(skill-name + skill-path)` tokens.
  - same tokenizer as `S_desc`.
  - `S_namepath = |Q ∩ N| / |Q ∪ N|` (Jaccard).
  - if `|Q ∪ N| = 0`, set `S_namepath = 0.0`.

- `S_runtime`: runtime compatibility score defined above.

Composite:

```text
S_total = 0.60*S_contract + 0.20*S_desc + 0.10*S_namepath + 0.10*S_runtime
```

Penalty and final score:

1. Compute `S_total`.
2. Compute penalties:
   - `invalid_token_penalty`
   - `overclaim_penalty`
   - `inflation_penalty` (if applicable)
3. `penalties = invalid_token_penalty + overclaim_penalty + inflation_penalty`.
4. `S_total_penalized = max(0.0, S_total - penalties)`.
5. `S_total_final = S_total_penalized * history_multiplier`.

#### DependentPolicy Defaults and Overrides

Defaults:

- `MinTotalScore=0.45`
- `MinContractScore=0.30`
- `MinRequiredCoverage=1.00` in `strict`, `0.60` in `best-effort`
- `MaxCandidates=5`
- `SelectionMode=single` (`single | cover`)
- `MaxProviders=3` (used only when `SelectionMode=cover`)
- `OnMissingRequired=hard-fail` in `strict`, `offer-emulation` in `best-effort`

Allowed override keys in `Pol(...)`:

- `min-total-score`
- `min-contract-score`
- `min-required-coverage`
- `max-candidates`
- `selection-mode` (`single | cover`)
- `max-providers` (integer >= 1)
- `on-missing-required` (`hard-fail | offer-emulation | auto-emulate`)

Precedence:

1. runtime/user override
2. consumer `Pol(...)`
3. defaults

Provider policy hints:

- provider hints are advisory and MUST NOT relax effective policy.
- provider hints MAY only tighten policy:
  - increase minimum thresholds
  - decrease `max-candidates`
  - move `on-missing-required` to stricter values only
- strictness ordering: `hard-fail > offer-emulation > auto-emulate`.

Selection gates:

- reject candidate when `S_total_final < MinTotalScore`.
- reject candidate when `S_contract < MinContractScore`.
- reject candidate when required coverage `< MinRequiredCoverage`.
- retain top `MaxCandidates` by `S_total_final` before final tie-break.

Selection cardinality:

- `SelectionMode=single`: choose one top-ranked candidate.
- `SelectionMode=cover`: choose a provider set that covers required capabilities.
  - use greedy set-cover tie-broken by `S_total_final`.
  - stop when all required capabilities are covered or `MaxProviders` reached.
  - if uncovered capabilities remain, apply `on-missing-required` policy.

#### On-Missing-Required Semantics

- `hard-fail`:
  - terminate selection with error status.
  - MUST include unresolved capabilities and top candidate diagnostics in report.
- `offer-emulation`:
  - pause for user decision with explicit options: `emulate`, `continue-with-partial`, `abort`.
  - MUST record user choice in report.
- `auto-emulate`:
  - proceed with emulation without prompting.
  - MUST set `degraded_mode=true` and list emulated capabilities in report.

#### Deterministic Tie-Breakers (Ordered)

1. higher `S_contract`
2. higher required-capability coverage
3. fewer unresolved required capabilities
4. higher capability specificity:
   - `S_specificity = required_resolved / max(1, provides_capability_count)`
   - this prefers exact/smaller-capability providers over broad supersets
5. higher `S_skill`, where `S_skill = 0.7*S_desc + 0.3*S_namepath`
6. lower stable hash of canonical candidate id
   - canonical id input: lowercase UTF-8 of `"skill-name::skill-path"`
   - algorithm: SHA-256
   - compare hex digests lexicographically

#### Normative Selection Algorithm (Pseudo-Spec)

```text
candidates = discover_installed_accessible_skills()
candidates = parse_and_validate_contracts(candidates)

for c in candidates:
  compute S_contract, S_desc, S_namepath, S_runtime
  compute penalties and S_total_final

effective_policy = resolve_policy(defaults, consumer_overrides, runtime_overrides)
effective_policy = apply_provider_hints_tightening_only(effective_policy)

gated = apply_selection_gates(candidates, effective_policy)
ranked = sort_by_score_then_tiebreakers(gated)
if effective_policy.selection_mode == "single":
  selected = take_top(ranked, 1)
else:
  selected = greedy_cover(ranked, required_capabilities, effective_policy.max_providers)

if selected is empty or required_capabilities_not_fully_satisfied(selected):
  apply on-missing-required policy
```

#### Manipulation Resistance

- over-claim penalty:
  - `p_count = count(P tokens)`
  - `p_median = median(p_count across candidates)`
  - if `p_count > max(20, 3*p_median)`,
    `overclaim_penalty = min(0.25, 0.05 * ceil((p_count - max(20, 3*p_median))/5))`.

- contract/description divergence check:
  - `S_skill = 0.7*S_desc + 0.3*S_namepath`
  - `delta = S_contract - S_skill`
  - edge cases:
    - candidate count `< 5`: use absolute rule `delta > 0.35`
    - `sigma_delta = 0` and candidate count `>= 5`: use `delta > mu_delta + 0.15`
    - candidate count `= 1`: skip statistical divergence flag
  - otherwise: `delta > mu_delta + 2*sigma_delta` -> `contract-inflated`.
  - strict behavior: exclude `contract-inflated` unless probe passes.
  - best-effort behavior: apply `inflation_penalty = 0.15` unless probe passes.

- capability probes:
  - `strict`: MUST run probe for top candidate when probe exists for any required capability.
  - `best-effort`: SHOULD prompt for probe on `contract-inflated` top candidate.

- local reliability multiplier:
  - track `success_rate_last_20` in `[0.0, 1.0]`
  - `history_multiplier = clamp(0.70, 1.00, 0.70 + 0.30*success_rate_last_20)`
  - apply after penalties.

#### Caching

- caching SHOULD be used for performance and MUST NOT change selection semantics.
- cache key SHOULD include:
  - query capability set
  - candidate id (`skill-name::skill-path`)
  - contract parser version
  - alias table version
  - candidate metadata hash
- cache invalidation MUST occur when parser version, alias version, or candidate metadata hash changes.

#### Reliability Persistence

- `success_rate_last_20` SHOULD be persisted locally.
- default location: `.dci/state/reliability.v1.json` at workspace root.
- workspace root resolution order:
  1. directory containing `.git`
  2. explicit runtime workspace root
  3. current working directory
- path MUST be workspace-relative and MUST NOT be skill-directory-relative.
- persistence fallback: in-memory state is allowed, but report MUST include `history_state=ephemeral`.

Schema:

- `docs/schemas/dci/reliability.v1.schema.json`

#### Required Run Artifact

consumer MUST emit `capability_resolution_report` for each run.

minimum fields per candidate:

- `S_contract`, `S_desc`, `S_namepath`, `S_runtime`
- `S_total`, penalties, `history_multiplier`, `S_total_final`
- tie-breaker details and applied step (if used)

required top-level fields:

- discovery sources scanned and inclusion/exclusion counts
- effective `selection-mode` and provider count limit
- unresolved required capabilities (if any)
- `on-missing-required` action taken
- `degraded_mode` flag and emulated capabilities (when applicable)
- user decision record for `offer-emulation` (when applicable)

Schema:

- `docs/schemas/dci/capability-resolution-report.v1.schema.json`

### Well-defined Contract Grammar

```ebnf
contract := "DCI/" version [ "^" mode ] SP clauses
version := 1*DIGIT
clauses := clause *(SP clause)
clause := provides | expects | accepts | required | optional | policy

provides := "P(" capability-values ")"
expects := "E(" capability-values ")"
required := "R(" capability-values ")"
optional := "O(" capability-values ")"
accepts := "A(" kvpairs ")"
policy := "Pol(" kvpairs ")"

capability-values := capability-value *("," capability-value)
capability-value := name-token
name-token := 1..64 chars of [a-z0-9-], no edge hyphen, no consecutive hyphen

kvpairs := kv *("," kv)
kv := key "=" value
key := 1*(ALPHA | DIGIT | "-" | "_")
value := 1*(safe-char | escaped-char)
safe-char := ALPHA | DIGIT | "-" | "_" | "." | "/" | ":" | "@"
escaped-char := "\\" ("," | "(" | ")" | "=" | "\\" | " ")

mode := "strict" | "best-effort"
```

Mode default:

- if omitted, mode defaults to `best-effort`.

Escaping rules:

- literal comma -> `\,`
- literal parentheses -> `\(` and `\)`
- literal equals -> `\=`
- literal backslash -> `\\`
- literal space SHOULD be escaped as `\ `.
- parsers MUST split `A(...)` and `Pol(...)` key/value at first unescaped `=`.

Token form policy:

- canonical serialization MUST use short forms: `P E A R O Pol`
- parsers MAY accept long forms (`Provides Expects Accepts Required Optional Policy`) for migration
- accepted long forms MUST be normalized to short forms before validation/matching

Example:

```yaml
compatibility: "copilot,cli"
metadata:
  contract: "DCI/1^strict P(option-evaluation) E(evaluation-criteria) A(output-format=json,output-template=raw) R(web-search) O(critical-thinking) Pol(min-total-score=0.45,on-missing-required=offer-emulation)"
```

## Schema Index

- Alias table: `docs/schemas/dci/aliases.v1.schema.json`
- Reliability state: `docs/schemas/dci/reliability.v1.schema.json`
- Resolution report: `docs/schemas/dci/capability-resolution-report.v1.schema.json`
- Stopword artifact: `docs/schemas/dci/english-stopwords.v1.txt`

## Key Advantages

- keeps fuzzy, prose-first compatibility with existing skills
- adds deterministic, auditable behavior for consumers that need reliability
- supports schema-backed IDE linting and completion
- avoids extra packaging or distribution frameworks

## Key Constraints

- consumer skills still own discovery, enforcement, and policy decisions
- fuzzy mode remains inherently probabilistic
- high-quality behavior depends on provider honesty plus probe/penalty safeguards
