"""FreeCAD Stream Deck Addon - Entry point
"""

## Modules
#

import streamdeck_addon as addon
from preferences import StreamDeckPreferencePage



## Entry point
FreeCADGui.addPreferencePage(StreamDeckPreferencePage, "Stream Deck")
addon.start(FreeCAD)
