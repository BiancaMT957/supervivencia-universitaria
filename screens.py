"""
screens.py
"Supervivencia Universitaria: La Vida Da Vueltas"

Funcionalidad #10 – Pantallas finales (diseño visual rico).
Funcionalidad  #6 – Victoria y derrota (lógica de evaluación y disparo).

Expone:
    · check_victoria_derrota(stats)  → str | None
          Evalúa Stats y devuelve el estado final ("victoria", "derrota_*")
          o None si la partida continúa.  Reemplaza la llamada directa a
          stats.estado_juego() == "jugando" en el game loop.

    · ScreenManager
          Gestiona la transición hacia la pantalla final adecuada y la
          dibuja cada frame mientras STATE_OVER esté activo.

          Uso:
            screen_mgr = ScreenManager(screen_w, screen_h, bg_finals)
            # cuando el juego detecta fin:
            screen_mgr.activar(estado_final, stats, elapsed_ms)
            # cada frame en STATE_OVER:
            screen_mgr.draw(surface, font_big, font_med, font_small, clock)
"""

import math
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stats import Stats

# ─────────────────────────────────────────────
#  PALETA
# ─────────────────────────────────────────────
C_TEXT      = (255, 255, 255)
C_ACCENT    = (255, 200,  50)
C_VICTORIA  = ( 50, 220,  90)
C_DERROTA   = (210,  40,  40)
C_DIM       = (160, 160, 180)
C_PANEL_BG  = ( 15,  10,  30, 230)
C_PANEL_BD  = ( 90,  90, 130)


# ─────────────────────────────────────────────
#  FUNCIÓN PÚBLICA: check_victoria_derrota
# ─────────────────────────────────────────────

def check_victoria_derrota(stats: "Stats") -> "str | None":
    """
    Evalúa el estado del juego.

    Retorna:
        None              → partida continúa
        "victoria"        → notas llegaron a 20
        "derrota_energia" → energía llegó a 0
        "derrota_dinero"  → dinero llegó a 0
        "derrota_notas"   → notas llegaron a 0

    Encapsula stats.estado_juego() para que main.py no llame directamente
    a Stats, manteniendo la separación de responsabilidades.
    """
    estado = stats.estado_juego()
    return None if estado == "jugando" else estado


# ─────────────────────────────────────────────
#  CONTENIDO DE CADA PANTALLA FINAL
# ─────────────────────────────────────────────

_CONTENIDO: dict[str, dict] = {
    "victoria": {
        "titulo"   : "¡APROBASTE!",
        "subtitulo": "Sobreviviste el semestre universitario.",
        "detalle"  : "Tus notas llegaron al máximo. ¡Eres la leyenda del campus!",
        "emoji"    : "🎓",
        "color"    : C_VICTORIA,
    },
    "derrota_energia": {
        "titulo"   : "SIN ENERGÍA",
        "subtitulo": "El estudiante colapsó de agotamiento.",
        "detalle"  : "No descansaste lo suficiente. El cuerpo tiene límites.",
        "emoji"    : "💤",
        "color"    : C_DERROTA,
    },
    "derrota_dinero": {
        "titulo"   : "SIN DINERO",
        "subtitulo": "No puedes cubrir tus gastos universitarios.",
        "detalle"  : "La cuenta llegó a S/0. Fin del semestre por deudas.",
        "emoji"    : "💸",
        "color"    : C_DERROTA,
    },
    "derrota_notas": {
        "titulo"   : "¡JALADO!",
        "subtitulo": "Las notas cayeron a cero. Fin del ciclo.",
        "detalle"  : "Demasiadas distracciones. El ciclo se perdió.",
        "emoji"    : "📉",
        "color"    : C_DERROTA,
    },
}


# ─────────────────────────────────────────────
#  HELPERS DE DIBUJO
# ─────────────────────────────────────────────

def _draw_panel_centrado(surface: pygame.Surface,
                         cx: int, cy: int,
                         w: int, h: int) -> None:
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, C_PANEL_BG, (0, 0, w, h), border_radius=14)
    pygame.draw.rect(panel, C_PANEL_BD, (0, 0, w, h), 2, border_radius=14)
    surface.blit(panel, (cx - w // 2, cy - h // 2))


def _draw_particles(surface: pygame.Surface,
                    screen_w: int, screen_h: int,
                    color: tuple, t_ms: float) -> None:
    """Partículas de celebración/colapso simples basadas en tiempo."""
    rng = __import__("random").Random(42)   # semilla fija → mismas posiciones
    for _ in range(22):
        x0   = rng.randint(0, screen_w)
        spd  = rng.uniform(0.04, 0.12)
        size = rng.randint(3, 7)
        y    = int((x0 * 1.3 + t_ms * spd) % screen_h)
        alpha = rng.randint(60, 180)
        s    = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color[:3], alpha), (size, size), size)
        surface.blit(s, (x0, y))


def _resumen_stats(stats: "Stats") -> list[tuple[str, str]]:
    """Devuelve lista (etiqueta, valor) con el resumen final de stats."""
    return [
        ("Energía final",  f"{int(stats.energia)}/100"),
        ("Dinero final",   f"S/{int(stats.dinero)}"),
        ("Notas finales",  f"{stats.notas:.1f}/20"),
    ]


# ─────────────────────────────────────────────
#  CLASE: ScreenManager
# ─────────────────────────────────────────────

class ScreenManager:
    """
    Gestiona las pantallas finales (victoria / derrota_*).

    Constructor:
        screen_w, screen_h : dimensiones de la ventana
        bg_finals          : Surface de fondo (puede ser None)
    """

    def __init__(self,
                 screen_w   : int,
                 screen_h   : int,
                 bg_finals  : "pygame.Surface | None" = None) -> None:
        self.screen_w   = screen_w
        self.screen_h   = screen_h
        self.bg_finals  = bg_finals
        self._estado    : str | None = None
        self._stats_snap: dict       = {}   # snapshot al activarse
        self._elapsed_ms: float      = 0.0  # tiempo de juego al activarse
        self._t_anim    : float      = 0.0  # tiempo dentro de la pantalla final

    # ── Activar ───────────────────────────────────────────────────────

    def activar(self,
                estado    : str,
                stats     : "Stats",
                elapsed_ms: float = 0.0) -> None:
        """
        Llama a esto en el game loop cuando check_victoria_derrota() no devuelva None.
        Guarda un snapshot de Stats para mostrarlo en la pantalla final.
        """
        self._estado     = estado
        self._elapsed_ms = elapsed_ms
        self._t_anim     = 0.0
        self._stats_snap = {
            "energia": stats.energia,
            "dinero" : stats.dinero,
            "notas"  : stats.notas,
        }
        print(f"[ScreenManager] Pantalla final activada: {estado}")

    # ── Update (acumular tiempo de animación) ─────────────────────────

    def update(self, dt_ms: float) -> None:
        self._t_anim += dt_ms

    # ── Draw ──────────────────────────────────────────────────────────

    def draw(self,
             surface   : pygame.Surface,
             font_big  : pygame.font.Font,
             font_med  : pygame.font.Font,
             font_small: pygame.font.Font,
             clock     : pygame.time.Clock) -> None:
        """Dibuja la pantalla final completa.  Llamar cada frame en STATE_OVER."""
        if self._estado is None:
            return

        contenido = _CONTENIDO.get(self._estado, _CONTENIDO["derrota_notas"])
        color     = contenido["color"]
        cx        = self.screen_w // 2
        cy        = self.screen_h // 2

        # ── Fondo ──────────────────────────────────────────────────────
        if self.bg_finals:
            surface.blit(self.bg_finals, (0, 0))
        else:
            surface.fill((10, 8, 25))

        # Overlay oscuro
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        # Partículas animadas
        _draw_particles(surface, self.screen_w, self.screen_h, color, self._t_anim)

        # ── Panel principal ────────────────────────────────────────────
        _draw_panel_centrado(surface, cx, cy - 20, 520, 300)

        # Entrada animada (fade-in en ~600 ms)
        alpha_texto = min(255, int(self._t_anim / 600 * 255))

        # Emoji / icono
        icono_surf = font_big.render(contenido["emoji"], True, color)
        icono_surf.set_alpha(alpha_texto)
        surface.blit(icono_surf, (cx - icono_surf.get_width() // 2, cy - 150))

        # Título con pulso suave
        pulse = 1.0 + 0.04 * math.sin(self._t_anim * 0.003)
        titulo_surf = font_big.render(contenido["titulo"], True, color)
        w_t = int(titulo_surf.get_width() * pulse)
        h_t = int(titulo_surf.get_height() * pulse)
        titulo_scaled = pygame.transform.scale(titulo_surf, (w_t, h_t))
        titulo_scaled.set_alpha(alpha_texto)
        surface.blit(titulo_scaled, (cx - w_t // 2, cy - 105))

        # Subtítulo
        sub_surf = font_med.render(contenido["subtitulo"], True, C_TEXT)
        sub_surf.set_alpha(alpha_texto)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, cy - 62))

        # Detalle
        det_surf = font_small.render(contenido["detalle"], True, C_DIM)
        det_surf.set_alpha(alpha_texto)
        surface.blit(det_surf, (cx - det_surf.get_width() // 2, cy - 32))

        # ── Resumen de stats ───────────────────────────────────────────
        resumen = [
            ("Energía final", f"{int(self._stats_snap.get('energia', 0))}/100"),
            ("Dinero final",  f"S/{int(self._stats_snap.get('dinero', 0))}"),
            ("Notas finales", f"{self._stats_snap.get('notas', 0):.1f}/20"),
        ]
        y_res = cy + 10
        for label, valor in resumen:
            col_lbl = font_small.render(f"{label}:", True, C_DIM)
            col_val = font_small.render(valor,        True, C_ACCENT)
            col_lbl.set_alpha(alpha_texto)
            col_val.set_alpha(alpha_texto)
            surface.blit(col_lbl, (cx - 130, y_res))
            surface.blit(col_val, (cx + 20,  y_res))
            y_res += 26

        # ── Instrucciones (aparecen después de 1 s) ────────────────────
        if self._t_anim > 1_000:
            alpha_inst = min(255, int((self._t_anim - 1_000) / 500 * 255))
            inst_surf  = font_small.render(
                "R = reiniciar     |     ESC = salir", True, C_ACCENT
            )
            inst_surf.set_alpha(alpha_inst)
            surface.blit(inst_surf,
                         (cx - inst_surf.get_width() // 2, cy + 105))

        # ── Tiempo de partida ──────────────────────────────────────────
        mins  = int(self._elapsed_ms // 60_000)
        segs  = int((self._elapsed_ms % 60_000) // 1_000)
        t_surf = font_small.render(f"Tiempo jugado: {mins}m {segs:02d}s", True, C_DIM)
        t_surf.set_alpha(alpha_texto)
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, cy + 135))

    # ── Reset ─────────────────────────────────────────────────────────

    def reset(self) -> None:
        self._estado     = None
        self._stats_snap = {}
        self._elapsed_ms = 0.0
        self._t_anim     = 0.0

    def __repr__(self) -> str:
        return f"ScreenManager(estado='{self._estado}', t_anim={self._t_anim:.0f}ms)"
