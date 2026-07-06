class Board:

    def __init__(self, size=3):
        self.size = size
        self.grid = [[" " for _ in range(size)] for _ in range(size)]

    def place(self, r, c, p):
        if self.grid[r][c] == " ":
            self.grid[r][c] = p
            return True
        return False

    def reset(self):
        self.grid = [[" " for _ in range(self.size)] for _ in range(self.size)]
