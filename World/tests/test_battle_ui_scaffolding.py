from types import SimpleNamespace

import pygame

from ui.ui_state import BattleUIState, PokemonView
from ui.layout import BattleLayout
from ui.renderer import BattleRenderer


class DummyPlayer(SimpleNamespace):
    pass


class DummyActive(SimpleNamespace):
    pass


def test_ui_state_from_minimal_engine_state():
    active_card = DummyActive(name="Pikachu", hp=30, max_hp=60)
    player = DummyPlayer(active=active_card, hand=[1, 2, 3])
    state = SimpleNamespace(players=[player, player], active_player=0)

    actions = [{"type": "attack", "label": "Thunder Jolt"}, {"type": "pass"}]
    log = ["Pikachu used Thunder Jolt!", "It did 30 damage."]

    ui = BattleUIState.from_engine_state(state, actions, selected_action_index=0, log_lines=log)

    assert ui.active_pokemon is not None
    assert ui.active_pokemon.name == "Pikachu"
    assert ui.hand_size == 3
    assert ui.actions == ["Thunder Jolt", "pass"]
    assert "Thunder Jolt" in ui.log_lines[-1]


def test_layout_rects_cover_screen_without_overlap_crash():
    pygame.init()
    size = (800, 600)
    layout = BattleLayout(size)
    rects = layout.compute_rects()

    assert {"opponent", "active", "hand", "actions", "log"} <= set(rects.keys())
    for key, r in rects.items():
        if isinstance(r, list):  # skip hand_slots list
            continue
        assert r.right <= size[0] + 1
        assert r.bottom <= size[1] + 1


def test_renderer_runs_without_crashing(monkeypatch):
    pygame.init()
    screen = pygame.Surface((800, 600))
    renderer = BattleRenderer(screen)

    ui = BattleUIState(
        active_pokemon=PokemonView(name="Pikachu", current_hp=30, max_hp=60),
        opponent_pokemon=None,
        hand_size=5,
        actions=["Thunder Jolt", "Pass"],
        selected_action_index=0,
        log_lines=["Battle started."],
    )

    layout = BattleLayout(screen.get_size())
    rects = layout.compute_rects()

    renderer.render(ui, rects)
