import pygame
import sys
import time
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
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
font_large = pygame.font.SysFont('Arial', 72)
font_medium = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)

# Physics constants
GRAVITY = 0.3  # Reduced gravity to account for longer distances
GROUND_LEVEL = HEIGHT - 100

class Bullet:
    def __init__(self, x, y, angle, speed, is_player):
        self.x = x
        self.y = y
        self.angle = angle  # in degrees
        self.speed = speed
        self.is_player = is_player
        self.active = True
        self.radius = 3  # Smaller bullet
        self.trail = []  # Store positions for bullet trail
        self.max_trail_length = 15  # Longer trail for better visibility at distance
        
        # Convert angle to radians and calculate velocity components
        angle_rad = math.radians(angle)
        direction = 1 if is_player else -1
        self.vx = math.cos(angle_rad) * speed * direction
        self.vy = -math.sin(angle_rad) * speed  # Negative because y increases downward
        
    def update(self):
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
        
        # Check if bullet hit ground
        if self.y > GROUND_LEVEL:
            self.y = GROUND_LEVEL
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
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.width = 30  # Reduced from 50
        self.height = 60  # Reduced from 100
        self.color = color
        self.has_shot = False
        self.shot_time = 0
        self.bullet = None
        self.health = 100  # Starting health
        self.max_health = 100  # Maximum health
        self.is_player = is_player
        self.aim_y = y + 25  # Adjusted for smaller height
        self.aim_direction = 1 if is_player else -1  # 1 for right, -1 for left
        self.aim_angle = 0  # Angle in degrees (0 is horizontal)
        self.aim_power = 35  # Increased initial bullet speed for longer distance
        self.min_power = 20  # Increased minimum power
        self.max_power = 50  # Increased maximum power
        
        # Reticle properties
        self.reticle_x = 0
        self.reticle_y = 0
        self.update_reticle_position()  # Initialize reticle position
        
    def draw(self, screen, aiming=False):
        # Draw body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw head
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y - 10), 12)  # Smaller head
        
        # Calculate gun position
        gun_x = self.x + self.width if self.is_player else self.x
        gun_y = self.aim_y
        
        # Calculate gun end point based on angle
        angle_rad = math.radians(self.aim_angle)
        gun_length = 20  # Shorter gun
        direction = self.aim_direction
        gun_end_x = gun_x + (gun_length * math.cos(angle_rad) * direction)
        gun_end_y = gun_y - (gun_length * math.sin(angle_rad))
        
        # Draw gun
        pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_end_x, gun_end_y), 3)  # Thinner gun
        
        # Draw reticle if in aiming phase and is player
        if aiming and self.is_player:
            # Draw reticle
            reticle_size = 10
            # Outer circle
            pygame.draw.circle(screen, RED, (int(self.reticle_x), int(self.reticle_y)), reticle_size, 1)
            # Inner circle
            pygame.draw.circle(screen, RED, (int(self.reticle_x), int(self.reticle_y)), reticle_size // 2, 1)
            # Crosshairs
            pygame.draw.line(screen, RED, (self.reticle_x - reticle_size, self.reticle_y), 
                            (self.reticle_x + reticle_size, self.reticle_y), 1)
            pygame.draw.line(screen, RED, (self.reticle_x, self.reticle_y - reticle_size), 
                            (self.reticle_x, self.reticle_y + reticle_size), 1)
            
            # Draw power meter
            power_percentage = (self.aim_power - self.min_power) / (self.max_power - self.min_power)
            meter_width = 100
            meter_height = 10
            meter_x = self.x
            meter_y = self.y - 50
            
            # Draw background
            pygame.draw.rect(screen, WHITE, (meter_x, meter_y, meter_width, meter_height))
            # Draw filled portion
            pygame.draw.rect(screen, RED, (meter_x, meter_y, int(meter_width * power_percentage), meter_height))
            # Draw border
            pygame.draw.rect(screen, BLACK, (meter_x, meter_y, meter_width, meter_height), 1)
            
            # Draw angle and power text
            angle_text = font_small.render(f"Angle: {self.aim_angle}°", True, BLACK)
            power_text = font_small.render(f"Power: {self.aim_power}", True, BLACK)
            screen.blit(angle_text, (self.x, self.y - 80))
            screen.blit(power_text, (self.x, self.y - 60))
            
    def adjust_aim_angle(self, direction):
        # Adjust aim angle (up/down) with finer control (0.10 degrees per adjustment)
        self.aim_angle += direction * 0.10
        # Limit angle to reasonable range (0-60 degrees)
        self.aim_angle = max(0, min(self.aim_angle, 60))
        
        # Update aim_y based on angle for compatibility
        self.aim_y = self.y + 25 - (self.aim_angle * 0.8)  # Adjusted for smaller height
        
        # Calculate reticle position for visual feedback
        self.update_reticle_position()
        
    def adjust_aim_power(self, direction):
        # Adjust aim power (stronger/weaker)
        self.aim_power += direction
        # Limit power to reasonable range
        self.aim_power = max(self.min_power, min(self.aim_power, self.max_power))
        
        # Update reticle position for visual feedback
        self.update_reticle_position()
        
    def update_reticle_position(self):
        # Calculate reticle position based on current angle and power
        angle_rad = math.radians(self.aim_angle)
        distance_multiplier = 2.5  # Reduced from 5 to make reticle twice as close
        
        # Calculate gun position
        gun_x = self.x + self.width if self.is_player else self.x
        gun_y = self.aim_y
        
        # Calculate gun end point
        gun_length = 20
        gun_end_x = gun_x + (gun_length * math.cos(angle_rad) * self.aim_direction)
        gun_end_y = gun_y - (gun_length * math.sin(angle_rad))
        
        # Calculate reticle position
        self.reticle_x = gun_end_x + (math.cos(angle_rad) * self.aim_power * distance_multiplier * self.aim_direction)
        self.reticle_y = gun_end_y - (math.sin(angle_rad) * self.aim_power * distance_multiplier)
        
        # Ensure reticle stays within screen bounds
        self.reticle_x = max(0, min(self.reticle_x, WIDTH))
        self.reticle_y = max(0, min(self.reticle_y, GROUND_LEVEL))
            
    def shoot(self):
        if not self.has_shot:
            self.has_shot = True
            self.shot_time = pygame.time.get_ticks()
            
            # Calculate gun position
            gun_x = self.x + self.width if self.is_player else self.x
            gun_y = self.aim_y
            
            # Calculate gun end point based on angle
            angle_rad = math.radians(self.aim_angle)
            gun_length = 20  # Shorter gun
            gun_end_x = gun_x + (gun_length * math.cos(angle_rad) * self.aim_direction)
            gun_end_y = gun_y - (gun_length * math.sin(angle_rad))
            
            # Create bullet - using the same angle and power that positions the reticle
            self.bullet = Bullet(gun_end_x, gun_end_y, self.aim_angle, self.aim_power, self.is_player)
                
    def update_bullet(self):
        if self.bullet and self.bullet.active:
            self.bullet.update()
            
    def draw_bullet(self, screen):
        if self.bullet:
            self.bullet.draw(screen)
            
    def check_hit(self, other):
        if self.bullet and self.bullet.active:
            return self.bullet.check_hit(other)
        return False

def draw_scene(player, npc, game_state, mode="simultaneous", countdown=None, winner=None, hit_message=None):
    # Draw sky
    screen.fill(SKY_BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, BROWN, (0, GROUND_LEVEL, WIDTH, HEIGHT - GROUND_LEVEL))
    
    # Draw players - show aiming line for player during aiming phase
    player.draw(screen, game_state == "aiming")
    npc.draw(screen, False)  # NPC never shows trajectory prediction
    
    # Draw bullets
    player.draw_bullet(screen)
    npc.draw_bullet(screen)
    
    # Draw health bars
    # Player health bar
    pygame.draw.rect(screen, RED, (50, 20, 200, 20))
    health_width = int(200 * (player.health / player.max_health))
    pygame.draw.rect(screen, GREEN, (50, 20, health_width, 20))
    
    # NPC health bar
    pygame.draw.rect(screen, RED, (WIDTH - 250, 20, 200, 20))
    health_width = int(200 * (npc.health / npc.max_health))
    pygame.draw.rect(screen, GREEN, (WIDTH - 250, 20, health_width, 20))
    
    # Draw health numbers
    player_health_text = font_small.render(f"{player.health}/{player.max_health}", True, BLACK)
    npc_health_text = font_small.render(f"{npc.health}/{npc.max_health}", True, BLACK)
    screen.blit(player_health_text, (50, 45))
    screen.blit(npc_health_text, (WIDTH - 250, 45))
    
    # Draw round indicator
    if game_state != "game_over":
        round_text = font_medium.render("Prepare to Duel!", True, BLACK)
        screen.blit(round_text, (WIDTH // 2 - 100, 20))
    
    # Draw hit message if available
    if hit_message:
        hit_text = font_medium.render(hit_message, True, RED)
        screen.blit(hit_text, (WIDTH // 2 - 200, 60))
    
    # Draw game state specific information
    if game_state == "aiming":
        instructions = font_medium.render("UP/DOWN: Angle, LEFT/RIGHT: Power, SPACE: Ready", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - 300, 100))
    elif game_state == "countdown" and countdown is not None:
        countdown_text = font_large.render(str(countdown), True, RED)
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 50))
    elif game_state == "game_over" and winner is not None:
        winner_text = font_medium.render(f"{winner} wins!", True, BLACK)
        screen.blit(winner_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        restart_text = font_small.render("Press R to restart or Q to quit", True, BLACK)
        screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 20))

def main():
    clock = pygame.time.Clock()
    
    # Create player and NPC with greatly increased distance (3x)
    player = Player(20, HEIGHT - 150, BLUE, is_player=True)
    npc = Player(WIDTH - 50, HEIGHT - 150, RED)
    
    # Game states: "aiming" -> "countdown" -> "shooting" -> "result" -> back to "aiming" or "game_over"
    game_state = "aiming"
    countdown_start = 0
    countdown_value = 3
    winner = None
    hit_message = None
    
    # Key state tracking for continuous adjustments
    keys_pressed = {
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False
    }
    
    # Key repeat settings
    key_repeat_delay = 100  # ms before starting to repeat
    key_repeat_interval = 30  # ms between repeats
    last_key_action_time = 0
    
    # NPC variables
    npc_aim_angle_change = 0
    npc_aim_power_change = 0
    npc_last_aim_time = 0
    npc_aim_interval = 300  # Time between NPC aim adjustments (ms)
    
    # Randomize initial NPC aim
    npc.aim_angle = random.randint(5, 30)
    npc.aim_power = random.randint(30, 45)  # Increased power for longer distance
    
    # Reset function for next round
    def reset_for_next_round():
        nonlocal game_state, hit_message, countdown_value
        # Reset bullets
        player.bullet = None
        npc.bullet = None
        player.has_shot = False
        npc.has_shot = False
        # Reset game state
        game_state = "aiming"
        hit_message = None
        countdown_value = 3
        
        # Randomize NPC aim for next round
        npc.aim_angle = random.randint(5, 30)
        npc.aim_power = random.randint(30, 45)
        
        # Reset NPC aim behavior
        nonlocal npc_aim_angle_change, npc_aim_power_change, npc_last_aim_time
        npc_aim_angle_change = random.choice([-1, 0, 1])
        npc_aim_power_change = random.choice([-1, 0, 1])
        npc_last_aim_time = pygame.time.get_ticks()
    
    # Initialize NPC aim behavior
    npc_aim_angle_change = random.choice([-1, 0, 1])
    npc_aim_power_change = random.choice([-1, 0, 1])
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
                    elif event.key == pygame.K_RIGHT:
                        player.adjust_aim_power(1)  # Increase power
                    elif event.key == pygame.K_LEFT:
                        player.adjust_aim_power(-1)  # Decrease power
                    elif event.key == pygame.K_SPACE:
                        # Start countdown when player is ready
                        game_state = "countdown"
                        countdown_start = pygame.time.get_ticks()
                
                # Game over controls
                if game_state == "game_over":
                    if event.key == pygame.K_r:
                        # Reset game completely
                        player = Player(20, HEIGHT - 150, BLUE, is_player=True)
                        npc = Player(WIDTH - 50, HEIGHT - 150, RED)
                        npc.aim_angle = random.randint(5, 30)
                        npc.aim_power = random.randint(30, 45)
                        game_state = "aiming"
                        winner = None
                        hit_message = None
                        countdown_value = 3
                        # Reset NPC aim behavior
                        npc_aim_angle_change = random.choice([-1, 0, 1])
                        npc_aim_power_change = random.choice([-1, 0, 1])
                        npc_last_aim_time = pygame.time.get_ticks()
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
            
            if keys_pressed[pygame.K_RIGHT]:
                player.adjust_aim_power(1)
                last_key_action_time = current_time
            elif keys_pressed[pygame.K_LEFT]:
                player.adjust_aim_power(-1)
                last_key_action_time = current_time
        
        # Update game state based on current state
        if game_state == "aiming":
            # NPC randomly adjusts aim periodically
            if current_time - npc_last_aim_time > npc_aim_interval:
                # Randomly change aim direction occasionally
                if random.random() < 0.3:
                    npc_aim_angle_change = random.choice([-1, 0, 1])
                if random.random() < 0.3:
                    npc_aim_power_change = random.choice([-1, 0, 1])
                
                # Apply the changes
                if npc_aim_angle_change != 0:
                    npc.adjust_aim_angle(npc_aim_angle_change)
                if npc_aim_power_change != 0:
                    npc.adjust_aim_power(npc_aim_power_change)
                
                npc_last_aim_time = current_time
        
        elif game_state == "countdown":
            elapsed = current_time - countdown_start
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
            player.update_bullet()
            npc.update_bullet()
            
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
        draw_scene(player, npc, game_state, "simultaneous", countdown_value, winner, hit_message)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
