#!/usr/bin/env python3
"""Word search puzzle generator

Given a list of words, generate a word search puzzle.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

S.D.G."""

# Import modules
import random
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as mb
from typing import Sequence
import numpy as np

# Coordinates start at top left, and are positive right down

# Directions in the form of (dx, dy)
# +dx is left to right, +dy is top to bottom
DIRECTIONS = [
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    ]

EASY_DIRECTIONS = DIRECTIONS[:4]  # Easy mode directions

# "size factor" is the ratio of total characters in puzzle to characters that
# are actually words
SIZE_FAC_OPTIONS = tuple(range(2, 10))
SIZE_FAC_DEFAULT = 4

# Filling characters and limiter for input words (modify this to allow for punctuation)
ALL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Generator:
    """Generate a word search puzzle"""

    # Things to fill the NumPy array
    fill_with_random = np.vectorize(lambda spot: spot if spot else random.choice(ALL_CHARS))
    fill_with_space = np.vectorize(lambda spot: spot if spot else " ")

    @staticmethod
    def get_puzzle_dim(words: list[str], size_fac: int):
        """
        Calculate puzzle dimension by word list.

        Args:
            words (list[str]): The list of words in the puzzle.
            size_fac (int): The size factor to use.

        Returns:
            edge (int): The length of one edge of a square puzzle."""

        # Count all the letters
        word_letter_total = sum((len(word) for word in words))

        # Return either the side of a square large enough for all the
        # characters times size_fac, or the length of the longest word
        return max((
            int((word_letter_total * size_fac) ** 0.5),
            len(max(words, key=len)),
            ))

    @staticmethod
    def create_empty_table(dim: int):
        """
        Create the empty 2D table to build the puzzle. referenced by table[y][x]=" "

        Args:
            dim (int): The size of the puzzle.

        Returns:
            table (np.array): The empty puzzle table.
        """

        # table = []
        # for y in range(dim):
        #     table.append([])
        #     for x in range(dim):
        #         table[-1].append(" ")
        return np.empty((dim, dim), dtype=str)

    @staticmethod
    def create_blank_tried_pos(words: list[str]) -> dict[str: list]:
        """
        Create a new tried positions dictionary

        Args:
            words (list[str]): The words to put in the puzzle.

        Returns:
            tried_positions (dict[str: list]): Empty ledger for tried positions.
        """
        return {word: [] for word in words}

    @staticmethod
    def all_random_coords(dim: int) -> tuple[list[int], list[int]]:
        """
        Generate shuffled lists of all possible X and Y coordinates.

        Args:
            dim (int): The puzzle dimension.

        Returns:
            xlist (list[int]): List of X coordinates.
            ylist (list[int]): List of Y coordinates.
        """

        xlist = list(range(dim))
        random.shuffle(xlist)
        ylist = list(range(dim))
        random.shuffle(ylist)
        return xlist, ylist

    @staticmethod
    def gen_word_search(
            words: list[str],
            directions: Sequence[tuple[int, int]] = DIRECTIONS,
            size_fac: int = SIZE_FAC_DEFAULT
            ) -> list[list[str]]:
        """
        Generate a word search puzzle.

        Args:
            words (list[str]): List of words to put in puzzle.
            directions (Sequence[Sequence[int, int]]) = Optionally specify the directions the words can go in.
                Defaults to all DIRECTIONS.
            size_fac (int): The ratio of word letters to total letters to aim for.
                Defaults to SIZE_FAC_DEFAULT.

        Returns:
            table (np.array): The completed puzzle.
        """

        dim = Generator.get_puzzle_dim(words, size_fac)  # Generate puzzle dimension
        table = Generator.create_empty_table(dim)
        table_history = {}

        # Dict of positions for each word that have been tried but hurt future words. Future word values should ALWAYS be empty.
        tried_positions = Generator.create_blank_tried_pos(words)

        current_index = 0
        while current_index < len(words):  # place every word

            word = words[current_index]

            table_history[word] = table.copy()  # Record previous table state

            # Randomly shuffle all coordinate possibilities
            xlist, ylist = Generator.all_random_coords(dim)

            # For all possible positions (randomized)...
            for x in xlist:
                for y in ylist:

                    # If all directions for this position are used, this will be the default value
                    success = False

                    # For all possible directions (randomized per position)...
                    random.shuffle(directions)
                    for direction in directions:

                        if (x, y, direction) in tried_positions[word]:
                            continue  # We already tried this direction

                        tcopy = table.copy()  # Copy the table
                        pos = [x, y]  # Current position in the word. To be incremented forward by direction for each letter
                        success = True  # Assume that the letter placing loop will succeed ;-D

                        for letter in word:  # Move forward in the word
                            try:  # check that the index is valid. REMEMBER: table must be indexed [y][x]
                                # Do not allow negative indexes
                                if pos[0] < 0 or pos[1] < 0:
                                    raise IndexError

                                tcopy[*pos]

                            except IndexError:  # Position does not exist
                                success = False
                                break

                            # Try placing the letter...
                            if not tcopy[*pos]:  # Letter successfully placed
                                tcopy[*pos] = letter

                            elif tcopy[*pos] == letter:  # Position was assigned, but is already this letter. Okay :-)
                                continue

                            else:  # Position is occupied by a different letter. Try another direction or spot...
                                success = False
                                break

                            # Step the position forward by direction
                            pos[0] += direction[0]
                            pos[1] += direction[1]

                        if success:  # Word successfully placed at this orientation
                            break
                    if success:  # ...and at this Y position
                        break
                if success:  # ...and at this X position
                    break
            if success:  # ...So, write changes to the table
                table = tcopy.copy()
                tried_positions[word].append((x, y, direction))  # Record the tried position for potential FUTURE use
                current_index += 1

            else:  # No position or orientation worked, so backtrack previous word placings
                current_index -= 1
                # Since we're backing up in the word list, any previously tried placing positions for this word are now invalid
                tried_positions[word] = []
                table = table_history[word].copy()

                # Nothing worked all the way back through the first word
                # so the puzzle is too small for this word list.
                if current_index < 0:
                    dim += 1
                    table = Generator.create_empty_table(dim)
                    table_history = {}  # May be no reason to clear this, but just to be safe
                    current_index = 0

        # Swap the X and Y axes for display
        return np.rot90(np.fliplr(table))

    @staticmethod
    def render_puzzle(table: np.array, fill: bool = True) -> str:
        """Render a NumPy array of the puzzle to text

        Args:
            table (np.array): The puzzle table.
            fill (bool): Wether or not to fill out the table with random characters.
                Defaults to True.

        Returns:
            puzzle (str): The rendered puzzle."""

        return "\n".join((
            " ".join(row)
            for row in (
                Generator.fill_with_space,
                Generator.fill_with_random,
                )[fill](table)
            ))


class Window(Tk):
    """Word Search Generator GUI"""

    def __init__(self):
        """Word Search Generator GUI"""
        super().__init__()
        self.title("Word Search Gen")

        # Tkinter variables
        self.use_hard = BooleanVar(self, True)
        self.size_fac_str = StringVar(self, SIZE_FAC_DEFAULT)
        self.size_fac_str.trace_add("write", lambda *args: self.verify_size_fac())

        self.build()
        self.mainloop()

    def build(self):
        """Construct the GUI widgets"""

        # Checkbutton for using hard directions
        Checkbutton(self, text="Use backwards directions", variable=self.use_hard).grid(row=0, sticky=N+E+W)

        # Number area for size_fac
        self.sf_frame = Frame(self)
        self.sf_frame.grid(row=1, sticky = EW)

        Label(self.sf_frame, text = "Size factor:").grid(row=0, column=0, sticky=E + N)

        self.sf_spinbox = Spinbox(self.sf_frame, values=SIZE_FAC_OPTIONS, textvariable=self.size_fac_str)
        self.sf_spinbox.grid(row=0, column=1, sticky=N + EW)

        self.sf_frame.columnconfigure(1, weight=1)  # Resize size factor frame around the column with the spinbox.

        # Entry area for the words, and a scrollbar
        self.entry_frame = Frame(self)
        self.entry_frame.grid(row=2, sticky=NSEW)
        self.text = Text(self.entry_frame, width=30, height=10, wrap="word")
        self.scrollbar = Scrollbar(self.entry_frame)

        self.scrollbar["command"] = self.text.yview  # Connect scrollbar to text
        self.text.configure(yscrollcommand=self.scrollbar.set)  # Connect text to scrollbar

        self.scrollbar.grid(row=0, column=1, sticky = NS + E)
        self.text.grid(row=0, column=0, sticky=N+S+E+W)
        self.text.insert(0.0, "Delete this text, then enter one word per line.")

        # Resize the entry frame around the text box
        self.entry_frame.rowconfigure(0, weight=1)
        self.entry_frame.columnconfigure(0, weight=1)

        # Go button
        Button(self, text="Generate", command=self.generate_puzzle).grid(row=3, sticky=S + EW)

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

        words_raw = self.text.get(0.0, END).strip().upper()  # Read the entry area for words

        # Checkpoint against invalid characters
        for letter in words_raw:
            if letter not in ALL_CHARS and not letter.isspace():
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
            print("--- Puzzle ---")
            print(keytext)
            print("--------------")

            mb.showinfo(
                "Key copied",
                "The answer key was copied to the clipboard (and printed to " +
                "stdout)."
                )


# If this program was not imported, call the GUI
if __name__ == "__main__":
    Window()

# HalleluJAH!!!
