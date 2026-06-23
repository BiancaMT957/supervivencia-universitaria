"""
events.py
"Supervivencia Universitaria: La Vida Da Vueltas"

Funcionalidad #5 – Eventos aleatorios (examen sorpresa, parcial difícil, etc.)

Arquitectura:
    · RandomEvent  → dato de un evento: nombre, efectos, duración visual.
    · EventManager → controla el intervalo entre eventos, activa uno aleatorio
                     y aplica sus efectos sobre Stats.

Uso en el game loop (STATE_PLAYING):
    # — inicialización —
    event_mgr = EventManager()

    # — update —
    event_mgr.update(dt_ms, stats)

    # — render (pasar a ui.draw_hud_enriched) —
    evento_activo = event_mgr.evento_activo
"""

import random
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stats import Stats


# ─────────────────────────────────────────────
#  CATÁLOGO DE EVENTOS
# ─────────────────────────────────────────────
#  Cada entrada es un dict con:
#    nombre            : str  – nombre corto visible en el HUD
#    descripcion_corta : str  – una línea de contexto
#    descripcion_larga : str  – texto para la pantalla de evento (escenas.py)
#    efectos           : dict – modificadores inmediatos sobre Stats
#                               claves: "energia", "dinero", "notas"
#    duracion_ms       : int  – cuánto tiempo se muestra el banner (ms)
#    color             : tuple – color del banner/pantalla
# ─────────────────────────────────────────────

CATALOGO_EVENTOS: list[dict] = [
    {
        "nombre"           : "Examen Sorpresa",
        "descripcion_corta": "El profesor acaba de sacar una hoja...",
        "descripcion_larga": "No hay aviso. Solo una hoja en blanco y la mirada del profe.",
        "efectos"          : {"notas": -2, "energia": -15},
        "duracion_ms"      : 4_000,
        "color"            : (220, 60, 60),
    },
    {
        "nombre"           : "Parcial Difícil",
        "descripcion_corta": "El parcial más temido del ciclo llegó.",
        "descripcion_larga": "Cinco horas de estudio no fueron suficientes.",
        "efectos"          : {"notas": -3, "energia": -20, "dinero": -20},
        "duracion_ms"      : 5_000,
        "color"            : (200, 40, 40),
    },
    {
        "nombre"           : "WiFi del Campus caído",
        "descripcion_corta": "Sin internet para subir la tarea.",
        "descripcion_larga": "El sistema del aula virtual no responde. Deadline en 5 min.",
        "efectos"          : {"notas": -1, "energia": -8},
        "duracion_ms"      : 3_500,
        "color"            : (100, 80, 200),
    },
    {
        "nombre"           : "Bono de Asistencia",
        "descripcion_corta": "¡Asistencia perfecta reconocida!",
        "descripcion_larga": "El coordinador anunció puntos extra por asistencia.",
        "efectos"          : {"notas": +2, "energia": +10},
        "duracion_ms"      : 4_000,
        "color"            : (50, 200, 100),
    },
    {
        "nombre"           : "Cola en Cafetería",
        "descripcion_corta": "Media hora esperando un sándwich.",
        "descripcion_larga": "Llegaste tarde a clase por la cola interminable.",
        "efectos"          : {"energia": -10, "dinero": -15},
        "duracion_ms"      : 3_000,
        "color"            : (180, 120, 40),
    },
    {
        "nombre"           : "Tutoría Gratis",
        "descripcion_corta": "Un monitor ofrece ayuda sin costo.",
        "descripcion_larga": "Una hora de tutoría que aclaró todo el tema.",
        "efectos"          : {"notas": +1, "energia": -5},
        "duracion_ms"      : 3_500,
        "color"            : (60, 160, 220),
    },
    {
        "nombre"           : "Feria de Prácticas",
        "descripcion_corta": "¡Empresa busca practicantes!",
        "descripcion_larga": "Te ofrecen una práctica con sueldo básico.",
        "efectos"          : {"dinero": +150, "energia": -10},
        "duracion_ms"      : 4_500,
        "color"            : (220, 180, 30),
    },
    {
        "nombre"           : "Semana de Exámenes",
        "descripcion_corta": "Cuatro exámenes en tres días.",
        "descripcion_larga": "El horario quedó imposible. Café y poco sueño.",
        "efectos"          : {"notas": -1, "energia": -25, "dinero": -30},
        "duracion_ms"      : 5_000,
        "color"            : (200, 50, 80),
    },
]

# Pesos de aparición (primeros eventos negativos son más frecuentes)
_PESOS_EVENTOS = [4, 4, 3, 2, 3, 2, 2, 4]


# ─────────────────────────────────────────────
#  CLASE: RandomEvent
# ─────────────────────────────────────────────

class RandomEvent:
    """Instancia activa de un evento sorpresa."""

    def __init__(self, data: dict) -> None:
        self.nombre             = data["nombre"]
        self.descripcion_corta  = data["descripcion_corta"]
        self.descripcion_larga  = data["descripcion_larga"]
        self.efectos            = data["efectos"]
        self.duracion_ms        = float(data["duracion_ms"])
        self.color              = data["color"]
        self.tiempo_restante_ms = self.duracion_ms
        self.activo             = True

    def update(self, dt_ms: float) -> None:
        if not self.activo:
            return
        self.tiempo_restante_ms -= dt_ms
        if self.tiempo_restante_ms <= 0:
            self.activo = False

    def aplicar_efectos(self, stats: "Stats") -> None:
        """Aplica los modificadores sobre Stats (se llama UNA sola vez al activarse)."""
        for stat, delta in self.efectos.items():
            if stat == "energia":
                stats.modificar_energia(delta)
            elif stat == "dinero":
                stats.modificar_dinero(delta)
            elif stat == "notas":
                stats.modificar_notas(delta)
        print(f"[EventManager] Evento '{self.nombre}' activado → {self.efectos}")

    def __repr__(self) -> str:
        return f"RandomEvent('{self.nombre}', activo={self.activo}, restante={self.tiempo_restante_ms:.0f}ms)"


# ─────────────────────────────────────────────
#  CLASE: EventManager
# ─────────────────────────────────────────────

class EventManager:
    """
    Controla la lógica de disparo de eventos aleatorios.

    Parámetros de constructor:
        intervalo_min_ms : tiempo mínimo entre eventos (default 18 s)
        intervalo_max_ms : tiempo máximo entre eventos (default 35 s)
    """

    def __init__(
        self,
        intervalo_min_ms: float = 18_000.0,
        intervalo_max_ms: float = 35_000.0,
    ) -> None:
        self._intervalo_min = intervalo_min_ms
        self._intervalo_max = intervalo_max_ms
        self._proximo_ms    = self._nuevo_intervalo()
        self._acumulado_ms  = 0.0
        self.evento_activo: RandomEvent | None = None
        # Historial para evitar repetir el mismo evento dos veces seguidas
        self._ultimo_idx: int | None = None

    # ── Intervalo aleatorio ────────────────────────────────────────────

    def _nuevo_intervalo(self) -> float:
        return random.uniform(self._intervalo_min, self._intervalo_max)

    # ── Selección de evento ────────────────────────────────────────────

    def _seleccionar_evento(self) -> RandomEvent:
        indices     = list(range(len(CATALOGO_EVENTOS)))
        pesos_local = list(_PESOS_EVENTOS)

        # Reducir peso del último evento para evitar repetición inmediata
        if self._ultimo_idx is not None:
            pesos_local[self._ultimo_idx] = max(1, pesos_local[self._ultimo_idx] - 3)

        idx = random.choices(indices, weights=pesos_local, k=1)[0]
        self._ultimo_idx = idx
        return RandomEvent(CATALOGO_EVENTOS[idx])

    # ── Update (llamar cada frame mientras STATE_PLAYING) ─────────────

    def update(self, dt_ms: float, stats: "Stats") -> None:
        # Actualizar evento en curso
        if self.evento_activo and self.evento_activo.activo:
            self.evento_activo.update(dt_ms)

        # Acumular tiempo hacia el próximo evento
        self._acumulado_ms += dt_ms

        if self._acumulado_ms >= self._proximo_ms:
            # Solo disparar si no hay evento activo
            if self.evento_activo is None or not self.evento_activo.activo:
                self._disparar_evento(stats)
            self._acumulado_ms  = 0.0
            self._proximo_ms    = self._nuevo_intervalo()

    def _disparar_evento(self, stats: "Stats") -> None:
        self.evento_activo = self._seleccionar_evento()
        self.evento_activo.aplicar_efectos(stats)

    # ── Reset (al reiniciar partida) ───────────────────────────────────

    def reset(self) -> None:
        self._acumulado_ms  = 0.0
        self._proximo_ms    = self._nuevo_intervalo()
        self.evento_activo  = None
        self._ultimo_idx    = None

    def __repr__(self) -> str:
        prox = max(0, self._proximo_ms - self._acumulado_ms)
        return (f"EventManager(próximo en {prox/1000:.1f}s, "
                f"activo={self.evento_activo})")
