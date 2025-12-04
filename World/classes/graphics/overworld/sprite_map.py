from typing import List, Optional, Union
from pathlib import Path
import inspect
from classes.utils.util_logging import graphics_logger as log
import pygame

 
class SpriteMap:    
    
    def __init__(self, sprite_map_path, transparent_color=None, sprite_dimensions=(16,16), left_border=0, top_border=0, right_border=0, bottom_border=0, between_border=0):
        """If initialized with a sprite_map_path, automatically loads it"""
        #TODO replace default variable assignments with if-not none checks to fix linting issues
        locals_copy = locals().copy()  # Make a copy of local variables to avoid modifying the actual locals during iteration
        for name, value in locals_copy.items():
            if name != 'self':
                setattr(self, name, value)
        self.load_map()
        
    def load_map(self):
        """Loads the map with pygame and converts the alpha"""
        sprite_map = pygame.image.load(self.sprite_map_path)
        if self.transparent_color is None:
            self.sprite_map = sprite_map.convert_alpha()
        else:
            self.sprite_map = sprite_map.convert()
            self.sprite_map.set_colorkey(self.transparent_color)
        
    def convert_to_list(self):
        """Make a list of sprites from the sprite sheet.
        """
        pass
    
    def get_sprite(self, x, y) -> pygame.Surface:
        """ Extracts and returns a single sprite from a sprite sheet. """
        
        #Surface that the selection of sprite map will be blitted on to
        sprite = pygame.Surface((self.sprite_dimensions[0], self.sprite_dimensions[1]), pygame.SRCALPHA)
        # sprite.blit(self.sprite_map, (0, 0), (x, y, self.sprite_dimensions[0], self.sprite_dimensions[1]))
        
        # Grabs sprite at x,y coord and blits it to Surface
        sprite.blit(self.sprite_map, (0, 0), (self.left_border + x*(self.sprite_dimensions[0]+self.between_border), 
                                              self.top_border + y*(self.sprite_dimensions[1]+self.between_border), 
                                              self.sprite_dimensions[0], 
                                              self.sprite_dimensions[1]))
        
        # Scales up Surface + Sprite blitted on to it
        sprite = pygame.transform.smoothscale(
            sprite,
            (self.sprite_dimensions[0] * 3, self.sprite_dimensions[1] * 3),
        ).convert_alpha()
        return sprite
    
    def get_animated_sprite(self, forward: List[tuple], backward: List[tuple], left: List[tuple], right=None):
        if right is None:
            right=left
            #FLIP THEM!!
            
        args = locals()
        del args["self"]
        # print(args)
        
        sprite = {}
        for direction,coords in args.items():
            sprite[direction] = [self.get_sprite(x,y) for x,y in coords]
            
        return sprite
        
        

SurfaceInput = Union[str, Path, pygame.Surface]

_SPRITE_MAP_SIGNATURE = inspect.signature(SpriteMap.__init__)
_SPRITE_MAP_DEFAULTS = {
    "sprite_dimensions": _SPRITE_MAP_SIGNATURE.parameters["sprite_dimensions"].default,
    "left_border": _SPRITE_MAP_SIGNATURE.parameters["left_border"].default,
    "top_border": _SPRITE_MAP_SIGNATURE.parameters["top_border"].default,
    "right_border": _SPRITE_MAP_SIGNATURE.parameters["right_border"].default,
    "bottom_border": _SPRITE_MAP_SIGNATURE.parameters["bottom_border"].default,
    "between_border": _SPRITE_MAP_SIGNATURE.parameters["between_border"].default,
}


def blit_png_groups_to_sprite_map(
    file_path: str,
    y_position: int,
    png_groups: List[List[SurfaceInput]],
    *,
    sprite_dimensions: Optional[tuple[int, int]] = None,
    left_border: Optional[int] = None,
    top_border: Optional[int] = None,
    right_border: Optional[int] = None,
    bottom_border: Optional[int] = None,
    between_border: Optional[int] = None,
) -> pygame.Surface:
    """Blit provided PNG frames into a sprite sheet row, creating or updating the file."""

    if y_position < 0:
        raise ValueError("y_position must be non-negative")
    if not png_groups or not any(png_groups):
        raise ValueError("png_groups must contain at least one PNG entry")

    sprite_dimensions = sprite_dimensions or _SPRITE_MAP_DEFAULTS["sprite_dimensions"]
    left_border = _SPRITE_MAP_DEFAULTS["left_border"] if left_border is None else left_border
    top_border = _SPRITE_MAP_DEFAULTS["top_border"] if top_border is None else top_border
    right_border = _SPRITE_MAP_DEFAULTS["right_border"] if right_border is None else right_border
    bottom_border = _SPRITE_MAP_DEFAULTS["bottom_border"] if bottom_border is None else bottom_border
    between_border = _SPRITE_MAP_DEFAULTS["between_border"] if between_border is None else between_border

    sprite_width, sprite_height = sprite_dimensions
    frames: List[pygame.Surface] = []
    for group in png_groups:
        if not isinstance(group, (list, tuple)):
            raise TypeError("png_groups must be a list of lists or tuples")
        for entry in group:
            if isinstance(entry, pygame.Surface):
                surface = entry.convert_alpha()
            else:
                entry_path = Path(entry)
                if not entry_path.is_file():
                    raise FileNotFoundError(f"PNG not found: {entry_path}")
                surface = pygame.image.load(entry_path.as_posix()).convert_alpha()
            if surface.get_size() != sprite_dimensions:
                surface = pygame.transform.smoothscale(surface, sprite_dimensions).convert_alpha()
            frames.append(surface)

    total_columns = len(frames)
    if total_columns == 0:
        raise ValueError("png_groups must contain at least one PNG entry")

    row_y_offset = top_border + y_position * (sprite_height + between_border)
    required_width = left_border + total_columns * sprite_width + max(0, total_columns - 1) * between_border + right_border
    required_height = row_y_offset + sprite_height + bottom_border

    target_path = Path(file_path)
    existing_surface: Optional[pygame.Surface] = None
    if target_path.is_file():
        existing_surface = pygame.image.load(target_path.as_posix()).convert_alpha()

    width = max(required_width, existing_surface.get_width() if existing_surface else 0)
    height = max(required_height, existing_surface.get_height() if existing_surface else 0)

    sheet_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    sheet_surface.fill((0, 0, 0, 0))
    if existing_surface:
        sheet_surface.blit(existing_surface, (0, 0))

    for index, frame in enumerate(frames):
        dest_x = left_border + index * (sprite_width + between_border)
        sheet_surface.blit(frame, (dest_x, row_y_offset))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet_surface, target_path.as_posix())
    return sheet_surface
