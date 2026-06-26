import pygame
import math

class Player:
    DEFAULT_SPEED  = 4
    DEFAULT_WIDTH  = 40
    DEFAULT_HEIGHT = 60
    DEFAULT_COLOR  = (70, 130, 180)

    def __init__(
        self,
        x: float,
        y: float,
        screen_width: int,
        screen_height: int,
        speed: int = DEFAULT_SPEED,
        image_path: str = None,
    ):
        self.x             = float(x)
        self.y             = float(y)
        self.speed         = speed
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.facing        = "down"

        if image_path:
            try:
                raw = pygame.image.load(image_path).convert_alpha()
                self.image  = pygame.transform.scale(
                    raw, (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
                )
                self.width  = self.image.get_width()
                self.height = self.image.get_height()
                self.color  = None
            except (pygame.error, FileNotFoundError) as e:
                print(f"[Player] No se pudo cargar imagen '{image_path}': {e}")
                self._use_fallback_rect()
        else:
            self._use_fallback_rect()

        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        moved = False

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y      -= self.speed
            self.facing  = "up"
            moved        = True

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y      += self.speed
            self.facing  = "down"
            moved        = True

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x      -= self.speed
            self.facing  = "left"
            moved        = True

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x      += self.speed
            self.facing  = "right"
            moved        = True

        if moved:
            self._clamp_to_screen()
            self._sync_rect()

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.handle_input(keys)

    def draw(self, surface: pygame.Surface) -> None:
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            head_cx = self.rect.centerx
            head_cy = self.rect.top + 14
            pygame.draw.circle(surface, self.color, (head_cx, head_cy), 14)
            pygame.draw.circle(surface, (255, 220, 185), (head_cx, head_cy), 13)

    def get_rect(self) -> pygame.Rect:
        return self.rect

    def set_position(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self._clamp_to_screen()
        self._sync_rect()

    def set_speed(self, speed: int) -> None:
        self.speed = max(1, speed)

    def _use_fallback_rect(self) -> None:
        self.width  = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.color  = self.DEFAULT_COLOR
        self.image  = None

    def _clamp_to_screen(self) -> None:
        self.x = max(0.0, min(self.x, self.screen_width  - self.width))
        self.y = max(0.0, min(self.y, self.screen_height - self.height))

    def _sync_rect(self) -> None:
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def __repr__(self) -> str:
        return (
            f"Player(x={self.x:.1f}, y={self.y:.1f}, "
            f"speed={self.speed}, facing='{self.facing}')"
        )
    
    def move_towards(self, target_x: float, target_y: float) -> bool:
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.x = target_x
            self.y = target_y
            self._sync_rect()
            return True

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"

        self._sync_rect()
        return False