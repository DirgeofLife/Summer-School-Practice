from .game import Board
from .game3d import Board3D

# 2D 4x4 棋盘的会话存储
sessions: dict[str, Board] = {}

# 3D 4x4x4 棋盘的会话存储
sessions3d: dict[str, Board3D] = {}
