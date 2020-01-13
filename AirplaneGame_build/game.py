import pygame
import os
import sys
import random


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    return image


def load_sound(name):
    return os.path.join('data\\music', name)


def load_level(filename):
    filename = "data/map/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    new_level = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    new_level[len(new_level) - 1] = 'E...................'

    ships = []
    for i in range(len(new_level)):
        a = []
        b = list(range(3, 14, 2))
        for j in range(random.randint(0, 1)):
            n = random.choice(b)
            b.remove(n)
            a.append(n)
        ships.append(a)
    trees = []
    for i in range(len(new_level)):
        a = []
        b = list(range(0, 3)) + list(range(18, 20))
        c = random.choice([0, 0, 0, 0, 1, 1, 2])
        for j in range(c):
            n = random.choice(b)
            b.remove(n)
            a.append(n)
        trees.append(a)
    for y in range(len(new_level)):
        for j in ships[y]:
            temp = list(new_level[y])
            temp[j] = 'S'
            new_level[y] = ''.join(temp)
        if trees[y] is not None:
            for j in trees[y]:
                temp = list(new_level[y])
                temp[j] = 'T'
                new_level[y] = ''.join(temp)
    return new_level


def game_over():
    global is_game_win
    screen.fill(COLORS['water'])
    all_sprites = pygame.sprite.Group()
    sound_gameover.play()
    if is_game_win:
        image = load_image('Youwon.png')
        color = (0, 255, 0)
    else:
        image = load_image('gameover.png')
        color = (255, 0, 0)
    sprite = pygame.sprite.Sprite()
    sprite.image = image
    sprite.rect = sprite.image.get_rect()
    all_sprites.add(sprite)
    v = 300
    sprite.rect.x = -600
    sprite.rect.y = 0

    while True:
        all_sprites.draw(screen)
        all_sprites.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        if sprite.rect.x <= 0:
            sprite.rect.x += v // FPS
        else:
            font = pygame.font.Font(None, 100)
            text = font.render("Score: " + str(player.score), 1, color)
            text_x = 7
            text_y = 327
            screen.blit(text, (text_x, text_y))
            text = font.render("Score: " + str(player.score), 1, color)
            text_x = 3
            text_y = 323
            screen.blit(text, (text_x, text_y))
            text = font.render("Score: " + str(player.score), 1, color)
            text_x = 7
            text_y = 323
            screen.blit(text, (text_x, text_y))
            text = font.render("Score: " + str(player.score), 1, color)
            text_x = 3
            text_y = 327
            screen.blit(text, (text_x, text_y))
            text = font.render("Score: " + str(player.score), 1, (0, 0, 0))
            text_x = 5
            text_y = 325
            screen.blit(text, (text_x, text_y))
        clock.tick(FPS)
        pygame.display.flip()
        screen.fill(COLORS['water'])


class Player(pygame.sprite.Sprite):
    def __init__(self, xx, yy, v):
        super().__init__()
        self.images = [player_idle, player_left, player_right]
        self.v = 5
        self.score = 0
        self.state = IDLE
        self.image = self.images[self.state]
        self.rect = pygame.Rect(xx, yy, width, height)
        self.score_add(0)

    def update(self, k):
        global is_game_over
        if k[pygame.K_a]:
            self.rect.x -= self.v
            self.state = LEFT
        elif k[pygame.K_d]:
            self.rect.x += self.v
            self.state = RIGHT
        elif not k[pygame.K_LEFT] and not k[pygame.K_RIGHT]:
            self.state = IDLE
        self.image = self.images[self.state]
        if pygame.sprite.spritecollide(self, enemy_group, False) or self.rect.x > 455 or self.rect.x < 90:
            create_particles((self.rect.x, self.rect.y))
            is_game_over = True

    def shoot(self):
        sound_shoot.play()
        Bullet(4, self.rect.x + 21, self.rect.y - 5)

    def score_add(self, a):
        self.score += a


class Bullet(pygame.sprite.Sprite):
    def __init__(self, radius, xx, yy):
        super().__init__(bullet_group)
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, COLORS['bullet'], (radius, radius), radius)
        self.rect = pygame.Rect(xx, yy, 2 * radius, 2 * radius)
        self.v = -8

    def update(self):
        self.rect = self.rect.move(0, self.v)
        if self.rect.y < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, enemy_group, False):
            create_particles((self.rect.x, self.rect.y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, xx, yy, t):
        super().__init__(enemy_group)
        self.t = t
        self.image = images[t]
        self.rect = self.image.get_rect().move(30 * xx, 50 * yy)

    def update(self):
        global objects_speed
        self.rect.y += objects_speed
        if pygame.sprite.spritecollide(self, bullet_group, True):
            if self.t == 'S':
                player.score_add(10)
            sound_explosion.play()
            self.kill()


class End(Enemy):
    def update(self):
        global is_game_over
        global is_game_win
        global objects_speed
        self.rect.y += objects_speed
        if self.rect.y >= 350:
            is_game_win = True
            is_game_over = True


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image('Particle.png')]
    for scale in (1, 2, 3):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particle_group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.rect2 = pygame.rect.Rect((pos[0] - 50, pos[1] - 50), (100, 100))

        self.velocity = [dx, dy]

        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.y += objects_speed
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.rect2):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 10
    # возможные скорости
    numbers = range(-2, 2)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def start_menu():
    pygame.mixer.music.load(load_sound('mainmusic.mp3'))
    pygame.mixer.music.play()

    title = load_image('Title.png')
    title_sprite = pygame.sprite.Sprite()
    press_space_image = load_image('press_space.png')
    title_group = pygame.sprite.Group()
    title_sprite.image = title
    title_sprite.rect = title_sprite.image.get_rect()
    title_group.add(title_sprite)
    title_sprite.rect.x = 600
    title_sprite.rect.y = 0
    v = 10
    text_group = pygame.sprite.Group()
    text_sprite = pygame.sprite.Sprite()
    text_sprite.image = press_space_image
    text_sprite.rect = text_sprite.image.get_rect()
    text_group.add(text_sprite)
    screen2 = pygame.Surface((600, 100))
    screen2.fill(COLORS['water'])
    image_on = False
    elapsed_time = -800

    while True:
        title_group.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and title_sprite.rect.x <= 10:
                if event.key == pygame.K_SPACE:
                    return
        elapsed_time += clock.tick(FPS)
        if elapsed_time > 500:
            image_on = not image_on
            if image_on:
                elapsed_time = -200
            else:
                elapsed_time = 0
        if image_on:
            text_group.draw(screen2)
        else:
            screen2.fill(COLORS['water'])
        title_group.draw(screen)
        if title_sprite.rect.x >= 10:
            title_sprite.rect.x -= v
        screen.blit(screen2, (0, 350))
        pygame.display.flip()
        screen.fill(COLORS['water'])
        clock.tick(FPS)


def generate_level(level):
    for y in range(len(level) - 1, 0, -1):
        for x in range(len(level[y])):
            if level[y][x] == 'S':
                Enemy(x, -y, 'S')
            elif level[y][x] == 'T':
                Enemy(x, -y, 'T')
            elif level[y][x] == 'E':
                End(x, -y, 'E')


def draw_window():
    screen.fill(COLORS['water'])
    rect = pygame.draw.rect(screen, COLORS['edge'], ((0, 0), (90, 450)), 10)
    screen.fill(COLORS['dirt'], rect)
    rect2 = pygame.draw.rect(screen, COLORS['edge'], ((510, 0), (90, 450)), 10)
    screen.fill(COLORS['dirt'], rect2)
    player_group.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)
    particle_group.draw(screen)

    text = font.render("Score: " + str(player.score), 1, (255, 255, 255))
    text_x = 0
    text_y = 420
    screen.blit(text, (text_x, text_y))


def main():
    start_menu()

    global is_game_over
    global objects_speed
    running = True
    lvl = load_level('2.txt')
    generate_level(lvl)
    pygame.mixer.music.pause()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_w:
                    objects_speed = 4
                elif event.key == pygame.K_s:
                    objects_speed = 2
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    objects_speed = 3
        if is_game_over:
            running = False
            game_over()

        keys = pygame.key.get_pressed()
        player_group.update(keys)
        bullet_group.update()
        enemy_group.update()
        particle_group.update()
        clock.tick(FPS)

        draw_window()

        pygame.display.flip()


pygame.init()
font = pygame.font.Font(None, 30)
SIZE = (600, 450)
screen_rect = (0, 0, SIZE[0], SIZE[1])
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Air Destroyer")
FPS = 60
clock = pygame.time.Clock()
COLORS = {'dirt': (53, 95, 24), 'water': (47, 50, 182), 'bullet': (255, 0, 0), 'edge': (125, 44, 0),
          'particle': (229, 189, 48)}
player_idle = load_image("Airplane_idle.png")
player_left = load_image("Airplane_left.png")
player_right = load_image("Airplane_right.png")

sound_gameover = pygame.mixer.Sound(load_sound('gameovermusic.wav'))
sound_explosion = pygame.mixer.Sound(load_sound('explosion.wav'))
sound_shoot = pygame.mixer.Sound(load_sound('shoot.wav'))
sound_shoot.set_volume(0.8)

v = 5
player_x = 275
player_y = 400
width = 50
height = 45
IDLE = 0
LEFT = 1
RIGHT = 2
state = IDLE
player = Player(player_x, player_y, v)

player_group = pygame.sprite.Group(player)
bullet_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

end = pygame.Surface((600, 50), pygame.SRCALPHA, 32)
end_line = pygame.draw.rect(end, (255, 255, 255, 0), ((0, 50), (600, -50)))
images = {'S': load_image('Ship.png'), 'T': load_image('Tree.png'), 'E': end}
objects_speed = 3

is_game_over = False
is_game_win = False

main()
terminate()
