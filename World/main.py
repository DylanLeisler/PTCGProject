from __future__ import annotations

import pygame

from game_config import GameConfig as GC
from scene_manager import SceneManager
from scenes.title_scene import TitleScene


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((GC.SCREEN_WIDTH, GC.SCREEN_HEIGHT))
    pygame.display.set_caption("PTCG-SM-CAMPAIGN")
    clock = pygame.time.Clock()
    scene_manager = SceneManager()
    scene_manager.push(TitleScene(screen, scene_manager))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene_manager.handle_event(event)

        scene_manager.update(dt)
        scene_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
