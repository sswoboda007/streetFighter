from __future__ import annotations

import math
import pygame
from enum import Enum, auto
from models.character import Character
from game.engine.settings import (
    FLOOR_Y, GRAVITY, JUMP_VY, WALK_SPEED, JUMP_SPEED_X,
    HIT_STUN_FRAMES, BLOCK_STUN_FRAMES, KNOCKBACK_VX,
    BLOCK_DAMAGE_MULT, SPECIAL_COOLDOWN,
    ARENA_LEFT, ARENA_RIGHT, FIGHTER_W, FIGHTER_H, PALETTE, FPS,
)


class State(Enum):
    IDLE    = auto()
    WALK_F  = auto()
    WALK_B  = auto()
    JUMP    = auto()
    CROUCH  = auto()
    LIGHT_PUNCH  = auto()
    HEAVY_PUNCH  = auto()
    LIGHT_KICK   = auto()
    HEAVY_KICK   = auto()
    SPECIAL      = auto()
    BLOCK        = auto()
    HIT_STUN     = auto()
    BLOCK_STUN   = auto()
    KO           = auto()


ATTACK_STATES = {
    State.LIGHT_PUNCH, State.HEAVY_PUNCH,
    State.LIGHT_KICK,  State.HEAVY_KICK,
    State.SPECIAL,
}

ATTACK_DURATION = {
    State.LIGHT_PUNCH: 0.20,
    State.HEAVY_PUNCH: 0.35,
    State.LIGHT_KICK:  0.22,
    State.HEAVY_KICK:  0.40,
    State.SPECIAL:     0.50,
}

ATTACK_DAMAGE_MULT = {
    State.LIGHT_PUNCH: 1.0,
    State.HEAVY_PUNCH: 2.0,
    State.LIGHT_KICK:  1.0,
    State.HEAVY_KICK:  2.0,
    State.SPECIAL:     2.5,
}

ATTACK_RANGE = {
    State.LIGHT_PUNCH: 90,
    State.HEAVY_PUNCH: 110,
    State.LIGHT_KICK:  100,
    State.HEAVY_KICK:  120,
    State.SPECIAL:     400,
}

ATTACK_ACTIVE_START = 0.05  # fraction into animation when hitbox is active
ATTACK_ACTIVE_END   = 0.65


class Fighter:
    def __init__(self, char: Character, x: float, facing: int) -> None:
        self.char = char
        self.name = char.name
        self.max_hp = char.max_health
        self.hp = float(self.max_hp)
        self.x = float(x)
        self.y = float(FLOOR_Y - FIGHTER_H)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = facing  # +1 = right, -1 = left

        self._state = State.IDLE
        self._state_timer = 0.0
        self._anim_frame = 0
        self._anim_timer = 0.0

        self._special_cd = 0.0
        self._hit_this_attack = False

        self._round_wins = 0

        self._walk_anim_t = 0.0
        self._idle_anim_t = 0.0

        stats = char.to_game_stats()
        speed_scale = stats['move_speed'] / 280.0
        self._walk_speed = WALK_SPEED * speed_scale
        self._dmg_light = stats['damage_light']
        self._dmg_heavy = stats['damage_heavy']

    @property
    def state(self) -> State:
        return self._state

    @property
    def is_airborne(self) -> bool:
        return self.y < FLOOR_Y - FIGHTER_H - 1

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), FIGHTER_W, FIGHTER_H)

    def hitbox(self) -> pygame.Rect | None:
        if self._state not in ATTACK_STATES:
            return None
        dur = ATTACK_DURATION[self._state]
        frac = self._state_timer / dur if dur > 0 else 0
        if not (ATTACK_ACTIVE_START <= frac <= ATTACK_ACTIVE_END):
            return None
        reach = ATTACK_RANGE[self._state]
        if self.facing == 1:
            hx = self.x + FIGHTER_W
        else:
            hx = self.x - reach
        return pygame.Rect(int(hx), int(self.y + 20), reach, FIGHTER_H - 40)

    def set_state(self, new_state: State) -> None:
        self._state = new_state
        self._state_timer = 0.0
        self._hit_this_attack = False

    def face_opponent(self, opponent: 'Fighter') -> None:
        if self._state in (State.KO,):
            return
        if opponent.x > self.x:
            self.facing = 1
        else:
            self.facing = -1

    def apply_hit(self, dmg: float, attacker_x: float) -> None:
        if self._state == State.KO:
            return
        if self._state == State.BLOCK:
            actual = dmg * BLOCK_DAMAGE_MULT
            self.hp = max(0.0, self.hp - actual)
            self.set_state(State.BLOCK_STUN)
            return
        self.hp = max(0.0, self.hp - dmg)
        kb_dir = 1 if self.x > attacker_x else -1
        self.vx = kb_dir * KNOCKBACK_VX
        if self.hp <= 0:
            self.set_state(State.KO)
        else:
            self.set_state(State.HIT_STUN)

    def update(self, dt: float, inp, opponent: 'Fighter') -> None:
        self.face_opponent(opponent)
        self._special_cd = max(0.0, self._special_cd - dt)

        if self._state == State.KO:
            self._apply_physics(dt)
            return

        self._state_timer += dt

        if self._state == State.HIT_STUN:
            if self._state_timer >= HIT_STUN_FRAMES / FPS:
                self.set_state(State.IDLE)
            self._apply_physics(dt)
            return

        if self._state == State.BLOCK_STUN:
            if self._state_timer >= BLOCK_STUN_FRAMES / FPS:
                self.set_state(State.IDLE)
            self._apply_physics(dt)
            return

        if self._state in ATTACK_STATES:
            dur = ATTACK_DURATION[self._state]
            if self._state_timer >= dur:
                self.set_state(State.IDLE)
            else:
                self._try_deal_damage(opponent)
            self._apply_physics(dt)
            return

        self._handle_input(inp, opponent)
        self._apply_physics(dt)

    def _handle_input(self, inp, opponent: 'Fighter') -> None:
        moving_forward = inp.held('right') if self.facing == 1 else inp.held('left')
        moving_back    = inp.held('left')  if self.facing == 1 else inp.held('right')

        if inp.held('block') and not self.is_airborne:
            self.set_state(State.BLOCK)
            self.vx = 0
            return

        if inp.pressed('light_punch') and not self.is_airborne:
            self.set_state(State.LIGHT_PUNCH)
            self.vx = 0
            return
        if inp.pressed('heavy_punch') and not self.is_airborne:
            self.set_state(State.HEAVY_PUNCH)
            self.vx = 0
            return
        if inp.pressed('light_kick') and not self.is_airborne:
            self.set_state(State.LIGHT_KICK)
            self.vx = 0
            return
        if inp.pressed('heavy_kick') and not self.is_airborne:
            self.set_state(State.HEAVY_KICK)
            self.vx = 0
            return

        if inp.pressed('light_punch') and self._special_cd <= 0 and inp.check_qcf():
            self.set_state(State.SPECIAL)
            self._special_cd = SPECIAL_COOLDOWN
            inp.clear_motion()
            return

        if inp.pressed('jump') and not self.is_airborne:
            self.vy = JUMP_VY
            if moving_forward:
                self.vx = self.facing * JUMP_SPEED_X
            elif moving_back:
                self.vx = -self.facing * JUMP_SPEED_X
            else:
                self.vx = 0
            self.set_state(State.JUMP)
            return

        if inp.held('crouch') and not self.is_airborne:
            self.set_state(State.CROUCH)
            self.vx = 0
            return

        if moving_forward:
            self.vx = self.facing * self._walk_speed
            self.set_state(State.WALK_F)
        elif moving_back:
            self.vx = -self.facing * self._walk_speed
            self.set_state(State.WALK_B)
        else:
            self.vx = 0
            self.set_state(State.IDLE)

    def _try_deal_damage(self, opponent: 'Fighter') -> None:
        if self._hit_this_attack:
            return
        hb = self.hitbox()
        if hb is None:
            return
        opp_rect = opponent.rect()
        if hb.colliderect(opp_rect):
            mult = ATTACK_DAMAGE_MULT[self._state]
            if self._state in (State.LIGHT_PUNCH, State.LIGHT_KICK):
                base = self._dmg_light
            else:
                base = self._dmg_heavy
            opponent.apply_hit(base * mult, self.x)
            self._hit_this_attack = True

    def _apply_physics(self, dt: float) -> None:
        if self.is_airborne or self._state == State.JUMP:
            self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        ground = FLOOR_Y - FIGHTER_H
        if self.y >= ground:
            self.y = ground
            self.vy = 0.0
            self.vx = 0.0
            if self._state == State.JUMP:
                self.set_state(State.IDLE)

        self.x = max(float(ARENA_LEFT), min(self.x, float(ARENA_RIGHT - FIGHTER_W)))

    def draw(self, screen: pygame.Surface) -> None:
        self._draw_sprite(screen)

    def _draw_sprite(self, screen: pygame.Surface) -> None:
        pal = PALETTE.get(self.name, {
            'skin': (242, 194, 139), 'gi': (150, 150, 150),
            'belt': (34, 34, 34), 'hair': (34, 34, 34), 'accent': (200, 200, 50),
        })
        skin   = pal['skin']
        gi     = pal['gi']
        belt   = pal['belt']
        hair   = pal['hair']
        accent = pal['accent']

        x = int(self.x)
        y = int(self.y)
        f = self.facing
        w = FIGHTER_W
        h = FIGHTER_H

        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        anim_off = 0
        leg_spread = 0
        arm_raise = 0

        s = self._state
        t = self._state_timer

        if s in (State.IDLE,):
            anim_off = int(math.sin(pygame.time.get_ticks() * 0.003) * 2)
        elif s in (State.WALK_F, State.WALK_B):
            cycle = (pygame.time.get_ticks() % 400) / 400.0
            anim_off = int(math.sin(cycle * math.pi * 2) * 3)
            leg_spread = int(math.sin(cycle * math.pi * 2) * 10)
        elif s == State.CROUCH:
            anim_off = 12
        elif s == State.JUMP:
            anim_off = -4
            leg_spread = -6
        elif s in (State.LIGHT_PUNCH, State.HEAVY_PUNCH, State.SPECIAL):
            arm_raise = -20 if t < 0.12 else -8
        elif s in (State.LIGHT_KICK, State.HEAVY_KICK):
            leg_spread = 14 if t < 0.15 else 6
        elif s in (State.HIT_STUN, State.BLOCK_STUN):
            anim_off = 4
            arm_raise = 5
        elif s == State.BLOCK:
            arm_raise = -10
        elif s == State.KO:
            anim_off = h - 20
            leg_spread = 20

        head_cx = w // 2
        head_cy = 16 + anim_off
        head_r = 14

        pygame.draw.circle(surf, skin, (head_cx, head_cy), head_r)

        hair_rect = pygame.Rect(head_cx - head_r, head_cy - head_r, head_r * 2, head_r)
        pygame.draw.ellipse(surf, hair, hair_rect)

        eye_y = head_cy - 2
        eye_col = (30, 20, 10)
        if f == 1:
            pygame.draw.circle(surf, eye_col, (head_cx + 5, eye_y), 2)
        else:
            pygame.draw.circle(surf, eye_col, (head_cx - 5, eye_y), 2)

        torso_top = head_cy + head_r
        torso_bot = torso_top + 44 + anim_off // 2
        torso_cx = w // 2
        torso_w = 32

        pygame.draw.rect(surf, gi,
            (torso_cx - torso_w // 2, torso_top, torso_w, torso_bot - torso_top))
        belt_y = torso_top + (torso_bot - torso_top) // 2
        pygame.draw.rect(surf, belt,
            (torso_cx - torso_w // 2, belt_y, torso_w, 6))

        shoulder_y = torso_top + 6
        arm_len = 28

        arm_ext = arm_raise
        if f == 1:
            elbow = (torso_cx + torso_w // 2 + 8, shoulder_y + arm_len // 2 + arm_ext)
            fist  = (torso_cx + torso_w // 2 + 16, shoulder_y + arm_len + arm_ext)
            back_arm = (torso_cx - torso_w // 2 - 4, shoulder_y + arm_len // 2)
        else:
            elbow = (torso_cx - torso_w // 2 - 8, shoulder_y + arm_len // 2 + arm_ext)
            fist  = (torso_cx - torso_w // 2 - 16, shoulder_y + arm_len + arm_ext)
            back_arm = (torso_cx + torso_w // 2 + 4, shoulder_y + arm_len // 2)

        pygame.draw.line(surf, skin, (torso_cx + torso_w // 2, shoulder_y), elbow, 6)
        pygame.draw.line(surf, skin, elbow, fist, 6)
        pygame.draw.circle(surf, skin, fist, 5)

        pygame.draw.line(surf, gi, (torso_cx - torso_w // 2, shoulder_y), back_arm, 5)

        waist_y = torso_bot
        leg_w = 12
        leg_len = 44

        left_foot  = (torso_cx - 10 - leg_spread, waist_y + leg_len + anim_off // 2)
        right_foot = (torso_cx + 10 + leg_spread, waist_y + leg_len + anim_off // 2)

        pygame.draw.line(surf, gi, (torso_cx - 8, waist_y), left_foot, leg_w)
        pygame.draw.line(surf, gi, (torso_cx + 8, waist_y), right_foot, leg_w)

        shoe = accent
        pygame.draw.circle(surf, shoe, left_foot, 7)
        pygame.draw.circle(surf, shoe, right_foot, 7)

        if f == -1:
            surf = pygame.transform.flip(surf, True, False)

        screen.blit(surf, (x, y))

        name_font = pygame.font.SysFont('arial', 14, bold=True)
        label = name_font.render(self.name, True, (255, 255, 255))
        screen.blit(label, (x + w // 2 - label.get_width() // 2, y - 18))
