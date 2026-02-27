---
name: creating-skill
description: Evaluate a specific use case or skill idea against memory patterns and existing skills, then provide actionable recommendations for enhancing existing skills, creating new PAX skills, project-local skills, aspects, or AGENTS.md updates. Delegates actual skill creation to skill-creator.
license: MIT
metadata:
  audience: agents, developers
  tags: skill-creation, recommendation, pattern-analysis, memory-search, evolution
  type: document
  subtype: skill
---

# Creating Skill

Intelligent skill creation advisor that searches memory for related patterns, compares against existing skills, and recommends the best approach: enhance existing, create new (PAX or project-local), update aspects, or modify AGENTS.md. **This skill recommends only**—actual creation is delegated to [[skill-creator]] per PAX conventions.

## When to Use

- Developer has an idea for a new skill
- Repeated pattern detected by continuous feedback loop
- Considering whether to enhance existing skill vs. create new one
- Deciding between PAX-level reusable skill vs. project-specific skill
- Identifying when a pattern should become an aspect or AGENTS.md rule

## Workflow

### Phase 1: Input Collection

**Required Inputs**:

- **Use case description**: What problem does this skill solve?
- **Expected outcomes**: What should the skill produce or accomplish?
- **Trigger phrases**: How would a user invoke this skill?

**Optional Inputs**:

- **Current platform**: GitHub Copilot, Codex, Cursor, etc.
- **Constraints**: Time, risk, dependencies, maintenance budget
- **Scope**: Intended users, environments, frequency of use

**Example Invocation**:

```markdown
@agent I need a skill for batch updating work items based on a CSV file. It should read the CSV, parse frontmatter from each referenced work item, apply updates, and validate against schemas. Trigger phrase: "batch update work items from CSV"
```

### Phase 2: Memory Search

**Search Operations**:

1. **Pattern Search**: Query `.vscode/pax-memory/patterns.json` for similar patterns

   - Match by use case keywords
   - Match by file types involved
   - Match by command sequences
   - Match by skill affinity

2. **Episode Search**: Query `.vscode/pax-memory/episodes.jsonl` for related events
   - Find repeated file/command patterns
   - Identify skill invocation sequences
   - Detect error/success patterns

3. **Existing Skill Search**: Compare against PAX skills library
   - Semantic similarity to existing skills
   - Use [[skill-reviewer]] rubric patterns
   - Identify overlap and gaps

**Output from Search**:

```json
{
  "similar_patterns": [
    {
      "pattern_id": "repeated-file-read-pattern-001",
      "occurrences": 5,
      "confidence": 0.85,
      "related_skills": ["update-work-item"]
    }
  ],
  "existing_skills_overlap": [
    {
      "skill": "update-work-item",
      "overlap_score": 0.7,
      "coverage_gaps": ["Does not handle batch mode", "No CSV parsing"]
    }
  ],
  "relevant_episodes": [
    "ep-101: read backlog/001.md",
    "ep-103: read backlog/002.md",
    "ep-107: update-work-item invoked"
  ]
}
```

### Phase 3: Recommendation Analysis

**Hybrid Routing Decision Matrix**:

Apply these rules in order:

| Condition                                          | Recommendation                | Rationale                                        |
| -------------------------------------------------- | ----------------------------- | ------------------------------------------------ |
| >70% overlap with existing PAX skill               | **Enhance existing**          | Avoid duplication, improve reusable skill        |
| Reusable across multiple projects                  | **Create PAX skill**          | Broad applicability, benefits all users          |
| Project-specific workflow, narrow use case         | **Create project skill**      | Keep PAX library focused, reduce maintenance     |
| Cross-cutting concern (routing, interaction)       | **Create or update aspect**   | Composable behavior pattern                      |
| Changes decision-point routing or agent boundaries | **Update AGENTS.md**          | Workflow orchestration, not skill logic          |
| <50% overlap, no reusable pattern                  | **Compose existing skills**   | Leverage composition instead of new skill        |

**Confidence Scoring**:

```text
Confidence = (pattern_occurrences * 0.4) +
             (existing_overlap * 0.3) +
             (episode_support * 0.3)

Thresholds:
- >0.8: High confidence, proceed with recommendation
- 0.5-0.8: Medium confidence, flag uncertainties
- <0.5: Low confidence, request more information
```

### Phase 4: Generate Recommendation

**Recommendation Output Format**:

```markdown
## Skill Recommendation: [Skill Name]

**Use Case**: [Derived from input + memory analysis]

**Recommendation**: enhance_existing | create_pax_skill | create_project_skill | create_aspect | update_agents | compose_existing

**Confidence**: 0.85 (High)

**Evidence from Memory**:

- Pattern ID: repeated-file-read-pattern-001 (5 occurrences over 6 days)
- Related skills: update-work-item (70% overlap)
- Relevant episodes: 12 episodes showing batch work item operations

**Existing Skill Analysis**:

- **Skill**: update-work-item
- **Location**: `pax/skills/workflow/update-work-item/`
- **Coverage**: Single work item updates, status transitions, frontmatter validation
- **Gaps**: No batch mode, no CSV parsing, no parallel execution

**Proposed Action**: Enhance update-work-item

**Enhancement Details**:

1. Add `--batch` flag
2. Add `--csv-input <file>` parameter
3. Parse CSV columns: id, field, value
4. Use [[parallel-execution]] for concurrent updates
5. Aggregate validation errors and report at end

**Implementation Estimate**: Medium (3-5 hours)

**Risks**:

- CSV schema variations (mitigation: document required format)
- Frontmatter schema conflicts (mitigation: dry-run mode)
- Partial failure handling (mitigation: transaction log)

**Alternative Considered**: Create new batch-update-work-items skill

- **Rejected because**: 70% code duplication with update-work-item
- **Trade-off**: Enhancement adds complexity vs. separate skill adds maintenance burden

**Next Steps**:

1. Review this recommendation
2. If approved, invoke: `@agent use skill-creator to enhance update-work-item with batch CSV mode`
3. Provide CSV schema documentation
4. Add test cases for batch mode

**Evidence**:

- Episode IDs: [ep-101, ep-103, ep-107, ep-112, ep-115]
- Pattern confidence: 0.85
- Existing skill overlap: 70%
- Memory analysis timestamp: 2026-02-26T14:32:00.000Z
```

### Phase 5: Delegation to skill-creator

**IMPORTANT**: This skill **does NOT execute creation**. It generates recommendations only.

**If user approves recommendation**:

```markdown
User: "Approved, proceed with enhancement"

Agent response:
@agent I'm delegating this to skill-creator as required by PAX conventions.

[Invokes skill-creator with context]:
- Recommendation: enhance update-work-item
- Enhancement details: [from recommendation]
- Evidence and rationale: [from memory analysis]
```

**Skill-creator then handles**:

- Scaffolding changes
- SKILL.md updates
- Implementation guidance
- Test case suggestions

## Configuration

**Memory Search Settings** (`.vscode/settings.json`):

```json
{
  "pax.creatingSrill similarity": 0.5,
  "pax.creatingSkill.minPatternOccurrences": 3,
  "pax.creatingSkill.episodeWindowDays": 7,
  "pax.creatingSkill.confidenceThreshold": 0.6,
  "pax.creatingSkill.enableMemorySearch": true
}
```

## Composition with Other Skills

This skill composes:

- [[capture-events]]: Consumes memory patterns from captured events
- [[skill-reviewer]]: Uses rubric patterns for existing skill analysis
- [[discover-validation-criteria]]: Pre-discovery phase for schema requirements
- [[skill-creator]]: Delegates actual creation/enhancement after approval

## Decision Points

Uses [[interaction-modes]] aspect:

**YOLO Mode**:

- Auto-search memory
- Auto-generate recommendation
- Present recommendation, wait for approval before delegating

**Collaborative Mode**:

- Ask clarifying questions about use case
- Show search results and ask which patterns to consider
- Discuss trade-offs between enhance vs. create new
- Confirm recommendation before generating output

## Output Artifacts

1. **Recommendation Markdown**: Structured recommendation document (shown above)
2. **Memory Search Log**: JSON file with full search results (optional, for debugging)
3. **Skill-creator Handoff**: Context package for skill-creator invocation

## Quality Gates

Before outputting recommendation:

- ✅ Memory search completed (or explicitly skipped if no memory available)
- ✅ Existing skill overlap computed
- ✅ Hybrid routing decision made with rationale
- ✅ Confidence score calculated and thresholded
- ✅ Evidence linked to specific episodes/patterns
- ✅ Alternative approaches considered and rejected with reasons
- ✅ Next steps clearly state skill-creator delegation

## Error Handling

**No memory available**:

```markdown
**Warning**: No memory patterns available yet. Recommendation based on existing skill analysis only.

- Confidence: 0.4 (Low - no historical data)
- Recommended: Start with [[skill-creator]] consultation
```

**Low confidence (<0.5)**:

```markdown
**Confidence**: 0.45 (Low)

**Uncertainties**:

- Only 2 pattern occurrences (threshold: 3)
- No existing skill overlap found
- Limited episode support

**Recommendation**: Request more specifics about use case before proceeding
```

**Conflicting signals**:

```markdown
**Conflict Detected**:

- Memory patterns suggest: enhance update-work-item
- Existing skill analysis suggests: create new skill
- Episode frequency suggests: low priority

**Recommendation**: Collaborative mode to resolve conflicts with user input
```

## Best Practices

1. **Search memory first**: Always query patterns before recommending
2. **favor enhancement over creation**: Reduce PAX skills proliferation
3. **Be specific about gaps**: Don't just say "missing feature", quantify coverage
4. **Show alternatives**: Always present enhance vs. create trade-offs
5. **Delegate to skill-creator**: Never attempt to create skills directly
6. **Update memory after use**: Record this analysis as an episode for future learning

## Integration with Continuous Feedback Loop

This skill is the **Recommendation Layer** in PAX's Continuous Feedback Loop:

```text
Capture → Memory → [Analyze] → **Creating-Skill** → (User Approval) → skill-creator
```

Automatic invocation triggers:

- Pattern detector finds 3+ occurrences → auto-invoke creating-skill
- PR feedback suggests missing automation → auto-invoke creating-skill
- Work item finalization shows repeated manual steps → auto-invoke creating-skill

## Related Skills

- [[skill-creator]] - Executes skill creation/enhancement (delegation target)
- [[skill-reviewer]] - Evaluates skills with rubric (used for overlap analysis)
- [[capture-events]] - Provides memory data (data source)
- [[discover-validation-criteria]] - Pre-phase for schema discovery

## Related Documentation

- [Continuous Feedback Loop Architecture](../../../docs/architecture/continuous-feedback-loop.md)
- [Skill Composition](../../../docs/SKILL_COMPOSITION.md)
- [Skill Library Plan](../../../docs/SKILL_LIBRARY_PLAN.md)
- [Skills AGENTS.md](../../AGENTS.md) - Mandatory skill-creator usage

## Example Scenarios

### Scenario 1: Enhance Existing Skill

**Input**: "I keep manually updating multiple work items with the same status change"

**Memory Patterns**: 8 occurrences of sequential update-work-item invocations

**Recommendation**: Enhance update-work-item with batch mode

**Confidence**: 0.9 (High - clear pattern, high overlap)

### Scenario 2: Create PAX Skill

**Input**: "I need to generate RFC-style technical specs from work item descriptions"

**Memory Patterns**: No existing pattern, but multiple projects could benefit

**Recommendation**: Create new PAX skill write-technical-rfc

**Confidence**: 0.7 (Medium - reusable, but no historical data)

### Scenario 3: Create Project Skill

**Input**: "I need to sync our internal CMS with GitHub issues"

**Memory Patterns**: Project-specific API, narrow use case

**Recommendation**: Create project-local skill in `{workspace}/.agents/skills/`

**Confidence**: 0.8 (High - clear scope, project-specific)

### Scenario 4: Create Aspect

**Input**: "Multiple skills need to handle retry logic the same way"

**Memory Patterns**: Error-retry sequences in 5 different skills

**Recommendation**: Create retry-strategy aspect

**Confidence**: 0.85 (High - cross-cutting concern)

### Scenario 5: Update AGENTS.md

**Input**: "When working on RFCs, I need different routing than regular docs"

**Memory Patterns**: RFC work items have special review requirements

**Recommendation**: Update AGENTS.md with RFC-specific routing

**Confidence**: 0.75 (Medium - workflow orchestration, not skill logic)
