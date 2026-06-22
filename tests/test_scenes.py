import random

import pygame

from collectibles import Collectible
from scenes import CampusScene, TransitionScene


SCREEN_BOUNDS = pygame.Rect(0, 0, 960, 540)


def create_campus(
    effects: list[dict[str, int]],
) -> CampusScene:
    return CampusScene(
        screen_bounds=SCREEN_BOUNDS,
        effect_handler=lambda effect: effects.append(
            dict(effect)
        ),
        rng=random.Random(1234),
    )


def test_academic_item_increases_progress(
    no_keyboard_input,
) -> None:
    effects: list[dict[str, int]] = []
    scene = create_campus(effects)

    scene.items.empty()
    scene.tasks_collected = 0

    item = Collectible(
        position=scene.player.rect.center,
        item_type="task",
        effects={
            "grades": 6,
        },
        objective_points=1,
    )

    scene.items.add(item)
    scene.update(0.01)

    assert scene.tasks_collected == 1
    assert effects == [
        {
            "energy": 0,
            "money": 0,
            "grades": 6,
        }
    ]
    assert len(scene.items) == 0


def test_distraction_does_not_increase_progress(
    no_keyboard_input,
) -> None:
    effects: list[dict[str, int]] = []
    scene = create_campus(effects)

    scene.items.empty()
    scene.tasks_collected = 0

    item = Collectible(
        position=scene.player.rect.center,
        item_type="social_media",
        effects={
            "grades": -5,
        },
        objective_points=0,
    )

    scene.items.add(item)
    scene.update(0.01)

    assert scene.tasks_collected == 0
    assert effects[0]["grades"] == -5
    assert len(scene.items) == 0


def test_campus_completes_when_target_is_reached(
    no_keyboard_input,
) -> None:
    effects: list[dict[str, int]] = []
    scene = create_campus(effects)

    scene.items.empty()
    scene.target_tasks = 1

    item = Collectible(
        position=scene.player.rect.center,
        item_type="notes",
        effects={
            "grades": 8,
        },
        objective_points=1,
    )

    scene.items.add(item)
    scene.update(0.01)

    assert scene.objective_reached
    assert scene.is_complete()
    assert scene.tasks_collected == 1


def test_campus_completes_when_time_expires(
    no_keyboard_input,
) -> None:
    effects: list[dict[str, int]] = []
    scene = create_campus(effects)

    scene.remaining_time = 0.01
    scene.update(0.02)

    assert scene.time_expired
    assert scene.is_complete()
    assert scene.remaining_time == 0.0


def test_completed_campus_does_not_spawn_more_items(
    no_keyboard_input,
) -> None:
    effects: list[dict[str, int]] = []
    scene = create_campus(effects)

    scene.items.empty()
    scene.tasks_collected = scene.target_tasks

    scene.update(20.0)

    assert len(scene.items) == 0


def test_reset_restores_campus_state(
    no_keyboard_input,
) -> None:
    effects: list[dict[str, int]] = []
    scene = create_campus(effects)

    scene.tasks_collected = 7
    scene.remaining_time = 1.0
    scene.items.empty()

    scene.reset()

    assert scene.tasks_collected == 0
    assert not scene.time_expired
    assert not scene.objective_reached
    assert len(scene.items) > 0
    assert scene.player.rect.center == scene.play_bounds.center


def test_transition_completes_after_duration() -> None:
    scene = TransitionScene(
        screen_bounds=SCREEN_BOUNDS,
        duration=1.0,
    )

    scene.update(0.4)
    assert not scene.is_complete()

    scene.update(0.7)
    assert scene.is_complete()
    assert scene.progress == 1.0
