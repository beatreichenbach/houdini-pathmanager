from . import base, cp, find, mv, relative, replace, set_directory, version


class PluginManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

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
        self._plugins = {plugin.name: plugin for plugin in plugins}

    def get_plugins(self) -> tuple[base.Plugin, ...]:
        return tuple(self._plugins.values())

    def get(self, name: str) -> base.Plugin | None:
        return self._plugins.get(name)
