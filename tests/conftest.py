import os

# Deben configurarse antes de inicializar PyGame.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest


class FakeKeys:
    """Representa el estado de teclas durante una prueba."""

    def __init__(self, *pressed_keys: int) -> None:
        self.pressed_keys = set(pressed_keys)

    def __getitem__(self, key: int) -> bool:
        return key in self.pressed_keys


@pytest.fixture(scope="session", autouse=True)
def pygame_session():
    """Inicializa PyGame una sola vez para toda la suite."""

    pygame.init()
    pygame.display.set_mode((1, 1))

    yield

    pygame.quit()


@pytest.fixture
def no_keyboard_input(monkeypatch):
    """Evita que las pruebas dependan del teclado físico."""

    monkeypatch.setattr(
        pygame.key,
        "get_pressed",
        lambda: FakeKeys(),
    )


@pytest.fixture
def fake_keys(monkeypatch):
    """Permite definir las teclas pulsadas en cada prueba."""

    def activate(*keys: int) -> None:
        monkeypatch.setattr(
            pygame.key,
            "get_pressed",
            lambda: FakeKeys(*keys),
        )

    return activate

