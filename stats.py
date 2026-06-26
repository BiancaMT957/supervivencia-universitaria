
import pygame
from typing import Tuple

# limites y variables iniciales

"""
stats.py

Clase Stats que gestiona los tres recursos del estudiante universitario:
    ❤  Energía – vitalidad del estudiante   (0 – 100)
    $  Dinero  – soles disponibles           (0 – 1 000)
    #  Notas   – sistema vigesimal peruano  (0 – 20)

Responsabilidades:
    · Guardar valores actuales con sus máximos y mínimos.
    · Exponer métodos para modificar cada estadística de forma segura.
    · Detectar condiciones de victoria y derrota.
    · Dibujar el HUD con barras visuales dentro de la ventana de PyGame.
"""

import pygame
from typing import Tuple



#  CONSTANTES GLOBALES DEL SISTEMA DE ESTADÍSTICAS


# Energía  (0 = colapso, 100 = descansado)

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

# Notas  (sistema vigesimal peruano: aprobado >= 11)
NOTAS_INICIAL   =  10
NOTAS_MIN       =   0
NOTAS_MAX       =  20
NOTAS_APROBADO  =  11       # umbral mínimo para "victoria"

#  Zonas de alerta (para cambiar color de la barra)
ENERGIA_PELIGRO  = 25     # <= 25  → rojo crítico
ENERGIA_BAJO     = 50     # <= 50  → naranja

DINERO_PELIGRO   = 150    # <= 150 → rojo crítico
DINERO_BAJO      = 350    # <= 350 → naranja

NOTAS_PELIGRO    =  5     # <=  5  → rojo crítico
NOTAS_BAJO       = 10     # <= 10  → naranja (reprobado)

#  Paleta de colores HUD
C_FONDO_PANEL = (20,  20,  45, 200)   # fondo semitransparente
C_BORDE_PANEL = (90,  90, 130)
C_BARRA_BG    = (50,  50,  80)        # fondo vacío de la barra
C_NORMAL      = (60, 200,  80)        # verde  (bien)
C_BAJO        = (230, 160,  30)       # naranja (alerta)
C_PELIGRO     = (210,  40,  40)       # rojo   (crítico)
C_LABEL       = (220, 220, 255)       # texto etiqueta
C_VALOR       = (255, 240, 180)       # texto valor numérico

# Dimensiones HUD
HUD_PANEL_W = 210
HUD_PANEL_H = 120
HUD_PADDING = 10
HUD_BAR_H   =  14
HUD_BAR_W   = 190
HUD_ROW_GAP =  34     # espacio vertical entre filas



#  CLASE STATS


class Stats:
    """
    Gestiona y visualiza las estadísticas del estudiante universitario.

    Uso típico en el game loop:
        stats = Stats()
        ...
        # actualizar
        stats.modificar_energia(-5)
        stats.modificar_dinero(+100)
        stats.modificar_notas(+2)
        # consultar estado
        estado = stats.estado_juego()   # "jugando" | "derrota_*" | "victoria"
        # dibujar HUD
        stats.draw_hud(screen, font, x=10, y=10)
        # reiniciar
        stats.reset()
    """

    def __init__(self) -> None:
        self._energia: float = float(ENERGIA_INICIAL)
        self._dinero:  float = float(DINERO_INICIAL)
        self._notas:   float = float(NOTAS_INICIAL)
        self._conocimiento: float = float(CONOCIMIENTO_INICIAL)


    
    #  PROPIEDADES (solo lectura)
    

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

    #  MODIFICADORES SEGUROS
    

    def modificar_energia(self, delta: float) -> None:
        """
        Suma delta a la energía (positivo = ganar, negativo = perder).
        Resultado siempre dentro de [ENERGIA_MIN, ENERGIA_MAX].
        """
        self._energia = self._clamp(self._energia + delta, ENERGIA_MIN, ENERGIA_MAX)

    def modificar_dinero(self, delta: float) -> None:
        """
        Suma delta al dinero en soles.
        Resultado siempre dentro de [DINERO_MIN, DINERO_MAX].
        """
        self._dinero = self._clamp(self._dinero + delta, DINERO_MIN, DINERO_MAX)

    def modificar_notas(self, delta: float) -> None:
        """
        Suma delta a las notas (escala vigesimal).
        Resultado siempre dentro de [NOTAS_MIN, NOTAS_MAX].
        """
        self._notas = self._clamp(self._notas + delta, NOTAS_MIN, NOTAS_MAX)

    def reset(self) -> None:
        """Restaura todas las estadísticas a sus valores iniciales."""
        self._energia = float(ENERGIA_INICIAL)
        self._dinero  = float(DINERO_INICIAL)
        self._notas   = float(NOTAS_INICIAL)

    
    #  ESTADO DEL JUEGO
    

    def estado_juego(self) -> str:
        """
        Determina si la partida continúa o ha terminado.

        Retorna uno de:
            "jugando"         → partida en curso
            "victoria"        → notas llegaron a 20/20
            "derrota_energia" → energía llegó a 0  (colapso)
            "derrota_dinero"  → dinero llegó a 0   (quiebra)
            "derrota_notas"   → notas llegaron a 0 (reprobado total)

        Prioridad: victoria > derrota_energia > derrota_dinero > derrota_notas
        """
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
=======
        """True si alguna estadística está en zona crítica (roja)."""
        return (
            self._energia <= ENERGIA_PELIGRO
            or self._dinero  <= DINERO_PELIGRO
            or self._notas   <= NOTAS_PELIGRO
        )

    def esta_aprobando(self) -> bool:
        """True si las notas actuales son suficientes para aprobar el semestre."""
        return self._notas >= NOTAS_APROBADO

    
    #  PORCENTAJES (útiles para la barra y para lógica externa)
   

    def porcentaje_energia(self) -> float:
        """Energía normalizada a [0.0, 1.0]."""
        return self._energia / ENERGIA_MAX

    def porcentaje_dinero(self) -> float:
        """Dinero normalizado a [0.0, 1.0]."""
        return self._dinero / DINERO_MAX

    def porcentaje_notas(self) -> float:
        """Notas normalizadas a [0.0, 1.0]."""
        return self._notas / NOTAS_MAX

    
    #  HUD VISUAL
   

    def draw_hud(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        x: int = 10,
        y: int = 10,
    ) -> None:


        """
        Dibuja el panel de estadísticas con barras de progreso.

        Args:
            surface : Superficie PyGame de destino (ventana principal).
            font    : Fuente para etiquetas y valores.
            x, y    : Esquina superior izquierda del panel.
        """
        # Panel de fondo semitransparente

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


        """Dibuja una fila: etiqueta  |  barra de progreso  |  valor."""
        # Etiqueta
        label_surf = font.render(icono, True, C_LABEL)
        surface.blit(label_surf, (x, y))

        # Valor numérico (a la derecha de la barra)
        val_surf = font.render(valor, True, C_VALOR)
        val_x    = x + HUD_BAR_W - val_surf.get_width()
        surface.blit(val_surf, (val_x, y))


        # Barra de progreso
        bar_y = y + label_surf.get_height() + 3

        # Fondo vacío
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



    #  UTILIDAD INTERNA

    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        """Restringe value al rango [min_val, max_val]."""
        return max(min_val, min(max_val, value))


    #  REPRESENTACIÓN


    def __repr__(self) -> str:
        return (
            f"Stats("
            f"energia={self._energia:.0f}/{ENERGIA_MAX}, "
            f"dinero={self._dinero:.0f}/{DINERO_MAX}, "
            f"notas={self._notas:.1f}/{NOTAS_MAX}, "

            f"conocimiento={self._conocimiento:.0f}/{CONOCIMIENTO_MAX}, "
            f"estado='{self.estado_juego()}')"
        )

            f"estado='{self.estado_juego()}')"
        )

