import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def read_json(path: Path) -> dict[str, Any] | None:
    """Return the data read from a JSON file, or None if it cannot be read."""

    if not path.exists():
        return None

    try:
        return json.loads(path.read_text())
    except OSError as e:
        logger.warning(f'Could not read file: {path}', exc_info=e)
    except json.JSONDecodeError as e:
        logger.debug(f'Failed to decode data: {path}', exc_info=e)
        logger.warning(f'Could not load data from file: {path}')
    return None


def write_json(data: dict[str, Any], path: Path, indent: int | None = 2) -> bool:
    """Write data as JSON to a path and return whether it succeeded."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=indent))
    except (OSError, TypeError, ValueError) as e:
        logger.error(f'Could not write file: {path}', exc_info=e)
        return False
    return True
