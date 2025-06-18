import pygame
import sys
import time
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wild West Duel")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)

# Load fonts
font_large = pygame.font.SysFont('Arial', 120)  # Increased from 72
font_medium = pygame.font.SysFont('Arial', 48)  # Increased from 36
font_small = pygame.font.SysFont('Arial', 36)   # Increased from 24

# Physics constants
GRAVITY = 0.3  # Reduced gravity to account for longer distances
BASE_GROUND_LEVEL = HEIGHT - 200  # Base ground level for higher resolution

# Terrain generation parameters
MAX_HILL_HEIGHT = 250  # Maximum height of hills
MIN_HILL_HEIGHT = 30   # Minimum height of hills
HILL_WIDTH_RANGE = (100, 300)  # Range of hill widths
CENTER_GAP = 600  # Gap in the center to ensure line of sight

# Terrain class to handle the ground and hills
class Terrain:
    def __init__(self):
        self.ground_level = BASE_GROUND_LEVEL
        self.hills = []  # List of hills [(x, y, width, height), ...]
        self.generate_terrain()
        
    def generate_terrain(self):
        self.hills = []
        
        # Generate left hill (player side) - ensure player is on a hill
        left_hill_height = random.randint(MIN_HILL_HEIGHT, MAX_HILL_HEIGHT)
        left_hill_width = random.randint(*HILL_WIDTH_RANGE)
        # Position the hill so the player is centered on it
        player_x = 50
        left_hill_x = max(0, player_x - left_hill_width // 2)
        self.hills.append((left_hill_x, BASE_GROUND_LEVEL - left_hill_height, left_hill_width, left_hill_height))
        
        # Generate right hill (NPC side) - ensure NPC is on a hill
        right_hill_height = random.randint(MIN_HILL_HEIGHT, MAX_HILL_HEIGHT)
        right_hill_width = random.randint(*HILL_WIDTH_RANGE)
        # Position the hill so the NPC is centered on it
        npc_x = WIDTH - 110
        right_hill_x = max(0, npc_x - right_hill_width // 2)
        self.hills.append((right_hill_x, BASE_GROUND_LEVEL - right_hill_height, right_hill_width, right_hill_height))
        
        # Randomly decide if we add a middle hill (with lower height to not block view)
        if random.random() < 0.3:  # 30% chance
            middle_hill_height = random.randint(MIN_HILL_HEIGHT, MIN_HILL_HEIGHT + 20)
            middle_hill_width = random.randint(100, 200)
            middle_hill_x = WIDTH // 2 - middle_hill_width // 2
            self.hills.append((middle_hill_x, BASE_GROUND_LEVEL - middle_hill_height, middle_hill_width, middle_hill_height))
    
    def draw(self, screen):
        # Draw base ground
        pygame.draw.rect(screen, BROWN, (0, BASE_GROUND_LEVEL, WIDTH, HEIGHT - BASE_GROUND_LEVEL))
        
        # Draw hills
        for x, y, width, height in self.hills:
            # Draw hill with a slightly darker color
            hill_color = (139, 69, 19)  # Darker brown
            pygame.draw.rect(screen, hill_color, (x, y, width, height))
            
            # Draw grass on top of the hill
            grass_color = (34, 139, 34)  # Forest green
            pygame.draw.rect(screen, grass_color, (x, y, width, 10))
    
    def get_ground_level_at(self, x):
        # Return the ground level at position x
        for hill_x, hill_y, hill_width, hill_height in self.hills:
            if hill_x <= x < hill_x + hill_width:
                return hill_y
        return BASE_GROUND_LEVEL

class Bullet:
    def __init__(self, x, y, angle, speed, is_player):
        self.x = x
        self.y = y
        self.angle = angle  # in degrees
        self.speed = speed
        self.is_player = is_player
        self.active = True
        self.radius = 2  # Larger bullet for higher resolution
        self.trail = []  # Store positions for bullet trail
        self.max_trail_length = 20  # Longer trail for better visibility at distance
        
        # Convert angle to radians and calculate velocity components
        angle_rad = math.radians(angle)
        # No need for direction multiplier since we're already using the correct angle for each character
        self.vx = math.cos(angle_rad) * speed * (1 if is_player else -1)
        self.vy = -math.sin(angle_rad) * speed  # Negative because y increases downward
        
    def update(self, terrain):
        if not self.active:
            return
            
        # Store current position for trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy
        
        # Apply gravity to vertical velocity
        self.vy += GRAVITY
        
        # Check if bullet hit ground or terrain
        ground_level_at_bullet = terrain.get_ground_level_at(self.x)
        if self.y > ground_level_at_bullet:
            self.y = ground_level_at_bullet
            self.active = False
            
        # Check if bullet is out of bounds
        if self.x < 0 or self.x > WIDTH:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw bullet trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            # Make trail fade out
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (100, 100, 100, alpha)
            trail_radius = int(self.radius * (i / len(self.trail)))
            if trail_radius < 1:
                trail_radius = 1
            pygame.draw.circle(screen, DARK_GRAY, (int(trail_x), int(trail_y)), trail_radius)
            
        # Draw bullet
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        
    def check_hit(self, player):
        if not self.active:
            return False
            
        # Check if bullet is in the vertical range of the player
        if (self.y > player.y - 10 - 12 and  # Head top (with radius)
            self.y < player.y + player.height):  # Body bottom
            
            # Check horizontal position
            if self.is_player:  # Player bullet
                if self.x > player.x - 12:  # Account for head radius
                    self.active = False
                    # Calculate damage based on hit location
                    if self.y < player.y:  # Headshot
                        damage = 40
                    else:  # Body shot
                        damage = 20
                    player.health -= damage
                    player.health = max(0, player.health)  # Ensure health doesn't go below 0
                    return True
            else:  # NPC bullet
                if self.x < player.x + player.width + 12:  # Account for head radius
                    self.active = False
                    # Calculate damage based on hit location
                    if self.y < player.y:  # Headshot
                        damage = 40
                    else:  # Body shot
                        damage = 20
                    player.health -= damage
                    player.health = max(0, player.health)  # Ensure health doesn't go below 0
                    return True
        return False

class Player:
    # Class variable to store terrain reference
    terrain = None
    
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.width = 30  # Reduced from 60 (half size)
        self.height = 60  # Reduced from 120 (half size)
        self.color = color
        self.has_shot = False
        self.shot_time = 0
        self.bullet = None
        self.health = 100  # Starting health
        self.max_health = 100  # Maximum health
        self.is_player = is_player
        self.aim_y = y + 10  # Adjusted for upper body position (reduced)
        self.aim_direction = 1 if is_player else -1  # 1 for right, -1 for left
        self.aim_angle = 0  # Angle in degrees (0 is horizontal)
        self.bullet_velocity = 45  # Increased for larger screen
        
        # Arm and pistol properties - keeping these unchanged
        self.arm_length = 35  # Keeping arm length unchanged
        self.arm_width = 8  # Keeping arm width unchanged
        self.pistol_length = 10  # Keeping pistol length unchanged
        self.current_arm_angle = -70  # Start downward (-45 degrees), no direction multiplier
        self.target_arm_angle = self.aim_angle  # Target angle for animation
        self.arm_animation_speed = 3  # Increased speed for quicker draw
        
        # Reticle properties
        self.reticle_x = 0
        self.reticle_y = 0
        self.update_reticle_position()  # Initialize reticle position
        
    def draw(self, screen, aiming=False):
        # Draw body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw head
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y - 10), 12)  # Reduced from 24 to 12 (half size)
        
        # Calculate arm position - moved higher up on the body
        arm_start_x = self.x + self.width // 2
        arm_start_y = self.y + 10  # Upper part of body
        
        # Calculate arm end point based on current arm angle
        # For NPC, we need to flip the angle calculation to make it face the player
        if self.is_player:
            arm_angle_rad = math.radians(self.current_arm_angle)
            arm_end_x = arm_start_x + (self.arm_length * math.cos(arm_angle_rad))
        else:
            arm_angle_rad = math.radians(180 - self.current_arm_angle)  # Flip angle for NPC
            arm_end_x = arm_start_x + (self.arm_length * math.cos(arm_angle_rad))
            
        arm_end_y = arm_start_y - (self.arm_length * math.sin(arm_angle_rad))
        
        # Draw arm with black outline
        # First draw a slightly thicker black line for the outline
        pygame.draw.line(screen, BLACK, (arm_start_x, arm_start_y), 
                        (arm_end_x, arm_end_y), self.arm_width + 2)
        # Then draw the colored arm on top
        pygame.draw.line(screen, self.color, (arm_start_x, arm_start_y), 
                        (arm_end_x, arm_end_y), self.arm_width)
        
        # Calculate pistol position at the end of arm
        # Use the same angle calculation as for the arm
        if self.is_player:
            pistol_end_x = arm_end_x + (self.pistol_length * math.cos(arm_angle_rad))
        else:
            pistol_end_x = arm_end_x + (self.pistol_length * math.cos(arm_angle_rad))
            
        pistol_end_y = arm_end_y - (self.pistol_length * math.sin(arm_angle_rad))
        
        # Draw pistol
        pygame.draw.line(screen, BLACK, (arm_end_x, arm_end_y), 
                        (pistol_end_x, pistol_end_y), 6)  # Keeping pistol thickness
        
        # Draw reticle if in aiming phase and is player
        if aiming and self.is_player:
            # Draw reticle
            reticle_size = 15  # Keeping reticle size
            # Outer circle
            pygame.draw.circle(screen, RED, (int(self.reticle_x), int(self.reticle_y)), reticle_size, 2)
            # Inner circle
            pygame.draw.circle(screen, RED, (int(self.reticle_x), int(self.reticle_y)), reticle_size // 2, 2)
            # Crosshairs
            pygame.draw.line(screen, RED, (self.reticle_x - reticle_size, self.reticle_y), 
                            (self.reticle_x + reticle_size, self.reticle_y), 2)
            pygame.draw.line(screen, RED, (self.reticle_x, self.reticle_y - reticle_size), 
                            (self.reticle_x, self.reticle_y + reticle_size), 2)
            
            # Draw angle text
            angle_text = font_small.render(f"Angle: {self.aim_angle:.2f}°", True, BLACK)
            screen.blit(angle_text, (self.x, self.y - 50))  # Adjusted position for smaller body
            
    def update_arm_animation(self):
        # Animate the arm to move toward the target angle
        if self.current_arm_angle != self.aim_angle:
            # Calculate the difference
            angle_diff = self.aim_angle - self.current_arm_angle
            
            # Determine the direction and amount to move
            if abs(angle_diff) < self.arm_animation_speed:
                # If we're close enough, just set to the target
                self.current_arm_angle = self.aim_angle
            else:
                # Otherwise move in the right direction
                direction = 1 if angle_diff > 0 else -1
                self.current_arm_angle += direction * self.arm_animation_speed
    def adjust_aim_angle(self, direction):
        # Adjust aim angle (up/down) with finer control (0.10 degrees per adjustment)
        self.aim_angle += direction * 0.10
        # Limit angle to reasonable range (0-60 degrees)
        self.aim_angle = max(0, min(self.aim_angle, 60))
        
        # Update aim_y based on angle for compatibility - adjusted for upper body position
        self.aim_y = self.y + 10 - (self.aim_angle * 0.8)
        
        # Update target arm angle for animation
        self.target_arm_angle = self.aim_angle
        
        # Calculate reticle position for visual feedback
        self.update_reticle_position()
        
    def adjust_aim_power(self, direction):
        # Adjust aim power (stronger/weaker)
        self.aim_power += direction
        # Limit power to reasonable range
        self.aim_power = max(self.min_power, min(self.aim_power, self.max_power))
        
        # Update reticle position for visual feedback
        self.update_reticle_position()
        
    def update_reticle_position(self, terrain=None):
        # Use class terrain if none provided
        if terrain is None:
            terrain = Player.terrain
            
        # Calculate reticle position based on current angle and fixed velocity
        angle_rad = math.radians(self.aim_angle)
        distance_multiplier = 2.5  # Reduced from 5 to make reticle twice as close
        
        # Calculate gun position
        gun_x = self.x + self.width if self.is_player else self.x
        gun_y = self.aim_y
        
        # Calculate gun end point
        gun_length = 20
        gun_end_x = gun_x + (gun_length * math.cos(angle_rad) * self.aim_direction)
        gun_end_y = gun_y - (gun_length * math.sin(angle_rad))
        
        # Calculate reticle position using fixed bullet velocity
        self.reticle_x = gun_end_x + (math.cos(angle_rad) * self.bullet_velocity * distance_multiplier * self.aim_direction)
        self.reticle_y = gun_end_y - (math.sin(angle_rad) * self.bullet_velocity * distance_multiplier)
        
        # Ensure reticle stays within screen bounds
        self.reticle_x = max(0, min(self.reticle_x, WIDTH))
        
        # If terrain is provided, ensure reticle doesn't go below ground
        if terrain:
            ground_level_at_reticle = terrain.get_ground_level_at(self.reticle_x)
            self.reticle_y = min(self.reticle_y, ground_level_at_reticle - 10)  # Keep slightly above ground
        else:
            self.reticle_y = max(0, min(self.reticle_y, BASE_GROUND_LEVEL))
    def shoot(self):
        if not self.has_shot:
            self.has_shot = True
            self.shot_time = pygame.time.get_ticks()
            
            # Calculate pistol position at the end of arm - using upper body position
            arm_start_x = self.x + self.width // 2
            arm_start_y = self.y + 20  # Upper part of body
            
            # Calculate arm and pistol positions with correct angles for both player and NPC
            if self.is_player:
                arm_angle_rad = math.radians(self.current_arm_angle)
                arm_end_x = arm_start_x + (self.arm_length * math.cos(arm_angle_rad))
                bullet_angle = self.current_arm_angle
            else:
                arm_angle_rad = math.radians(180 - self.current_arm_angle)  # Flip angle for NPC
                arm_end_x = arm_start_x + (self.arm_length * math.cos(arm_angle_rad))
                bullet_angle = self.current_arm_angle  # Use original angle for NPC bullet
                
            arm_end_y = arm_start_y - (self.arm_length * math.sin(arm_angle_rad))
            
            pistol_end_x = arm_end_x + (self.pistol_length * math.cos(arm_angle_rad))
            pistol_end_y = arm_end_y - (self.pistol_length * math.sin(arm_angle_rad))
            
            # Create bullet - using fixed velocity and correct angle
            self.bullet = Bullet(pistol_end_x, pistol_end_y, 
                                bullet_angle, self.bullet_velocity, self.is_player)
                
    def update_bullet(self, terrain):
        if self.bullet and self.bullet.active:
            self.bullet.update(terrain)
            
    def draw_bullet(self, screen):
        if self.bullet:
            self.bullet.draw(screen)
            
    def check_hit(self, other):
        if self.bullet and self.bullet.active:
            return self.bullet.check_hit(other)
        return False

def draw_scene(player, npc, terrain, game_state, mode="simultaneous", countdown=None, winner=None, hit_message=None):
    # Draw sky
    screen.fill(SKY_BLUE)
    
    # Draw terrain (ground and hills)
    terrain.draw(screen)
    
    # Draw players - show aiming line for player during aiming phase
    player.draw(screen, game_state == "aiming")
    npc.draw(screen, False)  # NPC never shows trajectory prediction
    
    # Draw bullets
    player.draw_bullet(screen)
    npc.draw_bullet(screen)
    
    # Draw health bars - scaled for higher resolution
    # Player health bar
    pygame.draw.rect(screen, RED, (100, 40, 400, 30))
    health_width = int(400 * (player.health / player.max_health))
    pygame.draw.rect(screen, GREEN, (100, 40, health_width, 30))
    
    # NPC health bar
    pygame.draw.rect(screen, RED, (WIDTH - 500, 40, 400, 30))
    health_width = int(400 * (npc.health / npc.max_health))
    pygame.draw.rect(screen, GREEN, (WIDTH - 500, 40, health_width, 30))
    
    # Draw health numbers
    player_health_text = font_small.render(f"{player.health}/{player.max_health}", True, BLACK)
    npc_health_text = font_small.render(f"{npc.health}/{npc.max_health}", True, BLACK)
    screen.blit(player_health_text, (100, 80))
    screen.blit(npc_health_text, (WIDTH - 500, 80))
    
    # Draw round indicator
    if game_state != "game_over":
        round_text = font_medium.render("Prepare to Duel!", True, BLACK)
        screen.blit(round_text, (WIDTH // 2 - 100, 40))
    
    # Draw hit message if available
    if hit_message:
        hit_text = font_medium.render(hit_message, True, RED)
        screen.blit(hit_text, (WIDTH // 2 - 200, 100))
    
    # Draw game state specific information
    if game_state == "aiming":
        instructions = font_medium.render("UP/DOWN: Adjust Angle, SPACE: Ready", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - 200, 160))
    elif game_state == "countdown" and countdown is not None:
        countdown_text = font_large.render(str(countdown), True, RED)
        screen.blit(countdown_text, (WIDTH // 2 - 40, HEIGHT // 2 - 100))
    elif game_state == "game_over" and winner is not None:
        winner_text = font_medium.render(f"{winner} wins!", True, BLACK)
        screen.blit(winner_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        restart_text = font_small.render("Press R to restart or Q to quit", True, BLACK)
        screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 20))

def main():
    clock = pygame.time.Clock()
    
    # Define player and NPC positions
    player_x = 50
    npc_x = WIDTH - 110
    
    # Create terrain
    terrain = Terrain()
    
    # Set the terrain in the Player class
    Player.terrain = terrain
    
    # Get ground levels for player and NPC positions
    player_ground_level = terrain.get_ground_level_at(player_x + 30)  # Center of player (half width)
    npc_ground_level = terrain.get_ground_level_at(npc_x + 30)  # Center of NPC (half width)
    
    # Create player and NPC with positions based on terrain
    player = Player(player_x, player_ground_level - 60, BLUE, is_player=True)  # Height is 60 now
    npc = Player(npc_x, npc_ground_level - 60, RED)
    
    # Game states: "aiming" -> "countdown" -> "shooting" -> "result" -> back to "aiming" or "game_over"
    game_state = "aiming"
    countdown_start = 0
    countdown_value = 3
    winner = None
    hit_message = None
    
    # Key state tracking for continuous adjustments
    keys_pressed = {
        pygame.K_UP: False,
        pygame.K_DOWN: False
    }
    
    # Key repeat settings
    key_repeat_delay = 100  # ms before starting to repeat
    key_repeat_interval = 30  # ms between repeats
    last_key_action_time = 0
    
    # NPC variables
    npc_aim_angle_change = 0
    npc_last_aim_time = 0
    npc_aim_interval = 300  # Time between NPC aim adjustments (ms)
    
    # Randomize initial NPC aim
    npc.aim_angle = random.randint(5, 15)
    
    # Reset function for next round
    def reset_for_next_round():
        nonlocal game_state, hit_message, countdown_value
        # Reset bullets
        player.bullet = None
        npc.bullet = None
        player.has_shot = False
        npc.has_shot = False
        
        # Define player and NPC positions - keep the same positions
        player_x = 50
        npc_x = WIDTH - 110
        
        # Keep the same terrain between rounds
        # Just reset player positions to their original spots
        player_ground_level = terrain.get_ground_level_at(player_x + 30)
        npc_ground_level = terrain.get_ground_level_at(npc_x + 30)
        
        # Update player positions
        player.x = player_x
        player.y = player_ground_level - 60
        npc.x = npc_x
        npc.y = npc_ground_level - 60
        
        # Reset arm positions to downward position
        player.current_arm_angle = -45  # No direction multiplier
        npc.current_arm_angle = -45  # No direction multiplier
        
        # Reset game state
        game_state = "aiming"
        hit_message = None
        countdown_value = 3
        
        # Randomize NPC aim for next round
        npc.aim_angle = random.randint(5, 30)
        
        # Reset NPC aim behavior
        nonlocal npc_aim_angle_change, npc_last_aim_time
        npc_aim_angle_change = random.choice([-1, 0, 1])
        npc_last_aim_time = pygame.time.get_ticks()
    
    # Initialize NPC aim behavior
    npc_aim_angle_change = random.choice([-1, 0, 1])
    npc_last_aim_time = pygame.time.get_ticks()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                # Track key press state for continuous adjustments
                if event.key in keys_pressed:
                    keys_pressed[event.key] = True
                    last_key_action_time = current_time - key_repeat_delay  # Allow immediate action
                
                # Player controls during aiming - immediate response
                if game_state == "aiming":
                    if event.key == pygame.K_UP:
                        player.adjust_aim_angle(1)  # Increase angle
                    elif event.key == pygame.K_DOWN:
                        player.adjust_aim_angle(-1)  # Decrease angle
                    elif event.key == pygame.K_SPACE:
                        # Start countdown when player is ready
                        game_state = "countdown"
                        countdown_start = pygame.time.get_ticks()
                
                # Game over controls
                if game_state == "game_over":
                    if event.key == pygame.K_r:
                        # Reset game completely
                        # Define player and NPC positions
                        player_x = 50
                        npc_x = WIDTH - 110
                        
                        # Generate new terrain
                        terrain = Terrain()
                        
                        # Update the terrain in the Player class
                        Player.terrain = terrain
                        
                        # Get new ground levels
                        player_ground_level = terrain.get_ground_level_at(player_x + 30)
                        npc_ground_level = terrain.get_ground_level_at(npc_x + 30)
                        
                        # Create new players at the correct heights
                        player = Player(player_x, player_ground_level - 60, BLUE, is_player=True)
                        npc = Player(npc_x, npc_ground_level - 60, RED)
                        npc.aim_angle = random.randint(5, 30)
                        game_state = "aiming"
                        winner = None
                        hit_message = None
                        countdown_value = 3
                        
                        # Reset NPC aim behavior
                        npc_aim_angle_change = random.choice([-1, 0, 1])
                        npc_last_aim_time = pygame.time.get_ticks()
                        
                        # Make sure arms start in downward position
                        player.current_arm_angle = -45  # No direction multiplier
                        npc.current_arm_angle = -45  # No direction multiplier
                    elif event.key == pygame.K_q:
                        running = False
            
            elif event.type == pygame.KEYUP:
                # Track key release
                if event.key in keys_pressed:
                    keys_pressed[event.key] = False
        
        # Handle continuous key presses for aiming adjustments
        if game_state == "aiming" and current_time - last_key_action_time > key_repeat_interval:
            if keys_pressed[pygame.K_UP]:
                player.adjust_aim_angle(1)
                last_key_action_time = current_time
            elif keys_pressed[pygame.K_DOWN]:
                player.adjust_aim_angle(-1)
                last_key_action_time = current_time
        
        # Update game state based on current state
        if game_state == "aiming":
            # NPC randomly adjusts aim periodically
            if current_time - npc_last_aim_time > npc_aim_interval:
                # Randomly change aim direction occasionally
                if random.random() < 0.3:
                    npc_aim_angle_change = random.choice([-1, 0, 1])
                
                # Apply the changes
                if npc_aim_angle_change != 0:
                    npc.adjust_aim_angle(npc_aim_angle_change)
                
                npc_last_aim_time = current_time
        
        elif game_state == "countdown":
            elapsed = current_time - countdown_start
            
            # Animate arms to move toward target angle during countdown
            player.target_arm_angle = player.aim_angle
            npc.target_arm_angle = npc.aim_angle
            
            # Update arm animations
            player.update_arm_animation()
            npc.update_arm_animation()
            
            if elapsed < 1000:
                countdown_value = 3
            elif elapsed < 2000:
                countdown_value = 2
            elif elapsed < 3000:
                countdown_value = 1
            else:
                # Both shoot simultaneously after countdown
                player.shoot()
                npc.shoot()
                game_state = "shooting"
                countdown_value = "FIRE!"
        
        elif game_state == "shooting":
            # Update both bullets
            player.update_bullet(terrain)
            npc.update_bullet(terrain)
            
            # Track hits
            player_hit_npc = False
            npc_hit_player = False
            
            # Check for player hitting NPC
            if player.bullet and player.bullet.active:
                if player.check_hit(npc):
                    player_hit_npc = True
                    damage = 40 if player.bullet.y < npc.y else 20
                    hit_message = f"Player hit NPC for {damage} damage!"
            
            # Check for NPC hitting player
            if npc.bullet and npc.bullet.active:
                if npc.check_hit(player):
                    npc_hit_player = True
                    damage = 40 if npc.bullet.y < player.y else 20
                    if hit_message:
                        hit_message += f" NPC hit Player for {damage} damage!"
                    else:
                        hit_message = f"NPC hit Player for {damage} damage!"
            
            # Check if both bullets are no longer active
            bullets_done = ((not player.bullet or not player.bullet.active) and 
                           (not npc.bullet or not npc.bullet.active))
            
            if bullets_done:
                if not player_hit_npc and not npc_hit_player:
                    hit_message = "Both missed!"
                game_state = "result"
                # Store the time when we entered result state
                main.result_start_time = current_time
        
        elif game_state == "result":
            # Check if anyone has died
            if player.health <= 0 and npc.health <= 0:
                winner = "Draw - Both died!"
                game_state = "game_over"
            elif player.health <= 0:
                winner = "NPC"
                game_state = "game_over"
            elif npc.health <= 0:
                winner = "Player"
                game_state = "game_over"
            else:
                # Wait a moment before next round
                if not hasattr(main, "result_start_time"):
                    main.result_start_time = current_time
                
                # After 2 seconds, move to next round
                if current_time - main.result_start_time > 2000:
                    delattr(main, "result_start_time")
                    reset_for_next_round()
        
        # Draw everything
        draw_scene(player, npc, terrain, game_state, "simultaneous", countdown_value, winner, hit_message)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
