import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga-like Game")

# Load images
background_image = pygame.image.load('background.jpg')
spaceship_image = pygame.image.load('player.png')
spaceship_image = pygame.transform.scale(spaceship_image, (50, 50))
enemy_image = pygame.image.load('enemy.png')
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
explosion_image = pygame.image.load('explosion.png')
explosion_image = pygame.transform.scale(explosion_image, (50, 50))  # Adjust size as needed
boss_image = pygame.image.load('boss.png')
boss_image = pygame.transform.scale(boss_image, (300, 300))  # Adjust size as needed
print("Boss image size:", boss_image.get_size())  # Print boss image dimensions

# Load sounds
explosion_sound = pygame.mixer.Sound('explosion.mp3')
laser_sound = pygame.mixer.Sound('laser.mp3')
enemy_laser_sound = pygame.mixer.Sound('laser.mp3')  # Use the same sound for enemy bullets
start_music = pygame.mixer.Sound('gamestart.mp3')
gameover_music = pygame.mixer.Sound('gameover.mp3')
boss_music = pygame.mixer.Sound('boss.mp3')  # Boss battle music

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game properties
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = spaceship_image.get_size()
ENEMY_WIDTH, ENEMY_HEIGHT = enemy_image.get_size()
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
spaceship_speed = 5
bullet_speed = 5  # Speed for both player and enemy bullets
enemy_speed = 2
enemy_bullet_speed = 4
enemy_fire_rate = 2000  # Milliseconds between enemy bursts
enemy_health = 3
score = 0
highscore = 0
wave = 1
max_enemies_on_screen = 4
game_active = False
boss_appears = False
boss_health = 10

# Initialize clock
clock = pygame.time.Clock()

# Initialize fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Initialize lists
bullets = []
enemies = []
explosions = []
last_enemy_burst = pygame.time.get_ticks()
enemy_entrance_timer = pygame.time.get_ticks()
boss = None
boss_entrance_timer = None

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

def draw_boss(x, y, health):
    # Ensure boss image is within screen boundaries
    if 0 <= x <= SCREEN_WIDTH - boss_image.get_width() and 0 <= y <= SCREEN_HEIGHT - boss_image.get_height():
        # Draw the boss image
        screen.blit(boss_image, (x, y))
        
        # Draw the health bar above the boss
        pygame.draw.rect(screen, RED, (x, y - 20, boss_image.get_width(), 10))  # Background bar
        pygame.draw.rect(screen, WHITE, (x, y - 20, boss_image.get_width() * (health / boss_health), 10))  # Foreground bar
        
        # Draw boss title text above the boss
        draw_text('King of Aliens', small_font, WHITE, screen, x + boss_image.get_width() // 2, y - 40)
        draw_text('Raviolis', small_font, WHITE, screen, x + boss_image.get_width() // 2, y - 25)
    else:
        print("Boss is out of bounds")  # Debugging message


def update_bullets():
    global bullets, score
    for bullet in bullets[:]:
        if bullet.get('is_enemy'):
            bullet['y'] += enemy_bullet_speed  # Enemies bullets move downwards
        else:
            bullet['y'] -= bullet_speed  # Player bullets move upwards

        if bullet['y'] < 0 or bullet['y'] > SCREEN_HEIGHT:
            bullets.remove(bullet)
            continue

        # Check collision with enemies
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
        
        # Check collision with player
        if bullet.get('is_enemy'):
            if (spaceship_x < bullet['x'] < spaceship_x + SPACESHIP_WIDTH or spaceship_x < bullet['x'] + BULLET_WIDTH < spaceship_x + SPACESHIP_WIDTH) and (spaceship_y < bullet['y'] < spaceship_y + SPACESHIP_HEIGHT or spaceship_y < bullet['y'] + BULLET_HEIGHT < spaceship_y + SPACESHIP_HEIGHT):
                return True  # Player hit by enemy bullet

    return False

def check_enemy_collisions():
    for enemy in enemies[:]:
        if (spaceship_x < enemy['x'] < spaceship_x + SPACESHIP_WIDTH or spaceship_x < enemy['x'] + ENEMY_WIDTH < spaceship_x + SPACESHIP_WIDTH) and (spaceship_y < enemy['y'] < spaceship_y + SPACESHIP_HEIGHT or spaceship_y < enemy['y'] + ENEMY_HEIGHT < spaceship_y + SPACESHIP_HEIGHT):
            return True  # Enemy has collided with the player
    return False

def update_enemies():
    global enemies, last_enemy_burst, enemy_entrance_timer, boss, boss_appears

    current_time = pygame.time.get_ticks()

    if boss_appears:
        if boss:
            # Move boss left and right
            boss['x'] += boss['dx']
            if boss['x'] <= 0 or boss['x'] >= SCREEN_WIDTH - boss_image.get_width():
                boss['dx'] *= -1

            # Boss fires multiple bullets
            if current_time - last_enemy_burst > enemy_fire_rate:
                for i in range(-1, 2):  # Fire 3 bullets
                    bullets.append({'x': boss['x'] + boss_image.get_width() // 2 - BULLET_WIDTH // 2, 'y': boss['y'] + boss_image.get_height(), 'is_enemy': True})
                enemy_laser_sound.play()
                last_enemy_burst = current_time

            # Check if boss is defeated
            if boss['health'] <= 0:
                boss = None
                boss_appears = False
                return False  # Boss defeated, game mode transition
        return False

    # Regular enemies
    for enemy in enemies[:]:
        # Move enemies left and right within a boundary
        enemy['x'] += enemy['dx']

        if enemy['x'] <= 0 or enemy['x'] >= SCREEN_WIDTH - ENEMY_WIDTH:
            enemy['dx'] *= -1

    # Fire bullets from enemies at regular intervals
    if current_time - last_enemy_burst > enemy_fire_rate:
        for enemy in enemies:
            bullets.append({'x': enemy['x'] + ENEMY_WIDTH // 2 - BULLET_WIDTH // 2, 'y': enemy['y'] + ENEMY_HEIGHT, 'is_enemy': True})
            enemy_laser_sound.play()
        last_enemy_burst = current_time

    # Handle entrance animation for enemies
    if enemies and (current_time - enemy_entrance_timer < 3000):  # 3 seconds for animation
        for enemy in enemies:
            if enemy['y'] < enemy['target_y']:
                enemy['y'] += enemy_speed
                if enemy['y'] > enemy['target_y']:
                    enemy['y'] = enemy['target_y']
    else:
        enemy_entrance_timer = current_time  # Reset timer after animation

    return False

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

def draw_game_status():
    draw_text(f'Score: {score}', font, WHITE, screen, 70, 20)
    draw_text(f'Wave: {wave}', font, WHITE, screen, SCREEN_WIDTH - 70, 20)

def reset_game():
    global spaceship_x, spaceship_y, bullets, enemies, game_active, wave, highscore, explosions, enemy_health, score, enemy_fire_rate, boss, boss_appears

    spaceship_x = SCREEN_WIDTH // 2 - SPACESHIP_WIDTH // 2
    spaceship_y = SCREEN_HEIGHT - SPACESHIP_HEIGHT - 10
    bullets = []
    enemies = []
    explosions = []
    score = 0
    wave = 1
    enemy_fire_rate = 2000
    enemy_health = 3
    game_active = True
    boss = None
    boss_appears = False

def spawn_enemies():
    global enemies, boss_appears, boss

    if wave > 0 and not boss_appears:
        print("Spawning boss")  # Debug print statement
        boss_appears = True
        # Start the boss just off-screen above
        boss = {'x': SCREEN_WIDTH // 2 - boss_image.get_width() // 2, 'y': -boss_image.get_height(), 'dx': 2, 'health': boss_health}
        pygame.time.wait(2000)  # Boss entrance delay
        boss_music.play(-1)  # Loop boss music
        return

    # Regular enemies
    num_enemies = int(wave * 0.5 * 10)  # Calculate the number of enemies for the current wave
    while len(enemies) < min(num_enemies, max_enemies_on_screen):
        x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        enemies.append({'x': x, 'y': -ENEMY_HEIGHT, 'dx': random.choice([-1, 1]), 'target_y': random.randint(100, SCREEN_HEIGHT // 2), 'health': enemy_health})


def update_enemies():
    global enemies, last_enemy_burst, enemy_entrance_timer, boss, boss_appears

    current_time = pygame.time.get_ticks()

    if boss_appears:
        if boss:
            # Move boss left and right
            boss['x'] += boss['dx']
            if boss['x'] <= 0 or boss['x'] >= SCREEN_WIDTH - boss_image.get_width():
                boss['dx'] *= -1

            # Move boss down into view
            if boss['y'] < SCREEN_HEIGHT // 2:  # Move until the middle of the screen
                boss['y'] += 2  # Adjust this speed as necessary

            # Boss fires multiple bullets
            if current_time - last_enemy_burst > enemy_fire_rate:
                for i in range(-1, 2):  # Fire 3 bullets
                    bullets.append({'x': boss['x'] + boss_image.get_width() // 2 - BULLET_WIDTH // 2, 'y': boss['y'] + boss_image.get_height(), 'is_enemy': True})
                enemy_laser_sound.play()
                last_enemy_burst = current_time

            # Check if boss is defeated
            if boss['health'] <= 0:
                print("Boss defeated")  # Debug print statement
                boss = None
                boss_appears = False
                return False  # Boss defeated, game mode transition
        return False

    # Regular enemies logic
    for enemy in enemies[:]:
        enemy['x'] += enemy['dx']
        if enemy['x'] <= 0 or enemy['x'] >= SCREEN_WIDTH - ENEMY_WIDTH:
            enemy['dx'] *= -1

    if current_time - last_enemy_burst > enemy_fire_rate:
        for enemy in enemies:
            bullets.append({'x': enemy['x'] + ENEMY_WIDTH // 2 - BULLET_WIDTH // 2, 'y': enemy['y'] + ENEMY_HEIGHT, 'is_enemy': True})
            enemy_laser_sound.play()
        last_enemy_burst = current_time

    if enemies and (current_time - enemy_entrance_timer < 3000):  # 3 seconds for animation
        for enemy in enemies:
            if enemy['y'] < enemy['target_y']:
                enemy['y'] += enemy_speed
                if enemy['y'] > enemy['target_y']:
                    enemy['y'] = enemy['target_y']
    else:
        enemy_entrance_timer = current_time  # Reset timer after animation

    return False




def draw_boss(x, y, health):
    print(f"Drawing boss at ({x}, {y}) with health: {health}")  # Debug print
    screen.blit(boss_image, (x, y))
    # Draw the health bar above the boss
    pygame.draw.rect(screen, RED, (x, y - 10, 100, 10))  # Background health bar
    pygame.draw.rect(screen, WHITE, (x, y - 10, 100 * (health / boss_health), 10))  # Foreground health bar
    draw_text('King of Aliens', small_font, WHITE, screen, x + boss_image.get_width() // 2, y - 20)
    draw_text('Raviolis', small_font, WHITE, screen, x + boss_image.get_width() // 2, y - 10)





def main():
    global spaceship_x, spaceship_y, bullets, enemies, game_active, wave, highscore, explosions, enemy_health, score, enemy_fire_rate, boss, boss_appears

    # Initialize game state
    reset_game()

    # Show the start menu first
    draw_start_menu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Properly quit Pygame
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

        if game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                spaceship_x -= spaceship_speed
            if keys[pygame.K_RIGHT]:
                spaceship_x += spaceship_speed

            spaceship_x = max(0, min(spaceship_x, SCREEN_WIDTH - SPACESHIP_WIDTH))

            # Spawn enemies if needed
            if len(enemies) == 0 and not boss_appears:
                wave += 1
                spawn_enemies()

            screen.blit(background_image, (0, 0))  # Draw background
            draw_spaceship(spaceship_x, spaceship_y)  # Draw spaceship
            draw_game_status()  # Draw score and wave number

            if update_bullets():
                game_active = False
                gameover_music.play()
                if score > highscore:
                    highscore = score
                draw_game_over()
                pygame.display.flip()
                pygame.time.wait(3000)  # Show game over screen for 3 seconds
                draw_start_menu()  # Show the start menu again after game over
                continue

            if check_enemy_collisions():
                game_active = False
                gameover_music.play()
                if score > highscore:
                    highscore = score
                draw_game_over()
                pygame.display.flip()
                pygame.time.wait(3000)  # Show game over screen for 3 seconds
                draw_start_menu()  # Show the start menu again after game over
                continue

            if update_enemies():
                game_active = False
                gameover_music.play()
                if score > highscore:
                    highscore = score
                draw_game_over()
                pygame.display.flip()
                pygame.time.wait(3000)  # Show game over screen for 3 seconds
                draw_start_menu()  # Show the start menu again after game over
                continue

            # Draw everything
            draw_explosions()
            for bullet in bullets:
                draw_bullet(bullet['x'], bullet['y'])
            for enemy in enemies:
                draw_enemy(enemy['x'], enemy['y'])
            if boss_appears and boss:
                draw_boss(boss['x'], boss['y'], boss['health'])

            pygame.display.flip()
            clock.tick(30)  # Frame rate


if __name__ == "__main__":
    main()
