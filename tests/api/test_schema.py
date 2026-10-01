from pathmanager.api.schema import Item, NodeType, ParmTypes


def item(raw: str) -> Item:
    return Item(
        parm_name='file',
        parm_type=ParmTypes.FILE,
        node_path='/stage/file',
        node_type=NodeType('file', 'sop'),
        path=Item.Path(raw=raw),
    )


def test_path_normalizes_backslashes() -> None:
    path = Item.Path(raw='C:\\HIP\\geo\\cube.obj', expanded='C:\\HIP\\geo\\cube.obj')
    assert path.raw == 'C:/HIP/geo/cube.obj'
    assert path.expanded == 'C:/HIP/geo/cube.obj'


def test_set_preview_matches_normalized_path() -> None:
    obj = item('C:\\HIP\\geo\\cube.obj')
    obj.set_preview('C:/HIP/geo/cube.obj')
    assert obj.preview.raw == ''


def test_set_preview_uses_forward_slashes() -> None:
    obj = item('C:\\HIP\\geo\\cube.obj')
    obj.set_preview('C:\\HIP\\geo\\cube.001.obj')
    assert obj.preview.raw == 'C:/HIP/geo/cube.001.obj'
