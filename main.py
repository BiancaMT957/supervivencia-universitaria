import pygame

from collectibles import Collectible, collect_items
from constants import (
    BACKGROUND_COLOR,
    DISTRACTION_COLOR,
    FPS,
    MAX_DT,
    NOTES_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TASK_COLOR,
)
from player import Player


def create_demo_collectibles() -> pygame.sprite.Group:
    """Crea objetos temporales para probar entidades y colisiones."""

    items = pygame.sprite.Group()

    items.add(
        Collectible(
            position=(180, 130),
            item_type="task",
            effects={"grades": 6},
            objective_points=1,
            color=TASK_COLOR,
        ),
        Collectible(
            position=(750, 130),
            item_type="notes",
            effects={"grades": 8},
            color=NOTES_COLOR,
        ),
        Collectible(
            position=(200, 420),
            item_type="social_media",
            effects={
                "energy": -3,
                "grades": -5,
            },
            color=DISTRACTION_COLOR,
        ),
        Collectible(
            position=(750, 420),
            item_type="assignment",
            effects={
                "energy": -5,
                "grades": 10,
            },
            objective_points=1,
            color=TASK_COLOR,
        ),
    )

    return items


def update_caption(collected_total: int) -> None:
    pygame.display.set_caption(
        "Supervivencia Universitaria"
        f" | Recolectados: {collected_total}"
        " | R: reiniciar objetos"
    )


def run() -> None:
    pygame.init()

    try:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        clock = pygame.time.Clock()

        player = Player(
            position=screen.get_rect().center,
            bounds=screen.get_rect(),
        )

        player_group = pygame.sprite.GroupSingle(player)
        collectibles = create_demo_collectibles()

        collected_total = 0
        update_caption(collected_total)

        running = True

        while running:
            dt = min(clock.tick(FPS) / 1000.0, MAX_DT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_r:
                        collectibles = create_demo_collectibles()
                        collected_total = 0
                        update_caption(collected_total)

            player_group.update(dt)

            collected_items = collect_items(
                player,
                collectibles,
            )

            for item in collected_items:
                collected_total += 1

                print(
                    "[COLISIÓN]",
                    f"tipo={item.item_type}",
                    f"efectos={item.effects}",
                    f"progreso={item.objective_points}",
                )

                update_caption(collected_total)

            screen.fill(BACKGROUND_COLOR)

            # Los objetos se dibujan primero para que el jugador aparezca
            # visualmente por encima de ellos durante una colisión.
            collectibles.draw(screen)
            player_group.draw(screen)

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    run()
