#!/usr/bin/env python3
"""Word search puzzle generator

Given a list of words, generate a word search puzzle.
S.D.G."""

# Import modules
import random
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as mb
from typing import Sequence

# Coordinates start at top left, and are positive right down

# Directions in the form of (dx, dy)
DIRECTIONS = [
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
    ]

EASY_DIRECTIONS = DIRECTIONS[:3]  # Easy mode directions

# "size factor" is the ratio of total characters in puzzle to characters that
# are actually words
SIZE_FAC_OPTIONS = tuple(range(2, 10))
SIZE_FAC_DEFAULT = 4

# Filling characters and limiter for input words (modify this to allow for punctuation)
ALL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Generator(object):
    def get_puzzle_dim(self, words: list[str], size_fac: int):
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

    def create_empty_table(self, dim: int):
        """
        Create the empty 2D table to build the puzzle. referenced by table[y][x]=" "

        Args:
            dim (int): The size of the puzzle.

        Returns:
            table (list[list[str]]): The empty puzzle table.
        """

        # table = []
        # for y in range(dim):
        #     table.append([])
        #     for x in range(dim):
        #         table[-1].append(" ")
        return [[" "] * dim] * dim

    def copy_table(self, table: list[list[str]]) -> list[list[str]]:
        """
        Create a shallow copy of the given table.

        Args:
            table (list[list[str]]): The table to duplicate.

        Returns:
            table (list[list[str]]): The duplicate of the table.
        """

        return [row.copy() for row in table]

    def create_blank_tried_pos(self, words: list[str]) -> dict[str: list]:
        """
        Create a new tried positions dictionary

        Args:
            words (list[str]): The words to put in the puzzle.

        Returns:
            tried_positions (dict[str: list]): Empty ledger for tried positions.
        """
        return {word: [] for word in words}

    def all_random_coords(self, dim: int) -> tuple[list[int], list[int]]:
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

    def gen_word_search(
            self,
            words: list[str],
            directions: Sequence[tuple[int, int]] = None,
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
            table (list[list[str]): The completed puzzle.
        """

        # Default to all directions
        if not directions:
            directions = DIRECTIONS[:]

        dim = self.get_puzzle_dim(words, size_fac) #Generate puzzle dimension
        table = self.create_empty_table(dim)
        table_history = {}

        # Dict of positions for each word that have been tried but hurt future words. Future word values should ALWAYS be empty.
        tried_positions = self.create_blank_tried_pos(words)

        current_index = 0
        while current_index < len(words):  # place every word

            word = words[current_index]

            table_history[word] = self.copy_table(table)  # Record previous table state

            # Randomly shuffle all coordinate possibilities
            xlist, ylist = self.all_random_coords(dim)

            # For all possible positions (randomized)...
            for x in xlist:
                for y in ylist:

                    # If all directions for this positionare used, this will be the default value
                    success = False

                    # For all possible directions (randomized per position)...
                    random.shuffle(directions)
                    for direction in directions:

                        if (x, y, direction) in tried_positions[word]:
                            continue  # We already tried this direction

                        tcopy = self.copy_table(table)  # Copy the table
                        pos = [x, y]  # Current position in the word. To be incremented forward by direction for each letter
                        success = True  # Assume that the letter placing loop will succeed ;-D

                        for letter in word:  # Move forward in the word
                            try:  # check that the index is valid. REMEMBER: table must be indexed [y][x]
                                # Do not allow negative indexes
                                if pos[0] < 0 or pos[1] < 0:
                                    raise IndexError

                                tcopy[pos[1]][pos[0]]

                            except IndexError:  # Position does not exist
                                success = False
                                break

                            # Try placing the letter...
                            if tcopy[pos[1]][pos[0]] == " ":  # Letter successfully placed
                                tcopy[pos[1]][pos[0]] = letter

                            elif tcopy[pos[1]][pos[0]] == letter:  # Position was assigned, but is already this letter. Okay :-)
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
                table = self.copy_table(tcopy)
                tried_positions[word].append((x, y, direction))  # Record the tried position for potential FUTURE use
                current_index += 1

            else:  # No position or orientation worked, so backtrack previous word placings
                current_index -= 1
                # Since we're backing up in the word list, any previously tried placing positions for this word are now invalid
                tried_positions[word] = []
                table = self.copy_table(table_history[word])

                # Nothing worked all the way back through the first word
                # so the puzzle is too small for this word list.
                if current_index < 0:
                    dim += 1
                    table = self.create_empty_table(dim)
                    table_history = {}  # May be no reason to clear this, but just to be safe
                    current_index = 0

        return table  # All finished :-D


class Window(Tk):
    """Word Search Generator GUI"""

    def __init__(self):
        """Word Search Generator GUI"""
        super(Window, self).__init__()
        self.title("Word Search Gen")
        self.build()
        self.mainloop()

    def build(self):
        """Construct the GUI widgets"""

        # Checkbutton for using hard directions
        self.use_hard = BooleanVar()
        self.use_hard.set(True)
        Checkbutton(self, text="Use upward/leftward directions", variable=self.use_hard, command=self.configure_directs).grid(row=0, sticky=N+E+W)
        self.configure_directs()

        # Number area for size_fac
        self.sf_frame = Frame(self)
        self.sf_frame.grid(row=1, sticky = EW)

        Label(self.sf_frame, text = "Size factor:").grid(row=0, column=0, sticky=E + N)

        self.sf_spinbox = Spinbox(self.sf_frame, values=SIZE_FAC_OPTIONS, command=self.configure_size_fac)
        self.sf_spinbox.grid(row=0, column=1, sticky=N + EW)
        self.configure_size_fac()  # Create the size_fac variable and set the spinbox to the default

        self.sf_frame.columnconfigure(1, weight=1)  # Resize size factor frame around the column with the spinbox.


        # Entry area for the words, and a scrollbar
        self.entry_frame = Frame(self)
        self.entry_frame.grid(row=2, sticky=NSEW)
        self.text = Text(self.entry_frame, width=30, height=20, wrap="word")
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

    def configure_directs(self):
        """Set up directions to use"""
        if self.use_hard.get():
            self.directions = DIRECTIONS[:]
        else:
            self.directions = EASY_DIRECTIONS[:]

    def configure_size_fac(self):
        """Configure the size factor"""

        # If size_fac is not set yet, set to default and alter spinbox
        if not hasattr(self, "size_fac"):
            self.size_fac = SIZE_FAC_DEFAULT * 1
            self.clear_sf_spinbox()
            return

        inp_value = self.sf_spinbox.get()
        try:
            self.size_fac = int(inp_value)  # Try assigning the new size_fac

            if self.size_fac < 1:  # Is size fac invalid?
                raise ValueError

            if str(self.size_fac) != inp_value:  # If we turned 4.0 into 4, alter the spinbox to match the interpretation
                self.clear_sf_spinbox()

        except ValueError:  # Entry was invalid, clear to existing size_fac value
            self.clear_sf_spinbox()

    def clear_sf_spinbox(self):
        """set the SF spinbox to whatever the current size_fac is"""
        self.sf_spinbox.delete(0, END)
        self.sf_spinbox.insert(0, str(self.size_fac))

    def generate_puzzle(self):
        """Generate a puzzle from the input words"""
        self.configure_size_fac()

        words_raw = self.text.get(0.0, END).upper()  # Read the entry area for words

        # Checkpoint against invalid characters
        for letter in words_raw:
            if letter not in ALL_CHARS + "\n":
                mb.showerror("Invalid text", "Enter one word per line with no punctuation.")
                return

        # Heal double-spacing
        while "\n\n" in words_raw:
            words_raw = words_raw.replace("\n\n", "\n")

        # Generate the puzzle
        words = words_raw.splitlines()
        table = Generator().gen_word_search(words, directions=self.directions[:], size_fac=self.size_fac * 1)

        # Prepare the returned puzzle table for use (turn into text and fill with random characters)
        text = ""
        for row in table:
            for letter in row:
                if letter == " ":
                    text += random.choice(ALL_CHARS)
                else:
                    text += letter
                text += " "  # Space out the characters to make it square
            text = text[:-1] + "\n"  # Remove the trailing space, and add a new line
        text = text[:-1]  # remove the trailing newline

        # Copy the finished puzzle to the Tkinter/system clipboard
        self.clipboard_clear()
        self.clipboard_append(text)
        mb.showinfo(
            "Generation complete",
            "The puzzle was copied to the clipboard. Paste into a word " +
            "processor set for a monospaced font BEFORE closing this program.",
            )


# If this program was not imported, call the GUI
if __name__ == "__main__":
    Window()

# HalleluJAH!!!
