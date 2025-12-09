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
INTERSECT_BIAS_NAMES = {-1: "avoid", 0: "random", 1: "prefer"}
INTERSECT_BIAS_DEFAULT = 0

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

    def __eq__(self, other):
        """
        Is this position equal to another?

        Args:
            other (position): The position to compare to"""

        assert isinstance(other, type(self)), "Cannot compare position to non-position"
        return self.x, self.y, self.direction == other.x, other.y, other.direction


class Generator:
    """Generate a word search puzzle"""

    # Things to fill the NumPy array
    fill_with_random = np.vectorize(lambda spot: spot if spot else random.choice(ALL_CHARS))
    fill_with_dots = np.vectorize(lambda spot: spot if spot else "·")


    def __init__(self, progress_step: callable = None):
        """Generate a word search puzzle

        Args:
            progress_step (callable): Will call this method for every word placed.
                Defaults to None
        """

        self.__progress_step = progress_step

        self.words = None
        self.size_fac = SIZE_FAC_DEFAULT
        self.dim = 1
        self.directions = DIRECTIONS
        self.intersect_bias = 0
        self.reset_generation_data()

        # For killing the loop mid-generation
        self.halted = True

    def progress_step(self):
        """Report our progress if we were passed a callable for such"""
        if callable(self.__progress_step):
            self.__progress_step()

    def reset_generation_data(self):
        """Create starter generation data with self.dim"""
        self.table = Generator.create_empty_table(self.dim)
        self.all_workable_posits = {}
        self.all_positions = Generator.all_posits(self.dim, self.directions)
        self.table_history = []
        self.index = 0

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
            directions: Sequence[tuple[int, int]] = DIRECTIONS,
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

        return False not in success_arr, int(sum(intersecion_arr))

    @property
    def cur_word(self) -> str | None:
        """The current word being placed"""
        if not self.words or self.index >= len(self.words):
            return None
        return self.words[self.index]

    @property
    def cur_workable_posits(self):
        """The workable positions for the current word"""

        if self.cur_word is None:
            return None

        # Calculate avaliable positions if we haven't already
        if self.cur_word not in self.all_workable_posits:
            cur_workable_posits = [
                pos for pos in self.all_positions
                if Generator.can_place(self.cur_word, pos, self.table)[0]
                ]
            random.shuffle(cur_workable_posits)

            # Be biased about word intersections
            if self.intersect_bias:
                cur_workable_posits.sort(
                    key=lambda pos: Generator.can_place(self.cur_word, pos, self.table)[1]
                    )
                # Favor intersections rather than avoid them
                if self.intersect_bias > 0:
                    cur_workable_posits.reverse()
            self.all_workable_posits[self.cur_word] = cur_workable_posits

        return self.all_workable_posits[self.cur_word]

    @cur_workable_posits.deleter
    def cur_workable_posits(self):
        """Delete the stored workable positions of the current word"""
        del self.all_workable_posits[self.cur_word]

    def gen_word_search(
            self,
            words: list[str] = None,
            directions: Sequence[tuple[int, int]] = None,
            size_fac: int = None,
            intersect_bias: int | bool = None,
            ) -> list[list[str]]:
        """
        Generate a word search puzzle.

        Args:
            words (list[str]): List of words to put in puzzle.
                Defaults to None, use stored words.
            directions (Sequence[Sequence[int, int]]) = Optionally specify the
                directions the words can go in.
                Defaults to None, use stored value.
            size_fac (int): The ratio of word letters to total letters to aim
                for.
                Defaults to None, use stored size factor.
            intersect_bias (int | bool): Wether or not to be biased about word
                intersections.
                False or 0 means no bias.
                True or 1 means favor intersections.
                -1 means avoid intersections.
                Defaults to None, use stored bias.

        Returns:
            puzzle (str): The completed puzzle.
            answers (str): The answer key.
        """

        # Accept words argument, or reuse stored
        if words:
            self.words = words

        # Remove all duplicate words
        self.words = list(set(self.words))

        assert self.words, "No words were passed or stored in object data"

        # Accept size_fac argument, or reuse stored
        if size_fac is not None:
            self.size_fac = size_fac

        self.dim = Generator.get_puzzle_dim(self.words, self.size_fac)  # Generate puzzle dimension

        # Store other arguments
        if directions is not None:
            self.directions = directions

        if intersect_bias is not None:
            self.intersect_bias = intersect_bias

        self.reset_generation_data()

        # Continue until we get through all of the words
        self.halted = False
        while self.index < len(self.words) and not self.halted:

            # This word has no workable positions that don't hurt future words
            if not self.cur_workable_posits:
                # Remove the now empty workable positions from the tree
                del self.cur_workable_posits

                # Back track to the previous word
                self.index -= 1

                # All words failed to place, puzzle is too small!
                # Reset to larger puzzle
                if self.index < 0:
                    self.dim += 1
                    self.reset_generation_data()

                # Reset to table state before the previous word was placed,
                # and remove the previous word's first tried position
                else:
                    self.table = self.table_history[self.index]
                    self.table_history.pop(self.index)
                    self.cur_workable_posits.pop(0)

            # We have positions we can try
            else:
                # Save the table state before the word was added
                self.table_history.append(self.table.copy())

                # Try the first position
                self.table[self.cur_workable_posits[0].indices(len(self.cur_word))] = \
                    np.array(list(self.cur_word), dtype=str)
                self.index += 1

            # Regardless what happened in the loop, report progress
            self.progress_step()

        # The generation was cancelled
        if self.halted:
            return None

        # The generation completed, so now we signal a stop
        self.halted = True

        return self.render_puzzle(), self.render_puzzle(answer_key=True)

    def render_puzzle(self, answer_key: bool = False) -> str:
        """Render the current puzzle

        Args:
            answer_key (bool): Changes to filling with dots and only capitalizing starts of words.
                Defaults to False.

        Returns:
            puzzle (str): The rendered puzzle."""

        # Be sure we actually have generated something
        if self.table is None:
            return

        table = self.table.copy()

        # Fill the table with dots, and make only word starts capitalized
        if answer_key:
            table = Generator.fill_with_dots(np.char.lower(table))
            for _, positions in self.all_workable_posits.items():
                pos = positions[0]
                table[pos.x, pos.y] = table[pos.x, pos.y].upper()

        # Fill out the table normally
        else:
            table = Generator.fill_with_random(table)

        return "\n".join((
            " ".join(row)
            # Swap the X and Y axes for display
            for row in np.rot90(np.fliplr(table))
            ))


# HalleluJAH!!!
