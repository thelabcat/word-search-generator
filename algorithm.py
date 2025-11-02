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

# Intersection biases
INTERSECT_BIASES = {"Avoid": -1, "Random": 0, "Prefer": 1}
INTERSECT_BIAS_DEFAULT = "Random"

# Filling characters and limiter for input words (modify this to allow for punctuation)
ALL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Position:
    """Potential position for a word"""

    def __init__(self, x: int, y: int, direction: tuple[int, int]):
        """
        Potential position for a word

        Args:
            x (int): The X coordinate of the word start.
            y (int): The Y coordinate of the word start.
            direction (tuple[int, int]): The word direction.
        """
        assert x >= 0 and y >= 0, "Coordinates cannot be less than zero."
        self.x = x
        self.y = y
        self.direction = direction
        self.dx, self.dy = direction

    def bounds_check(self, length: int, puzz_dim: int) -> bool:
        """
        Check if a word will fit at this position

        Args:
            length (int): The length of the word.
            puzz_dim (int): The size of the puzzle.

        Returns:
            result (bool): Can the word fit?
        """

        # Calculate where the end of the word would be
        xend = self.x + self.dx * (length - 1)
        yend = self.y + self.dy * (length - 1)

        return (0 <= xend < puzz_dim) and (0 <= yend < puzz_dim)

    def indices(self, length: int) -> tuple[np.array, np.array]:
        """
        Get the indices to place a word at this position

        Args:
            length (int): The length of the word.

        Returns:
            indices (tuple[np.array, np.array]): The X and Y coordinates, respectively.
        """

        if self.dx:
            # Travel in the direction of delta X, starting at our position
            xarray = np.array(range(self.x, self.x + self.dx * length, self.dx))
        else:
            # X does not change
            xarray = np.array([self.x] * length)

        if self.dy:
            # Travel in the direction of delta Y, starting at our position
            yarray = np.array(range(self.y, self.y + self.dy * length, self.dy))
        else:
            # Y does not change
            yarray = np.array([self.y] * length)

        return xarray, yarray


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
    def all_posits(
            dim: int,
            directions: Sequence[tuple[int, int]] = DIRECTIONS
            ) -> tuple[Position]:
        """
        Generate list of all possible positions.

        Args:
            dim (int): The puzzle dimension.
            directions (Sequence[tuple[int, int]]): Directions to use.
                Defaults to DIRECTIONS.

        Returns:
            positions (tuple[Position]): All positions in all directions
        """

        return [
            Position(x, y, direction)
            for x in range(dim)
            for y in range(dim)
            for direction in directions
            ]

    @staticmethod
    def can_place(word: str, pos: Position, puzzle: np.array) -> (bool, int):
        """
        Determine if we can place a word, and count intersections if so.

        Args:
            word (str): The word to check.
            pos (Position): The position to try placing the word at.
            puzzle (np.array): The current puzzle to try placing in.

        Returns:
            valid (bool): Can the word be placed here?
            intersect (int): How many other words does it legally intersect?
        """

        wordlen = len(word)
        wordarr = np.array(list(word), dtype=str)
        dim = puzzle.shape[0]  # Assume the puzzle is square

        # The word must be short enough
        if not pos.bounds_check(wordlen, dim):
            return False, 0

        indices = pos.indices(wordlen)

        # The letter positions for this word already match it from other words
        intersecion_arr = puzzle[indices] == wordarr

        # The letter positions for this word that are blank
        blankspots = puzzle[indices] == ""

        # If all the spots are either legal intersections or blank
        success_arr = np.logical_or(intersecion_arr, blankspots)

        return not (False in success_arr), int(sum(intersecion_arr))

    @staticmethod
    def gen_word_search(
            words: list[str],
            directions: Sequence[tuple[int, int]] = DIRECTIONS,
            size_fac: int = SIZE_FAC_DEFAULT,
            intersect_bias: int | bool = False,
            ) -> list[list[str]]:
        """
        Generate a word search puzzle.

        Args:
            words (list[str]): List of words to put in puzzle.
            directions (Sequence[Sequence[int, int]]) = Optionally specify the
                directions the words can go in.
                Defaults to all DIRECTIONS.
            size_fac (int): The ratio of word letters to total letters to aim
                for.
                Defaults to SIZE_FAC_DEFAULT.
            intersect_bias (int | bool): Wether or not to be biased about word
                intersections.
                False or 0 means no bias.
                True or 1 means favor intersections.
                -1 means avoid intersections.
                Defaults to False.

        Returns:
            table (np.array): The completed puzzle.
        """

        # Remove all duplicate words
        words = list(set(words))

        dim = Generator.get_puzzle_dim(words, size_fac)  # Generate puzzle dimension
        table = Generator.create_empty_table(dim)
        all_workable_posits = {}  # Dict of word: list[Position]
        all_positions = Generator.all_posits(dim, directions)
        table_history = []  # History of table status

        # Continue until we get through all of the words
        index = 0
        while index < len(words):
            word = words[index]

            # Load previously calculated available positions
            if word in all_workable_posits:
                cur_workable_posits = all_workable_posits[word]

            # Calculate avaliable positions
            else:
                cur_workable_posits = [
                    pos for pos in all_positions
                    if Generator.can_place(word, pos, table)[0]
                    ]
                random.shuffle(cur_workable_posits)

                # Be biased about word intersections
                if intersect_bias:
                    cur_workable_posits.sort(
                        key=lambda pos: Generator.can_place(word, pos, table)[1]
                        )
                    # Favor intersections rather than avoid them
                    if intersect_bias > 0:
                        cur_workable_posits.reverse()

                all_workable_posits[word] = cur_workable_posits

            # The placements failed after this word
            if not cur_workable_posits:
                # Remove the now empty workable positions from the tree
                del all_workable_posits[word]

                # Back track to the previous word
                index -= 1

                # All words failed to place, puzzle is too small!
                # Reset to larger puzzle
                if index < 0:
                    dim += 1
                    table = Generator.create_empty_table(dim)
                    all_workable_posits = {}
                    all_positions = Generator.all_posits(dim, directions)
                    table_history = []
                    index = 0

                # Reset to previous table state, and remove previous word's first tried position
                else:
                    table = table_history[index]
                    table_history.pop(index)
                    all_workable_posits[words[index]].pop(0)

            # We have positions we can try
            else:
                table[cur_workable_posits[0].indices(len(word))] = np.array(list(word), dtype=str)
                table_history.append(table)
                index += 1

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
