"""
objects.py
==========
Issue #2 – Sistema de colisiones y recolección  (con assets integrados)

Objetos del juego (8 tipos):
  POSITIVOS:
    task         → Tarea        +2 Notas  -10 Energía
    notes        → Apuntes      +1 Notas   -5 Energía
    coffee       → Café        +25 Energía -30 Dinero
    scholarship  → Beca         +1 Notas +200 Dinero

  NEGATIVOS:
    gamepad      → Videojuegos  -3 Notas  -15 Energía  -30 Dinero
    distraction  → Distracciones-2 Notas   -5 Energía  -20 Dinero
    broken_laptop→ Laptop Rota  -2 Notas             -50 Dinero
    sick         → Enfermedad   -2 Notas  -20 Energía
"""

import pygame
import random
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stats import Stats


# ─────────────────────────────────────────────────────────────────────────────
#  RUTAS DE ASSETS
# ─────────────────────────────────────────────────────────────────────────────

ASSETS_DIR = "assets/"

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURACIÓN DE OBJETOS
# ─────────────────────────────────────────────────────────────────────────────

OBJETO_CONFIG: dict[str, dict] = {

    # ── POSITIVOS ──────────────────────────────────────────────────────────

    "tareas": {
        "nombre"     : "Tarea",
        "simbolo"    : "TAR",
        "descripcion": "Entregaste a tiempo!",
        "image_path" : ASSETS_DIR + "task.png",
        "color"      : ( 70, 140, 230),
        "color_borde": (130, 180, 255),
        "forma"      : "rect",
        "size"       : 48,
        "efectos"    : {"notas": +2, "energia": -10},
    },
    "apuntes": {
        "nombre"     : "Apuntes",
        "simbolo"    : "APT",
        "descripcion": "Repaso listo!",
        "image_path" : ASSETS_DIR + "notes.png",
        "color"      : ( 40, 190, 150),
        "color_borde": (100, 230, 190),
        "forma"      : "rect",
        "size"       : 44,
        "efectos"    : {"notas": +1, "energia": -5},
    },
    "cafe": {
        "nombre"     : "Cafe",
        "simbolo"    : "CFE",
        "descripcion": "Cafeina activada!",
        "image_path" : ASSETS_DIR + "coffee.png",
        "color"      : (160,  90,  40),
        "color_borde": (210, 150,  80),
        "forma"      : "circle",
        "size"       : 44,
        "efectos"    : {"energia": +25, "dinero": -30},
    },
    "beca": {
        "nombre"     : "Beca",
        "simbolo"    : "BCA",
        "descripcion": "Conseguiste una beca!",
        "image_path" : ASSETS_DIR + "scholarship.png",
        "color"      : (220, 180,  30),
        "color_borde": (255, 230, 100),
        "forma"      : "circle",
        "size"       : 48,
        "efectos"    : {"dinero": +200, "notas": +1},
    },

    # ── NEGATIVOS ─────────────────────────────────────────────────────────

    "videojuegos": {
        "nombre"     : "Videojuegos",
        "simbolo"    : "VJ",
        "descripcion": "Mucho gaming...",
        "image_path" : ASSETS_DIR + "gamepad.png",
        "color"      : (130,  50, 210),
        "color_borde": (180, 110, 255),
        "forma"      : "rect",
        "size"       : 48,
        "efectos"    : {"notas": -3, "energia": -15, "dinero": -30},
    },
    "redes": {
        "nombre"     : "Distraccion",
        "simbolo"    : "RS",
        "descripcion": "Perdiste el tiempo...",
        "image_path" : ASSETS_DIR + "distraction.png",
        "color"      : (220,  60, 130),
        "color_borde": (255, 130, 180),
        "forma"      : "circle",
        "size"       : 44,
        "efectos"    : {"notas": -2, "energia": -5, "dinero": -20},
    },
    "laptop_rota": {
        "nombre"     : "Laptop Rota",
        "simbolo"    : "BLT",
        "descripcion": "Gasto inesperado...",
        "image_path" : ASSETS_DIR + "broken_laptop.png",
        "color"      : (180,  60,  60),
        "color_borde": (230, 110, 110),
        "forma"      : "rect",
        "size"       : 48,
        "efectos"    : {"notas": -2, "dinero": -50},
    },
    "enfermedad": {
        "nombre"     : "Enfermedad",
        "simbolo"    : "ENF",
        "descripcion": "Faltaste a clases...",
        "image_path" : ASSETS_DIR + "sick.png",
        "color"      : ( 80, 170,  80),
        "color_borde": (140, 220, 140),
        "forma"      : "circle",
        "size"       : 44,
        "efectos"    : {"energia": -20, "notas": -2},
    },
}

STAT_NOMBRE: dict[str, str] = {
    "notas"  : "Notas",
    "energia": "Energia",
    "dinero" : "Dinero",
}

C_POSITIVO     = (120, 255, 120)
C_NEGATIVO     = (255,  90,  90)
FLOAT_LIFETIME = 1_600    # ms
FLOAT_SPEED    = 0.055    # px/ms


# ─────────────────────────────────────────────────────────────────────────────
#  CACHÉ DE IMÁGENES  (carga cada imagen una sola vez)
# ─────────────────────────────────────────────────────────────────────────────

_image_cache: dict[str, pygame.Surface | None] = {}

def _load_image(path: str, size: int) -> pygame.Surface | None:
    """
    Carga y escala una imagen. Guarda en caché para no releerla en cada spawn.
    Devuelve None si el archivo no existe o no se puede leer.
    """
    key = f"{path}:{size}"
    if key not in _image_cache:
        try:
            raw = pygame.image.load(path).convert_alpha()
            _image_cache[key] = pygame.transform.scale(raw, (size, size))
        except (pygame.error, FileNotFoundError):
            print(f"[assets] No se encontró '{path}' — usando forma de color.")
            _image_cache[key] = None
    return _image_cache[key]


# ─────────────────────────────────────────────────────────────────────────────
#  CLASE: GameObj
# ─────────────────────────────────────────────────────────────────────────────

class GameObj:
    """Objeto recolectable en el mapa."""

    # Margen del glow en píxeles
    GLOW_PAD = 4

    def __init__(self, tipo: str, x: int, y: int) -> None:
        self.tipo  = tipo
        self.data  = OBJETO_CONFIG[tipo]
        size       = self.data["size"]
        self.rect  = pygame.Rect(x, y, size, size)
        self.image = _load_image(self.data["image_path"], size)

        # Animación de bob (suave oscilación vertical)
        self._bob_phase = random.uniform(0, math.tau)
        self._bob_t     = 0.0

    # ── Actualización ──────────────────────────────────────────────────────

    def update(self, dt_ms: float) -> None:
        self._bob_t += dt_ms * 0.003

    def _bob_dy(self) -> int:
        return int(math.sin(self._bob_t + self._bob_phase) * 4)

    # ── Colisión ───────────────────────────────────────────────────────────

    def collides_with(self, player_rect: pygame.Rect) -> bool:
        return self.rect.colliderect(player_rect)

    # ── Dibujado ───────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        dy   = self._bob_dy()
        size = self.data["size"]
        cx   = self.rect.centerx
        cy   = self.rect.centery + dy

        if self.image:
            self._draw_with_image(surface, cx, cy, size, dy)
        else:
            self._draw_fallback(surface, font, cx, cy, size, dy)

    def _draw_with_image(
        self,
        surface : pygame.Surface,
        cx      : int,
        cy      : int,
        size    : int,
        dy      : int,
    ) -> None:
        """Dibuja el sprite con un glow circular de fondo."""
        color_borde = self.data["color_borde"]
        pad         = self.GLOW_PAD

        # Glow: círculo semitransparente detrás del sprite
        glow_surf = pygame.Surface((size + pad * 2, size + pad * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf, (*color_borde, 80),
            (size // 2 + pad, size // 2 + pad),
            size // 2 + pad,
        )
        surface.blit(glow_surf, (cx - size // 2 - pad, cy - size // 2 - pad))

        # Sprite
        surface.blit(self.image, (cx - size // 2, cy - size // 2))

    def _draw_fallback(
        self,
        surface : pygame.Surface,
        font    : pygame.font.Font,
        cx      : int,
        cy      : int,
        size    : int,
        dy      : int,
    ) -> None:
        """Forma de color + símbolo cuando no hay imagen."""
        color       = self.data["color"]
        color_borde = self.data["color_borde"]
        forma       = self.data["forma"]

        if forma == "rect":
            r = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
            pygame.draw.rect(surface, color,       r, border_radius=8)
            pygame.draw.rect(surface, color_borde, r, 2, border_radius=8)
        else:
            pygame.draw.circle(surface, color,       (cx, cy), size // 2)
            pygame.draw.circle(surface, color_borde, (cx, cy), size // 2, 2)

        sym = font.render(self.data["simbolo"], True, (255, 255, 255))
        surface.blit(sym, (cx - sym.get_width() // 2, cy - sym.get_height() // 2))

    # ── Efectos para floating text ─────────────────────────────────────────

    def get_effect_lines(self) -> list[tuple[str, tuple]]:
        lineas = []
        for stat, delta in self.data["efectos"].items():
            signo = "+" if delta >= 0 else ""
            texto = f"{signo}{delta} {STAT_NOMBRE.get(stat, stat)}"
            color = C_POSITIVO if delta > 0 else C_NEGATIVO
            lineas.append((texto, color))
        return lineas

    def __repr__(self) -> str:
        return f"GameObj(tipo='{self.tipo}', pos=({self.rect.x},{self.rect.y}))"


# ─────────────────────────────────────────────────────────────────────────────
#  CLASE: FloatingText
# ─────────────────────────────────────────────────────────────────────────────

class FloatingText:
    """Texto que flota hacia arriba al recoger un objeto y se desvanece."""

    def __init__(self, x: float, y: float, lineas: list[tuple[str, tuple]]) -> None:
        self.x       = float(x)
        self.y       = float(y)
        self.lineas  = lineas
        self.elapsed = 0.0
        self.alive   = True

    def update(self, dt_ms: float) -> None:
        self.elapsed += dt_ms
        self.y       -= FLOAT_SPEED * dt_ms
        if self.elapsed >= FLOAT_LIFETIME:
            self.alive = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if not self.alive:
            return
        progress = self.elapsed / FLOAT_LIFETIME
        alpha    = 255 if progress < 0.6 else int(255 * (1.0 - (progress - 0.6) / 0.4))
        alpha    = max(0, min(255, alpha))
        line_h   = font.get_height() + 2

        for i, (texto, color) in enumerate(self.lineas):
            surf = font.render(texto, True, color)
            surf.set_alpha(alpha)
            surface.blit(surf, (self.x - surf.get_width() // 2, self.y + i * line_h))


# ─────────────────────────────────────────────────────────────────────────────
#  CLASE: ObjectManager
# ─────────────────────────────────────────────────────────────────────────────

class ObjectManager:
    """Gestiona spawn, colisiones, efectos y respawn de todos los objetos."""

    RESPAWN_DELAY = 2_500   # ms
    MAX_OBJETOS   = 6

    # Tipos disponibles y sus pesos de aparición
    TIPOS  = list(OBJETO_CONFIG.keys())
    PESOS  = [3, 3, 2, 2, 1, 2, 1, 1]   # tareas y apuntes más frecuentes

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w       = screen_w
        self.screen_h       = screen_h
        self.objetos        : list[GameObj]           = []
        self.floating_texts : list[FloatingText]      = []
        self._respawn_queue : list[tuple[float, str]] = []
        self._spawn_inicial()
        print(f"[ObjectManager] {len(self.objetos)} objetos generados.")

    # ── Spawn ──────────────────────────────────────────────────────────────

    def _spawn_inicial(self) -> None:
        iniciales = ["tareas", "apuntes", "cafe", "videojuegos", "redes", "beca"]
        for tipo in iniciales[:self.MAX_OBJETOS]:
            self.objetos.append(self._crear_objeto(tipo))

    def _crear_objeto(self, tipo: str, excluir_rect: pygame.Rect = None) -> GameObj:
        size   = OBJETO_CONFIG[tipo]["size"]
        margen = 30
        x_min, x_max = margen, self.screen_w - size - margen
        y_min, y_max = 185,    self.screen_h - size - margen

        for _ in range(20):
            x   = random.randint(x_min, x_max)
            y   = random.randint(y_min, y_max)
            new = pygame.Rect(x, y, size, size)
            solapa = any(new.colliderect(o.rect) for o in self.objetos)
            if excluir_rect:
                solapa = solapa or new.colliderect(excluir_rect.inflate(60, 60))
            if not solapa:
                break

        return GameObj(tipo, x, y)

    # ── Update ─────────────────────────────────────────────────────────────

    def update(
        self,
        dt_ms       : float,
        player_rect : pygame.Rect,
        stats       : "Stats",
    ) -> None:
        now = pygame.time.get_ticks()

        for obj in self.objetos:
            obj.update(dt_ms)

        # Detectar colisiones
        recolectados = [o for o in self.objetos if o.collides_with(player_rect)]
        for obj in recolectados:
            self._aplicar_efectos(obj, stats)
            self.floating_texts.append(
                FloatingText(obj.rect.centerx, obj.rect.centery - 10,
                             obj.get_effect_lines())
            )
            self.objetos.remove(obj)
            tipo_nuevo = random.choices(self.TIPOS, weights=self.PESOS, k=1)[0]
            self._respawn_queue.append((now + self.RESPAWN_DELAY, tipo_nuevo))

        # Respawn
        listos = [(t, tp) for t, tp in self._respawn_queue if now >= t]
        for entry in listos:
            self._respawn_queue.remove(entry)
            if len(self.objetos) < self.MAX_OBJETOS:
                self.objetos.append(self._crear_objeto(entry[1], player_rect))

        # Floating texts
        for ft in self.floating_texts:
            ft.update(dt_ms)
        self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

    def _aplicar_efectos(self, obj: GameObj, stats: "Stats") -> None:
        for stat, delta in obj.data["efectos"].items():
            if stat == "notas"  : stats.modificar_notas(delta)
            elif stat == "energia": stats.modificar_energia(delta)
            elif stat == "dinero" : stats.modificar_dinero(delta)
        print(f"[Colisión] {obj.data['nombre']}: {obj.data['efectos']} → {obj.data['descripcion']}")

    # ── Draw ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for obj in self.objetos:
            obj.draw(surface, font)
        for ft in self.floating_texts:
            ft.draw(surface, font)

    # ── Reset ──────────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.objetos.clear()
        self.floating_texts.clear()
        self._respawn_queue.clear()
        self._spawn_inicial()

    def cantidad(self) -> int:
        return len(self.objetos)

    def __repr__(self) -> str:
        return (f"ObjectManager(activos={len(self.objetos)}, "
                f"respawn={len(self._respawn_queue)}, "
                f"flotantes={len(self.floating_texts)})")
