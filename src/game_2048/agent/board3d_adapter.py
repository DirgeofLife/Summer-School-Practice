"""Adapt the concrete Board3D game rules to the Agent engine protocol."""

from __future__ import annotations

import random

from game_2048.game3d import Board3D

from .contracts import Action, EngineMove, GameSnapshot


class Board3DEngine:
    """Run isolated Board3D games for Q-learning without HTTP or frontend state."""

    def __init__(self) -> None:
        """Create a Board3D instance ready to be reset by the environment."""

        self._board = Board3D()

    def reset(self, seed: int | None = None) -> GameSnapshot:
        """Start a seeded Board3D game and return its immutable Agent state."""

        if seed is not None:
            random.seed(seed)
        self._board = Board3D()
        return self._snapshot()

    def move(self, action: Action) -> EngineMove:
        """Apply one Board3D direction and expose its score increase to the Agent."""

        score_before = self._board.score
        moved = self._board.slide(action.value)
        return EngineMove(
            snapshot=self._snapshot(),
            moved=moved,
            score_delta=self._board.score - score_before,
        )

    def _snapshot(self) -> GameSnapshot:
        """Copy Board3D mutable lists into an immutable 4x4x4 observation."""

        return GameSnapshot(
            grid=tuple(
                tuple(tuple(row) for row in layer) for layer in self._board.grid
            ),
            score=self._board.score,
            won=self._board.won,
            game_over=self._board.is_game_over(),
        )


def create_engine() -> Board3DEngine:
    """Build the default Board3D adapter used by the training CLI."""

    return Board3DEngine()
