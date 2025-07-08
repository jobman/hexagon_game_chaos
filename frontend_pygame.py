# frontend_pygame.py
import pygame
import math
from events import EventType
# Убираем: from tile_types import TILE_PROPERTIES
# Добавляем:
from frontend_visuals import TILE_COLORS, DEFAULT_TILE_COLOR, UNIT_VISUALS, DEFAULT_UNIT_VISUAL, CITY_CENTER_COLOR, CITY_NAME_COLOR
from unit_types import UnitType
from ui.ui_manager import UIManager
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH

# Константы для отрисовки
CLICK_DRAG_THRESHOLD = 5
DEFAULT_HEX_SIZE = 30
MIN_HEX_SIZE = 10
MAX_HEX_SIZE = 60
ZOOM_SPEED = 1.1

class PygameFrontend:
    """Управляет окном, вводом и отрисовкой."""

    def __init__(self, backend):
        self.backend = backend
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hexagonal TBS")
        self.font = pygame.font.SysFont("Arial", 14)
        self.running = True
        self.selected_unit_id = None
        self.camera_offset = pygame.math.Vector2(0, 0)
        self.is_dragging = False
        self.drag_start_pos = None
        self.hex_size = DEFAULT_HEX_SIZE
        self.ui_manager = UIManager(backend)
        self.selected_object_data = None
        self.valid_moves = []
    
    def _update_selection_data(self):
        """Обновляет данные о выбранном объекте для передачи в UI."""
        if self.selected_unit_id is not None:
            self.selected_object_data = self.backend.get_game_state().units.get(self.selected_unit_id)
        # elif self.selected_city_id is not None:
        #     self.selected_object_data = self.backend.get_game_state().cities.get(self.selected_city_id)
        else:
            self.selected_object_data = None
        
        self.ui_manager.update(self.selected_object_data)

    def _draw_city(self, surface, city_data, pos_x, pos_y):
        """Рисует центр города и его название по заданным пиксельным координатам."""
        # Рисуем звезду в центре города
        size = self.hex_size * 0.5
        points = []
        for i in range(10):
            angle = math.pi / 5 * i
            radius = size if i % 2 == 0 else size * 0.4
            points.append((pos_x + radius * math.sin(angle), pos_y - radius * math.cos(angle)))
        pygame.draw.polygon(surface, CITY_CENTER_COLOR, points)
        
        # Рисуем название города
        name_font = pygame.font.SysFont("Arial", 16, bold=True)
        text = name_font.render(city_data['name'], True, CITY_NAME_COLOR)
        text_rect = text.get_rect(midbottom=(pos_x, pos_y - self.hex_size * 0.6))
        surface.blit(text, text_rect)

    def _calculate_viewport_data(self):
        """
        Вычисляет и диапазон для отсечения, и точные угловые гексы для рамки.
        Возвращает: (диапазон_отсечения, список_угловых_гексов)
        """
        # 1. Находим точные угловые гексы
        points_to_check = [(0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)]
        corner_hexes = [self._pixel_to_hex(x, y) for x, y in points_to_check]
        
        # 2. На основе углов вычисляем диапазон для быстрой отрисовки
        all_qs = [q for q, r in corner_hexes]
        all_rs = [r for q, r in corner_hexes]
        
        margin = 2
        min_q = min(all_qs) - margin
        max_q = max(all_qs) + margin
        min_r = min(all_rs) - margin
        max_r = max(all_rs) + margin
        
        culling_range = (min_q, max_q, min_r, max_r)
        
        return culling_range, corner_hexes

    def _draw_unit(self, surface, unit_data, pos_x, pos_y):
        """Рисует одного юнита по заданным пиксельным координатам."""
        unit_type = unit_data['type']
        visual = UNIT_VISUALS.get(unit_type, DEFAULT_UNIT_VISUAL)
        size = self.hex_size * 0.6
        
        if visual.shape == 'circle':
            pygame.draw.circle(surface, visual.color, (pos_x, pos_y), size)
        elif visual.shape == 'square':
            rect = pygame.Rect(pos_x - size, pos_y - size, size * 2, size * 2)
            pygame.draw.rect(surface, visual.color, rect)
        elif visual.shape == 'triangle':
            points = [
                (pos_x, pos_y - size),
                (pos_x - size, pos_y + size * 0.7),
                (pos_x + size, pos_y + size * 0.7),
            ]
            pygame.draw.polygon(surface, visual.color, points)
            
        symbol_font = pygame.font.SysFont("Arial", int(size * 1.5))
        text = symbol_font.render(visual.symbol, True, (0,0,0))
        text_rect = text.get_rect(center=(pos_x, pos_y))
        surface.blit(text, text_rect)

        if unit_data['id'] == self.selected_unit_id:
            pygame.draw.circle(surface, (255, 255, 0), (pos_x, pos_y), self.hex_size * 0.7, 3)

    def _hex_to_pixel(self, q, r, q_offset=0):
        """Преобразует гекс-координаты в экранные, с учетом зацикливания по q."""
        world_x = self.hex_size * (3.0 / 2.0 * (q + q_offset))
        world_y = self.hex_size * (math.sqrt(3) / 2.0 * q + math.sqrt(3) * r)
        screen_x = world_x + SCREEN_WIDTH / 2 + self.camera_offset.x
        screen_y = world_y + SCREEN_HEIGHT / 2 + self.camera_offset.y
        return screen_x, screen_y

    def _pixel_to_hex(self, x, y):
        """Преобразует экранные координаты в гекс-координаты с учетом зацикливания."""
        # Сначала находим ближайший гекс в основной (не смещенной) системе координат
        world_x = x - SCREEN_WIDTH / 2 - self.camera_offset.x
        world_y = y - SCREEN_HEIGHT / 2 - self.camera_offset.y
        
        # Ширина мира в пикселях
        map_pixel_width = self.hex_size * (3.0 / 2.0 * MAP_WIDTH)
        
        # Нормализуем world_x, чтобы он находился в пределах одной ширины карты
        # Это важно для правильного преобразования обратно в гексы
        world_x = world_x % map_pixel_width

        q = (2.0 / 3.0 * world_x) / self.hex_size
        r = (-1.0 / 3.0 * world_x + math.sqrt(3) / 3.0 * world_y) / self.hex_size
        
        # Округляем до ближайшего целого гекса и применяем зацикливание по q
        q_round, r_round = self._hex_round(q, r)
        return q_round % MAP_WIDTH, r_round

    def _hex_round(self, q, r):
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        return int(rq), int(rr)
    
    def _get_unit_at_hex(self, hex_coords):
        state = self.backend.get_game_state()
        # Учитываем зацикливание при поиске юнита
        wrapped_hex = (hex_coords[0] % MAP_WIDTH, hex_coords[1])
        for unit_id, unit_data in state.units.items():
            if tuple(unit_data["position"]) == wrapped_hex:
                return unit_id
        return None
        
    def _get_visible_hex_range(self):
        """
        Вычисляет 4 угловых гекса, видимых на экране.
        Возвращает список из 4 кортежей (q,r).
        """
        points_to_check = [(0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)]
        visible_hexes = [self._pixel_to_hex(x, y) for x, y in points_to_check]
        return visible_hexes

    def _draw_hex(self, surface, color, pos_x, pos_y, border_color=(50, 50, 50), border_width=2):
        """Рисует гекс по заданным пиксельным координатам."""
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.pi / 180 * angle_deg
            points.append(
                (pos_x + self.hex_size * math.cos(angle_rad),
                 pos_y + self.hex_size * math.sin(angle_rad))
            )
        pygame.draw.polygon(surface, color, points)
        if border_width > 0:
            pygame.draw.polygon(surface, border_color, points, border_width)

    def _draw_game_state(self):
        """
        Основная функция отрисовки. Рисует все видимые объекты с учетом зацикливания.
        """
        state = self.backend.get_game_state()
        
        # Ширина мира в пикселях для смещения
        map_q_width = MAP_WIDTH
        
        # Смещения для отрисовки копий мира для бесшовного перехода
        q_offsets = [0, -map_q_width, map_q_width]

        # --- Отрисовка сетки и подсветки ходов ---
        for q, r in state.grid:
            hex_data = state.grid[(q, r)]
            tile_type = hex_data['tile']
            color = TILE_COLORS.get(tile_type, DEFAULT_TILE_COLOR)
            
            is_valid_move = (q, r) in self.valid_moves
            
            for q_offset in q_offsets:
                pos_x, pos_y = self._hex_to_pixel(q, r, q_offset)
                
                # Простая отсечка за пределами экрана
                if -self.hex_size < pos_x < SCREEN_WIDTH + self.hex_size and \
                   -self.hex_size < pos_y < SCREEN_HEIGHT + self.hex_size:
                    
                    border_color = (255, 255, 0) if is_valid_move else (50, 50, 50)
                    border_width = 3 if is_valid_move else 2
                    self._draw_hex(self.screen, color, pos_x, pos_y, border_color, border_width)

        # --- Отрисовка городов ---
        for city_id, city_data in state.cities.items():
            q, r = city_data['center_hex']
            for q_offset in q_offsets:
                pos_x, pos_y = self._hex_to_pixel(q, r, q_offset)
                if -self.hex_size < pos_x < SCREEN_WIDTH + self.hex_size and \
                   -self.hex_size < pos_y < SCREEN_HEIGHT + self.hex_size:
                    self._draw_city(self.screen, city_data, pos_x, pos_y)

        # --- Отрисовка юнитов ---
        for unit_id, unit_data in state.units.items():
            q, r = unit_data["position"]
            for q_offset in q_offsets:
                pos_x, pos_y = self._hex_to_pixel(q, r, q_offset)
                if -self.hex_size < pos_x < SCREEN_WIDTH + self.hex_size and \
                   -self.hex_size < pos_y < SCREEN_HEIGHT + self.hex_size:
                    self._draw_unit(self.screen, unit_data, pos_x, pos_y)
    
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            ui_action = self.ui_manager.handle_event(event)
            if ui_action:
                if ui_action == 'FOUND_CITY':
                    if self.selected_unit_id is not None:
                        city_name = f"Город {self.backend.game_state.next_city_id}"
                        success = self.backend.found_city(self.selected_unit_id, city_name)
                        if success: 
                            self.selected_unit_id = None
                            self.valid_moves = []
                elif ui_action == 'END_TURN':
                    self.backend.end_turn()
                
                # Если UI обработал клик, дальше ничего не делаем
                continue 

            if event.type == pygame.KEYDOWN:
                # Клавиша 'B' больше не нужна, теперь есть кнопка
                pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверяем, что клик был не по UI
                if not self.ui_manager.ui_rect.collidepoint(event.pos):
                    if event.button == 4 or event.button == 5: # Zoom
                        mouse_pos = pygame.math.Vector2(event.pos)
                        screen_center = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        world_pixel_before_zoom = (mouse_pos - screen_center - self.camera_offset) / self.hex_size
                        
                        if event.button == 4: self.hex_size *= ZOOM_SPEED
                        else: self.hex_size /= ZOOM_SPEED
                        self.hex_size = max(MIN_HEX_SIZE, min(MAX_HEX_SIZE, self.hex_size))
                        
                        new_world_pixel_pos = world_pixel_before_zoom * self.hex_size
                        self.camera_offset = mouse_pos - screen_center - new_world_pixel_pos

                    elif event.button == 1: # Drag start
                        self.is_dragging = True
                        self.drag_start_pos = pygame.math.Vector2(event.pos)
                    elif event.button == 3: # Right-click (move unit)
                        if self.selected_unit_id is not None:
                            clicked_hex = self._pixel_to_hex(*event.pos)
                            move_successful = self.backend.move_unit(self.selected_unit_id, clicked_hex)
                            if move_successful:
                                self.valid_moves = self.backend.get_valid_moves(self.selected_unit_id)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.is_dragging:
                    self.is_dragging = False
                    drag_distance = self.drag_start_pos.distance_to(event.pos)
                    if drag_distance < CLICK_DRAG_THRESHOLD: # Click
                        clicked_hex = self._pixel_to_hex(*event.pos)
                        unit_id = self._get_unit_at_hex(clicked_hex)
                        if unit_id is not None:
                            self.selected_unit_id = unit_id
                            self.valid_moves = self.backend.get_valid_moves(unit_id)
                        else:
                            self.selected_unit_id = None
                            self.valid_moves = []
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    current_pos = pygame.math.Vector2(event.pos)
                    self.camera_offset += current_pos - self.drag_start_pos
                    self.drag_start_pos = current_pos

    def _process_game_events(self):
        events = self.backend.get_events()
        for event in events:
            pass

    def run(self):
        """Главный цикл игры."""
        clock = pygame.time.Clock()
        while self.running:
            # --- ОБРАБОТКА ЛОГИКИ ---
            self._handle_input()
            self._process_game_events()
            self._update_selection_data()

            # --- ВЫЧИСЛЕНИЕ ДАННЫХ ДЛЯ ОТРИСОВКИ (ОДИН РАЗ ЗА КАДР) ---
            # culling_range, viewport_hexes = self._calculate_viewport_data()

            # --- ОТРИСОВКА ---
            self.screen.fill((20, 20, 30))
            
            # Основная отрисовка мира
            self._draw_game_state()
            
            # Отрисовка UI поверх всего
            viewport_hexes = self._get_visible_hex_range()
            self.ui_manager.draw(self.screen, viewport_hexes)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
