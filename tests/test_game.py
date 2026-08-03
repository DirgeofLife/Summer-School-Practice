import pytest
from game_2048.game import Board


class TestBoard:
    def test_new_board_has_two_tiles(self):
        board = Board()
        non_zero = sum(
            1 for r in range(4) for c in range(4) if board.grid[r][c] != 0
        )
        assert non_zero == 2

    def test_new_board_score_zero(self):
        board = Board()
        assert board.score == 0
        assert board.won is False

    def test_slide_left_merges_equal_tiles(self):
        board = Board()
        board.grid = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.score = 0
        moved = board.slide("left")
        assert moved is True
        assert board.grid[0][0] == 4
        assert board.score == 4
        # 滑动成功后还会随机生成 1 个新方块，总数应为 2（4 + 新方块）
        non_zero = sum(
            1 for r in range(4) for c in range(4) if board.grid[r][c] != 0
        )
        assert non_zero == 2

    def test_slide_left_compact(self):
        board = Board()
        board.grid = [
            [0, 0, 0, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("left")
        assert board.grid[0][0] == 2

    def test_slide_right_merges(self):
        board = Board()
        board.grid = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("right")
        assert board.grid[0][3] == 4

    def test_slide_up(self):
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("up")
        assert board.grid[0][0] == 4

    def test_slide_down(self):
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("down")
        assert board.grid[3][0] == 4

    def test_invalid_move_returns_false(self):
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        moved = board.slide("up")
        assert moved is False

    def test_win_detection(self):
        board = Board()
        board.grid = [
            [1024, 1024, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("left")
        assert board.won is True
        assert board.grid[0][0] == 2048

    def test_game_over_detection(self):
        board = Board()
        board.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        assert board.is_game_over() is True

    def test_game_not_over_with_empty(self):
        board = Board()
        board.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 0],
        ]
        assert board.is_game_over() is False

    def test_game_not_over_with_merge(self):
        board = Board()
        board.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 4],
        ]
        assert board.is_game_over() is False

    def test_spawn_after_move(self):
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("right")
        non_zero = sum(
            1 for r in range(4) for c in range(4) if board.grid[r][c] != 0
        )
        # Original 2 moved right + 1 new spawn = 2 tiles
        assert non_zero == 2

    def test_to_dict(self):
        board = Board()
        d = board.to_dict()
        assert "board" in d
        assert "score" in d
        assert "won" in d
        assert "game_over" in d
        assert len(d["board"]) == 4
        assert len(d["board"][0]) == 4

    def test_four_equal_in_row_merges_first_pair(self):
        """[2,2,2,2] → [4,4,0,0] + spawn"""
        board = Board()
        board.grid = [
            [2, 2, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("left")
        assert board.grid[0][0] == 4
        assert board.grid[0][1] == 4
        assert board.grid[0][2] == 0
        assert board.grid[0][3] == 0

    def test_up_with_gap(self):
        """Tiles in same column with gap merge upward"""
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("up")
        assert board.grid[0][0] == 4

    def test_down_with_gap(self):
        """Tiles in same column with gap merge downward"""
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("down")
        assert board.grid[3][0] == 4

    def test_right_single_compact(self):
        """Tile slides to right edge"""
        board = Board()
        board.grid = [
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("right")
        assert board.grid[0][3] == 2

    def test_multi_column_merge(self):
        """Two columns merge simultaneously"""
        board = Board()
        board.grid = [
            [2, 4, 0, 0],
            [2, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("up")
        assert board.grid[0][0] == 4
        assert board.grid[0][1] == 8

    def test_no_merge_different_values(self):
        """Different values adjacent don't merge"""
        board = Board()
        board.grid = [
            [2, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        board.slide("left")
        assert board.grid[0][0] == 2
        assert board.grid[0][1] == 4
