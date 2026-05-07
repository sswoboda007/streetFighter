from __future__ import annotations

import math
import pygame
from game.engine.settings import SCREEN_W, SCREEN_H, COLORS


OPTIONS = [
    ('1 PLAYER  (vs AI)',   '1p'),
    ('2 PLAYERS  (local)',  '2p'),
    ('TOURNAMENT',          'tournament'),
]


class ModeSelectScene:
    def __init__(self) -> None:
        self._font_title = pygame.font.SysFont('impact', 52)
        self._font_opt   = pygame.font.SysFont('impact', 38)
        self._font_hint  = pygame.font.SysFont('arial', 20)
        self._sel = 0
        self._time = 0.0
        self.done = False
        self.next_scene = 'char_select'
        self.chosen_mode = '1p'

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self._sel = (self._sel - 1) % len(OPTIONS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._sel = (self._sel + 1) % len(OPTIONS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            label, mode = OPTIONS[self._sel]
            self.chosen_mode = mode
            if mode == 'tournament':
                self.next_scene = 'tournament'
            else:
                self.next_scene = 'char_select'
            self.done = True
        elif event.key == pygame.K_ESCAPE:
            self.next_scene = 'title'
            self.done = True

    def update(self, dt: float) -> None:
        self._time += dt

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((10, 8, 25))

        title = self._font_title.render('SELECT MODE', True, COLORS['yellow'])
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))

        cy = SCREEN_H // 2 - (len(OPTIONS) * 60) // 2
        for i, (label, _) in enumerate(OPTIONS):
            selected = i == self._sel
            pulse = int(200 + 55 * math.sin(self._time * 3)) if selected else 160
            col = (pulse, int(pulse * 0.9), 40) if selected else (120, 120, 140)

            if selected:
                arrow = self._font_opt.render('> ', True, COLORS['red'])
                screen.blit(arrow, (SCREEN_W // 2 - 180, cy))

            opt = self._font_opt.render(label, True, col)
            screen.blit(opt, (SCREEN_W // 2 - opt.get_width() // 2, cy))
            cy += 68

        hint = self._font_hint.render('W/S or arrows to navigate  |  ENTER to select  |  ESC back', True, (130, 130, 130))
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))
