import pygame

from game_logic import GameController, GameState
from main import build_window_title


SCREEN_BOUNDS = pygame.Rect(0, 0, 960, 540)


def create_controller() -> GameController:
    return GameController(
        screen_bounds=SCREEN_BOUNDS,
        effect_handler=lambda effect: None,
    )


def test_finals_title_explains_survival_objective() -> None:
    controller = create_controller()

    controller.current_state = GameState.FINALS
    controller.finals_scene.remaining_time = 140.0
    controller.finals_scene.items_collected = 5

    title = build_window_title(controller)

    assert "Meta: resistir hasta 0 s" in title
    assert "Tiempo: 140 s" in title
    assert "Recogidos: 5" in title

    # El contador no debe presentarse como una meta.
    assert "Objetos:" not in title


def test_finals_title_reports_expired_time() -> None:
    controller = create_controller()

    controller.current_state = GameState.FINALS
    controller.finals_scene.remaining_time = 0.0

    title = build_window_title(controller)

    assert "Tiempo agotado" in title
    assert "Resultado pendiente" in title
    assert "Meta: resistir" not in title
