# Card Feature Taxonomy

## 1) Mana & Resource Production

- `produces_mana`
- `produced_mana_colours: set[str]`
- `produced_mana_count` (per activation / trigger)
- `is_colour_fixing`
- `is_ramp`
- `is_burst_ramp` (one-shot)
- `is_repeatable_ramp`
- `is_land_ramp`
- `is_artifact_ramp`
- `is_creature_ramp`
- `is_cost_reducer`
- `reduces_generic_cost`
- `reduces_coloured_cost`
- `reduces_spell_type_cost` (creature / instant / sorcery / etc.)
- `ritual_like` (temporary mana)
- `mana_sink`
- `scales_with_mana`
- `produces_treasure`
- `produces_clue`
- `produces_food`
- `produces_blood`
- `produces_powerstone`

---

## 2) Card Advantage & Selection

- `draws_cards`
- `draw_count`
- `is_repeatable_draw`
- `is_burst_draw`
- `conditional_draw`
- `draw_on_cast`
- `draw_on_etb`
- `draw_on_attack`
- `draw_on_death`
- `loot_effect` (draw + discard)
- `rummage_effect` (discard + draw)
- `impulse_draw`
- `topdeck_play`
- `card_selection`
- `scry_effect`
- `surveil_effect`
- `tutor_effect`
- `is_tutor`
- `tutor_scope` (any / creature / land / artifact / enchantment / instant / sorcery)
- `tutor_to_hand`
- `tutor_to_top`
- `tutor_to_battlefield`
- `conditional_tutor`
- `reveal_required`

---

## 3) Interaction & Disruption

- `is_interaction`
- `is_spot_removal`
- `is_boardwipe`
- `is_mass_bounce`
- `is_counterspell`
- `is_tax_effect`
- `is_stax_light`
- `is_stax_heavy`
- `is_tapdown`
- `is_fight_spell`
- `is_burn_removal`
- `removal_scope` (creature / artifact / enchantment / planeswalker / any)
- `removal_speed` (instant / sorcery)
- `exile_removal`
- `sacrifice_removal`
- `edict_effect`
- `damage_prevention`
- `fog_effect`
- `graveyard_hate`
- `static_graveyard_hate`
- `activated_graveyard_hate`
- `hand_disruption`
- `wheel_effect`
- `library_disruption`
- `mass_land_destruction`
- `soft_lock_piece`

---

## 4) Protection & Resilience

- `provides_protection`
- `protects_commander`
- `gives_hexproof`
- `gives_shroud`
- `gives_indestructible`
- `gives_protection_colour`
- `phasing_effect`
- `blink_effect`
- `flicker_effect`
- `saves_from_boardwipe`
- `recursion`
- `recursion_scope`
- `self_recursion`
- `graveyard_to_hand`
- `graveyard_to_battlefield`
- `death_trigger`
- `dies_trigger`
- `regeneration_effect`
- `shield_counter_support`
- `totem_armour`

---

## 5) Win Conditions & Closing Power

- `is_finisher`
- `win_condition_direct`
- `win_condition_combo`
- `win_condition_combat`
- `combo_piece`
- `combo_enabler`
- `combo_payoff`
- `infinite_enabler`
- `alternate_win_condition`
- `overrun_effect`
- `mass_pump`
- `extra_combat`
- `extra_turn`
- `drain_effect`
- `life_loss_scaling`
- `mill_win_condition`
- `burn_to_face`
- `commander_damage_enabler`
- `unblockable_grant`
- `evasion_provider`

---

## 6) Token, Board Presence & Scaling

- `creates_tokens`
- `token_types: set[str]`
- `token_rate` (burst / repeatable)
- `token_scaling`
- `doubling_effect`
- `tripling_effect`
- `populate_effect`
- `incubate_effect`
- `amass_effect`
- `army_scaler`
- `go_wide_support`
- `go_tall_support`
- `anthem_effect`
- `static_buff`
- `counter_production`
- `+1/+1_counter_support`
- `counter_proliferation`
- `counter_removal`
- `experience_counter_support`

---

## 7) Sacrifice & Death Synergies

- `sac_outlet`
- `free_sac_outlet`
- `conditional_sac_outlet`
- `sacrifice_payoff`
- `dies_payoff`
- `aristocrats_piece`
- `on_sac_trigger`
- `on_death_trigger`
- `death_loop_piece`
- `reanimation_target`
- `self_sacrifice`
- `edict_synergy`
- `graveyard_filler`

---

## 8) Synergy & Archetype Signals

- `archetype_tags: set[str]`

  - `tokens`
  - `sacrifice`
  - `spellslinger`
  - `enchantress`
  - `artifacts`
  - `reanimator`
  - `blink`
  - `lands`
  - `lifegain`
  - `lifeloss`
  - `mill`
  - `tribal:<type>`

- `mechanic_keywords: set[str]`
- `trigger_density`
- `engine_piece`
- `engine_payoff`
- `engine_enabler`
- `critical_mass_piece`
- `parasitic_card`
- `standalone_goodstuff`

---

## 9) Curve, Tempo & Efficiency

- `mana_value`
- `early_game_play` (<=2 MV)
- `midgame_play`
- `late_game_play`
- `tempo_positive`
- `tempo_negative`
- `cheats_mana_cost`
- `cheats_into_play`
- `alternative_cost`
- `flash_speed`
- `sorcery_speed_only`
- `instant_speed_interaction`
- `setup_required`
- `immediate_impact`
- `delayed_value`

---

## 10) Colour Identity & Mana Base Relevance

- `colour_identity`
- `colour_intensity` (pip count)
- `mono_coloured`
- `multi_coloured`
- `colourless`
- `hybrid_mana`
- `phyrexian_mana`
- `snow_synergy`
- `domain_synergy`
- `devotion_synergy`
- `colour_requirement_strict`
- `splash_friendly`

---

## 11) Land-Specific Features

- `is_land`
- `is_utility_land`
- `enters_tapped`
- `conditional_untap`
- `landfall_synergy`
- `fetch_land`
- `shock_land`
- `triome`
- `cycling_land`
- `channel_land`
- `manland`
- `sac_land`
- `land_recursion_target`
- `land_destruction`
- `mana_smoothing_land`

---

## 12) Risk, Variance & Anti-Signals

- `high_variance`
- `low_floor`
- `requires_setup`
- `win_more`
- `dead_draw_late`
- `dead_draw_early`
- `meta_dependent`
- `table_hate_generator`
- `political_card`
- `symmetrical_effect`
- `helps_opponents`
- `anti_synergy_with_commander`
- `anti_synergy_with_archetype`
- `nonbo_risk`

---

## 13) Redundancy & Effect Identity (for pruning)

- `effect_signature` (hashable tuple)
- `effect_family` (e.g. `"2cmc_mana_rock"`)
- `redundancy_index`
- `strictly_better_exists`
- `strictly_worse_than`
- `functional_reprint`
- `unique_effect`

---

## 14) Price & Availability (soft signals only)

- `estimated_price`
- `price_band` (cheap / medium / expensive)
- `price_pressure_score`
- `budget_friendly_alternative_exists`
- `high_price_for_role`
- `low_price_for_role`
- `price_volatility_risk`

---

## 15) UX / Explainability Helpers

- `matched_role_rules: list[str]`
- `matched_synergy_rules: list[str]`
- `rejected_role_rules: list[str]`
- `score_components_triggered: list[str]`
- `primary_reason_codes: list[str]`
- `secondary_reason_codes: list[str]`

---

### Implementation notes (non-verbose, actionable)

- Most features can be derived with:

  - regex on `oracle_text`
  - `type_line`
  - mana cost parsing
  - simple keyword tables

- Features should be:

  - **boolean or small enums**
  - **cached per card**

- Scoring, pruning, and explanations should reference **feature IDs**, not text.
