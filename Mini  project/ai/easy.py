import random

def get_move(board, ai_marker, human_marker):
    """Selects a completely random available spot on the board."""
    size = len(board)
    empty_cells = [(r, c) for r in range(size) for c in range(size) if board[r][c] == " "]

    if empty_cells:
        return random.choice(empty_cells)
    return None
