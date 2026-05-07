from __future__ import annotations

import math
import pygame
from game.engine.settings import SCREEN_W, SCREEN_H, COLORS


class ResultsScene:
    def __init__(self, winner: str) -> None:
        self._winner = winner
        self._font_lg = pygame.font.SysFont('impact', 72)
        self._font_md = pygame.font.SysFont('impact', 42)
        self._font_sm = pygame.font.SysFont('arial', 24)
        self._time = 0.0
        self.done = False
        self.next_scene = 'title'

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER,
                             pygame.K_ESCAPE, pygame.K_r):
                self.next_scene = 'char_select' if event.key == pygame.K_r else 'title'
                self.done = True

    def update(self, dt: float) -> None:
        self._time += dt

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((5, 5, 15))

        t = self._time
        pulse = int(200 + 55 * math.sin(t * 2.5))
        win_col = (pulse, int(pulse * 0.85), 30)

        w_surf = self._font_lg.render(self._winner, True, win_col)
        screen.blit(w_surf, (SCREEN_W // 2 - w_surf.get_width() // 2, SCREEN_H // 2 - 100))

        wins_surf = self._font_md.render('WINS!', True, COLORS['red'])
        screen.blit(wins_surf, (SCREEN_W // 2 - wins_surf.get_width() // 2, SCREEN_H // 2 - 10))

        blink = int(128 + 127 * math.sin(t * 3))
        r_hint = self._font_sm.render('R = Rematch   |   ENTER = Title', True, (200, 200, 200))
        r_hint.set_alpha(blink)
        screen.blit(r_hint, (SCREEN_W // 2 - r_hint.get_width() // 2, SCREEN_H // 2 + 100))
