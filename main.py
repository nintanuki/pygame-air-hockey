import pygame
import sys
import random
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Rectangles, Movement and Collisions')
        self.clock = pygame.time.Clock()
        
        # Game Rectangles and Positions

        # Player centered in the bottom half
        self.player = pygame.Rect(
            (SCREEN_WIDTH / 2) - (PLAYER_WIDTH / 2),  # Center horizontally
            (SCREEN_HEIGHT * 7 / 8) - (PLAYER_HEIGHT / 2),  # Center in the bottom half
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        # Opponent centered in the top half
        self.opponent = pygame.Rect(
            (SCREEN_WIDTH / 2) - (OPPONENT_WIDTH / 2),  # Center horizontally
            (SCREEN_HEIGHT / 8) - (OPPONENT_HEIGHT / 2),  # Center in the top half
            OPPONENT_WIDTH,
            OPPONENT_HEIGHT
        )

        # Puck at the very center
        self.puck = pygame.Rect(
            (SCREEN_WIDTH / 2) - (PUCK_WIDTH / 2),  # Center horizontally
            (SCREEN_HEIGHT / 2) - (PUCK_HEIGHT / 2),  # Center vertically
            PUCK_WIDTH,
            PUCK_HEIGHT
        )

        # Puck speed
        self.puck_speed_x = PUCK_SPEED
        self.puck_speed_y = PUCK_SPEED
        
        # Colors
        self.player_color = RED
        self.opponent_color = RED
        self.puck_color = BLACK
        self.bg_color = WHITE

        # Used later to prevent the puck from getting "stuck" in the opponent
        self.collision_cooldown = 0
        
    def puck_movement(self):
        self.puck.x += self.puck_speed_x
        self.puck.y += self.puck_speed_y
        
        # Constrain the puck to the screen
        if self.puck.top <= 0 or self.puck.bottom >= SCREEN_HEIGHT:
            self.puck_speed_y *= -1
        if self.puck.left <= 0 or self.puck.right >= SCREEN_WIDTH:
            self.puck_speed_x *= -1
            
        # Handling collisions with the player
        if self.puck.colliderect(self.player):
            self.puck_speed_x *= -1
            self.puck_speed_y *= -1
            
        # Handling collisions with opponent
        if self.puck.colliderect(self.opponent) and self.collision_cooldown == 0:
            self.puck_speed_x *= -1
            self.puck_speed_y *= -1
            self.collision_cooldown = 10  # Frames before another collision is detected
        
    def opponent_movement(self):
        if self.puck.x < self.opponent.x:
            self.opponent.x -= OPPONENT_SPEED
        if self.puck.x > self.opponent.x:
            self.opponent.x += OPPONENT_SPEED
        if self.puck.y < self.opponent.y:
            self.opponent.y -= OPPONENT_SPEED
        if self.puck.y > self.opponent.y:
            self.opponent.y += OPPONENT_SPEED
        
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

            # Visuals
            self.screen.fill(self.bg_color) # Fill the screen with a black background
            self.draw_dotted_line()
            pygame.draw.rect(self.screen, self.player_color, self.player)
            pygame.draw.rect(self.screen, self.opponent_color, self.opponent)
            pygame.draw.rect(self.screen, self.puck_color, self.puck)
            
            pygame.display.flip()
            self.clock.tick(FRAMERATE)
            
if __name__ == '__main__':
    game_manager = Game()
    game_manager.run()