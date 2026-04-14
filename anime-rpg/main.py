# main.py — Entry point, game loop, state machine
# Run: python main.py
# Requires: pip install pygame-ce numpy

import sys
import pygame
from constants import *
from entities import make_player, make_enemy, make_village_npcs
from exploration import ExploreScene
from combat import CombatScene
from dialogue import DialogueSystem
from ui import draw_victory, draw_game_over, draw_text
from sound import SoundManager
from particles import ParticleSystem


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    # --- Audio ---
    sound = SoundManager()
    sound.init()

    # --- Shared particle system ---
    particles = ParticleSystem()

    # --- Game objects ---
    player   = make_player()
    npcs     = make_village_npcs()
    dialogue = DialogueSystem(sound=sound)

    explore  = ExploreScene(player, npcs, particles=particles)
    combat: CombatScene | None = None

    state   = STATE_EXPLORE
    running = True

    sound.play_music('explore')

    while running:
        dt = clock.tick(FPS) / 1000.0

        # ----------------------------------------------------------------
        # Events
        # ----------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if state == STATE_EXPLORE:
                    if event.key == pygame.K_e:
                        lines = explore.handle_talk()
                        if lines:
                            dialogue.start(lines)
                            state = STATE_DIALOGUE
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif state == STATE_DIALOGUE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                        dialogue.advance()
                        if not dialogue.active:
                            state = STATE_EXPLORE
                    elif event.key == pygame.K_ESCAPE:
                        dialogue.active = False
                        state = STATE_EXPLORE

                elif state == STATE_COMBAT:
                    if combat:
                        combat.handle_event(event)

                elif state in (STATE_VICTORY, STATE_GAME_OVER):
                    if event.key == pygame.K_RETURN:
                        player.tile_x = 5
                        player.tile_y = 5
                        if state == STATE_GAME_OVER:
                            player.hp = player.max_hp
                            player.mp = player.max_mp
                        combat = None
                        particles.clear()
                        state = STATE_EXPLORE
                        sound.play_music('explore')

        # ----------------------------------------------------------------
        # Update
        # ----------------------------------------------------------------
        if state == STATE_EXPLORE:
            next_state = explore.update(dt)
            if next_state == STATE_COMBAT:
                enemy   = make_enemy()
                combat  = CombatScene(player, enemy,
                                      particles=particles,
                                      sound=sound)
                particles.clear()
                state   = STATE_COMBAT
                sound.play_sfx('combat_start')
                sound.play_music('combat')

        elif state == STATE_DIALOGUE:
            dialogue.update(dt)
            if not dialogue.active:
                state = STATE_EXPLORE

        elif state == STATE_COMBAT:
            if combat:
                combat.update(dt)
                result = combat.result_state()
                if result == STATE_VICTORY:
                    state = STATE_VICTORY
                elif result == STATE_GAME_OVER:
                    state = STATE_GAME_OVER
                elif result == STATE_EXPLORE:
                    player.tile_x = 5
                    player.tile_y = 5
                    combat = None
                    particles.clear()
                    state  = STATE_EXPLORE
                    sound.play_music('explore')

        # ----------------------------------------------------------------
        # Draw
        # ----------------------------------------------------------------
        screen.fill(COLOR_BG)

        if state in (STATE_EXPLORE, STATE_DIALOGUE):
            explore.draw(screen)
            if state == STATE_DIALOGUE:
                dialogue.draw(screen)

        elif state == STATE_COMBAT:
            if combat:
                combat.draw(screen)

        elif state == STATE_VICTORY:
            if combat:
                combat.draw(screen)
            draw_victory(screen)

        elif state == STATE_GAME_OVER:
            if combat:
                combat.draw(screen)
            draw_game_over(screen)

        # FPS counter
        fps_text = f"{int(clock.get_fps())} fps"
        draw_text(screen, fps_text, SCREEN_W - 62, 6,
                  COLOR_WHITE_DIM, size=12, shadow=False)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
