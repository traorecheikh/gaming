import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Spaceship Game")

# Load images and scale them
def load_and_scale_image(file_name, width, height):
    image = pygame.image.load(file_name)
    return pygame.transform.scale(image, (width, height))

background_image = load_and_scale_image('background.jpg', SCREEN_WIDTH, SCREEN_HEIGHT)
spaceship_image = load_and_scale_image('player.png', 50, 30)  # Example sizes, adjust as needed
enemy_image = load_and_scale_image('enemy.png', 50, 50)  # Example sizes, adjust as needed

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
bullet_speed = 7
enemy_speed = 2
enemy_spawn_rate = 25
enemy_health = 3
special_ex_max = 100
special_ex_fill_rate = 5
score = 0
highscore = 0
wave = 1
game_active = False

# Initialize clock
clock = pygame.time.Clock()

# Initialize fonts
font = pygame.font.Font(None, 36)

# Initialize lists
bullets = []
enemies = []

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

def update_bullets():
    global bullets
    for bullet in bullets[:]:
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
                        explosion_sound.play()
                    break

def update_enemies():
    global enemies, score
    for enemy in enemies[:]:
        enemy['y'] += enemy_speed
        if enemy['y'] > SCREEN_HEIGHT:
            enemies.remove(enemy)
            return True
        if random.randint(1, 100) <= 2:
            bullets.append({'x': enemy['x'] + ENEMY_WIDTH // 2 - BULLET_WIDTH // 2, 'y': enemy['y'] + ENEMY_HEIGHT, 'is_enemy': True})
        for bullet in bullets[:]:
            if bullet.get('is_enemy'):
                bullet['y'] += bullet_speed
                if bullet['y'] > SCREEN_HEIGHT:
                    bullets.remove(bullet)
                elif (spaceship_x < bullet['x'] < spaceship_x + SPACESHIP_WIDTH or spaceship_x < bullet['x'] + BULLET_WIDTH < spaceship_x + SPACESHIP_WIDTH) and (spaceship_y < bullet['y'] < spaceship_y + SPACESHIP_HEIGHT or spaceship_y < bullet['y'] + BULLET_HEIGHT < spaceship_y + SPACESHIP_HEIGHT):
                    return True
    return False

def draw_special_ex_bar(special_ex):
    pygame.draw.rect(screen, WHITE, (10, SCREEN_HEIGHT - 20, special_ex_max, 10))
    pygame.draw.rect(screen, (0, 255, 0), (10, SCREEN_HEIGHT - 20, special_ex, 10))

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

def main():
    global spaceship_x, spaceship_y, bullets, enemies, special_ex, game_active, wave, highscore

    spaceship_x = SCREEN_WIDTH // 2 - SPACESHIP_WIDTH // 2
    spaceship_y = SCREEN_HEIGHT - SPACESHIP_HEIGHT - 10
    special_ex = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not game_active:
                    game_active = True
                    score = 0
                    wave = 1
                    enemies = []
                    special_ex = 0
                    start_music.play(-1)
                if event.key == pygame.K_SPACE and special_ex >= special_ex_max:
                    special_ex = 0
                    deathray_sound.play()
                    enemies = []

        if game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                spaceship_x -= spaceship_speed
            if keys[pygame.K_RIGHT]:
                spaceship_x += spaceship_speed
            if keys[pygame.K_SPACE] and special_ex < special_ex_max:
                bullets.append({'x': spaceship_x + SPACESHIP_WIDTH // 2 - BULLET_WIDTH // 2, 'y': spaceship_y})
                laser_sound.play()

            spaceship_x = max(0, min(spaceship_x, SCREEN_WIDTH - SPACESHIP_WIDTH))

            if random.randint(1, enemy_spawn_rate) == 1:
                x = random.randint(0, max(SCREEN_WIDTH - ENEMY_WIDTH, 0))  # Ensure valid range
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
            draw_special_ex_bar(special_ex)

            draw_text(f'Score: {score}', font, WHITE, screen, 70, 20)
            draw_text(f'Wave: {wave}', font, WHITE, screen, SCREEN_WIDTH - 70, 20)

            pygame.display.flip()
            clock.tick(60)

        else:
            draw_start_menu()
            pygame.display.flip()

        if not game_active and pygame.event.get(pygame.QUIT):
            pygame.quit()
            return

        if not game_active and pygame.time.get_ticks() % 3000 < 1000:
            draw_game_over()
            pygame.display.flip()
            pygame.time.wait(3000)

if __name__ == "__main__":
    main()
