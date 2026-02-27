# Dependent Capability Contract Findings (Rebaselined, Ordered By Severity)

1. **High (resolved): Capability semantics are codified in the RFC draft.** [**POINT_CONCLUSION: CLOSED**]  
   Codified in `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:101`, `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:375`, and `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:642`: open capability domain, canonical `D(...)` deny clause, deterministic `require_deny_conflicts` semantics (`require_deny_conflicts = R_eff ∩ D_eff`) including transitive dependency contexts with bounded traversal, and explicit v1 out-of-scope for external agreement attestations.

2. **Medium: Malicious-skill risk mitigation is not yet specified as a first-class model.** [**POINT_CONCLUSION: OPEN**]  
   `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:533` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:559` include manipulation resistance and probes, but there is no normative threat model, trust boundary language, or mandatory runtime controls (allowlists/provenance/sandbox constraints).  
   Impact: `D(...)`/scoring/probes can mitigate declared conflicts, but undeclared malicious behavior remains insufficiently addressed.

3. **Medium: Transitive dependency resolution requires implementation-grade validation.** [**POINT_CONCLUSION: OPEN**]  
   `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:414` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:470` now specify deterministic traversal, context-scoped provider instances, and cache-key requirements, but there is no reference resolver or conformance corpus proving cross-runtime consistency.  
   Impact: different runtimes may still diverge on deep dependency resolution and cache reuse behavior.

4. **Low: Canonical long-form clause naming is defined, but parser conformance remains unproven.** [**POINT_CONCLUSION: OPEN**]  
   `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:44` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:63` and `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:689` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:691` define canonical long-form identifiers and mandatory normalization, but runtime parser conformance is still unproven.  
   Impact: implementations may diverge on canonical long-form parsing behavior without explicit conformance fixtures.

5. **Medium: Adoption claims remain ahead of implementation/governance evidence.** [**POINT_CONCLUSION: OPEN**]  
   `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:710` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:715` assert strong compatibility/adoption outcomes, but the spec still lacks a reference resolver implementation, conformance suite, and proposal governance workflow in-repo.  
   Impact: maintainers and integrators may treat the spec as promising but not yet production-verifiable.

6. **Low: Versioning exists, but compatibility negotiation is still undefined.** [**POINT_CONCLUSION: OPEN**]  
   `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:637` defines a versioned contract (`DCI/<version>`), but there is no sender/consumer negotiation or downgrade behavior for incompatible versions.  
   Impact: future version drift risks fragmented behavior across runtimes.

7. **Resolved: Core Agent Skills metadata compatibility conflict has been removed.** [**POINT_CONCLUSION: CLOSED**]  
   `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:14` uses a string-valued `metadata.contract`, which is consistent with string-string metadata constraints.

8. **Resolved: Discovery and selection are now normatively specified and deterministic.** [**POINT_CONCLUSION: CLOSED**]  
   Deterministic discovery scope and inclusion rules are defined at `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:84` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:97`; scoring and tie-breakers are defined at `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:236` and `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:479`.

9. **Resolved: Failure-policy semantics now include explicit defaults, consent, and audit artifacts.** [**POINT_CONCLUSION: CLOSED**]  
   Defaults and policy behavior are defined at `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:296` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:305`; missing-required behaviors and user consent are specified at `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:467` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:477`; report requirements are specified at `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:587` to `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:626`.

10. **Resolved: Machine parsing ambiguity in the old YAML-style example has been removed.** [**POINT_CONCLUSION: CLOSED**]  
    The example is now a single canonical contract string at `docs/rfcs/dependent-capability-interface/dependent-capability-concept.md:691`, avoiding mixed list/map structures.

11. **High: Interface-vs-capability model choice is unresolved and must be decided before further draft refinement.** [**POINT_CONCLUSION: OPEN**]  
    Evidence: The draft already supports “well-defined” contracts via DCI grammar and uses them for discovery/selection, but the working PR tool interface shows a fixed-operation contract with explicit parameters and workflows. See the DCI “Well-defined” contract and discovery protocol in [docs/rfcs/dependent-capability-interface/dependent-capability-concept.md](dependent-capability-concept.md) and the concrete interface contract in [skills/tools/PR_MANAGEMENT_INTERFACE.md](../../../skills/tools/PR_MANAGEMENT_INTERFACE.md).  
    Impact: Without deciding how interfaces relate to capabilities, the draft may optimize the wrong abstraction or under-specify deterministic integration.

Options (most to least disruptive):

1. Replace the capability model with explicit interface contracts (DCI becomes the interface grammar).
2. Treat interfaces as DCIv2 (new grammar + resolver path; DCIv1 remains as-is).
3. Split interfaces into a separate RFC with a bridging adapter to DCI selection.
4. Define interfaces as a structured, restrictive capability subtype with deterministic parameter/operation schemas.
5. Define interfaces as a well-defined grouping/aliasing layer for capabilities (interface = named bundle of `P/E/R/O/D`).
6. Keep capabilities as primary and allow optional interface metadata for documentation only (no selection impact).
7. Disregard interfaces as out of scope for DCI and document the exclusion explicitly.

---

## Rebaselined Scorecard

1. **Feasibility:** **8/10** (spec is implementable with clear deterministic core).
2. **Reliability:** **6/10** (good resolver mechanics; capability verification still underdefined).
3. **Determinism:** **6/10** (selection path is deterministic; conformance/probe semantics remain partial).
4. **Community adoption likelihood:** **5/10** now; **8/10** with reference resolver + conformance suite + governance path.

---

## Critical Gaps Remaining For Success

1. **Malicious-skill mitigation model:** threat model, trust boundaries, and mandatory runtime controls.
2. **Probe conformance layer:** normative schema for probes and pass/fail recording per capability.
3. **Transitive resolver conformance:** deterministic graph expansion, context-scoped cache behavior, and conflict handling fixtures.
4. **Long-form clause conformance:** canonical long-form clause parsing and normalization behavior across runtimes.
5. **Reference resolver + fixtures:** reproducible implementation and adversarial test corpus.
6. **Version negotiation model:** compatible/incompatible behavior across DCI versions.
7. **Governance path:** proposal lifecycle, compatibility guarantees, and migration policy.

---

## Concrete Next Steps

1. Add a security section for malicious-skill threat model and trust boundaries (`D(...)` is policy, not a security boundary).
2. Add `probes.v1.schema.json` and require probe result reporting per required capability in strict mode.
3. Add transitive dependency test fixtures (shared provider, divergent parent deny sets, depth limits, cycles, cache-key isolation).
4. Add clause-name conformance fixtures for canonical long-form identifiers and normalization behavior.
5. Publish a minimal reference resolver CLI/library aligned with the current scoring/tie-break spec.
6. Create a conformance test suite (positive, negative, adversarial metadata, and version-compat cases).
7. Define explicit DCI version negotiation and downgrade/fail behavior.

---

## Sources

- <https://agentskills.io/specification>
- <https://agentskills.io/integrate-skills>
- <https://github.com/agentskills/agentskills>
