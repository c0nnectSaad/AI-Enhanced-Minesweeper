import numpy as np
from typing import Tuple, List, Set

class Board:
    def __init__(self, width: int = 16, height: int = 16, mine_count: int = 40):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.board = np.zeros((height, width), dtype=int)  # -1 for mines, 0-8 for numbers
        self.revealed = np.zeros((height, width), dtype=bool)
        self.flagged = np.zeros((height, width), dtype=bool)
        self.mine_positions: Set[Tuple[int, int]] = set()
        self.initialize_board()

    def initialize_board(self) -> None:
        """Initialize the board with random mine placement."""
        # Clear existing state
        self.board.fill(0)
        self.revealed.fill(False)
        self.flagged.fill(False)
        self.mine_positions.clear()

        # Place mines randomly
        positions = [(x, y) for x in range(self.height) for y in range(self.width)]
        mine_indices = np.random.choice(len(positions), self.mine_count, replace=False)
        mine_positions = set(positions[idx] for idx in mine_indices)
        
        for pos in positions:
            if pos in mine_positions:
                x, y = pos
                self.board[x][y] = -1
                self.mine_positions.add((x, y))

        # Calculate numbers
        self._update_numbers()

    def _update_numbers(self) -> None:
        """Update the numbers on the board based on mine positions."""
        for x in range(self.height):
            for y in range(self.width):
                if self.board[x][y] != -1:
                    self.board[x][y] = self._count_adjacent_mines(x, y)

    def _count_adjacent_mines(self, x: int, y: int) -> int:
        """Count adjacent mines for a given position."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.height and 
                    0 <= new_y < self.width and 
                    self.board[new_x][new_y] == -1):
                    count += 1
        return count

    def reveal(self, x: int, y: int) -> bool:
        """
        Reveal a tile. Returns True if the move was valid, False if it hit a mine.
        """
        if self.flagged[x][y] or self.revealed[x][y]:
            return True

        self.revealed[x][y] = True
        
        if self.board[x][y] == -1:
            return False
        
        # If empty tile, reveal adjacent tiles
        if self.board[x][y] == 0:
            self._reveal_adjacent(x, y)
            
        return True

    def _reveal_adjacent(self, x: int, y: int) -> None:
        """Recursively reveal adjacent empty tiles."""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.height and 
                    0 <= new_y < self.width and 
                    not self.revealed[new_x][new_y] and 
                    not self.flagged[new_x][new_y]):
                    self.revealed[new_x][new_y] = True
                    if self.board[new_x][new_y] == 0:
                        self._reveal_adjacent(new_x, new_y)

    def toggle_flag(self, x: int, y: int) -> None:
        """Toggle flag on a tile."""
        if not self.revealed[x][y]:
            self.flagged[x][y] = not self.flagged[x][y]

    def is_won(self) -> bool:
        """Check if the game is won."""
        return np.all((self.revealed | (self.board == -1)) == True)

    def get_safe_moves(self) -> List[Tuple[int, int]]:
        """Get list of safe moves for the hint system."""
        safe_moves = []
        for x in range(self.height):
            for y in range(self.width):
                if (not self.revealed[x][y] and 
                    not self.flagged[x][y] and 
                    self.board[x][y] != -1):
                    safe_moves.append((x, y))
        return safe_moves

    def reposition_mine(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """Reposition a mine from one position to another."""
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        if self.board[x1][y1] != -1 or self.board[x2][y2] == -1:
            return

        # Move the mine
        self.board[x1][y1] = 0
        self.board[x2][y2] = -1
        self.mine_positions.remove((x1, y1))
        self.mine_positions.add((x2, y2))

        # Update numbers in affected areas
        for x in range(max(0, x1-1), min(self.height, x1+2)):
            for y in range(max(0, y1-1), min(self.width, y1+2)):
                if self.board[x][y] != -1:
                    self.board[x][y] = self._count_adjacent_mines(x, y)

        for x in range(max(0, x2-1), min(self.height, x2+2)):
            for y in range(max(0, y2-1), min(self.width, y2+2)):
                if self.board[x][y] != -1:
                    self.board[x][y] = self._count_adjacent_mines(x, y) 