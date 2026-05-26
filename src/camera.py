import pygame
from data.gameSetting import WINDOW_WIDTH, TILE_SIZE, LEVEL_COLS


class Camera:
    """
    Horizontal-only scrolling camera.

    Usage:
        camera.follow(player.rect)          # call once per frame
        screen_rect = camera.apply(world_rect)  # convert world → screen coords
        draw_thing(surface, camera.offset_x)    # pass offset to draw functions
    """

    def __init__(self):
        self.offset_x   = 0
        self.level_width = LEVEL_COLS * TILE_SIZE   # total pixel width of the level

    def follow(self, target_rect):
        """Center camera on the target, clamped so we never show past level edges."""
        desired = target_rect.centerx - WINDOW_WIDTH // 2
        max_offset = max(0, self.level_width - WINDOW_WIDTH)
        self.offset_x = max(0, min(desired, max_offset))

    def apply(self, world_rect):
        """Return a new Rect shifted from world coordinates to screen coordinates."""
        return pygame.Rect(
            world_rect.x - self.offset_x,
            world_rect.y,
            world_rect.width,
            world_rect.height,
        )
