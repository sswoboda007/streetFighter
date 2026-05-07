from __future__ import annotations

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
ROUND_TIME = 99  # seconds
ROUNDS_TO_WIN = 2

FLOOR_Y = 560  # y-coordinate of the ground surface

GRAVITY = 1800  # pixels per second^2
JUMP_VY = -700  # initial vertical velocity on jump

WALK_SPEED = 280  # base horizontal walk speed (px/s); scaled by agility
JUMP_SPEED_X = 220

HIT_STUN_FRAMES = 12
BLOCK_STUN_FRAMES = 6
KNOCKBACK_VX = 280  # horizontal knockback velocity on hit
BLOCK_DAMAGE_MULT = 0.25  # fraction of damage that gets through a block

SPECIAL_COOLDOWN = 2.5  # seconds between special move uses

FIGHTER_W = 80
FIGHTER_H = 120

ARENA_LEFT = 60
ARENA_RIGHT = SCREEN_W - 60

PALETTE = {
    'Ryu':     {'skin': (242, 194, 139), 'gi': (240, 240, 240), 'belt': (34, 34, 34),   'hair': (58, 42, 26),  'accent': (209, 59, 59)},
    'Ken':     {'skin': (242, 194, 139), 'gi': (209, 59, 59),   'belt': (34, 34, 34),   'hair': (240, 198, 116), 'accent': (34, 34, 34)},
    'Chun-Li': {'skin': (242, 194, 139), 'gi': (42, 111, 214),  'belt': (240, 198, 116), 'hair': (26, 26, 26),  'accent': (240, 198, 116)},
    'Zangief': {'skin': (224, 160, 112), 'gi': (139, 26, 26),   'belt': (34, 34, 34),   'hair': (58, 42, 26),  'accent': (240, 198, 116)},
}

COLORS = {
    'bg':          (10, 10, 20),
    'hud_bar_bg':  (40, 0, 0),
    'hud_p1':      (0, 220, 60),
    'hud_p2':      (0, 180, 220),
    'hud_border':  (200, 180, 50),
    'overlay_bg':  (0, 0, 0, 160),
    'white':       (255, 255, 255),
    'yellow':      (255, 230, 50),
    'red':         (220, 30, 30),
    'black':       (0, 0, 0),
    'shadow':      (30, 30, 30),
}
