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
I could some redefining stuff, but I'm not sure.
You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

S.D.G."""


from algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    SIZE_FAC_DEFAULT,
    INTERSECT_BIAS_DEFAULT,
    )


class GUICommon:
    """Common stuff between the GUIs"""

    class Defaults:
        """GUI control defaults"""
        use_hard = False
        size_fac = SIZE_FAC_DEFAULT
        intersect_bias = INTERSECT_BIAS_DEFAULT
        word_entry = "Delete this text, then enter one word per line."

    class Lang:
        """Labels for stuff"""
        window_title = "Word Search Gen"
        use_hard = "Use backwards directions"
        size_factor = "Size factor:"
        word_intersect_bias = "Word intersections bias:"
        gen_button = "Generate"
        cancel_button = "Cancel"
        copypuzz_button = "Copy puzzle"
        copykey_button = "Copy key"

    def __init__(self):
        """Common stuff between the GUIs"""

        # The last generated puzzle
        self.puzz_table = None

        # The generator object we will reuse
        self.generator = Generator(self.progress_update)

        # The operation Thread
        self.thread = None

        # Wether or not the GUI is running a thread operation now
        self.__gui_op_running = False

        # The last used word list
        self.last_used_words = []

    def progress_update(self):
        """Update the GUI with progress of self.generator"""
        NotImplemented

    @property
    def use_hard(self) -> bool:
        """Wether or not we are set to use hard directions"""
        raise NotImplementedError

    @property
    def size_factor(self) -> int:
        """The size factor we are set to use"""
        raise NotImplementedError

    @property
    def intersect_bias(self) -> int:
        """The intersection bias we are set to use"""
        raise NotImplementedError

    def copy_to_clipboard(self, text: str):
        """copy text to the clipboard"""
        raise NotImplementedError

    @property
    def words_entry_raw(self):
        """The raw entry in the text area"""
        raise NotImplementedError

    @words_entry_raw.setter
    def words_entry_raw(self, new: str):
        """The raw entry in the text area"""
        raise NotImplementedError

    @property
    def result_buttons_able(self) -> bool:
        """Are the result buttons enabled?"""
        raise NotImplementedError

    @result_buttons_able.setter
    def result_buttons_able(self, state: bool):
        """Enable or disable the result buttons"""
        raise NotImplementedError

    @property
    def gen_cancel_button_able(self) -> bool:
        """Is the generate button enabled?"""
        raise NotImplementedError

    @gen_cancel_button_able.setter
    def gen_cancel_button_able(self, state: bool):
        """Enable or disable the generate button"""
        raise NotImplementedError

    def configure_gen_cancel_button(self):
        """Visually turn the generate button into a cancel button or back appropriately"""
        raise NotImplementedError

    def update_gui_able(self):
        """Configure the GUI based on self.gui_op_running"""
        raise NotImplementedError

    def generate_puzzle(self):
        """Generate a puzzle from the input words (threaded)"""
        raise NotImplementedError

    def on_gen_cancel_button_click(self):
        """Start or abort generation"""
        if self.gui_op_running:
            self.generator.halted = True
        else:
            self.generate_puzzle()

    @property
    def current_words(self) -> str:
        """The currently entered words"""
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
        self.regulate_gen_cancel_button()
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
        if text[-1].isspace() or "\n\n" in text:
            lines.append("")

        # If no changes were made, don't write them (prevents recursion)
        new_text = "\n".join(lines)
        if self.words_entry_raw == new_text:
            return

        self.words_entry_raw = new_text

    def regulate_gen_cancel_button(self):
        """Set the state of the go button appropriately"""
        self.gen_cancel_button_able = bool(self.current_words) or self.gui_op_running
        self.configure_gen_cancel_button()

    def regulate_result_buttons(self):
        """Set the state of the result buttons appropriately"""

        # Enable the result buttons if we have a puzzle to copy,
        # and the entered words have not changed
        # and we are not running an operation
        self.result_buttons_able = self.puzz_table is not None and not self.gui_op_running

    def _generate_puzzle(self):
        """Generate a puzzle from the input words"""
        self.gui_op_running = True
        self.puzz_table = self.generator.gen_word_search(
            self.current_words,
            directions=self.directions,
            size_fac=self.size_factor,
            intersect_bias=self.intersect_bias
            )
        self.last_used_words = self.current_words
        self.gui_op_running = False

        self.regulate_result_buttons()

    @property
    def gui_op_running(self) -> bool:
        """Is the GUI currently running an operation?"""
        return self.__gui_op_running

    @gui_op_running.setter
    def gui_op_running(self, new: bool):
        """Set if the GUI is currently running an operation"""
        # Don't change anything if this is the status quo
        if new == self.__gui_op_running:
            return

        self.__gui_op_running = new
        self.update_gui_able()
        self.regulate_gen_cancel_button()
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
