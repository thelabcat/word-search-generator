#!/usr/bin/env python3
"""Word Search Generator common GUI class

Present a GUI for the word search generator algorithm (abstract base class)

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


from .algorithm import (
    Generator,
    ALL_CHARS,
    DIRECTIONS,
    EASY_DIRECTIONS,
    SIZE_FAC_DEFAULT,
    INTERSECT_BIAS_DEFAULT,
    )


class GUICommon:
    """Common stuff between the GUIs"""

    # The range of size factor options
    size_fac_range = 1, 99

    # How often to run status_tick in seconds
    status_tick_interval = 0.1

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
        gen_thread = "Puzzle Generator Thread"

    def __init__(self):
        """Common stuff between the GUIs"""

        # The last generated puzzle and answer key
        self.puzzle = None
        self.answer_key = None

        # The generator object we will reuse
        self.generator = Generator(self.progress_update)

        # The operation Thread
        self.gen_thread = None

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

    def set_result_buttons_able(self, state: bool):
        """Enable or disable the result buttons"""
        raise NotImplementedError

    def set_gen_cancel_button_able(self, state: bool):
        """Enable or disable the generate button"""
        raise NotImplementedError

    def update_progress_bar_max(self):
        """Set the progress bar to the appropriate maximum"""
        raise NotImplementedError

    def start_generation(self):
        """Create and launch the generation thread"""
        raise NotImplementedError

    def set_gen_cancel_button_mode(self, is_cancel: bool):
        """Visually change the gen/cancel button"""
        raise NotImplementedError

    def set_gui_able(self, state: bool):
        """Set if the GUI is currently enabled"""
        raise NotImplementedError

    #@property
    def is_thread_running(self) -> bool:
        """Wether or not the thread is still running"""
        raise NotImplementedError

    def status_tick(self):
        """Update components of the GUI affected by a running generation, appropriately"""
        self.update_gui_able()
        self.update_gen_cancel_button_mode()
        self.update_result_buttons_able()

    def update_gui_able(self):
        """Update the able state of the GUI based on self.is_thread_running"""
        self.set_gui_able(not self.is_thread_running())

    def update_gen_cancel_button_mode(self):
        """Appropriately change the gen/cancel button appearance"""
        self.set_gen_cancel_button_mode(self.is_thread_running())

    def update_result_buttons_able(self):
        """Set the result buttons to the appropriate current state"""
        self.set_result_buttons_able(bool(self.puzzle and not self.is_thread_running()))

    def on_gen_cancel_button_click(self):
        """Start or abort generation"""
        if self.is_thread_running():
            self.generator.halted = True
        else:
            self.update_progress_bar_max()
            self.configure_generator_object()
            self.start_generation()

    @property
    def current_words(self) -> str:
        """The currently entered words (filtered for duplicates)"""
        return list(set(self.words_entry_raw.strip().upper().split()))

    @property
    def directions(self) -> list[tuple[int, int]]:
        """Set up directions to use"""
        if self.use_hard:
            return DIRECTIONS

        return EASY_DIRECTIONS

    def on_input_text_changed(self):
        """What to do when the user edits the input text"""
        self.format_input_text()
        self.set_gen_cancel_button_able(bool(self.current_words))

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

    def configure_generator_object(self):
        """Write current GUI settings to generator memory before starting"""

        self.generator.words = self.current_words
        self.generator.directions=self.directions
        self.generator.size_fac=self.size_factor
        self.generator.intersect_bias=self.intersect_bias

    def generate_puzzle(self):
        """Generate a puzzle from the input words"""
        self.puzzle, self.answer_key = self.generator.gen_word_search()
        self.last_used_words = self.current_words

    def copy_puzzle(self):
        """Copy the puzzle to the clipboard and print to stdout"""
        self.copy_to_clipboard(self.puzzle)
        # print("--- Puzzle ---")
        print(self.puzzle)
        print()
        # print("--------------")

    def copy_answer_key(self):
        """Copy the answer key to the clipboard and print to stdout"""
        self.copy_to_clipboard(self.answer_key)
        # print("- Answer Key -")
        print(self.answer_key)
        print()
        # print("--------------")
