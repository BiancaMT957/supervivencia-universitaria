
import math
import pygame

# colores basicos
C_TEXT    = (255, 255, 255)
C_ACCENT  = (255, 200,  50)
C_DIM     = (160, 160, 180)
C_BTN_BG  = ( 30,  30,  60, 220)
C_BTN_HOV = ( 60,  60, 120, 230)
C_BTN_BD  = ( 90,  90, 160)
C_BTN_HOV_BD = (180, 140, 255)
C_TITLE1  = (255, 210,  60)
C_TITLE2  = (200, 220, 255)

class SceneManager:
    MENU    = "menu"
    PLAYING = "playing"
    OVER    = "over"
    _FADE_MS = 350.0

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.state     = self.MENU

        self._fade_surface  = pygame.Surface((screen_w, screen_h))
        self._fade_surface.fill((0, 0, 0))
        self._fading_out    = False
        self._fading_in     = False
        self._fade_progress = 0.0
        self._pending_state : str | None = None

    def goto_menu(self)    -> None: self._start_transition(self.MENU)
    def goto_playing(self) -> None: self._start_transition(self.PLAYING)
    def goto_over(self)    -> None: self._start_transition(self.OVER)

    def _start_transition(self, target: str) -> None:
        if self._fading_out or self._fading_in:
            return
        self._pending_state = target
        self._fading_out    = True
        self._fade_progress = 0.0

    def update(self, dt_ms: float) -> None:
        speed = dt_ms / self._FADE_MS

        if self._fading_out:
            self._fade_progress += speed
            if self._fade_progress >= 1.0:
                self._fade_progress = 1.0
                self._fading_out    = False
                if self._pending_state:
                    self.state          = self._pending_state
                    self._pending_state = None
                self._fading_in     = True

        elif self._fading_in:
            self._fade_progress -= speed
            if self._fade_progress <= 0.0:
                self._fade_progress = 0.0
                self._fading_in     = False

    def draw_transition(self, surface: pygame.Surface) -> None:
        if self._fade_progress <= 0.0:
            return
        alpha = int(self._fade_progress * 255)
        self._fade_surface.set_alpha(alpha)
        surface.blit(self._fade_surface, (0, 0))

    @property
    def transitioning(self) -> bool:
        return self._fading_out or self._fading_in

    def __repr__(self) -> str:
        return (f"SceneManager(state='{self.state}', "
                f"fade={self._fade_progress:.2f}, "
                f"pending='{self._pending_state}')")


class MenuRenderer:
    _BTN_W  = 260
    _BTN_H  = 50
    _BTN_R  = 10

    def __init__(self,
                 screen_w : int,
                 screen_h : int,
                 bg_menu  : "pygame.Surface | None" = None) -> None:
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.bg_menu   = bg_menu
        self._t        = 0.0

        self._botones = [
            ("▶  INICIAR JUEGO",  "play",  -30),
            ("✕  SALIR",          "quit",  +40),
        ]

    def update(self, dt_ms: float) -> None:
        self._t += dt_ms

    def draw(self,
             surface    : pygame.Surface,
             font_title : pygame.font.Font,
             font_med   : pygame.font.Font,
             font_small : pygame.font.Font,
             events     : "list[pygame.event.Event]") -> "str | None":
        cx = self.screen_w // 2
        cy = self.screen_h // 2

        if self.bg_menu:
            surface.blit(self.bg_menu, (0, 0))
        else:
            surface.fill((15, 15, 35))
            for x in range(0, self.screen_w, 40):
                for y in range(0, self.screen_h, 40):
                    pygame.draw.circle(surface, (35, 35, 60), (x, y), 1)

        ov = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        ov.fill((0, 0, 20, 140))
        surface.blit(ov, (0, 0))

        dy_title = int(math.sin(self._t * 0.0018) * 5)

        title1 = font_title.render("SUPERVIVENCIA UNIVERSITARIA", True, C_TITLE1)
        title2 = font_title.render("La Vida Da Vueltas",          True, C_TITLE2)
        surface.blit(title1, (cx - title1.get_width() // 2, 140 + dy_title))
        surface.blit(title2, (cx - title2.get_width() // 2, 182 + dy_title))

        pygame.draw.line(surface, C_ACCENT,
                         (cx - 180, 225 + dy_title),
                         (cx + 180, 225 + dy_title), 1)

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

            btn_surf = pygame.Surface((self._BTN_W, self._BTN_H), pygame.SRCALPHA)
            bg_col   = C_BTN_HOV if hov else C_BTN_BG
            bd_col   = C_BTN_HOV_BD if hov else C_BTN_BD
            pygame.draw.rect(btn_surf, bg_col, (0, 0, self._BTN_W, self._BTN_H),
                             border_radius=self._BTN_R)
            pygame.draw.rect(btn_surf, bd_col, (0, 0, self._BTN_W, self._BTN_H),
                             2, border_radius=self._BTN_R)
            surface.blit(btn_surf, (bx, by))

            col_txt  = C_ACCENT if hov else C_TEXT
            txt_surf = font_med.render(etiqueta, True, col_txt)
            surface.blit(txt_surf,
                         (cx - txt_surf.get_width() // 2,
                          by + (self._BTN_H - txt_surf.get_height()) // 2))

            if (mouse_click and hov) or (key_start and action == "play") \
                    or (key_quit and action == "quit"):
                accion = action

        hint = font_small.render(
            "Flechas/WASD: mover   R: reiniciar   ESC: menú", True, C_DIM
        )
        surface.blit(hint, (cx - hint.get_width() // 2, self.screen_h - 36))

        ver = font_small.render("v0.2 - Supervivencia Universitaria", True, C_DIM)
        surface.blit(ver, (cx - ver.get_width() // 2, self.screen_h - 18))

        return accion


