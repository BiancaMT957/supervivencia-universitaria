from collections.abc import Mapping

import pygame
import math

from constants import (
    FPS,
    MAX_DT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from game_logic import GameController, GameState


def log_effect(effect: Mapping[str, int]) -> None:
    """Adaptador temporal hasta integrar PlayerStats."""

    print(f"[EFECTO] {dict(effect)}")


def build_window_title(
    controller: GameController,
) -> str:
    """Construye un título diagnóstico según el estado activo."""

    state = controller.current_state

    if state is GameState.CAMPUS:
        scene = controller.campus_scene

        detail = (
            f"Materiales: "
            f"{scene.tasks_collected}/{scene.target_tasks}"
            f" | Tiempo: "
            f"{math.ceil(scene.remaining_time)} s"
        )

    elif state is GameState.TRANSITION:
        scene = controller.transition_scene

        remaining = max(
            0.0,
            scene.duration - scene.elapsed_time,
        )

        detail = (
            f"Finales en "
            f"{math.ceil(remaining)} s"
        )

    elif state is GameState.FINALS:
        detail = "Semana de Finales"

    else:
        detail = state.name

    return (
        "Supervivencia Universitaria"
        f" | {state.name}"
        f" | {detail}"
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

        previous_title = ""
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

            title = build_window_title(controller)

            if title != previous_title:
                pygame.display.set_caption(title)
                previous_title = title

            controller.draw(screen)
            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    run()