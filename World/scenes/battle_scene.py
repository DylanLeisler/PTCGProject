from __future__ import annotations

from typing import Any

import pygame

from scenes.base_scene import BaseScene

# We try to import the real engine API.
# Tests can monkeypatch this 'api' name.
try:
    from ptcgengine import api  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - in tests we monkeypatch 'api'
    api = None  # type: ignore[assignment]


class BattleScene(BaseScene):
    """
    Hybrid BattleScene:
    - Engine state (self.state) is treated as immutable and comes from ptcgengine.api.
    - UI state (selection index, log) is local and purely presentational.
    - Actions are taken from api.get_available_actions(self.state).
    - When an action is chosen, we call api.step(state, action) to get the next state.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        scene_manager: Any | None = None,
        initial_state: Any | None = None,
    ) -> None:
        self.screen = screen
        self.scene_manager = scene_manager

        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)

        # Engine state: canonical game rules state
        if initial_state is not None:
            self.state = initial_state
        elif api is not None:
            try:
                self.state = api.initial_state()
            except Exception:
                self.state = None
        else:
            self.state = None

        # UI state: local projection only
        self.actions: list[dict[str, Any]] = []
        self.selected_action_index: int = 0
        self.log: list[str] = []

        # --- Declarative UI integration ---
        from ui.ui_state import BattleUIState
        from ui.layout import BattleLayout
        from ui.renderer import BattleRenderer

        self._BattleUIState = BattleUIState
        self._layout = BattleLayout(self.screen.get_size())
        self._renderer = BattleRenderer(screen)

        if self.state is None:
            try:
                from ptcgengine.state import GameState
                self.state = GameState()
            except Exception:
                self.state = None

        if self.state is not None and api is not None:
            self._refresh_actions()
        else:
            self.actions = []

    # ---------------------------
    # Internal helpers
    # ---------------------------
    def _refresh_actions(self) -> None:
        """Pull the current legal actions from the engine."""
        if api is None or self.state is None:
            self.actions = []
            self.selected_action_index = 0
            return

        acts = api.get_available_actions(self.state)
        # Ensure it's a list of dicts for UI
        self.actions = list(acts)
        if not self.actions:
            self.selected_action_index = 0
        else:
            self.selected_action_index = min(self.selected_action_index, len(self.actions) - 1)

    def _log_action(self, action: dict[str, Any]) -> None:
        label = str(action.get("label") or action.get("type") or repr(action))
        self.log.append(f"> {label}")
        # Trim log to avoid unbounded growth
        if len(self.log) > 100:
            self.log = self.log[-100:]

    def _apply_selected_action(self) -> None:
        """Apply the currently selected action via the engine."""
        if api is None or self.state is None or not self.actions:
            return

        action = self.actions[self.selected_action_index]
        self._log_action(action)

        # Engine now returns (next_state, events)
        result = api.step(self.state, action)
        if isinstance(result, tuple):
            next_state, events = result
        else:  # Defensive fallback
            next_state, events = result, []

        self.state = next_state

        # Convert structured events into text for the UI
        for ev in events:
            msg = self._format_event(ev)
            self.log.append(msg)
        self.log = self.log[-100:]

        self._refresh_actions()

    def _format_event(self, ev):
        """Convert structured event objects to readable text."""
        if getattr(ev, "type", None) == "attack":
            payload = getattr(ev, "payload", {}) or {}
            return f"{payload.get('source', 'Unknown')} dealt {payload.get('damage', '?')} damage to {payload.get('target', 'Unknown')}."
        return f"[{getattr(ev, 'type', 'event')}] {getattr(ev, 'payload', {})}"

    # ---------------------------
    # BaseScene interface
    # ---------------------------
    def update(self, dt: float) -> None:  # noqa: ARG002
        # No time-based animation yet; hook reserved for future work.
        return

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                # Exit battle: pop this scene
                if self.scene_manager is not None:
                    self.scene_manager.pop()

            elif event.key in (pygame.K_UP, pygame.K_k):
                if self.actions:
                    self.selected_action_index = (
                        self.selected_action_index - 1
                    ) % len(self.actions)

            elif event.key in (pygame.K_DOWN, pygame.K_j):
                if self.actions:
                    self.selected_action_index = (
                        self.selected_action_index + 1
                    ) % len(self.actions)

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_x):
                self._apply_selected_action()

    def draw(self, screen: pygame.Surface) -> None:
        # Build declarative UI state derived from engine state
        ui = self._BattleUIState.from_engine_state(
            self.state,
            self.actions,
            self.selected_action_index,
            self.log,
        )

        # Compute rectangles and render
        rects = self._layout.compute_rects()
        self._renderer.render(ui, rects)
