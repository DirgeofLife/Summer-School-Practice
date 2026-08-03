"""Gym-like environment wrapper for a six-direction 3D 2048 engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log2
from typing import Any

from .config import RewardConfig
from .contracts import Action, GameSnapshot, Observation, SixDirectionGameEngine


@dataclass(frozen=True)
class RewardBreakdown:
    """Expose each reward component so Agent behaviour can be audited."""

    merge: float
    max_tile: float
    invalid_action: float
    win: float
    game_over: float

    @property
    def total(self) -> float:
        """Return the scalar reward consumed by Q-learning."""

        return sum(asdict(self).values())


def encode_observation(snapshot: GameSnapshot) -> Observation:
    """Flatten six faces and encode each tile as its base-two exponent."""

    encoded: list[int] = []
    for face in snapshot.faces:
        for row in face:
            for tile in row:
                encoded.append(0 if tile == 0 else int(log2(tile)))
    return tuple(encoded)


def largest_tile(snapshot: GameSnapshot) -> int:
    """Return the largest tile visible across all six game faces."""

    return max(tile for face in snapshot.faces for row in face for tile in row)


class ThreeD2048Environment:
    """Present the custom game engine through reset and step operations."""

    actions: tuple[Action, ...] = tuple(Action)

    def __init__(self, engine: SixDirectionGameEngine, reward_config: RewardConfig) -> None:
        """Bind one game-engine adapter and its externally configured rewards."""

        self._engine = engine
        self._reward_config = reward_config
        self._snapshot: GameSnapshot | None = None

    def reset(self, seed: int | None = None) -> tuple[Observation, dict[str, Any]]:
        """Reset the engine and return an encoded state plus display-friendly info."""

        self._snapshot = self._engine.reset(seed=seed)
        return encode_observation(self._snapshot), self._build_info(
            self._snapshot,
            RewardBreakdown(0.0, 0.0, 0.0, 0.0, 0.0),
        )

    def step(
        self, action: Action
    ) -> tuple[Observation, float, bool, bool, dict[str, Any]]:
        """Apply one action and return Gymnasium-compatible transition values."""

        if self._snapshot is None:
            raise RuntimeError("Call reset() before step().")

        previous = self._snapshot
        transition = self._engine.move(action)
        self._snapshot = transition.snapshot
        reward = self._reward(previous, transition.moved, transition.score_delta)
        terminated = self._snapshot.game_over or self._snapshot.won
        return (
            encode_observation(self._snapshot),
            reward.total,
            terminated,
            False,
            self._build_info(self._snapshot, reward, moved=transition.moved),
        )

    def _reward(
        self, previous: GameSnapshot, moved: bool, score_delta: int
    ) -> RewardBreakdown:
        """Calculate explainable rewards from one observed game transition."""

        assert self._snapshot is not None
        return RewardBreakdown(
            merge=score_delta * self._reward_config.merge_score_weight,
            max_tile=(
                self._reward_config.max_tile_bonus
                if largest_tile(self._snapshot) > largest_tile(previous)
                else 0.0
            ),
            invalid_action=(
                0.0 if moved else self._reward_config.invalid_action_penalty
            ),
            win=self._reward_config.win_bonus if self._snapshot.won else 0.0,
            game_over=(
                self._reward_config.game_over_penalty
                if self._snapshot.game_over and not self._snapshot.won
                else 0.0
            ),
        )

    def _build_info(
        self,
        snapshot: GameSnapshot,
        reward: RewardBreakdown,
        moved: bool | None = None,
    ) -> dict[str, Any]:
        """Build JSON-serializable state and reward details for visualisation."""

        return {
            "faces": snapshot.faces,
            "score": snapshot.score,
            "largest_tile": largest_tile(snapshot),
            "won": snapshot.won,
            "game_over": snapshot.game_over,
            "moved": moved,
            "reward": asdict(reward),
        }
