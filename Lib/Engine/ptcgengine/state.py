from dataclasses import dataclass, field
from typing import List, Any
from .cards import BaseCard, PokemonCard, EnergyCard, TrainerCard
from .events import GameEvent

@dataclass
class PlayerState:
    deck: List[BaseCard] = field(default_factory=list)
    hand: List[BaseCard] = field(default_factory=list)
    active: PokemonCard | None = None
    bench: List[PokemonCard] = field(default_factory=list)
    discard: List[BaseCard] = field(default_factory=list)

@dataclass
class GameState:
    players: List[PlayerState] = field(
        default_factory=lambda: [PlayerState(), PlayerState()]
    )
    active_player: int = 0
    turn: int = 1
    phase: str = "start"
    turn_flags: dict = field(default_factory=dict)
    event_log: List[GameEvent] = field(default_factory=list)
    trainer: Any | None = None
    deck: Any | None = None

    def clone(self):
        import copy
        return copy.deepcopy(self)

    def __repr__(self):
        return f"<GameState turn={self.turn} AP={self.active_player} phase={self.phase}>"
