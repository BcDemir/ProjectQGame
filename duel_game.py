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
GRAVITY = 0.5
GROUND_LEVEL = HEIGHT - 100

class Bullet:
    def __init__(self, x, y, angle, speed, is_player):
        self.x = x
        self.y = y
        self.angle = angle  # in degrees
        self.speed = speed
        self.is_player = is_player
        self.active = True
        self.radius = 5
        self.trail = []  # Store positions for bullet trail
        self.max_trail_length = 10
        
        # Convert angle to radians and calculate velocity components
        angle_rad = math.radians(angle)
        self.vx = math.cos(angle_rad) * speed * (1 if is_player else -1)
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
        if (self.y > player.y - 15 - 20 and  # Head top (with radius)
            self.y < player.y + player.height):  # Body bottom
            
            # Check horizontal position
            if self.is_player:  # Player bullet
                if self.x > player.x - 20:  # Account for head radius
                    self.active = False
                    player.health -= 100
                    return True
            else:  # NPC bullet
                if self.x < player.x + player.width + 20:  # Account for head radius
                    self.active = False
                    player.health -= 100
                    return True
        return False

class Player:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 100
        self.color = color
        self.has_shot = False
        self.shot_time = 0
        self.bullet = None
        self.health = 100
        self.is_player = is_player
        self.aim_y = y + 45  # Default aim height
        self.aim_direction = 1 if is_player else -1  # 1 for right, -1 for left
        self.aim_angle = 0  # Angle in degrees (0 is horizontal)
        self.aim_power = 25  # Initial bullet speed
        self.min_power = 15
        self.max_power = 35
        
    def draw(self, screen, aiming=False):
        # Draw body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw head
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y - 15), 20)
        
        # Calculate gun position
        gun_x = self.x + self.width if self.is_player else self.x
        gun_y = self.aim_y
        
        # Calculate gun end point based on angle
        angle_rad = math.radians(self.aim_angle)
        gun_length = 30
        gun_end_x = gun_x + (gun_length * math.cos(angle_rad) * self.aim_direction)
        gun_end_y = gun_y - (gun_length * math.sin(angle_rad))
        
        # Draw gun
        pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_end_x, gun_end_y), 5)
        
        # Draw aiming line and trajectory prediction if in aiming phase
        if aiming and self.is_player:
            # Draw aiming line
            line_length = 50
            line_end_x = gun_end_x + (line_length * math.cos(angle_rad) * self.aim_direction)
            line_end_y = gun_end_y - (line_length * math.sin(angle_rad))
            pygame.draw.line(screen, YELLOW, (gun_end_x, gun_end_y), (line_end_x, line_end_y), 2)
            
            # Draw trajectory prediction (simplified)
            self.draw_trajectory_prediction(screen, gun_end_x, gun_end_y)
            
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
            
    def draw_trajectory_prediction(self, screen, start_x, start_y):
        # Simplified trajectory prediction
        points = []
        
        # Calculate initial velocity components
        angle_rad = math.radians(self.aim_angle)
        vx = math.cos(angle_rad) * self.aim_power * self.aim_direction
        vy = -math.sin(angle_rad) * self.aim_power
        
        # Simulate trajectory
        sim_x, sim_y = start_x, start_y
        for _ in range(30):  # Predict 30 steps ahead
            sim_x += vx
            sim_y += vy
            vy += GRAVITY / 2  # Use half gravity for prediction to make it more visible
            
            # Stop if prediction hits ground or goes out of bounds
            if sim_y > GROUND_LEVEL or sim_x < 0 or sim_x > WIDTH:
                break
                
            points.append((int(sim_x), int(sim_y)))
            
        # Draw trajectory dots
        for i, point in enumerate(points):
            # Make dots fade out
            alpha = 255 - int(200 * (i / len(points)))
            dot_color = YELLOW
            dot_size = 2
            pygame.draw.circle(screen, dot_color, point, dot_size)
            
    def adjust_aim_angle(self, direction):
        # Adjust aim angle (up/down)
        self.aim_angle += direction * 2
        # Limit angle to reasonable range (0-90 degrees)
        self.aim_angle = max(0, min(self.aim_angle, 60))
        
        # Update aim_y based on angle for compatibility
        self.aim_y = self.y + 45 - (self.aim_angle * 1.5)
        
    def adjust_aim_power(self, direction):
        # Adjust aim power (stronger/weaker)
        self.aim_power += direction
        # Limit power to reasonable range
        self.aim_power = max(self.min_power, min(self.aim_power, self.max_power))
            
    def shoot(self):
        if not self.has_shot:
            self.has_shot = True
            self.shot_time = pygame.time.get_ticks()
            
            # Calculate gun position
            gun_x = self.x + self.width if self.is_player else self.x
            gun_y = self.aim_y
            
            # Calculate gun end point based on angle
            angle_rad = math.radians(self.aim_angle)
            gun_length = 30
            gun_end_x = gun_x + (gun_length * math.cos(angle_rad) * self.aim_direction)
            gun_end_y = gun_y - (gun_length * math.sin(angle_rad))
            
            # Create bullet
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

def draw_scene(player, npc, game_state, countdown=None, winner=None):
    # Draw sky
    screen.fill(SKY_BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, BROWN, (0, GROUND_LEVEL, WIDTH, HEIGHT - GROUND_LEVEL))
    
    # Draw players - show aiming line only in aiming phase
    player.draw(screen, game_state == "aiming")
    npc.draw(screen)
    
    # Draw bullets
    player.draw_bullet(screen)
    npc.draw_bullet(screen)
    
    # Draw health bars
    pygame.draw.rect(screen, RED, (50, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (50, 20, player.health * 2, 20))
    pygame.draw.rect(screen, RED, (WIDTH - 250, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (WIDTH - 250, 20, npc.health * 2, 20))
    
    # Draw labels
    player_label = font_small.render("Player", True, BLACK)
    npc_label = font_small.render("NPC", True, BLACK)
    screen.blit(player_label, (50, 45))
    screen.blit(npc_label, (WIDTH - 250, 45))
    
    # Draw game state specific information
    if game_state == "aiming":
        instructions = font_medium.render("UP/DOWN: Angle, LEFT/RIGHT: Power, SPACE: Ready", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - 300, 50))
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
    
    # Create player and NPC with greatly increased distance
    player = Player(20, HEIGHT - 200, BLUE, is_player=True)
    npc = Player(WIDTH - 70, HEIGHT - 200, RED)
    
    # Game states: "aiming" -> "countdown" -> "duel" -> "game_over"
    game_state = "aiming"
    countdown_start = 0
    countdown_value = 3
    winner = None
    
    # NPC variables
    npc_reaction_time = random.randint(200, 800)
    duel_start_time = 0
    
    # Randomize NPC aim
    npc.aim_angle = random.randint(5, 30)
    npc.aim_power = random.randint(20, 30)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
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
                
                if game_state == "game_over":
                    if event.key == pygame.K_r:
                        # Reset game
                        player = Player(20, HEIGHT - 200, BLUE, is_player=True)
                        npc = Player(WIDTH - 70, HEIGHT - 200, RED)
                        npc.aim_angle = random.randint(5, 30)
                        npc.aim_power = random.randint(20, 30)
                        game_state = "aiming"
                        countdown_value = 3
                        winner = None
                        npc_reaction_time = random.randint(200, 800)
                    elif event.key == pygame.K_q:
                        running = False
        
        # Update game state
        current_time = pygame.time.get_ticks()
        
        if game_state == "countdown":
            elapsed = current_time - countdown_start
            if elapsed < 1000:
                countdown_value = 3
            elif elapsed < 2000:
                countdown_value = 2
            elif elapsed < 3000:
                countdown_value = 1
            else:
                game_state = "duel"
                duel_start_time = current_time
                countdown_value = "DRAW!"
        
        elif game_state == "duel":
            # Both duelists shoot automatically after the countdown
            if not player.has_shot:
                player.shoot()
                
            # NPC shoots after reaction time
            if current_time - duel_start_time > npc_reaction_time and not npc.has_shot:
                npc.shoot()
            
            # Update bullets
            player.update_bullet()
            npc.update_bullet()
            
            # Check for hits
            if player.check_hit(npc):
                winner = "Player"
                game_state = "game_over"
            
            if npc.check_hit(player):
                winner = "NPC"
                game_state = "game_over"
                
            # Check if both bullets are inactive and no one hit
            if (player.has_shot and npc.has_shot and 
                ((player.bullet and not player.bullet.active) or not player.bullet) and
                ((npc.bullet and not npc.bullet.active) or not npc.bullet) and
                not winner):
                winner = "Nobody"
                game_state = "game_over"
        
        # Draw everything
        draw_scene(player, npc, game_state, countdown_value, winner)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
