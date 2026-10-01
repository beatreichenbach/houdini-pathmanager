from __future__ import annotations

from typing import ClassVar

from . import base, cp, find, mv, relative, replace, set_directory, version


class PluginManager:
    _instance: ClassVar[PluginManager | None] = None

    def __new__(cls) -> PluginManager:
        instance = cls._instance
        if instance is None:
            instance = super().__new__(cls)
            instance._init()
            cls._instance = instance
        return instance

    def _init(self) -> None:
        plugins = (
            replace.ReplacePlugin(),
            set_directory.SetDirectoryPlugin(),
            cp.CopyPlugin(),
            mv.MovePlugin(),
            find.FindPlugin(),
            version.VersionPlugin(),
            relative.RelativePlugin(),
        )
        self._plugins: dict[str, base.Plugin] = {
            plugin.name: plugin for plugin in plugins
        }

    def get_plugins(self) -> tuple[base.Plugin, ...]:
        return tuple(self._plugins.values())

    def get(self, name: str) -> base.Plugin | None:
        return self._plugins.get(name)
