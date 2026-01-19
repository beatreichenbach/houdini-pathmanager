from pathmanager.houdini.host import HoudiniHost
from pathmanager.ui.manager import PathManager

widgets: list[PathManager] = []


def get_manager() -> PathManager:
    widget = PathManager()
    host = HoudiniHost()
    widget.set_host(host)
    widgets.append(widget)
    return widget


def reload() -> None:
    for widget in widgets:
        try:
            widget.reload()
        except RuntimeError:
            pass
