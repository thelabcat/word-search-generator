#!/usr/bin/env python3
"""Word Search Generator legacy Tkinter GUI

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

from threading import Thread
import tkinter as tk
from tkinter import ttk

from algorithm import INTERSECT_BIASES
from gui_common import GUICommon

TK_SIZE_FAC_OPTIONS = tuple(
    range(GUICommon.size_fac_range[0], GUICommon.size_fac_range[1] + 1),
    )
PAD = 10  # Widget padding


class TkWindow(tk.Tk, GUICommon):
    """Word Search Generator GUI"""

    def __init__(self):
        """Word Search Generator GUI"""
        tk.Tk.__init__(self)
        GUICommon.__init__(self)

        self.title(GUICommon.Lang.window_title)

        # Tkinter variables
        self.__use_hard = tk.BooleanVar(self, GUICommon.Defaults.use_hard)
        self.__size_fac = tk.StringVar(self, GUICommon.Defaults.size_fac)
        self.__size_fac.trace_add(
            "write",
            lambda *args: self.verify_size_fac(allow_blank=True)
            )
        self.__intersect_bias = tk.IntVar(
            self,
            INTERSECT_BIASES[GUICommon.Defaults.intersect_bias]
            )
        self.progress_bar_val = tk.DoubleVar(self, 0)

        self.build()
        self.mainloop()

    def build(self):
        """Construct the GUI widgets"""

        # Widgets to disable when we are busy
        self.busy_disable_widgets = []

        # Checkbutton for using hard directions
        hard_checkbutton = ttk.Checkbutton(
            self,
            text=GUICommon.Lang.use_hard,
            variable=self.__use_hard
            )
        hard_checkbutton.grid(row=0, sticky=tk.NSEW, padx=PAD, pady=(PAD, 0))
        self.busy_disable_widgets.append(hard_checkbutton)

        # Number area for size_fac
        sf_frame = ttk.Frame(self)
        sf_frame.grid(row=1, sticky=tk.NSEW, padx=PAD, pady=(PAD, 0))

        sf_label = ttk.Label(
            sf_frame,
            text=GUICommon.Lang.size_factor + " ",
            anchor=tk.E,
            )
        sf_label.grid(row=0, column=0, sticky=tk.NSEW)
        self.busy_disable_widgets.append(sf_label)

        sf_spinbox = ttk.Spinbox(
            sf_frame,
            values=TK_SIZE_FAC_OPTIONS,
            textvariable=self.__size_fac
            )
        sf_spinbox.grid(row=0, column=1, sticky=tk.NSEW)
        sf_spinbox.bind("<FocusOut>", lambda *args: self.verify_size_fac())
        self.busy_disable_widgets.append(sf_spinbox)

        # Resize size factor frame around the column with the spinbox.
        sf_frame.columnconfigure(1, weight=1)

        # Intersection bias chooser
        bias_frame = ttk.Frame(self)
        bias_frame.grid(row=2, sticky=tk.NSEW, padx=PAD//2, pady=(PAD, 0))
        ttk.Label(bias_frame, text=GUICommon.Lang.word_intersect_bias)\
            .grid(row=0, column=0, columnspan=3, sticky=tk.NSEW, padx=PAD//2)

        # Create radiobuttons for the three biases
        for i, bias_pair in enumerate(INTERSECT_BIASES.items()):
            bias_name, bias_value = bias_pair
            rb = ttk.Radiobutton(
                bias_frame,
                text=bias_name.capitalize(),
                variable=self.__intersect_bias,
                value=bias_value
                )
            rb.grid(row=1, column=i, sticky=tk.NSEW,
                    padx=PAD//2, pady=PAD//2)
            self.busy_disable_widgets.append(rb)
            bias_frame.columnconfigure(i, weight=1)

        # Entry area for the words, and a scrollbar
        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=3, sticky=tk.NSEW, padx=PAD)
        self.text = tk.Text(entry_frame, width=30, height=10, wrap="word")
        self.text.bind(
            "<KeyRelease>",
            lambda _: self.on_input_text_changed(),
            )
        scrollbar = ttk.Scrollbar(entry_frame)

        # Connect scrollbar to text area
        scrollbar["command"] = self.text.yview
        self.text.configure(yscrollcommand=scrollbar.set)

        scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.busy_disable_widgets.append(self.text)

        # Resize the entry frame around the text box
        entry_frame.rowconfigure(0, weight=1)
        entry_frame.columnconfigure(0, weight=1)

        # Resize the GUI about the entry frame
        self.rowconfigure(3, weight=1)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_bar_val)
        self.progress_bar.grid(row=4, sticky=tk.NSEW, padx=PAD, pady=(PAD//2, 0))

        # Go button
        self.gen_cancel_button = ttk.Button(self, text=GUICommon.Lang.gen_button, command=self.on_gen_cancel_button_click)
        self.gen_cancel_button.grid(row=5, sticky=tk.NSEW, padx=PAD, pady=(PAD//2, 0))

        # We cannot do this until the gen/cancel button exists
        self.words_entry_raw = GUICommon.Defaults.word_entry
        self.on_input_text_changed()

        # The result buttons
        resultbuttons_frame = ttk.Frame(self)
        resultbuttons_frame.grid(row=6, sticky=tk.NSEW, padx=PAD, pady=(PAD//2, PAD))
        self.copypuzz_button = ttk.Button(resultbuttons_frame, text=GUICommon.Lang.copypuzz_button, command=self.copy_puzzle)
        self.copypuzz_button.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, PAD/4))
        resultbuttons_frame.columnconfigure(0, weight=1)
        self.copykey_button = ttk.Button(resultbuttons_frame, text=GUICommon.Lang.copykey_button, command=self.copy_answer_key)
        self.copykey_button.grid(row=0, column=1, sticky=tk.NSEW, padx=(PAD/4, 0))
        resultbuttons_frame.columnconfigure(1, weight=1)
        self.regulate_result_buttons()

        # Resize horizontally
        self.columnconfigure(0, weight=1)

    def verify_size_fac(self, allow_blank: bool = False):
        """
        Ensure that __size_fac is numbers only and not below 1

        Args:
            allow_blank (bool): Allow the entry field to be empty.
                Defaults to False.
        """

        if not self.__size_fac.get() and allow_blank:
            return

        self.__size_fac.set(
            max((
                int(
                    "0" + "".join((
                        char for char in self.__size_fac.get()
                        if char.isnumeric()
                        ))
                    )
                    ),
                1,
                )
            )

    def progress_update(self):
        """Update the GUI with progress of self.generator"""
        self.progress_bar_val.set(self.generator.index)

    @property
    def use_hard(self) -> bool:
        """Wether or not we are set to use hard directions"""
        return self.__use_hard.get()

    @property
    def size_factor(self) -> int:
        """Configure the size factor"""
        return int(self.__size_fac.get())

    @property
    def intersect_bias(self) -> int:
        """The intersection bias we are set to use"""
        return self.__intersect_bias.get()

    def copy_to_clipboard(self, text: str):
        """copy text to the clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)

    @property
    def words_entry_raw(self):
        """The raw entry in the text area"""
        return self.text.get(0.0, tk.END)

    @words_entry_raw.setter
    def words_entry_raw(self, new: str):
        """The raw entry in the text area"""
        self.text.delete(0.0, tk.END)
        self.text.insert(0.0, new)
        self.text.see(tk.END)

    @property
    def result_buttons_able(self) -> bool:
        """Are the result buttons enabled?"""
        return hasattr(self, "copypuzz_button") and self.copypuzz_button["state"] != tk.DISABLED

    @result_buttons_able.setter
    def result_buttons_able(self, state: bool):
        """Enable or disable the result buttons"""
        for button in ("copypuzz_button", "copykey_button"):
            if not hasattr(self, button):
                continue
            getattr(self, button).configure(state=(tk.DISABLED, tk.NORMAL)[state])

    @property
    def gen_cancel_button_able(self) -> bool:
        """Is the generate button enabled?"""
        return hasattr(self, "gen_cancel_button") and self.gen_cancel_button["state"] != tk.DISABLED

    @gen_cancel_button_able.setter
    def gen_cancel_button_able(self, state: bool):
        """Enable or disable the generate button"""
        if not hasattr(self, "gen_cancel_button"):
            return
        self.gen_cancel_button.config(state=(tk.DISABLED, tk.NORMAL)[state])

    def configure_gen_cancel_button(self):
        """Visually turn the generate button into a cancel button or back appropriately"""
        self.gen_cancel_button.configure(
            text=(
                GUICommon.Lang.gen_button,
                GUICommon.Lang.cancel_button,
                )[self.gui_op_running])

    def update_gui_able(self):
        """Configure the GUI based on self.gui_op_running"""
        for widget in self.busy_disable_widgets:
            widget.configure(state=(tk.NORMAL, tk.DISABLED)[self.gui_op_running])

    def generate_puzzle(self):
        """Generate a puzzle from the input words (threaded)"""
        self.progress_bar.configure(maximum=len(self.current_words))
        self.thread = Thread(target=self._generate_puzzle, daemon=True)
        self.thread.start()


def main():
    """Launch the GUI"""
    TkWindow()


# If this program was not imported, call the GUI
if __name__ == "__main__":
    main()
