import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Spaceship Game")

# Load images
background_image = pygame.image.load('background.jpg')
spaceship_image = pygame.image.load('player.png')
spaceship_image = pygame.transform.scale(spaceship_image, (50, 50))
enemy_image = pygame.image.load('enemy.png')
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
explosion_image = pygame.image.load('explosion.png')
explosion_image = pygame.transform.scale(explosion_image, (50, 50))  # Adjust size as needed

# Load sounds
explosion_sound = pygame.mixer.Sound('explosion.mp3')
laser_sound = pygame.mixer.Sound('laser.mp3')
deathray_sound = pygame.mixer.Sound('deathray.mp3')
start_music = pygame.mixer.Sound('gamestart.mp3')
gameover_music = pygame.mixer.Sound('gameover.mp3')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game properties
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = spaceship_image.get_size()
ENEMY_WIDTH, ENEMY_HEIGHT = enemy_image.get_size()
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
spaceship_speed = 5
bullet_speed = 5  # Speed for player bullets
enemy_bullet_speed = 0.25  # Speed for enemy bullets (slowed down significantly)
enemy_speed = 2
enemy_spawn_rate = 30  # Reduced spawn rate to make it slower
enemy_fire_rate = 150  # Enemies fire slower
special_ex_max = 100
special_ex_fill_rate = 5
enemy_health = 3
score = 0
highscore = 0
wave = 1
enemies_per_wave = 10
max_enemies_on_screen = 4
game_active = False

# Initialize clock
clock = pygame.time.Clock()

# Initialize fonts
font = pygame.font.Font(None, 36)

# Initialize lists
bullets = []
enemies = []
explosions = []

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_spaceship(x, y):
    screen.blit(spaceship_image, (x, y))

def draw_bullet(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BULLET_WIDTH, BULLET_HEIGHT))

def draw_enemy(x, y):
    screen.blit(enemy_image, (x, y))

def draw_explosions():
    for explosion in explosions[:]:
        screen.blit(explosion_image, (explosion['x'], explosion['y']))
        explosions.remove(explosion)  # Remove the explosion after drawing it

def update_bullets():
    global bullets, score
    for bullet in bullets[:]:
        if bullet.get('is_special'):
            bullet['y'] -= bullet_speed * 2  # Special ray moves faster
        else:
            bullet['y'] -= bullet_speed

        if bullet['y'] < 0:
            bullets.remove(bullet)
        else:
            for enemy in enemies[:]:
                if (enemy['x'] < bullet['x'] < enemy['x'] + ENEMY_WIDTH or enemy['x'] < bullet['x'] + BULLET_WIDTH < enemy['x'] + ENEMY_WIDTH) and (enemy['y'] < bullet['y'] < enemy['y'] + ENEMY_HEIGHT or enemy['y'] < bullet['y'] + BULLET_HEIGHT < enemy['y'] + ENEMY_HEIGHT):
                    enemy['health'] -= 1
                    bullets.remove(bullet)
                    if enemy['health'] <= 0:
                        enemies.remove(enemy)
                        score += 1
                        explosions.append({'x': enemy['x'], 'y': enemy['y']})
                        explosion_sound.play()
                    break

def update_enemies():
    global enemies
    for enemy in enemies[:]:
        # Move enemy towards the player
        dx = spaceship_x - enemy['x']
        dy = spaceship_y - enemy['y']
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance > 0:
            dx /= distance
            dy /= distance

        enemy['x'] += dx * enemy_speed
        enemy['y'] += dy * enemy_speed

        # Check if enemy has reached the bottom of the screen
        if enemy['y'] > SCREEN_HEIGHT:
            enemies.remove(enemy)
            return True

        # Spawn enemy bullets
        if random.randint(1, enemy_fire_rate) == 1:
            bullets.append({'x': enemy['x'] + ENEMY_WIDTH // 2 - BULLET_WIDTH // 2, 'y': enemy['y'] + ENEMY_HEIGHT, 'is_enemy': True})
        
        # Move enemy bullets
        for bullet in bullets[:]:
            if bullet.get('is_enemy'):
                bullet['y'] += enemy_bullet_speed
                if bullet['y'] > SCREEN_HEIGHT:
                    bullets.remove(bullet)
                elif (spaceship_x < bullet['x'] < spaceship_x + SPACESHIP_WIDTH or spaceship_x < bullet['x'] + BULLET_WIDTH < spaceship_x + SPACESHIP_WIDTH) and (spaceship_y < bullet['y'] < spaceship_y + SPACESHIP_HEIGHT or spaceship_y < bullet['y'] + BULLET_HEIGHT < spaceship_y + SPACESHIP_HEIGHT):
                    return True
    return False

def draw_special_ex_bar(experience):
    pygame.draw.rect(screen, WHITE, (10, SCREEN_HEIGHT - 20, special_ex_max, 10))
    pygame.draw.rect(screen, (0, 255, 0), (10, SCREEN_HEIGHT - 20, experience, 10))

def draw_start_menu():
    screen.fill(BLACK)
    draw_text('Press Enter to Start', font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()

def draw_game_over():
    screen.fill(BLACK)
    draw_text('Game Over', font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
    draw_text(f'Your Score: {score}', font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
    draw_text(f'Highscore: {highscore}', font, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
    pygame.display.flip()

def reset_game():
    global spaceship_x, spaceship_y, bullets, enemies, special_ex, game_active, wave, enemies_per_wave, explosions, enemy_health, score

    spaceship_x = SCREEN_WIDTH // 2 - SPACESHIP_WIDTH // 2
    spaceship_y = SCREEN_HEIGHT - SPACESHIP_HEIGHT - 10
    special_ex = 0
    bullets = []
    enemies = []
    explosions = []
    score = 0
    wave = 1
    enemies_per_wave = 10
    enemy_fire_rate = 150
    enemy_health = 3
    game_active = True

def main():
    global spaceship_x, spaceship_y, bullets, enemies, special_ex, game_active, wave, highscore, enemies_per_wave, explosions, enemy_health, score

    # Initialize game state
    reset_game()

    # Show the start menu first
    draw_start_menu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not game_active:
                    reset_game()
                    start_music.stop()
                    pygame.mixer.music.load('gamestart.mp3')
                    pygame.mixer.music.play(-1)
                if event.key == pygame.K_SPACE and game_active:
                    bullets.append({'x': spaceship_x + SPACESHIP_WIDTH // 2 - BULLET_WIDTH // 2, 'y': spaceship_y})
                    laser_sound.play()
                if event.key == pygame.K_b and special_ex >= special_ex_max:
                    bullets.append({'x': spaceship_x + SPACESHIP_WIDTH // 2 - BULLET_WIDTH // 2, 'y': spaceship_y, 'is_special': True})
                    special_ex = 0
                    score += len(enemies) * 3
                    enemies = []
                    deathray_sound.play()

        if game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                spaceship_x -= spaceship_speed
            if keys[pygame.K_RIGHT]:
                spaceship_x += spaceship_speed

            spaceship_x = max(0, min(spaceship_x, SCREEN_WIDTH - SPACESHIP_WIDTH))

            if len(enemies) < min(enemies_per_wave, max_enemies_on_screen):
                x = random.randint(0, max(SCREEN_WIDTH - ENEMY_WIDTH, 0))
                enemies.append({'x': x, 'y': -ENEMY_HEIGHT, 'health': enemy_health})

            special_ex = min(special_ex + special_ex_fill_rate, special_ex_max)

            screen.blit(background_image, (0, 0))
            draw_spaceship(spaceship_x, spaceship_y)
            update_bullets()
            if update_enemies():
                game_active = False
                gameover_music.play()
                if score > highscore:
                    highscore = score

            for bullet in bullets:
                draw_bullet(bullet['x'], bullet['y'])
            for enemy in enemies:
                draw_enemy(enemy['x'], enemy['y'])
            draw_explosions()  # Draw explosions
            draw_special_ex_bar(special_ex)

            draw_text(f'Score: {score}', font, WHITE, screen, 70, 20)
            draw_text(f'Wave: {wave}', font, WHITE, screen, SCREEN_WIDTH - 70, 20)

            pygame.display.flip()
            clock.tick(60)

            # Progress to the next wave if all enemies are cleared
            if not enemies:
                wave += 1
                enemies_per_wave = int(enemies_per_wave * 1.5)
                enemy_fire_rate = max(30, enemy_fire_rate - 10)  # Make it easier, not too hard
                enemy_health = min(10, enemy_health + 1)  # Increase difficulty

        else:
            draw_game_over()
            pygame.display.flip()
            pygame.time.wait(3000)  # Show game over screen for 3 seconds
            reset_game()  # Restart the game after showing game over

if __name__ == "__main__":
    main()
