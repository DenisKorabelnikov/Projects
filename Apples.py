"""
В планах изменить:
    - Начинать игру при нажатии на пробел
    - Заменить платформу и яблоки на картинки
    - С увеличением score повышать сложность:
        Увеличение скорости яблок
        Увеличение разброса между стартовой позицией яблок
    - Хранить таблицу рекордов (отображать слева при паузе)
"""

import pygame
import random
import copy


def print_text(s, score="", color=(255, 0, 0)):
    global WIDTH, HEIGHT
    base_font_size = 74
    font_size = int(base_font_size * (WIDTH / 600 + HEIGHT / 400) / 2)

    font = pygame.font.Font(None, font_size)
    text = font.render(s + str(score), True, color)
    text_rect = text.get_rect()
    text_rect.center = (sc.get_width() // 2, sc.get_height() // 2)
    sc.blit(text, text_rect)
    pygame.display.flip()


def update_object_sizes(OLD_WIDTH=None, OLD_HEIGHT=None, first=0):
    global WIDTH_PLAT, HEIGHT_PLAT, RAD_APPLE, SPEED_PLAT, SPEED_APPLE, Y_PLAT, X_PLAT
    scale_factor = (WIDTH / 600 + HEIGHT / 400) / 2  # Средний коэффициент изменения

    WIDTH_PLAT = int(BASE_WIDTH_PLAT * scale_factor)
    HEIGHT_PLAT = int(BASE_HEIGHT_PLAT * scale_factor)
    RAD_APPLE = int(BASE_RAD_APPLE * scale_factor)
    SPEED_PLAT = int(BASE_SPEED_PLAT * scale_factor)
    SPEED_APPLE = int(BASE_SPEED_APPLE * scale_factor)

    Y_PLAT = HEIGHT - HEIGHT_PLAT * 2
    X_PLAT = WIDTH // 2

    if not first:
        for i in range(len(apples)):
            apples[i][0] = int(apples[i][0] * (WIDTH / OLD_WIDTH))
            apples[i][1] = int(apples[i][1] * (HEIGHT / OLD_HEIGHT))


def draw_figure():
    sc.fill((255, 255, 255))
    for i in range(len(apples)):
        pygame.draw.circle(sc, COLOR_APPLE, apples[i], RAD_APPLE)

    pygame.draw.rect(
        sc,
        COLOR_PLAT,
        (X_PLAT - WIDTH_PLAT // 2, HEIGHT - HEIGHT_PLAT * 2, WIDTH_PLAT, HEIGHT_PLAT),
    )


pygame.init()

WIDTH = 600
HEIGHT = 400

# Базовые настройки
BASE_WIDTH_PLAT = 100
BASE_HEIGHT_PLAT = 15
BASE_RAD_APPLE = 15
BASE_SPEED_PLAT = 5
BASE_SPEED_APPLE = 3

update_object_sizes(first=1)
COLOR_PLAT = (128, 128, 128)
COLOR_APPLE = (0, 204, 0)
FPS = 60
apples = []
score = 0
pause = False
game_over = False
timer_for_apple = 0

flags = pygame.RESIZABLE | pygame.DOUBLEBUF
sc = pygame.display.set_mode((WIDTH, HEIGHT), flags)
sc.fill((255, 255, 255))
pygame.display.update()
clock = pygame.time.Clock()
pygame.display.set_caption("Apples game")

pygame.draw.rect(sc, COLOR_PLAT, (X_PLAT - WIDTH_PLAT // 2, Y_PLAT, WIDTH_PLAT, HEIGHT_PLAT))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        # Обновление размеров объектов при изменении окна
        if event.type == pygame.VIDEORESIZE:
            OLD_WIDTH, OLD_HEIGHT = WIDTH, HEIGHT
            WIDTH, HEIGHT = event.w, event.h
            sc = pygame.display.set_mode((WIDTH, HEIGHT), flags)
            sc.fill((255, 255, 255))
            update_object_sizes(OLD_WIDTH, OLD_HEIGHT)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            pause = not pause

    if any(y + RAD_APPLE >= HEIGHT for x, y in apples):
        print_text("GAME OVER")
        game_over = True
        continue

    if not game_over:
        if pause:
            draw_figure()
            print_text("SCORE: ", score, (0, 203, 0))
            continue

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and X_PLAT - WIDTH_PLAT // 2 > HEIGHT_PLAT:
                X_PLAT -= SPEED_PLAT
            elif keys[pygame.K_RIGHT] and X_PLAT + WIDTH_PLAT // 2 < WIDTH - HEIGHT_PLAT:
                X_PLAT += SPEED_PLAT

        timer_for_apple += 1
        if timer_for_apple == 100:
            X_APPLE = random.randint(HEIGHT_PLAT + RAD_APPLE, WIDTH - HEIGHT_PLAT - RAD_APPLE)
            Y_APPLE = 1
            apples.append([X_APPLE, Y_APPLE])
            pygame.draw.circle(sc, COLOR_APPLE, (X_APPLE, Y_APPLE), RAD_APPLE)
            timer_for_apple = 0

        for i in range(len(apples)):
            apples[i][1] += SPEED_APPLE

        copied_apples = copy.deepcopy(apples)
        for x, y in apples:
            if y + RAD_APPLE >= Y_PLAT and (
                x + RAD_APPLE >= X_PLAT - WIDTH_PLAT // 2
                and x - RAD_APPLE <= X_PLAT + WIDTH_PLAT // 2
            ):
                if [x, y] in apples:
                    score += 1
                    print(score)
                    apples.remove([x, y])

        draw_figure()
        pygame.display.update()

        clock.tick(FPS)
