---
name: write-technical-rfc
description: Create, revise, and maintain IETF-style Internet-Drafts and RFC-like technical specifications for protocols, APIs, interoperability contracts, and system behavior. Use when drafting a new spec, updating an existing draft, resolving review feedback, validating RFC 2119/8174 requirement language, or ensuring mandatory sections such as Security Considerations, IANA Considerations, and References are complete and consistent.
---

# Write Technical RFC

Produce clear, testable, and maintainable IETF-style specifications.
Preserve the repository's existing document format unless asked to migrate it.

## 1) Set Document Context

- Determine document mode: `new-draft`, `revision`, or `comment-resolution`.
- Determine target stream/maturity: `Standards Track`, `BCP`, `Informational`, `Experimental`, or `internal RFC-style`.
- Determine source format and preserve it: `markdown`, `xml2rfc`, or plain text.
- Refuse to invent publication metadata. Never fabricate RFC numbers, IANA assignments, working group consensus, or implementation claims.
- Record explicit assumptions when critical inputs are missing.

Collect or infer these minimum inputs before drafting:

- Problem statement and scope boundaries.
- Audience and interoperability goals.
- Protocol entities, message flows, and state transitions.
- Data model and wire-format constraints.
- Backward compatibility expectations.
- Security and privacy threat model.
- Deployment and operational constraints.
- Open questions and non-goals.

## 2) Build the RFC Structure

Use this section order unless the project already defines a required structure:

1. Title
2. Abstract
3. Status of This Memo
4. Copyright Notice
5. Introduction
6. Conventions and Terminology
7. Problem Statement, Goals, and Non-Goals
8. Protocol Overview
9. Detailed Specification
10. Error Handling
11. Operational Considerations
12. Security Considerations
13. Privacy Considerations (when applicable)
14. IANA Considerations
15. Backward Compatibility and Deployment
16. References
17. Appendices (examples, rationale, change log)

Apply these section rules:

- Keep `Security Considerations` and `IANA Considerations` in every draft.
- Write explicit `No IANA actions are required.` when no registry action exists.
- Split references into `Normative` and `Informative` subsections.
- Move long examples into appendices when they are non-normative.

## 3) Write Normative Requirements Correctly

- Use BCP 14 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) only for enforceable requirements.
- Add a BCP 14 boilerplate statement in `Conventions and Terminology`.
- Write each normative requirement so it is testable:
  - actor (`client`, `server`, `implementation`)
  - required behavior
  - condition/scope
  - error behavior when violated
- Avoid mixed-strength requirements in one sentence unless scoped with explicit conditions.
- Use lowercase prose for descriptive text that is not normative.

## 4) Maintain Technical Precision

- Define protocol terms once and reuse exact terms consistently.
- Specify defaults, limits, and units for all configurable values.
- Specify failure modes, retry behavior, timeout behavior, and idempotency where relevant.
- Include at least one end-to-end flow description for each major operation.
- Include wire examples or structured payload examples for complex exchanges.
- Prefer unambiguous language over motivational prose.

## 5) Handle Security, Privacy, and IANA Thoroughly

Security:

- Enumerate realistic threats (spoofing, tampering, replay, downgrade, resource exhaustion, data leakage).
- Map each threat to concrete mitigations and residual risk.
- Separate mandatory protections from optional operational guidance.

Privacy:

- Describe collected data, retention expectations, and correlation risks.
- State minimization recommendations and operator obligations.

IANA:

- Specify each registry action precisely:
  - registry name
  - registration policy
  - new values and semantics
  - section containing the defining behavior
- State explicit no-action text when no registry change is needed.

## 6) Revise and Maintain Existing Drafts

When updating an existing draft:

- Preserve stable section numbering unless structural change is necessary.
- Keep changes minimal and localized.
- Maintain a `Changes Since draft-XX` appendix for each revision.
- Add concise rationale for non-editorial changes.
- Update cross-references, terminology, and examples affected by edits.
- Remove stale TODO markers or convert them into explicit open issues.

When resolving reviewer comments:

- Classify each comment as `editorial`, `technical`, or `blocking`.
- Apply the smallest change that resolves the comment without widening scope.
- Record disposition in a short resolution log:
  - comment id
  - decision (`accepted`, `partially accepted`, `rejected`)
  - rationale
  - touched sections

## 7) Run Quality Gates Before Finalizing

Fail the draft if any check fails:

- Required sections are present and non-empty.
- Publication/standards-process claims are not fabricated.
- Normative keywords are contextually correct and testable.
- Terminology is consistent across sections.
- Security and privacy text addresses concrete risks, not generic statements.
- IANA section is explicit (actions or no-action statement).
- Normative and informative references are separated and cited consistently.
- Unresolved placeholders (`TODO`, `TBD`, `XXX`) are absent unless explicitly allowed.
- Revision notes match actual edits.

Use external tooling when available:

- Run `idnits` for Internet-Draft hygiene checks.
- Run `xml2rfc --v3` validation for xml source.

## 8) Produce Maintainable Outputs

Return these artifacts in every response:

- Updated RFC text in the repository's existing source format.
- `Change Summary` with section-by-section modifications.
- `Open Issues` list for unresolved design choices.
- `Validation Results` checklist with pass/fail status and concrete fixes.

## RFC Markdown Template

```markdown
# <Title>

## Abstract
<One concise paragraph describing scope and outcome.>

## Status of This Memo
<Draft/status text appropriate to the target stream and maturity.>

## Copyright Notice
<Applicable copyright/licensing notice.>

## 1. Introduction
<Context, problem, and document scope.>

## 2. Conventions and Terminology
The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14.
<Define terms and abbreviations.>

## 3. Goals and Non-Goals
### 3.1 Goals
### 3.2 Non-Goals

## 4. Protocol Overview
<Actors, components, and interaction model.>

## 5. Detailed Specification
### 5.1 Data Model
### 5.2 Message Formats
### 5.3 Processing Rules
### 5.4 State Transitions

## 6. Error Handling
<Failure codes, retries, timeouts, and recovery behavior.>

## 7. Operational Considerations
<Deployment, configuration, observability, performance limits.>

## 8. Security Considerations
<Threats, mitigations, and residual risk.>

## 9. Privacy Considerations
<Data handling and minimization guidance.>

## 10. IANA Considerations
<Registry actions or explicit no-action statement.>

## 11. Backward Compatibility and Deployment
<Migration and coexistence strategy.>

## 12. References
### 12.1 Normative References
### 12.2 Informative References

## Appendix A. Examples
<Optional examples and interoperability notes.>

## Appendix B. Change Log
### B.1 Changes Since draft-00
- <List updates.>
```
