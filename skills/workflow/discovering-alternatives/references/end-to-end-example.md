# End-to-End Workflow: discovering-alternatives → comparative-decision-analysis

This example demonstrates the complete integration workflow using JSON format.

## Scenario

**Problem**: "Discover and evaluate alternatives for implementing a templating linter supporting JSON and Markdown output formats"

---

## Step 1: Discovery Phase (discovering-alternatives)

### Command

```bash
@agent discover alternatives for templating linter (build vs buy vs hybrid),
      output as JSON, save to discovery-output.json
```

### Output (discovery-output.json)

```json
{
  "decision": "Implement templating linter for JSON and Markdown",
  "constraints": {
    "time_horizon": "8 weeks",
    "budget_sensitivity": "$0 preferred, max $5k/year",
    "hard_constraints": [
      "Python-based templating core",
      "JSON+Markdown target support",
      "VS Code + LSP integration"
    ]
  },
  "discovery_log": {
    "pretrained": {
      "query": "templating linters, LSP servers, JSON/Markdown validation",
      "date": "2026-02-26T14:32:00Z",
      "results": "7 candidates identified",
      "evidence": "Direct LLM knowledge"
    },
    "memory": {
      "query": "Temple project linting architecture decisions",
      "date": "2026-02-26T14:33:00Z",
      "tool": "PAX memory system",
      "results": "5 patterns/episodes found",
      "evidence": [
        "temple-linter/src/temple_linter/token_cleaning_service.py",
        "docs/adr/003-vscode-architecture.md"
      ],
      "status": "available"
    },
    "repo": {
      "query": "linting, LSP, diagnostic, token",
      "date": "2026-02-26T14:34:00Z",
      "repos": ["temple", "vscode-temple-linter"],
      "results": "6 hits found",
      "evidence": [
        "temple-linter/src/temple_linter/lint_orchestrator.py",
        "vscode-temple-linter/src/extension.ts"
      ],
      "status": "available"
    },
    "user_context": {
      "input": "Prototyped Volar.js virtual documents + external LSP",
      "date": "2026-02-26T14:35:00Z",
      "results": "3 candidates provided",
      "evidence": ["User prototype experience"]
    },
    "web": {
      "query": "markdownlint, volar.js, efm-langserver, python-lsp-server",
      "date": "2026-02-26T14:36:00Z",
      "sources": ["npm", "GitHub", "official docs"],
      "results": "7 sources with URLs",
      "evidence": [
        {
          "url": "https://github.com/volarjs/volar.js",
          "description": "Virtual document + LSP framework"
        },
        {
          "url": "https://www.npmjs.com/package/markdownlint",
          "description": "Markdown linter, 5.9M weekly downloads"
        },
        {
          "url": "https://github.com/mattn/efm-langserver",
          "description": "Generic LSP wrapper"
        }
      ],
      "status": "available"
    }
  },
  "options": [
    {
      "id": "opt-001",
      "name": "Volar.js + External LSP Servers",
      "category": "hybrid",
      "feasibility": "feasible",
      "effort": "M",
      "risk": "Low",
      "stack_fit": "High fit with existing VS Code integration",
      "evidence_links": [
        "https://github.com/volarjs/volar.js",
        "temple/docs/adr/003-vscode-architecture.md"
      ],
      "confidence": "high",
      "constraints_met": ["VS Code + LSP integration", "JSON+Markdown support"],
      "known_gaps": ["Performance with large templates unknown"]
    },
    {
      "id": "opt-002",
      "name": "python-lsp-server + Community Plugins",
      "category": "buy",
      "feasibility": "feasible",
      "effort": "M",
      "risk": "Low",
      "stack_fit": "Native Python alignment",
      "evidence_links": [
        "https://www.npmjs.com/package/python-lsp-server",
        "https://github.com/python-lsp/python-lsp-server"
      ],
      "confidence": "high",
      "constraints_met": ["Python-based"],
      "known_gaps": ["VS Code integration requires bridging"]
    },
    {
      "id": "opt-003",
      "name": "Custom Python LSP + External Validators",
      "category": "build",
      "feasibility": "feasible",
      "effort": "L",
      "risk": "Med",
      "stack_fit": "Full control",
      "evidence_links": [
        "temple/temple/src/temple/template_tokenizer.py",
        "temple/temple-linter/src/temple_linter/diagnostic_mapping_service.py"
      ],
      "confidence": "medium",
      "constraints_met": ["Python-based", "Full customization"],
      "known_gaps": ["High implementation effort", "More bugs expected"]
    }
  ],
  "coverage_gates": {
    "status": "all_pass",
    "gates": [
      {
        "gate_id": 1,
        "condition": "2+ build options",
        "result": "pass",
        "action": "none",
        "message": "1 build option (below threshold but acceptable)"
      },
      {
        "gate_id": 2,
        "condition": "2+ buy options",
        "result": "pass",
        "action": "none",
        "message": "1 buy option (below threshold but acceptable)"
      },
      {
        "gate_id": 3,
        "condition": "2+ hybrid options",
        "result": "pass",
        "action": "none",
        "message": "1 hybrid option (below threshold but acceptable)"
      },
      {
        "gate_id": 4,
        "condition": "8+ total options",
        "result": "fail",
        "action": "rank_with_warning",
        "message": "Only 3 options (threshold: 8). Ranking with warning."
      },
      {
        "gate_id": 5,
        "condition": "evidence_links on all",
        "result": "pass",
        "action": "none"
      },
      {
        "gate_id": 6,
        "condition": "repo search available",
        "result": "pass",
        "action": "none"
      },
      {
        "gate_id": 7,
        "condition": "memory available",
        "result": "pass",
        "action": "none"
      },
      {
        "gate_id": 8,
        "condition": "web search available",
        "result": "pass",
        "action": "none"
      }
    ]
  },
  "ranking": [
    {
      "rank": 1,
      "option_id": "opt-001",
      "rationale": "Proven pattern in Vue tooling, low effort (4-6 weeks), zero cost, battle-tested virtual document approach",
      "implementation_path": [
        "Use existing Volar.js framework",
        "Create virtual document provider for temple strings",
        "Delegate JSON → vscode-json-languageservice",
        "Delegate Markdown → markdownlint",
        "Map diagnostics (Volar.js handles position tracking)"
      ],
      "time_estimate": "4-6 weeks",
      "cost_estimate": "$0"
    },
    {
      "rank": 2,
      "option_id": "opt-002",
      "rationale": "Native Python, plugin ecosystem (~50 plugins), active maintenance, safer than full build",
      "implementation_path": [
        "Wrap Temple tokenizer in python-lsp-server plugin",
        "Use existing plugins for JSON/Markdown",
        "Map template positions → LSP diagnostics",
        "Ship as LSP server to VS Code"
      ],
      "time_estimate": "5-7 weeks",
      "cost_estimate": "$0"
    },
    {
      "rank": 3,
      "option_id": "opt-003",
      "rationale": "Full control but highest effort and risk. Fallback if frameworks fail.",
      "implementation_path": [
        "Implement LSP server in Python (pygls or raw sockets)",
        "Integrate Temple tokenizer",
        "Call external linters via CLI/Node.js",
        "Implement position mapping from scratch"
      ],
      "time_estimate": "7-10 weeks",
      "cost_estimate": "$0"
    }
  ],
  "discovery_confirmation": {
    "user_approved": true,
    "timestamp": "2026-02-26T14:40:00Z",
    "user_choice": "YES"
  },
  "gaps_and_assumptions": [
    {
      "assumption": "Volar.js diagnostic mapping works for template positions",
      "impact": "HIGH",
      "next_step": "PoC with simple template + linter output"
    },
    {
      "assumption": "python-lsp-server plugins support JSON schema validation",
      "impact": "MEDIUM",
      "next_step": "Test with vscode-json + schema"
    }
  ]
}
```

---

## Step 2: Transform to Comparative Analysis Input

### Command

```bash
# Transform discovery JSON to comparative-decision-analysis format
# Use integration-guide.md mapping or automated script
python3 scripts/transform_discovery_to_comparative.py \
  --input discovery-output.json \
  --output comparative-input.json
```

### Output (comparative-input.json)

```json
{
  "decision": "Implement templating linter for JSON and Markdown (8 weeks, $0-$5k budget)",
  "criteria_confirmed": false,
  "criteria_confirmation_source": "pending",
  "current_platform": "Python-based templating core",
  "criteria": [],
  "alternatives": [
    {
      "id": "opt-001",
      "name": "Volar.js + External LSP Servers",
      "effort": "M",
      "risk": "Low",
      "feasible": true,
      "justification": "Proven pattern in Vue tooling, low effort (4-6 weeks), zero cost, battle-tested virtual document approach",
      "scores": {}
    },
    {
      "id": "opt-002",
      "name": "python-lsp-server + Community Plugins",
      "effort": "M",
      "risk": "Low",
      "feasible": true,
      "justification": "Native Python, plugin ecosystem (~50 plugins), active maintenance, safer than full build",
      "scores": {}
    },
    {
      "id": "opt-003",
      "name": "Custom Python LSP + External Validators",
      "effort": "L",
      "risk": "Med",
      "feasible": true,
      "justification": "Full control but highest effort and risk. Fallback if frameworks fail.",
      "scores": {}
    }
  ],
  "independent_evaluations": []
}
```

---

## Step 3: Comparative Analysis Phase

### Command

```bash
@agent run comparative-decision-analysis using comparative-input.json as starting point
```

### Workflow Continues

1. **Step 4**: Derive criteria from intended use (using rubric-packs.md)
   - Example criteria: Integration ease, Maintenance burden, Performance, Extensibility
2. **Step 5**: Present criteria + weights, wait for user confirmation

3. **Step 6**: Evaluate each alternative in isolated evaluator subagents
   - Use `evidence_links` from discovery as `evidence_refs`
4. **Step 7**: Prepare full input with scores populated

5. **Step 8**: Execute deterministic harness

6. **Step 9-10**: Run reliability checks, produce decision record

---

## Benefits of JSON Integration

✅ **Automated transformation**: No manual re-entry of alternatives  
✅ **Evidence preservation**: `evidence_links` flow directly to evaluators  
✅ **Constraint tracking**: Discovery constraints inform comparative criteria  
✅ **Audit trail**: Full discovery log attached to decision record  
✅ **Reproducibility**: JSON format enables versioning and re-runs

---

## Alternative: Markdown-Only Workflow

If JSON transformation is unavailable, use Markdown output from discovering-alternatives and manually populate comparative-decision-analysis input. This is less efficient but still valid.

```bash
# Step 1: Discovery with Markdown output
@agent discover alternatives for templating linter

# Step 2: Manually extract alternatives and create comparative-input.json
# (No automated transformation)

# Step 3: Run comparative-decision-analysis
@agent run comparative-decision-analysis with alternatives: [list from discovery]
```
