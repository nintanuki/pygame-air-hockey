import pygame
import sys
import random
from settings import *
from audio import Audio

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Air Hockey')
        self.clock = pygame.time.Clock()
        self.audio = Audio()
        
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
        self.player_goal = pygame.Rect((SCREEN_WIDTH / 2) - (SCREEN_WIDTH / 8), SCREEN_HEIGHT - 10, SCREEN_WIDTH / 4, 10)
        self.opponent_goal = pygame.Rect((SCREEN_WIDTH / 2) - (SCREEN_WIDTH / 8), 0, SCREEN_WIDTH / 4, 10)
        
        # Scoring
        self.player_score = 0
        self.opponent_score = 0
        
        # Fonts
        self.score_font = pygame.font.Font('Pixeled.ttf', 12)
        self.countdown_font = pygame.font.Font('Pixeled.ttf', 32)
        
        # Countdown timer variables
        self.countdown = 0
        self.COUNTDOWN_EVENT = pygame.USEREVENT + 1 # Custom event, the +1 is to avoid conflicts with other events like QUIT
        self.COUNTDOWN_INTERVAL = 1000  # 1000 ms = 1 second

        # Used later to prevent the puck from getting "stuck" in the opponent
        self.collision_cooldown = 0
        
        # Calculate the player's velocity to influence the puck's direction
        self.player_velocity = [0, 0]  # Track player paddle velocity (x, y)
        self.prev_player_pos = self.player.center  # Store the previous position
        
        self.is_spiking = False # Flag to track if the player is spiking
        self.spike_speed = 30 # Speed at which the paddle moves upwards when spiking

        
        self.reset_puck()
        
    def puck_movement(self):
        """Move the puck and handles collisions."""
        self.puck.x += self.puck_speed_x
        self.puck.y += self.puck_speed_y
        
        # Constrain the puck to the screen
        if self.puck.top <= 0 or self.puck.bottom >= SCREEN_HEIGHT:
            self.puck_speed_y *= -1
            self.audio.channel_1.play(self.audio.plob_sound)
        if self.puck.left <= 0 or self.puck.right >= SCREEN_WIDTH:
            self.puck_speed_x *= -1
            self.audio.channel_1.play(self.audio.plob_sound)
            

        # Puck movement when hit by player.
        if self.puck.colliderect(self.player):
            """
            Calculate relative hit position (how far from the paddle's center), relative to the paddle's width.
            Take the difference between the puck's center and the paddle's center on the X and Y axes.
            Divide by half the width of the paddle, representing the distance from the paddle's center to its edge.
            0 means the puck hit the center of the paddle, -1 means the left edge, and 1 means the right edge.
            Store in a variable (relative) that determines the proportion of the puck's speed in the x and y direction based on where it hit the paddle.
            """
            relative_x = (self.puck.centerx - self.player.centerx) / (self.player.width / 2)
            relative_y = (self.puck.centery - self.player.centery) / (self.player.height / 2)

            """
            Use relative position to adjust puck's direction
            The puck's speed and direction are influenced by the collision position.
            Hitting the paddle closer to the edges will cause more diagonal movement, while hitting the center results in a straighter trajectory.
            """
            self.puck_speed_x = relative_x * INITIAL_PUCK_SPEED  # X speed proportional to hit position
            self.puck_speed_y = relative_y * INITIAL_PUCK_SPEED  # Y speed proportional to hit position

            # Add paddle's velocity influence
            self.puck_speed_x += self.player_velocity[0] * 0.5
            self.puck_speed_y += self.player_velocity[1] * 0.5
            self.increase_speed()
            self.audio.channel_1.play(self.audio.plob_sound)
            
        # Handling collisions with opponent
        if self.puck.colliderect(self.opponent) and self.collision_cooldown == 0:
            self.puck_speed_x *= -1
            self.puck_speed_y *= -1
            self.increase_speed()
            self.collision_cooldown = 30  # Frames before another collision is detected
            self.audio.channel_1.play(self.audio.plob_sound)

        # Apply friction
        self.puck_speed_x *= 0.995 # Is this the magic number?
        self.puck_speed_y *= 0.995
    
    def increase_speed(self):
        """Increase the puck speed when hit."""
        self.puck_speed_x *= 1.5
        self.puck_speed_y *= 1.5
        self.apply_speed_limit()
    
    def apply_speed_limit(self):
        """
        Ensure the puck does not exceed the speed limit.
        Calculates the puck's current speed using the Pythagorean theorem.
        The speed is the magnitude of the velocity vector.
        Scaling reduces the magnitude of the velocity vector to SPEED_LIMIT while preserving its direction.
        The ratio between the horizontal and vertical components remains unchanged, ensuring realistic motion.
        """
        speed = (self.puck_speed_x ** 2 + self.puck_speed_y ** 2) ** 0.5
        if speed > SPEED_LIMIT:
            # A scaling factor is calculated as the ratio SPEED_LIMIT to the current speed.
            scale = SPEED_LIMIT / speed
            self.puck_speed_x *= scale
            self.puck_speed_y *= scale
    
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
            self.start_countdown()
            self.audio.channel_2.play(self.audio.score_sound)
        elif self.puck.colliderect(self.opponent_goal):
            self.player_score += 1
            self.start_countdown()
            self.audio.channel_2.play(self.audio.score_sound)

    def start_countdown(self):
        """Countdown between rounds."""
        self.countdown = 3
        pygame.time.set_timer(self.COUNTDOWN_EVENT, self.COUNTDOWN_INTERVAL) # Start the timer with a 1 second interval


    def display_scores(self):
        """Display the scores on the screen."""
        player_score_text = self.score_font.render(f"Player: {self.player_score}", True, BLACK) # looks better with anti-aliasing?
        opponent_score_text = self.score_font.render(f"Opponent: {self.opponent_score}", True, BLACK)
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.is_spiking = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.is_spiking = False
                if event.type == self.COUNTDOWN_EVENT and self.countdown > 0:
                    self.countdown -= 1
                    if self.countdown == 0:
                        pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)  # Stop the timer
                        self.reset_puck()

            # Countdown logic
            if self.countdown > 0:
                # Still draw everything except the puck and the player/opponent
                self.screen.fill(WHITE)
                self.draw_dotted_line()
                pygame.draw.rect(self.screen, BLUE, self.player_goal)
                pygame.draw.rect(self.screen, BLUE, self.opponent_goal)
                self.display_scores()
                
                # Display countdown text
                countdown_text = self.countdown_font.render(str(self.countdown), True, BLACK)
                text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                self.screen.blit(countdown_text, text_rect)
                pygame.display.flip()
                self.clock.tick(FRAMERATE)
                continue

            # Get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Update player position to follow the mouse
            self.player.centerx = mouse_x
            self.player.centery = mouse_y

            # Move the player up if spiking
            if self.is_spiking:
                self.player.y -= self.spike_speed

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
            if self.opponent.bottom >= SCREEN_HEIGHT / 4:
                self.opponent.bottom = SCREEN_HEIGHT / 4
            if self.opponent.left <= 0:
                self.opponent.left = 0
            if self.opponent.right >= SCREEN_WIDTH:
                self.opponent.right = SCREEN_WIDTH

            # Cooldown for collisions
            if self.collision_cooldown > 0:
                self.collision_cooldown -= 1

            # Calculate player velocity
            self.player_velocity = [
                self.player.centerx - self.prev_player_pos[0],
                self.player.centery - self.prev_player_pos[1],
            ]
            self.prev_player_pos = self.player.center

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
            pygame.draw.ellipse(self.screen, BLACK, self.puck)
            self.display_scores()
            
            #Music
            if not self.audio.channel_0.get_busy(): # without this it sounds like static
                self.audio.channel_0.play(self.audio.bg_music)

            pygame.display.flip()
            self.clock.tick(FRAMERATE)
            
if __name__ == '__main__':
    game_manager = Game()
    game_manager.run()