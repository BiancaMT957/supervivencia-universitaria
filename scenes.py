from __future__ import annotations

import random
from collections.abc import Callable, Mapping

import pygame

from collectibles import Collectible, collect_items
from constants import (
    BACKGROUND_COLOR,
    CAMPUS_DURATION,
    CAMPUS_INITIAL_ITEMS,
    CAMPUS_MAX_ITEMS,
    CAMPUS_SPAWN_MAX_SECONDS,
    CAMPUS_SPAWN_MIN_SECONDS,
    CAMPUS_TARGET_TASKS,
    COLLECTIBLE_LIFETIME_SECONDS,
    COLLECTIBLE_SIZE,
    DISTRACTION_COLOR,
    HUD_HEIGHT,
    NOTES_COLOR,
    PLAY_AREA_BORDER_COLOR,
    PLAY_AREA_COLOR,
    PLAY_AREA_MARGIN,
    TASK_COLOR,
)
from player import Player


EffectHandler = Callable[[Mapping[str, int]], None]


CAMPUS_ITEM_DEFINITIONS = (
    {
        "item_type": "task",
        "effects": {
            "grades": 6,
        },
        "objective_points": 1,
        "color": TASK_COLOR,
        "weight": 25,
    },
    {
        "item_type": "notes",
        "effects": {
            "grades": 8,
        },
        "objective_points": 1,
        "color": NOTES_COLOR,
        "weight": 20,
    },
    {
        "item_type": "assignment",
        "effects": {
            "energy": -5,
            "grades": 10,
        },
        "objective_points": 1,
        "color": TASK_COLOR,
        "weight": 15,
    },
    {
        "item_type": "social_media",
        "effects": {
            "grades": -5,
        },
        "objective_points": 0,
        "color": DISTRACTION_COLOR,
        "weight": 15,
    },
    {
        "item_type": "video_games",
        "effects": {
            "energy": -5,
            "grades": -8,
        },
        "objective_points": 0,
        "color": DISTRACTION_COLOR,
        "weight": 13,
    },
    {
        "item_type": "sleep_deprivation",
        "effects": {
            "energy": -10,
        },
        "objective_points": 0,
        "color": DISTRACTION_COLOR,
        "weight": 12,
    },
)


class CampusScene:
    """Escenario de Campus.

    Administra jugador, recolectables, aparición de objetos,
    colisiones, progreso académico y temporizador.
    """

    def __init__(
        self,
        screen_bounds: pygame.Rect,
        effect_handler: EffectHandler,
        rng: random.Random | None = None,
    ) -> None:
        self.screen_bounds = pygame.Rect(screen_bounds)
        self.effect_handler = effect_handler
        self.rng = rng or random.Random()

        self.play_bounds = pygame.Rect(
            self.screen_bounds.left + PLAY_AREA_MARGIN,
            self.screen_bounds.top + HUD_HEIGHT,
            self.screen_bounds.width - 2 * PLAY_AREA_MARGIN,
            self.screen_bounds.height - HUD_HEIGHT - PLAY_AREA_MARGIN,
        )

        if self.play_bounds.width <= 0 or self.play_bounds.height <= 0:
            raise ValueError(
                "El área jugable no tiene dimensiones válidas."
            )

        self.player_group = pygame.sprite.GroupSingle()
        self.items = pygame.sprite.Group()

        self.player: Player

        self.remaining_time = 0.0
        self.tasks_collected = 0
        self.target_tasks = CAMPUS_TARGET_TASKS

        self._spawn_timer = 0.0

        self.reset()

    @property
    def objective_reached(self) -> bool:
        return self.tasks_collected >= self.target_tasks

    @property
    def time_expired(self) -> bool:
        return self.remaining_time <= 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Procesa eventos discretos propios de la escena.

        Por ahora no existen eventos discretos de Campus. El movimiento
        continuo se procesa desde Player.update().
        """

        _ = event

    def update(self, dt: float) -> None:
        """Actualiza todos los sistemas activos del Campus."""

        if dt < 0:
            raise ValueError("delta time no puede ser negativo.")

        if self.is_complete():
            return

        self.remaining_time = max(
            0.0,
            self.remaining_time - dt,
        )

        if self.time_expired:
            return

        self.player_group.update(dt)
        self.items.update(dt)

        collided_items = collect_items(
            self.player,
            self.items,
        )

        for item in collided_items:
            self.effect_handler(item.effects)

            self.tasks_collected = min(
                self.target_tasks,
                self.tasks_collected + item.objective_points,
            )

        if self.objective_reached:
            return

        self._spawn_timer -= dt

        if self._spawn_timer <= 0.0:
            if len(self.items) < CAMPUS_MAX_ITEMS:
                self._spawn_collectible()

            self._schedule_next_spawn()

    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja fondo, recolectables y jugador."""

        screen.fill(BACKGROUND_COLOR)

        pygame.draw.rect(
            screen,
            PLAY_AREA_COLOR,
            self.play_bounds,
        )

        pygame.draw.rect(
            screen,
            PLAY_AREA_BORDER_COLOR,
            self.play_bounds,
            width=2,
        )

        self.items.draw(screen)
        self.player_group.draw(screen)

    def is_complete(self) -> bool:
        """Indica que Campus terminó, no necesariamente que se superó."""

        return self.objective_reached or self.time_expired

    def reset(self) -> None:
        """Restaura completamente el estado interno de Campus."""

        self.remaining_time = CAMPUS_DURATION
        self.tasks_collected = 0

        self.items.empty()
        self.player_group.empty()

        self.player = Player(
            position=self.play_bounds.center,
            bounds=self.play_bounds,
        )

        self.player_group.add(self.player)

        for _ in range(CAMPUS_INITIAL_ITEMS):
            self._spawn_collectible()

        self._schedule_next_spawn()

    def _schedule_next_spawn(self) -> None:
        self._spawn_timer = self.rng.uniform(
            CAMPUS_SPAWN_MIN_SECONDS,
            CAMPUS_SPAWN_MAX_SECONDS,
        )

    def _spawn_collectible(self) -> None:
        definitions = CAMPUS_ITEM_DEFINITIONS

        weights = [
            int(definition["weight"])
            for definition in definitions
        ]

        definition = self.rng.choices(
            definitions,
            weights=weights,
            k=1,
        )[0]

        item = Collectible(
            position=self._find_spawn_position(),
            item_type=str(definition["item_type"]),
            effects=definition["effects"],
            objective_points=int(
                definition["objective_points"]
            ),
            color=definition["color"],
            lifetime=COLLECTIBLE_LIFETIME_SECONDS,
        )

        self.items.add(item)

    def _find_spawn_position(self) -> tuple[int, int]:
        """Busca una posición libre dentro del área jugable."""

        item_width, item_height = COLLECTIBLE_SIZE

        half_width = item_width // 2
        half_height = item_height // 2

        left = self.play_bounds.left + half_width
        right = self.play_bounds.right - half_width
        top = self.play_bounds.top + half_height
        bottom = self.play_bounds.bottom - half_height

        if left > right or top > bottom:
            raise ValueError(
                "El área jugable es menor que un recolectable."
            )

        for _ in range(30):
            position = (
                self.rng.randint(left, right),
                self.rng.randint(top, bottom),
            )

            candidate = pygame.Rect(
                0,
                0,
                item_width,
                item_height,
            )
            candidate.center = position

            player_safe_area = self.player.rect.inflate(
                100,
                100,
            )

            if candidate.colliderect(player_safe_area):
                continue

            overlaps_item = any(
                candidate.colliderect(
                    item.rect.inflate(12, 12)
                )
                for item in self.items
            )

            if not overlaps_item:
                return position

        # Evita un bucle infinito si el escenario está muy lleno.
        return (
            self.rng.randint(left, right),
            self.rng.randint(top, bottom),
        )
