# Changelog

## 0.1.0 - Initial Commit
- Engine + World prototypes
- Battle system stub
- Deck + Trainer persistence
- Test suite foundation


### Added
- Declarative UI integration pipeline (BattleUIState → BattleLayout → BattleRenderer).
- Card rendering system with sprite support and fallback placeholders.
- Perspective-aware engine accessors:
  - `get_human_hand()`
  - `get_opponent_hand()`
  - `get_human_entity()`
  - `get_opponent_entity()`
- Support for hidden cards (opponent hand renders as card backs).
- Tests covering:
  - UI state extraction paths
  - Rendering safety
  - Hidden-state model behavior
  - Engine accessor semantics

### Changed
- `CardInstance` has been replaced by `EngineCardState`.
- UI pipeline now derives card state from accessor API instead of raw engine objects.
- Hand rendering switches from text placeholder model to card-based visual layout.

### Breaking Changes
- Any code referencing `CardInstance` must now use `EngineCardState`.
- UI no longer reads engine state directly — it must use `api.get_*()` accessor functions.

### Notes
- This establishes the separation between *engine truth* and *player-visible UI state*.
- Hidden cards may now legally omit card metadata; revealed cards must contain full definitions.
