from collections.abc import Mapping

import pygame

from constants import (
    FPS,
    MAX_DT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from game_logic import GameController


def log_effect(effect: Mapping[str, int]) -> None:
    """Adaptador temporal hasta integrar PlayerStats."""

    print(f"[EFECTO] {dict(effect)}")


def update_window_title(
    controller: GameController,
) -> None:
    pygame.display.set_caption(
        "Supervivencia Universitaria"
        f" | {controller.current_state.name}"
        " | R: reiniciar"
    )


def run() -> None:
    pygame.init()

    try:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        clock = pygame.time.Clock()

        controller = GameController(
            screen_bounds=screen.get_rect(),
            effect_handler=log_effect,
        )

        previous_state = None
        running = True

        while running:
            dt = min(
                clock.tick(FPS) / 1000.0,
                MAX_DT,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False

                else:
                    controller.handle_event(event)

            controller.update(dt)

            if controller.current_state is not previous_state:
                update_window_title(controller)
                previous_state = controller.current_state

            controller.draw(screen)
            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    run()