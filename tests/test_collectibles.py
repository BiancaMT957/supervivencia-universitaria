import pygame
import pytest

from collectibles import Collectible, collect_items


def test_effects_are_normalized() -> None:
    item = Collectible(
        position=(100, 100),
        item_type="notes",
        effects={
            "grades": 8,
        },
    )

    assert item.effects == {
        "energy": 0,
        "money": 0,
        "grades": 8,
    }


def test_unknown_effect_key_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="no reconocidas",
    ):
        Collectible(
            position=(100, 100),
            item_type="invalid",
            effects={
                "luck": 10,
            },
        )


def test_negative_objective_points_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="objective_points",
    ):
        Collectible(
            position=(100, 100),
            item_type="task",
            effects={
                "grades": 6,
            },
            objective_points=-1,
        )


def test_collectible_expires_after_lifetime() -> None:
    item = Collectible(
        position=(100, 100),
        item_type="task",
        effects={
            "grades": 6,
        },
        lifetime=1.0,
    )

    group = pygame.sprite.Group(item)

    group.update(0.4)
    assert item.alive()

    group.update(0.7)
    assert not item.alive()
    assert len(group) == 0


def test_collision_removes_and_returns_item() -> None:
    player = pygame.sprite.Sprite()
    player.rect = pygame.Rect(80, 80, 40, 40)

    item = Collectible(
        position=(100, 100),
        item_type="task",
        effects={
            "grades": 6,
        },
        objective_points=1,
    )

    items = pygame.sprite.Group(item)

    collided = collect_items(
        player,
        items,
    )

    assert collided == [item]
    assert len(items) == 0
    assert not item.alive()


def test_non_colliding_item_remains_in_group() -> None:
    player = pygame.sprite.Sprite()
    player.rect = pygame.Rect(0, 0, 40, 40)

    item = Collectible(
        position=(300, 300),
        item_type="notes",
        effects={
            "grades": 8,
        },
    )

    items = pygame.sprite.Group(item)

    collided = collect_items(
        player,
        items,
    )

    assert collided == []
    assert item.alive()
    assert len(items) == 1
