import pytest
from ptcgengine.card_models import EngineCardState


def test_definition_required_for_non_hidden():
    with pytest.raises(ValueError):
        EngineCardState(definition=None, current_hp=10, hidden=False)


def test_definition_allowed_for_hidden():
    st = EngineCardState(definition=None, current_hp=0, hidden=True)
    assert st.definition is None
    assert st.hidden is True
