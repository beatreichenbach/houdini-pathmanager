import logging
from abc import ABC
from typing import Sequence

from qt_parameters import ParameterForm

from pathmanager import schema, utils


class Plugin(ABC):
    name: str
    label: str = ''

    def __init__(self) -> None:
        if not self.label:
            self.label = utils.title(self.name)

        self.logger = logging.getLogger(
            f'{__package__}.plugins.{self.__class__.__name__}'
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        for item in items:
            if item.preview:
                item.path = item.preview.path
                item.preview = schema.Item.Preview()

    def form(self) -> ParameterForm | None:
        return None

    def _get_difference(self, str_a: str, str_b: str) -> str:
        min_length = min(len(str_a), len(str_b))
        for i in range(min_length):
            if str_a[i] != str_b[i]:
                return str_b[i:]
        return str_b[min_length:]

    def _get_preview(self, path: str, original: str) -> schema.Item.Preview:
        preview = schema.Item.Preview(
            path=path, highlight=self._get_difference(original, path)
        )
        return preview
