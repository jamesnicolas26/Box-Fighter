import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHARACTER_WIDTH, CHARACTER_HEIGHT = 50, 100
CHARACTER_SPEED = 5
JUMP_SPEED = 10
GRAVITY = 0.5
ATTACK_DAMAGE = 10
SPECIAL_DAMAGE = 20
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
BACKGROUND_COLOR = (50, 50, 50)
CHARACTER_COLOR1 = (255, 0, 0)
CHARACTER_COLOR2 = (0, 0, 255)
SPECIAL_COLOR = (255, 255, 0)
HEALTH_COLOR = (0, 255, 0)
HEALTH_BAR_BG_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 30
FPS = 60
SPECIAL_MOVE_COOLDOWN = 100
SPECIAL_MOVE_SPEED = 7
AI_ACTION_COOLDOWN = 30

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Street Fighter')

# Fonts
font = pygame.font.Font(None, FONT_SIZE)


class Character:
    def __init__(self, x, y, color, controls=None, is_ai=False):
        self.rect = pygame.Rect(x, y, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        self.color = color
        self.vel_y = 0
        self.is_jumping = False
        self.health = 100
        self.is_attacking = False
        self.attack_cooldown = 0
        self.special_cooldown = SPECIAL_MOVE_COOLDOWN
        self.special_moves = []
        self.is_ai = is_ai
        self.ai_action_cooldown = AI_ACTION_COOLDOWN
        self.controls = controls

    def move(self, keys, opponent=None):
        if self.is_ai:
            self.ai_move(opponent)
        else:
            if keys[self.controls['left']]:
                self.rect.x -= CHARACTER_SPEED
            if keys[self.controls['right']]:
                self.rect.x += CHARACTER_SPEED
            if keys[self.controls['jump']] and not self.is_jumping:
                self.vel_y = -JUMP_SPEED
                self.is_jumping = True
            if keys[self.controls['attack']] and self.attack_cooldown == 0:
                self.is_attacking = True
                self.attack_cooldown = 20
            else:
                self.is_attacking = False

            if keys[self.controls['special']] and self.special_cooldown == 0:
                self.special_move()
                self.special_cooldown = SPECIAL_MOVE_COOLDOWN

        # Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.y > SCREEN_HEIGHT - CHARACTER_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - CHARACTER_HEIGHT
            self.is_jumping = False
            self.vel_y = 0

        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Special cooldown
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

        # Update special moves
        self.update_special_moves()

    def ai_move(self, opponent):
        # AI logic for improved behavior
        if self.ai_action_cooldown > 0:
            self.ai_action_cooldown -= 1
            return
        self.ai_action_cooldown = AI_ACTION_COOLDOWN

        # Simple AI: move towards the player and attack
        if random.random() < 0.7:
            if self.rect.x < opponent.rect.x:
                self.rect.x += CHARACTER_SPEED
            else:
                self.rect.x -= CHARACTER_SPEED

        # Randomly jump
        if random.random() < 0.05 and not self.is_jumping:
            self.vel_y = -JUMP_SPEED
            self.is_jumping = True

        # Randomly attack
        if random.random() < 0.1:
            self.is_attacking = True
            self.attack_cooldown = 20
        else:
            self.is_attacking = False

        # Randomly use special move
        if random.random() < 0.05 and self.special_cooldown == 0:
            self.special_move()
            self.special_cooldown = SPECIAL_MOVE_COOLDOWN

    def special_move(self):
        # Create a new special move projectile
        direction = 1 if self.color == CHARACTER_COLOR1 else -1
        special_move_rect = pygame.Rect(self.rect.centerx, self.rect.y + 20, 20, 10)
        self.special_moves.append((special_move_rect, direction))

    def update_special_moves(self):
        # Move special moves and remove them if they go off-screen
        for special_move in self.special_moves:
            special_move[0].x += SPECIAL_MOVE_SPEED * special_move[1]

        self.special_moves = [sm for sm in self.special_moves if 0 < sm[0].x < SCREEN_WIDTH]

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        if self.is_attacking:
            pygame.draw.line(surface, SPECIAL_COLOR, (self.rect.centerx, self.rect.top),
                             (self.rect.centerx + 50, self.rect.top), 5)

        # Draw special moves
        for special_move in self.special_moves:
            pygame.draw.rect(surface, SPECIAL_COLOR, special_move[0])

    def apply_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def draw_health(self, surface, x, y):
        health_bar = pygame.Rect(x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        current_health = pygame.Rect(x, y, HEALTH_BAR_WIDTH * (self.health / 100), HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, health_bar)
        pygame.draw.rect(surface, HEALTH_COLOR, current_health)
        draw_text(f"Health: {self.health}", font, TEXT_COLOR, surface, x + 10, y - 30)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def main():
    clock = pygame.time.Clock()

    # Controls
    controls1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_s,
                 'special': pygame.K_e}

    # Player character
    char1 = Character(100, SCREEN_HEIGHT - CHARACTER_HEIGHT, CHARACTER_COLOR1, controls1)

    # AI-controlled character
    char2 = Character(SCREEN_WIDTH - CHARACTER_WIDTH - 100, SCREEN_HEIGHT - CHARACTER_HEIGHT, CHARACTER_COLOR2,
                      is_ai=True)

    game_active = True

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()

            if game_active:
                # Control characters
                char1.move(keys)
                char2.move(keys, opponent=char1)

                # Check for collision or attacks
                if char1.rect.colliderect(char2.rect):
                    if char1.is_attacking:
                        char2.apply_damage(ATTACK_DAMAGE)
                    if char2.is_attacking:
                        char1.apply_damage(ATTACK_DAMAGE)

                # Check special move collisions
                for special_move in char1.special_moves:
                    if special_move[0].colliderect(char2.rect):
                        char2.apply_damage(SPECIAL_DAMAGE)
                        char1.special_moves.remove(special_move)

                for special_move in char2.special_moves:
                    if special_move[0].colliderect(char1.rect):
                        char1.apply_damage(SPECIAL_DAMAGE)
                        char2.special_moves.remove(special_move)

                # Game over check
                if char1.health <= 0 or char2.health <= 0:
                    game_active = False

            # Draw everything
            screen.fill(BACKGROUND_COLOR)
            char1.draw(screen)
            char2.draw(screen)
            char1.draw_health(screen, 10, 10)
            char2.draw_health(screen, SCREEN_WIDTH - HEALTH_BAR_WIDTH - 10, 10)

            if not game_active:
                if char1.health <= 0:
                    draw_text("AI Wins!", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                elif char2.health <= 0:
                    draw_text("Player Wins!", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

                draw_text("Press SPACE to Restart", font, TEXT_COLOR, screen, SCREEN_WIDTH // 2,
                          SCREEN_HEIGHT // 2 + 50)

                if keys[pygame.K_SPACE]:
                    # Reset the game
                    char1.health = 100
                    char2.health = 100
                    char1.rect.x = 100
                    char1.rect.y = SCREEN_HEIGHT - CHARACTER_HEIGHT
                    char2.rect.x = SCREEN_WIDTH - CHARACTER_WIDTH - 100
                    char2.rect.y = SCREEN_HEIGHT - CHARACTER_HEIGHT
                    char1.special_moves = []
                    char2.special_moves = []
                    game_active = True

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
