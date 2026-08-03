from __future__ import annotations

import random
from typing import Optional


class Board:
    SIZE = 4
    SPAWN_VALUES = [2] * 9 + [4]  # 90% 2, 10% 4
    WIN_VALUE = 2048

    def __init__(self) -> None:
        self.grid: list[list[int]] = [[0] * Board.SIZE for _ in range(Board.SIZE)]
        self.score: int = 0
        self.won: bool = False
        self._spawn_tile()
        self._spawn_tile()

    def _spawn_tile(self) -> None:
        empty = [
            (r, c)
            for r in range(Board.SIZE)
            for c in range(Board.SIZE)
            if self.grid[r][c] == 0
        ]
        if not empty:
            return
        r, c = random.choice(empty)
        self.grid[r][c] = random.choice(Board.SPAWN_VALUES)

    def _slide_row_left(self, row: list[int]) -> list[int]:
        compacted = [v for v in row if v != 0]
        merged: list[int] = []
        i = 0
        while i < len(compacted):
            if i + 1 < len(compacted) and compacted[i] == compacted[i + 1]:
                new_val = compacted[i] * 2
                merged.append(new_val)
                self.score += new_val
                if new_val == Board.WIN_VALUE:
                    self.won = True
                i += 2
            else:
                merged.append(compacted[i])
                i += 1
        merged.extend([0] * (Board.SIZE - len(merged)))
        return merged

    def _rotate_cw(self) -> list[list[int]]:
        return [
            [self.grid[Board.SIZE - 1 - c][r] for c in range(Board.SIZE)]
            for r in range(Board.SIZE)
        ]

    def _rotate_ccw(self) -> list[list[int]]:
        return [
            [self.grid[c][Board.SIZE - 1 - r] for c in range(Board.SIZE)]
            for r in range(Board.SIZE)
        ]

    def _reverse_rows(self) -> list[list[int]]:
        return [row[::-1] for row in self.grid]

    def slide(self, direction: str) -> bool:
        old_grid = [row[:] for row in self.grid]

        if direction == "left":
            self.grid = [self._slide_row_left(row) for row in self.grid]
        elif direction == "right":
            self.grid = self._reverse_rows()
            self.grid = [self._slide_row_left(row) for row in self.grid]
            self.grid = self._reverse_rows()
        elif direction == "up":
            self.grid = self._rotate_ccw()
            self.grid = [self._slide_row_left(row) for row in self.grid]
            self.grid = self._rotate_cw()
        elif direction == "down":
            self.grid = self._rotate_cw()
            self.grid = [self._slide_row_left(row) for row in self.grid]
            self.grid = self._rotate_ccw()

        if self.grid == old_grid:
            return False
        self._spawn_tile()
        return True

    def is_game_over(self) -> bool:
        for r in range(Board.SIZE):
            for c in range(Board.SIZE):
                if self.grid[r][c] == 0:
                    return False
        for r in range(Board.SIZE):
            for c in range(Board.SIZE):
                if c + 1 < Board.SIZE and self.grid[r][c] == self.grid[r][c + 1]:
                    return False
                if r + 1 < Board.SIZE and self.grid[r][c] == self.grid[r + 1][c]:
                    return False
        return True

    def to_dict(self) -> dict:
        return {
            "board": [row[:] for row in self.grid],
            "score": self.score,
            "won": self.won,
            "game_over": self.is_game_over(),
        }
