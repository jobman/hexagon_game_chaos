# frontend_pygame.py
import pygame
import math
from events import EventType
# Убираем: from tile_types import TILE_PROPERTIES
# Добавляем:
from frontend_visuals import TILE_COLORS, DEFAULT_TILE_COLOR, UNIT_VISUALS, DEFAULT_UNIT_VISUAL, CITY_CENTER_COLOR, CITY_NAME_COLOR
from unit_types import UnitType
from ui.ui_manager import UIManager

# Константы для отрисовки
WIDTH, HEIGHT = 800, 600
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
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hexagonal TBS")
        self.font = pygame.font.SysFont("Arial", 14)
        self.running = True
        self.selected_unit_id = None
        self.camera_offset = pygame.math.Vector2(0, 0)
        self.is_dragging = False
        self.drag_start_pos = None
        self.hex_size = DEFAULT_HEX_SIZE
        self.ui_manager = UIManager(WIDTH, HEIGHT, backend)
        self.selected_object_data = None
    
    def _update_selection_data(self):
        """Обновляет данные о выбранном объекте для передачи в UI."""
        if self.selected_unit_id is not None:
            self.selected_object_data = self.backend.get_game_state().units.get(self.selected_unit_id)
        # elif self.selected_city_id is not None:
        #     self.selected_object_data = self.backend.get_game_state().cities.get(self.selected_city_id)
        else:
            self.selected_object_data = None
        
        self.ui_manager.update(self.selected_object_data)

    def _draw_city(self, surface, city_data):
        """Рисует центр города и его название."""
        center_hex = city_data['center_hex']
        
        # Рисуем звезду в центре города
        pos_x, pos_y = self._hex_to_pixel(*center_hex)
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
        points_to_check = [(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)]
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

    def _draw_unit(self, surface, unit_data):
        """Рисует одного юнита в соответствии с его типом."""
        q, r = unit_data["position"]
        pos_x, pos_y = self._hex_to_pixel(q, r)
        
        # Получаем визуальные свойства для этого типа юнита
        unit_type = unit_data['type']
        visual = UNIT_VISUALS.get(unit_type, DEFAULT_UNIT_VISUAL)
        
        size = self.hex_size * 0.6
        
        # Рисуем фигуру
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
            
        # Рисуем символ юнита
        symbol_font = pygame.font.SysFont("Arial", int(size * 1.5))
        text = symbol_font.render(visual.symbol, True, (0,0,0))
        text_rect = text.get_rect(center=(pos_x, pos_y))
        surface.blit(text, text_rect)

        # Отрисовка выделения
        if unit_data['id'] == self.selected_unit_id:
            pygame.draw.circle(surface, (255, 255, 0), (pos_x, pos_y), self.hex_size * 0.7, 3)

    def _hex_to_pixel(self, q, r):
        world_x = self.hex_size * (3.0 / 2.0 * q)
        world_y = self.hex_size * (math.sqrt(3) / 2.0 * q + math.sqrt(3) * r)
        screen_x = world_x + WIDTH / 2 + self.camera_offset.x
        screen_y = world_y + HEIGHT / 2 + self.camera_offset.y
        return screen_x, screen_y

    def _pixel_to_hex(self, x, y):
        world_x = x - WIDTH / 2 - self.camera_offset.x
        world_y = y - HEIGHT / 2 - self.camera_offset.y
        q = (2.0 / 3.0 * world_x) / self.hex_size
        r = (-1.0 / 3.0 * world_x + math.sqrt(3) / 3.0 * world_y) / self.hex_size
        return self._hex_round(q, r)

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
        for unit_id, unit_data in state.units.items():
            if tuple(unit_data["position"]) == hex_coords:
                return unit_id
        return None
        
    def _get_visible_hex_range(self):
        """
        Вычисляет 4 угловых гекса, видимых на экране.
        Возвращает список из 4 кортежей (q,r).
        """
        points_to_check = [
            (0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)
        ]
        # Просто конвертируем 4 угла и возвращаем как есть
        visible_hexes = [self._pixel_to_hex(x, y) for x, y in points_to_check]
        return visible_hexes

    def _draw_hex(self, surface, color, q, r, border_color=(50, 50, 50), border_width=2):
        points = []
        center_x, center_y = self._hex_to_pixel(q, r)
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.pi / 180 * angle_deg
            points.append(
                (center_x + self.hex_size * math.cos(angle_rad),
                 center_y + self.hex_size * math.sin(angle_rad))
            )
        pygame.draw.polygon(surface, color, points)
        if border_width > 0:
            pygame.draw.polygon(surface, border_color, points, border_width)

    def _draw_game_state(self, culling_range):
        """
        Основная функция отрисовки. Рисует только видимые объекты.
        Принимает диапазон для отсечения.
        """
        state = self.backend.get_game_state()
        
        # Распаковываем полученный диапазон
        min_q, max_q, min_r, max_r = culling_range

        # Отрисовка сетки
        for q in range(min_q, max_q + 1): # <-- Теперь здесь нет ошибки
            for r in range(min_r, max_r + 1):
                if (q, r) in state.grid:
                    hex_data = state.grid[(q, r)]
                    tile_type = hex_data['tile']
                    color = TILE_COLORS.get(tile_type, DEFAULT_TILE_COLOR)
                    self._draw_hex(self.screen, color, q, r)

        # Отрисовка городов
        for city_id, city_data in state.cities.items():
            q, r = city_data['center_hex']
            if min_q <= q <= max_q and min_r <= r <= max_r:
                self._draw_city(self.screen, city_data)

        # Отрисовка юнитов
        for unit_id, unit_data in state.units.items():
            q, r = unit_data["position"]
            if min_q <= q <= max_q and min_r <= r <= max_r:
                self._draw_unit(self.screen, unit_data)
    
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
                        if success: self.selected_unit_id = None
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
                    if event.button == 4 or event.button == 5:
                        mouse_pos = pygame.math.Vector2(event.pos)
                        screen_center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
                        world_pixel_before_zoom = mouse_pos - screen_center - self.camera_offset
                        old_size = self.hex_size
                        if event.button == 4:
                            self.hex_size *= ZOOM_SPEED
                        else:
                            self.hex_size /= ZOOM_SPEED
                        self.hex_size = max(MIN_HEX_SIZE, min(MAX_HEX_SIZE, self.hex_size))
                        if old_size == 0: old_size = 0.0001
                        scale_factor = self.hex_size / old_size
                        new_world_pixel = world_pixel_before_zoom * scale_factor
                        self.camera_offset = mouse_pos - screen_center - new_world_pixel
                    elif event.button == 1:
                        self.is_dragging = True
                        self.drag_start_pos = pygame.math.Vector2(event.pos)
                    elif event.button == 3:
                        if self.selected_unit_id is not None:
                            clicked_hex = self._pixel_to_hex(*event.pos)
                            self.backend.move_unit(self.selected_unit_id, clicked_hex)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.is_dragging:
                    self.is_dragging = False
                    drag_distance = self.drag_start_pos.distance_to(event.pos)
                    if drag_distance < CLICK_DRAG_THRESHOLD:
                        clicked_hex = self._pixel_to_hex(*event.pos)
                        unit_id = self._get_unit_at_hex(clicked_hex)
                        if unit_id is not None:
                            self.selected_unit_id = unit_id
                        else:
                            self.selected_unit_id = None
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
            culling_range, viewport_hexes = self._calculate_viewport_data()

            # --- ОТРИСОВКА ---
            self.screen.fill((20, 20, 30))
            # Передаем диапазон для оптимизации
            self._draw_game_state(culling_range)
            # Передаем угловые точки для рамки миникарты
            self.ui_manager.draw(self.screen, viewport_hexes)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()