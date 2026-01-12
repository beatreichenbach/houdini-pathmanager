from __future__ import annotations

import dataclasses

from qtpy import QtCore

import tests
from pathmanager.tree import Field
from tests import application
from pathmanager.browser import Browser, Group


@dataclasses.dataclass
class Element:
    name: str = ''
    task: None = None


def main() -> None:
    with application():
        browser = Browser()
        browser.add_column(field=Field('status'))
        browser.add_column(field=Field('node_type'))
        browser.add_column(field=Field('node_path'))
        browser.add_column(field=Field('param'))
        browser.add_column(field=Field('path'))
        browser.add_column(field=Field('path_preview', editable=True))
        browser.show()

        elements = []
        for j in range(3):
            element = Element(name=f'element_{j:03d}')
            elements.append(element)

        browser.add_elements(elements)

        browser.resize(QtCore.QSize(640, 480))


if __name__ == '__main__':
    tests.init()
    main()
