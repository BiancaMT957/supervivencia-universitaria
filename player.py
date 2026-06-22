from __future__ import annotations

import pygame

from constants import PLAYER_COLOR, PLAYER_SIZE, PLAYER_SPEED


class Player(pygame.sprite.Sprite):
    """Jugador controlable con movimiento independiente de los FPS."""

    def __init__(
        self,
        position: tuple[float, float],
        bounds: pygame.Rect,
        speed: float = PLAYER_SPEED,
        image: pygame.Surface | None = None,
    ) -> None:
        super().__init__()

        if speed <= 0:
            raise ValueError("La velocidad del jugador debe ser mayor que cero.")

        self.bounds = pygame.Rect(bounds)

        if self.bounds.width <= 0 or self.bounds.height <= 0:
            raise ValueError(
                "Los límites del jugador deben tener un área positiva."
            )

        if image is None:
            self.image = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)

            pygame.draw.rect(
                self.image,
                PLAYER_COLOR,
                self.image.get_rect(),
                border_radius=8,
            )
        else:
            # Se copia para evitar que Player modifique accidentalmente
            # una Surface compartida con otro objeto.
            self.image = image.copy()

        self.rect = self.image.get_rect(
            center=(round(position[0]), round(position[1]))
        )

        if (
            self.rect.width > self.bounds.width
            or self.rect.height > self.bounds.height
        ):
            raise ValueError(
                "La imagen del jugador no cabe dentro de los límites."
            )

        self.rect.clamp_ip(self.bounds)

        # Vector2 conserva decimales y permite movimiento subpíxel.
        self.position = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2()
        self.speed = float(speed)

    def _read_direction(self) -> None:
        """Lee controles continuos y construye el vector de dirección."""

        keys = pygame.key.get_pressed()

        horizontal = int(
            keys[pygame.K_RIGHT] or keys[pygame.K_d]
        ) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )

        vertical = int(
            keys[pygame.K_DOWN] or keys[pygame.K_s]
        ) - int(
            keys[pygame.K_UP] or keys[pygame.K_w]
        )

        self.direction.update(horizontal, vertical)

        # Sin normalización, (1, 1) tendría longitud sqrt(2)
        # y el jugador avanzaría más rápido en diagonal.
        if self.direction.length_squared() > 0:
            self.direction.normalize_ip()

    def update(self, dt: float) -> None:
        """Actualiza la posición usando delta time expresado en segundos."""

        if dt < 0:
            raise ValueError("delta time no puede ser negativo.")

        self._read_direction()

        self.position += self.direction * self.speed * dt

        # Rect trabaja con enteros; position conserva los decimales.
        self.rect.center = (
            round(self.position.x),
            round(self.position.y),
        )

        center_before_clamp = self.rect.center
        self.rect.clamp_ip(self.bounds)

        # Solo sincronizamos position con rect si realmente chocó
        # contra un límite. Hacerlo siempre eliminaría la precisión
        # subpíxel acumulada.
        if self.rect.center != center_before_clamp:
            self.position.update(self.rect.center)
