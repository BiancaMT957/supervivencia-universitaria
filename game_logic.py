from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import Enum, auto

import pygame

from scenes import (
    CampusScene,
    FinalsScene,
    TransitionScene,
)


EffectHandler = Callable[[Mapping[str, int]], None]


class GameState(Enum):
    """Estados mutuamente excluyentes de la aplicación."""

    MENU = auto()
    CAMPUS = auto()
    TRANSITION = auto()
    FINALS = auto()
    VICTORY = auto()
    DEFEAT = auto()


class GameController:
    """Coordina escenas y cambios de estado.

    No implementa estadísticas, HUD ni eventos aleatorios.
    """

    def __init__(
        self,
        screen_bounds: pygame.Rect,
        effect_handler: EffectHandler,
    ) -> None:
        self.screen_bounds = pygame.Rect(screen_bounds)

        self.campus_scene = CampusScene(
            screen_bounds=self.screen_bounds,
            effect_handler=effect_handler,
        )

        self.transition_scene = TransitionScene(
            screen_bounds=self.screen_bounds,
        )

        self.finals_scene = FinalsScene(
            screen_bounds=self.screen_bounds,
            effect_handler=effect_handler,
        )

        # Durante esta etapa de desarrollo iniciamos directamente
        # en Campus. El menú se integrará posteriormente.
        self.current_state = GameState.CAMPUS

        self._campus_timeout_reported = False
        self._finals_timeout_reported = False

    @property
    def active_scene(
        self,
    ) -> CampusScene | TransitionScene | FinalsScene:
        if self.current_state is GameState.CAMPUS:
            return self.campus_scene

        if self.current_state is GameState.TRANSITION:
            return self.transition_scene

        if self.current_state is GameState.FINALS:
            return self.finals_scene

        raise RuntimeError(
            f"No existe una escena activa para "
            f"{self.current_state.name}."
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Delega eventos y procesa controles globales de sesión."""

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_r
        ):
            self.restart()
            return

        self.active_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("delta time no puede ser negativo.")

        self.active_scene.update(dt)

        if self.current_state is GameState.CAMPUS:
            self._update_campus_state()

        elif self.current_state is GameState.TRANSITION:
            self._update_transition_state()

        elif self.current_state is GameState.FINALS:
            self._update_finals_state()

    def draw(self, screen: pygame.Surface) -> None:
        self.active_scene.draw(screen)

    def restart(self) -> None:
        """Reinicia toda la sesión desde Campus."""

        self.campus_scene.reset()
        self.transition_scene.reset()
        self.finals_scene.reset()

        previous_state = self.current_state
        self.current_state = GameState.CAMPUS

        self._campus_timeout_reported = False
        self._finals_timeout_reported = False

        print(
            f"[ESTADO] {previous_state.name} -> "
            f"{self.current_state.name} (reinicio)"
        )

    def _update_campus_state(self) -> None:
        if self.campus_scene.objective_reached:
            self._change_state(GameState.TRANSITION)
            return

        if (
            self.campus_scene.time_expired
            and not self._campus_timeout_reported
        ):
            self._campus_timeout_reported = True

            print(
                "[CAMPUS] Tiempo agotado. "
                "La decisión de derrota se integrará "
                "con game_logic y estadísticas definitivas."
            )

    def _update_transition_state(self) -> None:
        if self.transition_scene.is_complete():
            self._change_state(GameState.FINALS)

    def _update_finals_state(self) -> None:
        """Informa una sola vez que Finales terminó.

        La decisión de victoria o derrota quedará a cargo de las
        estadísticas y reglas definitivas.
        """

        if (
            self.finals_scene.time_expired
            and not self._finals_timeout_reported
        ):
            self._finals_timeout_reported = True

            print(
                "[FINALS] Tiempo agotado. "
                "Pendiente evaluar estadísticas para decidir "
                "VICTORY o DEFEAT."
            )

    def _change_state(self, new_state: GameState) -> None:
        """Realiza un cambio de estado único y controlado."""

        if new_state is self.current_state:
            return

        previous_state = self.current_state

        if new_state is GameState.TRANSITION:
            self.transition_scene.reset()

        elif new_state is GameState.FINALS:
            self.finals_scene.reset()
            self._finals_timeout_reported = False

        self.current_state = new_state

        print(
            f"[ESTADO] {previous_state.name} -> "
            f"{new_state.name}"
        )
