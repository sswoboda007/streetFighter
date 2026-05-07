from __future__ import annotations

import pygame

P1_BINDINGS = {
    'left':        pygame.K_a,
    'right':       pygame.K_d,
    'jump':        pygame.K_w,
    'crouch':      pygame.K_s,
    'light_punch': pygame.K_j,
    'heavy_punch': pygame.K_k,
    'light_kick':  pygame.K_h,
    'heavy_kick':  pygame.K_l,
    'block':       pygame.K_f,
}

P2_BINDINGS = {
    'left':        pygame.K_LEFT,
    'right':       pygame.K_RIGHT,
    'jump':        pygame.K_UP,
    'crouch':      pygame.K_DOWN,
    'light_punch': pygame.K_KP1,
    'heavy_punch': pygame.K_KP2,
    'light_kick':  pygame.K_KP4,
    'heavy_kick':  pygame.K_KP5,
    'block':       pygame.K_KP0,
}


class InputState:
    def __init__(self, bindings: dict[str, int]) -> None:
        self._bindings = bindings
        self._held: set[str] = set()
        self._just_pressed: set[str] = set()
        self._just_released: set[str] = set()
        self._motion_buffer: list[str] = []

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            for action, key in self._bindings.items():
                if event.key == key:
                    self._just_pressed.add(action)
                    self._held.add(action)
                    if action in ('left', 'right', 'jump', 'crouch'):
                        self._motion_buffer.append(action)
                        if len(self._motion_buffer) > 6:
                            self._motion_buffer.pop(0)
        elif event.type == pygame.KEYUP:
            for action, key in self._bindings.items():
                if event.key == key:
                    self._held.discard(action)
                    self._just_released.add(action)

    def tick(self) -> None:
        self._just_pressed.clear()
        self._just_released.clear()

    def held(self, action: str) -> bool:
        return action in self._held

    def pressed(self, action: str) -> bool:
        return action in self._just_pressed

    def released(self, action: str) -> bool:
        return action in self._just_released

    def check_qcf(self) -> bool:
        """Quarter-circle forward (down, down-forward implied → right) + any attack pressed."""
        buf = self._motion_buffer
        if len(buf) >= 2 and buf[-2] == 'crouch' and buf[-1] == 'right':
            return True
        return False

    def clear_motion(self) -> None:
        self._motion_buffer.clear()
