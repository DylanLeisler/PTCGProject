import pygame

from scenes.base_scene import BaseScene
from scenes.overworld_scene import OverworldScene


class TitleScene(BaseScene):
    def __init__(self, screen: pygame.Surface, scene_manager) -> None:
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 64)
        self.sub_font = pygame.font.Font(None, 32)
        self.message = "Press X to continue"

    def update(self, dt: float) -> None:
        # No time-based updates needed for the placeholder title scene.
        return

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((10, 20, 40))
        title_surface = self.font.render("PTCG SM Campaign", True, (255, 255, 255))
        prompt_surface = self.sub_font.render(self.message, True, (200, 200, 220))
        title_rect = title_surface.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 40))
        prompt_rect = prompt_surface.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 30))
        screen.blit(title_surface, title_rect)
        screen.blit(prompt_surface, prompt_rect)

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_x):
                self.scene_manager.replace(OverworldScene(self.screen, self.scene_manager))
