"""Load Agent parameters from a TOML file without mixing them into code."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class QLearningConfig:
    """Store tunable Q-learning hyperparameters."""

    learning_rate: float
    discount_factor: float
    epsilon_start: float
    epsilon_end: float
    epsilon_decay: float
    seed: int


@dataclass(frozen=True)
class TrainingConfig:
    """Store execution limits for one training run."""

    episodes: int
    max_steps_per_episode: int


@dataclass(frozen=True)
class RewardConfig:
    """Store independent reward weights for transparent reward shaping."""

    merge_score_weight: float
    max_tile_bonus: float
    invalid_action_penalty: float
    win_bonus: float
    game_over_penalty: float


@dataclass(frozen=True)
class AgentConfig:
    """Collect all Agent parameter groups loaded from TOML."""

    q_learning: QLearningConfig
    training: TrainingConfig
    reward: RewardConfig


def load_agent_config(path: str | Path) -> AgentConfig:
    """Read Agent parameters from the supplied TOML configuration file."""

    with Path(path).open("rb") as config_file:
        raw = tomllib.load(config_file)
    return AgentConfig(
        q_learning=QLearningConfig(**raw["q_learning"]),
        training=TrainingConfig(**raw["training"]),
        reward=RewardConfig(**raw["reward"]),
    )
