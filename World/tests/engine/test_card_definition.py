import copy
import pytest

from ptcgengine.card_models import CardDefinition, EngineCardState


def test_card_definition_immutable():
    cd = CardDefinition(id="P1", name="Pika", supertype="pokemon", hp=60, image=None)
    with pytest.raises(Exception):
        cd.name = "Other"  # type: ignore[misc]


def test_card_instance_mutation_rules():
    cd = CardDefinition(id="P1", name="Pika", supertype="pokemon", hp=60, image=None)
    inst = EngineCardState(definition=cd, current_hp=50)

    inst.current_hp = 40
    inst.status.append("paralyzed")
    inst.meta["xp"] = 10

    with pytest.raises(AttributeError):
        inst.some_new_field = 1  # type: ignore[attr-defined]


def test_card_instance_copy_shares_definition():
    cd = CardDefinition(id="P1", name="Pika", supertype="pokemon", hp=60, image=None)
    inst = EngineCardState(definition=cd, current_hp=50)
    inst2 = copy.copy(inst)

    assert inst.definition is inst2.definition
    assert inst2.current_hp == inst.current_hp
