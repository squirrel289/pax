# Dependent Capability Contract

## Interface Specification

### Fuzzy

- `provider` skills "declare" capabilities via the existing defacto standard `description`-like prose.
- `consumer` skills apply SEO-style discovery to enumerate installed + accessible skills that may satisfy `expect`ations based on metadata (`name`-like, `description`-like, etc.)

### Well-defined

SKILLs MAY publish more strongly defined interface contracts using metadata structure.

#### Grammar

```ebnf
contract := "DCI/" version [ "^" mode ] SP clauses
version := 1*DIGIT
clauses := clause *(SP clause)
clause := provides | expects | accepts | required | optional | policy

provides := "P(" values ")"
expects := "E(" values ")"
accepts := "A(" kvpairs ")"
required := "R(" values ")"
optional := "O(" values ")"
policy := "Pol(" kvpairs ")"

values := value *("," value)
kvpairs := kv *("," kv)
kv := key "=" value
key := 1*(ALPHA | DIGIT | "-" | "_")
value := 1*(safe-char | escaped-char)
safe-char := ALPHA | DIGIT | "-" | "_" | "." | "/" | ":" | "@"
escaped-char := "\" ("," | "(" | ")" | "=" | "\" | " ")

mode := "strict" | "best-effort"
```

Mode default:

- If `^mode` is omitted, mode defaults to `best-effort`.

Escaping rules:

- Literal comma in a `value` MUST be escaped as `\,`.
- Literal opening/closing parenthesis in a `value` MUST be escaped as `\(` and `\)`.
- Literal equals in a `value` MUST be escaped as `\=`.
- Literal backslash in a `value` MUST be escaped as `\\`.
- Literal space in a `value` SHOULD be escaped as `\ ` for parser consistency.
- For `A(...)` and `Pol(...)`, parsers MUST split `key=value` at the first unescaped `=`.

How to read the grammar:

1. Parse the prefix: `DCI/<version>`.
2. Parse optional mode: `^strict` or `^best-effort`.
3. Parse one or more clauses separated by spaces.
4. For `P/E/R/O`, read a comma-delimited list of values.
5. For `A/Pol`, read comma-delimited key/value pairs (`key=value`).
6. Apply escape decoding inside each parsed value.

Parsing examples:

- `DCI/1 P(option-evaluation)` means version `1`, default mode `best-effort`, one `P` value.
- `DCI/1^strict R(web-search,reasoning-advanced)` means strict mode with two required capabilities.
- `DCI/1 A(output-template=raw\,v2)` means `output-template` value is `raw,v2`.

#### Example

```yaml
compatibility: "copilot,cli"
metadata:
  contract: "DCI/1^strict P(...) E(...) A(...) R(...) O(...) Pol(...)"
```

#### Token legend

- `[P]rovides(...)` provides
- `[E]xpects(...)` expects
- `[A]ccepts(...)` accepts
- `[R]equired(...)` required capabilities
- `[O]ptional(...)` optional capabilities
- `[Pol]icy(...)` dependency policy

Token form policy:

- Canonical serialization MUST use short-form tokens: `P E A R O Pol`.
- Parsers MAY accept long-form aliases (`Provides Expects Accepts Required Optional Policy`) for compatibility/migration.
- If long-form aliases are accepted, parsers MUST normalize them to short-form before validation or matching.

## Key Advantages

- leverages existing precedent of LLMs to load only the skill metadata upfront without overburdening the initial context.
- compatible with the massive ecosystem of existing `SKILL`s
- low-friction migration path for skills that want to optimize for reuse and discoverability
- solves the widely discussed "dependency management" problem
- doesn't require any new tools or frameworks for packaging, manifest management, distribution, etc.

## Key Constraints

- puts the onus on the `consumer` skill to `declare`, `discover` and `enforce` the necessary capabilities
- inherently non-deterministic
