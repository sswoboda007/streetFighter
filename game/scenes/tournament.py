from __future__ import annotations

import pygame
from models.character import Character
from tournaments import Tournament
from game.engine.settings import SCREEN_W, SCREEN_H, COLORS


_ROSTER = [
    Character('Ryu',     100, 12, 8,  ['Hadoken']),
    Character('Chun-Li', 90,  10, 14, ['Lightning Kick']),
    Character('Ken',     100, 13, 9,  ['Shoryuken']),
    Character('Zangief', 120, 15, 5,  ['Spinning Piledriver']),
]


class TournamentScene:
    def __init__(self) -> None:
        self._font_title = pygame.font.SysFont('impact', 48)
        self._font_md    = pygame.font.SysFont('impact', 28)
        self._font_sm    = pygame.font.SysFont('arial', 18)
        self._result: dict | None = None
        self.done = False
        self.next_scene = 'title'
        self._run()

    def _run(self) -> None:
        t = Tournament('World Warriors', list(_ROSTER), format='single_elimination')
        t.run()
        self._result = t.to_dict()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self.done = True

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((10, 10, 25))
        r = self._result
        if not r:
            return

        title = self._font_title.render('TOURNAMENT RESULTS', True, COLORS['yellow'])
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))

        champ = self._font_md.render(f"Champion: {r['champion']}", True, COLORS['white'])
        screen.blit(champ, (SCREEN_W // 2 - champ.get_width() // 2, 110))

        y = 160
        for rnd_i, rnd in enumerate(r['bracket']):
            rnd_surf = self._font_sm.render(f'--- Round {rnd_i + 1} ---', True, (160, 120, 60))
            screen.blit(rnd_surf, (SCREEN_W // 2 - rnd_surf.get_width() // 2, y))
            y += 22
            for match in rnd:
                line = f"{match['fighter_a']}  vs  {match['fighter_b']}   →  Winner: {match['winner']}"
                m_surf = self._font_sm.render(line, True, (200, 200, 220))
                screen.blit(m_surf, (SCREEN_W // 2 - m_surf.get_width() // 2, y))
                y += 22
            y += 10

        hint = self._font_sm.render('Press any key to return', True, (130, 130, 130))
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))
