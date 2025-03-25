"""
Отображать, что сохранение файла выполнено
Пофиксить прерывание карандаша

В будущем попробовать переписать логику изменения масштаба, чтобы при его изменении в середине рабочей области - сохранять текущее положение рисунка
"""

import pygame
import math
import numpy as np
import os


class Color:
    HEAD_BACK = (245,246,248)
    BACK = (202,211,226)
    RED = (234,28,33)
    GREEN = (34,176,78)
    BLUE = (59,72,202)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    SCROLL_BAR_NOT_ACTIVE =  (164,168,177)
    SCROLL_BAR_ACTIVE = (100,104,112)
    colors = [
            [(0, 0, 0), (126, 126, 126), (194, 194, 194), (255, 255, 255), (133, 2, 18), (241, 26, 41)],
            [(109, 148, 187), (64, 70, 208), (255, 173, 201), (255, 201, 15), (246, 132, 35), (179, 125, 87)],
            [(4, 161, 228), (152, 218, 232), (253, 245, 0), (239, 227, 177), (184, 227, 33), (39, 174, 82)]
        ]


class Paint:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1000
        self.HEIGHT = 800
        self.WIDTH_SHEET = self.WIDTH - 2 * 20
        self.HEIGHT_SHEET = self.HEIGHT - 100 - 2 * 20
        self.size = 12
        self.saving_size = (3840, 2640)
        self.fps = 60
        self.scroll_bar_width = 10
        
        self.right_scroll_bar_color = Color.SCROLL_BAR_NOT_ACTIVE
        self.down_scroll_bar_color = Color.SCROLL_BAR_NOT_ACTIVE

        self.flags = pygame.RESIZABLE  | pygame.DOUBLEBUF
        self.sc = pygame.display.set_mode((self.WIDTH, self.HEIGHT), self.flags)
        pygame.display.set_caption("MyPaint")
        self.clock = pygame.time.Clock()
        
        self.down_scroll_bar_length = self.WIDTH // 10
        self.right_scroll_bar_length = self.HEIGHT // 10
        self.right_scroll_bar_x = self.WIDTH - 15
        self.right_scroll_bar_y = 120
        self.down_scroll_bar_x = 20
        self.down_scroll_bar_y = self.HEIGHT - 15
        
        self.sheet_cur_x = 20
        self.sheet_cur_y = 120
        self.sheet_offset_x = 0
        self.sheet_offset_y = 0
        
        # Координаты кнопок меню в формате:
        # (x_start, x_end, y_start, y_end)
        self.coors = {"pencil": (14, 43, 14, 44),
                      "eraser": (14, 43, 55, 85),
                      "pipette": (306, 335, 14, 44),
                      "palette": (150, 293, 14, 85),
                      "figure_selection": (66, 137, 14, 85),
                      "save_jpg": (358, 387, 14, 44),
                      "save_png": (358, 387, 55, 85)
            }
        
        self.figure_selection = [["line", "rectangle", "ellipse"],
                               ["arc", "", ""],
                               ["", "", ""]]
        
        self.tool = "pencil"
        self.eraser = False
        self.drawing = False
        self.down_scroll_bar_active = False
        self.down_scroll_bar_draw = False
        self.right_scroll_bar_active = False
        self.right_scroll_bar_draw = False
        self.last_surface = None
        self.brush_color = self.last_color = Color.BLACK
        self.surfaces = []  # Список для хранения поверхностей

    def run(self):
        """Основной цикл программы."""
        while True:
            # try:
                self.handle_events()
                self.draw()
            # except Exception as e:
            #     print(f"Exception: {e}")
            #     break

    def handle_events(self):
        """Обработка событий.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            # Обновление размеров объектов при изменении окна
            if event.type == pygame.VIDEORESIZE:
                self.WIDTH, self.HEIGHT = event.w, event.h
                OLD_WIDTH, OLD_HEIGHT = self.WIDTH, self.HEIGHT
                self.sc = pygame.display.set_mode((self.WIDTH, self.HEIGHT), self.flags)
                
                self.down_scroll_bar_length = self.WIDTH // 10
                self.right_scroll_bar_length = self.HEIGHT // 10
                
                self.right_scroll_bar_x = self.WIDTH - 15
                self.down_scroll_bar_y = self.HEIGHT - 15
                
                if OLD_HEIGHT:
                    self.right_scroll_bar_y *= self.HEIGHT // OLD_HEIGHT
                if OLD_WIDTH:
                    self.down_scroll_bar_x *= self.WIDTH // OLD_WIDTH

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_button_down(event.pos)
            
            if event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.handle_mouse_button_up()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                self.scale_changing(0.5, event.button)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                self.scale_changing(2, event.button)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if self.surfaces:
                        self.surfaces.pop()

    def handle_mouse_button_down(self, pos):
        x, y = pos
        
        # Нажатие на правый скроллбар
        if self.down_scroll_bar_draw and self.right_scroll_bar_x <= x < self.right_scroll_bar_x + self.scroll_bar_width and self.right_scroll_bar_y <= y < self.right_scroll_bar_y + self.right_scroll_bar_length:
            self.right_scroll_bar_color = Color.SCROLL_BAR_ACTIVE
            self.right_scroll_bar_active = True
            # Смещенеие мыши относительно верхнего края скроллбара в момент нажатия
            self.right_scroll_bar_shift = y - self.right_scroll_bar_y
        
        # Нажатие на нижний скроллбар
        elif self.down_scroll_bar_draw and self.down_scroll_bar_x <= x < self.down_scroll_bar_x + self.down_scroll_bar_length and self.down_scroll_bar_y <= y < self.down_scroll_bar_y + self.scroll_bar_width:
            self.down_scroll_bar_color = Color.SCROLL_BAR_ACTIVE
            self.down_scroll_bar_active = True
            # Смещение мыши относительно левого края скроллбара в момент нажатия
            self.down_scroll_bar_shift = x - self.down_scroll_bar_x
        
        # Нажатие на рабочую область рисования
        elif 0 <= x <= self.WIDTH - 20 and 100 <= y <= self.HEIGHT - 20:           
            if self.tool == "pipette":
                for surface in self.surfaces[::-1]:
                    color = surface.get_at(self.shift(pos))
                    if color[3] > 0:
                        self.brush_color = color
                        break
            else:
                self.drawing = True
                self.last_surface = pygame.Surface((self.WIDTH_SHEET, self.HEIGHT_SHEET), pygame.SRCALPHA)
                self.last_surface.fill((0, 0, 0, 0))
                if self.tool == "pencil" or self.tool == "eraser":
                    pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift(pos), self.size, self.size))
                elif any(self.tool in row for row in self.figure_selection):
                    self.start_pos = pos
                
        # Нажатие на палитру цветов
        elif self.tool != "eraser" and self.tool != "pipette" and self.coors["palette"][0] <= x <= self.coors["palette"][1] and self.coors["palette"][2] <= y <= self.coors["palette"][3]:
            self.change_color(pos)
        
        # Выбор инструмента
        # Карандаш
        elif self.coors["pencil"][0] <= x <= self.coors["pencil"][1] and self.coors["pencil"][2] <= y <= self.coors["pencil"][3]:
            self.tools("pencil")
        # Ластик
        elif self.coors["eraser"][0] <= x <= self.coors["eraser"][1] and self.coors["eraser"][2] <= y <= self.coors["eraser"][3]:
            self.tools("eraser")
        # Пипетка
        elif self.coors["pipette"][0] <= x <= self.coors["pipette"][1] and self.coors["pipette"][2] <= y <= self.coors["pipette"][3]:
            self.tools("pipette")
        # Геометрические фигуры
        elif self.coors["figure_selection"][0] <= x <= self.coors["figure_selection"][1] and self.coors["figure_selection"][2] <= y <= self.coors["figure_selection"][3]:
            self.change_tool(pos)
            self.tools("figure_selection")
        # Сохранение в формате .jpg
        elif self.coors["save_jpg"][0] <= x <= self.coors["save_jpg"][1] and self.coors["save_jpg"][2] <= y <= self.coors["save_jpg"][3]:
            self.saving_image("jpg")
        # Сохранение в формате .png
        elif self.coors["save_png"][0] <= x <= self.coors["save_png"][1] and self.coors["save_png"][2] <= y <= self.coors["save_png"][3]:
            self.saving_image("png")

    def handle_mouse_motion(self, pos):
        if self.drawing:
            if self.tool == "pencil" or self.tool == "eraser":
                pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift(pos), self.size, self.size))
            elif self.tool == "line":
                self.draw_line(pos)
            elif self.tool == "rectangle":
                self.draw_rectangle(*self.start_pos, *pos)
            elif self.tool == "arc":
                self.draw_arc(*self.start_pos, *pos)
            elif self.tool == "ellipse":
                self.draw_ellipse(*self.start_pos, *pos)
                    
        # Движение правого скроллбара
        if self.right_scroll_bar_draw and self.right_scroll_bar_active:
            self.right_scroll_bar_y = pos[1] - self.right_scroll_bar_shift
            self.right_scroll_bar_max_y = self.HEIGHT - self.right_scroll_bar_length - 20
            self.sheet_offset_y = (self.right_scroll_bar_y - 120) / (self.right_scroll_bar_max_y - 120) * (self.HEIGHT_SHEET - (self.HEIGHT - 140))
            
            # Ограничение границ рабочей области рисования по Y
            if self.sheet_offset_y <= 0:
                self.sheet_offset_y = 0
            if self.sheet_offset_y >= self.HEIGHT - 140:
                self.sheet_offset_y = self.HEIGHT - 140
            
            # Ограничение границ правого скроллбара
            if self.right_scroll_bar_y <= 120:
                self.right_scroll_bar_y = 120
            if self.right_scroll_bar_y >= self.right_scroll_bar_max_y:
                self.right_scroll_bar_y = self.right_scroll_bar_max_y
        
        # Движение нижнего скроллбара
        if self.down_scroll_bar_draw and self.down_scroll_bar_active:
            self.down_scroll_bar_x = pos[0] - self.down_scroll_bar_shift
            self.down_scroll_bar_max_x = self.WIDTH - self.down_scroll_bar_length - 20
            self.sheet_offset_x = (self.down_scroll_bar_x - 20) / (self.down_scroll_bar_max_x - 20) * (self.WIDTH_SHEET - (self.WIDTH - 40))

            # Ограничение границ рабочей области рисования по X
            if self.sheet_offset_x <= 0:
                self.sheet_offset_x = 0
            if self.sheet_offset_x >= self.WIDTH - 40:
                self.sheet_offset_x = self.WIDTH - 40
            
            # Ограничение границ нижнего скроллбара
            if self.down_scroll_bar_x <= 20:
                self.down_scroll_bar_x = 20
            if self.down_scroll_bar_x >= self.down_scroll_bar_max_x:
                self.down_scroll_bar_x = self.down_scroll_bar_max_x

    def handle_mouse_button_up(self):
        if self.drawing:
            self.drawing = False
            self.surfaces.append(self.last_surface)
        if self.right_scroll_bar_active:
            self.right_scroll_bar_active = False
            self.right_scroll_bar_color = Color.SCROLL_BAR_NOT_ACTIVE
        if self.down_scroll_bar_active:
            self.down_scroll_bar_active = False
            self.down_scroll_bar_color = Color.SCROLL_BAR_NOT_ACTIVE

    def draw(self):
        """Отображение всех изменений
        В будущем можно выделить следующие фрагменты в отдельную функцию
        """
        self.sc.fill(Color.BACK)

        # Создание рабочей области
        self.sheet = pygame.Surface((self.WIDTH_SHEET, self.HEIGHT_SHEET))
        self.sheet.fill(Color.WHITE)
        self.sc.blit(self.sheet, (self.sheet_cur_x - self.sheet_offset_x, self.sheet_cur_y - self.sheet_offset_y))
        
        for surface in self.surfaces:
            self.sc.blit(surface, (self.sheet_cur_x - self.sheet_offset_x, self.sheet_cur_y - self.sheet_offset_y))
        
        if self.drawing and self.last_surface:
            self.sc.blit(self.last_surface, (self.sheet_cur_x - self.sheet_offset_x, self.sheet_cur_y - self.sheet_offset_y))
            
        # Заливка цветом позади меню
        self.head_back = pygame.Surface((self.WIDTH, 100))
        self.head_back.fill(Color.HEAD_BACK)
        self.sc.blit(self.head_back, (0, 0))
        
        # Меню
        self.head = pygame.image.load("..\\images\\head.png")
        self.sc.blit(self.head, (0, 0))
        
        self.active_button_surface = pygame.Surface((self.WIDTH, 100), pygame.SRCALPHA)
        self.active_button(self.tool)
        
        pygame.draw.rect(self.sc, self.brush_color, (309, 59, 24, 24))
        pygame.draw.rect(self.sc, Color.SCROLL_BAR_NOT_ACTIVE, (0, 100, self.WIDTH, 1))
        
        self.scroll_bar()
        pygame.display.flip()

    def scroll_bar(self):
        self.scroll_bar_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.scroll_bar_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.scroll_bar_surface, Color.BACK, (0, self.HEIGHT - 20, self.WIDTH, 20))
        pygame.draw.rect(self.scroll_bar_surface, Color.BACK, (self.WIDTH - 20, 101, 20, self.HEIGHT - 101))
        
        # Координаты правого скроллбара и его отображение
        if self.HEIGHT_SHEET > self.HEIGHT:
            pygame.draw.rect(self.scroll_bar_surface, self.right_scroll_bar_color, (self.right_scroll_bar_x, self.right_scroll_bar_y, self.scroll_bar_width, self.right_scroll_bar_length))
            self.right_scroll_bar_draw = True
        else:
            self.right_scroll_bar_draw = False
            self.sheet_offset_y = 0
            self.right_scroll_bar_y = 120
            
        
        # Координаты нижнего скроллбара и его отображение
        if self.WIDTH_SHEET > self.WIDTH:
            pygame.draw.rect(self.scroll_bar_surface, self.down_scroll_bar_color, (self.down_scroll_bar_x, self.down_scroll_bar_y, self.down_scroll_bar_length, self.scroll_bar_width))
            self.down_scroll_bar_draw = True
        else:
            self.down_scroll_bar_draw = False
            self.sheet_offset_x = 0
            self.down_scroll_bar_x = 20
        
        self.sc.blit(self.scroll_bar_surface, (0, 0))

    def shift(self, coors):
        """
        Производит смещение координат, полученных с event.pos.
        Это необходимо для того, чтобы рисовать на рабочей области
        (т.к. она смещена относительно окна программы)

        Параметры:
            coors (tuple): Кортеж координат от event.pos
        Возвращаемое значение:
            Кортеж со смещенными координатами
        """
        
        x, y = coors
        x = (x - (self.sheet_cur_x - self.sheet_offset_x)) // self.size * self.size
        y = (y - (self.sheet_cur_y - self.sheet_offset_y)) // self.size * self.size
        return (x, y)

    def change_color(self, pos):
        x, y = pos
        i = (x - 149) // 24
        j = (y - 13) // 24
        if 0 <= i <= 5 and 0 <= j <= 2:
            self.brush_color = Color.colors[j][i]

    def change_tool(self, pos):
        a = (pos[0] - self.coors["figure_selection"][0] - 1) // 24
        b = (pos[1] - self.coors["figure_selection"][2] - 1) // 24

        if self.figure_selection[b][a]:
            self.change_tool_x = a
            self.change_tool_y = b
            self.tool = self.figure_selection[self.change_tool_y][self.change_tool_x]

    def scale_changing(self, scale, button):
        if button == 4 or button == 5:
            self.WIDTH_SHEET //= scale
            self.HEIGHT_SHEET //= scale
            self.size //= scale
            if self.WIDTH_SHEET <= 240:
                self.WIDTH_SHEET = 240
                self.HEIGHT_SHEET = 165
                self.size = 3
            if self.WIDTH_SHEET >= 3840:
                self.WIDTH_SHEET = 3840
                self.HEIGHT_SHEET = 2640
                self.size = 48
            
            new_surfaces = []
            for surface in self.surfaces:
                new_surfaces.append(pygame.transform.scale(surface, (self.WIDTH_SHEET, self.HEIGHT_SHEET)))
            self.surfaces = new_surfaces.copy()

    def tools(self, tool):
        if tool in ("pencil", "eraser"):
            self.tool = tool
        if self.eraser and (tool == "pencil" or tool == "figure_selection"):
            self.eraser = False
            self.brush_color = self.last_color
        
        elif tool == "eraser":
            self.eraser = True
            self.last_color = self.brush_color
            self.brush_color = Color.WHITE

    def active_button(self, tool):
        if any(tool in row for row in self.figure_selection):
            pygame.draw.rect(self.active_button_surface, (*Color.colors[1][0], 50), (self.coors["figure_selection"][0] + self.change_tool_x * 24, self.coors["figure_selection"][2] + self.change_tool_y * 24, 24, 24))            
        else:
            x1, x2, y1, y2 = self.coors[f"{tool}"]
            pygame.draw.rect(self.active_button_surface, (*Color.colors[1][0], 50), (x1, y1, x2 - x1 + 1, y2 - y1 + 1))            
        self.sc.blit(self.active_button_surface, (0, 0))

    def bresenham(self, x1, y1, x2, y2):
        """Алгоритм Брезенхэма
        Генерирует координаты точек на линии от (x1, y1) до (x2, y2) по алгоритму Брезенхэма.
        Используется в программе для рисования: линии, квадрата, прямоугольника."""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            err2 = err * 2
            if err2 > -dy:
                err -= dy
                x1 += sx
            if err2 < dx:
                err += dx
                y1 += sy
        
        return points

    def draw_line(self, pos):
        self.last_surface.fill((0, 0, 0, 0))
        points = self.bresenham(*self.start_pos, *pos)

        for point in points:
            pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift(point), self.size, self.size))

    def draw_rectangle(self, x1, y1, x2, y2):
        self.last_surface.fill((0, 0, 0, 0))
        width = x2 - x1 - abs((x2 - x1) % self.size)
        height = y2 - y1 - abs((y2 - y1) % self.size)
        
        keys = pygame.key.get_pressed()
        is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if is_shift_pressed:
            width = min(abs(width), abs(height))
            width *= 1 if x2 - x1 > 0 else -1
            
            sign_y = 1 if y2 - y1 > 0 else - 1
            height = abs(width) * sign_y
            
        points = [
                (x1, y1),
                (x1 + width, y1),
                (x1 + width, y1 + height),
                (x1, y1 + height),
                (x1, y1)
            ]
        
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            line_points = self.bresenham(*start, *end)
            for point in line_points:
                pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift(point), self.size, self.size))

    def draw_arc(self, x1, y1, x2, y2):
        self.last_surface.fill((0, 0, 0, 0))
        # Радиус и центр дуги
        radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
        xc = (x1 + x2) // 2
        yc = (y1 + y2) // 2

        keys = pygame.key.get_pressed()
        is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Начальный и конечный углы в радианах
        theta_start = math.atan2(y1 - yc, x1 - xc)
        theta_end = math.atan2(y2 - yc, x2 - xc)
        
        if is_shift_pressed:
            theta_start += math.pi
            theta_end += math.pi

        if theta_end < theta_start:
            theta_end += 2 * math.pi
        # Алгоритм для рисования дуги
        for theta in np.arange(theta_start, theta_end, 0.01):
            x = int(xc + radius * math.cos(theta))
            y = int(yc + radius * math.sin(theta))
            pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift((x, y)), self.size, self.size))

    def draw_ellipse(self, x1, y1, x2, y2):
        self.last_surface.fill((0, 0, 0, 0))

        a = abs((x2 - x1) // 2)
        b = abs((y2 - y1) // 2)
        
        keys = pygame.key.get_pressed()
        is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if is_shift_pressed:
            a = b = min(a, b)
        
        a *= 1 if x2 - x1 > 0 else -1
        b *= 1 if y2 - y1 > 0 else - 1
            
        xc = x1 + a
        yc = y1 + b

        # Алгоритм для рисования эллипса
        for angle in range(0, 360):
            rad = math.radians(angle)
            x = int(a * math.cos(rad))
            y = int(b * math.sin(rad))
            
            pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift((xc + x, yc + y)), self.size, self.size))

    def saving_image(self, extension):
        full_surface = pygame.Surface(self.saving_size, pygame.SRCALPHA)
        if extension == "jpg":
            full_surface.fill((Color.WHITE))
        else:
            full_surface.fill((0, 0, 0, 0))
        
        for surface in self.surfaces:
            temp_surface = pygame.transform.scale(surface, self.saving_size)
            full_surface.blit(temp_surface, (0, 0))
        
        i = 1
        while os.path.exists(f"..\\saved_images\\drawing_{extension} ({i}).{extension}"):
            i += 1

        pygame.image.save(full_surface, f"..\\saved_images\\drawing_{extension} ({i}).{extension}")

if __name__ == "__main__":
    Paint().run()
