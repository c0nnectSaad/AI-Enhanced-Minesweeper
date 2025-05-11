import pygame
import sys
from board import Board
from ai_controller import AIController

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 40
WINDOW_SIZE = 550  # Fixed window size
HEADER_HEIGHT = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HEADER_HEIGHT))
        pygame.display.set_caption("AI Minesweeper")
        
        # Initialize with medium difficulty
        self.board = Board(16, 16, 40)
        self.ai = AIController(self.board)
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        
        self.flag_mode = False
        self.game_over = False
        self.won = False
        self.hint_cooldown = 0
        self.show_hint = False
        self.hint_position = None
        self.game_started = False
        self.score = 0
        self.start_time = 0
        self.best_score = 0
        self.difficulty = "Medium"  # Default difficulty

    def show_start_menu(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.title_font.render("Minesweeper", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_SIZE//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw difficulty options
        difficulties = ["Easy", "Medium", "Hard"]
        for i, diff in enumerate(difficulties):
            color = GREEN if diff == self.difficulty else BLACK
            text = self.font.render(diff, True, color)
            text_rect = text.get_rect(center=(WINDOW_SIZE//2, 200 + i * 50))
            self.screen.blit(text, text_rect)
        
        # Draw start button
        start_text = self.font.render("Start Game", True, BLUE)
        start_rect = start_text.get_rect(center=(WINDOW_SIZE//2, 400))
        self.screen.blit(start_text, start_rect)
        
        # Draw best score
        if self.best_score > 0:
            score_text = self.small_font.render(f"Best Score: {self.best_score}", True, BLACK)
            self.screen.blit(score_text, (10, WINDOW_SIZE + HEADER_HEIGHT - 30))
        
        pygame.display.flip()
        
        # Handle menu events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Check difficulty selection
                for i, diff in enumerate(difficulties):
                    if 200 + i * 50 - 20 <= y <= 200 + i * 50 + 20:
                        self.difficulty = diff
                        if diff == "Easy":
                            self.board = Board(10, 10, 10)
                        elif diff == "Medium":
                            self.board = Board(16, 16, 40)
                        else:  # Hard
                            self.board = Board(20, 20, 80)
                        self.ai = AIController(self.board)
                
                # Check start button
                if 380 <= y <= 420:
                    self.game_started = True
                    self.start_time = pygame.time.get_ticks()
                    return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_started = True
                    self.start_time = pygame.time.get_ticks()
                    return True
        
        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.flag_mode = not self.flag_mode
                # existing key handling
                if self.game_over:
                    self.__init__()
                    self.game_started = False
                    return True
                if event.key == pygame.K_h and self.hint_cooldown <= 0:
                    self.show_hint = True
                    self.hint_position = self.ai.get_hint()
                    self.hint_cooldown = 100
                    self.score -= 20  # Penalty for using hint
                elif event.key == pygame.K_r:
                    self.__init__()
                elif event.key == pygame.K_ESCAPE:
                    self.game_started = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.__init__()
                    self.game_started = False
                    return True
                if not self.game_over:
                    x, y = event.pos
                    board_y = (y - HEADER_HEIGHT) // TILE_SIZE
                    board_x = x // TILE_SIZE
                    
                    if 0 <= board_y < self.board.height and 0 <= board_x < self.board.width:
                        if event.button == 1:  # Left click
                            if self.flag_mode:
                                self.board.toggle_flag(board_x, board_y)
                            else:
                                if not self.board.flagged[board_x][board_y]:
                                    result = self.board.reveal(board_x, board_y)
                                    if not result:
                                        self.game_over = True
                                    else:
                                        self.ai.record_move(board_x, board_y)
                                        self.ai.update_board_state()
                                        self.score += 10  # Add points for successful reveal
                        elif event.button == 3:  # Right click still works too
                            self.board.toggle_flag(board_x, board_y)
                            if self.board.flagged[board_x][board_y]:
                                self.score += 5  # Add points for correct flag placement
        
        return True

    def update(self):
        if self.hint_cooldown > 0:
            self.hint_cooldown -= 1
        
        if not self.game_over and self.game_started:
            self.won = self.board.is_won()
            if self.won:
                self.game_over = True
                # Calculate final score based on time
                time_taken = (pygame.time.get_ticks() - self.start_time) // 1000
                time_bonus = max(0, 1000 - time_taken)
                self.score += time_bonus
                
                # Update best score
                if self.score > self.best_score:
                    self.best_score = self.score

    def draw(self):
        self.screen.fill(WHITE)
        
        if not self.game_started:
            return
        
        # Draw header
        pygame.draw.rect(self.screen, GRAY, (0, 0, WINDOW_SIZE, HEADER_HEIGHT))
        
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Draw difficulty
        diff_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, BLACK)
        self.screen.blit(diff_text, (WINDOW_SIZE - 150, 10))
        
        # Draw hint cooldown
        if self.hint_cooldown > 0:
            cooldown_text = self.small_font.render(f"Hint Cooldown: {self.hint_cooldown//10}", True, BLACK)
            self.screen.blit(cooldown_text, (10, 35))
        else:
            hint_text = self.small_font.render("Press H for Hint", True, BLACK)
            self.screen.blit(hint_text, (10, 35))
        
        hint_y = 35
        if self.hint_cooldown > 0:
            cooldown_text = self.small_font.render(f"Hint Cooldown: {self.hint_cooldown//10}", True, BLACK)
            self.screen.blit(cooldown_text, (10, 35))
        else:
            hint_text = self.small_font.render("Press H for Hint", True, BLACK)
            self.screen.blit(hint_text, (10, 35))
        flag_text = self.small_font.render(f"Press F for Flag ({'ON' if self.flag_mode else 'OFF'})", True, BLACK)
        self.screen.blit(flag_text, (200, hint_y))

        # Draw game state
        if self.game_over:
            state_text = "You Win!" if self.won else "Game Over!"
            text = self.font.render(state_text, True, GREEN if self.won else RED)
            self.screen.blit(text, (WINDOW_SIZE//2 - text.get_width()//2, 10))
            
            if self.won:
                final_score = self.font.render(f"Final Score: {self.score}", True, BLUE)
                self.screen.blit(final_score, (WINDOW_SIZE//2 - final_score.get_width()//2, 35))
        
        # Draw board
        for y in range(self.board.height):
            for x in range(self.board.width):
                rect = pygame.Rect(x * TILE_SIZE, 
                                 y * TILE_SIZE + HEADER_HEIGHT, 
                                 TILE_SIZE, TILE_SIZE)
                
                # Draw tile background
                if self.board.revealed[x][y]:
                    pygame.draw.rect(self.screen, GRAY, rect)
                else:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                
                # Draw grid lines
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                
                # Draw hint
                if (self.show_hint and 
                    self.hint_position and 
                    (x, y) == self.hint_position and 
                    not self.board.revealed[x][y]):
                    hint_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    hint_surface.set_alpha(128)
                    hint_surface.fill(GREEN)
                    self.screen.blit(hint_surface, rect)
                
                if self.board.revealed[x][y]:
                    if self.board.board[x][y] == -1:
                        # Draw mine
                        pygame.draw.circle(self.screen, BLACK,
                                         (x * TILE_SIZE + TILE_SIZE//2,
                                          y * TILE_SIZE + TILE_SIZE//2 + HEADER_HEIGHT),
                                         TILE_SIZE//4)
                    elif self.board.board[x][y] > 0:
                        # Draw number
                        text = self.font.render(str(self.board.board[x][y]), True, BLUE)
                        text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE//2,
                                                        y * TILE_SIZE + TILE_SIZE//2 + HEADER_HEIGHT))
                        self.screen.blit(text, text_rect)
                
                elif self.board.flagged[x][y]:
                    # Draw flag
                    pygame.draw.polygon(self.screen, RED,
                                     [(x * TILE_SIZE + TILE_SIZE//4,
                                       y * TILE_SIZE + TILE_SIZE//4 + HEADER_HEIGHT),
                                      (x * TILE_SIZE + TILE_SIZE//4,
                                       y * TILE_SIZE + TILE_SIZE*3//4 + HEADER_HEIGHT),
                                      (x * TILE_SIZE + TILE_SIZE*3//4,
                                       y * TILE_SIZE + TILE_SIZE//2 + HEADER_HEIGHT)])
        
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            if not self.game_started:
                running = self.show_start_menu()
            else:
                running = self.handle_events()
                self.update()
                self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit() 