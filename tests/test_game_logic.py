import pygame

from game_logic import GameController, GameState


SCREEN_BOUNDS = pygame.Rect(0, 0, 960, 540)


def create_controller() -> GameController:
    return GameController(
        screen_bounds=SCREEN_BOUNDS,
        effect_handler=lambda effect: None,
    )


def test_controller_starts_in_campus() -> None:
    controller = create_controller()

    assert controller.current_state is GameState.CAMPUS
    assert controller.active_scene is controller.campus_scene


def test_objective_changes_campus_to_transition() -> None:
    controller = create_controller()

    controller.campus_scene.tasks_collected = (
        controller.campus_scene.target_tasks
    )

    controller.update(0.0)

    assert controller.current_state is GameState.TRANSITION
    assert (
        controller.active_scene
        is controller.transition_scene
    )


def test_transition_changes_to_finals() -> None:
    controller = create_controller()

    controller.campus_scene.tasks_collected = (
        controller.campus_scene.target_tasks
    )
    controller.update(0.0)

    controller.transition_scene.elapsed_time = (
        controller.transition_scene.duration
    )
    controller.update(0.0)

    assert controller.current_state is GameState.FINALS
    assert controller.active_scene is controller.finals_scene


def test_campus_timeout_does_not_enter_finals() -> None:
    controller = create_controller()

    controller.campus_scene.remaining_time = 0.0
    controller.update(0.0)

    assert controller.current_state is GameState.CAMPUS


def test_restart_returns_to_clean_campus() -> None:
    controller = create_controller()

    controller.campus_scene.tasks_collected = (
        controller.campus_scene.target_tasks
    )
    controller.update(0.0)

    controller.transition_scene.elapsed_time = (
        controller.transition_scene.duration
    )
    controller.update(0.0)

    assert controller.current_state is GameState.FINALS

    controller.restart()

    assert controller.current_state is GameState.CAMPUS
    assert controller.campus_scene.tasks_collected == 0
    assert not controller.campus_scene.time_expired
    assert controller.transition_scene.elapsed_time == 0.0
    assert (
        controller.finals_scene.player.rect.center
        == controller.finals_scene.play_bounds.center
    )

