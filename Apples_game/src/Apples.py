"""
Запускать программу из Git_projects\Apples_game
В планах изменить:
    - Заменить платформу и яблоки на картинки
        (Для этого необходимо переписать логику вычисления координат)
    - С увеличением score повышать сложность:
        Увеличение скорости яблок
        Увеличение разброса между стартовой позицией яблок
"""

import pygame
import random
import sqlite3


class ColorText:
    RED = (255, 0, 0)
    GREEN = (0, 203, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    COLOR_PLAT = (128, 128, 128)
    COLOR_APPLE = (0, 204, 0)


def print_score():
    score_size = int(30 * (WIDTH / 600 + HEIGHT / 400) / 2)
    score_font = pygame.font.Font(None, score_size)
    score_text = score_font.render(str(score), True, ColorText.BLUE)
    a = int(10 * (WIDTH / 600 + HEIGHT / 400) / 2)
    sc.blit(score_text, (a, a))


def print_text(s, score="", color=ColorText.RED, start=False):
    global WIDTH, HEIGHT
    base_font_size = 60
    font_size = int(base_font_size * (WIDTH / 600 + HEIGHT / 400) / 2)

    font = pygame.font.Font(None, font_size)
    text = font.render(s + str(score), True, color)
    text_rect = text.get_rect()

    if start:
        sc.fill(ColorText.WHITE)
        text_rect.center = (sc.get_width() // 2, sc.get_height() * 0.15)
        sc.blit(text, text_rect)

        record_score_size = int(font_size * 0.8)
        record_score_font = pygame.font.Font(None, record_score_size)
        records_header = record_score_font.render("Records:", True, color)
        shift = text_rect.height + RAD_APPLE // 2
        header_rect = records_header.get_rect(
            center=(sc.get_width() // 2, sc.get_height() * 0.15 + shift)
        )
        sc.blit(records_header, header_rect)

        cur.execute("SELECT score FROM Records ORDER BY score DESC LIMIT 5")
        for i, row in enumerate(cur.fetchall()):
            record_score_text = record_score_font.render(str(row[0]), True, color)
            record_score_rect = record_score_text.get_rect(
                center=(sc.get_width() // 2, (sc.get_height() * 0.25) + shift)
            )
            sc.blit(record_score_text, record_score_rect)
            shift += header_rect.height
    else:
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
    global WIDTH, HEIGHT
    sc.fill((255, 255, 255))
    for i in range(len(apples)):
        pygame.draw.circle(sc, ColorText.COLOR_APPLE, apples[i], RAD_APPLE)

    pygame.draw.rect(
        sc,
        ColorText.COLOR_PLAT,
        (X_PLAT - WIDTH_PLAT // 2, HEIGHT - HEIGHT_PLAT * 2, WIDTH_PLAT, HEIGHT_PLAT),
    )

    print_score()


def db_add_record(cur, conn, score):
    if score > 0:
        cur.execute("INSERT INTO Records (score) VALUES (?)", (score,))
        conn.commit()


try:
    with sqlite3.connect("database\\records.db") as conn:
        cur = conn.cursor()
        pygame.init()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS Records (
        id INTEGER PRIMARY KEY,
        score INTEGER NOT NULL DEFAULT 0
        )            
        """
        )

        WIDTH = 600
        HEIGHT = 400

        # Базовые настройки
        BASE_WIDTH_PLAT = 100
        BASE_HEIGHT_PLAT = 15
        BASE_RAD_APPLE = 15
        BASE_SPEED_PLAT = 5
        BASE_SPEED_APPLE = 3

        update_object_sizes(first=1)

        FPS = 60
        first_game = True
        pause = False
        game_over = False

        timer_for_apple = 0
        score = 0

        flags = pygame.RESIZABLE | pygame.DOUBLEBUF
        sc = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        sc.fill(ColorText.WHITE)
        clock = pygame.time.Clock()
        pygame.display.set_caption("Apples game")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    db_add_record(cur, conn, score)
                    exit()

                # Обновление размеров объектов при изменении окна
                if event.type == pygame.VIDEORESIZE:
                    OLD_WIDTH, OLD_HEIGHT = WIDTH, HEIGHT
                    WIDTH, HEIGHT = event.w, event.h
                    sc = pygame.display.set_mode((WIDTH, HEIGHT), flags)
                    # sc.fill(ColorText.WHITE)
                    update_object_sizes(OLD_WIDTH, OLD_HEIGHT)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if first_game:
                            first_game = False
                            apples = []
                            score = 0
                        else:
                            pause = not pause
                    if event.key == pygame.K_r:
                        first_game = True
                        game_over = False
                        pause = False
                        apples = []
                        X_PLAT = WIDTH // 2
                        score = 0
                        db_add_record(cur, conn, score)

            if first_game:
                print_text(
                    'Press "Space" for start game', color=ColorText.GREEN, start=True
                )
                continue

            draw_figure()
            if any(y + RAD_APPLE >= HEIGHT for x, y in apples):
                print_text("GAME OVER")
                game_over = True
                continue

            if not game_over:
                if pause:
                    print_text("SCORE: ", score, ColorText.GREEN)
                    continue

                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT] and X_PLAT - WIDTH_PLAT // 2 > HEIGHT_PLAT:
                        X_PLAT -= SPEED_PLAT
                    elif (
                        keys[pygame.K_RIGHT]
                        and X_PLAT + WIDTH_PLAT // 2 < WIDTH - HEIGHT_PLAT
                    ):
                        X_PLAT += SPEED_PLAT

                timer_for_apple += 1
                if timer_for_apple == 100:
                    X_APPLE = random.randint(
                        HEIGHT_PLAT + RAD_APPLE, WIDTH - HEIGHT_PLAT - RAD_APPLE
                    )
                    Y_APPLE = 1
                    apples.append([X_APPLE, Y_APPLE])
                    pygame.draw.circle(
                        sc, ColorText.COLOR_APPLE, (X_APPLE, Y_APPLE), RAD_APPLE
                    )
                    timer_for_apple = 0

                for i in range(len(apples)):
                    apples[i][1] += SPEED_APPLE

                for x, y in apples[:]:
                    if y + RAD_APPLE >= Y_PLAT and (
                        x + RAD_APPLE >= X_PLAT - WIDTH_PLAT // 2
                        and x - RAD_APPLE <= X_PLAT + WIDTH_PLAT // 2
                    ):
                        if [x, y] in apples:
                            score += 1
                            apples.remove([x, y])

                pygame.display.update()
                clock.tick(FPS)

except sqlite3.OperationalError as e:
    print(f"OperationalError: {e}")
