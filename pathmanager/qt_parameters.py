# noinspection PyUnresolvedReferences
from qt_parameters import *

try:
    import hou

    from .hosts.houdini import HoudiniPathParameter as PathParameter
    from .hosts.houdini import HoudiniEnumParameter as EnumParameter
except ModuleNotFoundError:
    pass
