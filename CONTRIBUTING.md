# Contributing

## Development
```shell
python3.11 -m venv venv
venv/bin/python -m pip install -e ".[dev]"
```

## Publish

```shell
semantic-release version
```

## Screenshot in Houdini

```python
from pathmanager.ui import repo
repo.screenshot()
```
