"""
main.py
"Supervivencia Universitaria: La Vida Da Vueltas"

Controles:
    ESPACIO / ENTER   →  Iniciar desde el menú
    Flechas / WASD    →  Mover al estudiante
    R                 →  Reiniciar
    ESC               →  Volver al menú (durante juego) / Salir (en menú u otros)
"""

import sys
import pygame

from player  import Player
from stats   import Stats
from objects import ObjectManager

# ── Nuevos módulos (#9 HUD, #5 Eventos, #7 Menú, #3 Escenas, #10 Finales, #6 Victoria/Derrota) ──
from ui      import draw_hud_enriched
from events  import EventManager
from scenes  import SceneManager, MenuRenderer
from screens import ScreenManager, check_victoria_derrota


# ─────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────

SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Supervivencia Universitaria: La Vida Da Vueltas"

# Rutas de assets
BG_MENU    = "assets/menu.png"
BG_CAMPUS  = "assets/campus.png"
BG_FINALS  = "assets/finals_bg.png"
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

# Duración del semestre (ms)
DURACION_SEMESTRE = 300_000.0   # 5 minutos


# ─────────────────────────────────────────────
#  CARGA DE IMÁGENES CON FALLBACK
# ─────────────────────────────────────────────

def load_bg(path: str) -> pygame.Surface | None:
    """Carga un fondo y lo escala a la pantalla. Devuelve None si falla."""
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
    except (pygame.error, FileNotFoundError):
        print(f"[assets] Fondo no encontrado: '{path}' — usando color sólido.")
        return None


# ─────────────────────────────────────────────
#  FUNCIONES DE RENDER (auxiliares, sin cambios)
# ─────────────────────────────────────────────

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


def draw_leyenda(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Leyenda de objetos en la parte inferior izquierda."""
    items = [
        ("TAR", "Tarea       +2 Notas -10 Eng",      ( 70, 140, 230)),
        ("APT", "Apuntes     +1 Notas  -5 Eng",      ( 40, 190, 150)),
        ("CFE", "Cafe       +25 Eng   -S/30",         (160,  90,  40)),
        ("BCA", "Beca        +1 Nota  +S/200",        (220, 180,  30)),
        ("VJ",  "Videojuegos -3 Notas -15 Eng -S/30", (130,  50, 210)),
        ("RS",  "Distraccion -2 Notas  -5 Eng -S/20", (220,  60, 130)),
        ("BLT", "Laptop Rota -2 Notas -S/50",         (180,  60,  60)),
        ("ENF", "Enfermedad  -2 Notas -20 Eng",       ( 80, 170,  80)),
    ]
    base_y = SCREEN_H - 10 - len(items) * 17
    for i, (sim, desc, col) in enumerate(items):
        s = font.render(f"[{sim}] {desc}", True, col)
        surface.blit(s, (10, base_y + i * 17))


def draw_controls(surface: pygame.Surface, font: pygame.font.Font) -> None:
    lines = ["Mover: Flechas / WASD", "R: Reiniciar  ESC: Menú"]
    for i, l in enumerate(lines):
        s = font.render(l, True, C_TEXT)
        surface.blit(s, (SCREEN_W - s.get_width() - 10, 30 + i * 18))


# ─────────────────────────────────────────────
#  FÁBRICAS
# ─────────────────────────────────────────────

def make_player() -> Player:
    return Player(
        x             = SCREEN_W  // 2 - 20,
        y             = SCREEN_H  // 2 - 30,
        screen_width  = SCREEN_W,
        screen_height = SCREEN_H,
        speed         = 4,
        image_path    = PLAYER_IMG,
    )


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    # Fuentes
    font_sym   = pygame.font.SysFont("consolas", 13, bold=True)
    font_hud   = pygame.font.SysFont("consolas", 15)
    font_title = pygame.font.SysFont("arial",    30, bold=True)
    font_big   = pygame.font.SysFont("arial",    52, bold=True)
    font_small = pygame.font.SysFont("arial",    22)

    # Fondos
    bg_menu   = load_bg(BG_MENU)
    bg_campus = load_bg(BG_CAMPUS)
    bg_finals = load_bg(BG_FINALS)   # None si no existe el archivo

    # ── Managers nuevos (#3, #7, #10) ──────────────────────────────────
    scene_mgr  = SceneManager(SCREEN_W, SCREEN_H)
    menu_rend  = MenuRenderer(SCREEN_W, SCREEN_H, bg_menu)
    screen_mgr = ScreenManager(SCREEN_W, SCREEN_H, bg_finals)

    # ── Estado de la app ───────────────────────────────────────────────
    app_state = STATE_MENU
    player    = None
    stats     = None
    obj_mgr   = None
    event_mgr = None           # (#5) inicializado en start_game()
    elapsed_ms = 0.0           # tiempo acumulado de la partida activa

    # ── start_game ─────────────────────────────────────────────────────
    def start_game() -> None:
        nonlocal player, stats, obj_mgr, app_state, event_mgr, elapsed_ms
        player     = make_player()
        stats      = Stats()
        obj_mgr    = ObjectManager(SCREEN_W, SCREEN_H)
        event_mgr  = EventManager()       # (#5) nuevo manager de eventos
        elapsed_ms = 0.0                  # resetear cronómetro
        screen_mgr.reset()               # (#10) limpiar pantalla final
        app_state  = STATE_PLAYING
        print("[main] Partida iniciada.")

    # ── GAME LOOP ───────────────────────────────────────────────────────
    running = True

    while running:
        dt_ms = clock.tick(FPS)

        # Actualizar animaciones del menú cada frame (fuera del for de eventos)
        menu_rend.update(dt_ms)          # (#7) animación de título y botones

        # ── CAPTURA DE EVENTOS ────────────────────────────────────────
        eventos = pygame.event.get()     # lista capturada una sola vez

        for event in eventos:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if app_state == STATE_PLAYING:
                        scene_mgr.goto_menu()    # (#3) fade hacia menú
                        app_state = STATE_MENU
                    else:
                        running = False

                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if app_state == STATE_MENU:
                        scene_mgr.goto_playing() # (#3) fade hacia juego
                        start_game()

                if event.key == pygame.K_r:
                    if app_state in (STATE_PLAYING, STATE_OVER):
                        scene_mgr.goto_playing() # (#3) fade al reiniciar
                        start_game()

        # ── UPDATE ────────────────────────────────────────────────────
        scene_mgr.update(dt_ms)          # (#3) avanzar fade de transición

        if app_state == STATE_PLAYING:
            screen_mgr.update(dt_ms)     # (#10) avanzar animación de pantalla final

            # (#6) Evaluar victoria / derrota
            fin = check_victoria_derrota(stats)

            if fin is None:
                # Partida en curso
                elapsed_ms += dt_ms
                keys = pygame.key.get_pressed()
                player.update(keys)
                obj_mgr.update(float(dt_ms), player.get_rect(), stats)
                event_mgr.update(float(dt_ms), stats)   # (#5) eventos aleatorios
            else:
                # Fin de partida detectado
                screen_mgr.activar(fin, stats, elapsed_ms)  # (#10) activar pantalla final
                scene_mgr.goto_over()                        # (#3) fade a STATE_OVER
                app_state = STATE_OVER

        if app_state == STATE_OVER:
            screen_mgr.update(dt_ms)     # (#10) seguir animando pantalla final

        # ── RENDER ────────────────────────────────────────────────────

        # ── Menú ──────────────────────────────────────────────────────
        if app_state == STATE_MENU:
            # (#7) MenuRenderer con animaciones y botones interactivos
            accion = menu_rend.draw(
                screen, font_title, font_small, font_hud, eventos
            )
            if accion == "play":
                scene_mgr.goto_playing()
                start_game()
            elif accion == "quit":
                running = False

        # ── Juego activo ───────────────────────────────────────────────
        elif app_state == STATE_PLAYING:
            # Fondo del campus
            draw_background(screen, bg_campus, C_BG_CAMPUS)

            # Título de escenario
            t        = font_title.render("Campus — Ciclo I", True, C_ACCENT)
            t_shadow = font_title.render("Campus — Ciclo I", True, (0, 0, 0))
            screen.blit(t_shadow, (SCREEN_W // 2 - t.get_width() // 2 + 2, 16))
            screen.blit(t,        (SCREEN_W // 2 - t.get_width() // 2,     14))

            # Objetos y jugador
            obj_mgr.draw(screen, font_sym)
            player.draw(screen)

            # HUD de estadísticas (el de stats.py, sin cambios)
            stats.draw_hud(screen, font_hud, x=10, y=50)

            # Leyenda y controles
            draw_leyenda(screen, font_hud)
            draw_controls(screen, font_hud)

            # (#9) HUD enriquecido: barra de semestre, semáforo de peligro,
            #      banner de evento activo, FPS y conteo de objetos
            draw_hud_enriched(
                surface       = screen,
                font_hud      = font_hud,
                font_sym      = font_sym,
                clock         = clock,
                obj_mgr       = obj_mgr,
                stats         = stats,
                screen_w      = SCREEN_W,
                screen_h      = SCREEN_H,
                elapsed_ms    = elapsed_ms,
                duracion_ms   = DURACION_SEMESTRE,
                evento_activo = event_mgr.evento_activo if event_mgr else None,
            )

        # ── Pantalla final ─────────────────────────────────────────────
        elif app_state == STATE_OVER:
            # Fondo del campus como base (pantalla final se dibuja encima)
            draw_background(screen, bg_campus, C_BG_CAMPUS)

            # (#10) Pantalla final animada (victoria o derrota_*)
            screen_mgr.draw(screen, font_big, font_small, font_hud, clock)

        # ── Capa de transición (fade, siempre al final) ────────────────
        scene_mgr.draw_transition(screen)   # (#3) overlay negro de fade

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
