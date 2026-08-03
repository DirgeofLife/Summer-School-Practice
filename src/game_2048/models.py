from enum import Enum

from pydantic import BaseModel


class Direction(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    FORWARD = "forward"
    BACK = "back"


class MoveRequest(BaseModel):
    direction: Direction


class GameState(BaseModel):
    board: list[list[int]]
    score: int
    won: bool
    game_over: bool


class GameState3D(BaseModel):
    board: list[list[list[int]]]
    score: int
    won: bool
    game_over: bool


class MoveResponse(BaseModel):
    state: GameState
    moved: bool


class MoveResponse3D(BaseModel):
    state: GameState3D
    moved: bool
