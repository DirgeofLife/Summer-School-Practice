"""三维 2048 棋盘：在 4x4x4 立方体空间 (layer, row, col) 上运行，支持 6 方向滑动。"""

from __future__ import annotations

import random


class Board3D:
    """三维 2048 棋盘。

    棋盘索引为 grid[layer][row][col]，layer=0 为最底层。
    方向语义：
      - left/right   沿 col 轴（横向）
      - up/down      沿 row 轴（纵向）
      - forward/back 沿 layer 轴（层间），forward 向 layer=0 滑动，back 向 layer=3 滑动
    """

    SIZE = 4
    SPAWN_VALUES = [2] * 9 + [4]  # 90% 2, 10% 4
    WIN_VALUE = 2048

    def __init__(self) -> None:
        """初始化空棋盘并随机生成两个初始方块。"""
        self.grid: list[list[list[int]]] = [
            [[0] * Board3D.SIZE for _ in range(Board3D.SIZE)]
            for _ in range(Board3D.SIZE)
        ]
        self.score: int = 0
        self.won: bool = False
        self._spawn_tile()
        self._spawn_tile()

    def _spawn_tile(self) -> None:
        """在随机空位上生成一个新方块（90% 为 2，10% 为 4）。"""
        empty = [
            (z, r, c)
            for z in range(Board3D.SIZE)
            for r in range(Board3D.SIZE)
            for c in range(Board3D.SIZE)
            if self.grid[z][r][c] == 0
        ]
        if not empty:
            return
        z, r, c = random.choice(empty)
        self.grid[z][r][c] = random.choice(Board3D.SPAWN_VALUES)

    def _slide_line(self, line: list[int]) -> list[int]:
        """对一维数组执行 2048 滑动合并（靠向索引 0 侧），返回合并后的数组并累加分数。"""
        compacted = [v for v in line if v != 0]
        merged: list[int] = []
        i = 0
        while i < len(compacted):
            if i + 1 < len(compacted) and compacted[i] == compacted[i + 1]:
                new_val = compacted[i] * 2
                merged.append(new_val)
                self.score += new_val
                if new_val == Board3D.WIN_VALUE:
                    self.won = True
                i += 2
            else:
                merged.append(compacted[i])
                i += 1
        merged.extend([0] * (Board3D.SIZE - len(merged)))
        return merged

    def _get_line(self, f1: int, f2: int, axis: int) -> list[int]:
        """按轴取出一条线：axis=0 沿 col，axis=1 沿 row，axis=2 沿 layer。"""
        if axis == 0:
            return [self.grid[f1][f2][c] for c in range(Board3D.SIZE)]
        if axis == 1:
            return [self.grid[f1][r][f2] for r in range(Board3D.SIZE)]
        return [self.grid[z][f1][f2] for z in range(Board3D.SIZE)]

    def _set_line(self, f1: int, f2: int, axis: int, line: list[int]) -> None:
        """把一条线写回棋盘，axis 语义同 _get_line。"""
        for k in range(Board3D.SIZE):
            if axis == 0:
                self.grid[f1][f2][k] = line[k]
            elif axis == 1:
                self.grid[f1][k][f2] = line[k]
            else:
                self.grid[k][f1][f2] = line[k]

    def _apply_slide(self, axis: int, f1: int, f2: int, reverse: bool) -> None:
        """对单条线执行滑动：reverse=False 向索引小的一侧，否则向索引大的一侧。"""
        line = self._get_line(f1, f2, axis)
        if reverse:
            line = line[::-1]
        line = self._slide_line(line)
        if reverse:
            line = line[::-1]
        self._set_line(f1, f2, axis, line)

    def slide(self, direction: str) -> bool:
        """按方向滑动整个棋盘。棋盘有变化返回 True，并随机生成一个新方块。"""
        axis_map = {
            "left": (0, False),
            "right": (0, True),
            "up": (1, False),
            "down": (1, True),
            "forward": (2, False),
            "back": (2, True),
        }
        axis, reverse = axis_map[direction]
        old = [[row[:] for row in layer] for layer in self.grid]

        if axis == 0:
            for z in range(Board3D.SIZE):
                for r in range(Board3D.SIZE):
                    self._apply_slide(0, z, r, reverse)
        elif axis == 1:
            for z in range(Board3D.SIZE):
                for c in range(Board3D.SIZE):
                    self._apply_slide(1, z, c, reverse)
        else:
            for r in range(Board3D.SIZE):
                for c in range(Board3D.SIZE):
                    self._apply_slide(2, r, c, reverse)

        if self.grid == old:
            return False
        self._spawn_tile()
        return True

    def is_game_over(self) -> bool:
        """判断是否无空格且相邻（三维 6 邻域）无相同方块。"""
        size = Board3D.SIZE
        for z in range(size):
            for r in range(size):
                for c in range(size):
                    if self.grid[z][r][c] == 0:
                        return False
                    val = self.grid[z][r][c]
                    if c + 1 < size and val == self.grid[z][r][c + 1]:
                        return False
                    if r + 1 < size and val == self.grid[z][r + 1][c]:
                        return False
                    if z + 1 < size and val == self.grid[z + 1][r][c]:
                        return False
        return True

    def to_dict(self) -> dict:
        """输出可序列化的棋盘状态。"""
        return {
            "board": [[row[:] for row in layer] for layer in self.grid],
            "score": self.score,
            "won": self.won,
            "game_over": self.is_game_over(),
        }
