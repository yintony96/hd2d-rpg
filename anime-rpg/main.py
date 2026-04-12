# main.py — Entry point, game loop, state machine
# Run: python main.py
# Requires: pip install pygame

import sys
import pygame
from constants import *
from entities import make_player, make_enemy, make_village_npcs
from exploration import ExploreScene
from combat import CombatScene
from dialogue import DialogueSystem
from ui import draw_victory, draw_game_over, draw_text


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    # --- Create persistent objects ---
    player   = make_player()
    npcs     = make_village_npcs()
    dialogue = DialogueSystem()

    explore  = ExploreScene(player, npcs)
    combat   = None   # created fresh each encounter

    state = STATE_EXPLORE

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds

        # ----------------------------------------------------------------
        # Event handling
        # ----------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                # --- Explore state ---
                if state == STATE_EXPLORE:
                    if event.key == pygame.K_e:
                        lines = explore.handle_talk()
                        if lines:
                            dialogue.start(lines)
                            state = STATE_DIALOGUE

                    elif event.key == pygame.K_ESCAPE:
                        running = False

                # --- Dialogue state ---
                elif state == STATE_DIALOGUE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                        dialogue.advance()
                        if not dialogue.active:
                            state = STATE_EXPLORE

                    elif event.key == pygame.K_ESCAPE:
                        dialogue.active = False
                        state = STATE_EXPLORE

                # --- Combat state ---
                elif state == STATE_COMBAT:
                    if combat:
                        combat.handle_event(event)

                # --- Victory / Game Over ---
                elif state in (STATE_VICTORY, STATE_GAME_OVER):
                    if event.key == pygame.K_RETURN:
                        # Reset enemy and return to village
                        # Move player away from trigger tile
                        player.tile_x = 5
                        player.tile_y = 5
                        # Restore some HP after victory; full restore on game over
                        if state == STATE_GAME_OVER:
                            player.hp = player.max_hp
                            player.mp = player.max_mp
                        combat = None
                        state = STATE_EXPLORE

        # ----------------------------------------------------------------
        # Update
        # ----------------------------------------------------------------
        if state == STATE_EXPLORE:
            next_state = explore.update(dt)
            if next_state == STATE_COMBAT:
                # Start a fresh combat encounter
                enemy  = make_enemy()
                combat = CombatScene(player, enemy)
                state  = STATE_COMBAT

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
                    # Fled
                    player.tile_x = 5
                    player.tile_y = 5
                    combat = None
                    state = STATE_EXPLORE

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
            # Keep last combat frame visible
            if combat:
                combat.draw(screen)
            draw_victory(screen)

        elif state == STATE_GAME_OVER:
            if combat:
                combat.draw(screen)
            draw_game_over(screen)

        # FPS counter (top-right, subtle)
        fps_text = f"{int(clock.get_fps())} fps"
        draw_text(screen, fps_text, SCREEN_W - 60, 6,
                  COLOR_WHITE_DIM, size=12, shadow=False)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
