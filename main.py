import math
from collections.abc import Mapping

import pygame

from constants import (
    FPS,
    MAX_DT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from scenes import CampusScene


def log_effect(effect: Mapping[str, int]) -> None:
    """Adaptador temporal hasta integrar PlayerStats."""

    print(f"[EFECTO] {dict(effect)}")


def update_caption(scene: CampusScene) -> None:
    """Muestra temporalmente progreso y estado en el título."""

    if scene.objective_reached:
        status = "OBJETIVO COMPLETADO"

    elif scene.time_expired:
        status = "TIEMPO AGOTADO"

    else:
        status = (
            f"Materiales: "
            f"{scene.tasks_collected}/{scene.target_tasks}"
            f" | Tiempo: "
            f"{math.ceil(scene.remaining_time)} s"
        )

    pygame.display.set_caption(
        f"Supervivencia Universitaria"
        f" | Campus"
        f" | {status}"
        f" | R: reiniciar"
    )


def run() -> None:
    pygame.init()

    try:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        clock = pygame.time.Clock()

        scene = CampusScene(
            screen_bounds=screen.get_rect(),
            effect_handler=log_effect,
        )

        running = True

        while running:
            dt = min(
                clock.tick(FPS) / 1000.0,
                MAX_DT,
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_r:
                        scene.reset()

                scene.handle_event(event)

            scene.update(dt)
            update_caption(scene)
            scene.draw(screen)

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    run()