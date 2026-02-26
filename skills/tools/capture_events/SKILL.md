---
name: capture-events
description: Capture workspace events (file modifications, terminal commands, diagnostics, skill invocations) into local memory for pattern detection and skill evolution. Provider-agnostic design supports GitHub Copilot, Codex, Cursor, and universal workspace-only mode.
license: MIT
compatibility: copilot, codex, cursor, universal
metadata:
  audience: agents, background-workers, extensions
  tags: events, capture, memory, pattern-detection, feedback-loop, evolution
  type: document
  subtype: skill
---

# Capture Events

Provider-agnostic event capture system for PAX's Continuous Feedback Loop. Abstracts workspace signals into standardized events, stores them locally, and enables pattern detection for skill evolution.

## When to Use

- Running in background during development sessions
- Capturing workspace signals for pattern analysis
- Building episodic memory for skill recommendations
- Supporting assistant-agnostic feedback loops

## Architecture

This skill uses a **facade pattern** (similar to [[pull-request-tool]]) to delegate to provider-specific adapters:

```asciitree
capture-events (facade)
├── universal-provider (default)
│   ├── File watchers
│   ├── Terminal output parser
│   └── Diagnostic collectors
├── copilot-provider
│   ├── Extension integration
│   └── Copilot-specific context
├── codex-provider
│   └── API-based event capture
└── cursor-provider
    └── Extension integration
```

## Provider Selection

The skill auto-detects the environment and selects the appropriate provider:

1. Check for Copilot extension context → use `copilot-provider`
2. Check for Cursor extension context → use `cursor-provider`
3. Check for Codex API availability → use `codex-provider`
4. Default → use `universal-provider` (workspace-only signals)

## Event Schema

All providers emit events following this standardized schema:

```json
{
  "timestamp": "2026-02-26T14:32:00.000Z",
  "provider": "copilot|codex|cursor|universal",
  "event_type": "file_modified|terminal_command|diagnostic|skill_invoked|chat_context",
  "metadata": {
    "file_path": "optional string",
    "command": "optional string",
    "skill_name": "optional string",
    "diff_hash": "optional string (cheap deduplication)",
    "execution_result": "optional success|failure",
    "context_window": "optional array of related events"
  },
  "session_id": "auto-generated or provider-specific"
}
```

## Supported Event Types

| Event Type        | Trigger                           | Metadata Fields                             |
| ----------------- | --------------------------------- | ------------------------------------------- |
| `file_modified`   | File created, edited, or deleted  | `file_path`, `diff_hash`, `modification_type` |
| `terminal_command`| Command executed in terminal      | `command`, `execution_result`, `exit_code`  |
| `diagnostic`      | Linter/compiler error or warning  | `file_path`, `severity`, `message`          |
| `skill_invoked`   | Agent invokes a skill             | `skill_name`, `parameters`, `execution_result` |
| `chat_context`    | Chat session context change       | `context_window`, `user_intent`             |

## Storage Location

Events are stored locally in `.vscode/pax-memory/` (git-ignored):

```bash tree
.vscode/pax-memory/
├── episodes.jsonl    # Raw events (append-only)
├── patterns.json     # Aggregated patterns
├── signals.json      # Evolving signal definitions
└── proposals/        # Pending recommendations
```

## Usage

### Background Mode (Continuous Capture)

**Automatic启动 via VS Code Extension**:

The capture system runs continuously in the background when enabled in workspace settings:

```json
{
  "pax.feedbackLoop.enabled": true,
  "pax.feedbackLoop.provider": "universal|copilot|codex|cursor",
  "pax.feedbackLoop.captureEvents": true
}
```

**Manual Control**:

```bash
# Start capture (background process)
capture-events --start --provider universal

# Stop capture
capture-events --stop

# Check status
capture-events --status
```

### On-Demand Capture (Session-Based)

```bash
# Capture only during specific session
capture-events --session "work-item-007-implementation" --duration 3600

# Capture with custom filter
capture-events --filter "file_modified,terminal_command" --exclude-pattern "node_modules"
```

### Provider-Specific Usage

**Universal Provider** (default, no assistant required):

```bash
# Uses file watchers and terminal parsing only
capture-events --provider universal
```

**Copilot Provider**:

```bash
# Requires Copilot extension, captures Copilot-specific context
capture-events --provider copilot
```

**Codex Provider**:

```bash
# Requires Codex API access
capture-events --provider codex --api-key $CODEX_API_KEY
```

**Cursor Provider**:

```bash
# Requires Cursor extension
capture-events --provider cursor
```

## Configuration

**Workspace Settings** (`.vscode/settings.json`):

```json
{
  "pax.feedbackLoop.capture.enabled": true,
  "pax.feedbackLoop.capture.provider": "universal",
  "pax.feedbackLoop.capture.eventTypes": [
    "file_modified",
    "terminal_command",
    "diagnostic",
    "skill_invoked"
  ],
  "pax.feedbackLoop.capture.excludePatterns": [
    "node_modules/**",
    "**/.git/**",
    "**/dist/**",
    "**/.vscode/**"
  ],
  "pax.feedbackLoop.capture.maxEventsPerSession": 1000,
  "pax.feedbackLoop.capture.sessionIdleMinutes": 30
}
```

## Provider Capabilities

| Feature                  | Universal | Copilot | Codex | Cursor |
| ------------------------ | --------- | ------- | ----- | ------ |
| File modifications       | ✅        | ✅      | ✅    | ✅     |
| Terminal commands        | ✅        | ✅      | ✅    | ✅     |
| Diagnostics              | ✅        | ✅      | ✅    | ✅     |
| Skill invocations        | ⚠️ limited| ✅      | ✅    | ✅     |
| Chat context             | ❌        | ✅      | ✅    | ✅     |
| Session continuity       | ⚠️ local | ✅      | ✅    | ✅     |
| Cost                     | Free      | Free    | API   | Free   |

Legend: ✅ Full support, ⚠️ Limited support, ❌ Not available

## Output Format

**Success (append to episodes.jsonl)**:

```jsonl
{"timestamp":"2026-02-26T14:32:00.000Z","provider":"universal","event_type":"file_modified","metadata":{"file_path":"backlog/007_ast_renderer.md","diff_hash":"abc123","modification_type":"edit"},"session_id":"session-2026-02-26-001"}
{"timestamp":"2026-02-26T14:33:15.000Z","provider":"universal","event_type":"terminal_command","metadata":{"command":"pnpm run lint","execution_result":"success","exit_code":0},"session_id":"session-2026-02-26-001"}
```

**Error Handling**:

```json
{
  "status": "error",
  "error_type": "provider_unavailable",
  "message": "Copilot provider requested but extension not detected",
  "fallback": "universal",
  "action": "Switched to universal provider automatically"
}
```

## Integration with Continuous Feedback Loop

This skill is the **Capture Layer** in PAX's Continuous Feedback Loop architecture:

1. **Capture** (this skill) → Emit standardized events
2. **Memory** (background storage) → Append to episodes.jsonl
3. **Analyze** (background scheduler) → Detect patterns
4. **Recommend** ([[creating-skill]]) → Generate proposals
5. **Promote** (human approval) → Invoke [[skill-creator]]

See [docs/architecture/continuous-feedback-loop.md](../../../docs/architecture/continuous-feedback-loop.md) for full integration details.

## Security & Privacy

- **Local-only storage**: All events stay in `.vscode/pax-memory/` (git-ignored)
- **No network calls**: Universal provider operates entirely offline
- **Opt-in providers**: Codex/Copilot/Cursor providers require explicit enablement
- **Sensitive data filtering**: Automatically excludes secrets, tokens, credentials
- **User-controlled**: Can be paused, cleared, or disabled at any time

## Performance Considerations

- **Append-only writes**: O(1) event storage using JSONL
- **Non-blocking capture**: Fire-and-forget pattern, no main thread blocking
- **Memory limits**: Auto-truncate old episodes when max_events exceeded
- **Diff hashing**: Cheap deduplication using content-based hashing
- **Exclude patterns**: Skip noisy directories (node_modules, .git, dist)

## Best Practices

1. **Use universal provider by default**: Works everywhere, no dependencies
2. **Enable provider-specific features when available**: Richer context from Copilot/Codex/Cursor
3. **Configure exclude patterns**: Reduce noise from build artifacts and dependencies
4. **Monitor storage size**: Periodically check `.vscode/pax-memory/` size
5. **Review proposals regularly**: Feedback loop value increases with human validation

## Troubleshooting

**Event capture not working**:

```bash
# Check status
capture-events --status

# Verify provider availability
capture-events --check-providers

# Enable debug logging
capture-events --debug --log-file .vscode/pax-memory/debug.log
```

**Too many events**:

```json
{
  "pax.feedbackLoop.capture.excludePatterns": [
    "node_modules/**",
    "**/*.log",
    "**/coverage/**"
  ],
  "pax.feedbackLoop.capture.eventTypes": [
    "file_modified",
    "skill_invoked"
  ]
}
```

**Provider fallback loop**:

If a provider is unavailable, the skill automatically falls back to universal. Check logs for fallback reasons.

## Related Skills

- [[creating-skill]] - Consumes captured events to generate skill recommendations
- [[skill-reviewer]] - Evaluates existing skills using pattern data
- [[pull-request-tool]] - Similar facade pattern for PR management

## Related Documentation

- [Continuous Feedback Loop Architecture](../../../docs/architecture/continuous-feedback-loop.md)
- [Skill Composition](../../../docs/SKILL_COMPOSITION.md)
- [Aspects](../../../docs/ASPECTS.md)

## Reference vs. Canonical

This skill is **PAX-canonical**. The auto-evolution reference implementation in `pax/evolution/` uses shell-based hooks specific to Claude Code. This skill provides an assistant-agnostic alternative aligned with PAX's design principles.
