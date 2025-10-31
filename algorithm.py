#!/usr/bin/env python3
"""Word search puzzle generator algorithm

Given a list of words, generate a word search puzzle.

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

# Import modules
import random
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
        Create the empty 2D table to build the puzzle.

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

# HalleluJAH!!!
