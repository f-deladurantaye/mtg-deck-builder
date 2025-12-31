# Role and Feature Registries Reference

This file documents the two machine-readable registries used by the engine:

- `roles.yml` — role ontology + Scryfall query primitives + post-retrieval tagging heuristics
- `features.yml` — machine-readable feature registry + deterministic feature extraction rules

Both files are **versioned**, **editable without Python changes**, and are intended to be the single source of truth for role/feature semantics.

## 1) `roles.yml`

### Purpose

Defines:

- the **role ontology** (IDs, descriptions, defaults)
- **query fragments** used to retrieve candidates from Scryfall
- **must-have / anti-signal** heuristics for post-retrieval role tagging
- optional **weights** and **limits** for scoring/building

The engine uses `roles.yml` in two places:

1. query planning: assemble Scryfall queries from role fragments + deck constraints
2. role tagging: confirm/deny role assignment deterministically after retrieval

### File shape

Top-level keys (recommended):

- `version` (string) — registry version, e.g. `1.0.0`
- `roles` (list) — role definitions

Minimal skeleton:

```yml
version: "1.0.0"
roles:
  - id: ramp
    description: "Increase mana production or mana acceleration."
    weight_default: 1.0
    query_templates: []
    must_have_signals: []
    anti_signals: []
```

### `Role` schema

Each role item supports:

- `id` (string, required)

  - stable identifier used everywhere (`ramp`, `draw`, `removal`, `sac_outlet`, `token_gen`, etc.)
  - **lower_snake_case**, unique

- `description` (string, required)

- `weight_default` (number, optional)

  - baseline weight used by scoring when `DeckBrief.role_priority` doesn’t override

- `query_templates` (list of query fragments, optional)

  - each entry is a **fragment**, not a full query
  - the engine will wrap these fragments with:

    - colour identity constraints
    - legality constraints (Commander)
    - user exclusions
    - any deck-specific constraints (e.g., `type`, `cmc` windows)

- `must_have_signals` (list, optional)

  - deterministic checks used by the role tagger
  - intended to be **high precision**
  - applied after retrieval; if fails, role tag should be rejected

- `anti_signals` (list, optional)

  - deterministic checks that veto role tagging
  - used to reduce false positives

- `notes` (string, optional)

  - short internal note; keep minimal

### Signal rule format

Signals are expressed as simple structured rules (recommended), to keep parsing deterministic.

Supported rule shapes (recommended):

- `regex_any`: list of regex patterns; match if any matches
- `regex_all`: list of regex patterns; match if all match
- `type_any`: list of type-line substrings
- `type_none`: list of forbidden type-line substrings
- `cmc_max` / `cmc_min`: numeric bounds
- `keywords_any`: list of Scryfall keywords (if present)
- `produces_mana_any`: list of mana symbols (`["W","U","B","R","G","C"]`) (if normalised field exists)

Example:

```yml
- id: sac_outlet
  description: "Repeatable ways to sacrifice your own permanents."
  weight_default: 1.1

  query_templates:
    - "oracletag:free-sac-outlet"
    - '(o:"sacrifice" (o:"a creature" OR o:"another creature"))'

  must_have_signals:
    - regex_any:
        - '(?i)\bsacrifice\b'
      regex_any_2: [] # (avoid; prefer a single rule object per list item)
    - type_none:
        - "Instant"
        - "Sorcery"

  anti_signals:
    - regex_any:
        - '(?i)\bsacrifice an opponent\b'
        - '(?i)\bsacrifice.*only if\b'
```

**Rule evaluation** (deterministic, recommended):

- `must_have_signals`: all items must pass (AND across list)
- within a rule object: each key applies its own semantics (e.g., `regex_any` is OR within that key)
- `anti_signals`: if any item passes, veto role tagging

### Query fragment conventions

- Query fragments are plain Scryfall search syntax snippets.
- Do not include colour identity restrictions directly in fragments unless role-specific.
- Do not include user exclusions; those are applied by the engine.

Recommended fragment style:

- keep fragments **small**, composable, and role-centric
- prefer `oracletag:*` when stable and relevant; otherwise use oracle text/type heuristics

## 2) `features.yml`

### Purpose

Defines the **feature space** used for:

- deterministic feature extraction from Scryfall-normalised card data
- reusable, explainable scoring signals (`is_ramp`, `is_finisher`, `produces_mana`, etc.)
- consistent behaviour across builds and UI summaries

This registry is **machine-readable** and should be treated as a contract:

- adding a feature = updating YAML, not Python logic (beyond the generic evaluator)
- features are extracted deterministically from card fields

### File shape

Top-level keys (recommended):

- `version` (string)
- `features` (list)

Minimal skeleton:

```yml
version: "1.0.0"
features:
  - id: produces_mana
    type: enum_set
    description: "Mana symbols the card can produce."
    sources: ["produced_mana", "oracle_text"]
    rules: []
```

### `Feature` schema

Each feature item supports:

- `id` (string, required)

  - unique, lower_snake_case
  - stable identifier referenced by scorer/UI/export

- `type` (string, required)
  Supported (recommended) types:

  - `bool` — true/false
  - `int` — integer
  - `float` — numeric
  - `enum` — single value from a fixed set
  - `enum_set` — set of values from a fixed set
  - `string` — text (rare; avoid unless needed)
  - `string_set` — set of strings (rare; prefer enums)

- `description` (string, required)

- `sources` (list of strings, optional)

  - which normalised card fields this feature may read from
  - examples: `oracle_text`, `type_line`, `cmc`, `mana_cost`, `keywords`, `produced_mana`, `colour_identity`, `power`, `toughness`, `rarity`

- `values` (list, optional)

  - for `enum` / `enum_set`, define allowed values (e.g., `["W","U","B","R","G","C"]`)

- `default` (any, optional)

  - default value when rules don’t yield a value
  - for `bool`, default is typically `false`
  - for sets, default is `[]`

- `rules` (list, required)

  - ordered list of deterministic rules; first match can set or update feature value
  - rules should be **pure** and evaluable without side effects

- `notes` (string, optional)

### Rule format (recommended)

Each rule is a structured object with:

- `when` (object, required) — predicate over card fields
- `set` (any, optional) — assigns a value (overwrites)
- `add` (any, optional) — adds to a set / increments numeric
- `priority` (int, optional) — if present, higher runs first (otherwise file order)

Supported predicates (recommended):

- `regex_any`: `{ field: "oracle_text", patterns: [ ... ] }`
- `regex_all`: `{ field: "oracle_text", patterns: [ ... ] }`
- `type_any`: `{ values: [ ... ] }` against `type_line`
- `type_none`: `{ values: [ ... ] }` against `type_line`
- `cmc_min` / `cmc_max`
- `keywords_any`
- `has_field`: `{ field: "produced_mana" }`
- `equals`: `{ field: "...", value: ... }`
- `in_set`: `{ field: "...", values: [ ... ] }`

### Feature conventions

- Prefer **bool flags** for interpretable concepts:

  - `is_ramp`, `is_draw_engine`, `is_boardwipe`, `is_tutor`, `is_finisher`, `is_interaction`, `is_protection`, `is_recursion`, `is_grave_hate`, `is_mana_rock`, `is_mana_dork`, `is_land_ramp`, `is_sac_outlet`, `is_sac_payoff`, `is_token_generator`, `is_wincon_enabler`, etc.

- Prefer **enum_set** for compositional signals:

  - `produces_mana` (W/U/B/R/G/C)
  - `card_types` (Creature/Artifact/Enchantment/Instant/Sorcery/Land/Planeswalker/Battle)
  - `interaction_modes` (counterspell/removal/bounce/stax/tax/fog/etc.) if you model them

- Keep extraction rules conservative (precision > recall).

### Example feature definitions

```yml
version: "1.0.0"
features:
  - id: produces_mana
    type: enum_set
    values: ["W", "U", "B", "R", "G", "C"]
    default: []
    description: "Mana symbols the card can produce."
    sources: ["produced_mana", "oracle_text", "type_line"]
    rules:
      - when:
          has_field: { field: "produced_mana" }
        set: "{{produced_mana}}" # evaluator can substitute from normalised field

      - when:
          regex_any:
            field: "oracle_text"
            patterns:
              - '\{T\}:\s*Add\s*\{W\}'
        add: ["W"]

  - id: is_finisher
    type: bool
    default: false
    description: "High-leverage closing piece."
    sources: ["oracle_text", "cmc", "type_line", "power"]
    rules:
      - when:
          regex_any:
            field: "oracle_text"
            patterns:
              - '(?i)\bdouble\b.*\bdamage\b'
              - '(?i)\byou win the game\b'
              - '(?i)\bwhenever\b.*\bdeals combat damage\b.*\byou win\b'
        set: true
      - when:
          cmc_min: 6
          type_any: { values: ["Creature"] }
        set: true

  - id: is_tutor
    type: bool
    default: false
    description: "Searches library for a card and puts it into hand/top/battlefield."
    sources: ["oracle_text"]
    rules:
      - when:
          regex_any:
            field: "oracle_text"
            patterns:
              - '(?i)\bsearch your library\b.*\bfor a\b'
        set: true
      - when:
          regex_any:
            field: "oracle_text"
            patterns:
              - '(?i)\btutor\b'
        set: true
```

## 3) Shared registry rules

### Versioning

- Each registry has a `version` string.
- The build output should store:

  - role registry version
  - feature registry version
  - Scryfall query strings used
  - date/time of build
  - engine version

### Determinism requirements

- Registry evaluation must be deterministic:

  - no random ordering
  - stable tie-breakers
  - stable rule precedence (priority then file order)

### Interaction between features and roles

Recommended contract:

- **roles** represent _deckbuilding buckets_ and target coverage (counts/weights)
- **features** represent _card properties_ used for:

  - role tagging support
  - scoring components
  - UI explanations and filters

Typical flows:

- `RoleTagger` assigns role IDs using `roles.yml` (and can consult `features.yml` outputs)
- `FeatureExtractor` computes feature values using `features.yml`
- `Scorer` consumes:

  - `DeckBrief` (role targets/priorities, mechanics, soft budget intent)
  - assigned roles
  - extracted features
  - deck state

### Budget note (soft-only)

Budget is enforced as a **soft constraint**:

- candidates are not excluded solely by price
- scoring applies a budget penalty / preference
- UI should surface price and allow user overrides / locks

(Registry files should not encode budget logic; keep budget behaviour in scorer/policy.)

## 4) Minimal normalised card fields expected by registries

The evaluator assumes the Scryfall layer produces a normalised card object with at least:

- `name` (string)
- `scryfall_id` (string)
- `oracle_text` (string, may be empty)
- `type_line` (string)
- `mana_cost` (string, may be empty)
- `cmc` (number)
- `colour_identity` (list of symbols)
- `keywords` (list of strings, optional)
- `produced_mana` (list of symbols, optional)
- `prices` (object with configured price source key)
- `legalities.commander` (string / bool normalised)

Registries should avoid depending on fields not present here unless explicitly added to normalisation.
