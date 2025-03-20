"""
Дорисовать новое меню и сделать кнопки рабочими
Добавить выделение тех кнопок, которые активны на данный момент

В будущем попробовать переписать логику изменения масштаба, чтобы при его изменении в середине рабочей области - сохранять текущее положение рисунка
"""

import pygame


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
        self.fps = 60
        self.size = 12
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
        
        self.drawing = False
        self.down_scroll_bar_active = False
        self.down_scroll_bar_draw = False
        self.right_scroll_bar_active = False
        self.right_scroll_bar_draw = False
        self.last_surface = None
        self.brush_color = Color.BLACK
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
        elif 20 <= x <= self.WIDTH - 20 and 120 <= y <= self.HEIGHT - 20:
            self.drawing = True
            self.last_surface = pygame.Surface((self.WIDTH_SHEET, self.HEIGHT_SHEET), pygame.SRCALPHA)
            self.last_surface.fill((*Color.WHITE, 0))
            pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift(pos), self.size, self.size))
        
        # Нажатие на палитру цветов
        elif 150 <= x <= 293 and 14 <= y <= 85:
            self.change_color(pos)

    def handle_mouse_motion(self, pos):
        x, y = pos
        if 0 < x - 20 <= self.WIDTH_SHEET and 0 < y - 120 <= self.HEIGHT_SHEET:
            if self.drawing:
                pygame.draw.rect(self.last_surface, self.brush_color, (*self.shift(pos), self.size, self.size))
        
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
        

if __name__ == "__main__":
    Paint().run()
