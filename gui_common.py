#!/usr/bin/env python3
"""Word Search Generator common GUI class

Present a GUI for the word search generator algorithm (Tkitner)

This file is part of Word Search Generator.

Word Search Generator is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

S.D.G."""


from algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    )


class GUICommon:
    """Common stuff between the GUIs"""
    class Lang:
        """Labels for stuff"""
        window_title = "Word Search Gen"
        use_hard = "Use backwards directions"
        size_factor = "Size factor:"
        word_intersect_bias = "Word intersections bias:"
        word_entry_default = "Delete this text, then enter one word per line."
        gen_button = "Generate"
        copypuzz_button = "Copy puzzle"
        copykey_button = "Copy key"

    def __init__(self):
        """Common stuff between the GUIs"""

        # The last generated puzzle
        self.puzz_table = None

        # The last used word list
        self.last_used_words = []

    @property
    def current_words(self):
        """The currently entered words"""
        self.format_input_text()
        return self.words_entry_raw.strip().upper().split()

    @property
    def directions(self) -> list[tuple[int, int]]:
        """Set up directions to use"""
        if self.use_hard:
            return DIRECTIONS

        return EASY_DIRECTIONS

    def on_input_text_changed(self):
        """What to do when the user edits the input text"""
        self.format_input_text()
        self.regulate_gen_button()
        self.regulate_result_buttons()

    def format_input_text(self):
        """Lock the input text to acceptable formatting"""
        text = self.words_entry_raw

        if not text:
            return

        # Filter out disallowed characters
        text = "".join(c for c in text if c.upper() in ALL_CHARS or c.isspace())

        # Break words to one line each
        lines = text.split()

        # If we were on a new word, put in the new line
        if text[-1].isspace():
            lines.append("")

        self.words_entry_raw = "\n".join(lines)

    def regulate_gen_button(self):
        """Set the state of the go button appropriately"""
        self.gen_button_able = bool(self.current_words)

    def regulate_result_buttons(self):
        """Set the state of the result buttons appropriately"""

        # Enable the result buttons if we have a puzzle to copy,
        # and the entered words have not changed
        self.result_buttons_able = self.puzz_table is not None \
            and self.current_words == self.last_used_words

    def generate_puzzle(self):
        """Generate a puzzle from the input words"""

        self.puzz_table = Generator.gen_word_search(
            self.current_words,
            directions=self.directions,
            size_fac=self.size_factor,
            intersect_bias=self.intersect_bias
            )
        self.last_used_words = self.current_words

        self.regulate_result_buttons()

    @property
    def puzzle(self) -> str:
        """The current generated puzzle"""
        if self.puzz_table is None:
            return ""
        return Generator.render_puzzle(self.puzz_table)

    @property
    def answer_key(self) -> str:
        """The current generated puzzle's answer key"""
        if self.puzz_table is None:
            return ""
        return Generator.render_puzzle(self.puzz_table, fill=False)

    def copy_puzzle(self):
        """Copy the puzzle to the clipboard and print to stdout"""
        self.copy_to_clipboard(self.puzzle)
        print("--- Puzzle ---")
        print(self.puzzle)
        print("--------------")

    def copy_answer_key(self):
        """Copy the answer key to the clipboard and print to stdout"""
        self.copy_to_clipboard(self.answer_key)
        print("- Answer Key -")
        print(self.answer_key)
        print("--------------")
