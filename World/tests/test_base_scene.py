import pytest
from scenes.base_scene import BaseScene


def test_base_scene_enforces_abstract_interface():
    scene = BaseScene()
    with pytest.raises(NotImplementedError):
        scene.update(0.016)
    with pytest.raises(NotImplementedError):
        scene.draw(None)
    with pytest.raises(NotImplementedError):
        scene.handle_event(None)
