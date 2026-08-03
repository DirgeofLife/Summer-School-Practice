"""Board3D 三维 2048 棋盘逻辑测试。"""

import pytest

from game_2048.game3d import Board3D


def _empty_grid():
    """构造一个全零的 4x4x4 棋盘。"""
    return [[[0] * 4 for _ in range(4)] for _ in range(4)]


class TestBoard3D:
    def test_new_board_has_two_tiles(self):
        board = Board3D()
        non_zero = sum(
            1
            for z in range(4)
            for r in range(4)
            for c in range(4)
            if board.grid[z][r][c] != 0
        )
        assert non_zero == 2

    def test_new_board_score_zero(self):
        board = Board3D()
        assert board.score == 0
        assert board.won is False

    def test_slide_left_merges_equal_tiles_in_row(self):
        board = Board3D()
        board.grid = _empty_grid()
        board.grid[0][0] = [2, 2, 0, 0]
        board.score = 0
        moved = board.slide("left")
        assert moved is True
        assert board.grid[0][0] == [4, 0, 0, 0]
        assert board.score == 4

    def test_slide_up_merges_equal_tiles_in_column(self):
        board = Board3D()
        board.grid = _empty_grid()
        board.grid[0][0][0] = 2
        board.grid[0][1][0] = 2
        board.score = 0
        moved = board.slide("up")
        assert moved is True
        assert board.grid[0][0][0] == 4
        assert board.grid[0][1][0] == 0
        assert board.score == 4

    def test_slide_forward_merges_across_layers(self):
        board = Board3D()
        board.grid = _empty_grid()
        board.grid[0][0][0] = 2
        board.grid[1][0][0] = 2
        board.score = 0
        moved = board.slide("forward")
        assert moved is True
        assert board.grid[0][0][0] == 4
        assert board.grid[1][0][0] == 0
        assert board.score == 4

    def test_slide_back_merges_across_layers(self):
        board = Board3D()
        board.grid = _empty_grid()
        board.grid[2][1][1] = 2
        board.grid[3][1][1] = 2
        moved = board.slide("back")
        assert moved is True
        assert board.grid[3][1][1] == 4
        assert board.grid[2][1][1] == 0

    def test_no_change_returns_false(self):
        board = Board3D()
        board.grid = _empty_grid()
        board.grid[0][0][0] = 4
        board.grid[0][0][1] = 2
        moved = board.slide("left")
        assert moved is False
        # 棋盘未变化且未生成新方块
        assert board.grid[0][0][0] == 4
        assert board.grid[0][0][1] == 2

    def test_game_over_detection(self):
        board = Board3D()
        # 用 (z+r+c) 奇偶交错填满，保证任意相邻格数值不同
        board.grid = [
            [[((z + r + c) % 2) + 1 for c in range(4)] for r in range(4)]
            for z in range(4)
        ]
        board.score = 0
        assert board.is_game_over() is True
        assert board.to_dict()["game_over"] is True

    def test_not_game_over_with_empty(self):
        board = Board3D()
        assert board.is_game_over() is False

    def test_slide_invalid_direction_raises(self):
        board = Board3D()
        with pytest.raises(KeyError):
            board.slide("northwest")
