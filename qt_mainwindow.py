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
from PySide6.QtCore import Slot
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
    QPushButton,
    QMessageBox,
    )

from algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    SIZE_FAC_DEFAULT,
    INTERSECT_BIASES,
    INTERSECT_BIAS_DEFAULT,
    )

# Size factor options
SIZE_FAC_RANGE = 1, 99


class QtWindow(QWidget):
    """The Qt superwidget"""

    def __init__(self):
        """The Qt superwidget"""
        super().__init__()
        self.clipboard = QApplication.clipboard()
        self.intersect_bias = INTERSECT_BIASES[INTERSECT_BIAS_DEFAULT]
        self.build()

    def build(self):
        """Construct the GUI"""

        # Wether or not to use hard directions
        self.use_hard_w = QCheckBox("Use backwards directions")

        # The size factor control
        self.sf_spinbox = QSpinBox()
        self.sf_spinbox.setRange(*SIZE_FAC_RANGE)
        self.sf_spinbox.setValue(SIZE_FAC_DEFAULT)

        self.sf_label = QLabel("Size factor:")
        self.sf_label.setBuddy(self.sf_spinbox)

        self.sf_layout = QHBoxLayout()
        self.sf_layout.addWidget(self.sf_label)
        self.sf_layout.addWidget(self.sf_spinbox, stretch=1)

        # The intersection bias choosing
        self.bias_label = QLabel("Word intersections bias:")

        self.bias_ops_layout = QHBoxLayout()
        for bias_name, bias_value in INTERSECT_BIASES.items():
            widget = QRadioButton(bias_name.capitalize())
            widget.bias_value = bias_value
            widget.toggled.connect(self.set_bias)
            if bias_name == INTERSECT_BIAS_DEFAULT:
                widget.setChecked(True)
            self.bias_ops_layout.addWidget(widget)

        self.bias_layout = QVBoxLayout()
        self.bias_layout.addWidget(self.bias_label)
        self.bias_layout.addLayout(self.bias_ops_layout)

        # The text area
        self.entry_w = QPlainTextEdit()
        self.entry_w.appendPlainText("Delete this text, then enter one word per line.")

        # Finally, the generate button
        self.gen_button = QPushButton("Generate")
        self.gen_button.clicked.connect(self.generate_puzzle)

        # The overall layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.use_hard_w)
        self.main_layout.addLayout(self.sf_layout)
        self.main_layout.addLayout(self.bias_layout)
        self.main_layout.addWidget(self.entry_w, stretch=1)
        self.main_layout.addWidget(self.gen_button)

        self.setWindowTitle("Word Search Generator")

    def set_bias(self):
        """Set the current bias from the radiobuttons"""
        radiobutton = self.sender()
        if radiobutton.isChecked:
            self.intersect_bias = self.sender().bias_value

    @property
    def use_hard(self):
        """Wether or not to use hard directions"""
        return self.use_hard_w.isChecked()

    @property
    def directions(self) -> list[tuple[int, int]]:
        """Set up directions to use"""
        if self.use_hard:
            return DIRECTIONS

        return EASY_DIRECTIONS

    @property
    def size_factor(self):
        """The selected size factor of the puzzle"""
        return self.sf_spinbox.value()

    @Slot()
    def generate_puzzle(self):
        """Generate a puzzle from the input words"""

        # Read the entry area for words
        words_raw = self.entry_w.toPlainText().strip().upper()

        # Checkpoint against invalid characters
        for letter in words_raw:
            if letter not in ALL_CHARS and not letter.isspace():
                words_raw = None
                break

        # Report and halt at any text problems
        if not words_raw:
            QMessageBox.critical(
                self,
                "Invalid text",
                "Enter one word per line with no punctuation."
                )
            return

        # Generate the puzzle
        words = words_raw.split()
        table = Generator.gen_word_search(
            words,
            directions=self.directions,
            size_fac=self.size_factor,
            intersect_bias=self.intersect_bias
            )

        # Render the puzzle
        text = Generator.render_puzzle(table)

        # Copy the finished puzzle to the Tkinter/system clipboard
        self.clipboard.setText(text)

        # Patch for issue #1
        print("--- Puzzle ---")
        print(text)
        print("--------------")

        QMessageBox.information(
            self,
            "Generation complete",
            "The puzzle was copied to the clipboard (and printed to " +
            "stdout). Paste into a word processor set for a monospaced font " +
            "BEFORE closing this program.",
            )

        # Offer to print the key
        if QMessageBox.question(
            self,
            "Show key",
            "Would you like to copy (and print) the answer key now (will " +
            "replace the puzzle)?",
                ) == QMessageBox.Yes:
            keytext = Generator.render_puzzle(table, fill=False)

            # Copy the finished puzzle key to the Tkinter/system clipboard
            self.clipboard.setText(keytext)

            # Patch for issue #1
            print("- Answer Key -")
            print(keytext)
            print("--------------")

            QMessageBox.information(
                self,
                "Key copied",
                "The answer key was copied to the clipboard (and printed to " +
                "stdout)."
                )


def main():
    """Launch the GUI"""
    app = QApplication(sys.argv)
    window = QtWindow()
    window.show()
    app.exec()


# If this was not imported, run it
if __name__ == "__main__":
    main()
