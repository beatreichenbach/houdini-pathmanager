import pytest
from qtpy import QtGui

from pathmanager.api import meta
from pathmanager.api.schema import Status, Statuses


def test_iteration_order() -> None:
    assert [status.name for status in Statuses] == ['missing', 'found', 'expression']


def test_len() -> None:
    assert len(Statuses) == 3


def test_contains_member() -> None:
    assert Statuses.FOUND in Statuses
    assert Status('found') in Statuses


def test_contains_string() -> None:
    assert 'FOUND' in Statuses
    assert 'found' in Statuses
    assert 'bogus' not in Statuses


def test_getitem_by_key_and_name() -> None:
    assert Statuses['MISSING'] is Statuses.MISSING
    assert Statuses['FoUnD'] is Statuses.FOUND
    assert Statuses[0] is Statuses.MISSING


def test_getitem_unknown() -> None:
    with pytest.raises(KeyError):
        Statuses['bogus']


def test_get() -> None:
    assert Statuses.get('found') is Statuses.FOUND
    assert Statuses.get('bogus') is None


def test_subclass_collects_inherited_members() -> None:
    class Extended(Statuses):
        CUSTOM = Status('custom', icon='star')

    assert [status.name for status in Extended] == [
        'missing',
        'found',
        'expression',
        'custom',
    ]
    assert Extended.MISSING is Statuses.MISSING


def test_non_styled_attributes_are_not_members() -> None:
    class Extended(Statuses):
        CONSTANT = 3

        @property
        def helper(self) -> str:
            return 'x'

    assert [status.name for status in Extended] == ['missing', 'found', 'expression']


def test_color_accepts_name_and_qcolor() -> None:
    assert meta.StyledItem('x', color='#ff0000').color() == QtGui.QColor('#ff0000')
    color = QtGui.QColor('#00ff00')
    assert meta.StyledItem('x', color=color).color() == color
    assert meta.StyledItem('x').color() is None


def test_icon_falsy_returns_none() -> None:
    assert meta.StyledItem('x', icon=None).icon() is None
    assert meta.StyledItem('x', icon='').icon() is None


def test_icon_unsupported_raises() -> None:
    item = meta.StyledItem('x', icon=1.5)
    with pytest.raises(TypeError):
        item.icon()


def test_eq_is_type_aware() -> None:
    assert Status('found') == Statuses.FOUND
    assert meta.StyledItem('x') != 'x'
