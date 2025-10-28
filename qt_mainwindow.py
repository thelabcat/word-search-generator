#!/usr/bin/env python3
"""Word Search Generator main QT window

S.D.G."""

import sys
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QWidget, QCheckBox, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout, QPlainTextEdit, QPushButton

# Size factor options
SIZE_FAC_RANGE = 1, 99
SIZE_FAC_DEFAULT = 4


class QtWindow(QWidget):
    """The Qt superwidget"""

    def __init__(self):
        """The Qt superwidget"""
        super().__init__()
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

        # The text area
        self.entry_w = QPlainTextEdit()

        # Finally, the generate button
        self.gen_button = QPushButton("Generate")
        self.gen_button.clicked.connect(self.generate_puzzle)

        # The overall layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.use_hard_w)
        self.main_layout.addLayout(self.sf_layout)
        self.main_layout.addWidget(self.entry_w, stretch=1)
        self.main_layout.addWidget(self.gen_button)

        self.setWindowTitle("Word Search Generator (stub)")

    @property
    def use_hard(self):
        """Wether or not to use hard directions"""
        return self.use_hard_w.isChecked()

    @property
    def size_factor(self):
        """The selected size factor of the puzzle"""
        return self.sf_spinbox.value()

    @Slot()
    def generate_puzzle(self):
        """Generate the puzzle given the inputs"""
        print(f"Size factor is {self.size_factor}")
        print(f"Entered text: {self.entry_w.toPlainText()}")


app = QApplication(sys.argv)
window = QtWindow()
window.show()
app.exec()
