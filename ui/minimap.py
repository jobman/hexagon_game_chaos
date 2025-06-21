# ui/minimap.py
import pygame
from frontend_visuals import TILE_COLORS, DEFAULT_TILE_COLOR

class Minimap:
    def __init__(self, rect, backend):
        self.rect = rect
        self.backend = backend
        self.terrain_cache = None
        self.pixel_size = 1
        self.min_q, self.min_r = 0, 0
        self.offset_x, self.offset_y = 0, 0
        self._create_terrain_cache()

    def _hex_to_minimap_pixel(self, q, r):
        # Преобразуем в относительные пиксели (без центрирования)
        x_rel = (q - self.min_q) * self.pixel_size * 0.75
        y_rel = (r - self.min_r) * self.pixel_size + (q - self.min_q) * self.pixel_size * 0.5
        # Добавляем отступ для центрирования
        return x_rel + self.offset_x, y_rel + self.offset_y

    def _create_terrain_cache(self):
        state = self.backend.get_game_state()
        if not state.grid: return

        all_q = [q for q, r in state.grid.keys()]
        all_r = [r for q, r in state.grid.keys()]
        self.min_q, max_q = min(all_q), max(all_q)
        self.min_r, max_r = min(all_r), max(all_r)
        
        map_hex_width, map_hex_height = (max_q - self.min_q) + 1, (max_r - self.min_r) + 1
        if map_hex_width <= 1 or map_hex_height <= 1: return

        # --- ИСПРАВЛЕНИЕ РАСЧЕТА МАСШТАБА И ВЫСОТЫ ---
        # "Рабочая" ширина и высота карты в гексах для pointy-top
        effective_width_hex = map_hex_width * 0.75 + 0.25
        effective_height_hex = map_hex_height + 0.5 * (map_hex_width if map_hex_width % 2 == 0 else map_hex_width - 1)
        
        pixel_w = self.rect.width / effective_width_hex
        pixel_h = self.rect.height / effective_height_hex
        self.pixel_size = min(pixel_w, pixel_h)

        # Вычисляем финальный размер отрендеренной карты в пикселях
        rendered_map_width = effective_width_hex * self.pixel_size
        
        # Находим максимальную y-координату для точного расчета высоты
        max_y_rel = 0
        for q, r in state.grid.keys():
            y_rel = (r - self.min_r) * self.pixel_size + (q - self.min_q) * self.pixel_size * 0.5
            if y_rel > max_y_rel:
                max_y_rel = y_rel
        rendered_map_height = max_y_rel + self.pixel_size

        self.offset_x = (self.rect.width - rendered_map_width) / 2
        self.offset_y = (self.rect.height - rendered_map_height) / 2
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

        self.cache_surface = pygame.Surface(self.rect.size)
        self.cache_surface.fill((10, 20, 30))

        for (q, r), hex_data in state.grid.items():
            x, y = self._hex_to_minimap_pixel(q, r)
            color = TILE_COLORS.get(hex_data['tile'], DEFAULT_TILE_COLOR)
            pygame.draw.rect(self.cache_surface, color, (x, y, self.pixel_size, self.pixel_size))
        
        self.terrain_cache = self.cache_surface

    def draw(self, surface, viewport_hexes): # <-- Принимаем список гексов
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 2)
        
        if self.terrain_cache:
            surface.blit(self.terrain_cache, self.rect.topleft)

        if viewport_hexes:
            # --- ИСПРАВЛЕНИЕ ЛОГИКИ РАМКИ ---
            # Просто конвертируем полученные точки и рисуем полигон
            points = [self._hex_to_minimap_pixel(q, r) for q, r in viewport_hexes]
            
            screen_points = [(p[0] + self.rect.left, p[1] + self.rect.top) for p in points]
            pygame.draw.polygon(surface, (255, 255, 255), screen_points, 2)
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---