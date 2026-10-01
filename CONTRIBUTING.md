# Contributing

## Development

To get started:

```sh
uv venv --python 3.13
uv pip install -e ".[dev]"
pre-commit install
```

Run the checks:

```sh
ruff format examples pathmanager tests
ruff check --select I --fix examples pathmanager tests
ruff check examples pathmanager tests
ty check
pytest
```

## Project layout

```text
pathmanager/
├── api/          # Domain data (schema, styled items)
├── adapters/     # Persistence and other side effects (storage)
├── hosts/        # Host integrations outside the clean architecture (houdini)
├── services/     # Application use cases (plugins)
└── ui/           # Qt code: app/ (this application) and widgets/ (reusable)
├── utils/        # Shared helpers (text, path, thread)
```

Dependencies point inward: `ui` → `services`/`hosts` → `adapters` → `api` → `utils`.
The boundaries are enforced by `tests/test_architecture.py`.

## Updating Icons

The material icons are vendored into `pathmanager/qt_material_icons` with
[qt-material-icons]. To regenerate them after adding or removing an icon, run:

```sh
uv run qtmaterialicons -o pathmanager --names \
    block \
    cancel \
    check_box \
    check_box_outline_blank \
    check_circle \
    close \
    code \
    deployed_code \
    draft \
    error \
    folder \
    image \
    keyboard_arrow_down \
    keyboard_arrow_up \
    refresh \
    right_panel_close \
    right_panel_open \
    sort \
    stacks \
    text_snippet \
    undo \
    view_agenda \
    view_column
```

[qt-material-icons]: https://github.com/beatreichenbach/qt-material-icons

## Publish

```shell
semantic-release version
```

## Screenshot in Houdini

```python
from pathmanager.ui.app import repo
repo.screenshot()
```
