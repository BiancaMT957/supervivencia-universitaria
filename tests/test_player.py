import math

import pygame
import pytest

from player import Player


def test_player_moves_using_delta_time(fake_keys) -> None:
    fake_keys(pygame.K_RIGHT)

    player = Player(
        position=(500, 500),
        bounds=pygame.Rect(0, 0, 1000, 1000),
        speed=100,
    )

    initial_position = player.position.copy()

    player.update(0.5)

    assert player.position.x == pytest.approx(
        initial_position.x + 50
    )
    assert player.position.y == pytest.approx(
        initial_position.y
    )


def test_diagonal_movement_is_normalized(fake_keys) -> None:
    fake_keys(
        pygame.K_RIGHT,
        pygame.K_DOWN,
    )

    player = Player(
        position=(500, 500),
        bounds=pygame.Rect(0, 0, 1000, 1000),
        speed=100,
    )

    initial_position = player.position.copy()

    player.update(1.0)

    displacement = player.position - initial_position
    expected_axis_distance = 100 / math.sqrt(2)

    assert displacement.length() == pytest.approx(
        100,
        abs=0.01,
    )
    assert displacement.x == pytest.approx(
        expected_axis_distance,
        abs=0.01,
    )
    assert displacement.y == pytest.approx(
        expected_axis_distance,
        abs=0.01,
    )


def test_opposite_keys_cancel_movement(fake_keys) -> None:
    fake_keys(
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_UP,
        pygame.K_DOWN,
    )

    player = Player(
        position=(300, 300),
        bounds=pygame.Rect(0, 0, 600, 600),
        speed=100,
    )

    initial_position = player.position.copy()

    player.update(1.0)

    assert player.position == initial_position


def test_player_remains_inside_bounds(fake_keys) -> None:
    fake_keys(pygame.K_RIGHT)

    bounds = pygame.Rect(0, 0, 200, 200)

    player = Player(
        position=(180, 100),
        bounds=bounds,
        speed=100,
    )

    player.update(1.0)

    assert player.rect.right == bounds.right
    assert bounds.contains(player.rect)


def test_negative_delta_time_is_rejected(
    no_keyboard_input,
) -> None:
    player = Player(
        position=(100, 100),
        bounds=pygame.Rect(0, 0, 300, 300),
    )

    with pytest.raises(
        ValueError,
        match="delta time",
    ):
        player.update(-0.1)
