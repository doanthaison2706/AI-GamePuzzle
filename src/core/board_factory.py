from src.core.board import Board


class BoardFactory:
    """Factory for creating boards with size-specific scramble configurations."""

    CONFIGS = {
        3: {"num_shuffles": 50},
        4: {"num_shuffles": 200},
        5: {"num_shuffles": 500},
        6: {"num_shuffles": 1000},
        7: {"num_shuffles": 2000},
    }

    @classmethod
    def create(cls, size: int) -> Board:
        if size not in cls.CONFIGS:
            raise ValueError(f"Unsupported board size: {size}x{size}. Supported: 3-7")
        board = Board(size)
        board.num_shuffles = cls.CONFIGS[size]["num_shuffles"]
        return board
