# Role Taxonomy (Commander)

## 1) Core Infrastructure Roles

_These are required for almost every Commander deck._

### Mana & Acceleration

- `ramp`
- `ramp_land`
- `ramp_artifact`
- `ramp_creature`
- `ramp_burst` (rituals, one-shot)
- `mana_fixing`
- `cost_reduction`
- `mana_sink`

### Card Advantage

- `draw`
- `draw_repeatable`
- `draw_burst`
- `card_selection`
- `impulse_draw`
- `wheel`
- `cantrip`

---

## 2) Interaction & Control

_How the deck stops opponents._

### Removal

- `removal`
- `removal_creature`
- `removal_artifact`
- `removal_enchantment`
- `removal_planeswalker`
- `removal_any`
- `exile_removal`
- `damage_removal`
- `edict`

### Sweepers

- `boardwipe`
- `boardwipe_creatures`
- `boardwipe_artifacts`
- `boardwipe_enchantments`
- `mass_bounce`

### Stack & Tempo

- `counterspell`
- `soft_counter`
- `spell_copy`
- `stack_interaction`
- `tempo_play`

### Disruption

- `tax`
- `stax_light`
- `stax_heavy`
- `tapdown`
- `hand_disruption`
- `library_disruption`
- `grave_hate`

---

## 3) Protection & Resilience

_How the deck survives removal and wipes._

### Protection

- `protection`
- `protect_commander`
- `hexproof_grant`
- `indestructible_grant`
- `protection_colour`
- `ward_grant`
- `fog`

### Board Safety

- `boardwipe_protection`
- `blink_protection`
- `phasing_protection`
- `totem_armour`

### Recursion

- `recursion`
- `recursion_to_hand`
- `reanimation`
- `mass_reanimation`
- `self_recursion`
- `land_recursion`

---

## 4) Win Conditions & Finishers

_How the deck actually ends the game._

### Finishers

- `finisher`
- `combat_finisher`
- `noncombat_finisher`
- `overrun_effect`
- `mass_pump`
- `drain_finisher`
- `burn_finisher`

### Alternate Wins

- `alternate_wincon`
- `mill_wincon`
- `commander_damage_wincon`

### Combo

- `combo_piece`
- `combo_enabler`
- `combo_payoff`
- `infinite_enabler`
- `infinite_payoff`

---

## 5) Board Development & Scaling

_How the deck builds presence._

### Creatures & Tokens

- `token_generator`
- `token_scaler`
- `token_multiplier`
- `go_wide_support`
- `go_tall_support`
- `anthem`

### Counters

- `counter_generator`
- `counter_multiplier`
- `proliferate`
- `experience_counter_support`

---

## 6) Sacrifice & Death Engines

_Aristocrats, sacrifice loops, death value._

- `sac_outlet`
- `free_sac_outlet`
- `conditional_sac_outlet`
- `sac_payoff`
- `death_payoff`
- `dies_trigger`
- `aristocrats`
- `graveyard_filler`

---

## 7) Tutors & Consistency

_How the deck finds what it needs._

- `tutor`
- `tutor_any`
- `tutor_creature`
- `tutor_land`
- `tutor_artifact`
- `tutor_enchantment`
- `tutor_spell`
- `topdeck_tutor`
- `battlefield_tutor`

---

## 8) Synergy / Archetype Roles

_Deck-specific engines and payoffs._

### Spell-Based

- `spellslinger_payoff`
- `prowess_style`
- `storm_support`

### Permanent-Based

- `enchantress`
- `artifact_payoff`
- `artifact_engine`
- `blink_engine`
- `blink_payoff`

### Zone-Based

- `graveyard_synergy`
- `lands_synergy`
- `landfall_payoff`

### Tribal

- `tribal_enabler`
- `tribal_payoff`

---

## 9) Lands & Mana Base

_Specialised land roles._

- `land`
- `utility_land`
- `mana_land`
- `fetch_land`
- `cycling_land`
- `manland`
- `channel_land`
- `sac_land`

---

## 10) Meta & Deck-Health Roles

_Not strategy, but deck quality._

- `staple`
- `glue_piece`
- `engine_piece`
- `engine_payoff`
- `redundancy_piece`
- `flex_slot`
- `high_variance_piece`
- `political_piece`

---

## 11) Role Relationships (important)

### Role groups (for targets)

- **Infrastructure**: ramp, draw, interaction, protection
- **Execution**: synergy, engines, payoffs
- **Closing**: finishers, combos
- **Stability**: recursion, glue, lands

### Multi-role expectations

Cards are expected to satisfy **multiple roles**:

- Ramp + Fixing
- Sac Outlet + Engine
- Token Generator + Sac Fodder
- Protection + Synergy
- Tutor + Combo Piece

---

## 12) Taxonomy design rules (engine-relevant)

- Roles are **intent-based**, not card-type-based
- Roles are **non-exclusive** (many per card)
- Roles are **coverage-targeted** (counts / ranges)
- Roles are **explainable** (“this card fills X”)
- Features support roles; roles drive deck shape
