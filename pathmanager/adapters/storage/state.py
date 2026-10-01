import dataclasses
import logging
from pathlib import Path

import platformdirs

from .jsonfile import read_json, write_json
from .model import State

logger = logging.getLogger(__name__)

PACKAGE_NAME = 'houdini-pathmanager'


class StateManager:
    """Read and write the panel state to a JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            directory = Path(platformdirs.user_state_dir(PACKAGE_NAME))
            path = directory / 'state.json'
        self.path = path

    def get(self) -> State:
        data = read_json(self.path) or {}
        return State(browser=data.get('browser', {}))

    def set(self, state: State) -> None:
        write_json(dataclasses.asdict(state), self.path)

    def reset(self) -> None:
        self.path.unlink(missing_ok=True)
