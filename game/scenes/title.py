from __future__ import annotations

import math
import pygame
from game.engine.settings import SCREEN_W, SCREEN_H, COLORS


class TitleScene:
    def __init__(self) -> None:
        self._font_title = pygame.font.SysFont('impact', 96)
        self._font_sub   = pygame.font.SysFont('impact', 36)
        self._font_hint  = pygame.font.SysFont('arial', 22)
        self._time = 0.0
        self.done = False
        self.next_scene = 'char_select'
        self._bg = self._build_bg()

    def _build_bg(self) -> pygame.Surface:
        surf = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(10 + 30 * t)
            g = int(5 + 5 * t)
            b = int(20 + 20 * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))
        return surf

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                self.done = True

    def update(self, dt: float) -> None:
        self._time += dt

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._bg, (0, 0))

        t = self._time
        glow = int(200 + 55 * math.sin(t * 2))
        title_col = (glow, int(glow * 0.9), 50)

        title1 = self._font_title.render('STREET', True, title_col)
        title2 = self._font_title.render('FIGHTER', True, title_col)

        shadow_col = (60, 20, 0)
        sh1 = self._font_title.render('STREET', True, shadow_col)
        sh2 = self._font_title.render('FIGHTER', True, shadow_col)

        cx = SCREEN_W // 2
        y1 = SCREEN_H // 2 - 120
        y2 = y1 + title1.get_height() - 10

        screen.blit(sh1, (cx - sh1.get_width() // 2 + 4, y1 + 4))
        screen.blit(sh2, (cx - sh2.get_width() // 2 + 4, y2 + 4))
        screen.blit(title1, (cx - title1.get_width() // 2, y1))
        screen.blit(title2, (cx - title2.get_width() // 2, y2))

        sub = self._font_sub.render('II  TURBO', True, (200, 60, 60))
        screen.blit(sub, (cx - sub.get_width() // 2, y2 + title2.get_height() - 10))

        blink_alpha = int(128 + 127 * math.sin(t * 3))
        hint = self._font_hint.render('PRESS ENTER TO START', True, (255, 255, 255))
        hint.set_alpha(blink_alpha)
        screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 100))

        mode_hint = self._font_hint.render('1P vs AI  |  2P Local', True, (160, 160, 160))
        screen.blit(mode_hint, (cx - mode_hint.get_width() // 2, SCREEN_H - 65))
