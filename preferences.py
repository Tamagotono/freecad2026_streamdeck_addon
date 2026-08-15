"""FreeCAD Stream Deck Addon - Preferences page
"""

import FreeCAD
from PySide import QtGui

_ROOT = "User parameter:BaseApp/StreamDeckAddon"



class StreamDeckPreferencePage:
  """Preferences page shown under Edit > Preferences > Stream Deck"""

  def __init__(self):

    self.form = QtGui.QWidget()
    self.form.setWindowTitle("General")
    outer = QtGui.QVBoxLayout(self.form)
    outer.setContentsMargins(8, 8, 8, 8)
    outer.setSpacing(8)

    # General
    gen_group = QtGui.QGroupBox("General")
    gen_layout = QtGui.QFormLayout(gen_group)
    self._addon_enabled = QtGui.QCheckBox()
    gen_layout.addRow("Enable Stream Deck addon", self._addon_enabled)
    outer.addWidget(gen_group)

    # Device
    dev_group = QtGui.QGroupBox("Device")
    dev_layout = QtGui.QFormLayout(dev_group)
    self._device_type = QtGui.QLineEdit()
    self._device_type.setPlaceholderText("Any")
    dev_layout.addRow("Device type filter:", self._device_type)
    self._device_serial = QtGui.QLineEdit()
    self._device_serial.setPlaceholderText("Any")
    dev_layout.addRow("Serial number filter:", self._device_serial)
    self._long_press = QtGui.QDoubleSpinBox()
    self._long_press.setRange(0.1, 5.0)
    self._long_press.setSingleStep(0.1)
    self._long_press.setDecimals(1)
    self._long_press.setSuffix(" s")
    dev_layout.addRow("Long-press duration:", self._long_press)
    outer.addWidget(dev_group)

    # Display
    disp_group = QtGui.QGroupBox("Display")
    disp_layout = QtGui.QFormLayout(disp_group)
    self._max_brightness = QtGui.QSpinBox()
    self._max_brightness.setRange(0, 100)
    self._max_brightness.setSuffix(" %")
    disp_layout.addRow("Maximum brightness:", self._max_brightness)
    self._font_family = QtGui.QFontComboBox()
    disp_layout.addRow("Key text font:", self._font_family)
    self._font_size = QtGui.QSpinBox()
    self._font_size.setRange(6, 72)
    self._font_size.setSuffix(" pt")
    disp_layout.addRow("Key text font size:", self._font_size)
    outer.addWidget(disp_group)

    # Screen Saver
    ss_group = QtGui.QGroupBox("Screen Saver")
    ss_layout = QtGui.QFormLayout(ss_group)
    self._fading_enabled = QtGui.QCheckBox()
    ss_layout.addRow("Enable screen saver", self._fading_enabled)
    self._fade_after = QtGui.QSpinBox()
    self._fade_after.setRange(0, 86400)
    self._fade_after.setSuffix(" s")
    ss_layout.addRow("Fade after inactivity:", self._fade_after)
    self._min_brightness = QtGui.QSpinBox()
    self._min_brightness.setRange(0, 100)
    self._min_brightness.setSuffix(" %")
    ss_layout.addRow("Fade to brightness:", self._min_brightness)
    self._fade_time = QtGui.QSpinBox()
    self._fade_time.setRange(0, 3600)
    self._fade_time.setSuffix(" s")
    ss_layout.addRow("Fade duration:", self._fade_time)
    outer.addWidget(ss_group)

    # Bracket Colors
    bc_group = QtGui.QGroupBox("Bracket Colors")
    bc_layout = QtGui.QFormLayout(bc_group)
    self._color_repeated = QtGui.QLineEdit()
    bc_layout.addRow("Toolbars on every page:", self._color_repeated)
    self._color_nav = QtGui.QLineEdit()
    bc_layout.addRow("Page navigation keys:", self._color_nav)
    self._color_expandable = QtGui.QLineEdit()
    bc_layout.addRow("Expandable tools:", self._color_expandable)
    outer.addWidget(bc_group)

    # Toolbar Lists
    tl_group = QtGui.QGroupBox("Toolbar Lists")
    tl_layout = QtGui.QFormLayout(tl_group)
    self._excluded_toolbars = QtGui.QLineEdit()
    self._excluded_toolbars.setPlaceholderText("Comma-separated toolbar names")
    tl_layout.addRow("Excluded toolbars:", self._excluded_toolbars)
    self._repeated_toolbars = QtGui.QLineEdit()
    self._repeated_toolbars.setPlaceholderText("Comma-separated toolbar names")
    tl_layout.addRow("Toolbars on every page:", self._repeated_toolbars)
    outer.addWidget(tl_group)

    # Start/Stop Commands
    cmd_group = QtGui.QGroupBox("Start/Stop Commands")
    cmd_layout = QtGui.QFormLayout(cmd_group)
    self._cmd_start = QtGui.QLineEdit()
    cmd_layout.addRow("Command on start:", self._cmd_start)
    self._cmd_stop = QtGui.QLineEdit()
    cmd_layout.addRow("Command on stop:", self._cmd_stop)
    outer.addWidget(cmd_group)

    outer.addStretch()



  def loadSettings(self):

    pg = FreeCAD.ParamGet(_ROOT)
    self._addon_enabled.setChecked(pg.GetBool("Enabled", True))

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Filters")
    self._device_type.setText(pg.GetString("UseDeviceType", ""))
    self._device_serial.setText(pg.GetString("UseDeviceSerial", ""))

    pg = FreeCAD.ParamGet(_ROOT + "/Device/keys")
    self._long_press.setValue(pg.GetFloat("LongKeyPressDurationSeconds", 0.5))

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/Brightness")
    self._max_brightness.setValue(pg.GetUnsigned("BrightnessPercent", 80))

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/Text")
    family = pg.GetString("KeyTextFontFamily", "")
    if family:
      self._font_family.setCurrentFont(QtGui.QFont(family))
    self._font_size.setValue(pg.GetUnsigned("KeyTextFontSize", 14))

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/ScreenSaver")
    self._fading_enabled.setChecked(pg.GetBool("Enabled", True))
    self._fade_after.setValue(pg.GetUnsigned("FadeWhenUserInactiveForSeconds", 300))
    self._min_brightness.setValue(pg.GetUnsigned("FadeToBrightness", 0))
    self._fade_time.setValue(pg.GetUnsigned("FadeTimeSeconds", 10))

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/BracketColors")
    self._color_repeated.setText(pg.GetString("ToolbarsOnEveryPage", "Blue"))
    self._color_nav.setText(pg.GetString("PageNavigationKeys", "Blue"))
    self._color_expandable.setText(pg.GetString("ExpandableTools", "Red"))

    pg = FreeCAD.ParamGet(_ROOT + "/ToolbarLists")
    self._excluded_toolbars.setText(
      pg.GetString("ToolbarsExcluded_CommaSeparated", ""))
    self._repeated_toolbars.setText(
      pg.GetString("ToolbarsOnEveryPage_CommaSeparated", ""))

    pg = FreeCAD.ParamGet(_ROOT + "/StartStopCommands")
    self._cmd_start.setText(pg.GetString("ExecuteShellCommandWhenStarting", ""))
    self._cmd_stop.setText(pg.GetString("ExecuteShellCommandWhenStopping", ""))



  def saveSettings(self):

    pg = FreeCAD.ParamGet(_ROOT)
    pg.SetBool("Enabled", self._addon_enabled.isChecked())

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Filters")
    pg.SetString("UseDeviceType", self._device_type.text())
    pg.SetString("UseDeviceSerial", self._device_serial.text())

    pg = FreeCAD.ParamGet(_ROOT + "/Device/keys")
    pg.SetFloat("LongKeyPressDurationSeconds", self._long_press.value())

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/Brightness")
    pg.SetUnsigned("BrightnessPercent", self._max_brightness.value())

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/Text")
    pg.SetString("KeyTextFontFamily", self._font_family.currentFont().family())
    pg.SetUnsigned("KeyTextFontSize", self._font_size.value())

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/ScreenSaver")
    pg.SetBool("Enabled", self._fading_enabled.isChecked())
    pg.SetUnsigned("FadeWhenUserInactiveForSeconds", self._fade_after.value())
    pg.SetUnsigned("FadeToBrightness", self._min_brightness.value())
    pg.SetUnsigned("FadeTimeSeconds", self._fade_time.value())

    pg = FreeCAD.ParamGet(_ROOT + "/Device/Display/BracketColors")
    pg.SetString("ToolbarsOnEveryPage", self._color_repeated.text())
    pg.SetString("PageNavigationKeys", self._color_nav.text())
    pg.SetString("ExpandableTools", self._color_expandable.text())

    pg = FreeCAD.ParamGet(_ROOT + "/ToolbarLists")
    pg.SetString("ToolbarsExcluded_CommaSeparated",
      self._excluded_toolbars.text())
    pg.SetString("ToolbarsOnEveryPage_CommaSeparated",
      self._repeated_toolbars.text())

    pg = FreeCAD.ParamGet(_ROOT + "/StartStopCommands")
    pg.SetString("ExecuteShellCommandWhenStarting", self._cmd_start.text())
    pg.SetString("ExecuteShellCommandWhenStopping", self._cmd_stop.text())
