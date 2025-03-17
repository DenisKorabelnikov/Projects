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


class Game:
    def __init__(self):
        self.WIDTH = 600
        self.HEIGHT = 400

        self.base_width_plat = 100
        self.base_height_plat = 15
        self.base_rad_apple = 15
        self.base_speed_plat = 5
        self.base_speed_apple = 3

        self.fps = 60
        self.first_game = True
        self.pause = False
        self.timer_for_apple = 0
        self.score = 0

        self.update_object_sizes()

        pygame.init()
        self.flags = pygame.RESIZABLE | pygame.DOUBLEBUF
        self.sc = pygame.display.set_mode((self.WIDTH, self.HEIGHT), self.flags)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Apples game")

    # Основной цикл программы
    def run(self):
        try:
            with sqlite3.connect("database\\records.db") as self.conn:
                self.init_database()
                while True:
                    self.management()
                    if self.first_game:
                        self.print_text('Press "Space" for start game', ColorText.GREEN)
                        continue

                    self.draw_figure()
                    if any(
                        y + self.base_rad_apple >= self.HEIGHT for x, y in self.apples
                    ):
                        self.print_text("GAME OVER", ColorText.RED)
                    elif self.pause:
                        self.print_text(f"SCORE: {self.score}", ColorText.GREEN)
                    else:
                        self.game_logic()
                        self.clock.tick(self.fps)
                    pygame.display.update()

        except sqlite3.OperationalError as e:
            print(f"OperationalError: {e}")

    # Управление игрой и изменение размеров окна
    def management(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.db_add_record()
                exit()

            # Обновление размеров объектов при изменении окна
            if event.type == pygame.VIDEORESIZE:
                self.old_width, self.old_height = self.WIDTH, self.HEIGHT
                self.WIDTH, self.HEIGHT = event.w, event.h
                self.sc = pygame.display.set_mode((self.WIDTH, self.HEIGHT), self.flags)
                self.update_object_sizes()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.first_game:
                        self.first_game = False
                        self.apples = []
                        self.score = 0
                    else:
                        self.pause = not self.pause
                if event.key == pygame.K_r:
                    self.first_game = True
                    self.pause = False
                    self.apples = []
                    self.x_plat = self.WIDTH // 2
                    self.db_add_record()
                    self.score = 0

    # Отображение счёта в левом верхнем углу во время игры
    def print_score(self):
        score_size = int(30 * (self.WIDTH / 600 + self.HEIGHT / 400) / 2)
        score_font = pygame.font.Font(None, score_size)
        score_text = score_font.render(str(self.score), True, ColorText.BLUE)
        a = int(10 * (self.WIDTH / 600 + self.HEIGHT / 400) / 2)
        self.sc.blit(score_text, (a, a))

    # Отображение текста
    def print_text(self, s, color):
        base_font_size = 60
        font_size = int(base_font_size * (self.WIDTH / 600 + self.HEIGHT / 400) / 2)

        font = pygame.font.Font(None, font_size)
        text = font.render(s, True, color)
        text_rect = text.get_rect()

        center_x = self.sc.get_width() // 2
        center_y_first_game = self.sc.get_height() * 0.15
        center_y_second_game = self.sc.get_height() // 2

        if self.first_game:
            self.sc.fill(ColorText.WHITE)
            text_rect.center = (center_x, center_y_first_game)
            self.sc.blit(text, text_rect)

            record_score_size = int(font_size * 0.8)
            record_score_font = pygame.font.Font(None, record_score_size)
            records_header = record_score_font.render("Records:", True, color)
            shift = text_rect.height + self.base_rad_apple // 2

            header_rect = records_header.get_rect(
                center=(center_x, center_y_first_game + shift)
            )
            self.sc.blit(records_header, header_rect)

            self.cur.execute("SELECT score FROM Records ORDER BY score DESC LIMIT 5")
            for i, row in enumerate(self.cur.fetchall()):
                record_score_text = record_score_font.render(str(row[0]), True, color)
                record_score_rect = record_score_text.get_rect(
                    center=(center_x, (self.sc.get_height() * 0.25) + shift)
                )
                self.sc.blit(record_score_text, record_score_rect)
                shift += header_rect.height
        else:
            text_rect.center = (center_x, center_y_second_game)
            self.sc.blit(text, text_rect)

        pygame.display.flip()

    # Изменение всех размеров и координат при изменении размеров окна
    def update_object_sizes(self):
        # Коэффициент изменения
        scale_factor = (self.WIDTH / 600 + self.HEIGHT / 400) / 2

        self.width_plat = int(self.base_width_plat * scale_factor)
        self.height_plat = int(self.base_height_plat * scale_factor)
        self.rad_apple = int(self.base_rad_apple * scale_factor)
        self.speed_plat = int(self.base_speed_plat * scale_factor)
        self.speed_apple = int(self.base_speed_apple * scale_factor)

        self.y_plat = self.HEIGHT - self.height_plat * 2
        self.x_plat = self.WIDTH // 2

        if not self.first_game and self.old_width and self.old_height:
            for i in range(len(self.apples)):
                self.apples[i][0] = int(
                    self.apples[i][0] * (self.WIDTH / self.old_width)
                )
                self.apples[i][1] = int(
                    self.apples[i][1] * (self.HEIGHT / self.old_height)
                )

    # Управление платформой
    def plat_action(self):
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_LEFT]
            and self.x_plat - self.width_plat // 2 > self.height_plat
        ):
            self.x_plat -= self.speed_plat
        elif (
            keys[pygame.K_RIGHT]
            and self.x_plat + self.width_plat // 2 < self.WIDTH - self.height_plat
        ):
            self.x_plat += self.speed_plat

    # Отрисовка всех фигур, в том числе счёта в левом верхнему углу (кроме текста)
    def draw_figure(self):
        self.sc.fill(ColorText.WHITE)
        for i in range(len(self.apples)):
            pygame.draw.circle(
                self.sc, ColorText.COLOR_APPLE, self.apples[i], self.rad_apple
            )

        pygame.draw.rect(
            self.sc,
            ColorText.COLOR_PLAT,
            (
                self.x_plat - self.width_plat // 2,
                self.HEIGHT - self.height_plat * 2,
                self.width_plat,
                self.height_plat,
            ),
        )

        self.print_score()

    # Логика работы игры (Появление и падение яблок. Определение, попало ли яблоко на платформу)
    def game_logic(self):
        self.plat_action()

        self.timer_for_apple += 1
        if self.timer_for_apple == 100:
            x_apple = random.randint(
                self.base_height_plat + self.rad_apple,
                self.WIDTH - self.base_height_plat - self.rad_apple,
            )
            self.apples.append([x_apple, 0])
            pygame.draw.circle(
                self.sc, ColorText.COLOR_APPLE, (x_apple, 0), self.rad_apple
            )
            self.timer_for_apple = 0

        for i in range(len(self.apples)):
            self.apples[i][1] += self.speed_apple

        for x, y in self.apples[:]:
            if (
                y + self.rad_apple >= self.y_plat
                and x + self.rad_apple >= self.x_plat - self.width_plat // 2
                and x - self.rad_apple <= self.x_plat + self.width_plat // 2
            ):
                if [x, y] in self.apples:
                    self.score += 1
                    self.apples.remove([x, y])

    # Инициализация базы данных
    def init_database(self):
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
        CREATE TABLE IF NOT EXISTS Records (
        id INTEGER PRIMARY KEY,
        score INTEGER NOT NULL DEFAULT 0
        )            
        """
        )

    # Запись новых рекордов в БД и удаление старых
    def db_add_record(self):
        if self.score > 0:
            self.cur.execute("INSERT INTO Records (score) VALUES (?)", (self.score,))
            self.conn.commit()

            # Лимит хранимых записей в БД
            max_records = 5
            self.cur.execute(
                "DELETE FROM Records WHERE id NOT IN (SELECT id FROM Records ORDER BY score DESC LIMIT ?)",
                (max_records,),
            )
            self.conn.commit()


if __name__ == "__main__":
    game = Game()
    game.run()
