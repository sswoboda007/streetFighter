from __future__ import annotations

import math
import pygame
from game.engine.settings import (
    SCREEN_W, SCREEN_H, FLOOR_Y, ARENA_LEFT, ARENA_RIGHT, COLORS
)


def _lerp_color(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Arena:
    def __init__(self) -> None:
        self._time = 0.0
        self._shake_timer = 0.0
        self._shake_strength = 0
        self._offset = (0, 0)
        self._build_surface()

    def _build_surface(self) -> None:
        self._surf = pygame.Surface((SCREEN_W, SCREEN_H))
        sky_top = (20, 10, 40)
        sky_bot = (80, 30, 60)
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            c = _lerp_color(sky_top, sky_bot, t)
            pygame.draw.line(self._surf, c, (0, y), (SCREEN_W, y))

        floor_color = (60, 35, 20)
        floor_line = (100, 70, 40)
        pygame.draw.rect(self._surf, floor_color, (0, FLOOR_Y, SCREEN_W, SCREEN_H - FLOOR_Y))
        pygame.draw.line(self._surf, floor_line, (0, FLOOR_Y), (SCREEN_W, FLOOR_Y), 3)

        for i in range(0, SCREEN_W, 80):
            pygame.draw.line(self._surf, floor_line, (i, FLOOR_Y), (i, SCREEN_H), 1)

        for i, x in enumerate(range(100, SCREEN_W - 100, 220)):
            building_h = 180 + (i % 3) * 40
            b_color = (30 + i * 5, 20 + i * 3, 50 + i * 4)
            pygame.draw.rect(self._surf, b_color, (x, FLOOR_Y - building_h, 120, building_h))
            win_color = (200, 180, 80)
            for wy in range(FLOOR_Y - building_h + 15, FLOOR_Y - 10, 30):
                for wx in range(x + 10, x + 110, 25):
                    pygame.draw.rect(self._surf, win_color, (wx, wy, 14, 18))

        crowd_y = FLOOR_Y - 30
        for cx in range(0, SCREEN_W, 18):
            crowd_c = (80 + (cx % 40), 30, 60 + (cx % 30))
            pygame.draw.circle(self._surf, crowd_c, (cx + 9, crowd_y), 8)

    def trigger_shake(self, strength: int = 8, duration: float = 0.3) -> None:
        self._shake_strength = strength
        self._shake_timer = duration

    def update(self, dt: float) -> None:
        self._time += dt
        if self._shake_timer > 0:
            self._shake_timer -= dt
            import random
            s = self._shake_strength
            self._offset = (random.randint(-s, s), random.randint(-s, s))
        else:
            self._offset = (0, 0)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._surf, self._offset)
