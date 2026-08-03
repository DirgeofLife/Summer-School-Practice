"""Run Q-learning after providing a concrete adapter for the 3D game engine."""

from __future__ import annotations

import argparse
from importlib import import_module
from pathlib import Path
from typing import cast

from game_2048.agent.config import load_agent_config
from game_2048.agent.contracts import SixDirectionGameEngine
from game_2048.agent.environment import ThreeD2048Environment
from game_2048.agent.q_learning import QLearningAgent
from game_2048.agent.training import save_metrics, train_q_learning


def load_engine(factory_path: str) -> SixDirectionGameEngine:
    """Create a game engine from a dotted module path ending in a factory name."""

    module_name, separator, factory_name = factory_path.partition(":")
    if not separator or not module_name or not factory_name:
        raise ValueError("Adapter must use the format package.module:factory_name")
    factory = getattr(import_module(module_name), factory_name)
    return cast(SixDirectionGameEngine, factory())


def parse_arguments() -> argparse.Namespace:
    """Read the configuration, adapter and metrics-output paths from the CLI."""

    parser = argparse.ArgumentParser(description="Train the 3D 2048 Q-learning Agent.")
    parser.add_argument(
        "--adapter",
        required=True,
        help="Game adapter factory, for example game_2048.my_engine:create_engine",
    )
    parser.add_argument("--config", default="configs/agent.toml")
    parser.add_argument("--metrics-output", default="artifacts/training_metrics.json")
    return parser.parse_args()


def main() -> None:
    """Load settings and an engine adapter, then train and persist metrics."""

    args = parse_arguments()
    config = load_agent_config(Path(args.config))
    environment = ThreeD2048Environment(load_engine(args.adapter), config.reward)
    agent = QLearningAgent(config.q_learning)
    metrics = train_q_learning(
        environment, agent, config.training, seed=config.q_learning.seed
    )
    save_metrics(metrics, args.metrics_output)
    print(f"Saved {len(metrics)} episode metrics to {args.metrics_output}")


if __name__ == "__main__":
    main()
