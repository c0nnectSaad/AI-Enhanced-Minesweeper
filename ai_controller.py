import numpy as np
from typing import Tuple, List, Optional
from board import Board

class AIController:
    def __init__(self, board: Board):
        self.board = board
        self.move_history: List[Tuple[int, int]] = []
        self.danger_zones: List[Tuple[int, int]] = []
        self.difficulty_factor = 1.0
        self.transform_probability = 0.1

    def record_move(self, x: int, y: int) -> None:
        """Record a player's move for analysis."""
        self.move_history.append((x, y))
        self._update_danger_zones(x, y)

    def _update_danger_zones(self, x: int, y: int) -> None:
        """Update danger zones based on player moves."""
        # Clear old danger zones that are too far from recent moves
        self.danger_zones = [pos for pos in self.danger_zones 
                           if self._manhattan_distance(pos, (x, y)) <= 5]
        
        # Add new danger zone if conditions are met
        if len(self.move_history) >= 3:
            recent_moves = self.move_history[-3:]
            if self._are_moves_clustered(recent_moves):
                center = self._get_cluster_center(recent_moves)
                if center not in self.danger_zones:
                    self.danger_zones.append(center)

    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _are_moves_clustered(self, moves: List[Tuple[int, int]]) -> bool:
        """Check if recent moves are clustered together."""
        return all(self._manhattan_distance(moves[i], moves[j]) <= 3 
                  for i in range(len(moves)) 
                  for j in range(i + 1, len(moves)))

    def _get_cluster_center(self, moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Calculate the center of a cluster of moves."""
        x_avg = sum(x for x, _ in moves) // len(moves)
        y_avg = sum(y for _, y in moves) // len(moves)
        return (x_avg, y_avg)

    def get_hint(self) -> Optional[Tuple[int, int]]:
        """Provide a hint for the next move."""
        safe_moves = self.board.get_safe_moves()
        if not safe_moves:
            return None

        # Calculate risk scores for each safe move
        move_scores = []
        for move in safe_moves:
            score = self._calculate_move_risk(move)
            move_scores.append((score, move))

        # Return the move with the lowest risk score
        return min(move_scores, key=lambda x: x[0])[1]

    def _calculate_move_risk(self, move: Tuple[int, int]) -> float:
        """Calculate risk score for a potential move."""
        x, y = move
        risk_score = 0.0

        # Higher risk near danger zones
        for zone in self.danger_zones:
            distance = self._manhattan_distance(move, zone)
            if distance <= 3:
                risk_score += (4 - distance) * self.difficulty_factor

        # Consider adjacent revealed numbers
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.board.height and 
                    0 <= new_y < self.board.width and 
                    self.board.revealed[new_x][new_y]):
                    risk_score += self.board.board[new_x][new_y] * 0.5

        return risk_score

    def update_board_state(self) -> None:
        """Update the board state based on AI analysis."""
        self._handle_mine_movement()
        self._handle_tile_transformation()
        self._adjust_difficulty()

    def _handle_mine_movement(self) -> None:
        """Handle dynamic mine movement based on danger zones."""
        for zone in self.danger_zones:
            if np.random.random() < 0.2 * self.difficulty_factor:
                self._move_mine_to_danger_zone(zone)

    def _move_mine_to_danger_zone(self, zone: Tuple[int, int]) -> None:
        """Move a mine to a danger zone."""
        x, y = zone
        # Find a mine that's far from the danger zone
        for mine_pos in list(self.board.mine_positions):
            if self._manhattan_distance(mine_pos, zone) > 5:
                # Find a suitable position near the danger zone
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_x, new_y = x + dx, y + dy
                        if (0 <= new_x < self.board.height and 
                            0 <= new_y < self.board.width and 
                            not self.board.revealed[new_x][new_y] and
                            (new_x, new_y) not in self.board.mine_positions):
                            self.board.reposition_mine(mine_pos, (new_x, new_y))
                            return

    def _handle_tile_transformation(self) -> None:
        """Handle tile state transformations."""
        if np.random.random() < self.transform_probability:
            self._transform_random_tile()

    def _transform_random_tile(self) -> None:
        """Transform a random tile's state."""
        unrevealed = [(x, y) 
                     for x in range(self.board.height) 
                     for y in range(self.board.width)
                     if not self.board.revealed[x][y]]
        
        if unrevealed:
            x, y = unrevealed[np.random.randint(len(unrevealed))]
            if (x, y) in self.board.mine_positions:
                # Transform mine to safe tile
                self.board.reposition_mine((x, y), 
                                        self._find_safe_transformation_spot())
            elif np.random.random() < 0.3 * self.difficulty_factor:
                # Transform safe tile to mine
                old_mine_pos = next(iter(self.board.mine_positions))
                self.board.reposition_mine(old_mine_pos, (x, y))

    def _find_safe_transformation_spot(self) -> Tuple[int, int]:
        """Find a safe spot for tile transformation."""
        candidates = [(x, y) 
                     for x in range(self.board.height) 
                     for y in range(self.board.width)
                     if not self.board.revealed[x][y] and 
                     (x, y) not in self.board.mine_positions]
        
        if candidates:
            return candidates[np.random.randint(len(candidates))]
        return (0, 0)  # Fallback position

    def _adjust_difficulty(self) -> None:
        """Adjust difficulty based on player performance."""
        revealed_count = np.sum(self.board.revealed)
        if revealed_count > 0:
            success_rate = len([1 for x, y in self.move_history 
                              if self.board.board[x][y] != -1]) / revealed_count
            
            # Adjust difficulty based on success rate
            if success_rate > 0.8:
                self.difficulty_factor = min(2.0, self.difficulty_factor + 0.1)
            elif success_rate < 0.5:
                self.difficulty_factor = max(0.5, self.difficulty_factor - 0.1) 