import json
import logging
import os
from typing import Any

import platformdirs

PACKAGE_NAME = 'houdini-pathmanager'

logger = logging.getLogger(__name__)


class JSONStorage:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self) -> None: ...

    @staticmethod
    def read(path: str) -> dict:
        with open(path, 'r') as f:
            return json.load(f)

    @staticmethod
    def write(data: Any, path: str) -> None:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'w') as file:
            json.dump(data, file, indent=2)


class Storage(JSONStorage):
    def _init(self):
        self.state_dir = platformdirs.user_state_dir(PACKAGE_NAME)

        self._state_path = os.path.join(self.state_dir, 'state.json')
        logger.debug(self._state_path)

    def get_state(self) -> dict:
        try:
            state = self.read(self._state_path)
            return state
        except OSError:
            ...
        except json.JSONDecodeError:
            ...
        return {}

    def set_state(self, state: dict) -> None:
        try:
            self.write(state, self._state_path)
        except OSError:
            ...
        except ValueError:
            ...
