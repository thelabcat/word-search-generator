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
from PySide6.QtCore import Slot, QMutex, QThread
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

from algorithm import (
    SIZE_FAC_DEFAULT,
    INTERSECT_BIASES,
    INTERSECT_BIAS_DEFAULT,
    )
from gui_common import GUICommon

# Size factor options
SIZE_FAC_RANGE = 1, 99


class QtWindow(QWidget, GUICommon):
    """The Qt superwidget"""

    def __init__(self):
        """The Qt superwidget"""
        QWidget.__init__(self)
        GUICommon.__init__(self)

        self.clipboard = QApplication.clipboard()
        self.mutex = QMutex()

        self.__intersect_bias = INTERSECT_BIASES[INTERSECT_BIAS_DEFAULT]
        self.build()

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
        self.use_hard_w.setChecked(True)
        self.busy_disable_widgets.append(self.use_hard_w)

        # The size factor control
        self.sf_spinbox = QSpinBox()
        self.sf_spinbox.setRange(*SIZE_FAC_RANGE)
        self.sf_spinbox.setValue(SIZE_FAC_DEFAULT)
        self.busy_disable_widgets.append(self.sf_spinbox)

        self.sf_label = QLabel(GUICommon.Lang.size_factor)
        self.sf_label.setBuddy(self.sf_spinbox)

        self.sf_layout = QHBoxLayout()
        self.sf_layout.addWidget(self.sf_label)
        self.sf_layout.addWidget(self.sf_spinbox, stretch=1)

        # The intersection bias choosing
        self.bias_label = QLabel(GUICommon.Lang.word_intersect_bias)

        self.bias_ops_layout = QHBoxLayout()
        for bias_name, bias_value in INTERSECT_BIASES.items():
            widget = QRadioButton(bias_name.capitalize())
            widget.bias_value = bias_value
            widget.toggled.connect(self.update_intersect_bias)
            if bias_name == INTERSECT_BIAS_DEFAULT:
                widget.setChecked(True)
            self.bias_ops_layout.addWidget(widget)
            self.busy_disable_widgets.append(widget)

        self.bias_layout = QVBoxLayout()
        self.bias_layout.addWidget(self.bias_label)
        self.bias_layout.addLayout(self.bias_ops_layout)

        # The text area
        self.entry_w = QPlainTextEdit()
        self.entry_w.textChanged.connect(self.on_input_text_changed)
        self.words_entry_raw = GUICommon.Lang.word_entry_default
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
        self.regulate_result_buttons()

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
        """Do progress updates on the generation"""
        self.mutex.lock()
        self.progress_bar.setValue(self.generator.index)
        self.mutex.unlock()

    @property
    def result_buttons_able(self) -> bool:
        """Are the result buttons enabled?"""
        return hasattr(self, "copypuzz_button") \
            and self.copypuzz_button.isEnabled()

    @result_buttons_able.setter
    def result_buttons_able(self, state: bool):
        """Enable or disable the result buttons"""
        if not (
                hasattr(self, "copypuzz_button") and
                hasattr(self, "copykey_button")
                ):
            return
        self.copypuzz_button.setEnabled(state)
        self.copykey_button.setEnabled(state)

    @property
    def gen_cancel_button_able(self) -> bool:
        """Is the generate button enabled?"""
        return hasattr(self, "gen_cancel_button") and self.gen_cancel_button.isEnabled()

    @gen_cancel_button_able.setter
    def gen_cancel_button_able(self, state: bool):
        """Enable or disable the generate button"""
        if not hasattr(self, "gen_cancel_button"):
            return
        self.mutex.lock()
        self.gen_cancel_button.setEnabled(state)
        self.mutex.unlock()

    @Slot()
    def on_gen_cancel_button_click(self):
        """Start or abort generation"""
        GUICommon.on_gen_cancel_button_click(self)

    def update_intersect_bias(self):
        """Set the current bias from the radiobuttons"""
        radiobutton = self.sender()
        if radiobutton.isChecked:
            self.__intersect_bias = self.sender().bias_value

    def update_gui_able(self):
        """Configure the GUI based on self.gui_op_running"""
        self.mutex.lock()
        for widget in self.busy_disable_widgets:
            widget.setEnabled(not self.gui_op_running)
        self.mutex.unlock()

    def configure_gen_cancel_button(self):
        """
        Visually turn the generate button into a cancel button or back appropriately
        """

        if not hasattr(self, "gen_cancel_button"):
            return

        self.mutex.lock()
        if self.gui_op_running:
            self.gen_cancel_button.setText(GUICommon.Lang.cancel_button)
        else:
            self.gen_cancel_button.setText(GUICommon.Lang.gen_button)
        self.mutex.unlock()

    @Slot()
    def generate_puzzle(self):
        """Generate a puzzle from the input words (threaded)"""
        self.progress_bar.setMaximum(len(self.current_words))
        self.thread = PuzzGenThread(self)
        self.thread.start()

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

    def run(self):
        """The threaded code"""
        self.parent._generate_puzzle()


def main():
    """Launch the GUI"""
    app = QApplication(sys.argv)
    window = QtWindow()
    window.show()
    app.exec()


# If this was not imported, run it
if __name__ == "__main__":
    main()
