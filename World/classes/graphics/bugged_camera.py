import pygame


class Camera:
    def __init__(
        self,
        screen_size: tuple[int, int],
        world_size: tuple[int, int],
        base_view_size: tuple[int, int],
        max_zoom: float = 3.0,
    ) -> None:
        self.screen_width, self.screen_height = screen_size
        self.world_width, self.world_height = world_size
        self.base_view_width, self.base_view_height = base_view_size
        self.max_zoom = max_zoom
        self.zoom = 1.0
        self.offset = pygame.Vector2(0, 0)
        self.view_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        self._update_zoom()
        self._create_view_surface()

    def set_world_size(self, world_size: tuple[int, int]) -> None:
        self.world_width, self.world_height = world_size
        self._clamp_offset()

    def update(self, target_rect: pygame.Rect) -> None:
        self.offset.x = target_rect.centerx - self.view_width / 2
        self.offset.y = target_rect.centery - self.view_height / 2
        self._clamp_offset()

    def begin_draw(self, fill_color: tuple[int, int, int] = (0, 0, 0)) -> None:
        self.view_surface.fill(fill_color)

    def blit(self, surface: pygame.Surface, position: tuple[int, int]) -> None:
        dest_x = int(position[0] - self.offset.x)
        dest_y = int(position[1] - self.offset.y)
        self.view_surface.blit(surface, (dest_x, dest_y))

    def blit_rect(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        dest_rect = pygame.Rect(
            int(rect.x - self.offset.x),
            int(rect.y - self.offset.y),
            rect.width,
            rect.height,
        )
        self.view_surface.blit(surface, dest_rect)

    def present(self, screen: pygame.Surface) -> None:
        if self.zoom != 1.0:
            scaled = pygame.transform.smoothscale(
                self.view_surface, (self.screen_width, self.screen_height)
            )
            screen.blit(scaled, (0, 0))
        else:
            screen.blit(self.view_surface, (0, 0))

    def get_view_rect(self) -> pygame.Rect:
        return self.view_rect

    def _update_zoom(self) -> None:
        width_ratio = (
            self.base_view_width / self.screen_width if self.screen_width else 1.0
        )
        height_ratio = (
            self.base_view_height / self.screen_height if self.screen_height else 1.0
        )
        zoom = max(1.0, width_ratio, height_ratio)
        self.zoom = min(self.max_zoom, zoom)
        self.view_width = self.screen_width / self.zoom
        self.view_height = self.screen_height / self.zoom
        self.view_rect.size = (int(self.view_width), int(self.view_height))

    def _create_view_surface(self) -> None:
        size = (max(1, int(self.view_width)), max(1, int(self.view_height)))
        self.view_surface = pygame.Surface(size).convert()

    def _clamp_offset(self) -> None:
        if self.world_width > self.view_width:
            max_x = self.world_width - self.view_width
            self.offset.x = max(0, min(self.offset.x, max_x))
        if self.world_height > self.view_height:
            max_y = self.world_height - self.view_height
            self.offset.y = max(0, min(self.offset.y, max_y))
        self.view_rect.topleft = (int(self.offset.x), int(self.offset.y))
