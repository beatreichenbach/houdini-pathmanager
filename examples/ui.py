import sys

from examples import application, houdini, init

sys.modules['pathmanager.hosts.houdini'] = houdini

from pathmanager.ui import Parameters, PathManager  # noqa: E402


def show_manager() -> None:
    with application():
        manager = PathManager()
        manager.show()


def show_parameters() -> None:
    with application():
        widget = Parameters()
        widget.show()


if __name__ == '__main__':
    init()
    show_manager()
