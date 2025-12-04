"""
Sanity check: World environment can import Engine CardInstance module.

This ensures the editable install of ptcgengine is wired correctly and that
future deck-builder code can rely on card_instance without breaking imports.
"""


def test_card_instance_imports():
    from ptcgengine.card_instance import CardInstance, create_instance  # noqa: F401
