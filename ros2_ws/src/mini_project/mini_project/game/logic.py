class GameLogic:
    def __init__(self, size=3):
        self.size = size
        self.reset()
        
    def reset(self):
        self.board = [[" " for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        
        self.moves_x = []
        self.moves_o = []

    def make_move(self, r, c):
        """Attempts to place a piece. If 3 pieces already exist, the oldest is removed."""
        if self.game_over or self.board[r][c] != " ":
            return False
        
        self.board[r][c] = self.current_player
        
        if self.current_player == "X":
            self.moves_x.append((r, c))
            if len(self.moves_x) > 3:
                old_r, old_c = self.moves_x.pop(0)
                self.board[old_r][old_c] = " "
        else:
            self.moves_o.append((r, c))
            if len(self.moves_o) > 3:
                old_r, old_c = self.moves_o.pop(0)
                self.board[old_r][old_c] = " "

        self.winner = self.check_win()
        
        if self.winner:
            self.game_over = True
        else:
            self.switch_player()
        return True

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def get_fading_piece(self):
        """Returns the coordinates of the piece that will disappear on the player's NEXT turn."""
        if self.current_player == "X" and len(self.moves_x) == 3:
            return self.moves_x[0]
        elif self.current_player == "O" and len(self.moves_o) == 3:
            return self.moves_o[0]
        return None

    def check_win(self):
        # Check Rows
        for r in range(self.size):
            if self.board[r][0] != " " and all(self.board[r][c] == self.board[r][0] for c in range(self.size)):
                return self.board[r][0]
        
        # Check Columns
        for c in range(self.size):
            if self.board[0][c] != " " and all(self.board[r][c] == self.board[0][c] for r in range(self.size)):
                return self.board[0][c]
                
        if self.board[0][0] != " " and all(self.board[i][i] == self.board[0][0] for i in range(self.size)):
            return self.board[0][0]
            
        if self.board[0][self.size-1] != " " and all(self.board[i][self.size-1-i] == self.board[0][self.size-1] for i in range(self.size)):
            return self.board[0][self.size-1]

        return None
