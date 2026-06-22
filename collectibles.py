from __future__ import annotations

from collections.abc import Mapping
from typing import Final, cast

import pygame

from constants import COLLECTIBLE_SIZE


EFFECT_KEYS: Final[tuple[str, ...]] = (
    "energy",
    "money",
    "grades",
)


class Collectible(pygame.sprite.Sprite):
    """Objeto que puede ser recogido por el jugador.

    La entidad almacena sus efectos, pero no los aplica. La escena será
    responsable de comunicarlos al sistema de estadísticas.
    """

    def __init__(
        self,
        position: tuple[float, float],
        item_type: str,
        effects: Mapping[str, int],
        objective_points: int = 0,
        image: pygame.Surface | None = None,
        color: pygame.Color | tuple[int, int, int] = (80, 155, 230),
    ) -> None:
        super().__init__()

        normalized_type = item_type.strip()

        if not normalized_type:
            raise ValueError("item_type no puede estar vacío.")

        if isinstance(objective_points, bool) or not isinstance(
            objective_points,
            int,
        ):
            raise TypeError("objective_points debe ser un número entero.")

        if objective_points < 0:
            raise ValueError("objective_points no puede ser negativo.")

        unknown_keys = set(effects) - set(EFFECT_KEYS)

        if unknown_keys:
            unknown_text = ", ".join(sorted(unknown_keys))
            raise ValueError(
                f"Claves de efecto no reconocidas: {unknown_text}"
            )

        normalized_effects: dict[str, int] = {}

        for key in EFFECT_KEYS:
            value = effects.get(key, 0)

            # bool es subclase de int en Python; por eso se rechaza
            # explícitamente para evitar efectos como True o False.
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    f"El efecto '{key}' debe ser un número entero."
                )

            normalized_effects[key] = value

        self.item_type = normalized_type
        self.effects = normalized_effects
        self.objective_points = objective_points

        if image is None:
            self.image = self._create_placeholder(color)
        else:
            self.image = image.copy()

        self.rect = self.image.get_rect(
            center=(round(position[0]), round(position[1]))
        )

    @staticmethod
    def _create_placeholder(
        color: pygame.Color | tuple[int, int, int],
    ) -> pygame.Surface:
        """Crea un círculo provisional hasta recibir los sprites finales."""

        surface = pygame.Surface(
            COLLECTIBLE_SIZE,
            pygame.SRCALPHA,
        )

        center = (
            COLLECTIBLE_SIZE[0] // 2,
            COLLECTIBLE_SIZE[1] // 2,
        )

        radius = min(COLLECTIBLE_SIZE) // 2 - 2

        pygame.draw.circle(
            surface,
            color,
            center,
            radius,
        )

        pygame.draw.circle(
            surface,
            (245, 245, 245),
            center,
            radius,
            width=2,
        )

        return surface


def collect_items(
    player: pygame.sprite.Sprite,
    items: pygame.sprite.Group,
) -> list[Collectible]:
    """Detecta, elimina y devuelve los objetos tocados por el jugador."""

    collided = pygame.sprite.spritecollide(
        player,
        items,
        dokill=True,
    )

    # El grupo recibido debe contener exclusivamente Collectible.
    return cast(list[Collectible], collided)
