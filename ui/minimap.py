# ui/minimap.py
import pygame
import math
from frontend_visuals import TILE_COLORS, DEFAULT_TILE_COLOR
from constants import MAP_WIDTH, MAP_HEIGHT

class Minimap:
    def __init__(self, backend, rect):
        self.backend = backend
        self.rect = rect
        self.font = pygame.font.SysFont("Arial", 12)
        self.terrain_cache = None
        self._create_terrain_cache()

    def _create_terrain_cache(self):
        state = self.backend.get_game_state()
        if not state.grid:
            return

        self.cache_surface = pygame.Surface(self.rect.size)
        self.cache_surface.fill((10, 20, 30)) # Dark blue background

        # Determine the scale to fit the entire rectangular map
        # Effective map dimensions in hex units for odd-q layout
        map_hex_width = MAP_WIDTH * 1.5 + 0.5
        map_hex_height = MAP_HEIGHT * math.sqrt(3) + (math.sqrt(3) / 2)

        scale_x = self.rect.width / map_hex_width
        scale_y = self.rect.height / map_hex_height
        self.scale = min(scale_x, scale_y)
        self.hex_size = self.scale

        for (q, r), data in state.grid.items():
            col = q
            row = r + (q - (q & 1)) // 2

            # Use relative coordinates for drawing on the cache surface
            pixel_x = self.hex_size * 1.5 * col
            pixel_y = self.hex_size * math.sqrt(3) * (row + 0.5 * (col & 1))

            color = TILE_COLORS.get(data['tile'], DEFAULT_TILE_COLOR)
            pygame.draw.circle(self.cache_surface, color, (pixel_x, pixel_y), self.hex_size * 0.9)
        
        self.terrain_cache = self.cache_surface

    def _axial_to_minimap_pixel(self, q, r):
        """Converts an axial coordinate to a pixel coordinate on the minimap's surface.
           Returns coordinates relative to the minimap's top-left corner.
        """
        col = q
        row = r + (q - (q & 1)) // 2

        pixel_x = self.hex_size * 1.5 * col
        pixel_y = self.hex_size * math.sqrt(3) * (row + 0.5 * (col & 1))
        return pixel_x, pixel_y

    def draw(self, surface, viewport_hexes):
        if not self.terrain_cache:
            self._create_terrain_cache()
        
        surface.blit(self.terrain_cache, self.rect.topleft)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1) # Border

        if viewport_hexes:
            # Convert hexes to pixel coordinates relative to the minimap surface
            points = [self._axial_to_minimap_pixel(q, r) for q, r in viewport_hexes]

            # Check if the viewport is split across the wrap boundary
            q_coords = sorted([h[0] for h in viewport_hexes])
            is_split = (q_coords[-1] - q_coords[0]) > (MAP_WIDTH / 2)

            # Offset all points to be on the main screen
            screen_points = [(p[0] + self.rect.left, p[1] + self.rect.top) for p in points]

            if is_split:
                # Separate points into two polygons for each side of the map
                points_left = [p for p, h in zip(screen_points, viewport_hexes) if h[0] >= MAP_WIDTH / 2]
                points_right = [p for p, h in zip(screen_points, viewport_hexes) if h[0] < MAP_WIDTH / 2]

                # To make the right side appear on the left, we create a wrapped copy
                minimap_pixel_width = self.hex_size * 1.5 * MAP_WIDTH
                points_right_wrapped = [(p[0] + minimap_pixel_width, p[1]) for p in points_right]
                
                # Draw both polygons
                if len(points_left) > 1: pygame.draw.polygon(surface, (255, 255, 0), points_left, 2)
                if len(points_right_wrapped) > 1: pygame.draw.polygon(surface, (255, 255, 0), points_right_wrapped, 2)
            else:
                # If not split, draw a single polygon
                if len(screen_points) > 1:
                    pygame.draw.polygon(surface, (255, 255, 0), screen_points, 2)
