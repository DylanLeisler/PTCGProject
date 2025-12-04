import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from classes.graphics.bugged_camera import Camera
from game_config import GameConfig as GC


TILE_SIZE = GC.TILE_SIZE
COURTYARD_WIDTH = 16 * TILE_SIZE
COURTYARD_HEIGHT = 14 * TILE_SIZE
PLAYER_SIZE = TILE_SIZE // 2
PLAYER_STEP = TILE_SIZE // 4
ACCESS_MARGIN = TILE_SIZE  # Distance from edge where movement stops

ACCESS_BOUNDS = pygame.Rect(
    ACCESS_MARGIN,
    ACCESS_MARGIN,
    COURTYARD_WIDTH - ACCESS_MARGIN * 2,
    COURTYARD_HEIGHT - ACCESS_MARGIN * 2,
)


def describe_rect(rect: pygame.Rect) -> str:
    return f"[x:{rect.x} y:{rect.y} w:{rect.width} h:{rect.height}]"


def main() -> None:
    pygame.init()
    screen_size = (GC.SCREEN_WIDTH, GC.SCREEN_HEIGHT)
    world_size = (COURTYARD_WIDTH, COURTYARD_HEIGHT)
    pygame.display.set_mode(screen_size)

    camera = Camera(
        screen_size=screen_size,
        world_size=world_size,
        base_view_size=world_size,
        max_zoom=GC.MAX_CAMERA_ZOOM,
        # constrain_to_world=False,
    )

    player_rect = pygame.Rect(
        ACCESS_BOUNDS.centerx,
        ACCESS_BOUNDS.centery,
        PLAYER_SIZE,
        PLAYER_SIZE,
    )

    command_help = (
        "Use WASD (or arrow words: up/down/left/right) to move, "
        "'pos' to reprint state, 'quit' to exit."
    )
    print("Camera test environment ready.")
    print(command_help)
    while True:
        command = input("> ").strip().lower()
        if command in ("quit", "exit", "q"):
            break
        if command in ("help", "?"):
            print(command_help)
            continue

        dx = dy = 0
        if command in ("w", "up"):
            dy = -PLAYER_STEP
        elif command in ("s", "down"):
            dy = PLAYER_STEP
        elif command in ("a", "left"):
            dx = -PLAYER_STEP
        elif command in ("d", "right"):
            dx = PLAYER_STEP
        elif command != "pos":
            print("Unknown command; type 'help' for options.")
            continue

        if dx or dy:
            new_rect = player_rect.move(dx, dy)
            if ACCESS_BOUNDS.contains(new_rect):
                player_rect = new_rect

        camera.update(player_rect)
        top_left = (camera.offset.x, camera.offset.y)
        bottom_right = (
            camera.offset.x + camera.view_width,
            camera.offset.y + camera.view_height,
        )

        print(
            "Player", describe_rect(player_rect),
            "| Camera offset", f"({top_left[0]:.1f}, {top_left[1]:.1f})",
            "view", f"x:[{top_left[0]:.1f} → {bottom_right[0]:.1f}]",
            f"y:[{top_left[1]:.1f} → {bottom_right[1]:.1f}]",
        )

    pygame.quit()


if __name__ == "__main__":
    main()
