# ui/minimap.py
import pygame
import math
from frontend_visuals import TILE_COLORS, DEFAULT_TILE_COLOR
from constants import MAP_WIDTH, MAP_HEIGHT
from hex_utils import hex_neighbors

class Minimap:
    def __init__(self, backend, rect):
        self.backend = backend
        self.rect = rect
        self.font = pygame.font.SysFont("Arial", 12)
        self.terrain_cache = None
        self.scale_x = 1
        self.scale_y = 1
        self._create_terrain_cache()

    def _create_terrain_cache(self):
        state = self.backend.get_game_state()
        if not state.grid:
            return

        self.cache_surface = pygame.Surface(self.rect.size)
        self.cache_surface.fill((10, 20, 30)) # Dark blue background

        # Determine the scale to fit the entire rectangular map, stretching it.
        map_hex_width = MAP_WIDTH * 1.5 + 0.5
        map_hex_height = MAP_HEIGHT * math.sqrt(3) + (math.sqrt(3) / 2)

        self.scale_x = self.rect.width / map_hex_width
        self.scale_y = self.rect.height / map_hex_height

        for (q, r), data in state.grid.items():
            col = q
            row = r + (q - (q & 1)) // 2

            # Use relative coordinates for drawing on the cache surface
            pixel_x = self.scale_x * (1.5 * col)
            pixel_y = self.scale_y * (math.sqrt(3) * (row + 0.5 * (col & 1)))

            color = TILE_COLORS.get(data['tile'], DEFAULT_TILE_COLOR)
            
            # Use an ellipse to draw a stretched circle
            ellipse_rect = pygame.Rect(
                pixel_x - self.scale_x * 0.9,
                pixel_y - self.scale_y * 0.9,
                self.scale_x * 1.8,
                self.scale_y * 1.8
            )
            pygame.draw.ellipse(self.cache_surface, color, ellipse_rect)
        
        self.terrain_cache = self.cache_surface

    def _axial_to_minimap_pixel(self, q, r):
        """Converts an axial coordinate to a pixel coordinate on the minimap's surface.
           Returns coordinates relative to the minimap's top-left corner.
        """
        col = q
        row = r + (q - (q & 1)) // 2

        pixel_x = self.scale_x * (1.5 * col)
        pixel_y = self.scale_y * (math.sqrt(3) * (row + 0.5 * (col & 1)))
        return pixel_x, pixel_y

    def draw(self, surface, viewport_hexes):
        if not self.terrain_cache:
            self._create_terrain_cache()
        
        surface.blit(self.terrain_cache, self.rect.topleft)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1) # Border

        if viewport_hexes:
            original_clip = surface.get_clip()

            # Adjust the clipping rectangle to be slightly smaller on the right
            hex_width_on_minimap = self.scale_x * 1.5
            adjusted_clip_rect = self.rect.copy()
            adjusted_clip_rect.width -= hex_width_on_minimap
            surface.set_clip(adjusted_clip_rect)

            viewport_hexes_set = set(viewport_hexes)
            q_coords = sorted([h[0] for h in viewport_hexes])
            is_split = (q_coords[-1] - q_coords[0]) > (MAP_WIDTH / 2)
            minimap_pixel_width = self.scale_x * 1.5 * MAP_WIDTH

            outline_color = (255, 255, 255) # White outline

            for q, r in viewport_hexes:
                is_perimeter = False
                for neighbor_q, neighbor_r in hex_neighbors((q, r)):
                    wrapped_neighbor = (neighbor_q % MAP_WIDTH, neighbor_r)
                    if wrapped_neighbor not in viewport_hexes_set:
                        is_perimeter = True
                        break
                
                if is_perimeter:
                    pixel_x, pixel_y = self._axial_to_minimap_pixel(q, r)
                    screen_x = pixel_x + self.rect.left
                    screen_y = pixel_y + self.rect.top

                    ellipse_rect = pygame.Rect(
                        screen_x - self.scale_x * 0.9,
                        screen_y - self.scale_y * 0.9,
                        self.scale_x * 1.8,
                        self.scale_y * 1.8
                    )
                    pygame.draw.ellipse(surface, outline_color, ellipse_rect, 1)

                    if is_split and q < MAP_WIDTH / 2:
                        wrapped_ellipse_rect = ellipse_rect.move(minimap_pixel_width, 0)
                        pygame.draw.ellipse(surface, outline_color, wrapped_ellipse_rect, 1)

            surface.set_clip(original_clip)
