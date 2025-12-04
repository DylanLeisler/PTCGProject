from ptcgengine.card_models import CardDefinition, EngineCardState


def test_card_instance_construction_missing_image_ok():
    cd = CardDefinition(id="P1", name="NoImg", supertype="pokemon", hp=10)
    inst = EngineCardState(definition=cd, current_hp=10)
    assert inst.definition.image is None
    assert inst.current_hp == 10
