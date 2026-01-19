# noinspection PyUnresolvedReferences
from qt_parameters import *

try:
    from pathmanager.houdini import (
        HoudiniEnumParameter as EnumParameter,
        HoudiniPathParameter as PathParameter,
    )
except ImportError:
    pass
