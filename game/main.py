from __future__ import annotations

import sys
import pygame
from game.engine.settings import SCREEN_W, SCREEN_H, FPS, COLORS


def _make_scene(name: str, ctx: dict):
    from game.scenes.title import TitleScene
    from game.scenes.mode_select import ModeSelectScene
    from game.scenes.character_select import CharSelectScene
    from game.scenes.fight import FightScene
    from game.scenes.results import ResultsScene
    from game.scenes.tournament import TournamentScene

    if name == 'title':
        return TitleScene()
    if name == 'mode_select':
        return ModeSelectScene()
    if name == 'char_select':
        scene = CharSelectScene()
        scene.set_mode(ctx.get('mode', '1p'))
        return scene
    if name == 'fight':
        return FightScene(ctx['p1_char'], ctx['p2_char'], ctx.get('mode', '1p'))
    if name == 'results':
        return ResultsScene(ctx.get('winner', '???'))
    if name == 'tournament':
        return TournamentScene()
    raise ValueError(f'Unknown scene: {name}')


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Street Fighter II')
    clock = pygame.time.Clock()

    ctx: dict = {}
    scene_name = 'title'
    scene = _make_scene(scene_name, ctx)

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            scene.handle_event(event)

        scene.update(dt)
        scene.draw(screen)
        pygame.display.flip()

        if scene.done:
            next_name = scene.next_scene

            if scene_name == 'title':
                ctx = {}
                next_name = 'mode_select'

            elif scene_name == 'mode_select':
                ctx['mode'] = scene.chosen_mode
                if next_name == 'tournament':
                    pass
                else:
                    next_name = 'char_select'

            elif scene_name == 'char_select':
                ctx['p1_char'] = scene.p1_char
                ctx['p2_char'] = scene.p2_char

            elif scene_name == 'fight':
                ctx['winner'] = scene.winner_name
                if next_name == 'title':
                    ctx = {}

            elif scene_name == 'results':
                if next_name == 'char_select':
                    pass
                else:
                    ctx = {}

            scene_name = next_name
            scene = _make_scene(scene_name, ctx)


if __name__ == '__main__':
    run()
