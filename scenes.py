from __future__ import annotations

import random
from collections.abc import Callable, Mapping

import math
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
    FINALS_BACKGROUND_COLOR,
    FINALS_BORDER_COLOR,
    FINALS_PLAY_AREA_COLOR,
    TRANSITION_BACKGROUND_COLOR,
    TRANSITION_DURATION,
    TRANSITION_RING_COLOR,
    TRANSITION_RING_SECONDARY_COLOR,
    COFFEE_COLOR,
    EXTRA_CREDIT_COLOR,
    FINALS_DURATION,
    FINALS_INITIAL_ITEMS,
    FINALS_ITEM_LIFETIME_SECONDS,
    FINALS_MAX_ITEMS,
    FINALS_SPAWN_MAX_SECONDS,
    FINALS_SPAWN_MIN_SECONDS,
    ILLNESS_COLOR,
    SURPRISE_EXAM_COLOR,
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

FINALS_ITEM_DEFINITIONS = (
    {
        "item_type": "notes",
        "effects": {
            "grades": 8,
        },
        "color": NOTES_COLOR,
        "weight": 15,
    },
    {
        "item_type": "coffee",
        "effects": {
            "energy": 10,
            "money": -5,
        },
        "color": COFFEE_COLOR,
        "weight": 15,
    },
    {
        "item_type": "extra_credit",
        "effects": {
            "grades": 12,
        },
        "color": EXTRA_CREDIT_COLOR,
        "weight": 10,
    },
    {
        "item_type": "illness",
        "effects": {
            "energy": -15,
            "money": -8,
        },
        "color": ILLNESS_COLOR,
        "weight": 20,
    },
    {
        "item_type": "sleep_deprivation",
        "effects": {
            "energy": -12,
        },
        "color": DISTRACTION_COLOR,
        "weight": 20,
    },
    {
        "item_type": "surprise_exam",
        "effects": {
            "energy": -8,
            "grades": -5,
        },
        "color": SURPRISE_EXAM_COLOR,
        "weight": 20,
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
            self.items.empty()
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

class TransitionScene:
    """Transición temporal entre Campus y Semana de Finales."""

    def __init__(
        self,
        screen_bounds: pygame.Rect,
        duration: float = TRANSITION_DURATION,
    ) -> None:
        if duration <= 0:
            raise ValueError(
                "La duración de la transición debe ser mayor que cero."
            )

        self.screen_bounds = pygame.Rect(screen_bounds)
        self.duration = float(duration)
        self.elapsed_time = 0.0

    @property
    def progress(self) -> float:
        """Progreso normalizado de la transición entre 0 y 1."""

        return min(
            1.0,
            self.elapsed_time / self.duration,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """La transición no procesa controles propios."""

        _ = event

    def update(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("delta time no puede ser negativo.")

        self.elapsed_time = min(
            self.duration,
            self.elapsed_time + dt,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja una animación circular provisional."""

        screen.fill(TRANSITION_BACKGROUND_COLOR)

        center = self.screen_bounds.center
        base_radius = min(
            self.screen_bounds.width,
            self.screen_bounds.height,
        ) // 8

        pulse = 1.0 + 0.08 * math.sin(
            self.elapsed_time * 6.0
        )

        radius = round(base_radius * pulse)

        ring_rect = pygame.Rect(
            0,
            0,
            radius * 2,
            radius * 2,
        )
        ring_rect.center = center

        pygame.draw.circle(
            screen,
            TRANSITION_RING_SECONDARY_COLOR,
            center,
            radius,
            width=4,
        )

        start_angle = self.elapsed_time * 4.0
        end_angle = start_angle + math.pi * 1.4

        pygame.draw.arc(
            screen,
            TRANSITION_RING_COLOR,
            ring_rect,
            start_angle,
            end_angle,
            width=9,
        )

        inner_radius = max(8, radius // 4)

        pygame.draw.circle(
            screen,
            TRANSITION_RING_COLOR,
            center,
            inner_radius,
        )

    def is_complete(self) -> bool:
        return self.elapsed_time >= self.duration

    def reset(self) -> None:
        self.elapsed_time = 0.0


class FinalsScene:
    """Escenario de Semana de Finales.

    Administra jugador, recolectables, aparición de objetos,
    colisiones y temporizador. No decide victoria o derrota.
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
            self.screen_bounds.height
            - HUD_HEIGHT
            - PLAY_AREA_MARGIN,
        )

        if self.play_bounds.width <= 0 or self.play_bounds.height <= 0:
            raise ValueError(
                "El área jugable de Finales no tiene dimensiones válidas."
            )

        self.player_group = pygame.sprite.GroupSingle()
        self.items = pygame.sprite.Group()

        self.player: Player

        self.remaining_time = 0.0
        self.items_collected = 0

        self._spawn_timer = 0.0

        self.reset()

    @property
    def time_expired(self) -> bool:
        return self.remaining_time <= 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Finales todavía no posee eventos discretos propios."""

        _ = event

    def update(self, dt: float) -> None:
        """Actualiza los sistemas activos de Semana de Finales."""

        if dt < 0:
            raise ValueError("delta time no puede ser negativo.")

        if self.is_complete():
            return

        self.remaining_time = max(
            0.0,
            self.remaining_time - dt,
        )

        if self.time_expired:
            self.items.empty()
            return

        self.player_group.update(dt)
        self.items.update(dt)

        collided_items = collect_items(
            self.player,
            self.items,
        )

        for item in collided_items:
            self.effect_handler(item.effects)
            self.items_collected += 1

        self._spawn_timer -= dt

        if self._spawn_timer <= 0.0:
            if len(self.items) < FINALS_MAX_ITEMS:
                self._spawn_collectible()

            self._schedule_next_spawn()

    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja fondo, objetos y jugador."""

        screen.fill(FINALS_BACKGROUND_COLOR)

        pygame.draw.rect(
            screen,
            FINALS_PLAY_AREA_COLOR,
            self.play_bounds,
        )

        pygame.draw.rect(
            screen,
            FINALS_BORDER_COLOR,
            self.play_bounds,
            width=2,
        )

        self.items.draw(screen)
        self.player_group.draw(screen)

    def is_complete(self) -> bool:
        """Finales termina cuando se agota su temporizador."""

        return self.time_expired

    def reset(self) -> None:
        """Restaura completamente Semana de Finales."""

        self.remaining_time = FINALS_DURATION
        self.items_collected = 0

        self.items.empty()
        self.player_group.empty()

        self.player = Player(
            position=self.play_bounds.center,
            bounds=self.play_bounds,
        )

        self.player_group.add(self.player)

        for _ in range(FINALS_INITIAL_ITEMS):
            self._spawn_collectible()

        self._schedule_next_spawn()

    def _schedule_next_spawn(self) -> None:
        self._spawn_timer = self.rng.uniform(
            FINALS_SPAWN_MIN_SECONDS,
            FINALS_SPAWN_MAX_SECONDS,
        )

    def _spawn_collectible(self) -> None:
        definitions = FINALS_ITEM_DEFINITIONS

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
            objective_points=0,
            color=definition["color"],
            lifetime=FINALS_ITEM_LIFETIME_SECONDS,
        )

        self.items.add(item)

    def _find_spawn_position(self) -> tuple[int, int]:
        """Busca una posición libre dentro de la arena de Finales."""

        item_width, item_height = COLLECTIBLE_SIZE

        half_width = item_width // 2
        half_height = item_height // 2

        left = self.play_bounds.left + half_width
        right = self.play_bounds.right - half_width
        top = self.play_bounds.top + half_height
        bottom = self.play_bounds.bottom - half_height

        if left > right or top > bottom:
            raise ValueError(
                "El área de Finales es menor que un recolectable."
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

        return (
            self.rng.randint(left, right),
            self.rng.randint(top, bottom),
        )