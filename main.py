import pygame
import sys
import random
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Air Hockey')
        self.clock = pygame.time.Clock()
        
        #Game Rectangles and Positions
        self.player = pygame.Rect(
            (SCREEN_WIDTH / 2) - (PLAYER_WIDTH / 2),  # Center horizontally
            (SCREEN_HEIGHT * 7 / 8) - (PLAYER_HEIGHT / 2),  # Center in the bottom half
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )
        self.opponent = pygame.Rect(
            (SCREEN_WIDTH / 2) - (OPPONENT_WIDTH / 2),  # Center horizontally
            (SCREEN_HEIGHT / 8) - (OPPONENT_HEIGHT / 2),  # Center in the top half
            OPPONENT_WIDTH,
            OPPONENT_HEIGHT
        )
        self.puck = pygame.Rect(0, 0, PUCK_WIDTH, PUCK_HEIGHT)
        self.reset_puck()
        
        # Goals
        self.player_goal = pygame.Rect((SCREEN_WIDTH / 2) - (SCREEN_WIDTH / 8), SCREEN_HEIGHT - 10, SCREEN_WIDTH / 4, 10)
        self.opponent_goal = pygame.Rect((SCREEN_WIDTH / 2) - (SCREEN_WIDTH / 8), 0, SCREEN_WIDTH / 4, 10)
        
        # Scoring
        self.player_score = 0
        self.opponent_score = 0
        
        # Used later to prevent the puck from getting "stuck" in the opponent
        self.collision_cooldown = 0
        
    def puck_movement(self):
        """Move the puck and handles collisions."""
        self.puck.x += self.puck_speed_x
        self.puck.y += self.puck_speed_y
        
        # Constrain the puck to the screen
        if self.puck.top <= 0 or self.puck.bottom >= SCREEN_HEIGHT:
            self.puck_speed_y *= -1
            self.apply_inertia()
        if self.puck.left <= 0 or self.puck.right >= SCREEN_WIDTH:
            self.puck_speed_x *= -1
            self.apply_inertia()
            
        # Handling collisions with the player
        if self.puck.colliderect(self.player):
            self.puck_speed_x *= -1
            self.puck_speed_y *= -1
            self.increase_speed()
            
        # Handling collisions with opponent
        if self.puck.colliderect(self.opponent) and self.collision_cooldown == 0:
            self.puck_speed_x *= -1
            self.puck_speed_y *= -1
            self.increase_speed()
            self.collision_cooldown = 100  # Frames before another collision is detected
    
    def apply_inertia(self):
        """Apply inertia to the puck to slow it down."""
        self.puck_speed_x *= 0.9
        self.puck_speed_y *= 0.9
    
    def increase_speed(self):
        """Increase the puck speed when hit."""
        self.puck_speed_x *= 1.1
        self.puck_speed_y *= 1.1
    
    def opponent_movement(self):
        """Move the opponent towards the puck."""
        if self.puck.x < self.opponent.x:
            self.opponent.x -= OPPONENT_SPEED
        if self.puck.x > self.opponent.x:
            self.opponent.x += OPPONENT_SPEED
        if self.puck.y < self.opponent.y:
            self.opponent.y -= OPPONENT_SPEED
        if self.puck.y > self.opponent.y:
            self.opponent.y += OPPONENT_SPEED

    def reset_puck(self):
        """Reset the puck to the center with a random direction."""
        if random.choice([True, False]):
            # Near player
            self.puck.x = (SCREEN_WIDTH / 2) - (PUCK_WIDTH / 2)
            self.puck.y = (SCREEN_HEIGHT * 3 / 4) - (PUCK_HEIGHT / 2)
        else:
            # Near opponent
            self.puck.x = (SCREEN_WIDTH / 2) - (PUCK_WIDTH / 2)
            self.puck.y = (SCREEN_HEIGHT / 4) - (PUCK_HEIGHT / 2)
        self.puck_speed_x = random.choice([-1, 1]) * INITIAL_PUCK_SPEED
        self.puck_speed_y = random.choice([-1, 1]) * INITIAL_PUCK_SPEED

    def check_goals(self):
        """Check if the puck has entered a goal."""
        if self.puck.colliderect(self.player_goal):
            self.opponent_score += 1
            self.reset_puck()
        elif self.puck.colliderect(self.opponent_goal):
            self.player_score += 1
            self.reset_puck()

    def display_scores(self):
        """Display the scores on the screen."""
        font = pygame.font.Font('Pixeled.ttf', 12)
        player_score_text = font.render(f"Player: {self.player_score}", True, BLACK) # looks better with anti-aliasing?
        opponent_score_text = font.render(f"Opponent: {self.opponent_score}", True, BLACK)
        self.screen.blit(player_score_text, (10, SCREEN_HEIGHT - 40))
        self.screen.blit(opponent_score_text, (10, 10))

    def draw_dotted_line(self):
        """Draws a dotted line in the middle of the screen across the center of the table"""
        # Set the starting position
        y = SCREEN_HEIGHT // 2  # Middle of the screen vertically
        x = 0  # Start from the left side of the screen
        segment_length = 10  # Length of each dash
        gap_length = 5  # Length of the gap between dashes
        
        # Loop through the width of the screen, drawing segments
        while x < SCREEN_WIDTH:
            pygame.draw.line(self.screen, BLACK, (x, y), (x + segment_length, y))
            x += segment_length + gap_length
    
    def run(self):
        """Main game loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            # Get the current state of all keys
            keys = pygame.key.get_pressed()

            # Constraining the player to their side of the screen
            if self.player.top <= SCREEN_HEIGHT / 2:
                self.player.top = SCREEN_HEIGHT / 2
            if self.player.bottom >= SCREEN_HEIGHT:
                self.player.bottom = SCREEN_HEIGHT
            if self.player.left <= 0:
                self.player.left = 0
            if self.player.right >= SCREEN_WIDTH:
                self.player.right = SCREEN_WIDTH
                
            # Constraining the opponent to their side of the screen
            if self.opponent.top <= 0:
                self.opponent.top = 0
            if self.opponent.bottom >= SCREEN_HEIGHT / 2:
                self.opponent.bottom = SCREEN_HEIGHT / 2
            if self.opponent.left <= 0:
                self.opponent.left = 0
            if self.opponent.right >= SCREEN_WIDTH:
                self.opponent.right = SCREEN_WIDTH

            # Cooldown for collisions
            if self.collision_cooldown > 0:
                self.collision_cooldown -= 1

            # Update player position based on keys being held down (continuous movement)
            if keys[pygame.K_LEFT]:
                self.player.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.player.x += PLAYER_SPEED
            if keys[pygame.K_UP]:
                self.player.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                self.player.y += PLAYER_SPEED

            # Game Logic
            self.puck_movement()
            self.opponent_movement()
            self.check_goals()

            # Visuals
            self.screen.fill(WHITE) # Fill the screen with a black background
            self.draw_dotted_line()
            pygame.draw.rect(self.screen, BLUE, self.player_goal)
            pygame.draw.rect(self.screen, BLUE, self.opponent_goal)
            pygame.draw.rect(self.screen, RED, self.player)
            pygame.draw.rect(self.screen, RED, self.opponent)
            pygame.draw.rect(self.screen, BLACK, self.puck)
            self.display_scores()
            
            pygame.display.flip()
            self.clock.tick(FRAMERATE)
            
if __name__ == '__main__':
    game_manager = Game()
    game_manager.run()