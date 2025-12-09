#!/usr/bin/env python3
"""Word Search Generator Qt GUI

Present a GUI for the word search generator algorithm (Qt 6)

This file is part of Word Search Generator.

Word Search Generator is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

S.D.G."""

import sys
from PySide6.QtCore import Slot, QThread, QMetaObject
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QCheckBox,
    QLabel,
    QSpinBox,
    QRadioButton,
    QHBoxLayout,
    QVBoxLayout,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    )

from .algorithm import INTERSECT_BIAS_NAMES
from .gui_common import GUICommon


class QtWindow(QWidget, GUICommon):
    """The Qt superwidget"""

    def __init__(self):
        """The Qt superwidget"""
        QWidget.__init__(self)
        GUICommon.__init__(self)

        self.clipboard = QApplication.clipboard()

        self.__intersect_bias = GUICommon.Defaults.intersect_bias
        self.build()
        self.status_ticker_thread = StatusTicker(self)
        self.status_ticker_thread.start()

    def copy_to_clipboard(self, text: str):
        """copy text to the clipboard"""
        return self.clipboard.setText(text)

    @property
    def intersect_bias(self):
        """The intersection bias we are set to use"""
        return self.__intersect_bias

    def build(self):
        """Construct the GUI"""

        # Widgets to disable when we are busy
        self.busy_disable_widgets = []

        # Wether or not to use hard directions
        self.use_hard_w = QCheckBox(GUICommon.Lang.use_hard)
        self.use_hard_w.setChecked(GUICommon.Defaults.use_hard)
        self.busy_disable_widgets.append(self.use_hard_w)

        # The size factor control
        self.sf_spinbox = QSpinBox()
        self.sf_spinbox.setRange(*GUICommon.size_fac_range)
        self.sf_spinbox.setValue(GUICommon.Defaults.size_fac)
        self.busy_disable_widgets.append(self.sf_spinbox)

        self.sf_label = QLabel(GUICommon.Lang.size_factor)
        self.sf_label.setBuddy(self.sf_spinbox)

        self.sf_layout = QHBoxLayout()
        self.sf_layout.addWidget(self.sf_label)
        self.sf_layout.addWidget(self.sf_spinbox, stretch=1)

        # The intersection bias choosing
        self.bias_label = QLabel(GUICommon.Lang.word_intersect_bias)

        self.bias_ops_layout = QHBoxLayout()
        for bias_value, bias_name in INTERSECT_BIAS_NAMES.items():
            widget = QRadioButton(bias_name.capitalize())
            widget.bias_value = bias_value
            widget.toggled.connect(self.update_intersect_bias)
            if bias_value == GUICommon.Defaults.intersect_bias:
                widget.setChecked(True)
            self.bias_ops_layout.addWidget(widget)
            self.busy_disable_widgets.append(widget)

        self.bias_layout = QVBoxLayout()
        self.bias_layout.addWidget(self.bias_label)
        self.bias_layout.addLayout(self.bias_ops_layout)

        # The text area
        self.entry_w = QPlainTextEdit()
        self.entry_w.textChanged.connect(self.on_input_text_changed)
        self.busy_disable_widgets.append(self.entry_w)

        # The progress bar
        self.progress_bar = QProgressBar()

        # The generate button
        self.gen_cancel_button = QPushButton(GUICommon.Lang.gen_button)
        self.gen_cancel_button.clicked.connect(self.on_gen_cancel_button_click)

        # The result copying buttons
        self.copypuzz_button = QPushButton(GUICommon.Lang.copypuzz_button)
        self.copypuzz_button.clicked.connect(self.copy_puzzle)
        self.copykey_button = QPushButton(GUICommon.Lang.copykey_button)
        self.copykey_button.clicked.connect(self.copy_answer_key)
        self.resultbuttons_layout = QHBoxLayout()
        self.resultbuttons_layout.addWidget(self.copypuzz_button)
        self.resultbuttons_layout.addWidget(self.copykey_button)

        # We cannot do this until the generate and copy buttons exist
        self.words_entry_raw = GUICommon.Defaults.word_entry

        # The overall layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.use_hard_w)
        self.main_layout.addLayout(self.sf_layout)
        self.main_layout.addLayout(self.bias_layout)
        self.main_layout.addWidget(self.entry_w, stretch=1)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.gen_cancel_button)
        self.main_layout.addLayout(self.resultbuttons_layout)

        self.setWindowTitle(GUICommon.Lang.window_title)

    def progress_update(self):
        """Do progress updates on the generation (thread-safe)"""
        QMetaObject.invokeMethod(self, "_progress_update")

    @Slot()
    def _progress_update(self):
        """Do progress updates on the generation (slot)"""
        self.progress_bar.setValue(self.generator.index)

    def set_result_buttons_able(self, state: bool):
        """Enable or disable the result buttons (thread-safe)"""
        strstate = ("dis", "en")[state]
        QMetaObject.invokeMethod(self, f"_result_buttons_{strstate}able")

    @Slot()
    def _result_buttons_disable(self):
        """Disable the result buttons"""
        self._set_result_buttons_able(False)

    @Slot()
    def _result_buttons_enable(self):
        """Enable the result buttons"""
        self._set_result_buttons_able(True)

    def _set_result_buttons_able(self, state: bool):
        """Enable or disable the result buttons"""
        self.copypuzz_button.setEnabled(state)
        self.copykey_button.setEnabled(state)

    def set_gen_cancel_button_able(self, state: bool):
        """Enable or disable the generate button (thread-safe)"""
        #TODO, may not need thread-safe version
        strstate = ("dis", "en")[state]
        QMetaObject.invokeMethod(self, f"_gen_cancel_button_{strstate}able")

    @Slot()
    def _gen_cancel_button_disable(self):
        """Disable the generate/cancel button"""
        self.gen_cancel_button.setEnabled(False)

    @Slot()
    def _gen_cancel_button_enable(self):
        """Enable the generate/cancel button"""
        self.gen_cancel_button.setEnabled(True)

    @Slot()
    def on_gen_cancel_button_click(self):
        """Start or abort generation (slot)"""
        GUICommon.on_gen_cancel_button_click(self)

    def update_intersect_bias(self):
        """Set the current bias from the radiobuttons"""
        radiobutton = self.sender()
        if radiobutton.isChecked:
            self.__intersect_bias = self.sender().bias_value

    def update_progress_bar_max(self):
        """Set the progress bar to the appropriate maximum"""
        self.progress_bar.setMaximum(len(self.current_words))

    @Slot()
    def start_generation(self):
        """Create and launch the generation thread"""
        self.gen_thread = PuzzGenThread(self)
        self.gen_thread.start()

    def set_gen_cancel_button_mode(self, is_cancel: bool):
        """Visually change the gen/cancel button"""
        self.gen_cancel_button.setText((
                GUICommon.Lang.gen_button,
                GUICommon.Lang.cancel_button,
                )[is_cancel])

    def set_gui_able(self, state: bool):
        """Set if the GUI is currently enabled (thread-safe)"""
        #TODO, may not need thread-safe version
        strstate = ("dis", "en")[state]
        QMetaObject.invokeMethod(self, f"_gui_{strstate}able")

    @Slot()
    def _gui_disable(self):
        """Disable the gui"""
        self._set_gui_able(False)

    @Slot()
    def _gui_enable(self):
        """Enable the gui"""
        self._set_gui_able(True)

    def _set_gui_able(self, state: bool):
        """Set if the GUI is currently enabled"""
        for widget in self.busy_disable_widgets:
            widget.setEnabled(state)

    #@property
    def is_thread_running(self) -> bool:
        """Wether or not the generation thread is still running"""
        return bool(self.gen_thread and self.gen_thread.isRunning())

    @property
    def use_hard(self):
        """Wether or not to use hard directions"""
        return self.use_hard_w.isChecked()

    @property
    def size_factor(self):
        """The selected size factor of the puzzle"""
        return self.sf_spinbox.value()

    @property
    def words_entry_raw(self):
        """The raw entry in the text area"""
        return self.entry_w.toPlainText()

    @words_entry_raw.setter
    def words_entry_raw(self, new: str):
        """The raw entry in the text area"""
        self.entry_w.clear()
        self.entry_w.appendPlainText(new)


class PuzzGenThread(QThread):
    """Run puzzle generation in a Qt thread"""

    def __init__(self, parent: QtWindow):
        """
        Run puzzle generation in a Qt thread

        Args:
            parent (QtWindow): The parent window
        """
        super().__init__(parent)
        self.parent = parent
        self.setObjectName(GUICommon.Lang.gen_thread)

    def run(self):
        """The threaded code"""
        self.parent.generate_puzzle()

class StatusTicker(QThread):
    """Run GUI status_tick in a Qt thread constantly"""

    def __init__(self, parent: QtWindow):
        """
        Run puzzle generation in a Qt thread

        Args:
            parent (QtWindow): The parent window
        """
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("StatusTicker")

    def run(self):
        """The threaded code"""
        while not self.isInterruptionRequested():
            self.parent.status_tick()
            self.sleep(GUICommon.status_tick_interval)

def main():
    """Launch the GUI"""
    app = QApplication(sys.argv)
    window = QtWindow()
    window.show()
    app.exec()
    window.status_ticker_thread.requestInterruption()


# If this was not imported, run it
if __name__ == "__main__":
    main()
