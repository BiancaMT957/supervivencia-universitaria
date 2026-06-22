import pygame

from constants import (
    BACKGROUND_COLOR,
    FPS,
    MAX_DT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from player import Player


def run() -> None:
    pygame.init()

    try:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption(
            "Supervivencia Universitaria"
        )

        clock = pygame.time.Clock()

        player = Player(
            position=screen.get_rect().center,
            bounds=screen.get_rect(),
        )

        sprites = pygame.sprite.Group(player)

        running = True

        while running:
            # Clock.tick devuelve milisegundos.
            # Dividir entre 1000 produce segundos.
            dt = min(clock.tick(FPS) / 1000.0, MAX_DT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            sprites.update(dt)

            screen.fill(BACKGROUND_COLOR)
            sprites.draw(screen)

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    run()
