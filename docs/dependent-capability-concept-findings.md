# Dependent Capability Contract Findings (Ordered By Severity)

1. **High: Your optional “well-defined contract” currently conflicts with the Agent Skills core spec.** [**POINT_CONCLUSION: CLOSED**]
`docs/dependent-capability-concept.md:10` and `docs/dependent-capability-concept.md:13` define nested arrays/objects under `metadata`, but Agent Skills spec defines `metadata` as a string→string map, and validation is tied to `skills-ref validate`.  
Impact: breaks interoperability and undermines your “low-friction migration” claim.  
Refs: <https://agentskills.io/specification>, <https://agentskills.io/integrate-skills>

2. **High: “SEO-style discovery” is underspecified and therefore unreliable at runtime.** [**POINT_CONCLUSION: CLOSED**]
`docs/dependent-capability-concept.md:6` has no normative scoring function, tokenization rules, conflict resolution, or deterministic tie-breakers.  
Impact: high false positives/negatives, prompt-stuffing vulnerability, inconsistent provider selection between runs.

3. **High: Capability semantics are not operationally testable.**  
`docs/dependent-capability-concept.md:25`, `docs/dependent-capability-concept.md:27`, `docs/dependent-capability-concept.md:29` use ambiguous capabilities (`<reasoning level>`, `critical thinking`) with no probes or conformance tests.  
Impact: “dependency satisfied” can’t be verified; quality gating becomes subjective.

4. **Medium: Failure-policy semantics are incomplete and can silently degrade outcomes.**  
`docs/dependent-capability-concept.md:31` and `docs/dependent-capability-concept.md:47` mention emulation/hard-fail but do not define default behavior, user consent requirements, or audit trace requirements.  
Impact: hidden fail-open behavior and hard-to-debug regressions.

5. **Medium: The YAML example is syntactically/structurally ambiguous for machine parsing.**  
`docs/dependent-capability-concept.md:20` through `docs/dependent-capability-concept.md:24` (`accepts`) mixes list and keyed defaults in a way most parsers won’t interpret as intended.  
Impact: implementation divergence and incompatible parsers.

6. **Medium: Adoption claims are overstated without compatibility profile + reference implementation.**  
`docs/dependent-capability-concept.md:40` and `docs/dependent-capability-concept.md:42` claim ecosystem compatibility and dependency-management resolution, but no conformance suite, resolver reference, or governance path is defined.  
Impact: low trust from maintainers/platform integrators.

7. **Low: No versioning or compatibility negotiation model.**  
No contract version field or negotiation protocol exists.  
Impact: breaking changes likely as capability vocabulary evolves.

---

## Scorecard

1. **Feasibility:** **6/10** (prototype feasible, standardization not yet).  
2. **Reliability:** **3/10** as written (too much semantic ambiguity).  
3. **Determinism:** **2/10** as written (explicitly non-deterministic, no strict mode).  
4. **Community adoption likelihood:** **4/10** now; **7/10** if you add a compatibility profile, resolver reference, and conformance tests.

---

## Key Considerations Missing For Success

1. A **two-mode contract**: `best-effort` (fuzzy) vs `strict` (deterministic, fail-closed).  
2. A **controlled capability vocabulary** (canonical ids + aliases + deprecations).  
3. **Capability verification probes** (self-test tasks per capability).  
4. **Resolver transparency artifact** (`capability_resolution_report.json`) per run.  
5. **Security model** for provider trust, allowlists, and provenance.  
6. **Drift controls** (pin selected provider and resolver version per run).  
7. **Benchmark dataset** for discovery precision/recall and routing quality.  
8. **Governance path** (proposal lifecycle, compatibility guarantees, migration policy).

---

## Concrete Next Steps To Reach Agent Skill Spec-Level Rigor

1. Publish a v0.1 RFC with normative language (`MUST/SHOULD/MAY`) and explicit non-goals.  
2. Define a **spec-compatible metadata profile** (string-only keys/values) plus optional sidecar contract file for richer structure.  
3. Release a reference resolver CLI/library with deterministic mode, seeded ranking, and full trace output.  
4. Create a conformance test suite: discovery accuracy, fallback behavior, hard-fail behavior, and adversarial metadata cases.  
5. Add telemetry KPIs: match precision, fallback rate, emulation success rate, user override rate.  
6. Pilot with 3-5 real consumer/provider skill pairs and publish failure analyses.  
7. Draft a formal extension proposal for Agent Skills after pilot evidence, not before.

---

## Sources

- <https://agentskills.io/specification>  
- <https://agentskills.io/integrate-skills>  
- <https://github.com/agentskills/agentskills>

__

## Resolution Conversation Protocol

1. I present one point only: claim, evidence, risk, and concrete fix.
2. You respond with one of:
   - `ACCEPT`
   - `CHALLENGE: <reason>`
   - `REVISE: <change you want>`
3. I either revise or defend once.
4. I emit a definitive marker:
   - `POINT_CONCLUSION: CLOSED` (we move to next point)
   - `POINT_CONCLUSION: OPEN` (we stay on this point)

Advance rule: we only move forward after `POINT_CONCLUSION: CLOSED`.
