"""Tabular Q-learning policy for the discrete six-action 2048 environment."""

from __future__ import annotations

from collections import defaultdict
import random

from .config import QLearningConfig
from .contracts import Action, Observation


class QLearningAgent:
    """Learn state-action values with epsilon-greedy exploration."""

    def __init__(self, config: QLearningConfig) -> None:
        """Create an empty Q-table with reproducible random exploration."""

        self._config = config
        self._rng = random.Random(config.seed)
        self.epsilon = config.epsilon_start
        self.q_table: defaultdict[Observation, list[float]] = defaultdict(
            lambda: [0.0] * len(Action)
        )

    def select_action(self, state: Observation, explore: bool = True) -> Action:
        """Choose a random exploratory action or a highest-value learned action."""

        if explore and self._rng.random() < self.epsilon:
            return self._rng.choice(tuple(Action))
        values = self.q_table[state]
        best_value = max(values)
        best_indexes = [index for index, value in enumerate(values) if value == best_value]
        return tuple(Action)[self._rng.choice(best_indexes)]

    def learn(
        self,
        state: Observation,
        action: Action,
        reward: float,
        next_state: Observation,
        terminated: bool,
    ) -> None:
        """Update one Q-table value using the standard temporal-difference rule."""

        action_index = tuple(Action).index(action)
        current_value = self.q_table[state][action_index]
        next_value = 0.0 if terminated else max(self.q_table[next_state])
        target = reward + self._config.discount_factor * next_value
        self.q_table[state][action_index] = current_value + self._config.learning_rate * (
            target - current_value
        )

    def decay_exploration(self) -> None:
        """Reduce exploration after an episode without falling below its floor."""

        self.epsilon = max(
            self._config.epsilon_end,
            self.epsilon * self._config.epsilon_decay,
        )
