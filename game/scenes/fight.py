from __future__ import annotations

import pygame
from models.character import Character
from game.engine.fighter import Fighter, State
from game.engine.arena import Arena
from game.engine.hud import HUD
from game.engine.input_handler import InputState, P1_BINDINGS, P2_BINDINGS
from game.engine.ai import AIController
from game.engine.settings import (
    SCREEN_W, SCREEN_H, ROUND_TIME, ROUNDS_TO_WIN, FLOOR_Y, FIGHTER_W, COLORS
)


class _Phase:
    INTRO   = 'intro'
    FIGHT   = 'fight'
    KO      = 'ko'
    TIMEOUT = 'timeout'
    RESULTS = 'results'


class FightScene:
    def __init__(self, p1_data: dict, p2_data: dict, mode: str = '1p') -> None:
        self._p1_data = p1_data
        self._p2_data = p2_data
        self._mode = mode

        self._arena = Arena()
        self._hud   = HUD()

        self._inp1 = InputState(P1_BINDINGS)
        self._inp2 = InputState(P2_BINDINGS)
        self._ai   = AIController('medium') if mode == '1p' else None

        self._p1_wins = 0
        self._p2_wins = 0

        self.done = False
        self.next_scene = 'results'
        self.winner_name = ''

        self._phase = _Phase.INTRO
        self._phase_timer = 0.0

        self._font_ko  = pygame.font.SysFont('impact', 80)
        self._font_rnd = pygame.font.SysFont('impact', 54)
        self._font_sm  = pygame.font.SysFont('arial', 22)

        self._round = 1
        self._round_time = float(ROUND_TIME)

        self._spawn()

    def _spawn(self) -> None:
        def make(data: dict) -> Fighter:
            c = Character(
                data['name'], data['health'], data['strength'],
                data['agility'], data['special_skills'],
            )
            return c

        p1c = make(self._p1_data)
        p2c = make(self._p2_data)

        self._p1 = Fighter(p1c, SCREEN_W * 0.28, facing=1)
        self._p2 = Fighter(p2c, SCREEN_W * 0.65, facing=-1)

        self._phase = _Phase.INTRO
        self._phase_timer = 0.0
        self._round_time = float(ROUND_TIME)
        self._inp1.tick()
        self._inp2.tick()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
            self.next_scene = 'title'
            return
        self._inp1.process_event(event)
        self._inp2.process_event(event)

    def update(self, dt: float) -> None:
        self._arena.update(dt)
        self._phase_timer += dt

        if self._phase == _Phase.INTRO:
            if self._phase_timer >= 2.0:
                self._phase = _Phase.FIGHT
                self._phase_timer = 0.0
            return

        if self._phase == _Phase.KO or self._phase == _Phase.TIMEOUT:
            if self._phase_timer >= 2.5:
                self._next_round_or_end()
            return

        if self._phase == _Phase.RESULTS:
            if self._phase_timer >= 1.5:
                self.done = True
            return

        self._round_time -= dt
        if self._round_time <= 0:
            self._round_time = 0
            self._phase = _Phase.TIMEOUT
            self._phase_timer = 0.0
            self._award_timeout()
            return

        if self._ai:
            self._ai.update(dt, self._p2, self._p1)
            p2_inp = self._ai.input
        else:
            p2_inp = self._inp2

        self._p1.update(dt, self._inp1, self._p2)
        self._p2.update(dt, p2_inp, self._p1)

        self._inp1.tick()
        self._inp2.tick()
        if self._ai:
            self._ai.input.tick()

        if self._p1.state == State.KO:
            self._arena.trigger_shake(10, 0.5)
            self._p2_wins += 1
            self._phase = _Phase.KO
            self._phase_timer = 0.0
        elif self._p2.state == State.KO:
            self._arena.trigger_shake(10, 0.5)
            self._p1_wins += 1
            self._phase = _Phase.KO
            self._phase_timer = 0.0

    def _award_timeout(self) -> None:
        if self._p1.hp >= self._p2.hp:
            self._p1_wins += 1
        else:
            self._p2_wins += 1

    def _next_round_or_end(self) -> None:
        if self._p1_wins >= ROUNDS_TO_WIN:
            self.winner_name = self._p1_data['name'] + ' (P1)'
            self._phase = _Phase.RESULTS
            self._phase_timer = 0.0
        elif self._p2_wins >= ROUNDS_TO_WIN:
            label = self._p2_data['name']
            label += ' (AI)' if self._mode == '1p' else ' (P2)'
            self.winner_name = label
            self._phase = _Phase.RESULTS
            self._phase_timer = 0.0
        else:
            self._round += 1
            self._spawn()

    def draw(self, screen: pygame.Surface) -> None:
        self._arena.draw(screen)
        self._p1.draw(screen)
        self._p2.draw(screen)

        self._hud.draw(
            screen,
            self._p1.hp, self._p1.max_hp, self._p1_wins,
            self._p2.hp, self._p2.max_hp, self._p2_wins,
            self._round_time,
        )
        self._hud.draw_controls(screen)

        if self._phase == _Phase.INTRO:
            alpha = min(1.0, self._phase_timer / 0.4)
            rnd_str = f'ROUND  {self._round}'
            fight_str = 'FIGHT!'
            self._hud.draw_overlay(screen, rnd_str, fight_str if self._phase_timer > 1.0 else '')

        elif self._phase == _Phase.KO:
            ko_winner = 'P1' if self._p1.state != State.KO else 'P2'
            self._hud.draw_overlay(screen, 'K.O.', f'{ko_winner} wins the round!')

        elif self._phase == _Phase.TIMEOUT:
            self._hud.draw_overlay(screen, 'TIME!', 'Judge decision...')

        elif self._phase == _Phase.RESULTS:
            self._hud.draw_overlay(screen, self.winner_name, 'WINS!')
