from pathlib import Path

from pathmanager.adapters.storage import StateManager
from pathmanager.adapters.storage.jsonfile import read_json, write_json
from pathmanager.adapters.storage.model import State


def test_read_json_missing(tmp_path: Path) -> None:
    assert read_json(tmp_path / 'missing.json') is None


def test_read_json_invalid(tmp_path: Path) -> None:
    path = tmp_path / 'invalid.json'
    path.write_text('{')
    assert read_json(path) is None


def test_write_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / 'nested' / 'data.json'
    assert write_json({'a': 1}, path) is True
    assert read_json(path) == {'a': 1}


def test_state_manager_missing(tmp_path: Path) -> None:
    manager = StateManager(tmp_path / 'state.json')
    assert manager.get().browser == {}


def test_state_manager_roundtrip(tmp_path: Path) -> None:
    manager = StateManager(tmp_path / 'state.json')
    state = State(
        browser={
            'column_visibility': {'param_name': False},
            'splitter_sizes': [1, 2],
            'filters': {'status': {'value': ['found'], 'inverted': True}},
        }
    )
    manager.set(state)

    loaded = manager.get()
    assert loaded.browser == {
        'column_visibility': {'param_name': False},
        'splitter_sizes': [1, 2],
        'filters': {'status': {'value': ['found'], 'inverted': True}},
    }


def test_state_manager_reset(tmp_path: Path) -> None:
    path = tmp_path / 'state.json'
    path.write_text('{}')
    StateManager(path).reset()
    assert not path.exists()
