"""Test the Agent contract, reward calculation and Q-learning update."""

from __future__ import annotations

from game_2048.agent.config import QLearningConfig, RewardConfig
from game_2048.agent.contracts import Action, EngineMove, GameSnapshot
from game_2048.agent.environment import ThreeD2048Environment, encode_observation
from game_2048.agent.q_learning import QLearningAgent


def make_faces(first_tile: int = 2) -> tuple:
    """Create a compact six-face 4×4 board for Agent tests."""

    face = tuple(tuple(0 for _ in range(4)) for _ in range(4))
    first_face = ((first_tile, 0, 0, 0),) + face[1:]
    return (first_face, face, face, face, face, face)


class FakeEngine:
    """Provide deterministic transitions while the real 3D engine is unfinished."""

    def __init__(self) -> None:
        """Prepare the first fake snapshot."""

        self._snapshot = GameSnapshot(make_faces(), score=0, won=False, game_over=False)

    def reset(self, seed: int | None = None) -> GameSnapshot:
        """Reset to a fixed board so reward assertions are reproducible."""

        self._snapshot = GameSnapshot(make_faces(), score=0, won=False, game_over=False)
        return self._snapshot

    def move(self, action: Action) -> EngineMove:
        """Return one valid merge for left and an invalid transition otherwise."""

        if action == Action.LEFT:
            self._snapshot = GameSnapshot(make_faces(4), score=4, won=False, game_over=False)
            return EngineMove(self._snapshot, moved=True, score_delta=4)
        return EngineMove(self._snapshot, moved=False, score_delta=0)


def reward_config() -> RewardConfig:
    """Build intentionally simple weights used by the reward unit tests."""

    return RewardConfig(0.01, 1.0, -0.5, 100.0, -10.0)


def test_observation_encodes_all_six_faces() -> None:
    """Encode 96 cells and convert tiles into base-two exponents."""

    observation = encode_observation(GameSnapshot(make_faces(8), 0, False, False))
    assert len(observation) == 96
    assert observation[0] == 3


def test_environment_rewards_merge_and_max_tile_growth() -> None:
    """Reward a valid merge with its score contribution and progress bonus."""

    environment = ThreeD2048Environment(FakeEngine(), reward_config())
    environment.reset(seed=1)
    _, reward, terminated, _, info = environment.step(Action.LEFT)
    assert reward == 1.04
    assert terminated is False
    assert info["reward"]["merge"] == 0.04
    assert info["reward"]["max_tile"] == 1.0


def test_environment_penalizes_invalid_action() -> None:
    """Apply the configured penalty when an action cannot move the board."""

    environment = ThreeD2048Environment(FakeEngine(), reward_config())
    environment.reset()
    _, reward, _, _, info = environment.step(Action.W)
    assert reward == -0.5
    assert info["moved"] is False


def test_q_learning_updates_the_selected_action() -> None:
    """Apply a deterministic temporal-difference update to the Q-table."""

    config = QLearningConfig(0.5, 0.9, 0.0, 0.0, 1.0, 7)
    agent = QLearningAgent(config)
    state = (0,) * 96
    next_state = (1,) * 96
    agent.learn(state, Action.S, reward=2.0, next_state=next_state, terminated=True)
    assert agent.q_table[state][5] == 1.0
