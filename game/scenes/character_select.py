from __future__ import annotations

import math
import pygame
from game.engine.settings import SCREEN_W, SCREEN_H, COLORS, PALETTE, FIGHTER_W, FIGHTER_H


ROSTER = [
    {'name': 'Ryu',     'health': 100, 'strength': 12, 'agility': 8,  'special_skills': ['Hadoken']},
    {'name': 'Chun-Li', 'health': 90,  'strength': 10, 'agility': 14, 'special_skills': ['Lightning Kick']},
    {'name': 'Ken',     'health': 100, 'strength': 13, 'agility': 9,  'special_skills': ['Shoryuken']},
    {'name': 'Zangief', 'health': 120, 'strength': 15, 'agility': 5,  'special_skills': ['Spinning Piledriver']},
]


def _draw_mini_fighter(surf: pygame.Surface, x: int, y: int, name: str, scale: float = 1.0) -> None:
    pal = PALETTE.get(name, {
        'skin': (242, 194, 139), 'gi': (150, 150, 150),
        'belt': (34, 34, 34), 'hair': (34, 34, 34), 'accent': (200, 200, 50),
    })
    skin = pal['skin']; gi = pal['gi']; belt = pal['belt']
    hair = pal['hair']; accent = pal['accent']

    w = int(FIGHTER_W * scale)
    h = int(FIGHTER_H * scale)
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)

    cx = w // 2
    head_r = int(14 * scale)
    head_cy = int(16 * scale)
    pygame.draw.circle(tmp, skin, (cx, head_cy), head_r)
    pygame.draw.ellipse(tmp, hair, (cx - head_r, head_cy - head_r, head_r * 2, head_r))
    pygame.draw.circle(tmp, (30, 20, 10), (cx + int(5 * scale), head_cy - int(2 * scale)), max(1, int(2 * scale)))

    torso_top = head_cy + head_r
    torso_h = int(44 * scale)
    torso_w = int(32 * scale)
    pygame.draw.rect(tmp, gi, (cx - torso_w // 2, torso_top, torso_w, torso_h))
    belt_y = torso_top + torso_h // 2
    pygame.draw.rect(tmp, belt, (cx - torso_w // 2, belt_y, torso_w, int(6 * scale)))

    waist_y = torso_top + torso_h
    leg_len = int(44 * scale)
    leg_w = max(3, int(12 * scale))
    pygame.draw.line(tmp, gi, (cx - int(8 * scale), waist_y), (cx - int(10 * scale), waist_y + leg_len), leg_w)
    pygame.draw.line(tmp, gi, (cx + int(8 * scale), waist_y), (cx + int(10 * scale), waist_y + leg_len), leg_w)
    pygame.draw.circle(tmp, accent, (cx - int(10 * scale), waist_y + leg_len), max(3, int(7 * scale)))
    pygame.draw.circle(tmp, accent, (cx + int(10 * scale), waist_y + leg_len), max(3, int(7 * scale)))

    surf.blit(tmp, (x - w // 2, y - h // 2))


class CharSelectScene:
    def __init__(self) -> None:
        self._font_title = pygame.font.SysFont('impact', 48)
        self._font_name  = pygame.font.SysFont('impact', 28)
        self._font_stat  = pygame.font.SysFont('arial', 16)
        self._font_hint  = pygame.font.SysFont('arial', 18)
        self._font_mode  = pygame.font.SysFont('impact', 24)

        self.p1_sel = 0
        self.p2_sel = 1
        self._p1_confirmed = False
        self._p2_confirmed = False

        self.done = False
        self.next_scene = 'fight'
        self.p1_char: dict | None = None
        self.p2_char: dict | None = None
        self.mode = '1p'  # '1p' or '2p'
        self._time = 0.0

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if not self._p1_confirmed:
            if event.key == pygame.K_a:
                self.p1_sel = (self.p1_sel - 1) % len(ROSTER)
            elif event.key == pygame.K_d:
                self.p1_sel = (self.p1_sel + 1) % len(ROSTER)
            elif event.key in (pygame.K_j, pygame.K_k, pygame.K_RETURN):
                self._p1_confirmed = True

        if self.mode == '2p' and not self._p2_confirmed:
            if event.key == pygame.K_LEFT:
                self.p2_sel = (self.p2_sel - 1) % len(ROSTER)
            elif event.key == pygame.K_RIGHT:
                self.p2_sel = (self.p2_sel + 1) % len(ROSTER)
            elif event.key in (pygame.K_KP1, pygame.K_KP2):
                self._p2_confirmed = True

        if event.key == pygame.K_ESCAPE:
            self.next_scene = 'title'
            self.done = True

        self._check_ready()

    def _check_ready(self) -> None:
        if self.mode == '1p' and self._p1_confirmed:
            self.p1_char = ROSTER[self.p1_sel]
            opponents = [r for i, r in enumerate(ROSTER) if i != self.p1_sel]
            import random
            self.p2_char = random.choice(opponents)
            self.done = True
        elif self.mode == '2p' and self._p1_confirmed and self._p2_confirmed:
            self.p1_char = ROSTER[self.p1_sel]
            self.p2_char = ROSTER[self.p2_sel]
            self.done = True

    def update(self, dt: float) -> None:
        self._time += dt

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((15, 10, 30))

        title = self._font_title.render('SELECT YOUR FIGHTER', True, COLORS['yellow'])
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))

        mode_str = '1P vs AI' if self.mode == '1p' else '2 PLAYER'
        mode_surf = self._font_mode.render(mode_str, True, (180, 120, 60))
        screen.blit(mode_surf, (SCREEN_W // 2 - mode_surf.get_width() // 2, 85))

        card_w = 210
        card_h = 300
        cols = len(ROSTER)
        spacing = 20
        total_w = cols * card_w + (cols - 1) * spacing
        start_x = (SCREEN_W - total_w) // 2
        card_y = 130

        for i, char in enumerate(ROSTER):
            cx = start_x + i * (card_w + spacing)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)

            is_p1 = (i == self.p1_sel)
            is_p2 = (i == self.p2_sel) and self.mode == '2p'

            bg_col = (35, 25, 50)
            if is_p1 or is_p2:
                bg_col = (50, 35, 70)
            pygame.draw.rect(screen, bg_col, card_rect, border_radius=8)

            border_col = (60, 40, 80)
            border_w = 2
            if is_p1:
                border_col = (0, 220, 60)
                border_w = 3
            if is_p2:
                border_col = (0, 180, 220)
                border_w = 3
            pygame.draw.rect(screen, border_col, card_rect, border_w, border_radius=8)

            mid_x = cx + card_w // 2
            _draw_mini_fighter(screen, mid_x, card_y + 130, char['name'], scale=1.2)

            name_surf = self._font_name.render(char['name'], True, COLORS['white'])
            screen.blit(name_surf, (mid_x - name_surf.get_width() // 2, card_y + 220))

            stats = [
                f"HP  {char['health']}",
                f"STR {char['strength']}",
                f"AGI {char['agility']}",
                f"Special: {char['special_skills'][0]}",
            ]
            for j, line in enumerate(stats):
                s = self._font_stat.render(line, True, (180, 180, 200))
                screen.blit(s, (cx + 10, card_y + 248 + j * 16))

            if is_p1:
                tag = self._font_stat.render('P1', True, (0, 220, 60))
                screen.blit(tag, (cx + 6, card_y + 6))
            if is_p2:
                tag = self._font_stat.render('P2', True, (0, 180, 220))
                screen.blit(tag, (cx + card_w - tag.get_width() - 6, card_y + 6))

        hint_lines = [
            'P1: A/D to select  |  J or ENTER to confirm',
        ]
        if self.mode == '2p':
            hint_lines.append('P2: LEFT/RIGHT to select  |  Num1 to confirm')
        hint_lines.append('ESC = back')
        y = SCREEN_H - 18 * len(hint_lines) - 8
        for line in hint_lines:
            s = self._font_hint.render(line, True, (160, 160, 160))
            screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, y))
            y += 18
