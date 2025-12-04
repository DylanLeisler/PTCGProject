from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "Lib" / "Engine"
if str(ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(ENGINE_PATH))


def test_ptcgengine_import():
    import ptcgengine.api as api
    state = api.initial_state()
    assert state is not None
