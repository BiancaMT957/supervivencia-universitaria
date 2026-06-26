import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stats   import Stats
    from objects import ObjectManager
    from events  import RandomEvent

C_ACCENT       = (255, 200,  50)
C_TEXT         = (255, 255, 255)
C_PELIGRO_GLOW = (210,  40,  40, 60)
C_OK_GLOW      = ( 60, 200,  80, 40)
C_EVENTO_BG    = ( 20,  10,  40, 210)
C_EVENTO_BORDE = (180,  80, 255)
C_BARRA_TIEMPO = ( 80,  60, 180)
C_BARRA_LLENA  = ( 60, 200, 240)
C_BARRA_ALERTA = (255, 140,  30)
C_BARRA_CRITICA= (220,  40,  40)

def _draw_panel(surface: pygame.Surface,
                x: int, y: int, w: int, h: int,
                bg_rgba=(20, 20, 45, 200),
                border_color=(90, 90, 130),
                radius: int = 8) -> None:
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg_rgba,      (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(panel, border_color, (0, 0, w, h), 1, border_radius=radius)
    surface.blit(panel, (x, y))

def _draw_peligro_glow(surface: pygame.Surface,
                       screen_w: int, screen_h: int,
                       stats: "Stats") -> None:
    if not stats.esta_en_peligro():
        return

    t   = pygame.time.get_ticks()
    pct = 0.45 + 0.35 * abs(__import__("math").sin(t * 0.003))
    alpha = int(pct * 120)

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    franja = 18
    for rect in [
        (0,                   0,          screen_w, franja),
        (0,   screen_h - franja,          screen_w, franja),
        (0,                   0,          franja,   screen_h),
        (screen_w - franja,   0,          franja,   screen_h),
    ]:
        pygame.draw.rect(overlay, (210, 40, 40, alpha), rect)
    surface.blit(overlay, (0, 0))

def _draw_barra_tiempo(surface: pygame.Surface,
                       font: pygame.font.Font,
                       elapsed_ms: float,
                       duracion_ms: float,
                       screen_w: int,
                       y: int = 6) -> None:
    BAR_W = 320
    BAR_H = 14
    x     = screen_w // 2 - BAR_W // 2

    progreso = min(1.0, elapsed_ms / duracion_ms)

    pygame.draw.rect(surface, (40, 40, 70), (x, y, BAR_W, BAR_H), border_radius=6)

    fill_w = int(BAR_W * progreso)
    if fill_w > 0:
        if progreso < 0.6:
            color = C_BARRA_LLENA
        elif progreso < 0.85:
            color = C_BARRA_ALERTA
        else:
            color = C_BARRA_CRITICA
        pygame.draw.rect(surface, color, (x, y, fill_w, BAR_H), border_radius=6)

    pygame.draw.rect(surface, (90, 90, 130), (x, y, BAR_W, BAR_H), 1, border_radius=6)

    pct_restante = int((1 - progreso) * 100)
    label = font.render(f"Semestre  {pct_restante}% restante", True, C_TEXT)
    surface.blit(label, (screen_w // 2 - label.get_width() // 2, y + BAR_H + 2))

def _draw_evento_activo(surface: pygame.Surface,
                        font_big: pygame.font.Font,
                        font_small: pygame.font.Font,
                        evento: "RandomEvent | None",
                        screen_w: int) -> None:
    if evento is None or not evento.activo:
        return

    PANEL_W  = 420
    PANEL_H  = 70
    x        = screen_w // 2 - PANEL_W // 2
    y        = 32

    _draw_panel(surface, x, y, PANEL_W, PANEL_H,
                bg_rgba=(20, 10, 40, 210),
                border_color=C_EVENTO_BORDE)

    seg_rest = max(0, int(evento.tiempo_restante_ms / 1000))
    titulo = font_big.render(f"⚠ {evento.nombre}  ({seg_rest}s)", True, C_EVENTO_BORDE)
    desc   = font_small.render(evento.descripcion_corta, True, C_TEXT)

    cx = x + PANEL_W // 2
    surface.blit(titulo, (cx - titulo.get_width() // 2, y + 6))
    surface.blit(desc,   (cx - desc.get_width()   // 2, y + 36))

def _draw_mini_overlay(surface: pygame.Surface,
                       font: pygame.font.Font,
                       clock: pygame.time.Clock,
                       obj_mgr: "ObjectManager",
                       screen_w: int,
                       screen_h: int) -> None:
    fps = font.render(f"FPS: {clock.get_fps():.0f}", True, C_ACCENT)
    cnt = font.render(f"Obj: {obj_mgr.cantidad()}", True, C_ACCENT)
    surface.blit(fps, (screen_w - fps.get_width() - 10, screen_h - 22))
    surface.blit(cnt, (screen_w - cnt.get_width() - 10, screen_h - 40))

def draw_hud_enriched(
    surface       : pygame.Surface,
    font_hud      : pygame.font.Font,
    font_sym      : pygame.font.Font,
    clock         : pygame.time.Clock,
    obj_mgr       : "ObjectManager",
    stats         : "Stats",
    screen_w      : int,
    screen_h      : int,
    elapsed_ms    : float = 0.0,
    duracion_ms   : float = 300_000.0,
    evento_activo : "RandomEvent | None" = None,
) -> None:
    _draw_peligro_glow(surface, screen_w, screen_h, stats)
    _draw_barra_tiempo(surface, font_hud, elapsed_ms, duracion_ms, screen_w)
    _draw_evento_activo(surface, font_hud, font_sym, evento_activo, screen_w)
    _draw_mini_overlay(surface, font_hud, clock, obj_mgr, screen_w, screen_h)