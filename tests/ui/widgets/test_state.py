import dataclasses

from pathmanager.ui.widgets.state import FilterBrowserState, FilterState


def test_from_dict_roundtrip() -> None:
    state = FilterBrowserState(
        column_visibility={'param_name': False},
        splitter_sizes=(1, 2),
        filters={'status': FilterState(value=('found',), inverted=True)},
    )
    data = dataclasses.asdict(state)
    assert FilterBrowserState.from_dict(data) == state


def test_from_dict_empty() -> None:
    state = FilterBrowserState.from_dict({})
    assert state.column_visibility == {}
    assert state.splitter_sizes == ()
    assert state.filters == {}
