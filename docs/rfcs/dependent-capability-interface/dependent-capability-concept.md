# Dependent Capability Contract

## Interface Specification

### Contract Declaration Modes

#### Fuzzy

- `provider` skills declare capabilities using `description` prose and optional runtime metadata.
- `consumer` skills discover candidate providers from installed and accessible skills.

#### Well-defined

- skills MAY declare a machine-readable `metadata.contract` string using the [DCI grammar](#dependent-capability-interface-dci-grammar).
- well-defined contracts improve matching precision, policy enforcement, and reproducibility.

### Discovery and Selection Protocol (Applies to Fuzzy and Well-defined)

> [!NOTE]
> This protocol is weighted, not sequentially required. Exact capability matching is not mandatory, but higher-confidence signals are weighted more heavily.

#### Protocol Summary

1. Discover candidates from deterministic sources.
2. Parse and validate contract clauses when present.
3. Score candidates (`S_contract`, `S_desc`, `S_namepath`, `S_runtime`), then apply penalties and history multiplier.
4. Apply effective policy gates and selection mode (`single` or `cover`).
5. Resolve ties deterministically.
6. Apply `on-missing-required` behavior when coverage is insufficient.
7. Emit `capability_resolution_report`.

#### Specification Language and Conformance

- Normative keywords (`MUST`, `SHOULD`, `MAY`) are interpreted per RFC 2119 / RFC 8174.
- Grammar is expressed in EBNF for readability; a future revision MAY publish ABNF for stricter parser interoperability.

#### Definitions

- **`query capabilities`**: capability identifiers the consumer requires for the current run.
- **`contract token`**: an atomic value from `P(...)`, `E(...)`, `A(...)`, `R(...)`, `O(...)`, `D(...)`, `Rt(...)`, `M(...)`, or `Pol(...)`.
- **`candidate`**: one installed and accessible skill under evaluation.
- **`host runtime`**: current execution runtime identifier (for example `copilot`, `cli`, `opencode`).

#### Accepted Clause Tokens

- `P(...)` / `Provides(...)`: capabilities a provider offers.
- `E(...)` / `Expects(...)`: required input assumptions from caller/context.
- `A(...)` / `Accepts(...)`: accepted key/value configuration parameters.
- `R(...)` / `Requires(...)`: required dependent capabilities to fulfill behavior.
- `O(...)` / `Optional(...)`: optional dependent capabilities.
- `D(...)` / `Denies(...)`: denied dependent capabilities that MUST NOT be introduced by selected providers.
- `Rt(...)` / `Runtime(...)`: structured runtime compatibility declarations.
- `M(...)` / `Model(...)`: structured model compatibility declarations.
- `Pol(...)` / `Policy(...)`: policy override hints and thresholds.

Long-form naming policy:

- canonical long-form identifiers MUST use standardized forms:
  - `Provides`, `Expects`, `Accepts`, `Requires`, `Optional`, `Denies`, `Runtime`, `Model`, `Policy`.
- all accepted long forms MUST normalize to short forms before validation/matching.

#### Token Navigation Map

- Capability tokens (`P/E/R/O/D`):
  - [Capability Token Validation](#capability-token-validation-and-normalization)
  - [Scoring Components](#scoring-components-00-to-10)
  - [Deterministic Tie-Breakers](#deterministic-tie-breakers-ordered)
- Accepts token (`A`):
  - [Dependent Capability Interface (DCI) Grammar](#dependent-capability-interface-dci-grammar)
  - [Allowed override keys in `Pol(...)`](#allowed-override-keys-in-pol)
- Runtime token (`Rt`):
  - [Runtime Compatibility Determination](#runtime-compatibility-determination)
  - [Dependent Capability Interface (DCI) Grammar](#dependent-capability-interface-dci-grammar)
- Model token (`M`):
  - [Model Compatibility Determination](#model-compatibility-determination)
  - [Dependent Capability Interface (DCI) Grammar](#dependent-capability-interface-dci-grammar)
- Policy token (`Pol`):
  - [DependentPolicy Defaults and Overrides](#dependentpolicy-defaults-and-overrides)
  - [On-Missing-Required Semantics](#on-missing-required-semantics)
  - [Provider policy hints](#provider-policy-hints)

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

#### Capability Token Validation and Normalization

Capability vocabulary is intentionally open in DCI/1. There is no global closed enum for capability values.
Interoperability is achieved by local convention, alias tables, and deterministic scoring/probing.

Agent Skill naming convention alignment:

- provider capability tokens SHOULD align with the Agent Skill `name`-field style
  (`lowercase`, `kebab-case`, no whitespace) to improve cross-skill discoverability.
- consumers MUST treat this as an interoperability preference, not a hard validity boundary, unless explicitly overridden by runtime policy.
- reference: [Agent Skill `name` field](https://agentskills.io/specification#name-field)

Capability tokens in `P/E/R/O/D` MUST conform to this syntactic profile:

- length 1..128
- allowed characters: alphanumeric, hyphen, underscore, dot, slash, colon
- MUST start and end with an alphanumeric character
- MUST NOT contain whitespace

Validation behavior:

- parser MUST decode DCI escapes and trim surrounding whitespace for all clause tokens.
- parser MUST normalize accepted long-form clause identifiers to short forms before validation/matching.
- mode-specific value normalization:
  - `strict`:
    - token-value comparison is case-sensitive.
    - parser MUST NOT lowercase or otherwise rewrite token values.
  - `best-effort`:
    - parser SHOULD lowercase identifier token values in `P/E/R/O/D/Rt/M` and keys in `A/Pol` after trimming.
    - parser MUST preserve `A/Pol` values as-is (no lowercasing).
- if an identifier token fails validation:
  - `strict`: treat as unresolved.
  - `best-effort`: keep candidate and apply `invalid_token_penalty`.

Penalty definition:

- `invalid_token_penalty = min(0.20, 0.02 * invalid_token_count_per_candidate)`.

Invalid token definitions:

- invalid capability token:
  - any value in `P/E/R/O/D/Rt` that violates capability-token constraints.
- invalid model token:
  - any value in `M` that violates model-pattern constraints.
- invalid key token:
  - any key in `A/Pol` that violates `key := 1*(ALPHA | DIGIT | "-" | "_")`.
- unknown clause identifier:
  - any clause with an unknown identifier, for example `X(...)`, not recognized by the grammar (or accepted long-form aliases).

Unknown clause identifier behavior:

- `strict`: candidate contract parsing fails; candidate is treated as unresolved for contract-based matching.
- `best-effort`: unknown clause identifiers are ignored and `unknown_clause_penalty` is applied.
- `unknown_clause_penalty = min(0.20, 0.05 * unknown_clause_identifier_count_per_candidate)`.

#### Alias Table Governance

Alias resolution supports interoperability without special-case normalization.

- alias table format: `canonical-token -> aliases[]`.
- canonical and alias tokens MUST each pass capability-token validation.
- alias matching MUST follow the same mode-specific value normalization rules defined in
  [Capability Token Validation and Normalization](#capability-token-validation-and-normalization).
  - `strict`: exact value comparison after escape decoding + trim.
  - `best-effort`: lowercase identifier-token values before lookup and comparison.
- alias resolution precedence:
  1. runtime/user-provided alias table
  2. workspace alias table (`.dci/aliases.v1.json`)
  3. built-in alias table
- within a single table, canonical exact match wins before alias match.
- alias tables MUST declare `alias_table_version`; this version MUST be part of cache keys.
- alias cycles MUST be flattened to canonical key at load time.
- trust and integrity:
  - runtime/workspace alias tables can influence ranking and MUST be treated as trusted configuration only.
  - `strict` mode SHOULD default to built-in aliases unless runtime/user explicitly opts in external alias tables.
  - report MUST include alias source and alias table version used for the run.

##### Schema

- `docs/rfcs/dependent-capability-interface/schemas/dci/aliases.v1.schema.json`

#### Runtime Compatibility Determination

##### Runtime compatibility uses a hybrid model

- legacy/prose source: top-level `compatibility` in skill frontmatter.
- structured complement: optional `Rt(...)` / `Runtime(...)` contract clause.

This preserves low-friction adoption: legacy skills do not need to add new fields, and structured declaration remains opt-in.

##### Semantics

- `Rt(...)` declares an admissible runtime set (disjunctive OR semantics).
- runtime compatibility is satisfied when host runtime matches any declared runtime identifier.

##### Rules

- parse `Rt(...)` as structured runtime identifiers using the same capability-token constraints.
- parse `compatibility` as comma-delimited runtime prose identifiers.
- precedence for provider runtime declaration:
  1. `Rt(...)` / `Runtime(...)` (structured)
  2. top-level `compatibility` (legacy prose)
  3. runtime-agnostic default (when neither is present)
- if both `Rt(...)` and `compatibility` are present and differ:
  - `strict`: use `Rt(...)` and record mismatch warning in run artifact.
  - `best-effort`: use `Rt(...)` and record mismatch warning in run artifact.
- if `Rt(...)` is absent or invalid in `best-effort`, use top-level `compatibility`.
- token `*` means runtime-agnostic in either source.
- token `all` MUST be accepted as an alias of `*`.
- unknown compatibility tokens MUST be ignored and logged in the run artifact.
- `S_rt = 1.0` when candidate is runtime-agnostic or host runtime is listed; otherwise `0.0`.
- in `strict` mode, runtime-incompatible candidates MUST be filtered out before final selection.

#### Model Compatibility Determination

##### Model compatibility uses a structured model clause

- source: optional `M(...)` / `Model(...)` contract clause.

##### Semantics

- `M(...)` declares an admissible model set (disjunctive OR semantics).
- model compatibility is satisfied when host model identifier matches any declared model pattern.
- `M` supports exact model identifiers and prefix wildcard patterns using a trailing `*`.
  - example exact: `M(openai/gpt-5.1)`
  - example prefix wildcard: `M(openai/gpt-5*)`
- wildcard scope:
  - only suffix `*` is valid.
  - interior `*` and `?` are invalid model tokens.
  - bare `all` is reserved as an alias of `*` (model-agnostic).

##### Rules

- parse `M(...)` values using this model-pattern grammar:
  - `model-pattern := model-token ["*"]`
  - `model-token := 1*(ALPHA | DIGIT | "-" | "_" | "." | "/" | ":" | "@")`
- comparisons MUST follow mode-specific normalization rules defined above.
- if `M(...)` is absent, candidate is model-agnostic.
- token `*` in `M(...)` means model-agnostic.
- token `all` in `M(...)` MUST be accepted as an alias of `*`.
- unknown model patterns MUST be ignored and logged in run artifact in `best-effort`.
- in `strict` mode, model-incompatible candidates MUST be filtered out before final selection.
- `S_model = 1.0` when candidate is model-agnostic or host model matches any `M(...)` pattern; otherwise `0.0`.

#### Scoring Components (`0.0` to `1.0`)

- `S_contract`: capability fit between query capabilities and candidate contract capabilities.
  - for candidates without `metadata.contract` (see [Fuzzy Declaration Mode]):
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
      - this is NOT equivalent to a single regex word-boundary (`\\w`) split because `_`, `-`, and `/` are explicit segment boundaries here
    - remove fixed english stopword set from `docs/rfcs/dependent-capability-interface/schemas/dci/english-stopwords.v1.txt` by exact-token match after tokenization/lowercasing
    - Porter stemming
  - scorer:
    - BM25 with `k1=1.2`, `b=0.75` (chosen to align with common IR defaults, maximizing portability)
    - normalize: `S_desc = bm25_i / max_bm25`
    - if `max_bm25 = 0`, set `S_desc = 0.0` (for example: empty candidate corpus, or all scores are zero due to no lexical overlap).

- `S_namepath`: lexical overlap between query tokens and `(skill-name + skill-path)` tokens.
  - same tokenizer as `S_desc`.
  - `S_namepath = |Q ∩ N| / |Q ∪ N|` (Jaccard).
  - if `|Q ∪ N| = 0`, set `S_namepath = 0.0`.

- `S_runtime`: environment compatibility score.
  - `S_runtime = min(S_rt, S_model)`.
  - `S_rt` and `S_model` are defined in runtime/model sections above.

##### Composite

```text
S_total = 0.60*S_contract + 0.20*S_desc + 0.10*S_namepath + 0.10*S_runtime
```

##### Penalty and final score

1. Compute `S_total`.
2. Compute penalties:
   - `invalid_token_penalty`
   - `unknown_clause_penalty`
   - `overclaim_penalty`
   - `inflation_penalty` (if applicable)
   - `require_deny_penalty` (if applicable)
3. `penalties = invalid_token_penalty + unknown_clause_penalty + overclaim_penalty + inflation_penalty + require_deny_penalty`.
4. `S_total_penalized = max(0.0, S_total - penalties)`.
5. `S_total_final = S_total_penalized * history_multiplier`.

#### DependentPolicy Defaults and Overrides

##### Defaults

- `MinTotalScore=0.45`
- `MinContractScore=0.30`
- `MinRequiredCoverage=1.00` in `strict`, `0.60` in `best-effort`
- `MaxCandidates=5`
- `SelectionMode=single` (`single | cover`)
- `MaxProviders=3` (used only when `SelectionMode=cover`)
- `MaxDependencyDepth=2`
- `OnMissingRequired=hard-fail` in `strict`, `offer-emulation` in `best-effort`

##### Allowed override keys in `Pol(...)`

- `min-total-score`
- `min-contract-score`
- `min-required-coverage`
- `max-candidates`
- `selection-mode` (`single | cover`)
- `max-providers` (integer >= 1)
- `max-dependency-depth` (integer >= 0)
- `on-missing-required` (`hard-fail | offer-emulation | auto-emulate`)

##### Override key definitions

- `min-total-score`:
  - numeric `[0.0, 1.0]`; minimum `S_total_final` allowed after penalties/history.
- `min-contract-score`:
  - numeric `[0.0, 1.0]`; minimum `S_contract` before candidate is rejected.
- `min-required-coverage`:
  - numeric `[0.0, 1.0]`; minimum resolved required-capability ratio.
- `max-candidates`:
  - integer `>= 1`; maximum number of ranked candidates retained before final selection.
- `selection-mode`:
  - `single | cover`; single-provider pick or multi-provider set cover.
- `max-providers`:
  - integer `>= 1`; max selected providers when `selection-mode=cover`.
- `max-dependency-depth`:
  - integer `>= 0`; dependency traversal bound used for transitive require-deny conflict detection.
- `on-missing-required`:
  - `hard-fail | offer-emulation | auto-emulate`; behavior when unresolved required capabilities remain.

##### Precedence

1. runtime/user override
2. consumer `Pol(...)`
3. provider hints (tightening-only)
4. defaults

##### Provider policy hints

- provider hints are advisory and MUST NOT relax effective policy.
- provider hints MAY only tighten policy:
  - increase minimum thresholds
  - decrease `max-candidates`
  - move `on-missing-required` to stricter values only
- strictness ordering: `hard-fail > offer-emulation > auto-emulate`.

##### Selection gates

- reject candidate when `S_total_final < MinTotalScore`.
- reject candidate when `S_contract < MinContractScore`.
- reject candidate when required coverage `< MinRequiredCoverage`.
- retain top `MaxCandidates` by `S_total_final` before final tie-break.

##### Selection cardinality

- `SelectionMode=single`: choose one top-ranked candidate.
- `SelectionMode=cover`: choose a provider set that covers required capabilities.
  - use greedy set-cover tie-broken by `S_total_final`.
  - stop when all required capabilities are covered or `MaxProviders` reached.
  - if uncovered capabilities remain, apply `on-missing-required` policy.

#### Require-Deny Conflict Semantics

`D(...)` provides explicit denylist behavior for dependency compatibility checks.

- `R_eff`: effective required capability set across the traversed dependency graph.
- `D_eff`: effective denied capability set across the traversed dependency graph.
- `require_deny_conflicts = R_eff ∩ D_eff`.

Traversal and determinism rules:

- traversal MUST use the selected dependency graph (consumer root plus selected providers).
- traversal MUST be breadth-first and deterministic by canonical candidate id order.
- traversal depth MUST be bounded by `MaxDependencyDepth`.
  - depth `0`: consumer
  - depth `1`: directly selected providers
  - depth `N`: providers selected to satisfy depth `N-1` provider requirements
- resolver MUST stop revisiting nodes already seen (cycle-safe).

Evaluation rules:

- `strict`:
  - if `require_deny_conflicts` is non-empty, selection MUST fail with `on-missing-required=hard-fail` behavior.
- `best-effort`:
  - candidate set MAY continue, but each require-deny conflict MUST be treated as unresolved required.
  - apply `require_deny_penalty = min(0.25, 0.05 * count(require_deny_conflicts))`.

Example (direct conflict):

- consumer requires `R(web-search)`.
- selected provider declares `D(web-search)`.
- result: `require_deny_conflicts={web-search}`.

Example (transitive conflict):

- consumer `c1` requires `R(tool-x,tool-y)`
- `c1` selects provider `p1` for `P(tool-y)`
- `p1` requires `R(tool-z)`.
- `p1` selects provider `p2` for `P(tool-z)`.
- `p2` denies `D(tool-x)`.
- result: `require_deny_conflicts={tool-x}` because conflict is detected within bounded transitive traversal.

#### Transitive Dependency Resolution, Caching, and Context Mutation Policy

Transitive dependency resolution MUST be deterministic and context-scoped.

##### Normative algorithm

1. Initialize BFS queue with selected depth-1 providers and root context:
   - `context.required = consumer.R`
   - `context.denied = consumer.D`
2. For each queue item `(provider_instance, depth, context)`:
   - parse provider contract (`R_local`, `D_local`, `P_local`).
   - compute:
     - `R_path = context.required ∪ R_local`
     - `D_path = context.denied ∪ D_local`
     - `require_deny_conflicts_path = R_path ∩ D_path`
   - record path conflicts to run artifact.
   - if `depth == MaxDependencyDepth`, stop expansion for this path.
   - otherwise, resolve provider-local requirements (`R_local`) using the same candidate scoring/gating pipeline and current effective policy.
   - enqueue selected child providers with `depth+1` and inherited context:
     - `context.required = R_path`
     - `context.denied = D_path`
3. Aggregate across all traversed paths:
   - `R_eff = union(all R_path)`
   - `D_eff = union(all D_path)`
   - `require_deny_conflicts = R_eff ∩ D_eff`
4. Apply strict/best-effort handling from [Require-Deny Conflict Semantics](#require-deny-conflict-semantics).

##### Context-scoped dependency mutation policy

- dependency selection is immutable within a single resolved provider instance.
- provider instances are context-scoped, not globally singleton by provider id.
- the same provider candidate MAY appear multiple times in one run with different child graphs when parent contexts differ.
- context identity MUST include at least:
  - provider candidate id
  - mode (`strict` or `best-effort`)
  - effective policy hash
  - inherited required-set hash
  - inherited deny-set hash
  - host runtime/model signatures

##### Resolved dependency caching

- caching SHOULD be used and MUST preserve semantic equivalence.
- cache entries MUST be keyed by context identity; reusing cache across different context hashes is forbidden.
- minimum transitive cache key fields:
  - `dci_version`
  - `provider_candidate_id`
  - `mode`
  - `effective_policy_hash`
  - `required_set_hash`
  - `deny_set_hash`
  - `host_runtime`
  - `host_model`
  - `max_dependency_depth`
  - `alias_table_version`
- cached value MUST include selected child provider ids and path conflict summary.
- cache invalidation MUST occur when any key component changes.

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
2. higher weighted required-capability coverage quality (`exact > alias > fuzzy`)
3. fewer hard-unresolved required capabilities (`match_score = 0.0`)
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

R_eff, D_eff = collect_effective_requirements_and_denies(
  consumer, selected, effective_policy.max_dependency_depth
)
require_deny_conflicts = intersect(R_eff, D_eff)
if require_deny_conflicts is not empty:
  if mode == "strict":
    fail_with_require_deny_conflicts(require_deny_conflicts)
  else:
    mark_unresolved_required(require_deny_conflicts)
    apply require_deny_penalty

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
- report linkage:
  - report and reliability state remain separate artifacts; linkage is by source metadata + candidate snapshots.
  - report MUST include top-level reliability source metadata (`mode`, `path`, `schema_version`, `updated_at`).
  - report MUST include per-candidate reliability snapshot used for scoring.
  - per-candidate snapshot MUST include `success_rate_last_20`, `sample_size`, and `outcomes_last_20`.

##### Schema

- `docs/rfcs/dependent-capability-interface/schemas/dci/reliability.v1.schema.json`

#### Required Run Artifact

consumer MUST emit `capability_resolution_report` for each run.

##### Minimum fields per candidate

- `S_contract`
- `S_desc`
- `S_namepath`
- `S_runtime`
- `S_total`
- penalties.`unknown_clause_penalty` (when applicable)
- penalties.`require_deny_penalty` (when applicable)
- `history_multiplier`
- `S_total_final`
- tie-breaker details and applied step (if used)
- reliability_snapshot.`sample_size`
- reliability_snapshot.`success_rate_last_20`
- reliability_snapshot.`outcomes_last_20`
- require_deny_conflicts.`capability` (when present)
- require_deny_conflicts.`required_by_candidate_id` (when present)
- require_deny_conflicts.`denied_by_candidate_id` (when present)
- require_deny_conflicts.`required_depth` (when present)
- require_deny_conflicts.`denied_depth` (when present)

##### Required top-level fields

- discovery sources scanned and inclusion/exclusion counts
- alias table source and alias table version used
- effective `selection-mode` and provider count limit
- effective `max-dependency-depth`
- reliability source metadata (`mode`, `path`, `schema_version`, `updated_at`)
- unresolved required capabilities (if any)
- unresolved require-deny conflicts (if any)
- `on-missing-required` action taken
- `degraded_mode` flag and emulated capabilities (when applicable)
- user decision record for `offer-emulation` (when applicable)

##### Schema

- `docs/rfcs/dependent-capability-interface/schemas/dci/capability-resolution-report.v1.schema.json`

### Dependent Capability Interface (DCI) Grammar

```ebnf
contract := "DCI/" version [ "^" mode ] SP clauses
version := 1*DIGIT
clauses := clause *(SP clause)
clause := provide | expect | accept | require | optional | deny | runtime | model | policy

provide := "P(" capability-values ")"
expect := "E(" capability-values ")"
require := "R(" capability-values ")"
optional := "O(" capability-values ")"
deny := "D(" capability-values ")"
accept := "A(" kvpairs ")"
runtime := "Rt(" runtime-values ")"
model := "M(" model-values ")"
policy := "Pol(" kvpairs ")"

runtime-values := runtime-value *("," runtime-value)
runtime-value := capability-token | "*"

model-values := model-value *("," model-value)
model-value := model-pattern
model-pattern := model-token ["*"] | "*"
model-token := 1*(ALPHA | DIGIT | "-" | "_" | "." | "/" | ":" | "@")

capability-values := capability-value *("," capability-value)
capability-value := capability-token
capability-token := capability-part *(capability-sep capability-part)
capability-part := 1*(ALPHA | DIGIT)
capability-sep := "-" | "_" | "." | "/" | ":"

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
- literal space SHOULD be escaped as `\`.
- parsers MUST split `A(...)` and `Pol(...)` key/value at first unescaped `=`.

Token form policy:

- canonical serialization MUST use short forms: `P E A R O D Rt M Pol`
- parsers MUST accept canonical long forms (`Provides Expects Accepts Requires Optional Denies Runtime Model Policy`)
- accepted long forms MUST be normalized to short forms before validation/matching

Example:

```yaml
compatibility: "copilot,cli"
metadata:
  contract: "DCI/1^strict P(option-evaluation) E(evaluation-criteria) A(output-format=json,output-template=raw) R(web-search) O(critical-thinking) Rt(copilot,cli) M(openai/gpt-5*) Pol(min-total-score=0.45,on-missing-required=offer-emulation)"
```

## Schema Index

- Alias table: `docs/rfcs/dependent-capability-interface/schemas/dci/aliases.v1.schema.json`
- Reliability state: `docs/rfcs/dependent-capability-interface/schemas/dci/reliability.v1.schema.json`
- Resolution report: `docs/rfcs/dependent-capability-interface/schemas/dci/capability-resolution-report.v1.schema.json`
- Stopword artifact: `docs/rfcs/dependent-capability-interface/schemas/dci/english-stopwords.v1.txt`

## Key Advantages

- keeps fuzzy, prose-first compatibility with existing skills
- adds deterministic, auditable behavior for consumers that need reliability
- supports schema-backed IDE linting and completion
- avoids extra packaging or distribution frameworks

## Key Constraints

- consumer skills still own discovery, enforcement, and policy decisions
- fuzzy mode remains inherently probabilistic
- high-quality behavior depends on provider honesty plus probe/penalty safeguards
- external agreement attestation mechanisms (for example `agreement_ref`, `published_doc`, third-party compliance assertions) are intentionally out of scope for DCI/1

[Fuzzy Declaration Mode]: #fuzzy "Fuzzy Declaration Mode"
