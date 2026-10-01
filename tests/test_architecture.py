import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parent.parent / 'pathmanager'

# Allowed intra-package imports per source package. Dependencies point inward.
# `hosts` sits outside the clean architecture because it holds both UI and
# service logic.
ALLOWED: dict[str, set[str]] = {
    'utils': set(),
    'api': {'utils'},
    'adapters': {'api', 'utils'},
    'hosts': {'api', 'utils'},
    'services': {'api', 'adapters', 'hosts', 'utils'},
    'ui': {'adapters', 'api', 'hosts', 'services', 'utils'},
}


def imported_packages(path: Path) -> set[str]:
    """Return the pathmanager packages imported by a module."""

    tree = ast.parse(path.read_text())
    found: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ''
            if module == 'pathmanager':
                found.update(alias.name.split('.')[0] for alias in node.names)
            elif module.startswith('pathmanager.'):
                found.add(module.split('.')[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('pathmanager.'):
                    found.add(alias.name.split('.')[1])

    return {name for name in found if name in ALLOWED}


def source_package(path: Path) -> str | None:
    """Return the top-level package of a module, or None for root modules."""

    name = path.relative_to(PACKAGE).parts[0]
    return name if name in ALLOWED else None


@pytest.mark.parametrize('path', sorted(PACKAGE.rglob('*.py')), ids=str)
def test_import_boundaries(path: Path) -> None:
    source = source_package(path)
    if source is None:
        return

    for target in imported_packages(path):
        if target == source:
            continue
        assert target in ALLOWED[source], f'{source} must not import {target}: {path}'
