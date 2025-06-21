# ui/action_panel.py
import pygame
from unit_types import UnitType

class ActionPanel:
    def __init__(self, rect, backend):
        self.rect = rect
        self.backend = backend
        self.buttons = []
        self.font = pygame.font.SysFont("Arial", 18)

    def update(self, selected_object_data):
        """Создает кнопки на основе выбранного объекта."""
        self.buttons.clear()
        if selected_object_data is None:
            return

        obj_type = selected_object_data.get('type')

        # Если выбран юнит-поселенец
        if obj_type == UnitType.SETTLER:
            self._add_button("Основать город", "FOUND_CITY")

        # Добавляйте другие кнопки для других юнитов или городов здесь
        # elif obj_type == UnitType.WARRIOR:
        #     self._add_button("Укрепиться", "FORTIFY")
        
    def _add_button(self, text, action_id):
        button_width, button_height = 150, 40
        x = self.rect.x + 20 + len(self.buttons) * (button_width + 10)
        y = self.rect.centery - button_height / 2
        button_rect = pygame.Rect(x, y, button_width, button_height)
        self.buttons.append({'rect': button_rect, 'text': text, 'action': action_id})

    def draw(self, surface):
        for button in self.buttons:
            pygame.draw.rect(surface, (80, 90, 100), button['rect'])
            pygame.draw.rect(surface, (150, 160, 170), button['rect'], 2)
            
            text_surf = self.font.render(button['text'], True, (220, 220, 220))
            text_rect = text_surf.get_rect(center=button['rect'].center)
            surface.blit(text_surf, text_rect)
            
    def handle_click(self, pos):
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                return button['action']
        return None