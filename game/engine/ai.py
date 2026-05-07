from __future__ import annotations

import random
from game.engine.fighter import State


DIFFICULTY = {
    'easy':   {'react_delay': 0.6, 'aggression': 0.3, 'block_chance': 0.1},
    'medium': {'react_delay': 0.3, 'aggression': 0.6, 'block_chance': 0.25},
    'hard':   {'react_delay': 0.1, 'aggression': 0.85, 'block_chance': 0.45},
}


class FakeInput:
    """Mimics InputState interface for AI-driven fighter."""

    def __init__(self) -> None:
        self._held: set[str] = set()
        self._pressed: set[str] = set()

    def _set(self, held: set[str], pressed: set[str]) -> None:
        self._held = held
        self._pressed = pressed

    def held(self, action: str) -> bool:
        return action in self._held

    def pressed(self, action: str) -> bool:
        return action in self._pressed

    def released(self, action: str) -> bool:
        return False

    def check_qcf(self) -> bool:
        return False

    def clear_motion(self) -> None:
        pass

    def tick(self) -> None:
        self._pressed.clear()


class AIController:
    def __init__(self, level: str = 'medium') -> None:
        cfg = DIFFICULTY.get(level, DIFFICULTY['medium'])
        self._react_delay: float = cfg['react_delay']
        self._aggression: float = cfg['aggression']
        self._block_chance: float = cfg['block_chance']
        self._timer = 0.0
        self._decision_interval = 0.15
        self._current_held: set[str] = set()
        self._current_pressed: set[str] = set()
        self.input = FakeInput()

    def update(self, dt: float, ai_fighter, player_fighter) -> None:
        self._timer += dt
        if self._timer < self._decision_interval:
            self.input._set(self._current_held, set())
            return
        self._timer = 0.0
        self._decide(ai_fighter, player_fighter)
        self.input._set(self._current_held, self._current_pressed)

    def _decide(self, me, opp) -> None:
        from game.engine.fighter import ATTACK_RANGE, State
        self._current_held.clear()
        self._current_pressed.clear()

        if me.state in (State.HIT_STUN, State.BLOCK_STUN, State.KO):
            return

        dist = abs(me.x - opp.x)
        low_hp = me.hp / me.max_hp < 0.35

        if random.random() < self._block_chance and opp.state in (
            State.LIGHT_PUNCH, State.HEAVY_PUNCH, State.LIGHT_KICK,
            State.HEAVY_KICK, State.SPECIAL,
        ):
            self._current_held.add('block')
            return

        move_dir = 'right' if opp.x > me.x else 'left'
        retreat  = 'left'  if opp.x > me.x else 'right'

        if dist > 160:
            if random.random() < self._aggression:
                self._current_held.add(move_dir)
        elif dist < 60:
            self._current_held.add(retreat)
        else:
            if random.random() < self._aggression:
                attack = random.choice(['light_punch', 'heavy_punch', 'light_kick', 'heavy_kick'])
                self._current_pressed.add(attack)
                if low_hp and random.random() < 0.3:
                    self._current_pressed.discard(attack)
