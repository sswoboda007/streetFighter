from __future__ import annotations

import pygame
from game.engine.settings import SCREEN_W, SCREEN_H, COLORS, ROUNDS_TO_WIN


class HUD:
    def __init__(self) -> None:
        self._font_lg = pygame.font.SysFont('impact', 64)
        self._font_md = pygame.font.SysFont('impact', 36)
        self._font_sm = pygame.font.SysFont('arial', 22, bold=True)
        self._font_xs = pygame.font.SysFont('arial', 16)

    def draw(
        self,
        screen: pygame.Surface,
        p1_hp: float, p1_max: float, p1_wins: int,
        p2_hp: float, p2_max: float, p2_wins: int,
        time_left: float,
    ) -> None:
        bar_w = 440
        bar_h = 28
        margin = 30
        top = 18

        p1_frac = max(0.0, p1_hp / p1_max)
        p2_frac = max(0.0, p2_hp / p2_max)

        pygame.draw.rect(screen, COLORS['hud_bar_bg'], (margin, top, bar_w, bar_h), border_radius=4)
        p1_fill_w = int(bar_w * p1_frac)
        p1_col = _hp_color(p1_frac)
        pygame.draw.rect(screen, p1_col, (margin, top, p1_fill_w, bar_h), border_radius=4)
        pygame.draw.rect(screen, COLORS['hud_border'], (margin, top, bar_w, bar_h), 2, border_radius=4)

        p2_bar_x = SCREEN_W - margin - bar_w
        pygame.draw.rect(screen, COLORS['hud_bar_bg'], (p2_bar_x, top, bar_w, bar_h), border_radius=4)
        p2_fill_w = int(bar_w * p2_frac)
        p2_col = _hp_color(p2_frac)
        pygame.draw.rect(screen, p2_col,
            (p2_bar_x + bar_w - p2_fill_w, top, p2_fill_w, bar_h), border_radius=4)
        pygame.draw.rect(screen, COLORS['hud_border'], (p2_bar_x, top, bar_w, bar_h), 2, border_radius=4)

        p1_label = self._font_sm.render('P1', True, COLORS['white'])
        screen.blit(p1_label, (margin + 6, top + 4))
        p2_label = self._font_sm.render('P2', True, COLORS['white'])
        screen.blit(p2_label, (SCREEN_W - margin - 6 - p2_label.get_width(), top + 4))

        timer_str = str(max(0, int(time_left)))
        timer_surf = self._font_md.render(timer_str, True, COLORS['yellow'])
        screen.blit(timer_surf, (SCREEN_W // 2 - timer_surf.get_width() // 2, top - 2))

        dot_y = top + bar_h + 6
        dot_r = 7
        for i in range(ROUNDS_TO_WIN):
            col = COLORS['yellow'] if i < p1_wins else COLORS['shadow']
            pygame.draw.circle(screen, col, (margin + 20 + i * 22, dot_y + dot_r), dot_r)
            pygame.draw.circle(screen, COLORS['hud_border'], (margin + 20 + i * 22, dot_y + dot_r), dot_r, 2)

        for i in range(ROUNDS_TO_WIN):
            col = COLORS['yellow'] if i < p2_wins else COLORS['shadow']
            cx = SCREEN_W - margin - 20 - i * 22
            pygame.draw.circle(screen, col, (cx, dot_y + dot_r), dot_r)
            pygame.draw.circle(screen, COLORS['hud_border'], (cx, dot_y + dot_r), dot_r, 2)

    def draw_overlay(self, screen: pygame.Surface, text: str, sub: str = '') -> None:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        main_surf = self._font_lg.render(text, True, COLORS['yellow'])
        screen.blit(main_surf, (
            SCREEN_W // 2 - main_surf.get_width() // 2,
            SCREEN_H // 2 - main_surf.get_height() // 2 - 20,
        ))

        if sub:
            sub_surf = self._font_md.render(sub, True, COLORS['white'])
            screen.blit(sub_surf, (
                SCREEN_W // 2 - sub_surf.get_width() // 2,
                SCREEN_H // 2 + main_surf.get_height() // 2,
            ))

    def draw_controls(self, screen: pygame.Surface) -> None:
        lines = [
            'P1: A/D move  W jump  S crouch  F block  J light punch  K heavy punch  H light kick  L heavy kick',
            'P2: Arrow keys move  Num1 light punch  Num2 heavy punch  Num4 light kick  Num5 heavy kick  Num0 block',
            'Special: crouch then forward + J (P1) or down then right + Num1 (P2)',
        ]
        y = SCREEN_H - 14 * len(lines) - 4
        for line in lines:
            surf = self._font_xs.render(line, True, (180, 180, 180))
            screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))
            y += 15


def _hp_color(frac: float) -> tuple:
    if frac > 0.5:
        return (0, 200, 60)
    elif frac > 0.25:
        return (220, 180, 0)
    else:
        return (220, 40, 20)
