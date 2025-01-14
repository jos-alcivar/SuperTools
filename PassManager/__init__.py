from __future__ import absolute_import

import Katana
from . import v1 as PassManager

if PassManager:
    PluginRegistry = [
        ("SuperTool", 2, "PassManager",
            (PassManager.PassManagerNode,
                PassManager.GetEditor)
        )
    ]