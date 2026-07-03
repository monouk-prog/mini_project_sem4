import random

def check_simulated_win(board, player):
    """Helper to check if a specific player has won the current board state."""
    size = len(board)

    # Check Rows and Columns
    for i in range(size):
        if all(board[i][j] == player for j in range(size)): return True
        if all(board[j][i] == player for j in range(size)): return True

    # Check Diagonals
    if all(board[i][i] == player for i in range(size)): return True
    if all(board[i][size - 1 - i] == player for i in range(size)): return True

    return False

def get_move(board, ai_marker, human_marker):
    """Wins if possible, blocks if threatened, takes center, or moves randomly."""
    size = len(board)
    empty_cells = [(r, c) for r in range(size) for c in range(size) if board[r][c] == " "]

    if not empty_cells:
        return None

    # 1. Attack: Can the AI win in this exact turn?
    for r, c in empty_cells:
        board[r][c] = ai_marker
        if check_simulated_win(board, ai_marker):
            board[r][c] = " "  # Reset board state
            return (r, c)
        board[r][c] = " "

    # 2. Defend: Is the human about to win? Block them!
    for r, c in empty_cells:
        board[r][c] = human_marker
        if check_simulated_win(board, human_marker):
            board[r][c] = " "  # Reset board state
            return (r, c)
        board[r][c] = " "

    # 3. Positional: Grab the dead center of the board if it's wide open
    center = size // 2
    if board[center][center] == " ":
        return (center, center)

    # 4. Fallback: Nothing critical happening, pick a random slot
    return random.choice(empty_cells)
