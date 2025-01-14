import os
from PyQt5 import QtGui

__all__ = [
    "Colors",
    "Icons",
    "StyleSheets"
]

class Icons:
    # Determine the root directory of the icons
    __root = os.path.join(os.path.dirname(__file__), "icons")
    
    # Define the path to the gear icon
    gear_icon = os.path.join(__root, "gearDark16.png")
    gear_icon_rollover = os.path.join(__root, "gearDark16_hilite.png")
    plus_icon = os.path.join(__root, "plus16.png")
    plus_icon_rollover = os.path.join(__root, "plusHilite16.png")
