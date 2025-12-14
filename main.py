import pygame
import sys
import random

# -------------------------------------------------
# NIGHT GUARD 
# Controls:
#   A = toggle left door
#   D = toggle right door
#   R = restart after game over
#   ESC = quit
# -------------------------------------------------

# -----------------------------
# INITIAL SETUP
# -----------------------------
pygame.init()

# window size
WIDTH = 640
HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Night Guard")

clock = pygame.time.Clock()
FPS = 60  # frames per second

# -----------------------------
# COLORS
# -----------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREY = (30, 30, 30)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (230, 230, 50)
BLUE = (50, 50, 200)

# -----------------------------
# GAME VARIABLES
# -----------------------------
# Power system: drains very slowly,
# a bit faster when doors are closed.
power = 100.0             
base_power_drain = 0.003  
door_power_drain = 0.05   

# Doors: 
door_width = 30
door_height = 140

# doors near the middle of the room
left_door_x = WIDTH // 2 - 150
right_door_x = WIDTH // 2 + 120

left_door_rect = pygame.Rect(
    left_door_x,
    HEIGHT // 2 - door_height // 2,
    door_width,
    door_height
)

right_door_rect = pygame.Rect(
    right_door_x,
    HEIGHT // 2 - door_height // 2,
    door_width,
    door_height
)

# Door states: True = closed, False = open
left_door_closed = False
right_door_closed = False

# Monster: small, slow yellow square
monster_size = 40
monster_speed = 1.0   # slow movement so you have time

monster_rect = pygame.Rect(0, 0, monster_size, monster_size)
monster_side = "LEFT"  # "LEFT" or "RIGHT"

# Attack timing
attack_in_progress = False
time_between_attacks = 180  
attack_timer = 0

# Score: how many attacks you survived
score = 0

# Font for text
font = pygame.font.SysFont("arial", 24)

# Game state
game_over = False


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def start_attack():
    """
    Start a new monster attack from either the left or right side.
    """
    global attack_in_progress, monster_side, monster_rect, attack_timer

    attack_in_progress = True
    attack_timer = 0
    monster_side = random.choice(["LEFT", "RIGHT"])

    # Start off-screen on the chosen side
    if monster_side == "LEFT":
        monster_rect.x = -monster_size
    else:
        monster_rect.x = WIDTH

    # Center vertically
    monster_rect.y = HEIGHT // 2 - monster_size // 2


def reset_game():
    """
    Reset the game so the player can play again.
    """
    global left_door_closed, right_door_closed, attack_in_progress
    global attack_timer, score, monster_speed, game_over, power

    left_door_closed = False
    right_door_closed = False
    attack_in_progress = False
    attack_timer = 0
    score = 0

    # Reset monster speed 
    monster_speed = 1.0

    game_over = False
    power = 100.0  # full power again


# -----------------------------
# MAIN GAME LOOP
# -----------------------------
running = True
while running:
    clock.tick(FPS)

    # -------------------------
    # EVENT HANDLING
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # ESC = quit the game
            if event.key == pygame.K_ESCAPE:
                running = False

            if not game_over:
                # A = toggle left door
                if event.key == pygame.K_a:
                    left_door_closed = not left_door_closed

                # D = toggle right door
                if event.key == pygame.K_d:
                    right_door_closed = not right_door_closed
            else:
                # If game is over, R = restart
                if event.key == pygame.K_r:
                    reset_game()

    # -----------------------------
    # GAME LOGIC
    # -----------------------------
    if not game_over:
        # --- POWER LOGIC ---
        # Always drain a tiny bit of power
        power -= base_power_drain

        # Closed doors drain extra power
        if left_door_closed:
            power -= door_power_drain
        if right_door_closed:
            power -= door_power_drain

        # Clamp and check for power-out game over
        if power <= 0:
            power = 0
            game_over = True

        # --- ATTACK LOGIC ---
        if not attack_in_progress:
            # Wait some time before starting an attack
            attack_timer += 1
            if attack_timer >= time_between_attacks:
                start_attack()

        if attack_in_progress:
            if monster_side == "LEFT":
                monster_rect.x += monster_speed
                # Monster reaches left door area
                if monster_rect.x + monster_size >= left_door_rect.x:
                    if not left_door_closed:
                        game_over = True
                    else:
                        score += 1
                        monster_speed += 0.15  # tiny speed increase
                    attack_in_progress = False
                    attack_timer = 0
            else:  # monster_side == "RIGHT"
                monster_rect.x -= monster_speed
                # Monster reaches right door area
                if monster_rect.x <= right_door_rect.x + right_door_rect.width:
                    if not right_door_closed:
                        game_over = True
                    else:
                        score += 1
                        monster_speed += 0.15
                    attack_in_progress = False
                    attack_timer = 0

    # -----------------------------
    # DRAWING
    # -----------------------------
    screen.fill(DARK_GREY)

    # Doors: green = open, red = closed
    left_color = RED if left_door_closed else GREEN
    right_color = RED if right_door_closed else GREEN
    pygame.draw.rect(screen, left_color, left_door_rect)
    pygame.draw.rect(screen, right_color, right_door_rect)

    # Small desk at bottom center
    desk_width = 220
    desk_height = 60
    desk_rect = pygame.Rect(
        WIDTH // 2 - desk_width // 2,
        HEIGHT - desk_height - 30,
        desk_width,
        desk_height
    )
    pygame.draw.rect(screen, BLUE, desk_rect)

    # Monster (yellow square)
    if attack_in_progress and not game_over:
        pygame.draw.rect(screen, YELLOW, monster_rect)

    # Title / version label so you KNOW this is the new game
    title_text = font.render("Night Guard", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

    # Score text
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 40))

    # Power text
    power_text = font.render(f"Power: {int(power)}%", True, WHITE)
    screen.blit(power_text, (10, 70))

    # Game over text
    if game_over:
        game_over_text = font.render("Game Over! Press R to restart", True, WHITE)
        text_x = WIDTH // 2 - game_over_text.get_width() // 2
        text_y = HEIGHT // 2 - game_over_text.get_height() // 2
        screen.blit(game_over_text, (text_x, text_y))

    pygame.display.flip()

# -----------------------------
# CLEANUP
# -----------------------------
pygame.quit()
sys.exit()
# pushing to github
