# frontend_pygame.py
import pygame
import math
from events import EventType
from frontend_visuals import TILE_COLORS, DEFAULT_TILE_COLOR, UNIT_VISUALS, DEFAULT_UNIT_VISUAL
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
        if self.selected_unit_id is not None:
            self.selected_object_data = self.backend.get_game_state().units.get(self.selected_unit_id)
        else:
            self.selected_object_data = None
        self.ui_manager.update(self.selected_object_data)

    

    def _draw_unit(self, surface, unit_data, pos_x, pos_y):
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

    def _axial_to_pixel(self, q, r, world_x_offset=0):
        """Converts axial coordinates to pixel coordinates for rectangular (odd-q) layout."""
        col = q
        row = r + (q - (q & 1)) // 2
        x = self.hex_size * 3/2 * col
        y = self.hex_size * math.sqrt(3) * (row + 0.5 * (col & 1))
        return x + world_x_offset + self.camera_offset.x, y + self.camera_offset.y

    def _pixel_to_hex(self, x, y):
        """Converts pixel coordinates to axial coordinates for rectangular (odd-q) layout."""
        px = x - self.camera_offset.x
        py = y - self.camera_offset.y
        
        map_pixel_width = self.hex_size * 3/2 * MAP_WIDTH
        world_instance_offset = round(px / map_pixel_width) * map_pixel_width
        px_in_world = px - world_instance_offset

        # Fractional axial coordinates
        q_frac = (2/3 * px_in_world) / self.hex_size
        r_frac = (-1/3 * px_in_world + math.sqrt(3)/3 * py) / self.hex_size
        
        # Hex rounding
        q = round(q_frac)
        r = round(r_frac)
        s = round(-q_frac - r_frac)

        q_diff = abs(q - q_frac)
        r_diff = abs(r - r_frac)
        s_diff = abs(s - (-q_frac - r_frac))

        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        elif r_diff > s_diff:
            r = -q - s
        
        return q, r

    def _get_unit_at_hex(self, hex_coords):
        state = self.backend.get_game_state()
        for unit_id, unit_data in state.units.items():
            if tuple(unit_data["position"]) == hex_coords:
                return unit_id
        return None
        
    def _get_visible_hexes(self):
        """Calculates all hexes currently visible in the viewport."""
        visible_hexes = set()
        state = self.backend.get_game_state()
        if not state.grid:
            return []

        map_pixel_width = self.hex_size * 3/2 * MAP_WIDTH
        world_offsets = [0, -map_pixel_width, map_pixel_width]

        for q, r in state.grid.keys():
            for offset in world_offsets:
                pos_x, pos_y = self._axial_to_pixel(q, r, world_x_offset=offset)
                # Check if the hex is within the screen bounds (with a margin)
                if -self.hex_size < pos_x < SCREEN_WIDTH + self.hex_size and \
                   -self.hex_size < pos_y < SCREEN_HEIGHT + self.hex_size:
                    visible_hexes.add((q, r))
                    break  # Found as visible, no need to check other wrapped worlds
        
        return list(visible_hexes)

    def _draw_hex(self, surface, color, pos_x, pos_y, border_color=(50, 50, 50), border_width=2):
        points = []
        for i in range(6):
            angle = math.pi / 180 * (60 * i)
            points.append((pos_x + self.hex_size * math.cos(angle), pos_y + self.hex_size * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)
        if border_width > 0:
            pygame.draw.polygon(surface, border_color, points, border_width)

    def _draw_game_state(self):
        state = self.backend.get_game_state()
        map_pixel_width = self.hex_size * 3/2 * MAP_WIDTH
        world_offsets = [0, -map_pixel_width, map_pixel_width]

        for (q, r), hex_data in state.grid.items():
            tile_type = hex_data['tile']
            color = TILE_COLORS.get(tile_type, DEFAULT_TILE_COLOR)
            is_valid_move = (q, r) in self.valid_moves
            
            for offset in world_offsets:
                pos_x, pos_y = self._axial_to_pixel(q, r, offset)
                if -self.hex_size < pos_x < SCREEN_WIDTH + self.hex_size and \
                   -self.hex_size < pos_y < SCREEN_HEIGHT + self.hex_size:
                    border_color = (255, 255, 0) if is_valid_move else (50, 50, 50)
                    border_width = 3 if is_valid_move else 2
                    self._draw_hex(self.screen, color, pos_x, pos_y, border_color, border_width)

        

        for unit_data in state.units.values():
            q, r = unit_data["position"]
            for offset in world_offsets:
                pos_x, pos_y = self._axial_to_pixel(q, r, offset)
                if -self.hex_size < pos_x < SCREEN_WIDTH + self.hex_size and \
                   -self.hex_size < pos_y < SCREEN_HEIGHT + self.hex_size:
                    self._draw_unit(self.screen, unit_data, pos_x, pos_y)
    
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            ui_action = self.ui_manager.handle_event(event)
            if ui_action:
                if ui_action == 'END_TURN': self.backend.end_turn()
                continue 

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.ui_manager.ui_rect.collidepoint(event.pos):
                    if event.button == 4 or event.button == 5: # Zoom
                        mouse_pos = pygame.math.Vector2(event.pos)
                        world_pos_before_zoom = (mouse_pos - self.camera_offset)
                        
                        if event.button == 4: self.hex_size *= ZOOM_SPEED
                        else: self.hex_size /= ZOOM_SPEED
                        self.hex_size = max(MIN_HEX_SIZE, min(MAX_HEX_SIZE, self.hex_size))
                        
                        scale = self.hex_size / (self.hex_size / (ZOOM_SPEED if event.button == 4 else 1/ZOOM_SPEED))
                        self.camera_offset = mouse_pos - world_pos_before_zoom * scale

                    elif event.button == 1: # Drag start
                        self.is_dragging = True
                        self.drag_start_pos = pygame.math.Vector2(event.pos)
                    elif event.button == 3 and self.selected_unit_id is not None:
                        clicked_hex = self._pixel_to_hex(*event.pos)
                        if self.backend.move_unit(self.selected_unit_id, clicked_hex):
                            self.valid_moves = self.backend.get_valid_moves(self.selected_unit_id)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.is_dragging:
                    self.is_dragging = False
                    if self.drag_start_pos.distance_to(event.pos) < CLICK_DRAG_THRESHOLD:
                        clicked_hex = self._pixel_to_hex(*event.pos)
                        unit_id = self._get_unit_at_hex(clicked_hex)
                        self.selected_unit_id = unit_id
                        self.valid_moves = self.backend.get_valid_moves(unit_id) if unit_id else []
            elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                self.camera_offset += event.rel

    def _process_game_events(self):
        for event in self.backend.get_events(): pass

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self._handle_input()
            self._process_game_events()
            self._update_selection_data()

            # --- Camera Wrapping Logic ---
            map_pixel_width = self.hex_size * 3/2 * MAP_WIDTH
            # Wrap the camera offset to keep it within the bounds of one map width
            self.camera_offset.x = self.camera_offset.x % -map_pixel_width

            self.screen.fill((20, 20, 30))
            self._draw_game_state()
            self.ui_manager.draw(self.screen, self._get_visible_hexes())
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
