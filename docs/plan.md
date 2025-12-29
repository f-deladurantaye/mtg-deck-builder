# MTG Commander Deck Builder

## Guiding principles (non-negotiable)

1. **Ship value early**: a legal, coherent, explainable deck beats a perfect engine.
2. **Determinism is a tool, not a religion**: only enforce it where it protects trust.
3. **Composition over classification**: cards have features; roles are compositions of features.
4. **Critical path first**: anything not on the path to a usable deck is optional until proven otherwise.
5. **LLMs are assistants, never decision-makers**.

---

## 1. Scope boundaries

### In scope (all versions)

- Commander format only
- Offline-capable local tool
- Deterministic engine (given snapshot + recipe)
- Explainable decisions

### Explicitly out of scope (until v3+)

- Competitive tier optimization
- Multiplayer meta analysis
- Auto-tuning via learning
- Recommendation personalization across users

---

## 2. Critical vs Optional architecture (at a glance)

| Layer         | Critical (must exist in v1)      | Optional / Later              |
| ------------- | -------------------------------- | ----------------------------- |
| Data          | SQLite cache OR DuckDB bulk      | Full snapshot UI              |
| Cards         | Normalised card table            | Full raw JSON mirror          |
| Roles         | Feature extraction + composition | Complex synergy DSL           |
| Engine        | Role coverage + curve + legality | Advanced pruning heuristics   |
| Scoring       | Simple weighted sum              | Multi-objective tuning        |
| UI            | CLI or minimal Streamlit         | Rich interactivity            |
| LLM           | None                             | DeckBrief interviewer         |
| Observability | Basic logs                       | Full trace + DuckDB ingestion |

---

## 3. Core data architecture (critical)

### 3.1 SQLite — Scryfall cache (CRITICAL)

Purpose: **stability + offline builds**

- Stores:

  - query
  - page
  - response JSON
  - fetched_at

- Supports:

  - read-through
  - offline mode

- Snapshot concept exists **internally**, not exposed in v1 UI.

> If this fails, nothing else matters.

---

### 3.2 DuckDB — Card index (CRITICAL)

Purpose: **fast deterministic filtering + evaluation**

Tables:

- `cards` (normalised, engine-facing)
- `card_features` (derived features, see below)

DuckDB is **read-mostly** in v1.

---

## 4. Role system — composition model (CRITICAL)

### 4.1 Card features (the foundation)

Each card is annotated with **atomic, testable features**.

Examples:

```text
produces_mana
draws_cards
removes_creature
removes_noncreature
is_board_wipe
is_tutor
creates_tokens
is_finisher
protects_board
recurs_from_graveyard
```

Feature extraction rules:

- Pure functions
- Deterministic
- Tested on curated fixtures
- No scoring logic here

> Features are facts, not opinions.

---

### 4.2 Roles = compositions of features (CRITICAL)

Roles are **logical groupings**, not labels applied by regex soup.

Example:

```yaml
ramp:
  requires:
    - produces_mana
  optional:
    - draws_cards
  excludes:
    - is_land_only

card_draw:
  requires:
    - draws_cards

interaction:
  requires_any:
    - removes_creature
    - removes_noncreature
    - is_board_wipe

finisher:
  requires:
    - is_finisher
```

Properties:

- No weights in v1
- Boolean membership
- One card can belong to multiple roles

---

### 4.3 Why this is critical

- Enables explainability
- Prevents YAML entropy
- Makes scoring tractable
- Allows incremental refinement

---

## 5. Engine (critical path)

### 5.1 DeckBrief (CRITICAL)

Minimal required inputs:

- commander
- colour identity
- role targets (counts, not weights)
- soft budget
- exclusions / must-includes

No archetype inference in v1.

---

### 5.2 Candidate generation (CRITICAL)

For each role:

1. Build query constraints
2. Fetch candidates from cache
3. Normalise + index
4. Filter legality + colour
5. Assign features → roles

---

### 5.3 Scoring (CRITICAL but simple)

**V1 scoring is intentionally dumb.**

Score components:

- role deficit satisfaction
- curve fit (coarse bins)
- soft budget penalty

No synergy scoring in v1.

```text
score = role_deficit_bonus
      + curve_bonus
      - budget_penalty
```

Explainability comes from the breakdown.

---

### 5.4 Assembly loop (CRITICAL)

Order:

1. Commander
2. Lands (minimum target)
3. Role buckets (in fixed priority)
4. Stop at 99

No pruning in v1 beyond:

- max deck size
- duplicate prevention

---

## 6. UI (minimal but usable)

### V1 UI (CRITICAL)

Either:

- CLI **or**
- Minimal Streamlit

Must support:

- Input DeckBrief
- Run build
- Show decklist
- Show role counts
- Export JSON

Anything else is optional.

---

## 7. What is OPTIONAL in v1 (explicitly deferred)

- Advanced pruning
- Synergy rules
- Staples filler
- LLM integration
- Snapshot selection UI
- Lock/swap UX
- Evaluation dashboards

These are **not allowed to block v1**.

---

## 8. Success criteria by version

---

## V1 — “It Works and I Trust It” (Must-have)

### Functional

- ✅ Generates a **legal 99-card Commander deck**
- ✅ Respects colour identity and commander legality
- ✅ Meets minimum role targets (ramp, draw, interaction)
- ✅ Deterministic given same cache
- ✅ Fully explainable (why each card was added)

### Non-functional

- ✅ Runs offline
- ✅ Builds complete deck in < 10s locally
- ✅ No silent nondeterminism

### User reaction goal

> “This is coherent and usable, even if not perfect.”

---

## V2 — “It’s Actually Good” (Important)

### Added capabilities

- Synergy scoring
- Staples filler (gap-only)
- Deterministic pruning to 99
- Snapshot management UI
- Basic evaluation harness
- LLM DeckBrief interviewer (optional)

### User reaction goal

> “This feels like a thoughtful deck builder, not a rules engine.”

---

## V3 — “It’s Insightful” (Advanced)

### Added capabilities

- Archetype inference
- Multiple scoring profiles
- Deck comparison & diffing
- Rich Streamlit UX
- Build trace visualisation
- Batch evaluation across archetypes

### User reaction goal

> “I learn something about deckbuilding from this.”

---

## 9. Implementation order (guarded)

### Phase 1 — Hard core (cannot skip)

1. SQLite cache
2. Card normalisation
3. DuckDB card index
4. Feature extraction
5. Role composition
6. Simple deck assembly

### Phase 2 — Quality

7. Scoring refinement
8. Deterministic pruning
9. Evaluation harness

### Phase 3 — UX & intelligence

10. LLM integration
11. Rich UI
12. Advanced observability

---

## 10. Explicit kill switches (PM safety valves)

If any of these happen, **stop and reassess**:

- Role rules exceed 2 screens without tests
- Scoring logic becomes unreadable
- UI work blocks engine progress
- “We just need to tweak weights” appears often
