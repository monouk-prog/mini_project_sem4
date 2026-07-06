def check_game_status(board, ai_marker, human_marker):
    """Terminal state checker for the evaluation loop."""
    size = len(board)

    for r in range(size):
        if board[r][0] != " " and all(board[r][c] == board[r][0] for c in range(size)):
            return 10 if board[r][0] == ai_marker else -10

    for c in range(size):
        if board[0][c] != " " and all(board[r][c] == board[0][c] for r in range(size)):
            return 10 if board[0][c] == ai_marker else -10

    if board[0][0] != " " and all(board[i][i] == board[0][0] for i in range(size)):
        return 10 if board[0][0] == ai_marker else -10

    if board[0][size-1] != " " and all(board[i][size-1-i] == board[0][size-1] for i in range(size)):
        return 10 if board[0][size-1] == ai_marker else -10

    if all(board[r][c] != " " for r in range(size) for c in range(size)):
        return 0  # Draw

    return None  # Ongoing game

def evaluate_board(board, ai_marker, human_marker):
    """Heuristic scoring system for calculating cut-off paths on larger grids."""
    score = 0
    size = len(board)
    lines = []

    for i in range(size):
        lines.append([board[i][j] for j in range(size)])
        lines.append([board[j][i] for j in range(size)])
    lines.append([board[i][i] for i in range(size)])
    lines.append([board[i][size-1-i] for i in range(size)])

    for line in lines:
        ai_count = line.count(ai_marker)
        human_count = line.count(human_marker)
        if ai_count > 0 and human_count == 0:
            score += ai_count
        elif human_count > 0 and ai_count == 0:
            score -= human_count

    return score

def minimax(board, depth, is_maximizing, alpha, beta, ai_marker, human_marker, max_depth):
    status = check_game_status(board, ai_marker, human_marker)
    if status is not None:
        return status

    if depth >= max_depth:
        return evaluate_board(board, ai_marker, human_marker)

    size = len(board)
    if is_maximizing:
        max_eval = float('-inf')
        for r in range(size):
            for c in range(size):
                if board[r][c] == " ":
                    board[r][c] = ai_marker
                    eval_score = minimax(board, depth + 1, False, alpha, beta, ai_marker, human_marker, max_depth)
                    board[r][c] = " "
                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for r in range(size):
            for c in range(size):
                if board[r][c] == " ":
                    board[r][c] = human_marker
                    eval_score = minimax(board, depth + 1, True, alpha, beta, ai_marker, human_marker, max_depth)
                    board[r][c] = " "
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
        return min_eval

def get_move(board, ai_marker, human_marker):
    """Calculates optimal moves using depth-capped Alpha-Beta pruning."""
    size = len(board)

    # Establish computation thresholds to protect performance on larger layouts
    if size == 3:
        max_depth = 9
    elif size == 4:
        max_depth = 4
    else:
        max_depth = 3

    # Fast-track performance optimization: if board is empty, take the center instantly
    empty_count = sum(1 for r in range(size) for c in range(size) if board[r][c] == " ")
    if empty_count == size * size:
        return (size // 2, size // 2)

    best_score = float('-inf')
    best_move = None

    for r in range(size):
        for c in range(size):
            if board[r][c] == " ":
                board[r][c] = ai_marker
                score = minimax(board, 0, False, float('-inf'), float('inf'), ai_marker, human_marker, max_depth)
                board[r][c] = " "
                if score > best_score:
                    best_score = score
                    best_move = (r, c)

    return best_move
