import pygame
from typing import Tuple

# limites y variables iniciales
ENERGIA_INICIAL = 100
ENERGIA_MIN     =   0
ENERGIA_MAX     = 100

DINERO_INICIAL  = 500
DINERO_MIN      =   0
DINERO_MAX      = 1_000

NOTAS_INICIAL   =  10
NOTAS_MIN       =   0
NOTAS_MAX       =  20
NOTAS_APROBADO  =  11

ENERGIA_PELIGRO  = 25
ENERGIA_BAJO     = 50

DINERO_PELIGRO   = 150
DINERO_BAJO      = 350

NOTAS_PELIGRO    =  5
NOTAS_BAJO       = 10

CONOCIMIENTO_INICIAL = 0
CONOCIMIENTO_MIN     = 0
CONOCIMIENTO_MAX     = 100
CONOCIMIENTO_PELIGRO = 25
CONOCIMIENTO_BAJO    = 50

# colores de la ui para stats
C_FONDO_PANEL = (20,  20,  45, 200)
C_BORDE_PANEL = (90,  90, 130)
C_BARRA_BG    = (50,  50,  80)
C_NORMAL      = (60, 200,  80)
C_BAJO        = (230, 160,  30)
C_PELIGRO     = (210,  40,  40)
C_LABEL       = (220, 220, 255)
C_VALOR       = (255, 240, 180)

# tamaos panel hud
HUD_PANEL_W = 210
HUD_PANEL_H = 158
HUD_PADDING = 10
HUD_BAR_H   =  14
HUD_BAR_W   = 190
HUD_ROW_GAP =  36

class Stats:
    def __init__(self) -> None:
        self._energia: float = float(ENERGIA_INICIAL)
        self._dinero:  float = float(DINERO_INICIAL)
        self._notas:   float = float(NOTAS_INICIAL)
        self._conocimiento: float = float(CONOCIMIENTO_INICIAL)

    @property
    def energia(self) -> float:
        return self._energia

    @property
    def dinero(self) -> float:
        return self._dinero

    @property
    def notas(self) -> float:
        return self._notas

    @property
    def conocimiento(self) -> float:
        return self._conocimiento

    def modificar_energia(self, delta: float) -> None:
        self._energia = self._clamp(self._energia + delta, ENERGIA_MIN, ENERGIA_MAX)

    def modificar_dinero(self, delta: float) -> None:
        self._dinero = self._clamp(self._dinero + delta, DINERO_MIN, DINERO_MAX)

    def modificar_notas(self, delta: float) -> None:
        self._notas = self._clamp(self._notas + delta, NOTAS_MIN, NOTAS_MAX)

    def modificar_conocimiento(self, delta: float) -> None:
        self._conocimiento = self._clamp(
            self._conocimiento + delta, CONOCIMIENTO_MIN, CONOCIMIENTO_MAX
        )

    def reset(self) -> None:
        self._energia      = float(ENERGIA_INICIAL)
        self._dinero       = float(DINERO_INICIAL)
        self._notas        = float(NOTAS_INICIAL)
        self._conocimiento = float(CONOCIMIENTO_INICIAL)

    def estado_juego(self) -> str:
        if self._notas >= NOTAS_MAX:
            return "victoria"
        if self._energia <= ENERGIA_MIN:
            return "derrota_energia"
        if self._dinero <= DINERO_MIN:
            return "derrota_dinero"
        if self._notas <= NOTAS_MIN:
            return "derrota_notas"
        return "jugando"

    def esta_en_peligro(self) -> bool:
        return (
            self._energia      <= ENERGIA_PELIGRO
            or self._dinero    <= DINERO_PELIGRO
            or self._notas     <= NOTAS_PELIGRO
            or self._conocimiento <= CONOCIMIENTO_PELIGRO
        )

    def esta_aprobando(self) -> bool:
        return self._notas >= NOTAS_APROBADO

    def porcentaje_energia(self) -> float:
        return self._energia / ENERGIA_MAX

    def porcentaje_dinero(self) -> float:
        return self._dinero / DINERO_MAX

    def porcentaje_notas(self) -> float:
        return self._notas / NOTAS_MAX

    def porcentaje_conocimiento(self) -> float:
        return self._conocimiento / CONOCIMIENTO_MAX

    def draw_hud(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        x: int = 10,
        y: int = 10,
    ) -> None:
        panel = pygame.Surface((HUD_PANEL_W, HUD_PANEL_H), pygame.SRCALPHA)
        panel.fill(C_FONDO_PANEL)
        pygame.draw.rect(panel, C_BORDE_PANEL, (0, 0, HUD_PANEL_W, HUD_PANEL_H), 1)
        surface.blit(panel, (x, y))

        filas = [
            {
                "icono"         : "ENERGIA",
                "valor"         : f"{int(self._energia):3d}/{ENERGIA_MAX}",
                "pct"           : self.porcentaje_energia(),
                "umbral_peligro": ENERGIA_PELIGRO / ENERGIA_MAX,
                "umbral_bajo"   : ENERGIA_BAJO    / ENERGIA_MAX,
            },
            {
                "icono"         : "DINERO",
                "valor"         : f"S/{int(self._dinero):4d}",
                "pct"           : self.porcentaje_dinero(),
                "umbral_peligro": DINERO_PELIGRO  / DINERO_MAX,
                "umbral_bajo"   : DINERO_BAJO     / DINERO_MAX,
            },
            {
                "icono"         : "NOTAS",
                "valor"         : f"{self._notas:4.1f}/{NOTAS_MAX}",
                "pct"           : self.porcentaje_notas(),
                "umbral_peligro": NOTAS_PELIGRO   / NOTAS_MAX,
                "umbral_bajo"   : NOTAS_BAJO      / NOTAS_MAX,
            },
            {
                "icono"         : "CONOCIM.",
                "valor"         : f"{int(self._conocimiento):3d}/{CONOCIMIENTO_MAX}",
                "pct"           : self.porcentaje_conocimiento(),
                "umbral_peligro": CONOCIMIENTO_PELIGRO / CONOCIMIENTO_MAX,
                "umbral_bajo"   : CONOCIMIENTO_BAJO    / CONOCIMIENTO_MAX,
            },
        ]

        row_y = y + HUD_PADDING
        for fila in filas:
            self._draw_stat_row(
                surface        = surface,
                font           = font,
                x              = x + HUD_PADDING,
                y              = row_y,
                icono          = fila["icono"],
                valor          = fila["valor"],
                pct            = fila["pct"],
                umbral_peligro = fila["umbral_peligro"],
                umbral_bajo    = fila["umbral_bajo"],
            )
            row_y += HUD_ROW_GAP

    def _draw_stat_row(
        self,
        surface        : pygame.Surface,
        font           : pygame.font.Font,
        x              : int,
        y              : int,
        icono          : str,
        valor          : str,
        pct            : float,
        umbral_peligro : float,
        umbral_bajo    : float,
    ) -> None:
        label_surf = font.render(icono, True, C_LABEL)
        surface.blit(label_surf, (x, y))

        val_surf = font.render(valor, True, C_VALOR)
        val_x    = x + HUD_BAR_W - val_surf.get_width()
        surface.blit(val_surf, (val_x, y))

        bar_y = y + label_surf.get_height() + 3

        pygame.draw.rect(
            surface, C_BARRA_BG,
            (x, bar_y, HUD_BAR_W, HUD_BAR_H),
            border_radius=4
        )

        fill_w = max(0, int(HUD_BAR_W * pct))
        if fill_w > 0:
            color = self._color_barra(pct, umbral_peligro, umbral_bajo)
            pygame.draw.rect(
                surface, color,
                (x, bar_y, fill_w, HUD_BAR_H),
                border_radius=4
            )

        pygame.draw.rect(
            surface, C_BORDE_PANEL,
            (x, bar_y, HUD_BAR_W, HUD_BAR_H),
            1, border_radius=4
        )

    @staticmethod
    def _color_barra(
        pct: float,
        umbral_peligro: float,
        umbral_bajo: float,
    ) -> Tuple[int, int, int]:
        if pct <= umbral_peligro:
            return C_PELIGRO
        if pct <= umbral_bajo:
            return C_BAJO
        return C_NORMAL

    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(max_val, value))

    def __repr__(self) -> str:
        return (
            f"Stats("
            f"energia={self._energia:.0f}/{ENERGIA_MAX}, "
            f"dinero={self._dinero:.0f}/{DINERO_MAX}, "
            f"notas={self._notas:.1f}/{NOTAS_MAX}, "
            f"conocimiento={self._conocimiento:.0f}/{CONOCIMIENTO_MAX}, "
            f"estado='{self.estado_juego()}')"
        )