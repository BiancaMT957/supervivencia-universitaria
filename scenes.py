"""
scenes.py
"Supervivencia Universitaria: La Vida Da Vueltas"

Funcionalidad #7 – Menú principal (pantalla inicial con opciones).
Funcionalidad  #3 – Cambio de escenarios (transiciones entre estados).

Expone:
    · SceneManager
          Centraliza el estado de la aplicación (MENU → PLAYING → OVER)
          y ejecuta las transiciones visuales (fade-in / fade-out).

          Uso en main.py:
            scene_mgr = SceneManager(screen_w, screen_h)
            scene_mgr.goto_menu()

            # update (cada frame):
            scene_mgr.update(dt_ms)

            # draw (cada frame):
            scene_mgr.draw_transition(surface)   # capa encima de todo

            # consultar estado actual:
            if scene_mgr.state == SceneManager.PLAYING: ...

            # disparar transiciones:
            scene_mgr.goto_playing()
            scene_mgr.goto_over()
            scene_mgr.goto_menu()

    · MenuRenderer
          Dibuja el menú principal enriquecido (fondo, título animado,
          botones con hover, créditos).

          Uso en main.py:
            menu_renderer = MenuRenderer(screen_w, screen_h, bg_menu)
            # en STATE_MENU:
            action = menu_renderer.draw(surface, font_title, font_med, font_small, events)
            if action == "play":  scene_mgr.goto_playing()
            if action == "quit":  running = False
"""

import math
import pygame

# ─────────────────────────────────────────────
#  PALETA
# ─────────────────────────────────────────────
C_TEXT    = (255, 255, 255)
C_ACCENT  = (255, 200,  50)
C_DIM     = (160, 160, 180)
C_BTN_BG  = ( 30,  30,  60, 220)
C_BTN_HOV = ( 60,  60, 120, 230)
C_BTN_BD  = ( 90,  90, 160)
C_BTN_HOV_BD = (180, 140, 255)
C_TITLE1  = (255, 210,  60)
C_TITLE2  = (200, 220, 255)


# ─────────────────────────────────────────────
#  CLASE: SceneManager  (transiciones)
# ─────────────────────────────────────────────

class SceneManager:
    """
    Máquina de estados simple con fade-in/fade-out entre escenas.

    Estados:
        MENU    → pantalla de inicio
        PLAYING → juego activo
        OVER    → pantalla final
    """

    MENU    = "menu"
    PLAYING = "playing"
    OVER    = "over"

    _FADE_MS = 350.0   # duración del fade en ms

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.state     = self.MENU

        # Fade
        self._fade_surface  = pygame.Surface((screen_w, screen_h))
        self._fade_surface.fill((0, 0, 0))
        self._fading_out    = False   # True = oscurecer antes de cambiar
        self._fading_in     = False   # True = aclarar al llegar
        self._fade_progress = 0.0    # 0.0 = transparente, 1.0 = negro
        self._pending_state : str | None = None  # estado destino

    # ── Transiciones públicas ─────────────────────────────────────────

    def goto_menu(self)    -> None: self._start_transition(self.MENU)
    def goto_playing(self) -> None: self._start_transition(self.PLAYING)
    def goto_over(self)    -> None: self._start_transition(self.OVER)

    def _start_transition(self, target: str) -> None:
        if self._fading_out or self._fading_in:
            return   # ya hay una transición en curso
        self._pending_state = target
        self._fading_out    = True
        self._fade_progress = 0.0

    # ── Update ────────────────────────────────────────────────────────

    def update(self, dt_ms: float) -> None:
        speed = dt_ms / self._FADE_MS

        if self._fading_out:
            self._fade_progress += speed
            if self._fade_progress >= 1.0:
                self._fade_progress = 1.0
                self._fading_out    = False
                # Cambiar estado en el punto más oscuro
                if self._pending_state:
                    self.state          = self._pending_state
                    self._pending_state = None
                self._fading_in     = True

        elif self._fading_in:
            self._fade_progress -= speed
            if self._fade_progress <= 0.0:
                self._fade_progress = 0.0
                self._fading_in     = False

    # ── Draw (capa encima de todo) ────────────────────────────────────

    def draw_transition(self, surface: pygame.Surface) -> None:
        """Dibuja el overlay negro de fade. Llamar ÚLTIMO en cada frame."""
        if self._fade_progress <= 0.0:
            return
        alpha = int(self._fade_progress * 255)
        self._fade_surface.set_alpha(alpha)
        surface.blit(self._fade_surface, (0, 0))

    # ── Consultas ─────────────────────────────────────────────────────

    @property
    def transitioning(self) -> bool:
        return self._fading_out or self._fading_in

    def __repr__(self) -> str:
        return (f"SceneManager(state='{self.state}', "
                f"fade={self._fade_progress:.2f}, "
                f"pending='{self._pending_state}')")


# ─────────────────────────────────────────────
#  CLASE: MenuRenderer  (menú principal)
# ─────────────────────────────────────────────

class MenuRenderer:
    """
    Dibuja el menú principal enriquecido.

    draw() devuelve:
        "play"  → el usuario quiere iniciar
        "quit"  → el usuario quiere salir
        None    → sin acción
    """

    _BTN_W  = 260
    _BTN_H  = 50
    _BTN_R  = 10   # radio borde

    def __init__(self,
                 screen_w : int,
                 screen_h : int,
                 bg_menu  : "pygame.Surface | None" = None) -> None:
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.bg_menu   = bg_menu
        self._t        = 0.0   # tiempo acumulado para animaciones

        # Definición de botones: (etiqueta, acción, y_offset_desde_centro)
        self._botones = [
            ("▶  INICIAR JUEGO",  "play",  -30),
            ("✕  SALIR",          "quit",  +40),
        ]

    # ── Update interno ────────────────────────────────────────────────

    def update(self, dt_ms: float) -> None:
        self._t += dt_ms

    # ── Draw ──────────────────────────────────────────────────────────

    def draw(self,
             surface    : pygame.Surface,
             font_title : pygame.font.Font,
             font_med   : pygame.font.Font,
             font_small : pygame.font.Font,
             events     : "list[pygame.event.Event]") -> "str | None":
        """
        Renderiza el menú y procesa los eventos de ratón/teclado.
        Devuelve la acción del botón pulsado o None.
        """
        cx = self.screen_w // 2
        cy = self.screen_h // 2

        # ── Fondo ──────────────────────────────────────────────────────
        if self.bg_menu:
            surface.blit(self.bg_menu, (0, 0))
        else:
            surface.fill((15, 15, 35))
            # cuadrícula de puntos
            for x in range(0, self.screen_w, 40):
                for y in range(0, self.screen_h, 40):
                    pygame.draw.circle(surface, (35, 35, 60), (x, y), 1)

        # Overlay semitransparente para legibilidad
        ov = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        ov.fill((0, 0, 20, 140))
        surface.blit(ov, (0, 0))

        # ── Título animado ─────────────────────────────────────────────
        dy_title = int(math.sin(self._t * 0.0018) * 5)

        title1 = font_title.render("SUPERVIVENCIA UNIVERSITARIA", True, C_TITLE1)
        title2 = font_title.render("La Vida Da Vueltas",          True, C_TITLE2)
        surface.blit(title1, (cx - title1.get_width() // 2, 140 + dy_title))
        surface.blit(title2, (cx - title2.get_width() // 2, 182 + dy_title))

        # Línea separadora
        pygame.draw.line(surface, C_ACCENT,
                         (cx - 180, 225 + dy_title),
                         (cx + 180, 225 + dy_title), 1)

        # ── Botones ────────────────────────────────────────────────────
        mouse_pos    = pygame.mouse.get_pos()
        mouse_click  = any(
            e.type == pygame.MOUSEBUTTONDOWN and e.button == 1
            for e in events
        )
        key_start = any(
            e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN)
            for e in events
        )
        key_quit  = any(
            e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
            for e in events
        )

        accion = None

        for etiqueta, action, y_off in self._botones:
            bx  = cx - self._BTN_W // 2
            by  = cy + y_off
            btn = pygame.Rect(bx, by, self._BTN_W, self._BTN_H)
            hov = btn.collidepoint(mouse_pos)

            # Fondo del botón
            btn_surf = pygame.Surface((self._BTN_W, self._BTN_H), pygame.SRCALPHA)
            bg_col   = C_BTN_HOV if hov else C_BTN_BG
            bd_col   = C_BTN_HOV_BD if hov else C_BTN_BD
            pygame.draw.rect(btn_surf, bg_col, (0, 0, self._BTN_W, self._BTN_H),
                             border_radius=self._BTN_R)
            pygame.draw.rect(btn_surf, bd_col, (0, 0, self._BTN_W, self._BTN_H),
                             2, border_radius=self._BTN_R)
            surface.blit(btn_surf, (bx, by))

            # Texto del botón
            col_txt  = C_ACCENT if hov else C_TEXT
            txt_surf = font_med.render(etiqueta, True, col_txt)
            surface.blit(txt_surf,
                         (cx - txt_surf.get_width() // 2,
                          by + (self._BTN_H - txt_surf.get_height()) // 2))

            # Detectar clic
            if (mouse_click and hov) or (key_start and action == "play") \
                    or (key_quit and action == "quit"):
                accion = action

        # ── Controles ──────────────────────────────────────────────────
        hint = font_small.render(
            "Flechas/WASD: mover   R: reiniciar   ESC: menú", True, C_DIM
        )
        surface.blit(hint, (cx - hint.get_width() // 2, self.screen_h - 36))

        # ── Versión ────────────────────────────────────────────────────
        ver = font_small.render("v0.2 – Supervivencia Universitaria", True, C_DIM)
        surface.blit(ver, (cx - ver.get_width() // 2, self.screen_h - 18))

        return accion
