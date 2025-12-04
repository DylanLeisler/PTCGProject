from dataclasses import dataclass, field


@dataclass
class Attack:
    # NOTE:
    # This class is metadata-only.
    # All gameplay rules (attacks, damage, effects, evolution)
    # are implemented *exclusively* inside the functional PTCGEngine.
    name: str = ""
    damage: str | int = ""
    itemized_cost: list[str] = field(default_factory=list)
    total_cost: int | None = None
    description: str = ""
