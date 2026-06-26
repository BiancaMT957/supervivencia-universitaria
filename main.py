
import sys
import math

"""
main.py
"Supervivencia Universitaria: La Vida Da Vueltas"

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
from ui      import draw_hud_enriched
from events  import EventManager
from scenes  import SceneManager, MenuRenderer
from screens import ScreenManager, check_victoria_derrota

# config general



#  CONFIGURACIÓN



SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Supervivencia Universitaria: La Vida Da Vueltas"


# assets
BG_MENU    = "assets/menu.png"
BG_CAMPUS  = "assets/campus.png"
BG_FINALS  = "assets/finals_bg.png"
PLAYER_IMG = "assets/player.png"

# colores base

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


# estados
STATE_MENU              = "menu"
STATE_PLAYING           = "playing"
STATE_TRANSICION_EXAMEN = "transicion_examen"
STATE_EXAMEN_FINAL      = "examen_final"
STATE_OVER              = "over"

# tiempos
DURACION_SEMESTRE  = 120_000.0
TRIGGER_EXAMEN_PCT = 0.05
CARTEL_DURACION_MS = 3_500.0

def calcular_veredicto_final(stats: Stats) -> tuple[bool, float]:
    nota_examen: float = (stats.conocimiento / 100.0) * 20.0

    if stats.energia < 30.0:
        nota_examen *= 0.75

    promedio: float = round((stats.notas * 0.40) + (nota_examen * 0.60), 3)
    promedio = max(0.0, min(20.0, promedio))

    return promedio >= 10.5, promedio

def load_bg(path: str) -> pygame.Surface | None:
  
# Estados de la aplicación
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_OVER    = "over"



#  CARGA DE IMÁGENES CON FALLBACK


def load_bg(path: str) -> pygame.Surface | None:
    """Carga un fondo y lo escala a la pantalla. Devuelve None si falla."""

    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
    except (pygame.error, FileNotFoundError):

        print(f"[assets] Fondo no encontrado: '{path}' - usando fallback.")
        return None


        print(f"[assets] Fondo no encontrado: '{path}' — usando color sólido.")
        return None



#  FUNCIONES DE RENDER



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

    if not bg_image:
        pygame.draw.rect(surface, C_BORDE, (0, 0, SCREEN_W, SCREEN_H), 3)

def draw_leyenda(surface: pygame.Surface, font: pygame.font.Font) -> None:
    items = [
        ("TAR", "Tarea       +2 Notas -10 Eng",      ( 70, 140, 230)),
        ("APT", "Apuntes     +15 Conoc -15 Eng",     ( 50, 150, 255)),
        ("CFE", "Cafe       +25 Eng   -S/30",        (160,  90,  40)),
        ("BCA", "Beca        +1 Nota  +S/200",       (220, 180,  30)),
        ("VJ",  "Videojuegos -3 Notas -15 Eng -S/30", (130,  50, 210)),
        ("RS",  "Distraccion -2 Notas  -5 Eng -S/20", (220,  60, 130)),
        ("BLT", "Laptop Rota -2 Notas -S/50",         (180,  60,  60)),
        ("ENF", "Enfermedad  -2 Notas -20 Eng",       ( 80, 170,  80)),


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


def draw_controls(surface: pygame.Surface, font: pygame.font.Font) -> None:
    lines = ["Mover: Flechas / WASD", "R: Reiniciar  ESC: Menu"]


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


def draw_panel(surface: pygame.Surface,
               x: int, y: int, w: int, h: int,
               bg=(20, 15, 45, 210), border=(100, 80, 200),
               radius: int = 12) -> None:
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(p, bg,     (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(p, border, (0, 0, w, h), 2, border_radius=radius)
    surface.blit(p, (x, y))

def draw_transicion_examen(
    surface     : pygame.Surface,
    font_big    : pygame.font.Font,
    font_small  : pygame.font.Font,
    t_ms        : float,
    duracion_ms : float,
) -> None:
    FADE_IN_MS  = 600.0
    TEXTO_IN_MS = 400.0

    alpha_negro = int(min(1.0, t_ms / FADE_IN_MS) * 255)
    negro = pygame.Surface((SCREEN_W, SCREEN_H))
    negro.fill((0, 0, 0))
    negro.set_alpha(alpha_negro)
    surface.blit(negro, (0, 0))

    if t_ms < FADE_IN_MS:
        return

    t_texto   = t_ms - FADE_IN_MS
    alpha_txt = int(min(1.0, t_texto / TEXTO_IN_MS) * 255)
    cx, cy    = SCREEN_W // 2, SCREEN_H // 2

    draw_panel(surface, cx - 310, cy - 80, 620, 160,
               bg=(10, 5, 30, 220), border=(160, 80, 255))

    pulse   = 1.0 + 0.03 * math.sin(t_ms * 0.004)
    titulo  = font_big.render("SEMANA DE EXAMENES FINALES", True, (255, 200, 50))
    w_t = int(titulo.get_width() * pulse)
    h_t = int(titulo.get_height() * pulse)
    titulo_s = pygame.transform.scale(titulo, (w_t, h_t))
    titulo_s.set_alpha(alpha_txt)
    surface.blit(titulo_s, (cx - w_t // 2, cy - 55))

    sub = font_small.render("Preparate... todo lo que aprendiste sera evaluado.", True, (200, 200, 220))
    sub.set_alpha(alpha_txt)
    surface.blit(sub, (cx - sub.get_width() // 2, cy + 18))

    hint = font_small.render("Presiona ESPACIO o ENTER para continuar", True, (130, 110, 180))
    hint.set_alpha(int(alpha_txt * 0.75))
    surface.blit(hint, (cx - hint.get_width() // 2, cy + 52))

def draw_examen_final(
    surface    : pygame.Surface,
    bg_finals  : pygame.Surface | None,
    player     : Player,
    font_big   : pygame.font.Font,
    font_title : pygame.font.Font,
    font_small : pygame.font.Font,
    aprobado   : bool,
    promedio   : float,
    stats      : Stats,
    t_ms       : float,
    fase       : int,
) -> None:
    
    if bg_finals:
        surface.blit(bg_finals, (0, 0))
    else:
        surface.fill((10, 8, 25))
        for gx in range(0, SCREEN_W, 60):
            pygame.draw.line(surface, (20, 18, 45), (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(surface, (20, 18, 45), (0, gy), (SCREEN_W, gy))

    if fase == 0:
        txt = font_small.render("Respiras hondo... ¿Estás listo?", True, (255, 255, 255))
        surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 100))

    elif fase == 2:
        txt = font_small.render("Presiona [F] para repasar (+3 Conoc / -10 Eng)", True, (100, 255, 100))
        surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 100))

    elif fase == 3:
        progreso = min(1.0, t_ms / 4000.0)
        pygame.draw.rect(surface, (50, 50, 80), (SCREEN_W//2 - 120, 100, 240, 15), border_radius=5)
        pygame.draw.rect(surface, (100, 200, 100), (SCREEN_W//2 - 120, 100, int(240 * progreso), 15), border_radius=5)
        txt = font_small.render("Rindiendo examen...", True, (255, 255, 255))
        surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 70))

    elif fase == 4:
        txt = font_small.render("Entregando examen... Esperando resultados...", True, (255, 255, 255))
        surface.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 100))

    elif fase == 5:
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 130))
        surface.blit(ov, (0, 0))
        
        RESULTADO_IN_MS = 800.0
        alpha = int(min(1.0, t_ms / RESULTADO_IN_MS) * 255)
        
        cx, cy       = SCREEN_W // 2, SCREEN_H // 2
        color_borde  = (50, 220, 90) if aprobado else (210, 40, 40)

        draw_panel(surface, cx - 240, cy - 140, 480, 295, bg=(10, 8, 25, 225), border=color_borde)

        def blit_a(surf: pygame.Surface, pos: tuple) -> None:
            surf.set_alpha(alpha)
            surface.blit(surf, pos)

        color_titulo = (50, 220, 90) if aprobado else (210, 40, 40)
        emoji        = "APROBASTE!" if aprobado else "JALADO"
        titulo       = font_big.render(emoji, True, color_titulo)
        blit_a(titulo, (cx - titulo.get_width() // 2, cy - 132))
        
        pygame.draw.line(surface, (*color_borde, alpha), (cx - 200, cy - 84), (cx + 200, cy - 84), 1)

        nota_bruta  = (stats.conocimiento / 100.0) * 20.0
        penalizado  = stats.energia < 30.0
        nota_examen = nota_bruta * (0.75 if penalizado else 1.0)
        
        filas = [
            ("Notas acumuladas (40%)", f"{stats.notas:.1f}/20", (180, 180, 255)),
            ("Nota del examen  (60%)", f"{nota_examen:.1f}/20", (255, 160, 60)),
            ("PROMEDIO FINAL", f"{promedio:.2f} / 20", (255, 240, 100)),
        ]
        
        row_y = cy - 68
        for label, valor, col in filas:
            lbl_s = font_small.render(label + ":", True, (180, 180, 200))
            val_s = font_small.render(valor, True, col)
            blit_a(lbl_s, (cx - 220, row_y))
            blit_a(val_s, (cx + 220 - val_s.get_width(), row_y))
            row_y += 30

        if t_ms > 1_200:
            inst = font_small.render("R = reiniciar   |   ESC = salir", True, (255, 200, 50))
            surface.blit(inst, (cx - inst.get_width() // 2, cy + 130))

    if fase != 5:
        player.draw(surface)


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



#  FÁBRICAS



def make_player() -> Player:
    return Player(
        x             = SCREEN_W  // 2 - 20,
        y             = SCREEN_H  // 2 - 30,
        screen_width  = SCREEN_W,
        screen_height = SCREEN_H,
        speed         = 4,

        image_path    = PLAYER_IMG,
    )


        image_path    = PLAYER_IMG,   # ← usa el sprite del jugador
    )



#  MAIN



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


    bg_menu   = load_bg(BG_MENU)
    bg_campus = load_bg(BG_CAMPUS)
    bg_finals = load_bg(BG_FINALS)

    scene_mgr  = SceneManager(SCREEN_W, SCREEN_H)
    menu_rend  = MenuRenderer(SCREEN_W, SCREEN_H, bg_menu)
    screen_mgr = ScreenManager(SCREEN_W, SCREEN_H, bg_finals)

    app_state  = STATE_MENU
    player     = None
    stats      = None
    obj_mgr    = None
    event_mgr  = None
    elapsed_ms = 0.0

    transicion_t_ms  = 0.0
    examen_t_ms      = 0.0
    examen_fase      = 0
    examen_aprobado  = False
    examen_promedio  = 0.0

    def start_game() -> None:
        nonlocal player, stats, obj_mgr, app_state, event_mgr, elapsed_ms
        nonlocal transicion_t_ms, examen_t_ms, examen_fase, examen_aprobado, examen_promedio
        player           = make_player()
        stats            = Stats()
        obj_mgr          = ObjectManager(SCREEN_W, SCREEN_H)
        event_mgr        = EventManager()
        elapsed_ms       = 0.0
        transicion_t_ms  = 0.0
        examen_t_ms      = 0.0
        examen_fase      = 0
        examen_aprobado  = False
        examen_promedio  = 0.0
        screen_mgr.reset()
        app_state = STATE_PLAYING

    def start_transicion_examen() -> None:
        nonlocal app_state, transicion_t_ms
        transicion_t_ms = 0.0
        app_state       = STATE_TRANSICION_EXAMEN

    def start_examen_final() -> None:
        nonlocal app_state, examen_t_ms, examen_fase
        examen_t_ms = 0.0
        examen_fase = 0
        player.set_position(SCREEN_W // 2 - 160, SCREEN_H + 20)
        app_state = STATE_EXAMEN_FINAL

    running = True

    while running:
        dt_ms = clock.tick(FPS)
        menu_rend.update(dt_ms)
        eventos = pygame.event.get()

        for event in eventos:

    #  Cargar fondos
    bg_menu   = load_bg(BG_MENU)
    bg_campus = load_bg(BG_CAMPUS)
    # bg_finals = load_bg("assets/finals_bg.png")  ← Issue #3

    #  Estado de la app
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

    #  GAME LOOP
    running = True
    while running:
        dt_ms = clock.tick(FPS)

        # EVENTOS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:

                    if app_state in (STATE_PLAYING, STATE_TRANSICION_EXAMEN, STATE_EXAMEN_FINAL):
                        scene_mgr.goto_menu()
                        app_state = STATE_MENU
                    else:
                        running = False

                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if app_state == STATE_MENU:
                        scene_mgr.goto_playing()
                        start_game()
                    elif app_state == STATE_TRANSICION_EXAMEN:
                        if transicion_t_ms >= 600.0:
                            start_examen_final()

                if event.key == pygame.K_r:
                    if app_state in (STATE_PLAYING, STATE_OVER, STATE_EXAMEN_FINAL):
                        scene_mgr.goto_playing()
                        start_game()

        scene_mgr.update(dt_ms)

        if app_state == STATE_PLAYING:
            screen_mgr.update(dt_ms)

            fin = check_victoria_derrota(stats)
            if fin is not None:
                screen_mgr.activar(fin, stats, elapsed_ms)
                scene_mgr.goto_over()
                app_state = STATE_OVER
            else:
                elapsed_ms += dt_ms
                tiempo_restante = DURACION_SEMESTRE - elapsed_ms
                if tiempo_restante <= DURACION_SEMESTRE * TRIGGER_EXAMEN_PCT:
                    start_transicion_examen()
                else:
                    keys = pygame.key.get_pressed()
                    player.update(keys)
                    obj_mgr.update(float(dt_ms), player.get_rect(), stats)
                    event_mgr.update(float(dt_ms), stats)

        elif app_state == STATE_TRANSICION_EXAMEN:
            transicion_t_ms += dt_ms
            if transicion_t_ms >= CARTEL_DURACION_MS:
                start_examen_final()

        elif app_state == STATE_EXAMEN_FINAL:
            if examen_fase == 0:
                examen_t_ms += dt_ms
                if examen_t_ms >= 2000.0:
                    examen_fase = 1
                    examen_t_ms = 0.0
            
            elif examen_fase == 1:
                player.speed = 2 if stats.conocimiento < 50 else 4
                if player.move_towards(SCREEN_W // 2 - 160, SCREEN_H // 2 - 10):
                    examen_fase = 2
                    examen_t_ms = 0.0
                    
            elif examen_fase == 2:
                examen_t_ms += dt_ms
                keys = pygame.key.get_pressed()
                if keys[pygame.K_f] and stats.energia >= 10:
                    stats.modificar_conocimiento(3)
                    stats.modificar_energia(-10)
                    examen_fase = 3
                if examen_t_ms >= 3000.0:
                    examen_fase = 3
                    
            elif examen_fase == 3:
                examen_t_ms += dt_ms
                if examen_t_ms >= 4000.0:
                    examen_fase = 4
                    examen_t_ms = 0.0
                    
            elif examen_fase == 4:
                if player.move_towards(SCREEN_W // 2, SCREEN_H // 2 - 200):
                    examen_t_ms += dt_ms
                    if examen_t_ms >= 2000.0:
                        examen_aprobado, examen_promedio = calcular_veredicto_final(stats)
                        examen_fase = 5
            
            elif examen_fase == 5:
                examen_t_ms += dt_ms

        elif app_state == STATE_OVER:
            screen_mgr.update(dt_ms)

        if app_state == STATE_MENU:
            accion = menu_rend.draw(
                screen, font_title, font_small, font_hud, eventos
            )
            if accion == "play":
                scene_mgr.goto_playing()
                start_game()
            elif accion == "quit":
                running = False

        elif app_state == STATE_PLAYING:
            draw_background(screen, bg_campus, C_BG_CAMPUS)

            t        = font_title.render("Campus - Ciclo I", True, C_ACCENT)
            t_shadow = font_title.render("Campus - Ciclo I", True, (0, 0, 0))
            screen.blit(t_shadow, (SCREEN_W // 2 - t.get_width() // 2 + 2, 16))
            screen.blit(t,        (SCREEN_W // 2 - t.get_width() // 2,     14))

            obj_mgr.draw(screen, font_sym)
            player.draw(screen)

            stats.draw_hud(screen, font_hud, x=10, y=50)
            draw_leyenda(screen, font_hud)
            draw_controls(screen, font_hud)

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

            tiempo_restante = DURACION_SEMESTRE - elapsed_ms
            if tiempo_restante <= DURACION_SEMESTRE * 0.10:
                pulso  = 0.6 + 0.4 * abs(math.sin(elapsed_ms * 0.005))
                alerta = font_title.render("EXAMENES FINALES CERCA!", True, (255, 80, 50))
                alerta.set_alpha(int(pulso * 255))
                screen.blit(alerta,
                            (SCREEN_W // 2 - alerta.get_width() // 2, SCREEN_H - 48))

        elif app_state == STATE_TRANSICION_EXAMEN:
            draw_background(screen, bg_campus, C_BG_CAMPUS)
            if player and obj_mgr:
                obj_mgr.draw(screen, font_sym)
                player.draw(screen)
                stats.draw_hud(screen, font_hud, x=10, y=50)
            draw_transicion_examen(
                screen, font_big, font_small,
                transicion_t_ms, CARTEL_DURACION_MS
            )

        elif app_state == STATE_EXAMEN_FINAL:
            draw_examen_final(
                surface    = screen,
                bg_finals  = bg_finals,
                player     = player,
                font_big   = font_big,
                font_title = font_title,
                font_small = font_small,
                aprobado   = examen_aprobado,
                promedio   = examen_promedio,
                stats      = stats,
                t_ms       = examen_t_ms,
                fase       = examen_fase,
            )

        elif app_state == STATE_OVER:
            draw_background(screen, bg_campus, C_BG_CAMPUS)
            screen_mgr.draw(screen, font_big, font_small, font_hud, clock)

        scene_mgr.draw_transition(screen)

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

        # UPDATE
        if app_state == STATE_PLAYING:
            game_estado = stats.estado_juego()

            if game_estado == "jugando":
                keys = pygame.key.get_pressed()
                player.update(keys)
                obj_mgr.update(float(dt_ms), player.get_rect(), stats)
            else:
                app_state = STATE_OVER

        # RENDER
        if app_state == STATE_MENU:
            draw_menu(screen, bg_menu, font_title, font_small)

        elif app_state in (STATE_PLAYING, STATE_OVER):
            # Fondo del campus
            draw_background(screen, bg_campus, C_BG_CAMPUS)

            # Título de escenario para el escenario 1
            t = font_title.render("Campus — Ciclo I", True, C_ACCENT)
            # Sombra sutil para legibilidad sobre la imagen
            t_shadow = font_title.render("Campus — Ciclo I", True, (0, 0, 0))
            screen.blit(t_shadow, (SCREEN_W // 2 - t.get_width() // 2 + 2, 16))
            screen.blit(t,        (SCREEN_W // 2 - t.get_width() // 2,     14))

            # Objetos hasta jugador (orden: objetos debajo, jugador encima)
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


if __name__ == "__main__":
    main()

