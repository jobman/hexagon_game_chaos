# ui/ui_manager.py
import pygame
from .minimap import Minimap
from .action_panel import ActionPanel
from .end_turn_panel import EndTurnPanel
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class UIManager:
    def __init__(self, backend):
        self.backend = backend

        # Определяем общую область UI (нижняя четверть экрана)
        self.ui_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.75, SCREEN_WIDTH, SCREEN_HEIGHT * 0.25)
        
        # Разбиваем область UI на три части
        minimap_width = SCREEN_WIDTH * 0.25
        end_turn_width = SCREEN_WIDTH * 0.25
        action_panel_width = SCREEN_WIDTH - minimap_width - end_turn_width

        minimap_rect = pygame.Rect(0, self.ui_rect.top, minimap_width, self.ui_rect.height)
        action_panel_rect = pygame.Rect(minimap_width, self.ui_rect.top, action_panel_width, self.ui_rect.height)
        end_turn_rect = pygame.Rect(minimap_width + action_panel_width, self.ui_rect.top, end_turn_width, self.ui_rect.height)

        # Создаем экземпляры каждой панели
        self.minimap = Minimap(backend, minimap_rect)
        self.action_panel = ActionPanel(action_panel_rect, backend)
        self.end_turn_panel = EndTurnPanel(end_turn_rect, backend)

    def draw(self, surface, viewport_hexes): # <-- Аргумент переименован для ясности
        """Рисует все компоненты UI."""
        s = pygame.Surface((self.ui_rect.width, self.ui_rect.height), pygame.SRCALPHA)
        s.fill((20, 30, 40, 220))
        surface.blit(s, self.ui_rect.topleft)

        self.minimap.draw(surface, viewport_hexes) # <-- Просто передаем дальше
        self.action_panel.draw(surface)
        self.end_turn_panel.draw(surface)

    def handle_event(self, event):
        """Обрабатывает события и передает их нужной панели."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ui_rect.collidepoint(event.pos):
                # Клик был внутри UI, передаем его панелям
                if self.minimap.rect.collidepoint(event.pos):
                    # Логика клика по миникарте (пока пропустим)
                    pass
                elif self.action_panel.rect.collidepoint(event.pos):
                    return self.action_panel.handle_click(event.pos)
                elif self.end_turn_panel.rect.collidepoint(event.pos):
                    return self.end_turn_panel.handle_click(event.pos)
                return 'ui_click' # Сообщаем, что клик обработан UI, но без действия
        return None

    def update(self, selected_object_data):
        """Обновляет состояние панелей (например, панель действий)."""
        self.action_panel.update_selected_object(selected_object_data)