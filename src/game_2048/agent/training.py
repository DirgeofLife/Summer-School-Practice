"""Train the tabular Agent and produce visualisation-ready episode metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .config import TrainingConfig
from .environment import ThreeD2048Environment
from .q_learning import QLearningAgent


@dataclass(frozen=True)
class EpisodeMetric:
    """Capture the outcome and policy state of one training episode."""

    episode: int
    total_reward: float
    score: int
    largest_tile: int
    steps: int
    epsilon: float
    won: bool


def train_q_learning(
    environment: ThreeD2048Environment,
    agent: QLearningAgent,
    config: TrainingConfig,
    seed: int,
) -> list[EpisodeMetric]:
    """Train the Agent for the configured episodes and return compact metrics."""

    metrics: list[EpisodeMetric] = []
    for episode in range(config.episodes):
        state, _ = environment.reset(seed=seed + episode)
        total_reward = 0.0
        info: dict[str, object] = {}
        for step in range(1, config.max_steps_per_episode + 1):
            action = agent.select_action(state)
            next_state, reward, terminated, _, info = environment.step(action)
            agent.learn(state, action, reward, next_state, terminated)
            state = next_state
            total_reward += reward
            if terminated:
                break
        metrics.append(
            EpisodeMetric(
                episode=episode + 1,
                total_reward=total_reward,
                score=int(info["score"]),
                largest_tile=int(info["largest_tile"]),
                steps=step,
                epsilon=agent.epsilon,
                won=bool(info["won"]),
            )
        )
        agent.decay_exploration()
    return metrics


def save_metrics(metrics: list[EpisodeMetric], path: str | Path) -> None:
    """Write episode metrics as JSON for the standalone browser dashboard."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([asdict(metric) for metric in metrics], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
