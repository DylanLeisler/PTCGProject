from ptcgengine.card_identity import compute_revision, make_canonical_id
from ptcgengine.card_instance import create_instance


def test_canonical_id_is_deterministic():
    a = make_canonical_id("PTCG", "PIKACHU-BASE")
    b = make_canonical_id("PTCG", "PIKACHU-BASE")
    assert a.canonical_id == b.canonical_id
    assert a.namespace == "PTCG"
    assert a.definition_id == "PIKACHU-BASE"


def test_canonical_id_changes_with_namespace_or_definition():
    a = make_canonical_id("PTCG", "PIKACHU-BASE")
    b = make_canonical_id("FANMOD", "PIKACHU-BASE")
    c = make_canonical_id("PTCG", "RAICHU-BASE")
    assert a.canonical_id != b.canonical_id
    assert a.canonical_id != c.canonical_id


def test_revision_hash_ignores_key_order():
    meta1 = {"level": 5, "xp": 1200, "nickname": "Sparky"}
    meta2 = {"nickname": "Sparky", "xp": 1200, "level": 5}
    r1 = compute_revision(meta1)
    r2 = compute_revision(meta2)
    assert r1.hash == r2.hash


def test_card_instance_revision_changes_on_meta_update():
    meta1 = {"level": 1, "xp": 10}
    inst1 = create_instance("PIKACHU-BASE", meta=meta1, namespace="PTCG")

    meta2 = {"level": 2, "xp": 120}
    inst2 = inst1.with_updated_meta(meta2)

    # Canonical identity remains stable
    assert inst1.canonical_id == inst2.canonical_id

    # Revision hash must change as metadata changes
    assert inst1.revision_hash != inst2.revision_hash

    # Meta is updated as expected
    assert inst2.meta == meta2
