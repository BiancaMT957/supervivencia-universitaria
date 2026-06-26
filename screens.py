import math
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stats import Stats

# paleta ui
C_TEXT      = (255, 255, 255)
C_ACCENT    = (255, 200,  50)
C_VICTORIA  = ( 50, 220,  90)
C_DERROTA   = (210,  40,  40)
C_DIM       = (160, 160, 180)
C_PANEL_BG  = ( 15,  10,  30, 230)
C_PANEL_BD  = ( 90,  90, 130)

def check_victoria_derrota(stats: "Stats") -> "str | None":
    estado = stats.estado_juego()
    if estado == "victoria":
        return None
    return None if estado == "jugando" else estado

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
    rng = __import__("random").Random(42)
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
    return [
        ("Energía final",  f"{int(stats.energia)}/100"),
        ("Dinero final",   f"S/{int(stats.dinero)}"),
        ("Notas finales",  f"{stats.notas:.1f}/20"),
    ]

class ScreenManager:
    def __init__(self,
                 screen_w   : int,
                 screen_h   : int,
                 bg_finals  : "pygame.Surface | None" = None) -> None:
        self.screen_w   = screen_w
        self.screen_h   = screen_h
        self.bg_finals  = bg_finals
        self._estado    : str | None = None
        self._stats_snap: dict       = {}
        self._elapsed_ms: float      = 0.0
        self._t_anim    : float      = 0.0

    def activar(self,
                estado    : str,
                stats     : "Stats",
                elapsed_ms: float = 0.0) -> None:
        self._estado     = estado
        self._elapsed_ms = elapsed_ms
        self._t_anim     = 0.0
        self._stats_snap = {
            "energia": stats.energia,
            "dinero" : stats.dinero,
            "notas"  : stats.notas,
        }
        print(f"[ScreenManager] Pantalla final activada: {estado}")

    def update(self, dt_ms: float) -> None:
        self._t_anim += dt_ms

    def draw(self,
             surface   : pygame.Surface,
             font_big  : pygame.font.Font,
             font_med  : pygame.font.Font,
             font_small: pygame.font.Font,
             clock     : pygame.time.Clock) -> None:
        if self._estado is None:
            return

        contenido = _CONTENIDO.get(self._estado, _CONTENIDO["derrota_notas"])
        color     = contenido["color"]
        cx        = self.screen_w // 2
        cy        = self.screen_h // 2

        if self.bg_finals:
            surface.blit(self.bg_finals, (0, 0))
        else:
            surface.fill((10, 8, 25))

        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        _draw_particles(surface, self.screen_w, self.screen_h, color, self._t_anim)
        _draw_panel_centrado(surface, cx, cy - 20, 520, 300)

        alpha_texto = min(255, int(self._t_anim / 600 * 255))

        icono_surf = font_big.render(contenido["emoji"], True, color)
        icono_surf.set_alpha(alpha_texto)
        surface.blit(icono_surf, (cx - icono_surf.get_width() // 2, cy - 150))

        pulse = 1.0 + 0.04 * math.sin(self._t_anim * 0.003)
        titulo_surf = font_big.render(contenido["titulo"], True, color)
        w_t = int(titulo_surf.get_width() * pulse)
        h_t = int(titulo_surf.get_height() * pulse)
        titulo_scaled = pygame.transform.scale(titulo_surf, (w_t, h_t))
        titulo_scaled.set_alpha(alpha_texto)
        surface.blit(titulo_scaled, (cx - w_t // 2, cy - 105))

        sub_surf = font_med.render(contenido["subtitulo"], True, C_TEXT)
        sub_surf.set_alpha(alpha_texto)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, cy - 62))

        det_surf = font_small.render(contenido["detalle"], True, C_DIM)
        det_surf.set_alpha(alpha_texto)
        surface.blit(det_surf, (cx - det_surf.get_width() // 2, cy - 32))

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

        if self._t_anim > 1_000:
            alpha_inst = min(255, int((self._t_anim - 1_000) / 500 * 255))
            inst_surf  = font_small.render(
                "R = reiniciar     |     ESC = salir", True, C_ACCENT
            )
            inst_surf.set_alpha(alpha_inst)
            surface.blit(inst_surf,
                         (cx - inst_surf.get_width() // 2, cy + 105))

        mins  = int(self._elapsed_ms // 60_000)
        segs  = int((self._elapsed_ms % 60_000) // 1_000)
        t_surf = font_small.render(f"Tiempo jugado: {mins}m {segs:02d}s", True, C_DIM)
        t_surf.set_alpha(alpha_texto)
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, cy + 135))

    def reset(self) -> None:
        self._estado     = None
        self._stats_snap = {}
        self._elapsed_ms = 0.0
        self._t_anim     = 0.0

    def __repr__(self) -> str:
        return f"ScreenManager(estado='{self._estado}', t_anim={self._t_anim:.0f}ms)"