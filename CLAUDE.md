# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

FreeCAD addon that mirrors FreeCAD toolbar tools onto an Elgato Stream Deck macropad in real-time. When a Stream Deck key is pressed, the corresponding FreeCAD tool activates.

The addon runs inside FreeCAD's Python environment (Python 3.11 in FreeCAD 1.1.x AppImage). It uses PySide6 via FreeCAD's compatibility shim (`Ext/PySide/`) which maps `from PySide import QtCore, QtGui` to PySide6.

## Architecture

- **`InitGui.py`** — Entry point. FreeCAD executes this on startup, injecting `FreeCAD` as a global. Imports `streamdeck_addon` and calls `start(FreeCAD)`.
- **`streamdeck_addon.py`** — Main program. Owns the QTimer loop that polls the Stream Deck and syncs toolbar state.
- **`gui_actions.py`** — Extracts toolbar/action data from the FreeCAD main window using Qt introspection (`findChildren`). Converts `QIcon` to PIL images via `QBuffer`.
- **`streamdeck_comm.py`** — Stream Deck device abstraction: open/close, key image upload, brightness, input event polling.
- **`streamdeck_pages.py`** — Pure Python: builds paginated key layouts from toolbar actions as encoded strings.
- **`parameters.py`** — Reads/writes user settings via `FreeCAD.ParamGet()`. Attaches a parameter observer for live updates.

The addon directory is added to `sys.path` by FreeCAD, so all inter-module imports are bare absolute imports (e.g. `from parameters import UserParameters`).

## Dependencies

`pillow` and `streamdeck` are declared in `package.xml` and installed automatically by the FreeCAD Addon Manager. They are not tracked in git. For manual installs or AppImage users, install them into the addon directory with:

    python3 -m pip install --target=<addon-dir> pillow streamdeck

## FreeCAD 1.1.x Compatibility Notes

FreeCAD 1.1.x switched from PySide2 to PySide6. The `Ext/PySide/` shim handles this transparently — `QtGui.py` re-exports both `PySide6.QtGui.*` and `PySide6.QtWidgets.*`, so `QToolBar`, `QToolButton`, `QMenu` etc. remain available under `QtGui`.

Key fixes applied for FreeCAD 1.1.x:
- `QBuffer` must be opened with `open(QIODevice.WriteOnly)` before saving a pixmap to it (Qt6 requirement).
- Icon data is read from `qbf.data()` (not from the QByteArray passed to the constructor), since QByteArray is a value type in PySide6 Python bindings.
- Font loading uses a try/except fallback chain: bundled file → system font search → `ImageFont.load_default(size=...)`.
- `broken_image` reference in `set_key()` was a typo; corrected to `self.broken_image`.

## Settings

All user parameters live under `Tools > Edit Parameters > BaseApp > StreamDeckAddon`. Changes take effect immediately without restarting FreeCAD.

## No Build Step

This is a pure Python addon. There is no build process. Changes to `.py` files take effect after restarting FreeCAD (or deleting `__pycache__/*.pyc` to force recompilation).
