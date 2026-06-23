"""
main.py
=======
"Supervivencia Universitaria: La Vida Da Vueltas"

Issues integrados:
    #1 – Movimiento del jugador   (player.py)
    #4 – Sistema de estadísticas  (stats.py)
    #2 – Colisiones y recolección (objects.py)

Assets integrados:
    assets/backgrounds/menu.png
    assets/backgrounds/campus.png
    assets/backgrounds/finals_bg.png   ← reservado para Escenario 2
    assets/player/player.png
    assets/objects/task.png  notes.png  coffee.png  scholarship.png
                   gamepad.png  distraction.png  broken_laptop.png  sick.png

Controles:
    ESPACIO / ENTER   →  Iniciar desde el menú
    Flechas / WASD    →  Mover al estudiante
    R                 →  Reiniciar
    ESC               →  Salir
"""

import sys
import pygame

from player  import Player
from stats   import Stats
from objects import ObjectManager

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────

SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Supervivencia Universitaria: La Vida Da Vueltas"

# Rutas de assets
BG_MENU    = "assets/menu.png"
BG_CAMPUS  = "assets/campus.png"
PLAYER_IMG = "assets/player.png"

# Colores de fallback (se usan si el asset no carga)
C_BG_MENU   = ( 15,  15,  35)
C_BG_CAMPUS = ( 30,  30,  50)
C_GRID      = ( 45,  45,  70)
C_TEXT      = (255, 255, 255)
C_ACCENT    = (255, 200,  50)
C_DERROTA   = (180,  30,  30)
C_VICTORIA  = ( 30, 180,  60)
C_BORDE     = (200,  60,  60)

# Estados de la aplicación
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_OVER    = "over"


# ─────────────────────────────────────────────────────────────────────────────
#  CARGA DE IMÁGENES CON FALLBACK
# ─────────────────────────────────────────────────────────────────────────────

def load_bg(path: str) -> pygame.Surface | None:
    """Carga un fondo y lo escala a la pantalla. Devuelve None si falla."""
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
    except (pygame.error, FileNotFoundError):
        print(f"[assets] Fondo no encontrado: '{path}' — usando color sólido.")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  FUNCIONES DE RENDER
# ─────────────────────────────────────────────────────────────────────────────

def draw_background(
    surface   : pygame.Surface,
    bg_image  : pygame.Surface | None,
    fallback  : tuple,
    with_grid : bool = True,
) -> None:
    """Dibuja el fondo: imagen si existe, color sólido + cuadrícula si no."""
    if bg_image:
        surface.blit(bg_image, (0, 0))
    else:
        surface.fill(fallback)
        if with_grid:
            for x in range(0, SCREEN_W, 50):
                pygame.draw.line(surface, C_GRID, (x, 0), (x, SCREEN_H))
            for y in range(0, SCREEN_H, 50):
                pygame.draw.line(surface, C_GRID, (0, y), (SCREEN_W, y))

    # Borde rojo en modo sin imagen (confirma límites)
    if not bg_image:
        pygame.draw.rect(surface, C_BORDE, (0, 0, SCREEN_W, SCREEN_H), 3)


def draw_menu(
    surface    : pygame.Surface,
    bg_menu    : pygame.Surface | None,
    font_title : pygame.font.Font,
    font_sub   : pygame.font.Font,
) -> None:
    """Pantalla de menú principal."""
    draw_background(surface, bg_menu, C_BG_MENU, with_grid=False)

    # Overlay semitransparente para legibilidad si hay imagen de fondo
    if bg_menu:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

    cx = SCREEN_W // 2
    title1 = font_title.render("SUPERVIVENCIA UNIVERSITARIA", True, C_ACCENT)
    title2 = font_title.render("La Vida Da Vueltas", True, C_TEXT)
    sub    = font_sub.render("ESPACIO o ENTER para iniciar", True, C_ACCENT)
    esc    = font_sub.render("ESC para salir", True, (180, 180, 180))

    surface.blit(title1, (cx - title1.get_width() // 2, 180))
    surface.blit(title2, (cx - title2.get_width() // 2, 230))
    surface.blit(sub,    (cx - sub.get_width()    // 2, 340))
    surface.blit(esc,    (cx - esc.get_width()    // 2, 380))


def draw_leyenda(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Leyenda de objetos en la parte inferior izquierda."""
    items = [
        ("TAR", "Tarea       +2 Notas -10 Eng",     ( 70, 140, 230)),
        ("APT", "Apuntes     +1 Notas  -5 Eng",     ( 40, 190, 150)),
        ("CFE", "Cafe       +25 Eng   -S/30",        (160,  90,  40)),
        ("BCA", "Beca        +1 Nota  +S/200",       (220, 180,  30)),
        ("VJ",  "Videojuegos -3 Notas -15 Eng -S/30",(130,  50, 210)),
        ("RS",  "Distraccion -2 Notas  -5 Eng -S/20",(220,  60, 130)),
        ("BLT", "Laptop Rota -2 Notas -S/50",        (180,  60,  60)),
        ("ENF", "Enfermedad  -2 Notas -20 Eng",      ( 80, 170,  80)),
    ]
    base_y = SCREEN_H - 10 - len(items) * 17
    for i, (sim, desc, col) in enumerate(items):
        s = font.render(f"[{sim}] {desc}", True, col)
        surface.blit(s, (10, base_y + i * 17))


def draw_hud_overlay(
    surface : pygame.Surface,
    font    : pygame.font.Font,
    clock   : pygame.time.Clock,
    obj_mgr : ObjectManager,
) -> None:
    """FPS y conteo de objetos en esquina superior derecha."""
    fps = font.render(f"FPS: {clock.get_fps():.0f}", True, C_ACCENT)
    cnt = font.render(f"Objetos: {obj_mgr.cantidad()}", True, C_ACCENT)
    surface.blit(fps, (SCREEN_W - fps.get_width() - 10, SCREEN_H - 24))
    surface.blit(cnt, (SCREEN_W - cnt.get_width() - 10, 10))


def draw_controls(surface: pygame.Surface, font: pygame.font.Font) -> None:
    lines = ["Mover: Flechas / WASD", "R: Reiniciar  ESC: Salir"]
    for i, l in enumerate(lines):
        s = font.render(l, True, C_TEXT)
        surface.blit(s, (SCREEN_W - s.get_width() - 10, 30 + i * 18))


def draw_game_over(
    surface    : pygame.Surface,
    font_big   : pygame.font.Font,
    font_small : pygame.font.Font,
    estado     : str,
) -> None:
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    mensajes = {
        "derrota_energia": ("Sin energia!",  "El estudiante colapso de agotamiento."),
        "derrota_dinero" : ("Sin dinero!",   "No puedes cubrir tus gastos universitarios."),
        "derrota_notas"  : ("Jalado!",       "Las notas cayeron a cero. Fin del ciclo."),
        "victoria"       : ("Aprobaste!",    "Sobreviviste el semestre universitario!"),
    }
    titulo, sub = mensajes.get(estado, ("Game Over", ""))
    color = C_VICTORIA if estado == "victoria" else C_DERROTA
    cx    = SCREEN_W // 2

    t = font_big.render(titulo, True, color)
    s = font_small.render(sub,   True, C_TEXT)
    r = font_small.render("R = reiniciar   |   ESC = salir", True, C_ACCENT)
    surface.blit(t, (cx - t.get_width() // 2, 210))
    surface.blit(s, (cx - s.get_width() // 2, 275))
    surface.blit(r, (cx - r.get_width() // 2, 330))


# ─────────────────────────────────────────────────────────────────────────────
#  FÁBRICAS
# ─────────────────────────────────────────────────────────────────────────────

def make_player() -> Player:
    return Player(
        x             = SCREEN_W  // 2 - 20,
        y             = SCREEN_H  // 2 - 30,
        screen_width  = SCREEN_W,
        screen_height = SCREEN_H,
        speed         = 4,
        image_path    = PLAYER_IMG,   # ← usa el sprite del jugador
    )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    font_sym   = pygame.font.SysFont("consolas", 13, bold=True)
    font_hud   = pygame.font.SysFont("consolas", 15)
    font_title = pygame.font.SysFont("arial",    30, bold=True)
    font_big   = pygame.font.SysFont("arial",    52, bold=True)
    font_small = pygame.font.SysFont("arial",    22)

    # ── Cargar fondos ──────────────────────────────────────────────────────
    bg_menu   = load_bg(BG_MENU)
    bg_campus = load_bg(BG_CAMPUS)
    # bg_finals = load_bg("assets/finals_bg.png")  ← Issue #3

    # ── Estado de la app ───────────────────────────────────────────────────
    app_state = STATE_MENU
    player    = None
    stats     = None
    obj_mgr   = None

    def start_game():
        nonlocal player, stats, obj_mgr, app_state
        player    = make_player()
        stats     = Stats()
        obj_mgr   = ObjectManager(SCREEN_W, SCREEN_H)
        app_state = STATE_PLAYING
        print("[main] Partida iniciada.")

    # ── GAME LOOP ──────────────────────────────────────────────────────────
    running = True
    while running:
        dt_ms = clock.tick(FPS)

        # ── EVENTOS ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if app_state == STATE_PLAYING:
                        app_state = STATE_MENU   # volver al menú
                    else:
                        running = False

                # Iniciar desde menú o reiniciar desde fin
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if app_state == STATE_MENU:
                        start_game()

                if event.key == pygame.K_r:
                    if app_state in (STATE_PLAYING, STATE_OVER):
                        start_game()   # reinicio completo

        # ── UPDATE ─────────────────────────────────────────────────────────
        if app_state == STATE_PLAYING:
            game_estado = stats.estado_juego()

            if game_estado == "jugando":
                keys = pygame.key.get_pressed()
                player.update(keys)
                obj_mgr.update(float(dt_ms), player.get_rect(), stats)
            else:
                app_state = STATE_OVER

        # ── RENDER ─────────────────────────────────────────────────────────
        if app_state == STATE_MENU:
            draw_menu(screen, bg_menu, font_title, font_small)

        elif app_state in (STATE_PLAYING, STATE_OVER):
            # Fondo del campus
            draw_background(screen, bg_campus, C_BG_CAMPUS)

            # Título de escenario (Escenario 1)
            t = font_title.render("Campus — Ciclo I", True, C_ACCENT)
            # Sombra sutil para legibilidad sobre la imagen
            t_shadow = font_title.render("Campus — Ciclo I", True, (0, 0, 0))
            screen.blit(t_shadow, (SCREEN_W // 2 - t.get_width() // 2 + 2, 16))
            screen.blit(t,        (SCREEN_W // 2 - t.get_width() // 2,     14))

            # Objetos → jugador (orden: objetos debajo, jugador encima)
            obj_mgr.draw(screen, font_sym)
            player.draw(screen)

            # HUD de estadísticas
            stats.draw_hud(screen, font_hud, x=10, y=50)

            # Leyenda, controles, FPS
            draw_leyenda(screen, font_hud)
            draw_controls(screen, font_hud)
            draw_hud_overlay(screen, font_hud, clock, obj_mgr)

            # Overlay de fin si corresponde
            if app_state == STATE_OVER:
                draw_game_over(screen, font_big, font_small, stats.estado_juego())

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
