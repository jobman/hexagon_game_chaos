# ui/end_turn_panel.py
import pygame

class EndTurnPanel:
    def __init__(self, rect, backend):
        self.rect = rect
        self.backend = backend
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        
        # Центрируем кнопку внутри ее панели
        w, h = self.rect.width * 0.8, self.rect.height * 0.6
        x = self.rect.centerx - w / 2
        y = self.rect.centery - h / 2
        self.button_rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, (100, 120, 80), self.button_rect)
        pygame.draw.rect(surface, (180, 200, 160), self.button_rect, 3)
        
        text_surf = self.font.render("Конец хода", True, (240, 240, 240))
        text_rect = text_surf.get_rect(center=self.button_rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, pos):
        if self.button_rect.collidepoint(pos):
            return "END_TURN"
        return None