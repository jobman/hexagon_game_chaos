# ui/action_panel.py
import pygame
from unit_types import UnitType, UNIT_PROPERTIES

class ActionPanel:
    def __init__(self, rect, backend):
        self.rect = rect
        self.backend = backend
        self.buttons = []
        self.font = pygame.font.SysFont("Arial", 18)
        self.info_font = pygame.font.SysFont("Arial", 16)
        self.selected_unit_data = None

    def update_selected_object(self, selected_object_data):
        """Обновляет панель на основе выбранного объекта."""
        self.buttons.clear()
        self.selected_unit_data = None

        if selected_object_data is None:
            return

        if 'energy' in selected_object_data:
            self.selected_unit_data = selected_object_data

        obj_type = selected_object_data.get('type')

        if obj_type == UnitType.SETTLER:
            self._add_button("Основать город", "FOUND_CITY")

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

        if self.selected_unit_data:
            unit_type = self.selected_unit_data['type']
            unit_props = UNIT_PROPERTIES[unit_type]
            
            current_energy = self.selected_unit_data['energy']
            max_energy = unit_props.max_energy
            
            energy_text = f"Энергия: {current_energy} / {max_energy}"
            
            text_surf = self.info_font.render(energy_text, True, (230, 230, 230))
            text_rect = text_surf.get_rect(centery=self.rect.centery)
            text_rect.right = self.rect.right - 20
            surface.blit(text_surf, text_rect)
            
    def handle_click(self, pos):
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                return button['action']
        return None
