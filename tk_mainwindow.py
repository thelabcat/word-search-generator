#!/usr/bin/env python3
"""Word Search Generator legacy Tkinter GUI

Present a GUI for the word search generator algorithm (Tkitner)

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

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

from algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    SIZE_FAC_DEFAULT,
    )


TK_SIZE_FAC_OPTIONS = tuple(range(2, 10))


class TkWindow(tk.Tk):
    """Word Search Generator GUI"""

    def __init__(self):
        """Word Search Generator GUI"""
        super().__init__()
        self.title("Word Search Gen")

        # Tkinter variables
        self.use_hard = tk.BooleanVar(self, True)
        self.size_fac_str = tk.StringVar(self, SIZE_FAC_DEFAULT)
        self.size_fac_str.trace_add("write", lambda *args: self.verify_size_fac())

        self.build()
        self.mainloop()

    def build(self):
        """Construct the GUI widgets"""

        # Checkbutton for using hard directions
        ttk.Checkbutton(self, text="Use backwards directions", variable=self.use_hard).grid(row=0, sticky=tk.N + tk.EW)

        # Number area for size_fac
        self.sf_frame = ttk.Frame(self)
        self.sf_frame.grid(row=1, sticky=tk.EW)

        ttk.Label(self.sf_frame, text="Size factor:").grid(row=0, column=0, sticky=tk.E + tk.N)

        self.sf_spinbox = ttk.Spinbox(self.sf_frame, values=TK_SIZE_FAC_OPTIONS, textvariable=self.size_fac_str)
        self.sf_spinbox.grid(row=0, column=1, sticky=tk.N + tk.EW)

        self.sf_frame.columnconfigure(1, weight=1)  # Resize size factor frame around the column with the spinbox.

        # Entry area for the words, and a scrollbar
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.grid(row=2, sticky=tk.NSEW)
        self.text = tk.Text(self.entry_frame, width=30, height=10, wrap="word")
        self.scrollbar = ttk.Scrollbar(self.entry_frame)

        self.scrollbar["command"] = self.text.yview  # Connect scrollbar to text
        self.text.configure(yscrollcommand=self.scrollbar.set)  # Connect text to scrollbar

        self.scrollbar.grid(row=0, column=1, sticky=tk.NS + tk.E)
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.text.insert(0.0, "Delete this text, then enter one word per line.")

        # Resize the entry frame around the text box
        self.entry_frame.rowconfigure(0, weight=1)
        self.entry_frame.columnconfigure(0, weight=1)

        # Go button
        ttk.Button(self, text="Generate", command=self.generate_puzzle).grid(row=3, sticky=tk.S + tk.EW)

        # Resize GUI about entry frame
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

    @property
    def directions(self) -> list[tuple[int, int]]:
        """Set up directions to use"""
        if self.use_hard.get():
            return DIRECTIONS

        return EASY_DIRECTIONS

    def verify_size_fac(self):
        """Ensure that size_fac_str is numbers only and not below 1"""
        self.size_fac_str.set(
            max((
                int(
                    "0" + "".join((
                        char for char in self.size_fac_str.get()
                        if char.isnumeric()
                        ))
                    )
                    ),
                1,
                )
            )

    @property
    def size_fac(self) -> int:
        """Configure the size factor"""

        return int(self.sf_spinbox.get())

    def generate_puzzle(self):
        """Generate a puzzle from the input words"""

        words_raw = self.text.get(0.0, tk.END).strip().upper()  # Read the entry area for words

        # Checkpoint against invalid characters
        for letter in words_raw:
            if letter not in ALL_CHARS and not letter.isspace():
                words_raw = None
                break

        # Report and halt at any text problems
        if not words_raw:
            mb.showerror("Invalid text", "Enter one word per line with no punctuation.")
            return

        # Generate the puzzle
        words = words_raw.split()
        table = Generator.gen_word_search(words, directions=self.directions, size_fac=self.size_fac)

        # Render the puzzle
        text = Generator.render_puzzle(table)

        # Copy the finished puzzle to the Tkinter/system clipboard
        self.clipboard_clear()
        self.clipboard_append(text)

        # Patch for issue #1
        print("--- Puzzle ---")
        print(text)
        print("--------------")

        mb.showinfo(
            "Generation complete",
            "The puzzle was copied to the clipboard (and printed to " +
            "stdout). Paste into a word processor set for a monospaced font " +
            "BEFORE closing this program.",
            )

        # Offer to print the key
        if mb.askyesno(
            "Show key",
            "Would you like to copy (and print) the answer key now (will " +
            "replace the puzzle)?",
                ):
            keytext = Generator.render_puzzle(table, fill=False)

            # Copy the finished puzzle key to the Tkinter/system clipboard
            self.clipboard_clear()
            self.clipboard_append(keytext)

            # Patch for issue #1
            print("- Answer Key -")
            print(keytext)
            print("--------------")

            mb.showinfo(
                "Key copied",
                "The answer key was copied to the clipboard (and printed to " +
                "stdout)."
                )


def main():
    """Launch the GUI"""
    TkWindow()


# If this program was not imported, call the GUI
if __name__ == "__main__":
    main()
