from dataclasses import dataclass, field


@dataclass
class Card:
    # NOTE:
    # This class is metadata-only.
    # All gameplay rules (attacks, damage, effects, evolution)
    # are implemented *exclusively* inside the functional PTCGEngine.
    name: str
    card_id: str
    supertype: str
    properties: list[str] = field(default_factory=list)
    description: str = ""
    image: str = ""



    
